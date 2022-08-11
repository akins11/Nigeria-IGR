import dash
from dash import dcc, html
import dash_bootstrap_components as dbc



def dropdown_menu(drop_radio_id):
    return dbc.DropdownMenu(
            [
                dbc.DropdownMenuItem(
                    [
                        dbc.RadioItems(
                            id = drop_radio_id,
                            options = [
                                {"label": "First Quarter", "value": "q1"},
                                {"label": "Second Quarter", "value": "q2"},
                                {"label": "Half Year", "value": "half_year"}
                            ],
                            value= "q1"
                        )
                    ]
                )
            ],
            label = "Select Period",
        )


def state_zone_radioitem(radio_id, selected = "State"):
    return  dbc.RadioItems(
            id = radio_id,
            options=[
                {"label": "State", "value": "State"},
                {"label": "Zone", "value": "Zone"}
            ],
            value = selected,
            inline = True
        )


def create_graph(graph_object):
    return html.Div(
        [
            dcc.Graph(
                figure = graph_object,
                config={
                    "displaylogo": False,
                    "modeBarButtonsToRemove": ["pan2d", "lasso2d", "zoomIn2d", "zoomOut2d", "zoom2d", "toImage",
                                               "select2d", "autoScale2d"]
                }
            )
        ],
    )