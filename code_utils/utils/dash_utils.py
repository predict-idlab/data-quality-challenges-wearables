# -*- coding: utf-8 -*-
"""
"""

from pathlib import Path
from typing import Dict, List

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State
from functional import seq
from plotly_resampler import FigureResampler
from trace_updater import TraceUpdater

__author__ = "Jonas Van Der Donckt"


def serve_layout(app, title, checklist_options, name_folders_list) -> dbc.Container:
    """Constructs the app's layout.

    Returns
    -------
    A Container withholding the layout.
    """
    center = {"textAlign": "center"}
    # fmt: off
    return dbc.Container([
        dbc.Container(html.H1(title), style=center),
        html.Hr(),
        dbc.Row([
            # COL 1: the selection widgets
            dbc.Col(
                multiple_folder_user_date_range_sensor_selector(app, checklist_options, name_folders_list),
                md=2,
            ),
            # COL 2: the visualization
            dbc.Col([
                dcc.Graph(id="resampled-graph"),
                dcc.Loading(dcc.Store(id="store")),
                TraceUpdater(id="trace-updater", gdID="resampled-graph", sequentialUpdate=False),
            ], md=10)
        ],
        # align="center",
        )],
        fluid=True,
    )
    # fmt: on


def get_selector_states(name_folders_list) -> List[State]:
    """Returns the states of the folder, user, date and sensor selectors.

    This can then be used to construct the callback.
    """
    return list(
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


def _create_subfolder_dict(
    subfolder_str, inter_folder_sep=";", intra_folder_subfolder_sep=","
) -> dict:
    folder_subfolder_dict = {}
    for folder_subfolder in subfolder_str.split(inter_folder_sep):
        if len(folder_subfolder.split(intra_folder_subfolder_sep)) == 2:
            f, sub_f = folder_subfolder.split(",")
            folder_subfolder_dict[f] = sub_f
    return folder_subfolder_dict


def _update_user_widget(folder: Path, reverse=True):
    if folder is None:
        return []
    return [
        {"label": username, "value": username}
        for username in sorted(
            set(
                list(
                    seq(Path(folder).iterdir())
                    .filter(lambda x: x.is_dir())
                    .map(lambda x: x.name)
                )
            ),
            reverse=reverse,
        )
    ]


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


def _update_sensor_widget(user, date, folder, sub_folders=""):
    if folder is None or user is None or date is None:
        return []

    folder_subfolder_dict = _create_subfolder_dict(sub_folders)
    sensors = sorted(
        list(
            seq(
                Path(folder)
                .joinpath(user)
                .joinpath(folder_subfolder_dict.get(folder, ""))
                .glob(f"*{date}*")
            ).map(lambda x: "_".join(x.name.split("_")[:-3]))
        ),
        reverse=True,
    )
    print("sensors", sensors)
    return [{"label": sensor_str, "value": sensor_str} for sensor_str in sensors]


def _register_selection_callbacks(app, ids=None):
    if ids is None:
        ids = [""]

    user_folder_inputs_subfolder_states = list(
        sum(
            [
                (
                    Input(f"user-selector{_id}", "value"),
                    Input(f"folder-selector{_id}", "value"),
                )
                for _id in ids
            ],
            (),
        )
    )

    # states must come after subfolders -> hence the weird order of not grouping
    user_folder_inputs_subfolder_states += (
        [State(f"subfolder{_id}", "children") for _id in ids],
    )

    def reorder_user_folder_subfolder(*args):
        offset = len(args) // 3
        return [
            (args[2 * i], args[2 * i + 1], args[offset * 2 + i])
            for i in range(len(args) // 3)
        ]

    app.callback(Output("start-date", "options"), *user_folder_inputs_subfolder_states)(
        lambda *x: _update_date_widget(reorder_user_folder_subfolder(*x), reverse=False)
    )
    app.callback(Output("end-date", "options"), *user_folder_inputs_subfolder_states)(
        lambda *x: _update_date_widget(reorder_user_folder_subfolder(*x), reverse=False)
    )

    for id in ids:
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


def multiple_folder_user_date_range_sensor_selector(
    app, checklist_options, name_folders_list: List[Dict[str, dict]]
) -> dbc.Card:
    """Constructs a folder user date selector

    Creates a `dbc.Card` component which can be

    Parameters
    ----------
    app:
        The dash application.
    name_folders_list:List[Dict[str, Union[Path, str]]]
    TODO
         A dict with key, the display-key and values the corresponding path.

    Returns
    -------
    A bootstrap card component
    """
    selector = dbc.Card(
        [
            dbc.Form(
                [
                    dbc.Label("date", style={"textAlign": "center"}),
                    dcc.Dropdown(id="start-date", options=[], clearable=False),
                    dbc.Label("end", style={"textAlign": "center"}),
                    dcc.Dropdown(id="end-date", options=[], clearable=False),
                    html.Br(),
                    dcc.Checklist(id="checklist", options=checklist_options),
                    html.Br(),
                ]
            ),
            html.Br(),
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
                                    {"label": label, "value": str(f["user_folder"])}
                                    for (label, f) in name_folders.items()
                                ],
                                clearable=True,
                            ),
                            # a div with stored 'folder_name',"sub_folder";...
                            html.Div(
                                ";".join(
                                    [
                                        str(f["user_folder"])
                                        + ","
                                        + str(f.get("sub_folder", ""))
                                        for (_, f) in name_folders.items()
                                    ]
                                ),
                                id=f"subfolder{i}",
                                style={"display": "none"},
                            ),
                            dbc.Label("User:"),
                            dcc.Dropdown(
                                id=f"user-selector{i}", options=[], clearable=False
                            ),
                            dbc.Label("Sensors:"),
                            dcc.Dropdown(
                                id=f"sensor-selector{i}", options=[], multi=True
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
    )

    _register_selection_callbacks(app=app, ids=range(1, len(name_folders_list) + 1))

    # Also add the figure update callback
    @app.callback(
        Output("trace-updater", "updateData"),
        Input("resampled-graph", "relayoutData"),
        State("store", "data"),
    )
    def update_graph(relayoutdata: dict, fr: FigureResampler):
        if fr is None or relayoutdata is None:
            raise dash.exceptions.PreventUpdate()
        return fr.construct_update_data(relayoutdata)

    return selector
