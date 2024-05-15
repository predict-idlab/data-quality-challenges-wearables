import ast
import os
import textwrap
from pathlib import Path
from typing import List, Optional, Union

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from functional import seq
from plotly.subplots import make_subplots
from plotly_resampler import FigureResampler

from code_utils.utils.visualizations import draw_line, draw_rectangle

from .event_parsing import EventDumpParser
from .headaches import construct_headache_day_df


def construct_headache_event_hovertext(r: pd.Series) -> str:
    td = r.endTime - r.time
    hours = int(td.total_seconds() // 3600)
    minutes = int((td.total_seconds() - 3600 * hours) // 60)

    last_edited_time = None
    if all(c in r for c in ["created_on", "updated_on"]):
        last_edited_time = r[["created_on", "updated_on"]].dropna().max()

    edit_time_str = ""
    if not pd.isna(last_edited_time):
        td_e = last_edited_time - r.endTime
        hours_e = int(abs(td_e.total_seconds()) // 3600)
        minutes_e = int((abs(td_e.total_seconds()) - 3600 * hours_e) // 60)
        edit_time_str = (
            "<br><b>time difference</b> w.r.t. H end: "
            + ("-" if td_e.total_seconds() < 0 else "")
            + f"{hours_e}:{minutes_e}"
        )

    created_on_str = (
        (
            f"<b>Created on</b>: {r.created_on.strftime('%d/%m %H:%M')} "
            if "created_on" in r and pd.notna(r.created_on)
            else ""
        )
        + (
            f"- last edited: {last_edited_time.strftime('%d/%m %H:%M')}"
            if "created_on" in r
            and pd.notna(last_edited_time)
            and last_edited_time > r.created_on
            else ""
        )
        + edit_time_str
    )
    time_intensity_str = (
        f"<b>Interval</b>: {r.time.strftime('%H:%M')} - "
        f"{r.endTime.strftime('%H:%M')}" + f" - <b>Duration</b>: {hours}h{minutes}min "
        "- <b>Intensity</b>: "
        + str(r.intensity_str if "instensity_str" in r else r.intensity)
    )
    medication_str = (
        f"<b>Took medication</b>: {str(r.tookMedication)}  -  "
        + f"<b>medication working</b>: {str(r.medicationWorked)}"
    )

    # location_list = ast.literal_eval(r.location)
    # if isinstance(location_list, list):
    #     loc_str = "<b>Location</b>:<br>   " + "<br>   ".join(
    #         textwrap.wrap(", ".join(sorted([k["name_en"] for k in location_list])))
    #     )  # + "<br>"
    # else:
    loc_str = "<b>   no location</b>"

    def parse_symp_trgr_list(st_list, checked: bool = True):
        return ", ".join(
            sorted(
                seq(st_list)
                .filter(lambda y: y.get("isChecked") == checked)
                .map(lambda y: y.get("name_en"))
                .to_list()
            )
        )

    symp_list = ast.literal_eval(r.symptoms)
    if isinstance(symp_list, list):
        symp_str = "<b>Symptoms</b>:<br>   " + "<br>   ".join(
            textwrap.wrap(parse_symp_trgr_list(symp_list), width=80)
        )  # + "<br>"
    else:
        symp_str = "<b>   no symptoms<b>"

    trgr_list = ast.literal_eval(r.triggers)
    if isinstance(trgr_list, list):
        trigger_str = "<b>Triggers</b>:<br>   " + "<br>   ".join(
            textwrap.wrap(parse_symp_trgr_list(trgr_list), width=80)
        )  # + "<br>"
    else:
        trigger_str = "<b>no triggers</b>"

    return "<br>".join(
        [
            created_on_str,
            time_intensity_str,
            medication_str,
            loc_str,
            trigger_str,
            symp_str,
        ]
    )


def fast_scatter(df, subplots=False, mode="lines", **init_kwargs) -> FigureResampler:
    if not subplots:
        fig = FigureResampler(**init_kwargs)
    else:
        fig = FigureResampler(
            make_subplots(rows=df.shape[1], cols=1, shared_xaxes=True)
        )
    for i, c in enumerate(df.columns, 1):
        kwargs = {"row": i, "col": 1} if subplots else {}
        fig.add_trace(
            go.Scattergl(name=c, mode=mode), hf_x=df.index, hf_y=df[c], **kwargs
        )
    return fig


def subplot_scatter(df, row_mode, **init_kwargs) -> go.Figure:
    default_kwargs = {"shared_xaxes": True}
    default_kwargs.update(init_kwargs)
    fig = make_subplots(rows=len(row_mode), cols=1, **default_kwargs)
    for i, (c_list, mode) in enumerate(row_mode, 1):
        c_list = [c_list] if not isinstance(c_list, list) else c_list
        for c in c_list:
            fig.add_trace(
                go.Scattergl(name=c, x=df.index, y=df[c], mode=mode), row=i, col=1
            )
    return fig


def add_headache_timeline_to_fig(
    fig: go.Figure,
    row: int,
    col: Optional[int] = 1,
    df_eventdump: Optional[pd.DataFrame] = None,
    df_medicine: Optional[pd.DataFrame] = None,
    df_headache: Optional[pd.DataFrame] = None,
    df_tag: Optional[pd.DataFrame] = None,
    df_morning_headache: Optional[pd.DataFrame] = None,
    show_headache_implicitness_row: Optional[bool] = True,
) -> None:
    if df_headache is None and df_medicine is None:
        assert df_eventdump is not None

    if df_eventdump is None:
        df_eventdump = pd.DataFrame()
    if df_headache is None:
        df_headache = EventDumpParser.parse_headache_events(df_eventdump)
        for c in ["time", "endTime"]:
            df_headache[c] = df_headache[c].dt.tz_convert("Europe/Brussels")
        df_headache = df_headache[df_headache.deprecated != True]
        print(df_headache.columns)
        df_headache = df_headache.dropna(subset=['tookMedication'], how='any')
    if df_medicine is None:
        df_medicine = EventDumpParser.parse_medicine_events(df_eventdump)

    # TODO -> clean up this code
    date_range = pd.date_range(
        df_headache.time.min().date(), df_headache.time.max().date(), freq="D"
    )
    date_range = date_range.tz_localize("Europe/Brussels")
    print(date_range)
    # add a shaded v_rect for the weekends
    # make it clear to typehinding that the index is a datetime index
    print(date_range[date_range.dayofweek == 5])
    for sat in np.unique(date_range[date_range.dayofweek == 5].date):
        fig.add_vrect(
            x0=sat,
            x1=sat + pd.Timedelta(days=2),
            # fillcolor="rgba(0, 0, 0, .04)",
            fillcolor="blue",
            line_width=0,
            row=1,
        )

    legend_names = []
    # Add the data to the figure
    for _, r in df_headache.iterrows():
        fig.add_trace(
            draw_rectangle(
                t_start=r.time,
                t_end=r.endTime,
                row=1,
                line=dict(color="rgba(255, 0, 0, 0.3)", width=1),  # red
                mode="lines+markers",
                marker_size=2,
                name="headaches",
                legendgroup="headaches",
                showlegend="headaches" not in legend_names,
                hovertext=construct_headache_event_hovertext(r),
            ),
            row=row,
            col=col,
        )
        legend_names.append("headaches")

    for _, r in df_medicine.iterrows():
        fig.add_trace(
            draw_line(
                timestamp=r.time,
                row=2,
                marker_color="lightgreen",
                opacity=0.7,
                line_width=5,
                name="medicine",
                legendgroup="medicine",
                hovertext=(
                    f"<b>aangemaakt</b>: {r.created_on.strftime('%d/%m %H:%M')} "
                    if "created_on" in r and pd.notna(r.created_on)
                    else ""
                )
                + "<br>medicine:<br>    "
                + r["medicine.name"]
                + "<br>    "
                + r["medicine.description"],
                showlegend="medicine" not in legend_names,
            ),
            row=row,
            col=col,
        )
        legend_names.append("medicine")

    if df_tag is not None:
        for ts, r in df_tag.iterrows():
            # print(dict(r))
            fig.add_trace(
                draw_line(
                    ts,
                    row=2,
                    line_color="black",
                    name="tag",
                    mode="lines",
                    opacity=0.3,
                    line_width=3,
                    legendgroup="tag",
                    text=f"processed by user: {dict(r).get('processed_by_user', 'NaN')}",
                    showlegend="tag" not in legend_names,
                ),
                limit_to_view=False,
                row=row,
                col=col,
            )
            legend_names.append("tag")

    if df_morning_headache is None:
        return

    color_list = px.colors.qualitative.Set2
    for _, r in df_morning_headache.iterrows():
        if r["answer.id"] == "yes":
            if r.q_headaches_ref_date == 0:
                # green - correct that there were no headaches
                color = color_list[0]
            else:
                # red - correct that there were headaches
                color = color_list[1]
        else:
            if r.q_headaches_ref_date == 0:
                # red - incorrect that there were no headaches
                color = px.colors.qualitative.Set1[0]
            else:
                # blue - unknown
                color = color_list[2]
        hovertext = (
            f"gevraagd op {r.q_date.date()}<br>had u {r.q_headaches_ref_date} "
            f"hoofdpijnaanvallen op {r.ref_date.date()}: <br>antwoord: {r['answer.value']}"
        )

        fig.add_trace(
            draw_rectangle(
                t_start=r.ref_date,
                t_end=r.q_date,
                row=3,
                line=dict(color=color, width=1),
                mode="lines+markers",
                marker_size=2,
                name="headache-implicitness",
                legendgroup="headache-implicitness",
                hovertext=hovertext,
                showlegend="headache-implicitness" not in legend_names,
            ),
            row=row,
            col=col,
        )
        legend_names.append("headache-implicitness")

    # If both the morning questionnaire and the headache data are given: Perform a check
    # to see if the headache data is consistent with the morning questionnaire
    if (
        not show_headache_implicitness_row
        or df_morning_headache is None
        or df_headache is None
    ):
        return

    user_headache_day = construct_headache_day_df(df_headache)

    for _, r in df_morning_headache.iterrows():
        ref_series = user_headache_day[
            user_headache_day.index.date == r.ref_date.date()
        ].iloc[0]
        any_headaches = (
            ref_series.nbr_headaches_start_day > 0
            or ref_series.nbr_headaches_end_day > 0
            or ref_series.nbr_headaches_overlap_day > 0
        )
        any_no_headaches = (
            ref_series.nbr_headaches_start_day == 0
            or ref_series.nbr_headaches_end_day == 0
            or ref_series.nbr_headaches_overlap_day == 0
        )

        if r["answer.id"] == "yes":
            if r.q_headaches_ref_date == 0:
                # green - correct that there were no headaches
                color = color_list[0]

                # IF there were headaches, then set the color to red
                if not any_no_headaches:
                    color = px.colors.qualitative.Set1[0]
            else:
                # RED color -> no perfect match between the morning questionnaire
                # (indicating >0 headaches) and the headache data
                color = px.colors.qualitative.Set1[0]
                if (
                    ref_series.nbr_headaches_start_day == r.q_headaches_ref_date
                    or ref_series.nbr_headaches_end_day == r.q_headaches_ref_date
                    or ref_series.nbr_headaches_overlap_day == r.q_headaches_ref_date
                ):
                    # green - exact match between the morning questionnaire
                    color = color_list[0]
        else:  # incorrect answer
            if r.q_headaches_ref_date == 0:
                # red - incorrect that there were no headaches
                color = px.colors.qualitative.Set1[0]
                if any_headaches:
                    # orange - headache data is consistent with answer
                    # (but we do not know how many)
                    color = color_list[1]
            else:
                # red - incorrect
                color = px.colors.qualitative.Set1[0]
                if (
                    ref_series.nbr_headaches_start_day != r.q_headaches_ref_date
                    or ref_series.nbr_headaches_end_day != r.q_headaches_ref_date
                    or ref_series.nbr_headaches_overlap_day != r.q_headaches_ref_date
                ):
                    # orange - headache data is consistent with answer
                    # (but we do not know how many)
                    color = color_list[1]
        hovertext = (
            f"gevraagd op {r.q_date.date()}<br>had u {r.q_headaches_ref_date} "
            f"hoofdpijnaanvallen op {r.ref_date.date()}: "
            f"<br>antwoord: {r['answer.value']}"
            "<br>headaches which ... on this day:<br>"
            f"   <b>start</b>: {ref_series.nbr_headaches_start_day} "
            f" - <b>end</b>: {ref_series.nbr_headaches_end_day} "
            f" - <b>overlap</b>: {ref_series.nbr_headaches_overlap_day},"
        )

        fig.add_trace(
            draw_rectangle(
                t_start=r.ref_date,
                t_end=r.q_date,
                row=4,
                line=dict(color=color, width=1),
                mode="lines+markers",
                marker_size=2,
                name="implicitness checks",
                legendgroup="implicitness checks",
                hovertext=hovertext,
                showlegend="implicitness checks" not in legend_names,
            ),
            row=row,
            col=col,
        )
        legend_names.append("implicitness checks")
