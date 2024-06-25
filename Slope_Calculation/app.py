import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import plotly.express as px
import base64
import io

app = dash.Dash(__name__)
app.title = "Slope and CO2 Concentration Calculation from Scatter Plot Points"

server = app.server

app.layout = html.Div([
    html.H1("Slope and CO2 Concentration Calculation from Scatter Plot Points"),
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select a CSV File')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        multiple=False
    ),
    dcc.Graph(id='scatter-plot'),
    html.Div(id='output-container'),
    dcc.Store(id='selected-points', data=[]),
    dcc.Store(id='click-count', data=0)
])

def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            return df
        else:
            return None
    except Exception as e:
        print(e)
        return None

@app.callback(
    Output('scatter-plot', 'figure'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def update_scatter(contents, filename):
    if contents is not None:
        df = parse_contents(contents, filename)
        if df is not None and 'ticks' in df.columns and 'co2_concentration' in df.columns:
            fig = px.scatter(df, x='ticks', y='co2_concentration', title="CO2 Concentration")
            fig.update_traces(mode='markers', marker=dict(size=5))
            fig.update_layout(clickmode='event+select')
            return fig
    return px.scatter(title="Please upload a CSV file with 'ticks' and 'co2_concentration' columns")

@app.callback(
    [Output('selected-points', 'data'), Output('click-count', 'data')],
    Input('scatter-plot', 'clickData'),
    [State('selected-points', 'data'), State('click-count', 'data')]
)
def update_selected_points(clickData, selected_points, click_count):
    if clickData:
        point = clickData['points'][0]['x'], clickData['points'][0]['y']
        selected_points.append(point)

        click_count += 1

        if len(selected_points) > 2:
            selected_points = selected_points[-2:]

    return selected_points, click_count

@app.callback(
    Output('output-container', 'children'),
    [Input('selected-points', 'data'), Input('click-count', 'data')]
)
def display_slope(selected_points, click_count):
    if click_count % 2 == 1:
        slope_message = "Slope: 0"
        co2C_message = "CO2 Concentration Difference: 0"
    elif len(selected_points) == 2:
        x1, y1 = selected_points[0]
        x2, y2 = selected_points[1]
        if x2 - x1 == 0:
            slope_message = "Slope is undefined (division by zero). Please select points with different x coordinates."
            co2C_message = ""
        else:
            slope = (y2 - y1) / 0.16
            co2C = y2 - y1
            slope_message = f"Slope: {slope:.4f}"
            co2C_message = f"CO2 Concentration Difference: {co2C:.4f}"
    else:
        slope_message = "Click on the scatter plot to select two points for slope calculation."
        co2C_message = ""

    return f"{slope_message} and {co2C_message}"

if __name__ == '__main__':
    app.run_server(debug=True)
