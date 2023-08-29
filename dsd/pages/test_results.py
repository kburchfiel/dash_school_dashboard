# By Kenneth Burchfiel
# Released under the MIT license

# Additional documentation can be found within
# current_enrollment.py.

import dash
from dash import Dash, html, dcc, callback, Output, Input, dash_table
import plotly.express as px

from app_functions_and_variables import offline_mode, read_from_online_db, df_curr_enrollment, create_filters_and_comparisons, grade_reordering_map, create_pivot_for_charts, create_interactive_line_chart_and_table, retrieve_data_from_table, merge_demographics_into_df
import pandas as pd
import sqlalchemy
import dash_bootstrap_components as dbc

dash.register_page(__name__, path = '/test_results')
# See https://dash.plotly.com/urls


df_test_results = retrieve_data_from_table('test_results')

# df_test_results doesn't have all of the demographic 
# values on which we want users to be able to filter,
# so we'll use merge_demographics_into_df() to add in those
# extra values.
df_test_results = merge_demographics_into_df(df_test_results)



layout = dbc.Container([
      
    create_filters_and_comparisons(df_test_results),
        dcc.Graph(id='test_results_chart'),
        dash_table.DataTable(id = "test_results_table",
    export_format = 'csv', 
    style_table = {'height':'300px', 'overflowY':'auto'})
])

@callback(
    Output('test_results_chart', 'figure'),
    Output('test_results_table', 'data'),
    Input('school_filter', 'value'),
    Input('grade_filter', 'value'),
    Input('gender_filter', 'value'),
    Input('race_filter', 'value'),
    Input('ethnicity_filter', 'value'),
    Input('enrollment_comparisons', 'value'),
)

def update_graph(school_filter, grade_filter, 
    gender_filter, race_filter, ethnicity_filter,
    enrollment_comparisons):
    filter_list = [('School', school_filter), ('Grade', grade_filter),
    ('Gender', gender_filter), ('Race', race_filter), 
    ('Ethnicity', ethnicity_filter)]
    print("Enrollment comparisons:", enrollment_comparisons)

    # For this line chart (and likely others also), it's ideal to 
    # have the code select the color and line dash variables based on the 
    # items found within enrollment_comparisons. This is because mismatches
    # between the enrollment comparisons and the color/pattern variables
    # can result in faulty line graph output.

    print("Enrollment comparisons:",enrollment_comparisons)

    if len(enrollment_comparisons) == 0:
        color_variable = None
        line_dash_variable = None

    if len(enrollment_comparisons) == 1:
        color_variable = enrollment_comparisons[0]
        line_dash_variable = None

    if len(enrollment_comparisons) >= 2:
        color_variable = enrollment_comparisons[0]
        line_dash_variable = enrollment_comparisons[1]
        # Additional enrollment values will be discarded:
        enrollment_comparisons = enrollment_comparisons[0:2].copy()

    # Note that the 'Period' option is added to enrollment_comparisons
    # within both function calls so that the line chart can visualize
    # changes between periods.

    test_results_pivot = create_pivot_for_charts(
        original_data_source=df_test_results, y_value = 'Score', 
        comparison_values = ['Period']+enrollment_comparisons, pivot_aggfunc= 'mean', 
        filter_list = filter_list, color_value = color_variable, 
        secondary_differentiator = line_dash_variable, reorder_bars_by = 'Grade', 
        reordering_map = grade_reordering_map, debug = True)

    return create_interactive_line_chart_and_table(
        data_source_pivot = test_results_pivot, y_value = 'Score', 
        comparison_values = ['Period']+enrollment_comparisons, 
        color_value = color_variable, 
        secondary_differentiator= line_dash_variable,
        label_round_precision=1,
        table_round_precision=1)
