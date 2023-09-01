# Code for Current Enrollment dashboard

# By Kenneth Burchfiel
# Released under the MIT license

# Source of code used to implement Dash Pages functionality: 
# https://dash.plotly.com/urls

import dash
from dash import Dash, html, dcc, callback, Output, Input, dash_table
# For dash_table documentation, visit https://dash.plotly.com/datatable
import plotly.express as px
# Many of the following items were once defined within this Python file.
# However, I chose to move them to app_functions_and_variables so that they 
# could be more easily accessed by other files, thus simplifying my codebase.

from app_functions_and_variables import offline_mode, read_from_online_db, \
df_curr_enrollment, create_filters_and_comparisons, \
create_color_and_pattern_variable_dropdowns, grade_reordering_map, \
create_pivot_for_charts, create_interactive_bar_chart_and_table

import pandas as pd
import sqlalchemy
import dash_bootstrap_components as dbc
# See https://dash-bootstrap-components.opensource.faculty.ai/examples/iris/#sourceCode

dash.register_page(__name__, path='/')
# See https://dash.plotly.com/urls
# I set the path to '/' because I want this to be the default visualization
# that users see after logging in. Other pages have their names embedded
# into their paths.


# Defining the page's layout:

# Applying layout functions defined within
# app_functions_and_variables.py helps simplify this section of the code.
layout = dbc.Container([
    create_filters_and_comparisons(df_curr_enrollment),
    create_color_and_pattern_variable_dropdowns(),
    dcc.Graph(id='enrollment_chart'),
    dash_table.DataTable(id = "enrollment_table",
    export_format = 'csv', 
    # Allows the datatable to be exported to a .csv file. See
    # See https://dash.plotly.com/datatable/reference
    style_table = {'height':'300px', 'overflowY':'auto'})
])

# Adding in code to generate a bar chart and table:

# To better understand how callbacks work, see:
# https://dash.plotly.com/basic-callbacks
# The 'Dash App With Multiple Inputs' section of this documentation
# is particularly relevant to this code.

@callback(
    Output('enrollment_chart', 'figure'),
    Output('enrollment_table', 'data'),
    Input('school_filter', 'value'),
    Input('grade_filter', 'value'),
    Input('gender_filter', 'value'),
    Input('race_filter', 'value'),
    Input('ethnicity_filter', 'value'),
    Input('enrollment_comparisons', 'value'),
    Input('color_variable', 'value'),
    Input('pattern_variable', 'value')
)

# The following update_graph() function
# uses the input variables specified in @callback() to
# generate a chart and table. The first argument (school_filter) 
# corresponds to the first Input callback shown ('school_filter'),
# the second argument corresponds to the second Input callback, and so on.
# The callback names and function arguments don't need to match, but keeping
# the names similar helps make the code more intuitive.

def update_graph(school_filter, grade_filter, 
    gender_filter, race_filter, ethnicity_filter,
    enrollment_comparisons, color_variable, pattern_variable):

    # Creating a list of filters to be passed to create_pivot_for_chart:
    filter_list = [('School', school_filter), ('Grade',grade_filter),
    ('Gender', gender_filter), ('Race', race_filter), 
    ('Ethnicity', ethnicity_filter)]

    print("Enrollment comparisons:", enrollment_comparisons)

    # The following two functions used to be a single function, but I split
    # them in order to make the code more flexible. create_pivot_for_charts(),
    # as its name suggests, produces a pivot table from which charts
    # can be created. create_interactive_bar_chart_and_table() uses this
    # pivot table to produce both a bar chart and a table.

    # These functions are defined within app_functions_and_variables.py,
    # which makes them easier to use within other code files.

    curr_enrollment_pivot = create_pivot_for_charts(
        original_data_source=df_curr_enrollment, y_value = 'Students', 
        comparison_values = enrollment_comparisons, pivot_aggfunc= 'sum', 
        filter_list = filter_list, color_value = color_variable, 
        secondary_differentiator = pattern_variable, reorder_bars_by = 'Grade', 
        reordering_map = grade_reordering_map, debug = True)

    return create_interactive_bar_chart_and_table(
        data_source_pivot = curr_enrollment_pivot, y_value = 'Students', 
        comparison_values = enrollment_comparisons, 
        color_value = color_variable, 
        secondary_differentiator= pattern_variable)

        # create_interactive_bar_chart_and_table() returns both a bar
        # chart (which corresponds to the 'enrollment_chart' Output)
        # and a table (which corresponds to the 'enrollment_table' Output). 
