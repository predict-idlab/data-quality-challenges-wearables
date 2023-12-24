"""Various functions to process the accelerometer data."""

__author__ = "Jonas Van Der Donckt"


from typing import Optional

import pandas as pd


def SMV(sig_df: pd.DataFrame, scale_factor=1) -> pd.Series:
    """Calculate the signal magnitude vector (SMV) for the given signal dataframe.

    Note
    ----
    This is also known as the Euclidean Norm (EN).

    Parameters
    ----------
    sig_df: pd.DataFrame
        The signal dataframe to calculate the SMV for.
    scale_factor: float
        sig_df will be divided by this factor, by default 1


    Returns
    -------
    pd.Series
        The SMV of the given signal dataframe, with output name "SMV"

    """
    return ((sig_df / scale_factor) ** 2).sum(axis=1).pow(0.5).rename("SMV")


def ABS_AI(
    sig_df: pd.DataFrame,
    n: int,
    sigma_i: Optional[int] = 0,
    scale_factor: Optional[int] = 1,
    suffix: Optional[str] = "",
    step: Optional[int] = None,
) -> pd.Series:
    """Calculate the absolute activity index.

    note that the `sigma_i` represents the systematic noise variant for
    **participant** $i$:

    $$
    \bar{\sigma}_{i}^{2}=\sigma_{i 1}^{2}+\sigma_{i 2}^{2}+\sigma_{i 3}^{2}
    $$

    parameters
    ----------
    sig_df: pd.DataFrame
        The signal dataframe whose columns will be aggregated to calculate the ABS AI
    n: int
        The centered rolling variance window
    sigma_i: float, optional
        This is the systematic noise variance, by default 0
    scale_factor : float, optional
        sig_df will be divided by this factor, by default 1
    suffix: str, optional
        An additional suffix to the "ABS_AI" output name, by default ''
    step: int, optional
        The step size of the rolling window, by default None (which is equivalent to
        step size = 1)

    Returns
    -------
    pd.Series
        The absolute activity index of the given signal dataframe,
        with output name "ABS_AI"

    See also
    --------
    An Activity Index for Raw Accelerometer Data and Its Comparison with Other
    Activity Metrics

    """
    return (
        # Calculate the variance on each signal, sub
        ((sig_df / scale_factor).rolling(n, center=True, step=step).var() - sigma_i)
        .mean(axis=1)
        .clip(lower=0)
        .pow(0.5)
        .rename(f"ABS_AI{suffix}")
    )
