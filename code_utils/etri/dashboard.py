"""Code to generate time-series visualization dashboard for the etri data. """


import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Tuple
from inspect import getsourcefile

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash_extensions.enrich import (
    DashProxy,
    ServersideOutput,
    ServersideOutputTransform,
)
from functional import seq
from plotly.subplots import make_subplots
from plotly_resampler import FigureResampler
from trace_updater import TraceUpdater

# fmt: off
# isort: off
sys.path.append(str(Path(getsourcefile(lambda: 0)).parent.parent.parent.absolute()))
from code_utils.etri.visualization import add_etri_timeline_to_fig  # noqa: E402
from code_utils.path_conf import processed_etri_path  # noqa: E402
from code_utils.utils.dash_utils import (  # noqa: E402
    _create_subfolder_dict,
    _update_sensor_widget,
    _update_user_widget
)
# isort: on
# fmt: on

app = DashProxy(
    __name__,
    external_stylesheets=[dbc.themes.LUX],
    transforms=[ServersideOutputTransform()],
)

df_labels = pd.read_parquet(processed_etri_path / "labels.parquet")

# each list is a type
name_folders_list = [
    {
        "etri": {"user_folder": processed_etri_path},
    },
    {
        "etri": {"user_folder": processed_etri_path},
    },
]

# --------------------------------- Visualization ---------------------------------
def plot_multi_sensors(
    har_checklist,
    folder_usr_subfold_startdt_enddt_sensor_list: List[
        Tuple[str, str, str, str, str, List[str]]
    ],
    session_id,
    number_of_samples,
) -> go.Figure:
    har_checklist = [h.strip() for h in har_checklist]

    # create the figures
    prev_rows: List[str] = []
    if "show timeline" in har_checklist:
        prev_rows += ["timeline"]

    if "RAW  HAR predictions" in har_checklist:
        prev_rows += ["acitivity predictions"]

    if "HAR timeline predictions" in har_checklist:
        prev_rows += ["HAR timeline"]

    if "HAR aggregation" in har_checklist:
        prev_rows += ["movement ratio"]

    print(folder_usr_subfold_startdt_enddt_sensor_list)
    sensors_names = [
        " ".join([Path(f).name, sensor])
        for f, _, _, _, _, sensors in folder_usr_subfold_startdt_enddt_sensor_list
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
    fig.update_layout(template="plotly_white")

    fig.update_layout(height=min(1000, 400 * total_rows))
    fig.update_layout(title="Multi sensor overview", title_x=0.5)

    # 0. Visualize the ETRI timeline
    row_idx = 1
    if "show timeline" in har_checklist:
        df_labels_user = df_labels[
            df_labels["user"] == folder_usr_subfold_startdt_enddt_sensor_list[0][1]
        ]
        add_etri_timeline_to_fig(fig, df_labels_user, row=row_idx)
        row_idx += 1

    # 1. Visualize the sensor data
    for (
        folder,
        user,
        subfolders,
        start_date,
        end_date,
        sensors,
    ) in folder_usr_subfold_startdt_enddt_sensor_list:
        # todo -> this functionality should be separated
        folder_subfolder_dict = _create_subfolder_dict(subfolders)
        sensors = [] if not isinstance(sensors, list) else sensors
        for sensor in sensors:
            sensor_path = Path(folder) / user / folder_subfolder_dict.get(folder, "")

            print("sensor_path", sensor_path)
            print(sensor_path)
            # check if uses day -> boolean
            df_list = []
            for dates in pd.date_range(
                datetime.strptime(start_date, "%Y_%m_%d").date(),
                datetime.strptime(end_date, "%Y_%m_%d").date(),
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


dark_figure = go.Figure()
dark_figure.update_layout(template="plotly_white")


# --------------------------------- DASH code base ---------------------------------
def serve_layout() -> dbc.Container:
    """Constructs the app's layout.

    Returns
    -------
    A Container withholding the layout.
    """
    session_id = str(uuid.uuid4())
    return dbc.Container(
        [
            # todo look into:
            # https://stackoverflow.com/questions/62732631/how-to-collapsed-sidebar-in-
            # dash-plotly-dash-bootstrap-components
            dbc.Container(
                html.H1("Plotly-Resampler ETRI lifelog 2020 dashboard"),
                style={"textAlign": "center"},
            ),
            # will be used for session storage
            html.Div(session_id, id="session-id", style={"display": "none"}),
            # is used to detect close events
            html.Div(id="listener"),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.Form(
                                    [
                                        dbc.Label(
                                            "start", style={"textAlign": "center"}
                                        ),
                                        dcc.Dropdown(
                                            id="start-date", options=[], clearable=False
                                        ),
                                        dbc.Label("end", style={"textAlign": "center"}),
                                        dcc.Dropdown(
                                            id="end-date", options=[], clearable=False
                                        ),
                                        html.Br(),
                                        dcc.Checklist(
                                            id="har-checklist",
                                            options=[
                                                " show timeline  ",
                                                # " process GSR  ",
                                            ],
                                        ),
                                        html.Br(),
                                    ]
                                )
                            ]
                            + [
                                dbc.Card(
                                    [
                                        dbc.Form(
                                            [
                                                dbc.Label("folder"),
                                                dcc.Dropdown(
                                                    id=f"folder-selector{i}",
                                                    options=[
                                                        {
                                                            "label": label,
                                                            "value": str(
                                                                f["user_folder"]
                                                            ),
                                                        }
                                                        for (
                                                            label,
                                                            f,
                                                        ) in name_folders.items()
                                                    ],
                                                    clearable=True,
                                                ),
                                                # a div with stored 'folder_name',
                                                # "sub_folder";...
                                                html.Div(
                                                    ";".join(
                                                        [
                                                            str(f["user_folder"])
                                                            + ","
                                                            + str(
                                                                f.get("sub_folder", "")
                                                            )
                                                            for (
                                                                _,
                                                                f,
                                                            ) in name_folders.items()
                                                        ]
                                                    ),
                                                    id=f"subfolder{i}",
                                                    style={"display": "none"},
                                                ),
                                                dbc.Label("User:"),
                                                dcc.Dropdown(
                                                    id=f"user-selector{i}",
                                                    options=[],
                                                    clearable=False,
                                                ),
                                                dbc.Label("Sensors:"),
                                                dcc.Dropdown(
                                                    id=f"sensor-selector{i}",
                                                    options=[],
                                                    multi=True,
                                                ),
                                            ]
                                        )
                                    ],
                                    color="primary",
                                    outline=True,
                                )
                                for i, name_folders in enumerate(name_folders_list, 1)
                            ]
                            + [
                                dbc.Form(
                                    [
                                        html.Br(),
                                        dbc.Button(
                                            "Run interact",
                                            id="plot-button",
                                            color="primary",
                                            style={"textAlign": "center"},
                                        ),
                                    ],
                                    style={"textAlign": "center"},
                                )
                            ],
                            body=True,
                        ),
                        md=2,
                    ),
                    dbc.Col(
                        [
                            dcc.Graph(
                                id="resampled-graph",
                                figure=FigureResampler(dark_figure),
                            ),
                            dcc.Loading(dcc.Store(id="store")),
                            TraceUpdater(
                                id="trace-updater",
                                gdID="resampled-graph",
                                sequentialUpdate=False,
                            ),
                        ],
                        md=10,
                    ),
                ],
                align="center",
            ),
        ],
        fluid=True,
    )


def _update_date_widget(user_folder_subfolders, reverse=True):
    if user_folder_subfolders is None:
        return []

    opt_list = []
    for user, folder, subfolder in user_folder_subfolders:
        if user is None or folder is None:  # or subfolder is None:
            continue

        opt_list.extend(
            seq(
                Path(folder)
                .joinpath(user)
                .joinpath(_create_subfolder_dict(subfolder).get(folder, ""))
                .iterdir()
            )
            .map(lambda x: "_".join(x.name.split(".")[0].split("_")[-3:]))
            .to_list()
        )

    opt_list = sorted(set(opt_list), reverse=reverse)
    return [{"label": date_str, "value": date_str} for date_str in opt_list]


@app.callback(
    Output("start-date", "options"),
    [
        Input("user-selector1", "value"),
        Input("user-selector2", "value"),
        State("folder-selector1", "value"),
        State("subfolder1", "children"),
        State("folder-selector2", "value"),
        State("subfolder2", "children"),
    ],
)
def update_start_date_widget(
    user_1, user_2, folder_1, subfolder_1, folder_2, subfolder_2
):
    return _update_date_widget(
        [(user_1, folder_1, subfolder_1), (user_2, folder_2, subfolder_2)],
        reverse=False,
    )


@app.callback(
    Output("end-date", "options"),
    [
        Input("user-selector1", "value"),
        Input("user-selector2", "value"),
        State("folder-selector1", "value"),
        State("subfolder1", "children"),
        State("folder-selector2", "value"),
        State("subfolder2", "children"),
    ],
)
def update_end_date_widget(
    user_1, user_2, folder_1, subfolder_1, folder_2, subfolder_2
):
    return _update_date_widget(
        [(user_1, folder_1, subfolder_1), (user_2, folder_2, subfolder_2)], reverse=True
    )


for id, _ in enumerate(name_folders_list, 1):
    app.callback(
        Output(f"user-selector{id}", "options"),
        [Input(f"folder-selector{id}", "value")],
    )(_update_user_widget)

    app.callback(
        Output(f"sensor-selector{id}", "options"),
        [
            Input(f"user-selector{id}", "value"),
            Input("start-date", "value"),
            State(f"folder-selector{id}", "value"),
            State(f"subfolder{id}", "children"),
        ],
    )(_update_sensor_widget)

app.layout = serve_layout()

# --- update the figure
# the list sum operationflattens the list
# TODO -> this is not loosely coupled
selector_states = list(
    sum(
        [
            (
                State(f"folder-selector{i}", "value"),
                State(f"user-selector{i}", "value"),
                State(f"subfolder{i}", "children"),
                State(f"sensor-selector{i}", "value"),
            )
            for i in range(1, len(name_folders_list) + 1)
        ],
        (),
    )
)


@app.callback(
    Output("trace-updater", "updateData"),
    Input("resampled-graph", "relayoutData"),
    State("store", "data"),
)
def update_graph(relayoutdata: dict, fr: FigureResampler):
    if fr is None or relayoutdata is None:
        raise dash.exceptions.PreventUpdate()
    return fr.construct_update_data(relayoutdata)


@app.callback(
    Output("resampled-graph", "figure"),
    ServersideOutput("store", "data"),
    [
        Input("plot-button", "n_clicks"),
        State("har-checklist", "value"),
        State("session-id", "children"),
        State("start-date", "value"),
        State("end-date", "value"),
        *selector_states,
    ],
)
def plot_or_update_graph(
    n_clicks, har_checklist, session_id, start_date, end_date, *folder_list
):
    har_checklist = [] if har_checklist is None else har_checklist

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
            har_checklist=har_checklist,
            folder_usr_subfold_startdt_enddt_sensor_list=folder_user_day_sensor_list,
            session_id=session_id,
            number_of_samples=1000,
        )
        return fig, fig
    return dash.no_update, dash.no_update


if __name__ == "__main__":
    app.run_server(port=8022, host="0.0.0.0", debug=True)
