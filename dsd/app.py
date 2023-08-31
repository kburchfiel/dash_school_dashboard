# Main app file for my interactive school dashboard

# By Kenneth Burchfiel
# Released under the MIT license (see below for credits for the login
# component of the code, which constitutes much of this particular file)

# There is not much visualization-related code within this file. Visit the
# files within the pages folder and the app_functions_and_variables file
# to see how the charts and tables shown in this app are generated.

# Note: All data in this dashboard is entirely fictional.

'''
CREDIT for the login component of the code: 
This code was originally adapted for Pages based on Nader Elshehabi's article:
https://dev.to/naderelshehabi/securing-plotly-dash-using-flask-login-4ia2
https://github.com/naderelshehabi/dash-flask-login
Nader's code has been made available under the MIT license.
(See https://github.com/naderelshehabi/dash-flask-login/blob/main/LICENSE.md)

This version was updated by Dash community member @jinnyzor. For more info, see:
https://community.plotly.com/t/dash-app-pages-with-flask-login-flow-using-flask/69507
https://community.plotly.com/t/dash-app-pages-with-flask-login-flow-using-flask/69507/38

For other Dash authentication options, see:
Dash Enterprise:  https://dash.plotly.com/authentication#dash-enterprise-auth
Dash Basic Auth:  https://dash.plotly.com/authentication#basic-auth

Jinnyzor kindly made this code free to use in other projects:
https://community.plotly.com/t/dash-app-pages-with-flask-login-flow-using-flask/69507/55

Much of the documentation in this app.py file comes from Nader and/or Jinnyzor
as well. I am very grateful to both of them for allowing me to incorporate
their terrific work into this project!
'''

# We'll first import a range of libraries: 
import os
from flask import Flask, request, redirect, session, jsonify, \
url_for, render_template
from flask_login import login_user, LoginManager, UserMixin, \
logout_user, current_user
import dash
from dash import dcc, html, Input, Output, State, ALL, callback
import pandas as pd
import plotly.express as px
import sqlalchemy
import dash_bootstrap_components as dbc

# Exposing the Flask Server so that it can be configured for the login process:
server = Flask(__name__)

@server.before_request
def check_login():
    if request.method == 'GET':
        if request.path in ['/login', '/logout']:
            return
        if current_user:
            if current_user.is_authenticated:
                return
            else:
                for pg in dash.page_registry:
                    if request.path == dash.page_registry[pg]['path']:
                        session['url'] = request.url
        return redirect(url_for('login'))
    else:
        if current_user:
            if (request.path == '/login') or (current_user.is_authenticated):
                return
        return jsonify({'status':'401', 'statusText':'unauthorized access'})


@server.route('/login', methods=['POST', 'GET'])
def login(message=""):
    if request.method == 'POST':
        if request.form:
            username = request.form['username']
            password = request.form['password']
            if VALID_USERNAME_PASSWORD.get(username) is None:
                return """The username and/or password you entered \
was invalid. Please try again: <a href='/login'>login here</a> """
            if VALID_USERNAME_PASSWORD.get(username) == password:
                login_user(User(username))
                if 'url' in session:
                    if session['url']:
                        url = session['url']
                        session['url'] = None
                        return redirect(url) ## redirect to target url
                return redirect('/') ## redirect to home
            message = "The username and/or password you entered was invalid. \
Please try again."
    else:
        if current_user:
            if current_user.is_authenticated:
                return redirect('/')
    return render_template('login.html', message=message)

@server.route('/logout', methods=['GET'])
def logout():
    if current_user:
        if current_user.is_authenticated:
            logout_user()
    return render_template('login.html', message="You have \
now been logged out.")

app = dash.Dash(
    __name__, server=server, use_pages=True, suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP])

# In a real-life app with actual data to protect, I would move these
# username and password pairs out of the source code.
VALID_USERNAME_PASSWORD = {"test": "test", "hello": "world"}

# Updating the Flask Server configuration with a secret key to encrypt 
# the user session cookie:
server.config.update(SECRET_KEY='notsosecretkey')
# In a non-demo app, I would move this key to my Cloud Run project's
# Secret Manager volume. (See the create_database_engine() function
# within the app_functions_and_variables.py file for more information
# about this step.)

# Login manager object will be used to log users in and out:
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = "/login"


class User(UserMixin):
    # User data model. It has to have at least self.id as a minimum
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(username):
    """This function loads the user by user id. Typically this looks up 
    the user from a user database. We won't be registering or looking up users 
    in this example, so we'll simply return a User object 
    with the passed-in username.
    """
    return User(username)

app.layout = html.Div(
    [
    html.A('logout', href='../logout'),
    html.Br(),
    html.H1("Dash School Dashboard"),

# The following code comes from
# https://dash.plotly.com/urls . It allows all of the files
# stored in the pages folder to show up as navigation links,
# thus allowing the user to navigate among pages.

 html.Div(
        [
            html.Div(
                dcc.Link(
                    f"{page['name']} - {page['path']}", 
                    href=page["relative_path"]
                )
            )
            for page in dash.page_registry.values()
        ]
    ), # From https://dash.plotly.com/urls

    dash.page_container

    ]
)



if __name__ == "__main__":
    app.run_server(debug=True)
# Earlier versions of this code that lacked the flask-login 
# functionality used app.run(), but run_server is used here instead 
# to accommodate the flask-based login setup. (The original code provided by
# Nader and Jinnyzor also uses app.run_server(). For example,
# see https://github.com/naderelshehabi/dash-flask-login/blob/main/app.py )