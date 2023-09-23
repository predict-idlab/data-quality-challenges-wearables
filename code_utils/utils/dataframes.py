# -*- coding: utf-8 -*-
""" Utility code for wrangling time series DataFrames """
__author__ = "Jonas Van Der Donckt"

from typing import List, Union

import numpy as np
import pandas as pd


def groupby_consecutive(
    df: Union[pd.Series, pd.DataFrame], col_name: str = None
) -> pd.DataFrame:
    """Merges consecutive `column_name` values in a single dataframe.

    This is especially useful if you want to represent sparse data in a more
    compact format.

    Parameters
    ----------
    df : Union[pd.Series, pd.DataFrame]
        Must be time-indexed!
    col_name : str, optional
        If a dataFrame is passed, you will need to specify the `col_name` on which
        the consecutive-grouping will need to take plase.

    Returns
    -------
    pd.DataFrame
        A new `DataFrame` view, with columns:
        [`start`, `end`, `n_consecutive`, `col_name`], representing the
        start- and endtime of the consecutive range, the number of consecutive samples,
        and the col_name's consecutive values.
    """
    if type(df) == pd.Series:
        col_name = df.name
        df = df.to_frame()

    assert col_name in df.columns

    df_cum = (
        (df[col_name] != df[col_name].shift(1))
        .astype("int")
        .cumsum()
        .rename("value_grp")
        .to_frame()
    )
    df_cum["sequence_idx"] = df.index
    df_cum[col_name] = df[col_name]

    df_grouped = pd.DataFrame(
        {
            "start": df_cum.groupby("value_grp")["sequence_idx"].first(),
            "end": df_cum.groupby("value_grp")["sequence_idx"].last(),
            "n_consecutive": df_cum.groupby("value_grp").size(),
            col_name: df_cum.groupby("value_grp")[col_name].first(),
        }
    ).reset_index(drop=True)
    df_grouped["next_start"] = df_grouped.start.shift(-1).fillna(df_grouped["end"])
    return df_grouped


def arr_to_repetitive_count(arr: Union[pd.Series, List]) -> np.array:
    """Return an array of same shape as `arr` where the values represent the
    number of same consecutive values of the coressponding item in `arr`

    Parameters
    ----------
    arr: Union[pd.Series, List]
        The array for which the number of same-consecutive values for each item will
        be calculated

    Returns
    -------
    np.array

    """
    # 1. calculate where there are diffs -> indices
    shift = np.diff(arr)
    change = np.where(shift != 0)[0] + 1  # add 1 -> since diff reduces lenght with 1

    # base case: all values are the same -> return array with all values = len(arr)
    if len(change) <= 1:
        a = np.empty(len(arr), dtype="uint32")
        a.fill(len(arr))
        return a

    # calculte the diff of the whres and add
    # * prepend the first value of change (lost due to diff)
    # * append len(arr) - change[-1] (the number of repetitions of the last values)
    diffs = np.append(np.insert(np.diff(change), 0, change[0]), len(arr) - change[-1])
    return np.repeat(diffs, diffs)
