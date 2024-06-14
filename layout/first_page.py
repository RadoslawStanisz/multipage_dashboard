
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import plotly.graph_objects as go
from helpers.figures import aggregate_data, generate_datatable, generate_cytoscape_graph
from helpers.data_loading import load_data_from_files, prepare_data
from app import app
from dash.dependencies import Input, Output

file_contents, station_coords, df0 = load_data_from_files()
df = df0.copy()

processed_data = prepare_data(df)

indicators = [
    "Total Revenue",
    "Net Revenue",
    "Tickets sold",
    "Cancelled travels",
    "Delayed travels",
    "Routes"
]

T_Rev = processed_data['T_Rev'] 
N_Rev = processed_data['N_Rev'] 
Tickets = processed_data['Tickets'] 
Cancelled = processed_data['Cancelled'] 
Delayed = processed_data['Delayed'] 
Routes = processed_data['Routes'] 
T_Rev_ref = processed_data['T_Rev_ref'] 
N_Rev_ref = processed_data['N_Rev_ref'] 
Tickets_ref = processed_data['Tickets_ref'] 
Cancelled_ref = processed_data['Cancelled_ref'] 
Delayed_ref = processed_data['Delayed_ref'] 
Routes_ref = processed_data['Routes_ref'] 

values = [T_Rev, N_Rev, Tickets, Cancelled, Delayed, Routes]
values_ref = [T_Rev_ref, N_Rev_ref, Tickets_ref, Cancelled_ref, Delayed_ref, Routes_ref]

introduction = file_contents['introduction']
description = file_contents['description']
description2 = file_contents['description2']
df_filtered = processed_data['df_filtered']

df_pivot_monthly_reset = processed_data['df_pivot_monthly_reset']
df_pivot_weekly_reset = processed_data['df_pivot_weekly_reset']

station_labels = {
    'London Paddington': {'label': 'London', 'text-valign': 'top', 'text-halign': 'right'},
    'Cardiff Central': {'label': 'Cardiff'},
    'Liverpool Lime Street': {'label': 'Liverpool', 'text-halign': 'left'},
    'York': {'label': 'York'},
    'Manchester Piccadilly': {'label': 'Manchester'},
    'Oxford': {'label': 'Oxford'},
    'Birmingham New Street': {'label': 'Birmingham', 'text-valign': 'bottom', 'text-halign': 'left'},
    'Reading': {'label': 'Reading', 'text-valign': 'bottom'},
    'Durham': {'label': 'Durham'},
    'Edinburgh Waverley': {'label': 'Edinburgh'}
}

def create_kpi_section():
    fig = go.Figure()
    for i in range(6):
        fig.add_trace(go.Indicator(
            mode="number+delta",
            value=values[i],
            title={"text": indicators[i]},
            delta={'reference': values_ref[i], 'relative': True, 'valueformat':'.2%'},
            domain={'x': [i / 6, (i + 1) / 6], 'y': [0, 1]}
        ))
    fig.update_layout(
        font={'family': 'Arial, sans-serif'},
        height=250,
        plot_bgcolor='#FFD700',  
        paper_bgcolor='#FFD700'  
    )
    return fig


cytoscape_graph = html.Div([
    html.H2('Most popular routes', style={'textAlign': 'center', 'color': '#800080', 'font-family': 'Arial, sans-serif'}),
    html.H5('Choose the scope', style={'color': '#800080', 'font-family': 'Arial, sans-serif'}),
    dcc.Dropdown(
        id='route-selection',
        options=[
            {'label': 'Top 10', 'value': 10},
            {'label': 'Top 30', 'value': 30},
            {'label': 'All', 'value': 'all'}
        ],
        value=10,
        clearable=False,
        style={'width': '50%', 'color': '#6c757d'}
    ),
    html.Br(),
    html.Div(id='hoverNode', style={'font-size': '20px', 'font-family': 'Arial, sans-serif'}),
    html.Div(id='hoverEdge', style={'font-size': '20px', 'font-family': 'Arial, sans-serif'}),
    generate_cytoscape_graph(station_labels)
])

@app.callback(
    Output('cytoscape-simple-graph', 'elements'),
    Input('route-selection', 'value')
)
def update_elements(selected_value):
    if selected_value == 'all':
        top_routes = df.groupby(['Departure Station', 'Arrival Destination'])['Transaction ID'].count().reset_index(name='Tickets Sold').sort_values(by='Tickets Sold', ascending=False)
    else:
        top_routes = df.groupby(['Departure Station', 'Arrival Destination'])['Transaction ID'].count().reset_index(name='Tickets Sold').sort_values(by='Tickets Sold', ascending=False).head(selected_value)

    nodes = []
    scale = 200
    for station, coords in station_coords.items():
        node_class = 'station'
        if station in station_labels:
            node_class += ' ' + station.lower().replace(' ', '_')
        nodes.append({
            'data': {'id': station, 'label': station, 'width': 20, 'height': 20},
            'position': {'x': coords[1] * scale, 'y': -coords[0] * scale},
            'classes': node_class
        })

    edges = []
    for _, row in top_routes.iterrows():
        route = (row['Departure Station'], row['Arrival Destination'])
        edges.append({
            'data': {'source': route[0], 'target': route[1], 'label': f"{route[0]} --> {route[1]}", 'Tickets Sold': row['Tickets Sold'], 'width': 2},
            'classes': 'top-route'
        })

    return nodes + edges

@app.callback(
    Output('hoverNode', 'children'),
    Input('cytoscape-simple-graph', 'mouseoverNodeData')
)
def display_hover_node_data(data):
    if data:
        return "Station: %s" % data['label']

@app.callback(
    Output('hoverEdge', 'children'),
    Input('cytoscape-simple-graph', 'mouseoverEdgeData')
)
def display_hover_edge_data(data):
    if data:
        label = data['label']
        tickets_sold = data['Tickets Sold'] if 'Tickets Sold' in data else None
        if tickets_sold:
            return "Route: %s, Tickets Sold: %s" % (label, tickets_sold)
        else:
            return "Route: %s" % label
        
table = html.Div([
    html.H3("Revenue by ticket type and class", style={'textAlign': 'center', 'color': '#800080', 'font-family': 'Arial, sans-serif'}),
    html.H5("Choose time interval", style={'color': '#800080', 'font-family': 'Arial, sans-serif'}),
    dcc.Dropdown(
        id='aggregation-dropdown',
        options=[
            {'label': 'Monthly', 'value': 'monthly'},
            {'label': 'Weekly', 'value': 'weekly'}
        ],
        value='monthly',
        clearable=False,
        style={'width': '50%'}
    ),
    html.Br(),
    html.Div(id='datatable-container')
])


@app.callback(
    Output('datatable-container', 'children'),
    Input('aggregation-dropdown', 'value')
)
def update_datatable(aggregation):
    return generate_datatable(aggregation)


revenue_variability = html.Div([
    html.H3("Revenue variability", style={'textAlign': 'center', 'color': '#800080', 'font-family': 'Arial, sans-serif'}),
    html.H5("Choose time interval", style={'color': '#800080', 'font-family': 'Arial, sans-serif'}), 
    dcc.Dropdown(
        id='interval-dropdown',
        options=[
            {'label': 'Monthly', 'value': 'Monthly'},
            {'label': 'Weekly', 'value': 'Weekly'},
            {'label': 'Daily', 'value': 'Daily'}
        ],
        value='Monthly',
        clearable=False,
        style={'width': '50%'}
    ),
    dcc.Graph(id='revenue-graph', style={'width': '100%', 'height':'50vh'}),
    html.Br(),
    html.Br()
])

@app.callback(
    Output('revenue-graph', 'figure'),
    Input('interval-dropdown', 'value')
)
def update_graph(selected_interval):
    df_agg = aggregate_data(df_filtered, selected_interval)

    trace1 = go.Scatter(
        x=df_agg['Date of Purchase'],
        y=df_agg['Price'],
        mode='lines',
        name='Total Revenue',
        line=dict(color='green')
    )

    trace2 = go.Scatter(
        x=df_agg['Date of Purchase'],
        y=df_agg['Net Revenue'],
        mode='lines',
        name='Net Revenue',
        line=dict(color='#800080')
    )

    layout = go.Layout(
        title=None,
        xaxis={'title': 'Date', 'gridcolor': 'lightgrey', 'gridwidth': 1, 'showline': False},
        yaxis={'title': 'Revenue', 'gridcolor': 'lightgrey', 'gridwidth': 1},
        font={'family': 'Arial, sans-serif', 'size': 18},
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    return {'data': [trace1, trace2], 'layout': layout}

cumulative_revenue_daily = html.Div([
    html.H3("Cumulative revenue by ticket type and class (Daily)", style={'textAlign': 'center', 'color': '#800080', 'font-family': 'Arial, sans-serif'}),
    html.H5("Choose parameter", style = {'color': '#800080', 'font-family': 'Arial, sans-serif'}),
    dcc.Dropdown(
        id='revenue-type',
        options=[
            {'label': 'Ticket Type', 'value': 'Ticket Type'},
            {'label': 'Ticket Class', 'value': 'Ticket Class'}
        ],
        value='Ticket Type',
        clearable=False,
        style={'width': '50%'}
    ),
    dcc.Graph(id='revenue-graph2', style={'width': '100%','height':'50vh'})
])

@app.callback(
    Output('revenue-graph2', 'figure'),
    Input('revenue-type', 'value')
)
def update_figure(selected_type):
    daily_revenue = df_filtered.groupby(['Date of Purchase', selected_type]).agg({'Price': 'sum'}).reset_index()
    daily_revenue = daily_revenue.rename(columns={'Price': 'Revenue'})

    daily_revenue['Date of Purchase'] = pd.to_datetime(daily_revenue['Date of Purchase'])
    daily_revenue = daily_revenue.sort_values(by='Date of Purchase')

    daily_revenue['Cumulative Revenue'] = daily_revenue.groupby(selected_type)['Revenue'].cumsum()

    fig_cum = px.line(daily_revenue, x='Date of Purchase', y='Cumulative Revenue', color=selected_type,
                      labels={'Date of Purchase': 'Date', 'Cumulative Revenue': 'Cumulative Revenue', selected_type: selected_type},
                      color_discrete_sequence=['#800080', 'orange', 'green'])

    fig_cum.update_layout(
        title=None,
        font={'family': 'Arial, sans-serif', 'size': 18},
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    fig_cum.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
    fig_cum.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')

    return fig_cum


style = {'textAlign': 'center', 'color': '#800080', 'font-family': 'Arial, sans-serif'}
markdown_style = {'textAlign': 'justify', 'margin-right': '30px', 'color': '#800080', 'font-family': 'Arial, sans-serif', 'font-size': '20px'}


first_page_layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(html.H1("UK National Rail Dashboard", style={'textAlign': 'center', 'color': '#800080', 'font-family': 'Arial, sans-serif', 'fontSize': '62px'}), width=12)
            ]
        ),
        html.Br(),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(html.H5(dcc.Markdown(introduction, style={'textAlign': 'justify', 'color': '#800080', 'font-family': 'Arial, sans-serif', 'font-size': '20px'})), width=12)
            ]
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(html.Div(dcc.Graph(figure=create_kpi_section(), style={'margin': 'auto'})), width=12)
            ],
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(html.Div(cytoscape_graph), width=6),
                dbc.Col(
                    [
                        html.Div(revenue_variability),
                        html.Div(cumulative_revenue_daily)
                    ],
                    width=6
                )
            ]
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H3("How to use this dashboard?", style={'textAlign': 'left', 'color': '#800080', 'font-family': 'Arial, sans-serif'}),
                        html.Br(),
                        dcc.Markdown(description, style=markdown_style),
                        dcc.Markdown(description2, style=markdown_style)
                    ],
                    width=5
                ),
                dbc.Col(
                    html.Div(table),
                    width=7,
                    className="mx-auto"
                ),
            ],
            className="d-flex justify-content-end" 
        )
    ]
)
