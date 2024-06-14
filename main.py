from dash import html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from app import app
from layout.first_page import first_page_layout
from layout.second_page import second_page_layout
from layout.third_page import third_page_layout

server = app.server
app.layout = dbc.Container([
    dcc.Location(id='url', refresh=False),

    dbc.Row(
        dbc.Col(
            dbc.ButtonGroup([
                dbc.Button("Revenue", href='/', color='primary', className='me-2 btn-lg'),
                dbc.Button("Delays", href='/delays_reporting', color='primary', className='me-2 btn-lg'),
                dbc.Button("Customer behavior", href='/customers_reporting', color='primary btn-lg')
            ]),
            width='auto',
            className='d-flex justify-content-center align-items-center'
        ),
        justify='center',
        style={'margin-top': '10px'}
    ),
    html.Br(),
    html.Div(id='page-content', style={'margin-top': '20px'})
], fluid=True)

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/delays_reporting':
        return second_page_layout
    elif pathname == '/customers_reporting':
        return third_page_layout
    else:
        return first_page_layout


if __name__ == '__main__':
    app.run_server(debug=True)
