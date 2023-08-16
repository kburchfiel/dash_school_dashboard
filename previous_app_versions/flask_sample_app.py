# Flask app that I'm planning to attempt to add Dash onto
# Source of original app: 
# https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-service

import os

from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello_world():
    """Example Hello World route."""
    name = os.environ.get("NAME", "World")
    return f"Hello {name}! (Note: the web demo of my school dashboard app is currently down because I'm trying out an alternative setup that will feature a dash app on top of a pre-existing flask app (like this one). I hope to have the main school dashboard demo back up soon.)"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8050)))
    # Changed to 8050 to match previous version of app