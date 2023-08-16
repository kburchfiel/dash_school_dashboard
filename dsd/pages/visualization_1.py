# Based in part on: https://dash.plotly.com/urls
import dash

from dash import html, dcc, callback, Input, Output
import pandas as pd
import plotly.express as px

dash.register_page(__name__)

# Incorporating code from: https://dash.plotly.com/minimal-app
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')

layout = html.Div([
html.H1(children='Title of Dash App', style={'textAlign':'center'}),
    dcc.Dropdown(df.country.unique(), 'Canada', id='dropdown-selection'),
    dcc.Graph(id='graph-content')
])
# Note that 'layout' is used here instead of 'app.layout'

@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_graph(value):
    dff = df[df.country==value]
    return px.line(dff, x='year', y='pop')