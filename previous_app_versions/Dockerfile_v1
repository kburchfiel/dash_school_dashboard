# Source: https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-service

# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.11-slim

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Install production dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:server
# Note: I changed the final part to app:server because I was receiving error messages
# relating to gunicorn's inability to find 'main,' and because Arturo Tagle Correa's
# guide showed app:server here as well (See https://medium.com/kunder/deploying-dash-to-cloud-run-5-minutes-c026eeea46d4 ).
# Note that the sample Heroku Procfile provided by Dash also 
# ends in app:server : https://dash.plotly.com/deployment