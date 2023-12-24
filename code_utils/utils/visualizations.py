"""This module contains functions for plotly visualizations."""

import pandas as pd
import plotly.graph_objects as go


def draw_rectangle(
    t_start: pd.Timestamp, t_end: pd.Timestamp, row: int = 1, **kwargs
) -> go.Scatter:
    """Use a go.Scatter object to draw a rectangle.

    :param t_start: The start time of the rectangle
    :param t_end: The end time of the rectangle
    :param row: The row on which the rectangle will be drawn
        INDEX starts at 1!!
    :param kwargs: Additional arguments which will be passed to the Scatter function.

    :return: The drawn rectangle

    See Also
    --------
    https://plotly.com/python-api-reference/generated/plotly.graph_objects.Scatter.html
    for more info.

    """
    # assert t_start <= t_end, f"t_start must be less than or equal to t_end - {t_start} - {t_end}"
    row = max(1, row)
    return go.Scatter(
        x=[t_start, t_start, t_end, t_end, t_start],
        y=[row - 0.9, row - 0.1, row - 0.1, row - 0.9, row - 0.9],
        fill="toself",
        **kwargs,
    )


def draw_line(timestamp: pd.Timestamp, row: int = 1, **kwargs) -> go.Scatter:
    """Use a go.Scatter object to draw a rectangle.

    :param timestamp: The timestamp where the line will be drawn
    :param row: The row on which the rectangle will be drawn
        INDEX starts at 1!!
    :param kwargs: Additional arguments which will be passed to the Scatter function

    :return: The drawn rectangle

    See Also
    --------
    https://plotly.com/python-api-reference/generated/plotly.graph_objects.Scatter.html
    for more info.

    """
    row = max(1, row)
    return go.Scatter(x=[timestamp, timestamp], y=[row - 1 + 0.1, row - 0.1], **kwargs)
