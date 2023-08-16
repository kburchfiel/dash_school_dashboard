# multi_page_app_with_dash_auth.py

# Alternative version of simple multi-page, login-required Dash app that uses dash_auth instead of flask-login




"""
 CREDIT: This code was originally adapted for Pages  based on Nader Elshehabi's  article:
   https://dev.to/naderelshehabi/securing-plotly-dash-using-flask-login-4ia2
   https://github.com/naderelshehabi/dash-flask-login

   This version is updated by Dash community member @jinnyzor For more info see:
   https://community.plotly.com/t/dash-app-pages-with-flask-login-flow-using-flask/69507

For other Authentication options see:
  Dash Enterprise:  https://dash.plotly.com/authentication#dash-enterprise-auth
  Dash Basic Auth:  https://dash.plotly.com/authentication#basic-auth

"""


import os
from flask import Flask, request, redirect, session, jsonify, url_for, render_template
import dash_auth # See https://dash.plotly.com/authentication

import dash
from dash import dcc, html, Input, Output, State, ALL, callback
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
# See https://dash-bootstrap-components.opensource.faculty.ai/examples/iris/#sourceCode



VALID_USERNAME_PASSWORD_PAIRS = {
    'basicauth': 'basicpassword'
}
# Test code from https://dash.plotly.com/authentication

app = dash.Dash(__name__,
           external_stylesheets=[dbc.themes.BOOTSTRAP], 
           use_pages = True,
           suppress_callback_exceptions = True)
# See https://dash-bootstrap-components.opensource.faculty.ai/docs/
# The following code comes from https://dash.plotly.com/authentication
auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)


server = app.server # Added based on 
# https://dash.plotly.com/deployment#heroku-for-sharing-public-dash-apps-for-free
# Don't add a () after 'server'!

app.layout = html.Div(
    [html.H1("Dash School Dashboard (work in progress)"),

 html.Div(
        [
            html.Div(
                dcc.Link(
                    f"{page['name']} - {page['path']}", href=page["relative_path"]
                )
            )
            for page in dash.page_registry.values()
        ]
    ), # From https://dash.plotly.com/urls

    dash.page_container

    ]
)



if __name__ == "__main__":
    app.run(debug=True)