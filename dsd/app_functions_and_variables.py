# App Functions and Variables

# By Kenneth Burchfiel
# Released under the MIT license

# This file contains a number of essential functions and variables that allow
# the app to retrieve, reformat, and display data. Defining these functions 
# and variables in a separate file helps keep the rest of the app code cleaner. 
# It also reduces the total length of the codebase, since I can access the 
# functions stored here within multiple parts of the app.

import plotly.express as px
import pandas as pd
import platform
import sqlalchemy
import dash_bootstrap_components as dbc
# This is a great library for enhancing both the look and functionality of 
# the app.
# See https://dash-bootstrap-components.opensource.faculty.ai/examples/iris/#sourceCode
import dash
from dash import Dash, html, dcc, Output, Input


# Determining where the program is being run and how to access data:

# The following code checks whether the output of platform.node() is equal
# to the network name of my laptop. If it is, I know that the code is running
# locally. If it isn't, I can assume that the code is running
# via Cloud Run. (You'll need to replace this value with your own
# computer's network name in order for the code to run correctly on your 
# end. You can find this name by running platform.node() on 
# your own computer.)
# platform.node() returned 'localhost' for me when I tried running this 
# code via Cloud Run, so you could also rewrite the code so that
# offline_mode is set to False if platform.node() = localhost.

print("Computer's network name:", platform.node())
if platform.node() == 'DESKTOP-83K77J1': # Change this to your own computer's
    # network name
    offline_mode = True
else:
    offline_mode = False

read_from_online_db = False # When both this variable and offline_mode are set
# to True, the script will import data from the online PostgreSQL database 
# rather than from a local .csv file. (When offline_mode is False, the script
# will always read from the online database regardless of the value of
# read_from_online_db.)

def create_database_engine():
    '''This function allows us to create a SQLAlchemy engine that can connect
    to our database. 

    We will utilize two different methods of retrieving the online PostgreSQL 
    database's URL (which will play a crucial role in creating the engine). If 
    offline_mode is True, we'll get the URL from a local folder. 
    If it's instead set to False, we'll access the key through 
    Google Cloud's Secret manager service.
    
    The URL itelf can be found within the database's home page on
    elephantsql.com. As shown below, 
    SQLAlchemy can use this URL to connect to the database. The setup will
    likely vary somewhat for other database providers, particularly if
    you are not using a PostgreSQL database.
    
    '''
    if offline_mode == True: 
        # The following code is based on my computer's folder structure,
        # so you'll probably need to update it on your end in order
        # to direct the code to the location of your database's URL.
        with open ("../../key_paths/path_to_keys_folder.txt") as file:
            key_path = file.read()
        with open(key_path+"/elephantsql_dashschooldemodb_url.txt") as file:
            db_url = file.read()
        
    else: # The URL for the ElephantSQL database will
    # be accessed through a Secret Manager volume stored online
        with open('/projsecrets/elephant-sql-db-url') as file:
            db_url = file.read()
        # Based on:
        # https://stackoverflow.com/questions/68533094/how-do-i-access-mounted-secrets-when-using-google-cloud-run
        # In order for this step to work, I needed to go to 
        # https://console.cloud.google.com/run , select 'Edit & Deploy 
        # New Revision,'and then mount my secret (which I had created earlier) 
        # as a volume. 
        # (I chose 'projsecrets' as my volume name.)
        # Note that the Secret Manager Secret Accessor role must be enabled for 
        # your service account for your code to work, as noted here:
        # https://cloud.google.com/run/docs/configuring/secrets#access-secret

    # Now that we've retrieved the URL, we can use it to connect to the
    # online database. 

    elephantsql_db_url_for_sqlalchemy = db_url.replace(
    'postgres://', 'postgresql://')
    # This change, which is required for SQLAlchemy to work correctly, 
    # is based on the code suggested at:
    # https://help.heroku.com/ZKNTJQSK/why-is-sqlalchemy-1-4-x-not-connecting-to-heroku-postgres

    elephantsql_engine = sqlalchemy.create_engine(
    elephantsql_db_url_for_sqlalchemy)
    # See https://docs.sqlalchemy.org/en/20/core/engines.html
    return elephantsql_engine

# Using create_database_engine() to create an elephantsql engine that we can
# use in subsequent code: 
# (We'll only need this engine in certain cases, however, hence
# the inclusion of an if statement.)
if (offline_mode == False) or (read_from_online_db == True): 
    elephantsql_engine = create_database_engine()

def retrieve_data_from_table(table_name):
    '''This function retrieves all data from a given database table. This
    may be performed online or through an offline import of a .csv file
    containing a copy of this table.

    If you only need a portion of the data stored in a given table,
    your app may run faster if you define and use a separate read_sql()
    call that retrieves only that portion of the data.

    In order for this function to work correctly, 
    the name of the offline .csv file that contains the table 
    must be the same as the table name within the online database.'''

    print("offline_mode is set to:", offline_mode)
    print("read_from_online_db is set to:", read_from_online_db)
    if (offline_mode == True) and (read_from_online_db == False):
        print("Reading from local .csv file")
        # The file will be read locally, rather than from the online database,
        # only if both of these conditions are met.
        df_query = pd.read_csv(f'../{table_name}.csv')
    else:
        print("Reading from online database")
        df_query = pd.read_sql(f"select * from {table_name}", 
        con = elephantsql_engine)
        
    return df_query

# Retrieving all current enrollment data: 
# (Initializing df_curr_enrollment
# here will make it easier, and perhaps faster,
# to use this data within multiple DataFrames.)
df_curr_enrollment = retrieve_data_from_table(table_name = 'curr_enrollment')

# Defining a standard set of values by which we would like to compare
# our fictional student data:
enrollment_comparisons = ['School', 'Grade', 'Gender',
'Race', 'Ethnicity'] 

# The following code creates a copy of enrollment_comparisons with a
# 'None' option
# so that users can choose not to select a given value.
enrollment_comparisons_plus_none = enrollment_comparisons.copy()
enrollment_comparisons_plus_none.append('None')

# This dictionary will be used to help order grades correctly within charts.
# Without this reordering, K will often appear at the end of grade-based
# charts.
grade_reordering_map = {'K':0, '1':1, '2':2, '3':3, '4':4, '5':5, '6':6, 
        '7':7, '8':8, '9':9, '10':10, '11':11, '12':12, 1:1, 2:2, 3:3, 
        4:4, 5:5, 6:6, 7:7, 8:8, 9:9, 10:10, 11:11, 12:12} 


def merge_demographics_into_df(df):
    '''This function merges demographic variables from df_current_enrollment
    into the DataFrame passed to df, then returns the new version
    of the DataFrame.'''

    # Creating a copy of df_current_enrollment that only contains 
    # Student IDs (which will serve as the key for the merge) and 
    # the demographic values contained in enrollment_comparisons:
    df_curr_enrollment_for_merge = df_curr_enrollment.copy(
    )[['Student_ID'] + enrollment_comparisons]
    # Some of these demographic values may already be present within 
    # the DataFrame, in which case they should be removed from
    # df_curr_enrollment_for_merge so that we don't end up with multiple
    # copies of the same column.
    for column in df.columns:
        if column in enrollment_comparisons:
            df_curr_enrollment_for_merge.drop(column, 
                axis = 1, inplace = True)
    return df.merge(df_curr_enrollment_for_merge, 
        on = 'Student_ID', how = 'left')


def create_filters_and_comparisons(df, default_comparison_option = ['School']):
    '''This function creates a set of filters and comparison options that
    can be imported into the layout section of a dashboard page. Building
    them within a function allows me to use them for multiple charts,
    thus simplifying my code.
    
    df refers to the DataFrame from which you would like to retrieve
    comparison options. This should generally be the same DataFrame
    on which visualizations will be based. Otherwise, the user will
    be presented with options that don't match the actual options
    found in the DataFrame.

    default_comparison_option allows you to choose the initial comparison 
    group that will be presented to the user. If you do not wish to show
    any comparisons by default, set this variable to [].
    '''

    # This Dash Bootstrap Components documentation page proved very
    # helpful in developing this code:
    # https://dash-bootstrap-components.opensource.faculty.ai/docs/components/layout/
    # The Dash documentation on dcc.Dropdown was very helpful also. It's 
    # available at https://dash.plotly.com/dash-core-components/dropdown

    filters_and_comparisons = html.Div([
        # Generating filter options:
        dbc.Row(
            [dbc.Col('Schools:', lg = 1),
            dbc.Col(
                dcc.Dropdown(df['School'].unique(), 
                list(df['School'].unique()), 
                id='school_filter', multi=True), lg = 4), 
            dbc.Col('Genders:', lg = 1),
            dbc.Col(
                dcc.Dropdown(df['Gender'].unique(), 
                list(df['Gender'].unique()), id='gender_filter', 
                multi=True), lg = 3)
                ]),
        dbc.Row([
            dbc.Col('Grades:', lg = 1),
            dbc.Col(
                dcc.Dropdown(df['Grade'].unique(), 
                list(df['Grade'].unique()), id='grade_filter', 
                multi=True))]),
        dbc.Row([
            dbc.Col('Races:', lg = 1),
            dbc.Col(
                dcc.Dropdown(df['Race'].unique(), 
                list(df['Race'].unique()), id='race_filter', 
                multi=True), lg = 6),
            dbc.Col('Ethnicities:', lg = 1),
            dbc.Col(
                dcc.Dropdown(df['Ethnicity'].unique(), 
                list(df['Ethnicity'].unique()), 
                id='ethnicity_filter', 
                multi=True), lg = 4)            
                ]),

        # Generating comparison options:
        dbc.Row(
            [dbc.Col('Comparison Options:', lg=2),
            dbc.Col(
                dcc.Dropdown(enrollment_comparisons, 
            default_comparison_option, id='enrollment_comparisons', multi=True))
        ]),
        ])
    return filters_and_comparisons

def create_color_and_pattern_variable_dropdowns(color_default = 'School',
    pattern_default = 'None'):
    '''This function makes it easier to insert color and pattern variable
    options into a dashboard. These options will allow the user to modify
    the appearance of the dashboard's visualization(s).
    
    This code used to be part of create_filters_and_comparisons,
    but I found that it is sometimes better to have the code define
    these variables than for the user to be able to select them.
    Therefore, I moved them to a standalone function so that they 
    would only be added to pages' layouts when needed.
    
    The color_default and pattern_default variables allow you to choose
    default entries for color_variable and pattern_variable if needed.'''

    # Note that this code uses enrollment_comparisons_plus_none instead
    # of enrollment_comparisons so that users can choose not to 
    # select a color or pattern variable.
    color_and_pattern_variable_dropdowns = html.Div([dbc.Row(
    [dbc.Col('Color variable:', lg = 2),
    dbc.Col(
        dcc.Dropdown(enrollment_comparisons_plus_none, 
    color_default, id='color_variable', multi=False), lg = 3),
    
    dbc.Col('Pattern variable:', lg = 2),
    dbc.Col(
        dcc.Dropdown(enrollment_comparisons_plus_none,
        id='pattern_variable', multi=False), lg = 3)])])
    return color_and_pattern_variable_dropdowns


def create_pivot_for_charts(original_data_source, y_value,
comparison_values, pivot_aggfunc, filter_list = None, 
color_value = None, drop_color_value_from_x_vals = True, 
secondary_differentiator = None, 
drop_secondary_differentiator_from_x_vals = True,
reorder_bars_by = '', reordering_map = {}, debug = False):
    '''This function turns the DataFrame passed to original_data_source
    into a pivot table that can serve as the basis for a Plotly chart. This 
    code plays a crucial role in making the charts truly interactive, as
    the comparisons and filters passed to this function will in turn
    modify the pivot table's contents, thus allowing the resulting
    visualizations to take on different forms.
    This function does not perform any graphing tasks; those are carried out 
    by separate functions defined later in this code. This setup allows
    this function to support the creation of multiple graph types.
    
    original_data_source: The source of the data that will be graphed.

    y_value: The y value to use within the graph.

    comparison_values: A list of values that will be used to pivot the
    DataFrame. These values help determine the level of detail shown in the
    final bar chart. Set this to an empty list ([]) 
    if no comparison values will be used. 

    pivot_aggfunc: The aggregate function ('mean', 'sum', 'count', etc.) 
    to be passed to the pivot_table() call.

    filter_list: A list of tuples that govern how the DataFrame will be 
    filtered. The first component of each tuple is a column name; the second
    component is a list of values to include.

    color_value and drop_color_value_from_x_vals: 
    color_value specifies the variable to use for a color-based comparison 
    in the final graph.
    In order to represent all of the specified values in the bar chart, 
    the code creates a column describing all (or almost all) of the 
    pivot index variables in the other columns, which then gets fed into 
    the x axis parameter of a histogram. However, if a color value is also 
    specified *and* drop_color_value_from_x_vals is set to True, this item 
    will not get added into this column, since this data will already get 
    represented in the bar chart (by means of the color legend). 
    Removing this value helps simplify the final chart output.

    secondary_differentiator: Similar to color_value, this is 
    a second variable that will be represented via a chart feature 
    (such as pattern_shape for a bar chart or line_dash for a 
    line chart). Defining this variable allows it to be
    removed from the column that describes the pivot index variables
    so that the graph can be further simplified.

    drop_secondary_differentiator_from_x_vals: Set this to True to remove
    the variable stored in secondary_differentiator from the pivot table
    column that will contain different x values.

    reorder_bars_by and reordering_map: Variables that you can
    use to update the order of the bars in the resulting chart. For instance,
    suppose you want to order the bars by a 'Grade' column whose values
    range from K (kindergarten) to 12. If these are stored as strings 
    (which they often will be due to the inclusion of 'K'),
    the first 5 bars will be 1, 10, 11, 12, and 2, and the 
    last bar will be K. (That's because these x values are 
    being sorted alphabetically). However, by setting
    reorder_bars_by to 'grade' and reordering_map to {'K':0, '1':1, '2':2, 
    '3':3, . . . '12':12},
    you can instruct the function to (1) create a new order for the grade
    column and then (2) sort the DataFrame based on this new order. This 
    sort operation will in turn reorder the bars so that 'K' comes first
    and '12' comes last.

    Note: If you don't need to update the sort order of the values in the 
    column whose name was passed to reorder_bars_by, simply keep 
    reordering_map as {}.
    
    debug: set to True to include additional print statements during
    the function's execution.'''

    # Converting 'None' strings to None values:
    if color_value == 'None':
        color_value = None

    if secondary_differentiator == 'None':
        secondary_differentiator = None

    if debug == True:
        print("Current state of color_value:", color_value, type(color_value))
        print("Current state of secondary_differentiator:",
        secondary_differentiator, type(secondary_differentiator))
        print("Filter list:",filter_list)

    data_source = original_data_source.copy()
    
    all_data_value = 'All'

    # The following line goes through each tuple in filter_list and
    # filters the DataFrame based on the values provided there.
    # filter[0] corresponds to a column in the DataFrame, and filter[1]
    # contains a list of which values to keep within that column.
    data_source_filtered = data_source.copy()
    if filter_list != None:
        for filter in filter_list:
           data_source_filtered.query(
            f"{filter[0]} in {filter[1]}", inplace = True)
    if debug == True:
        print("data_source_filtered:",data_source_filtered)

    # The color value must be present within the comparison_values
    # table. If it is not, the following line sets color_value to None.
    if color_value not in comparison_values:
        color_value = None

    # The same holds true for secondary_differentiator.
    if secondary_differentiator not in comparison_values:
        secondary_differentiator = None

    # In order to show comparisons within the final graph, we need to create
    # a table that contains those various comparisons. This function does so
    # using the pivot_table() function within Pandas. The resulting pivot
    # table will have one row for each comparison combination (as long as
    # y value data were present for that combination.)

    # If at least one comparison value was provided, the comparison_values
    # variable will be used as the index for the pivot_table() function. 
    # Otherwise, a new column will be 
    # created (with the same value in every cell), and the pivot_table()
    # function will use this column as its index instead. 
    if len(comparison_values) == 0:
        data_source_filtered[all_data_value] = all_data_value 
        data_source_pivot = data_source_filtered.pivot_table(
            index = all_data_value, values = y_value, 
            aggfunc = pivot_aggfunc).reset_index()
    else:
        data_source_pivot = data_source_filtered.pivot_table(
            index = comparison_values, values = y_value, 
            aggfunc = pivot_aggfunc).reset_index()

    # Next, we need to create x values that reflect the different column
    # values in each row of the pivot table. These x values will then 
    # get passed to the graphing function.
    # The following lines accomplish this by creating a new 
    # data_source_pivot column that contains strings made up of the 
    # values of each of the columns (other than the y value column) 
    # present in the bar chart. The chart will use these strings as 
    # x values when creating the grouped chart. 

    if len(comparison_values) == 0:
        data_descriptor = all_data_value

    else:
        data_descriptor_values = comparison_values.copy()
        
        # We'll now remove the variables stored in
        # color_value and secondary_differentiator from the chart if
        # drop_color_value_from_x_vals and 
        # drop_secondary_differentiator_from_x_vals are set to True,
        # respectively.
        if ((color_value != None) & (len(data_descriptor_values) > 1) 
            & (drop_color_value_from_x_vals == True)):
            data_descriptor_values.remove(color_value) 
            # If a value will be assigned a
            # color component in the graph, it doesn't need to be assigned a 
            # group component, since it will show up in the graph regardless. 
            # Removing it here helps simplify the graph.

        # Performing the same steps for secondary_differentiator:
        if ((secondary_differentiator != None) & 
            (len(data_descriptor_values) > 1) 
            & (drop_secondary_differentiator_from_x_vals == True)):
            data_descriptor_values.remove(secondary_differentiator) 
         
        if debug == True:
            print(data_descriptor_values)   
        data_descriptor = data_source_pivot[
            data_descriptor_values[0]].copy().astype('str') # This line 
        # initializes data_descriptor as the first item within 
        # data_descriptor_values. copy() is needed in order to avoid 
        # modifying this column when the group column gets chosen.

        # The following for loop iterates through each column name (except
        # for the initial column, which has already been added
        # to data_descriptor) in order to add all of the values present in 
        # data_descriptor_values to data_descriptor.
        # The use of a for loop allows this code to adapt to different variable
        # choices and different column counts.
        for i in range(1, len(data_descriptor_values)):
            data_descriptor += ' ' + data_source_pivot[
                data_descriptor_values[i]].astype('str') # This line adds 
                # the value of a given column to data_descriptor.

    data_source_pivot['Group'] = data_descriptor # This group column will be 
    # used as the x value of the chart.

    # The following code reorders the rows in the pivot table
    # in order to change the order of the items in the ensuing chart.
    # See the description of reorder_bars_by and reordering_map
    # in the function docstring for more information.
    if (reorder_bars_by != '') & (reorder_bars_by in data_source_pivot.columns):
        # The above line first checks to ensure that the column passed to
        # reorder_bars_by is actually in the pivot; otherwise, we'll run 
        # into an error by trying to sort by a nonexistent column.
        if reordering_map == {}: # Since nothing has been passed to 
            # reordering_map, the function will simply sort the DataFrame
            # by the values in the column referenced by reorder_bars_by.
            data_source_pivot.sort_values('reorder_bars_by', inplace = True)
        else: # In this case, the function will first create a separate column
            # that will store a new order of the values in reorder_bars_by,
            # then sort the DataFrame by that column instead. 
            data_source_pivot['column_for_sorting'] = data_source_pivot[
                reorder_bars_by].map(reordering_map)
            data_source_pivot.sort_values('column_for_sorting', 
            inplace = True)
            data_source_pivot.drop('column_for_sorting', axis = 1, 
            inplace = True) # This column is no longer needed,
            # so we can remove it from the DataFrame.
    
    if debug == True:
        print("Pivot table created for charts/tables:")
        print(data_source_pivot)
    return data_source_pivot


def create_interactive_bar_chart_and_table(data_source_pivot, y_value,
comparison_values, color_value = None, color_discrete_map = None, 
barmode = 'group', color_discrete_sequence = px.colors.qualitative.Light24,
secondary_differentiator = None, text_auto = True, label_round_precision = None,
table_round_precision = None):
    '''This function converts a pivot table (presumably one returned by
    create_pivot_for_charts() into an interactive bar chart and table.

    data_source_pivot: The pivot table that will serve as the foundation
    for the chart. It is expected, but not required, that this table 
    originate from create_pivot_for_charts().

    For definitions of y_value, comparison_values, and color_value,
    see the create_pivot_for_charts() documentation.

    color_discrete_map: A custom color mapping to pass to the chart.

    color_discrete_sequence: The color palette to use for the charts.
    The default is Light24 because its use of 24 distinct colors
    helps prevent bar colors from overlapping.

    barmode: The means by which the bars will be presented relative to
    one another. This keyword comes from Plotly's px.histogram() code.

    secondary_differentiator: A value to pass to the pattern_shape argument,
    allowing for further distinction between different bars. For documentation
    on pattern_shape, see:
    # https://plotly.com/python-api-reference/generated/plotly.express.bar

    text_auto: Set to True to show data labels within charts.

    label_round_precision: The extent to which chart labels should be rounded.
    If the label is originally 555.933, a label_round_precision of 1 will
    produce the number 555.9, and a label_round_precision of 0 will produce
    556. No rounding will occur if label_round_precision is set to None.

    table_round_precision: This variable rounds table values in the same way
    that label_round_precision rounds label values.

    '''

    # Converting 'None' strings to None values:
    if color_value == 'None':
        color_value = None

    if secondary_differentiator == 'None':
        secondary_differentiator = None


    data_source_pivot_for_table = data_source_pivot.copy() # This script 
    # will apply changes to copies of data_source_pivot so that the original
    # pivot table is not affected.

    # Rounding table values if requested:
    if table_round_precision != None:
        data_source_pivot_for_table[y_value] = round(
            data_source_pivot_for_table[y_value], table_round_precision)

    table_data = data_source_pivot_for_table.to_dict('records') 
    # See https://dash.plotly.com/datatable
    # This data will get returned at the end of the function so that it can
    # serve as the basis for a data table within a dashboard.

    data_source_pivot_for_chart = data_source_pivot.copy()

    # There is no need to perform bar grouping if only one pivot variable 
    # exists, so the following if/else statement sets barmode to 
    # 'relative' in that case. Otherwise, barmode is set to 'group' 
    # in order to simplify the x axis variables.
    if len(comparison_values) == 1:
        selected_barmode = 'relative'
    else:
        selected_barmode = barmode
    
    # The color value must be present within the comparison_values
    # table in order for the code to utilize it. 
    # If it is not, the following line sets color_value to None.
    if color_value not in comparison_values:
        color_value = None

    # The same holds true for secondary_differentiator.
    if secondary_differentiator not in comparison_values:
        secondary_differentiator = None

    # Rounding y values to be shown in labels (if requested):
    if label_round_precision != None:
        data_source_pivot_for_chart[y_value] = round(
            data_source_pivot_for_chart[y_value], 
        label_round_precision)

    # Creating the bar chart:
    # px.histogram() is used instead of px.bar() in order to group different
    # components of each bar together. For px.histogram() documentation,
    # see https://plotly.com/python/histograms/
    output_histogram = px.histogram(data_source_pivot_for_chart, x = 'Group', 
    y = y_value, color = color_value, 
    barmode = selected_barmode, color_discrete_map=color_discrete_map,
    color_discrete_sequence=color_discrete_sequence,
    pattern_shape = secondary_differentiator, text_auto = text_auto
    )

    return output_histogram, table_data




def create_interactive_line_chart_and_table(data_source_pivot, y_value, 
comparison_values, color_value = None, color_discrete_map = None, 
color_discrete_sequence = px.colors.qualitative.Light24, 
markers = True, secondary_differentiator = None,
show_labels = True, label_round_precision = None,
table_round_precision = None):
    '''This function converts a pivot table (presumably one returned by
    create_pivot_for_charts() into an interactive line chart and table.

    data_source_pivot: The pivot table on which the chart will be based.
    It is expected, but not required, that this table originate from
    create_pivot_for_charts().

    For definitions of y_value, comparison_values, and color_value,
    see create_pivot_for_charts().

    color_discrete_map: A custom color mapping to pass to the chart.

    color_discrete_sequence: The color palette to use for the charts.
    The default is Light24 because its use of 24 distinct colors
    helps prevent bar colors from overlapping.

    markers: Set to True to add markers to your line chart and False to
    omit them.

    secondary_differentiator: A variable to be passed to the line_dash
    # argument of px.line(). For documentation on line_dash,
    # see: https://plotly.com/python-api-reference/generated/plotly.express.line 

    show_labels: Set to True to show data labels within charts.

    label_round_precision: The extent to which chart labels should be rounded.
    If the label is originally 555.933, a label_round_precision of 1 will
    produce the number 555.9, and a label_round_precision of 0 will produce
    556. No rounding will occur if label_round_precision is set to None.

    table_round_precision: This variable rounds table values in the same way
    that label_round_precision rounds label values.

    '''

    # Converting 'None' strings to None values:
    if color_value == 'None':
        color_value = None

    if secondary_differentiator == 'None':
        secondary_differentiator = None

    # The color value must be present within the comparison_values
    # table in order for the code to utilize it. 
    # If it is not, the following line sets color_value to None.
    if color_value not in comparison_values:
        color_value = None

    # The same holds true for secondary_differentiator.
    if secondary_differentiator not in comparison_values:
        secondary_differentiator = None


    data_source_pivot_for_table = data_source_pivot.copy() # This script 
    # will apply changes to copies of data_source_pivot so that the original
    # pivot table is not affected.
    
    # Rounding table values (if requested):
    if table_round_precision != None:
        data_source_pivot_for_table[y_value] = round(
            data_source_pivot_for_table[y_value], table_round_precision)

    table_data = data_source_pivot_for_table.to_dict('records') 
    # See https://dash.plotly.com/datatable


    data_source_pivot_for_chart = data_source_pivot.copy()


    # Rounding y values to be shown in labels (if requested):
    if label_round_precision != None:
        data_source_pivot_for_chart[y_value] = round(
            data_source_pivot_for_chart[y_value], 
        label_round_precision)

    # Determining whether to show labels:
    if show_labels == True:
        text = y_value
    else:
        text = None

    # For Plotly line chart documentation, see:
    # https://plotly.com/python/line-charts/
    output_chart = px.line(data_source_pivot_for_chart, x = 'Group', 
    y = y_value, color = color_value,
    color_discrete_map=color_discrete_map,
    color_discrete_sequence=color_discrete_sequence,
    markers = markers, line_dash = secondary_differentiator, text = y_value
    )
    
    return output_chart, table_data