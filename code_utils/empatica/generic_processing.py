"""Various functions to process wearable data."""
from __future__ import annotations

__author__ = "Jonas Van Der Donckt"


from typing import Optional, Union

import numpy as np
import pandas as pd
from scipy import signal


def sqi_and(*series, output_name: str):
    sqi = None
    for s in series:
        if sqi is None:
            sqi = s.rename(output_name)
            continue
        if len(sqi) == len(s):
            sqi &= s
        else:
            raise ValueError
    return sqi


def sqi_or(*series, output_name: str):
    # TODO: what do we do with NaNs?
    sqi = None
    for s in series:
        if sqi is None:
            sqi = s.rename(output_name)
            continue
        if len(sqi) == len(s):
            sqi |= s
        else:
            raise ValueError
    return sqi


def sqi_smoothen(
    sqi: pd.Series,
    fs: int,
    window_s: int = 5,
    min_ok_ratio=0.75,
    flip=False,
    center=True,
    output_name="EDA_SQI_smoothend",
):
    if flip:
        sqi = ~sqi

    w_size = window_s * fs
    ok_sum = sqi.rolling(w_size + (w_size % 2 - 1), center=center).sum()
    out = (sqi & ((ok_sum / w_size) >= min_ok_ratio)).rename(output_name)

    if flip:
        out = ~out

    return out


def std_sum(
    sig_df: pd.DataFrame, n, name, scaling_factor=1, **rolling_kwgs
) -> pd.Series:
    """Calculate the std of centered rolling window `n_samples`, followed by the sum
    over axis=1.

    Parameters
    ----------
    sig_df : pd.DataFrame
        The dataframe on which the rolling std-sum will be calculated.
    n : int
        The window size on which the std will be calculated.
    name : str
        The name of the output series.
    scaling_factor : int, optional
        The factor through which sig_df will be divided, by default 1.
    rolling_kwgs : dict
        Additional keyword arguments passed to the `pd.DataFrame.rolling` method.

    Returns
    -------
    pd.Series
        The rolling std of the given series, with output name `name`
    """
    return (
        (sig_df / scaling_factor)
        .rolling(n, **rolling_kwgs)
        .std()
        .sum(axis=1)
        .bfill()
        .ffill()
        .rename(name)
    )


def mean_resample(
    s: pd.Series,
    new_freq: Union[str, pd.Timedelta],
    label: str = "left",
    name: Optional[str] = None,
) -> pd.Series:
    """Resample the given series to a new frequency, and calculate the mean."""
    return s.resample(new_freq, label=label).mean().rename(name or s.name)


def rolling_mean(
    sig: pd.Series, n: Union[int, str], suffix: Optional[str] = None, **rolling_kwgs
) -> pd.Series:
    """Calculate the rolling, centered, mean on `sig` with window `n`.

    Note
    ----
    This is equivalent to normalized area.

    Parameters
    ----------
    sig : pd.Series
        The series on which the rolling mean will be calculated.
    n : int
        The window-size.
    suffix : str, optional
        An additional suffix to the output name, by default None (which adds '_mean').
    rolling_kwgs : dict
        Additional keyword arguments passed to the `pd.DataFrame.rolling` method.

    Returns
    -------
    pd.Series
        The rolling mean of the given series, with output name "<sig.name>_mean"

    """
    if suffix is None:
        suffix = "_mean"
    return sig.rolling(n, **rolling_kwgs).mean().rename(str(sig.name) + suffix)


def low_pass_filter(
    s: pd.Series,
    order: int = 5,
    f_cutoff: int = 1,
    fs: int | float | None = None,
    output_name="filter",
    contains_nans=False,
) -> pd.Series:
    if fs is None:  # determine the sample frequency
        fs = 1 / pd.Timedelta(pd.infer_freq(s.index)).total_seconds()
    b, a = signal.butter(
        N=order, Wn=f_cutoff / (0.5 * fs), btype="lowpass", output="ba", fs=fs
    )
    if not contains_nans:
        assert not s.isna().any(), f"{s.name} should not contain any NaN values"
    else:
        s = s.dropna()

    # the filtered output has the same shape as sig.values
    return pd.Series(
        index=s.index, data=signal.filtfilt(b=b, a=a, x=s.values).astype(np.float32)
    ).rename(output_name)


def nan_padded_low_pass_filter(
    s: pd.Series,
    order: int = 5,
    f_cutoff: int = 1,
    fs: int | float | None = None,
    nan_pad_size_s=None,
    output_name="filter",
) -> pd.Series:
    if fs is None:  # determine the sample frequency
        fs = 1 / pd.Timedelta(pd.infer_freq(s.index)).total_seconds()

    # we will perform an or_convolution with a nan padded signal
    nan_mask = s.isna()
    expanded_nan_mask = (
        np.convolve(nan_mask, np.ones(int(2 * nan_pad_size_s * fs + 1)), mode="same")
        > 0
    )
    b, a = signal.butter(
        N=order, Wn=f_cutoff / (0.5 * fs), btype="lowpass", output="ba", fs=fs
    )
    # the filtered output has the same shape as sig.values
    filt_data = signal.filtfilt(b=b, a=a, x=s[~nan_mask].values).astype(np.float32)
    s_ = pd.Series(index=s.index, dtype=np.float32)
    s_[~nan_mask] = filt_data
    s_[expanded_nan_mask] = None
    return s_.rename(output_name)


def high_pass_filter(
    s: pd.Series,
    order: int = 5,
    f_cutoff: int = 1,
    fs: int | float | None = None,
    output_name="filter",
) -> pd.Series:
    if fs is None:  # determine the sample frequency
        fs = 1 / pd.Timedelta(pd.infer_freq(s.index)).total_seconds()
    b, a = signal.butter(
        N=order, Wn=f_cutoff / (0.5 * fs), btype="highpass", output="ba", fs=fs
    )
    # the filtered output has the same shape as sig.values
    # s = s.dropna()
    return pd.Series(
        index=s.index, data=signal.filtfilt(b=b, a=a, x=s.values).astype(np.float32)
    ).rename(output_name)


def threshold_sqi(s: pd.Series, output_name, max_thresh=None, min_thresh=None):
    sqi = pd.Series(index=s.index, data=True)
    if max_thresh is not None:
        sqi &= s <= max_thresh
    if min_thresh is not None:
        sqi &= s >= min_thresh
    return sqi.rename(output_name)
