# -*- coding: utf-8 -*-
"""Interface code for parsing mBrain app event data"""
__author__ = "Jonas Van Der Donckt"

import ast
from typing import List

import pandas as pd
from functional import seq


class EventDumpParser:
    """Interface to parse event dump data."""

    @staticmethod
    def _filter_transform_time(
        df_event: pd.DataFrame, type_filter: str, time_cols: List[str]
    ) -> pd.DataFrame:
        # base case -> empty input -> empty output
        if not len(df_event):
            return pd.DataFrame()

        df_event_type = df_event[df_event.type == type_filter].dropna(axis=1, how="all")

        for c in set(time_cols).intersection(df_event_type.columns):
            df_event_type[c] = (
                # If ‘coerce’, then invalid parsing will be set as NaT.
                pd.to_datetime(
                    df_event_type[c].values, errors="coerce", unit="ms"
                ).tz_localize("utc")
            )
        return df_event_type

    @staticmethod
    def parse_stress_events(df_event: pd.DataFrame) -> pd.DataFrame:
        time_cols = [
            "endTime",
            "feedbackTime",
            "time",
            "predictedEndTime",
            "predictedStartTime",
        ]
        return EventDumpParser._filter_transform_time(df_event, "stress", time_cols)

    @staticmethod
    def parse_activity_events(df_event: pd.DataFrame) -> pd.DataFrame:
        time_cols = [
            "endTime",
            "feedbackTime",
            "time",
            "predictedEndTime",
            "predictedTime",
            "sedentaryFeedbackTime",
            "created_on",
            "updated_on",
            "deprecated_on",
            "predictedStartTime",
        ]
        return EventDumpParser._filter_transform_time(df_event, "activity", time_cols)

    @staticmethod
    def parse_daily_record(df_event: pd.DataFrame) -> pd.DataFrame:
        t_cols = [
            "time",
            "foodIntake.breakfastTime",
            "foodIntake.dinnerTime",
            "foodIntake.lunchTime",
            "created_on",
            "updated_on",
        ]
        df_daily_record = EventDumpParser._filter_transform_time(
            df_event, "daily-record", t_cols
        )
        if len(df_daily_record):
            df_daily_record["date"] = df_daily_record["time"].dt.date
        return df_daily_record

    @staticmethod
    def parse_headache_events(df_event: pd.DataFrame) -> pd.DataFrame:
        time_cols = ["created_on", "endTime", "time", "updated_on"]
        return EventDumpParser._filter_transform_time(df_event, "headache", time_cols)

    @staticmethod
    def parse_medicine_events(df_event: pd.DataFrame) -> pd.DataFrame:
        time_cols = ["created_on", "time"]
        return EventDumpParser._filter_transform_time(df_event, "medicine", time_cols)

    @staticmethod
    def parse_questionnaire_events(df_event: pd.DataFrame) -> pd.DataFrame:
        time_cols = ["time", "payload.start_time", "payload.end_time", "created_on"]
        return EventDumpParser._filter_transform_time(
            df_event, "questionnaire", time_cols
        )

    @staticmethod
    def filter_parse_relevant_headaches(df_headache: pd.DataFrame) -> pd.DataFrame:
        """"""
        # Filter `df_headache_tot` where we disregard deprecated  uncompleted headaches
        df_headache_relevant = (
            df_headache[
                (df_headache.deprecated != True)
                & df_headache.intensity.notna()
                & ~df_headache.duplicated(subset="_id.$oid")
            ]
            .reset_index(drop=True)
            .copy()
        )

        # There are (a lot of) classification columns in the headache dataframe,
        # lets drop them
        df_headache_relevant = df_headache_relevant.drop(
            columns=list(df_headache_relevant.filter(regex="classification").columns)
        )

        df_headache_relevant["symptoms"] = df_headache_relevant["symptoms"].apply(
            ast.literal_eval
        )
        df_headache_relevant["triggers"] = df_headache_relevant["triggers"].apply(
            ast.literal_eval
        )

        df_headache_relevant["location"] = df_headache_relevant["location"].apply(
            ast.literal_eval
        )

        intensity_list = [
            "No pain",
            "Light pain",
            "Moderate pain",
            "Severe pain",
            "Very severe pain",
        ]
        df_headache_relevant["intensity_str"] = df_headache_relevant["intensity"].map(
            lambda x: intensity_list[int(x) - 1]
        )

        def parse_symp_trgr_list(st_list):
            return ", ".join(
                sorted(
                    seq(st_list)
                    .filter(lambda y: y.get("isChecked"))
                    .map(lambda y: y.get("name_nl"))
                    .to_list()
                )
            )

        df_headache_relevant["symptoms"] = df_headache_relevant["symptoms"].map(
            parse_symp_trgr_list
        )
        df_headache_relevant["triggers"] = df_headache_relevant["triggers"].map(
            parse_symp_trgr_list
        )
        df_headache_relevant["location"] = df_headache_relevant["location"].map(
            lambda x: ", ".join(sorted([k.get("name_nl") for k in x]))
        )

        df_headache_relevant["extraTriggers"] = df_headache_relevant[
            "extraTriggers"
        ].map(lambda x: ", ".join(ast.literal_eval(x)) if not pd.isnull(x) else None)
        df_headache_relevant["extraSymptoms"] = df_headache_relevant[
            "extraSymptoms"
        ].map(lambda x: ", ".join(ast.literal_eval(x)) if not pd.isnull(x) else None)

        def reorder_cols(first_cols, df):
            col_order = [*first_cols, *set(df.columns).difference(first_cols)]
            return df.sort_values(by=first_cols)[col_order]

        df_headache_relevant = reorder_cols(
            ["user", "time", "endTime"], df_headache_relevant
        )
        return df_headache_relevant


def between(t, start, end):
    return (start <= t) & (t <= end)


def overlap(t0, t1, start, end):
    return (t0 <= start) & (t1 >= start) | (t0 >= start) & (t0 <= end)
