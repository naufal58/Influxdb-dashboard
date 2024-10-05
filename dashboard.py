import dash
from functools import lru_cache
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests

app = dash.Dash(__name__)

# Layout aplikasi Dash dengan styling yang diperbaiki
app.layout = html.Div([
    # Title
    html.H1("Data Explorer", style={'text-align': 'left', 'color': '#FFFFFF', 'padding': '20px', 'font-size': '32px', 'font-weight': 'bold'}),

    html.Div([
        html.Div(style={
            'color': 'white', 
            'font-size': '20px', 
            'margin-bottom': '10px'  # Add some space between the label and the dropdown
        }),
        dcc.Dropdown(
            id='visualization-type',
            options=[
                {'label': 'Line Graph', 'value': 'line'},
                {'label': 'Scatter Plot', 'value': 'scatter'}
            ],
            value='line',  # Default to 'line'
            clearable=False,  # Prevents the user from clearing the selected item
            style={  # Set the width to 1/8 of the parent container
                'backgroundColor': '#021526', 
                'color': 'white',
                'border': '1px solid #444',  # Adds a subtle border
                'border-radius': '10px'  # Rounds the corners of the dropdown
            }
        )
    ], style={
        'width': '12.5%',
        'margin': '15px',
        'border-radius': '5px', 
        'margin-bottom': '20px'
    }),

    # Graph or Histogram display
    dcc.Graph(id='influx-data-graph'),

    # Submit button
    html.Div([
        html.Button('Submit', id='submit-button', n_clicks=0, style={
            'backgroundColor': '#0275d8', 
            'color': 'white', 
            'border': 'none', 
            'padding': '12px 24px', 
            'margin': '10px',
            'margin-top': '30px',
            'font-size': '16px',
            'border-radius': '5px',
            'cursor': 'pointer',
            'transition': 'background-color 0.3s'
        })
    ], style={'text-align': 'right'}),

    # Grid layout for the filters
    html.Div([

        # Filter Measurement
        html.Div([
            html.Div('Filter Measurement', className='dropdown-label', style={'margin-bottom': '5px', 'font-size': '20px', 'color': 'white'}),
            dcc.Checklist(
                id='measurement-checklist',
                options=[
                    {'label': 'airSensors', 'value': 'airSensors'}
                ],
                value=[],
                labelStyle={'display': 'block', 'padding': '10px', 'color': 'white'},
                style={'backgroundColor': '#17153b', 'border': 'none', 'margin': '10px', 'border-radius': '10px'}
            )
        ], className='filter-container', style={
            'margin': '10px', 
            'box-shadow': '0 2px 5px rgba(0,0,0,0.1)', 
            'padding': '15px', 
            'border-radius': '10px', 
            'background-color': '#021526',  # Ubah warna latar belakang kontainer
            'transition': 'transform 0.3s',
            'hover': 'transform: scale(1.02)'
        }),
        # Filter Fields
        html.Div([
            html.Div('Filter Fields', className='dropdown-label', style={'margin-bottom': '5px', 'font-size': '20px', 'color': 'white'}),
            dcc.Checklist(
                id='field-checklist',
                options=[
                    {'label': 'co', 'value': 'co'},
                    {'label': 'humidity', 'value': 'humidity'},
                    {'label': 'temperature', 'value': 'temperature'}
                ],
                value=[],
                labelStyle={'display': 'block', 'padding': '10px', 'color': 'white'},
                style={'backgroundColor': '#17153b', 'border': 'none', 'margin': '10px', 'border-radius': '10px'}
            )
        ], className='filter-container', style={
            'margin': '10px', 
            'box-shadow': '0 2px 5px rgba(0,0,0,0.1)', 
            'padding': '15px', 
            'border-radius': '10px', 
            'background-color': '#021526',  # Ubah warna latar belakang kontainer
            'transition': 'transform 0.3s',
            'hover': 'transform: scale(1.02)'
        }),

        # Filter Sensor ID
        html.Div([
            html.Div('Filter Sensor ID', className='dropdown-label', style={'margin-bottom': '5px', 'font-size': '20px', 'color': 'white'}),
            dcc.Checklist(
                id='sensor-id-checklist',
                options=[{'label': sensor_id, 'value': sensor_id} for sensor_id in 
                         ['TLM0100', 'TLM0101', 'TLM0102', 'TLM0103', 
                          'TLM0200', 'TLM0201', 'TLM0202', 'TLM0203']],
                value=[],
                labelStyle={'display': 'block', 'padding': '10px', 'color': 'white'},
                style={'backgroundColor': '#17153b', 'border': 'none', 'margin': '10px', 'border-radius': '10px'}
            )
        ], className='filter-container', style={
            'margin': '10px', 
            'box-shadow': '0 2px 5px rgba(0,0,0,0.1)', 
            'padding': '15px', 
            'border-radius': '10px', 
            'background-color': '#021526',  # Ubah warna latar belakang kontainer
            'transition': 'transform 0.3s',
            'hover': 'transform: scale(1.02)'
        }),

        # Filter Time Range
        html.Div([
            html.Div('Filter Time Range', className='dropdown-label', style={'margin-bottom': '5px', 'font-size': '20px', 'color': 'white'}),
            dcc.Dropdown(
                id='time-range-dropdown',
                placeholder="Select time range",
                options=[
                    {'label': 'Last 1 minute', 'value': '-1m'},
                    {'label': 'Last 5 minutes', 'value': '-5m'},
                    {'label': 'Last 15 minutes', 'value': '-15m'},
                    {'label': 'Last 30 minutes', 'value': '-30m'},
                    {'label': 'Last 1 hour', 'value': '-1h'},
                    {'label': 'Last 6 hours', 'value': '-6h'},
                    {'label': 'Last 12 hours', 'value': '-12h'},
                    {'label': 'Last 24 hours', 'value': '-24h'}
                ],
                value='-1h',
                style={
                    'backgroundColor': '#f8f9fa',
                    'color': 'black',
                    'border-radius': '5px',
                    'padding': '5px'
                }
            )
        ], className='filter-container', style={
            'margin': '10px', 
            'padding': '15px',
            'border-radius': '10px', 
            'background-color': '#021526',  # Ubah warna latar belakang kontainer
            'transition': 'transform 0.3s',
            'hover': 'transform: scale(1.02)'
        }),

    ], style={
        'display': 'grid',
        'grid-template-columns': 'repeat(4, 1fr)',  # 4 kolom untuk filter
        'gap': '10px',
        'margin-top': '20px'
    }),

    dcc.Interval(
        id='interval-component',
        interval=60000,
        n_intervals=0
    )
], style={'backgroundColor': '#0A1F44', 'padding': '20px', 'min-height': '100vh'})


# Callback for updating the graph\
@app.callback(
    Output('influx-data-graph', 'figure'),
    [Input('submit-button', 'n_clicks'),
     Input('visualization-type', 'value')],
    [State('measurement-checklist', 'value'),
     State('field-checklist', 'value'),
     State('sensor-id-checklist', 'value'),
     State('time-range-dropdown', 'value')]
)
def update_graph(n_clicks, visualization_type, measurements, fields, sensor_ids, time_range):
    if n_clicks == 0:
        return go.Figure()

    if not measurements:
        measurements = ['airSensors']
    if not fields:
        fields = ['co', 'temperature', 'humidity']
    if not sensor_ids:
        sensor_ids = ['TLM0100', 'TLM0101', 'TLM0102', 'TLM0103', 
                      'TLM0200', 'TLM0201', 'TLM0202', 'TLM0203']

    traces = []
    for measurement in measurements:
        for field in fields:
            for sensor_id in sensor_ids:
                params = {'measurement': measurement, 'field': field, 'sensor_id': sensor_id, 'time_range': time_range}
                response = requests.get(f'http://localhost:5000/data', params=params)
                if response.status_code == 200 and response.text:
                    data = pd.DataFrame(response.json())
                    if data.empty:
                        print(f"No data returned for {measurement}, {field}, {sensor_id}")
                        continue
                    data['_time'] = pd.to_datetime(data['_time'])

                    trace_type = 'lines' if visualization_type == 'line' else 'markers'
                    traces.append(go.Scatter(
                        x=data['_time'], y=data[field],
                        mode=trace_type,
                        name=f'{field} from {sensor_id}'
                    ))
                else:
                    print(f"API error: {response.status_code} - {response.text}")

    if not traces:
        return go.Figure(layout=dict(title="No data to display"))

    layout = go.Layout(
        plot_bgcolor='#021526',
        paper_bgcolor='#021526',
        font_color='white',
        title='Sensor Data Visualization',
        xaxis_title='Time',
        yaxis_title='Value',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='gray')
    )
    return go.Figure(data=traces, layout=layout)


if __name__ == '__main__':
    app.run_server(debug=True, port=8050)

