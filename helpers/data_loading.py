
import json
import pandas as pd
import numpy as np


def load_data_from_files():
    file_paths = {
        'introduction': 'Data/dashboard_strings/introduction.txt',
        'description': 'Data/dashboard_strings/description.txt',
        'description2': 'Data/dashboard_strings/description2.txt',
        'introduction_2': 'Data/dashboard_strings/introduction2.txt',
        'introduction_3': 'Data/dashboard_strings/introduction3.txt'
    }

    file_contents = {}
    for key, path in file_paths.items():
        with open(path, 'r', encoding='utf-8') as file:
            file_contents[key] = file.read()

    json_file = "Data/station_coords.json"
    with open(json_file, 'r') as file:
        station_coords = json.load(file)

    df0 = pd.read_csv("Data/railway.csv")

    return file_contents, station_coords, df0



def prepare_data(df):
    
    # Convert dates
    df[['Date of Purchase', 'Date of Journey']] = df[['Date of Purchase', 'Date of Journey']].apply(pd.to_datetime)
    df[['Time of Purchase', 'Departure Time', 'Arrival Time', 'Actual Arrival Time']] = df[['Time of Purchase', 'Departure Time', 'Arrival Time', 'Actual Arrival Time']].apply(pd.to_timedelta)

    # Add new cols
    df['Days_between_purch_trip'] = (df['Date of Journey'] - df['Date of Purchase']).dt.days
    df['Day of Week'] = df['Date of Journey'].dt.day_name()
    df['is weekend'] = df['Day of Week'].isin(['Saturday', 'Sunday'])
    df['Month of Purchase'] = df['Date of Purchase'].dt.month
    df['Week Number'] = df['Date of Purchase'].dt.isocalendar().week
    df['Refund Amount'] = df.apply(lambda row: row['Price'] if row['Refund Request'] == 'Yes' else 0, axis=1)
    df['Net Revenue'] = df['Price'] - df['Refund Amount']
    df['Duration'] = df.apply(lambda row: row['Arrival Time'] + pd.Timedelta(days=1) - row['Departure Time'] if row['Arrival Time'] < row['Departure Time'] else row['Arrival Time'] - row['Departure Time'], axis=1)
    df['Duration'] = df['Duration'].dt.total_seconds() / 60
    df['Delay_min'] = (df['Actual Arrival Time'] - df['Arrival Time']).dt.total_seconds() / 60
    
    #Data cleaning
    df['Reason for Delay'] = df['Reason for Delay'].replace({
        None: 'Unknown',
        'Weather': 'Weather Conditions',
        'Staffing': 'Staff Shortage',
        'Signal failure': 'Signal Failure'
    })
    df.fillna({'Railcard': 'No Railcard'}, inplace=True)
    
    # Filter data
    df_filtered = df[df['Date of Purchase'] >= '2024-01-01']
    df_filtered_ref = df[(df['Date of Purchase'] >= '2024-01-01') & (df['Date of Purchase'] < '2024-04-01')]
    df_ref = df[df['Date of Purchase'] < '2024-04-01']
    refund = df[df['Refund Request'] == 'Yes']
    cancelled_df = df[df['Journey Status'] == 'Cancelled']
    cancelled_df_ref = df[(df['Journey Status'] == 'Cancelled') & (df['Date of Journey'] < '2024-04-01')]
    delayed_df = df[df['Journey Status'] == 'Delayed']
    delayed_df_ref = df[(df['Journey Status'] == 'Delayed') & (df['Date of Journey'] < '2024-04-01')]
    
    # Group data
    cancelled_departures = cancelled_df.groupby(['Departure Station', 'Arrival Destination', 'Date of Journey', 'Departure Time']).size().reset_index(name='Count')
    cancelled_departures_ref = cancelled_df_ref.groupby(['Departure Station', 'Arrival Destination', 'Date of Journey', 'Departure Time']).size().reset_index(name='Count')
    delayed_departures = delayed_df.groupby(['Departure Station', 'Arrival Destination', 'Date of Journey', 'Departure Time']).size().reset_index(name='Count')
    delayed_departures_ref = delayed_df_ref.groupby(['Departure Station', 'Arrival Destination', 'Date of Journey', 'Departure Time']).size().reset_index(name='Count')
    rush_hours=df.groupby(['Departure Station','Arrival Destination','Date of Journey','Departure Time', 'is weekend','Journey Status'])['Transaction ID'].size().reset_index()
    rush_hours['Departure Hour']=rush_hours['Departure Time'].dt.components.hours
    
    # Delays groupings
    all_df = df[df['Journey Status'] != 'Cancelled']
    all_trips = all_df.groupby(['Departure Station', 'Arrival Destination', 'Date of Journey',  'Departure Time', 'Journey Status'])['Transaction ID'].size().reset_index()
    delayed_trips_by_routes = all_trips[all_trips['Journey Status'] == 'Delayed'].groupby(['Departure Station', 'Arrival Destination']).size().reset_index(name='Delayed Departures')
    all_trips_by_routes = all_trips.groupby(['Departure Station', 'Arrival Destination']).size().reset_index(name='All Departures')

    route_stats = pd.merge(all_trips_by_routes, delayed_trips_by_routes, on=['Departure Station', 'Arrival Destination'], how='left')
    route_stats['Delayed Departures'] = route_stats['Delayed Departures'].fillna(0).astype(int)
    route_stats['Delayed Percentage'] = round((route_stats['Delayed Departures'] / route_stats['All Departures']) * 100, 1)

    ranking = route_stats.sort_values(by='Delayed Percentage', ascending=False)
    
    all_delayed_departures_by_reason = df[df['Journey Status'] == 'Delayed'].groupby(['Departure Station','Arrival Destination','Date of Journey','Departure Time', 'Reason for Delay'])['Transaction ID'].size().reset_index()
    all_delayed_departures2 = df[df['Journey Status'] == 'Delayed'].groupby(['Departure Station','Arrival Destination','Date of Journey','Departure Time', 'Delay_min'])['Transaction ID'].size().reset_index()
    all_delayed_departures3 = df[df['Journey Status'] == 'Delayed'].groupby(['Departure Station','Arrival Destination','Date of Journey','Departure Time', 'Delay_min', 'Duration'])['Transaction ID'].size().reset_index()

    #KPI
    T_Rev = df_filtered['Price'].sum()
    N_Rev = df_filtered['Net Revenue'].sum()
    Tickets = len(df['Transaction ID'].unique())
    Cancelled = len(cancelled_departures)
    Delayed = len(delayed_departures)
    Routes = df.groupby(['Departure Station', 'Arrival Destination']).size().reset_index().shape[0]

    T_Rev_ref = df_filtered_ref['Price'].sum()
    N_Rev_ref = df_filtered_ref['Net Revenue'].sum()
    Tickets_ref = len(df_ref['Transaction ID'].unique())
    Cancelled_ref = len(cancelled_departures_ref)
    Delayed_ref = len(delayed_departures_ref)
    Routes_ref = df_ref.groupby(['Departure Station', 'Arrival Destination']).size().reset_index().shape[0]
    
    # Pivots
    df_pivot_monthly = pd.pivot_table(df_filtered, index=['Month of Purchase', 'Ticket Class'], columns='Ticket Type', values='Price', aggfunc='sum')
    df_pivot_monthly['Subtotal'] = df_pivot_monthly.sum(axis=1)
    df_pivot_monthly.loc[('Subtotal', ''), :] = df_pivot_monthly.sum()
    df_pivot_monthly['Change rate [%]'] = ((df_pivot_monthly['Subtotal'] - df_pivot_monthly['Subtotal'].shift(2)) / df_pivot_monthly['Subtotal'].shift(2)) * 100
    df_pivot_monthly['Change rate [%]'] = df_pivot_monthly['Change rate [%]'].round(1)
    df_pivot_monthly.loc['Subtotal', 'Change rate [%]'] = None

    month_map = {1: 'January', 2: 'February', 3: 'March', 4: 'April'}
    df_pivot_monthly_reset = df_pivot_monthly.reset_index()
    df_pivot_monthly_reset['Month of Purchase'] = df_pivot_monthly_reset['Month of Purchase'].map(month_map)

    # Prepare df_pivot for weekly aggregation
    df_pivot_weekly = pd.pivot_table(df_filtered, index=['Week Number', 'Ticket Class'], columns='Ticket Type', values='Price', aggfunc='sum')
    df_pivot_weekly['Subtotal'] = df_pivot_weekly.sum(axis=1)
    df_pivot_weekly.loc[('Subtotal', ''), :] = df_pivot_weekly.sum()
    df_pivot_weekly['Change rate [%]'] = ((df_pivot_weekly['Subtotal'] - df_pivot_weekly['Subtotal'].shift(2)) / df_pivot_weekly['Subtotal'].shift(2)) * 100
    df_pivot_weekly['Change rate [%]'] = df_pivot_weekly['Change rate [%]'].round(1)
    df_pivot_weekly.loc['Subtotal', 'Change rate [%]'] = None
    df_pivot_weekly_reset = df_pivot_weekly.reset_index()
    
    return {
    'df': df,
    'ranking': ranking,
    'rush_hours': rush_hours,
    'all_delayed_departures2': all_delayed_departures2,
    'all_delayed_departures3': all_delayed_departures3,
    'all_delayed_departures_by_reason': all_delayed_departures_by_reason,
    'refund': refund,
    'df_filtered': df_filtered,
    'df_filtered_ref': df_filtered_ref,
    'df_ref': df_ref,
    'cancelled_departures': cancelled_departures,
    'cancelled_departures_ref': cancelled_departures_ref,
    'delayed_departures': delayed_departures,
    'delayed_departures_ref': delayed_departures_ref,
    'T_Rev': T_Rev,
    'N_Rev': N_Rev,
    'Tickets': Tickets,
    'Cancelled': Cancelled,
    'Delayed': Delayed,
    'Routes': Routes,
    'T_Rev_ref': T_Rev_ref,
    'N_Rev_ref': N_Rev_ref,
    'Tickets_ref': Tickets_ref,
    'Cancelled_ref': Cancelled_ref,
    'Delayed_ref': Delayed_ref,
    'Routes_ref': Routes_ref,
    'df_pivot_monthly_reset': df_pivot_monthly_reset,
    'df_pivot_weekly_reset': df_pivot_weekly_reset

    }
