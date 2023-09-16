from itertools import cycle
from typing import List, Optional

import matplotlib.colors as mcolors
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly_resampler import FigureResampler


def add_etri_timeline_to_fig(
    fig: FigureResampler,
    df_labels: pd.DataFrame,
    df_cols_to_plot: Optional[List[str]] = ["activity", "place", "condition"],
    row: Optional[int] = 1,
    col: Optional[int] = 1,
):
    if "timestamp" in df_labels.columns:
        df_labels = df_labels.drop_duplicates(subset="timestamp").set_index("timestamp")
    df_labels = df_labels.reindex(
        pd.date_range(df_labels.index[0], df_labels.index[-1], freq="1min")
    )
    color_list_cycle = cycle(
        [
            px.colors.qualitative.Plotly,
            px.colors.qualitative.Prism,
            px.colors.qualitative.Safe,
        ]
    )
    for i, col_name in enumerate(df_cols_to_plot):
        s = df_labels[col_name]
        color_cycle = cycle(next(color_list_cycle))
        factor = len(df_cols_to_plot) - 1 - i
        for k in s.cat.categories:
            c = next(color_cycle)
            if "rgb" not in c:
                c_a = (
                    "rgba("
                    + ", ".join([str(int(255 * c_)) for c_ in list(mcolors.to_rgb(c))])
                    + ", 0.5)"
                )
            else:
                c_a = "rgba(" + c[4:-1] + ", 0.5)"

            fig.add_trace(
                go.Scatter(
                    showlegend=False,
                    line_width=0,
                    mode="lines",
                    hoverinfo="skip",
                    line_shape="hvh",
                ),
                hf_x=pd.Index([df_labels.index[0], df_labels.index[-1]]),
                hf_y=np.zeros(2) + 1.2 * factor,
                # hf_x=df_labels.index,
                # hf_y=np.zeros(len(df_labels)) + 1.2 * factor,
                row=row,
                col=col,
            )
            fig.add_trace(
                go.Scatter(
                    name=k,
                    hoveron="fills",
                    legendgroup=f"group_{col_name}",
                    legendgrouptitle=dict(text=f"<b>{col_name.capitalize()}</b>:"),
                    line_color=c_a,
                    fillcolor=c_a,
                    line_shape="hvh",
                    fill="tonexty",
                    line_width=0,
                    mode="lines",
                ),
                hf_x=df_labels.index,
                hf_y=(s == k).astype(float) + 1.2 * factor,
            )

        # =========== Alternative way to plot the timeline ===========
        #     fig.add_trace(
        #         go.Scatter(
        #             name=k,
        #             stackgroup="one",
        #             mode="lines",
        #             line_color=c_a,
        #             fillcolor=c_a,
        #             legendgroup=f"group_{col_name}_s",
        #             hoveron="fills+points",
        #             hoverinfo="name",
        #             text=k,
        #             line_shape="hvh",
        #             line_width=0.5,
        #         ),
        #         check_nans=False,
        #         downsampler=downsampler,
        #         hf_x=df_labels.index,
        #         hf_y=(s == k).astype(int),
        #         row=row,
        #         col=col,
        #     )

        # fig.add_trace(
        #     go.Scatter(
        #         stackgroup="one",
        #         name="buffer",
        #         showlegend=False,
        #         hoverinfo="skip",
        #         fillcolor="rgba(0, 0, 0, .05)",
        #         line_color="rgba(0, 0, 0, .05)",
        #         legendgroup=f"group_{col_name}_s",
        #         line_shape="hvh",
        #         line_width=0,
        #         opacity=1,
        #     ),
        #     hf_x=df_labels.index,
        #     hf_y=0.2 * np.ones(len(df_labels))+df_labels[col_name].isna().astype(int),
        #     downsampler=downsampler,
        #     row=row,
        #     col=col,
        # )
        # =============================================================

        # add a shaded v_rect for the weekends
        # make it clear to typehinding that the index is a datetime index
        for sat in np.unique(df_labels[df_labels.index.dayofweek == 5].index.date):
            fig.add_vrect(
                x0=sat,
                x1=sat + pd.Timedelta(days=2),
                fillcolor="rgba(0, 0, 0, .04)",
                line_width=0,
            )
