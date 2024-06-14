
import plotly.graph_objs as go
import plotly.express as px
from dash import dash_table
import pandas as pd
import dash_cytoscape as cyto
from dash.dependencies import Input, Output
from helpers.data_loading import load_data_from_files, prepare_data


file_contents, station_coords, df0 = load_data_from_files()
df = df0.copy()
processed_data = prepare_data(df)


df_pivot_monthly_reset = processed_data['df_pivot_monthly_reset']
df_pivot_weekly_reset = processed_data['df_pivot_weekly_reset']



def generate_cytoscape_graph(station_labels):
    return cyto.Cytoscape(
        id='cytoscape-simple-graph',
        style={'width': '100%', 'height': '100vh'},
        layout={'name': 'preset'},
        stylesheet=[
            {
                'selector': 'node',
                'style': {
                    'width': 'data(width)',
                    'height': 'data(height)',
                    'background-color': '#800080',
                    'color': '#000',
                    'font-family': 'Arial, sans-serif',
                    'font-size': '10px',
                    'text-opacity': 0,
                    'shape': 'ellipse'
                }
            },
            {
                'selector': '.station',
                'style': {
                    'font-size': '18px',
                    'font-family': 'Arial, sans-serif',
                    'text-opacity': 1,
                }
            },
            *[
                {
                    'selector': f'.{station.lower().replace(" ", "_")}',
                    'style': {
                        'label': details['label'],
                        'text-halign': details.get('text-halign', 'center'),
                        'text-valign': details.get('text-valign', 'top'),
                        'font-family': 'Arial, sans-serif'
                    }
                } for station, details in station_labels.items()
            ],
            {
                'selector': '.top-route',
                'style': {
                    'line-color': '#FF4136',
                    'width': 'data(width)',
                    'target-arrow-color': '#FF4136',
                    'target-arrow-shape': 'triangle',
                    'arrow-scale': 1.2,
                    'curve-style': 'bezier'
                }
            },
            {
                'selector': 'edge',
                'style': {
                    'line-color': '#888',
                    'width': 'data(width)',
                    'curve-style': 'bezier'
                }
            }
        ],
        userZoomingEnabled=False,
        userPanningEnabled=False
    )


def create_rush_hours_histogram(df):
    
    fig_rush_hours = px.histogram(df, 
                   x='Departure Hour', 
                   color='Journey Status',
                   labels={'Departure Hour': 'Departure time (hour)', 'count': 'count'},
                   title=None,
                   barmode='stack',  
                   color_discrete_sequence=['#800080', '#EF553B', '#FFD700'] 
                  )

    fig_rush_hours.update_layout(
    bargap=0.2,  
    font={'family': 'Arial, sans-serif', 'size': 14},
    plot_bgcolor='white',  
    paper_bgcolor='white',
    legend=dict(
        orientation='h',  
        yanchor='bottom',  
        y=1.02,
        x=0.36,
        title=None,
        font=dict(size=14)
    ),
    xaxis=dict(
        tickmode='array',  
        tickvals=list(range(0, 24)),  
        ticktext=list(range(0, 24)),  
        range=[-1, 24],  
        )
    )
    fig_rush_hours.update_traces(textfont_size=14)
    fig_rush_hours.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
    fig_rush_hours.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')

    return fig_rush_hours

def create_delays_histogram(df):

    fig_all_delayed_departures2 = px.histogram(
                  df, 
                  x='Delay_min',     
                  labels={'Delay_min': 'Delay [minutes]'}, 
                  title=None, 

                  color_discrete_sequence=['#800080'],
                  )

    fig_all_delayed_departures2.update_layout(
                bargap=0.4,  
                font={'family': 'Arial, sans-serif', 'size': 14},
                plot_bgcolor='white',  
                paper_bgcolor='white',
                yaxis_title='count',
                legend=dict(font=dict(size=14))
                )
        
    fig_all_delayed_departures2.update_traces(textfont_size=14)
    fig_all_delayed_departures2.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
    fig_all_delayed_departures2.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
    
    return fig_all_delayed_departures2

def generate_bar_chart(df):
  
    all_departures = df[df['Journey Status'] != 'Cancelled'].groupby(['Departure Station','Arrival Destination','Date of Journey','Departure Time', 'is weekend','Journey Status'])['Transaction ID'].size().reset_index()
    all_delayed_departures = df[df['Journey Status'] == 'Delayed'].groupby(['Departure Station','Arrival Destination','Date of Journey','Departure Time', 'is weekend'])['Transaction ID'].size().reset_index()
    all_delayed_departures.shape[0]/all_departures.shape[0]
    weekend= all_delayed_departures[all_delayed_departures['is weekend'] == True].shape[0]/all_departures[all_departures['is weekend'] == True].shape[0]
    workday = all_delayed_departures[all_delayed_departures['is weekend'] == False].shape[0]/all_departures[all_departures['is weekend'] == False].shape[0]
    
    data = {
    'Category': ['Weekend', 'Weekday'],
    'Value': [weekend, workday]
    }

    delays_by_weekend = pd.DataFrame(data)

    fig = px.bar(delays_by_weekend, x='Category', y='Value', color='Category',
                 labels={'Category': '', 'Value': 'Delays Rate'},
                 color_discrete_sequence=['#800080', 'green'])

    fig.update_layout(
        font={'family': 'Arial, sans-serif', 'size': 14},
        plot_bgcolor='white',  
        paper_bgcolor='white',
        title=None,
        showlegend=False
    )
    
    return fig


def generate_pie_chart(df):

    fig_all_delayed_departures_by_reason = df['Reason for Delay'].value_counts()
    fig = px.pie(
        names=fig_all_delayed_departures_by_reason.index,
        values=fig_all_delayed_departures_by_reason.values,
        title=None,
        hole=0.4,
        color_discrete_sequence = ['#AB63FA', 'blue', '#FFA15A', 'green', '#B6E880']
    )
    
    fig.update_traces(
        textinfo='percent+label',
        textposition='outside',
        textfont_size=14
    )
    
    fig.update_layout(
        showlegend=False
        )
    
    
    return fig

def create_scatter(df):
    fig = px.scatter(df, x='Duration', y='Delay_min', color_discrete_sequence=['blue'])
    
    fig.update_layout(
        plot_bgcolor='white', 
        paper_bgcolor='white',
        font={'family': 'Arial, sans-serif', 'size': 14},
        xaxis_title='Travel duration (minutes)',  
        yaxis_title='Delay (minutes)'     
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
    
    return fig


def gen_pie_charts(df, column):
    """
    Generate a pie chart based on the specified column of the DataFrame.

    Args:
    - df (DataFrame): DataFrame containing the data.
    - column (str): Name of the column in the DataFrame.

    Returns:
    - fig (plotly.graph_objects.Figure): Plotly figure object.
    """
    value_counts = df[column].value_counts()

    fig = px.pie(
        names=value_counts.index,
        values=value_counts.values,
        title=None,
        hole=0.4,
        color_discrete_sequence=['#AB63FA', 'blue', '#FFA15A', 'green', '#B6E880']
    )
    fig.update_traces(textfont_size=14)
    fig.update_layout(
        legend=dict(
            font=dict(size=14)
        )
    )

    return fig


def page_3_chart_7(df):
    
    days_between = px.histogram(df, 
        x='Days_between_purch_trip',     
        labels={'Days_between_purch_trip': 'Days between purchase and travel'}, 
        title=None, 
        color_discrete_sequence=['#800080'])

    days_between.update_layout(
        bargap=0.4,  
        font={'family': 'Arial, sans-serif', 'size': 14},
        plot_bgcolor='white',  
        paper_bgcolor='white',
        yaxis_title='Frequency',
        yaxis_type='log',
        yaxis=dict(
            range=[1, 5],  
            tickvals=[10, 100, 1000, 10000, 100000],  
            ticktext=['10', '100', '1000', '10000']  
        )
    )

    return days_between

def generate_datatable(aggregation):
    if aggregation == 'monthly':
        df = df_pivot_monthly_reset
        columns = [
            {'name': 'Month', 'id': 'Month of Purchase'},
            {'name': 'Ticket Class', 'id': 'Ticket Class'}
        ]
    elif aggregation == 'weekly':
        df = df_pivot_weekly_reset
        columns = [
            {'name': 'Week', 'id': 'Week Number'},
            {'name': 'Ticket Class', 'id': 'Ticket Class'}
        ]
    columns += [{'name': col, 'id': col} for col in df.columns if col not in ['Month of Purchase', 'Week Number', 'Ticket Class']]
    
    datatable = dash_table.DataTable(
    id='datatable',
    columns=columns,
    data=df.to_dict('records'),
    style_table={'overflowX': 'auto'},
    style_cell={'minWidth': '100px', 'width': '100px', 'maxWidth': '100px', 'textAlign': 'center', 'font-family': 'Arial, sans-serif', 'font-size': '18px'},  # Zwiększono rozmiar czcionki do 16px
    style_cell_conditional=[
        {'if': {'column_id': 'Month of Purchase'}, 'textAlign': 'left'},
        {'if': {'column_id': 'Ticket Class'}, 'textAlign': 'left'}
    ],
    style_header={'fontWeight': 'bold'},  
    editable=False,
    filter_action='native',
    sort_action='native',
    export_format='xlsx',
    export_headers='display',
    merge_duplicate_headers=True,  
        style_data_conditional=[
            {
                'if': {
                    'filter_query': '{Change rate [%]} > 0',
                    'column_id': 'Change rate [%]'
                },
                'backgroundColor': '#32CD32',
                'color': 'white'
            },
            {
                'if': {
                    'filter_query': '{Change rate [%]} < 0',
                    'column_id': 'Change rate [%]'
                },
                'backgroundColor': '#FF4136',
                'color': 'white'
            }
        ]
    )
    return datatable



def create_data_table(df):
    return dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'),
        style_table={'overflowX': 'auto'},
        style_cell={
            'textAlign': 'left',
            'fontFamily': 'Arial, sans-serif',
            'fontSize': '18px',
            'padding': '5px',
        },
        style_header={
            'backgroundColor': '#800080',
            'color': 'white',
            'fontWeight': 'bold',
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }
        ],
    )

def aggregate_data(df, interval):
    if interval == 'Monthly':
        df_agg = df.resample('ME', on='Date of Purchase').sum(numeric_only=True).reset_index()
    elif interval == 'Weekly':
        df_filtered_weekly = df[df['Week Number'] <= 17]
        df_agg = df_filtered_weekly.resample('W', on='Date of Purchase').sum(numeric_only=True).reset_index()
    elif interval == 'Daily':
        df_agg = df.resample('D', on='Date of Purchase').sum(numeric_only=True).reset_index()
    return df_agg

