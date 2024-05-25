import plotly.express as px
import plotly.graph_objects as go
from plotly_resampler.aggregation import MedDiffGapHandler


def plot_gsr_cols(f, df_s, row_idx, palette, add_skip_cols=[]):
    secondary_y_cols = ["EDA_SQI_smoothend"]
    skip_cols = [
        "raw_cleaned",
        "EDA_lf_1Hz",
        "EDA_SQI_smoothend",
        "slope",
        "raw_cleaned_duration_filter",
    ]
    skip_cols += ["EDA_lost_SQI", "EDA_slope_SQI"]
    skip_cols += add_skip_cols
    additional_row_cols = ["slope", "noise", "noise_mean_2s"]
    additional_row_secondary_y_cols = [
        "EDA_lost_SQI",
        "EDA_delta_SQI",
        "EDA_slope_SQI",
        "EDA_noise_SQI",
    ]
    cols = sorted(set(df_s.columns.values).difference(["index"]))
    for col in cols:
        print(f"{col}" + "-" * 30)
        if df_s[col].dtype == "bool":
            df_s[col] = df_s[col].astype("uint8")
        if col in skip_cols:
            continue
        if not len(df_s[col].dropna()):
            print(col, "is all na")
            continue

        if col == "EDA_SQI" or col == "EDA_SQI_tot":
            for sqi_col, col_or, opacity in [
                (df_s[col], "#2ca02c", 0.1),  # good
                ((1 - df_s[col]), "#d62728", 0.2),  # bad
            ]:
                f.add_trace(
                    go.Scattergl(
                        mode="lines",
                        line_width=0,
                        fill="tozeroy",
                        fillcolor=col_or,
                        opacity=opacity,
                        line_shape="vh",
                        showlegend=False,
                    ),
                    hf_x=df_s.index,
                    hf_y=sqi_col,
                    gap_handler=MedDiffGapHandler(fill_value=0),
                    secondary_y=True,
                    row=row_idx,
                    col=1,
                )
        elif col in secondary_y_cols:
            f.add_trace(
                dict(
                    name=col,
                    visible="legendonly",
                    legend=f"legend{row_idx}",
                    makrer_color=next(palette),
                ),
                hf_x=df_s.index,
                hf_y=df_s[col],
                row=row_idx,
                col=1,
                secondary_y=True,
            )
        elif col in additional_row_cols:
            f.add_trace(
                dict(
                    name=col,
                    visible="legendonly",
                    legend=f"legend{row_idx+1}",
                    marker_color=next(palette),
                ),
                hf_x=df_s.index,
                hf_y=df_s[col],
                row=row_idx + 1,
                col=1,
            )
        elif col in additional_row_secondary_y_cols:
            f.add_trace(
                dict(
                    name=col,
                    visible="legendonly",
                    legend=f"legend{row_idx+1}",
                    marker_color=next(palette),
                ),
                hf_x=df_s.index,
                hf_y=df_s[col],
                row=row_idx + 1,
                col=1,
                secondary_y=True,
            )
        else:
            f.add_trace(
                dict(
                    name=col,
                    visible="legendonly",
                    legend=f"legend{row_idx}",
                    marker_color=next(palette),
                ),
                hf_x=df_s[col].index,
                hf_y=df_s[col],
                row=row_idx,
                col=1,
            )
