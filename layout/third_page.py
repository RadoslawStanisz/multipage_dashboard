
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
from helpers.figures import gen_pie_charts, page_3_chart_7
from helpers.data_loading import load_data_from_files, prepare_data

file_contents, station_coords, df0 = load_data_from_files()
df = df0.copy()

processed_data = prepare_data(df)

refund = processed_data['refund']
introduction_3 = file_contents['introduction_3']

style = {'textAlign': 'center', 'color': '#800080', 'font-family': 'Arial, sans-serif'}

third_page_layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(html.H4(dcc.Markdown(introduction_3), style={'textAlign': 'justify', 'color': '#800080', 'font-family': 'Arial, sans-serif', 'font-size': '20px'}), width=12),
                html.Br(),
                html.Br(),
                html.Br(),
                dbc.Col(
                    [
                        html.H4("Refund requests by Journey Status", style=style),
                        html.Div(dcc.Graph(figure=gen_pie_charts(refund, 'Journey Status')))
                    ],
                    width=3
                ),
                dbc.Col(
                    [
                        html.H4("Tickets sold by ticket type", style=style),
                        html.Div(dcc.Graph(figure=gen_pie_charts(df, 'Ticket Type')))
                    ],
                    width=3
                ),
                dbc.Col(
                    [
                        html.H4("Tickets sold by ticket class", style=style),
                        html.Div(dcc.Graph(figure=gen_pie_charts(df, 'Ticket Class')))
                    ],
                    width=3
                ),
                dbc.Col(
                    [
                        html.H4("Tickets sold by railcard type", style=style),
                        html.Div(dcc.Graph(figure=gen_pie_charts(df, 'Railcard')))
                    ],
                    width=3
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H4("Tickets sold by purchase type", style=style),
                        html.Div(dcc.Graph(figure=gen_pie_charts(df, 'Purchase Type')))
                    ],
                    width=3
                ),
                dbc.Col(
                    [
                        html.H4("Tickets sold by payment method", style=style),
                        html.Div(dcc.Graph(figure=gen_pie_charts(df, 'Payment Method')))
                    ],
                    width=3,
                    className="ml-5"
                ),
                dbc.Col(
                    [
                        html.H4("Days between purchase and travel", style=style),
                        html.Div(dcc.Graph(figure=page_3_chart_7(df)))
                    ],
                    width=5
                )
            ]
        )
    ]
)
