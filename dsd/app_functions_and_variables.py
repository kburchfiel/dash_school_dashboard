# App Functions and Variables

# By Kenneth Burchfiel
# Released under the MIT license


# Defining these functions and variables in a separate file helps keep
# the main app.py code cleaner.

import plotly.express as px
import pandas as pd

# Functions:

def create_interactive_bar_chart_and_table(original_data_source, y_value,
comparison_values, pivot_aggfunc, filter_list = None, 
color_value = None, color_discrete_map = None, barmode = 'group',
drop_color_value_from_x_vals = True, reorder_bars_by = '',
reordering_map = {}, debug = False,
color_discrete_sequence = px.colors.qualitative.Light24):
    '''
    This function creates an interactive bar chart (created using 
    px.histogram() and a corresponding set of table data. Users can
    update the chart by selecting comparison and filter values. 
    These charts and table data are based off a pivot table that is 
    created using the comparison values specified in the 
    comparison_values argument. 

    original_data_source: The source of the data that will be graphed.

    y_value: The y value to use within the graph.

    comparison_values: A list of values that will be used to pivot the
    DataFrame. These values help determine the level of detail shown in the
    final bar chart. Set this to an empty list ([]) 
    if no comparison values will be used. 

    pivot_aggfunc: the function ('mean', 'sum', 'count', etc.) to be passed
    to the pivot_table() call.

    filter_list: a list of tuples that govern how the DataFrame will be 
    filtered. The first component of each tuple is a column name; the second
    component is a list of values to include.

    color_value: The variable to use for a color-based comparison in the
    final graph.

    color_discrete_map: A custom color mapping to pass to the chart.

    In order to represent all of the specified values in the bar chart, 
    the code creates a column describing all (or almost all) 
    of the pivot index variables
    in the other columns, which then gets fed into the x axis parameter of 
    a histogram. However, if a color value is also specified, this item 
    does not get added into this column, since this
    data will already get represented in the bar chart (by means of the color
    legend). Removing this value helps
    simplify the final chart output.

    reorder_bars_by and reordering_map: Variables that you can
    use to update the order of the bars in the resulting chart. For instance,
    suppose you want to order the bars by a 'grade' column whose values
    range from K (kindergarten) to 12. If these are stored as strings 
    (which they often will be due to the inclusion of 'K'),
    the first 5 bars will be 1, 10, 11, 12, and 2, and the 
    last bar will be K. (That's because these bars are 
    being treated alphabetically). However, by setting
    reorder_bars_by to 'grade' and reordering_map to {'K':0, '1':1, '2':2, 
    '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, '10':10, '11':11, 
    '12':12, 1:1, 2:2, 3:3, 4:4, 5:5, 6:6, 7:7, 8:8, 9:9, 10:10, 11:11, 12:12},
    you can instruct the function to (1) create a new order for the grade
    column and then (2) sort the DataFrame based on this new order. This 
    sort operation will in turn reorder the bars so that 'K' comes first
    and '12' comes last.

    Note: If you don't need to update the sort order of the values in the 
    column whose name was passed to reorder_bars_by, simply keep 
    reordering_map as {}.

    color_discrete_sequence: The color palette to use for the charts.
    The default is Light24 because its use of 24 distinct colors
    helps prevent bar colors from overlapping.
    '''

    print("Filter list:",filter_list)
    data_source = original_data_source.copy() # Included to avoid modifying the
    # original DataFrame (although this line may not be necessary)
    
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

    # The color value must also be present within the comparison_values
    # table. If it is not, the following line sets color_value to None.
    if color_value not in comparison_values:
        color_value = None

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
        if ((color_value != None) & (len(data_descriptor_values) > 1) 
            & (drop_color_value_from_x_vals == True)):
            data_descriptor_values.remove(color_value) 
            # If a value will be assigned a
            # color component in the graph, it doesn't need to be assigned a 
            # group component, since it will show up in the graph regardless. 
            # Removing it here helps simplify the graph.
        print(data_descriptor_values)   
        data_descriptor = data_source_pivot[
            data_descriptor_values[0]].copy() # This line initializes 
            # data_descriptor as the first item within data_descriptor_values.
            # copy() is needed in order to avoid modifying this column when
        # the group column gets chosen.
        # The following for loop iterates through each column name (except
        # for the initial column, which has already been added
        # to data_descriptor) in order to set data_descriptor with all the
        # the values present in data_descriptor_values.
        # The use of a for loop allows this code to adapt to different variable
        # choices and different column counts.
        for i in range(1, len(data_descriptor_values)):
            data_descriptor += ' ' + data_source_pivot[
                data_descriptor_values[i]] # This line adds the value of a 
                # given column to data_descriptor.

    data_source_pivot['Group'] = data_descriptor # This group column will be 
    # used as the x value of the histogram.

    # The following code reorders the rows in the pivot table
    # in order to change the order of the bars in the ensuing chart.
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
            print(data_source_pivot)
            data_source_pivot.drop('column_for_sorting', axis = 1, 
            inplace = True) # This column is no longer needed,
            # so we can remove it from the DataFrame.


    # There is no need to perform bar grouping if only one pivot variable 
    # exists, so the following if/else statement sets barmode to 
    # 'relative' in that case. Otherwise, barmode is set to 'group' 
    # in order to simplify the x axis variables.
    if len(comparison_values) == 1:
        selected_barmode = 'relative'
    
    else:
        selected_barmode = barmode

    output_histogram = px.histogram(data_source_pivot, x = 'Group', 
    y = y_value, color = color_value, 
    barmode = selected_barmode, color_discrete_map=color_discrete_map,
    color_discrete_sequence=color_discrete_sequence
    )

    table_data = data_source_pivot.to_dict('records')

    return output_histogram#, table_data



