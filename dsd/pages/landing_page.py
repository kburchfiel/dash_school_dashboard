# By Kenneth Burchfiel
# Released under the MIT license

# Source of code used to implement Dash Pages functionality: https://dash.plotly.com/urls

import dash
from dash import Dash, html, dcc, callback, Output, Input, dash_table
# For dash_table documentation, visit https://dash.plotly.com/datatable
import plotly.express as px
# Many of the following items were once defined within this Python file.
# However, I chose to move them to app_functions_and_variables so that they 
# could be more easily accessed by other files, thus simplifying my codebase.
from app_functions_and_variables import offline_mode, read_from_online_db, df_curr_enrollment, create_filters_and_comparisons, grade_reordering_map, create_interactive_bar_chart_and_table
import pandas as pd
import sqlalchemy
import dash_bootstrap_components as dbc
# See https://dash-bootstrap-components.opensource.faculty.ai/examples/iris/#sourceCode

dash.register_page(__name__, path='/')


layout = dbc.Container([
      
    create_filters_and_comparisons(df_curr_enrollment),

        dcc.Graph(id='enrollment_chart'),
        dash_table.DataTable(id = "enrollment_table",
    export_format = 'csv', 
    style_table = {'height':'300px', 'overflowY':'auto'})
])

@callback(
    Output('enrollment_chart', 'figure'),
    Output('enrollment_table', 'data'),
    Input('school_filter', 'value'),
    Input('grade_filter', 'value'),
    Input('gender_filter', 'value'),
    Input('race_filter', 'value'),
    Input('ethnicity_filter', 'value'),
    Input('enrollment_comparisons', 'value'),
    Input('color_bars_by', 'value')
)
def update_graph(school_filter, grade_filter, 
    gender_filter, race_filter, ethnicity_filter,
    enrollment_comparisons, color_bars_by):
    filter_list = [('School', school_filter), ('Grade',grade_filter),
    ('Gender', gender_filter), ('Race', race_filter), 
    ('Ethnicity', ethnicity_filter)]
    print("Enrollment comparisons:",enrollment_comparisons)
    return create_interactive_bar_chart_and_table(
        original_data_source=df_curr_enrollment, y_value = 'Students', 
        comparison_values = enrollment_comparisons, pivot_aggfunc= 'sum', 
        filter_list = filter_list, 
        color_value = color_bars_by, reorder_bars_by = 'Grade', 
        reordering_map = grade_reordering_map, debug = False)
