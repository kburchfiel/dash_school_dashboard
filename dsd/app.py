# Sample Dash app that creates an interactive school dashboard

# This code was based on Dash's sample Dash app, available at: 
# https://dash.plotly.com/minimal-app

# By Kenneth Burchfiel
# Released under the MIT license

# Note: All data in this dashboard is entirely fictional.

from dash import Dash, html, dcc, callback, Output, Input
from support_functions import create_interactive_bar_chart_and_table
import plotly.express as px
import pandas as pd
import sqlalchemy
import dash_bootstrap_components as dbc
# See https://dash-bootstrap-components.opensource.faculty.ai/examples/iris/#sourceCode

offline_mode = False
read_from_online_db = True # When both this variable and offline_mode are set
# to True, the script will import data from the online PostgreSQL database 
# rather than from a local .csv file. (When offline_mode is False, the script
# will always read from the online database regardless of the value of
# read_from_online_db.)

if read_from_online_db == True: 
    # We will utilize two different methods of retrieving the online PostgreSQL 
    # database's URL (which will play a crucial role in connecting to it).
    # If offline_mode is True, we'll get the URL from a local folder. 
    # If it's instead set to False, we'll access the key through 
    # Google Cloud's Secret manager service.
    if offline_mode == True: 
        with open ("../../key_paths/path_to_keys_folder.txt") as file:
            key_path = file.read()
        with open(key_path+"/elephantsql_dashschooldemodb_url.txt") as file:
            db_url = file.read()
        # This code reads in my database's URL, which is listed on the home page for my database within elephantsql.com. As shown below, SQLAlchemy can use this URL to connect to the database. 

    else: # The URL for the ElephantSQL database will
    # be accessed through a Secret Manager volume stored online
        with open('/projsecrets/elephant-sql-db-url') as file:
            db_url = file.read()
        # Based on https://stackoverflow.com/questions/68533094/how-do-i-access-mounted-secrets-when-using-google-cloud-run
        # In order for this step to work, I needed to go to 
        # https://console.cloud.google.com/run , select 'Edit & Deploy New Revision,'
        # and then mount my secret (which I had created earlier) as a volume. 
        # (I chose 'projsecrets' as my volume
        # name.
        # Note that the Secret Manager Secret Accessor role must be enabled for 
        # your service account for your code to work, as noted here:
        # https://cloud.google.com/run/docs/configuring/secrets#access-secret

    # Now that we've retrieved the URL, we can use it to connect to the
    # online database. 

    elephantsql_db_url_for_sqlalchemy = db_url.replace('postgres://', 'postgresql://')
    # This change, which is required for SQLAlchemy to work correctly, is based on the code suggested at:
    # # https://help.heroku.com/ZKNTJQSK/why-is-sqlalchemy-1-4-x-not-connecting-to-heroku-postgres

    elephantsql_engine = sqlalchemy.create_engine(elephantsql_db_url_for_sqlalchemy)
    df_curr_enrollment = pd.read_sql("select * from curr_enrollment", con = elephantsql_engine)

else: # In this case, the file will be read 
        # locally rather than from the online database.
    df_curr_enrollment = pd.read_csv('../curr_enrollment.csv')



app = Dash(__name__,
           external_stylesheets=[dbc.themes.BOOTSTRAP])
# See https://dash-bootstrap-components.opensource.faculty.ai/docs/

server = app.server # Added based on 
# https://dash.plotly.com/deployment#heroku-for-sharing-public-dash-apps-for-free
# Don't add a () after 'server'!

enrollment_comparisons = ['School', 'Grade', 'Gender',
'Race', 'Ethnicity']

# The usage of dbc elements in the following lines
# comes from 
# https://dash-bootstrap-components.opensource.faculty.ai/docs/components/layout/
# and  
# https://github.com/facultyai/dash-bootstrap-components/blob/main/examples/gallery/faithful/app.py
app.layout = dbc.Container([
    html.H1(children='Dash School Dashboard', style={'textAlign':'center'}),
    dbc.Row(
        [dbc.Col('Schools:', width = 2),
            dbc.Col(
            dcc.Dropdown(df_curr_enrollment['School'].unique(), 
            list(df_curr_enrollment['School'].unique()), 
            id='school_filter', multi=True))]),
    dbc.Row([dbc.Col('Grades:', width = 2),
        dbc.Col(
        dcc.Dropdown(df_curr_enrollment['Grade'].unique(), 
        list(df_curr_enrollment['Grade'].unique()), id='grade_filter', multi=True))]),
    dbc.Row(
        [dbc.Col('Comparison Options:', width = 2),
        dbc.Col(
            dcc.Dropdown(enrollment_comparisons, 
        ['School'], id='enrollment_comparisons', multi=True), width = 3)
    ]),

    dbc.Row(
        [dbc.Col('Color bars by:', width = 2),
        dbc.Col(
            dcc.Dropdown(enrollment_comparisons, 
        'School', id='color_bars_by', multi=False), width = 3)]),


        dcc.Graph(id='enrollment_chart')
])

@callback(
    Output('enrollment_chart', 'figure'),
    Input('school_filter', 'value'),
    Input('grade_filter', 'value'),
    Input('enrollment_comparisons', 'value'),
    Input('color_bars_by', 'value')
)
def update_graph(school_filter, grade_filter, 
    enrollment_comparisons, color_bars_by):
    print("School filter:",school_filter)
    print("Grade filter:",grade_filter)
    print("Enrollment comparisons:",enrollment_comparisons)
    return create_interactive_bar_chart_and_table(
        original_data_source=df_curr_enrollment, y_value = 'Students', 
        comparison_values = enrollment_comparisons, pivot_aggfunc= 'sum', 
        filter_list = [('School', school_filter), ('Grade',grade_filter)], 
        color_value = color_bars_by, reorder_bars_by = 'Grade', 
        reordering_map = {'K':0, '1':1, '2':2, '3':3, '4':4, '5':5, '6':6, 
        '7':7, '8':8, '9':9, '10':10, '11':11, '12':12, 1:1, 2:2, 3:3, 
        4:4, 5:5, 6:6, 7:7, 8:8, 9:9, 10:10, 11:11, 12:12}, debug = False)

if __name__ == '__main__':
    app.run(debug=True)