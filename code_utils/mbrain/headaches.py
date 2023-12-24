import pandas as pd

from .event_parsing import between, overlap


def construct_headache_day_df(
    user_headache_df: pd.DataFrame, margin=pd.Timedelta("90d"), overlap_end=True  # TODO
) -> pd.DataFrame:
    """Construct a dataframe with the number of headache events (start, end overlap)
    per day.

    Parameters
    ----------
    user_headache_df : pd.DataFrame
        The user headache dataframe, must contain the columns 'time', 'endTime'
    margin : pd.Timedelta, optional
        The time margin which is added to the first and last headache event to construct
        the output dataframe, by default pd.Timedelta("90d")

    Returns
    -------
    pd.DataFrame
        The constructed dataframe with the following columns:
            * index: the date of the day
            * nbr_headaches_start: # headache events which start on the day
            * nbr_headaches_end: # headache events which end on the day
            * nbr_headaches_overlap: # headache events which overlap on that day

    """
    user_headache_day = pd.Series(
        index=pd.date_range(
            (user_headache_df.time.min() - margin).date(),
            (user_headache_df.time.max() + margin).date(),
            freq="D",
            tz="UTC",
            name="date",
        ),
        data=0,
        name="nbr_headaches_start",
    ).to_frame()

    user_headache_day[
        "nbr_headaches_start_day"
    ] = user_headache_day.index.to_series().map(
        lambda x: between(
            user_headache_df.time, start=x, end=x + pd.Timedelta(days=1)
        ).sum()
    )

    user_headache_day[
        "nbr_headaches_end_day"
    ] = user_headache_day.index.to_series().map(
        lambda x: between(
            user_headache_df.endTime, start=x, end=x + pd.Timedelta(days=1)
        ).sum()
    )

    user_headache_day[
        "nbr_headaches_overlap_day"
    ] = user_headache_day.index.to_series().map(
        lambda x: overlap(
            t0=user_headache_df.time,
            t1=user_headache_df.endTime,
            start=x,
            end=x + pd.Timedelta(days=1),
        ).sum()
    )
    return user_headache_day
