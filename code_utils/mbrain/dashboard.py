"""Code to generate time-series visualization dashboard for the mBrain data."""

import sys
from datetime import datetime
from inspect import getsourcefile
from pathlib import Path
from typing import List, Tuple

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from dash_extensions.enrich import (
    DashProxy,
    ServersideOutput,
    ServersideOutputTransform,
)
from plotly.subplots import make_subplots
from plotly_resampler import FigureResampler
from plotly_resampler.aggregation import MinMaxLTTB

# fmt: off
# isort: off
sys.path.append(str(Path(getsourcefile(lambda: 0)).parent.parent.parent.absolute()))
from code_utils.mbrain.visualization import add_headache_timeline_to_fig  # noqa: E402
from code_utils.path_conf import processed_mbrain_path, mbrain_metadata_path, loc_data_dir  # noqa: E402
from code_utils.utils.dash_utils import serve_layout, get_selector_states, _create_subfolder_dict # noqa: E402
# isort: on
# fmt: on

df_h = pd.read_parquet(
    loc_data_dir / "df_headache_relevant.parquet", engine="fastparquet"
)

# Create the Dash app
app = DashProxy(
    __name__,
    external_stylesheets=[dbc.themes.LUX],
    transforms=[ServersideOutputTransform()],
)


# each list is a type
name_folders_list = [
    {"mbrain": {"user_folder": processed_mbrain_path}},
    {"mbrain": {"user_folder": processed_mbrain_path}},
]

# Construct the layout
app.layout = serve_layout(
    app,
    title="plotly-resampler mBrain dashboard",
    checklist_options=["show timeline"],
    name_folders_list=name_folders_list,
)
selector_states = get_selector_states(name_folders_list)


# --------------------------------- Visualization ---------------------------------
def plot_multi_sensors(
    selected_items,
    fold_usr_subf_start_end_sensor_list: List[
        Tuple[str, str, str, str, str, List[str]]
    ],
) -> go.Figure:
    selected_items = [h.strip() for h in selected_items]

    # create the figures
    prev_rows: List[str] = []
    if "show timeline" in selected_items:
        prev_rows += ["timeline"]

    sensors_names = [
        " ".join([Path(f).name, sensor])
        for f, _, _, _, _, sensors in fold_usr_subf_start_end_sensor_list
        for sensor in (sensors if isinstance(sensors, list) else [])
    ]
    total_rows: int = len(prev_rows) + len(sensors_names)
    kwargs = {"vertical_spacing": 0.15 / total_rows} if total_rows >= 2 else {}

    fig = FigureResampler(
        make_subplots(
            rows=total_rows,
            cols=1,
            shared_xaxes=True,
            subplot_titles=prev_rows + sensors_names,
            **kwargs,
        )
    )
    fig.update_layout(height=min(1000, 400 * total_rows), template="plotly_white")

    # 0. Visualize the mBrain timeline
    row_idx = 1
    if "show timeline" in selected_items:
        # TODO: also filter on the date range
        patient_id = fold_usr_subf_start_end_sensor_list[0][1].split(".")[0]
        # df_eventdump = pd.read_csv(mbrain_metadata_path / patient_id / "event_dump.csv")
        df_h_u = df_h[df_h["user"] == patient_id]
        add_headache_timeline_to_fig(fig, row_idx, df_headache=df_h_u)
        row_idx += 1

    # 1. Visualize the sensor data
    for (fold, usr, subf, start, end, sensors) in fold_usr_subf_start_end_sensor_list:
        # todo -> this functionality should be separated
        folder_subfolder_dict = _create_subfolder_dict(subf)
        sensors = [] if not isinstance(sensors, list) else sensors
        for sensor in sensors:
            sensor_path = Path(fold) / usr / folder_subfolder_dict.get(fold, "")

            print("sensor_path", sensor_path)
            print(sensor_path)
            # check if uses day -> boolean
            df_list = []
            for dates in pd.date_range(
                datetime.strptime(start, "%Y_%m_%d").date(),
                datetime.strptime(end, "%Y_%m_%d").date(),
                freq="D",
            ):
                sensor_files = list(
                    sensor_path.glob(f"{sensor}_{dates.strftime('%Y_%m_%d')}*")
                )
                if len(sensor_files) != 1:
                    continue

                sensor_file: Path = sensor_files[0]
                df_sensor = pd.read_parquet(sensor_file)
                if "timestamp" in df_sensor.columns:
                    df_sensor = df_sensor.set_index("timestamp")
                df_list.append(df_sensor)
            df_sensor = pd.concat(df_list)

            for col in sorted(
                set(df_sensor.columns.values).difference(["index", "timestamp"])
            ):
                print(f"{col}" + f" {len(df_sensor[col]):,} " + "-" * 30)
                print(col, df_sensor[col].dtype)
                fig.add_trace(
                    trace=go.Scattergl(x=[], y=[], name=col),
                    row=row_idx,
                    col=1,
                    hf_x=df_sensor[col].index,
                    hf_y=df_sensor[col],
                )
            row_idx += 1
    return fig


# --------------------------------- Callbacks ---------------------------------
# -------- plot or update graph ---------
@app.callback(
    Output("resampled-graph", "figure"),
    ServersideOutput("store", "data"),
    [
        Input("plot-button", "n_clicks"),
        State("checklist", "value"),
        State("start-date", "value"),
        State("end-date", "value"),
        *selector_states,
    ],
)
def plot_or_update_graph(_, selected_items, start_date, end_date, *folder_list):
    selected_items = [] if selected_items is None else selected_items

    it = iter(folder_list)
    folder_user_day_sensor_list = []
    for folder, user, subfolder, sensors in zip(it, it, it, it):
        if not all((folder, user, subfolder, start_date, end_date)):
            continue
        else:
            folder_user_day_sensor_list.append(
                (folder, user, subfolder, start_date, end_date, sensors)
            )

    ctx = dash.callback_context
    if (
        len(ctx.triggered)
        and "plot-button" in ctx.triggered[0]["prop_id"]
        and len(folder_user_day_sensor_list)
    ):
        fig = plot_multi_sensors(
            selected_items=selected_items,
            fold_usr_subf_start_end_sensor_list=folder_user_day_sensor_list,
        )
        return fig, fig
    return dash.no_update, dash.no_update


if __name__ == "__main__":
    app.run_server(port=8022, host="0.0.0.0", debug=True)
