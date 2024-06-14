

from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
from helpers.figures import create_rush_hours_histogram, create_delays_histogram, generate_pie_chart, generate_bar_chart, create_scatter, create_data_table
from helpers.data_loading import load_data_from_files, prepare_data

file_contents, station_coords, df0 = load_data_from_files()
df = df0.copy()

processed_data = prepare_data(df)

introduction_2 = file_contents['introduction_2']
rush_hours = processed_data['rush_hours']
all_delayed_departures2 = processed_data['all_delayed_departures2']
all_delayed_departures3 = processed_data['all_delayed_departures3']
all_delayed_departures_by_reason = processed_data['all_delayed_departures_by_reason']
ranking = processed_data['ranking']

table2 = html.Div([
    html.H2("Routes reliability", style={'textAlign': 'center', 'color': '#800080', 'font-family': 'Arial, sans-serif'}),
    create_data_table(ranking)
]) 

style = {'textAlign': 'center', 'color': '#800080', 'font-family': 'Arial, sans-serif'}

second_page_layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div([
                            html.Br(),
                            html.H5(dcc.Markdown(introduction_2), style={'textAlign': 'justify', 'margin-right': '40px', 'color': '#800080', 'font-family': 'Arial, sans-serif', 'font-size': '20px'}),
                            html.Br(),
                            html.H3("Peak travel times and journey status by hour of departure", style=style),
                            dcc.Graph(figure=create_rush_hours_histogram(rush_hours)),
                            html.Br(),
                            html.Br(),
                            html.H3("Distribution of delays", style=style),
                            dcc.Graph(figure=create_delays_histogram(all_delayed_departures2)),
                            html.Br(),
                            html.Br(),
                        ]),
                        dbc.Row(
                            [
                                dbc.Col(html.H3("Departure delays by reason", style=style), width=7),
                                dbc.Col(html.H3("Delays percentage by day type", style=style), width=5)
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col(html.Div(dcc.Graph(figure=generate_pie_chart(all_delayed_departures_by_reason))), width=8),
                                dbc.Col(html.Div(dcc.Graph(figure=generate_bar_chart(df))), width=3)
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col(html.Div([
                                    html.H3("Delays vs. Travel duration", style=style),
                                    dcc.Graph(figure=create_scatter(all_delayed_departures3))]))
                            ]
                        )
                    ],
                    width=7
                ),
                dbc.Col(html.Div(table2), width=5)
            ]
        )
    ]
)
