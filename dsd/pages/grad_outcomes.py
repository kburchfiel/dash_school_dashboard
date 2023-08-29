# By Kenneth Burchfiel
# Released under the MIT license

# Based in part on: https://dash.plotly.com/urls
import dash

from dash import html, dcc, callback, Output, Input, dash_table
import pandas as pd
import plotly.express as px

from app_functions_and_variables import offline_mode, read_from_online_db, \
create_filters_and_comparisons, grade_reordering_map, create_pivot_for_charts, \
create_interactive_bar_chart_and_table, retrieve_data_from_table, \
enrollment_comparisons_plus_none, \
create_color_and_pattern_variable_dropdowns
import pandas as pd
import sqlalchemy
import dash_bootstrap_components as dbc

# Additional documentation can be found within
# current_enrollment.py.

dash.register_page(__name__, path = '/grad_outcomes')
# See https://dash.plotly.com/urls

df_grad_outcomes = retrieve_data_from_table('grad_outcomes')
df_grad_outcomes['Grade'] = df_grad_outcomes['Grade'].astype('str') # Since
# we don't have any K students in the Grade column, this column will
# default to an integer data type, which can create issues for code that
# expects grades to be a string. To avoid these issues, we'll simply
# change the grade to a string.


print(df_grad_outcomes.head)


layout = dbc.Container([
      
    # Adding in a school year filter:
    dbc.Row(
            [dbc.Col('Starting School Year:', lg=2),
            dbc.Col(
                dcc.Dropdown(df_grad_outcomes['Starting_Year'].unique(), 
                list(df_grad_outcomes['Starting_Year'].unique()),
                id='starting_year_filter', multi=True))
        ]),

    create_filters_and_comparisons(df_grad_outcomes, 
    default_comparison_option=[]),

    # The color and pattern variable menus will be defined below,
    # rather than through create_color_and_pattern_variable_dropdowns,
    # so that we can add in some additional options for both the color
    # variable and the pattern variable.
    html.Div([dbc.Row(
    [dbc.Col('Color variable:', lg = 2),
    dbc.Col(
        dcc.Dropdown([
            'Outcome', 'Starting_Year'] + enrollment_comparisons_plus_none, 
    'Outcome', id='color_variable', multi=False), lg = 3),
    
    dbc.Col('Pattern variable:', lg = 2),
    dbc.Col(
        dcc.Dropdown([
        'Outcome', 'Starting_Year'] + enrollment_comparisons_plus_none,
        id='pattern_variable', multi=False), lg = 3)])]),

        dcc.Graph(id='grad_outcomes_chart'),
        dash_table.DataTable(id = "grad_outcomes_table",
    export_format = 'csv', 
    style_table = {'height':'300px', 'overflowY':'auto'})
])

@callback(
    Output('grad_outcomes_chart', 'figure'),
    Output('grad_outcomes_table', 'data'),
    Input('starting_year_filter', 'value'),
    Input('school_filter', 'value'),
    Input('grade_filter', 'value'),
    Input('gender_filter', 'value'),
    Input('race_filter', 'value'),
    Input('ethnicity_filter', 'value'),
    Input('enrollment_comparisons', 'value'),
    Input('color_variable', 'value'),
    Input('pattern_variable', 'value')
)


def update_graph(starting_year_filter, school_filter, grade_filter, 
    gender_filter, race_filter, ethnicity_filter,
    enrollment_comparisons, color_variable, pattern_variable):
    filter_list = [('Starting_Year', starting_year_filter), 
    ('School', school_filter), ('Grade',grade_filter),
    ('Gender', gender_filter), ('Race', race_filter), 
    ('Ethnicity', ethnicity_filter)]
    print("Enrollment comparisons:", enrollment_comparisons)


    # The following functions hard-code Starting_Year and Outcome into
    # the beginning of the comparison_values list, so these variables
    # will factor into the graph regardless of the value of
    # enrollment_comparisons.

    grad_outcomes_pivot = create_pivot_for_charts(
        original_data_source=df_grad_outcomes, y_value = 'Students', 
        comparison_values = ['Starting_Year', 'Outcome'] + enrollment_comparisons, pivot_aggfunc= 'sum', 
        filter_list = filter_list, color_value = color_variable, 
        secondary_differentiator = pattern_variable, reorder_bars_by = 'Grade', 
        reordering_map = grade_reordering_map, debug = True)

    return create_interactive_bar_chart_and_table(
        data_source_pivot = grad_outcomes_pivot, y_value = 'Students', 
        comparison_values = ['Starting_Year', 'Outcome'] + enrollment_comparisons, 
        color_value = color_variable, 
        secondary_differentiator= pattern_variable,
        barmode = 'group')
