from pathlib import Path
from typing import Iterable

import pandas as pd
from tqdm.auto import tqdm


def _get_td_range_df(df_: pd.DataFrame, threshold=pd.Timedelta) -> pd.DataFrame:
    data_list = []
    for date in tqdm(
        pd.date_range(df_.index[0].date(), df_.index[-1].date(), freq="D").tz_localize(
            df_.index.tz
        )
    ):
        df_day = df_[date : date + pd.Timedelta(days=1)]
        if not len(df_day):
            continue

        gaps_start = df_day.index.to_series().diff() > threshold
        gaps_start.iloc[[0]] = True

        gaps_end = gaps_start.shift(-1)
        gaps_end.iloc[[-1]] = True

        gaps_start = df_day[gaps_start].index.to_list()
        gaps_end = df_day[gaps_end].index.to_list()
        data_list += [[date, gs, ge] for gs, ge in zip(gaps_start, gaps_end)]

    sessions = pd.DataFrame(data=data_list, columns=["date", "start", "end"])
    sessions["session_dur"] = sessions.end - sessions.start

    sessions = pd.merge(
        sessions,
        sessions.groupby("date")["session_dur"].sum().rename("daily_wear_time"),
        left_on="date",
        right_index=True,
        how="outer",
    )
    return sessions


def get_wearable_session_df(glob: Iterable[Path], fs_exp) -> pd.DataFrame:
    data_list = []
    for eligible_file in glob:
        pqt = pd.read_parquet(eligible_file)  # .set_index("timestamp")
        data_list.append(pqt)

    if not len(data_list):
        return pd.DataFrame()

    df_ = pd.concat(data_list)
    df_ = df_.drop_duplicates(subset=["timestamp"]).set_index("timestamp").sort_index()
    del data_list
    return _get_td_range_df(df_, threshold=pd.Timedelta(seconds=1.1 / fs_exp))


def get_label_interaction_df(df_user_label: pd.DataFrame) -> pd.DataFrame:
    if "timestamp" in df_user_label.columns:
        df_user_label = df_user_label.drop_duplicates(subset=["timestamp"]).set_index(
            "timestamp"
        )
    return _get_td_range_df(df_user_label, threshold=pd.Timedelta(seconds=60 * 1.1))
