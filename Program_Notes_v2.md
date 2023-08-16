## Dash School Dashboard Setup Notes

Kenneth Burchfiel

## Steps I took:

I started my project by writing code that would prove useful in my Dash app, even though it wasn't Dash-specific.

1. I created a database table within database_generator.ipynb, then saved it to a .csv file. (I'll create a cloud-based verison later on.)

1. I created a function within plotly_sandbox.ipynb that can produce visualizations of this database table. This function will play a central role in my Dash app.

Now that I had some code in place for my program, I switched my attention to getting a demo Dash application set up both locally and in the cloud. The official [Dash Tutorial](https://dash.plotly.com/installation) proved very helpful here.

First, as suggested in the tutorial's [Dash Installation](https://dash.plotly.com/installation) section, I created a new Python environment called 'dashschooldashboard.' Activating this environment required only two steps, as explained [here](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-with-commands):

conda create --name dashschooldashboard

conda activate dashschooldashboard

Using Miniforge and conda, I then installed pandas, dash, and jupyter-dash into this library , as recommended in the Dash tutorial. (I also used pip to install gunicorn since this was recommended by a tutorial that I'll discuss later on.)

Next, I copied the demo app code in the tutorial's [Minimal App](https://dash.plotly.com/minimal-app) section into a new Python file called app.py, which in turn was placed into a folder named 'dsd' (short for 'dash_school_dashboard'). I then ran this file locally.

**Note:** I received a 'Service Unavailable' message in my Cloud Run version of this app when trying to use a name other than app.py. Therefore, I recommend sticking to app.py as the program's name.

I then switched my focus to getting my project online via Google Cloud Run. (In the past, I would have used Heroku for this step, but it's now more expensive than Google Cloud.) I started by getting the sample app to run online; after that step was complete, I could update the code to get my own app to run.

1. First, I created a new Google Cloud project within my [Google Cloud Console](https://console.cloud.google.com/) called 'kburchfiel-dash-apps'. My plan is to use this project for future Dash apps as well (thus limiting the number of Google Cloud Projects I'll need to set up and maintain). 

I then set up the Google Cloud Command Line Interface (CLI) on my computer; this tool allows me to run my Python project online via Google Cloud Run. (See ['Install the gcloud CLI'](https://cloud.google.com/sdk/docs/install) for more information.) Instead of using the bundled version of Python, I updated my Windows system PATH file with the Python environment I wanted to use. [This guide](https://leifengblog.net/blog/Installing-Google-Cloud-SDK-to-Use-Python-from-Anaconda/) explains how to accomplish this step. 

As instructed by the [Cloud Run setup guide](https://cloud.google.com/run/docs/setup), I enabled the Cloud Run API for this new project. 


1. With these setup tasks out of the way, I then followed the steps shown in Google's [Deploy a Python service to Cloud Run](https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-service) article, but made a couple changes along the way based on the [Dash Heroku deployment guide](https://dash.plotly.com/deployment#heroku-for-sharing-public-dash-apps-for-free) and on Arturo Tagle Correa's [Deploying Dash to Google Cloud Run in 5 minutes](https://medium.com/kunder/deploying-dash-to-cloud-run-5-minutes-c026eeea46d4) guide. These changes were necessary because the Deploy a Python Service to Cloud Run guide uses a Flask app as its example rather than Dash (which I believe is also based on Flask). This quote from the Dash Heroku guide also helped clarify things for me:

"Note that app refers to the filename app.py. server refers to the variable server inside that file."

(By the way, I didn't simply follow Arturo's guide because his method involves installing Docker desktop. However, Docker is not free for certain commercial use cases. The above steps did not require that I install Docker desktop.)

First, instead of using the main.py file shown in the Google article, I used the app.py example found [within the Layout section of the Plotly tutorial](https://dash.plotly.com/layout#more-about-html-components). (As discussed earlier, I also used the name 'app.py' instead of 'main.py' or anything else.) I then added  "server = app.server" under "app = Dash(\_\_name\_\_)" within this file, as this is seen in both Arturo's guide and Dash's Heroku deployment tutorial. 

Second, I used pip to install gunicorn into my virtual environment as shown in the Heroku deployment guide (although I'm not sure this was necessary, since I also added it to my requirements.txt file.)

Third, to create my requirements.txt file, I simply typed in:

dash

pandas

gunicorn


Fourth, I changed the final part of the Dockerfile example in the Google guide from "main:app" to "app:server", since (1) I was receiving error messages relating to gunicorn's inability to find 'main,'* and (2) [Arturo's guide](https://medium.com/kunder/deploying-dash-to-cloud-run-5-minutes-c026eeea46d4) showed app:server here as well. Note that the Heroku Procfile shown in the Heroku deployment guide also ends in app:server.

* Note to self: when running Flask apps (not dash apps) via Cloud Run, if you change the name of your app from 'main.py' to something else (e.g. 'app.py'), you'll also need to change 'main' to the name of your app (e.g. main:app --> app:app in the case of app.py). Otherwise, you'll receive an error message such as "no module named 'main'".

5. Once I made these changes, I was able to successfully deploy my app to Cloud Run. I did so by opening my command prompt, navigating to the folder containing my app.py file, and entering:

gcloud run deploy --source .

(Note that the space and period after 'source' are part of the command and must be included.)

For guidance on what to enter after this command, visit [this section](https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-service#deploy) of Google's Deploy a Python Service to Cloud Run guide.

You may also need to enter gcloud auth login if you haven't logged in already.

When asked to provide a service name, you can just hit Enter to choose the default option. ([Source](https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-service))

Ideally, after the CLI finishes processing your request, you'll see a message similar to the following:

"Service [dsd] revision [dsd-00003-qah] has been deployed and is serving 100 percent of traffic.
Service URL: https://dsd-vtwzngx2pa-uc.a.run.app"

Go ahead and click on the service URL (which will be different from the above URL in your case). You'll hopefully see a copy of the current version of your app. If you see a black page with a 'Service Unavailable' message, you'll likely need to modify your app's code or another file.

When errors arose, I could debug them using my project's log at https://console.cloud.google.com/logs/ . Sometimes, the most useful error messages were listed under the 'Default' severity category rather than the 'Error category,' so try looking at all messages instead of just those labeled 'error' when needed. Trying to run the app locally can also help, as an error that you encounter during local debugging can also be the explanation for an issue with the cloud-based version of the app.

In order to limit the cost of your project, you may want to delete older versions of your app from Google's storage. You can do so by going to console.cloud.google.com, navigating to the Cloud Storage section, and deleting obsolete copies of your app. Similarly, you can go to https://console.cloud.google.com/artifacts/docker/ to delete obsolete Docker containers. (To identify any other services, such as Cloud Run, that are incurring charges, go to https://console.cloud.google.com/billing)

6. Now that I had successfully deployed a sample Dash app to Cloud Run, I revised my app.py file to incorporate my school dashboard code. Although I could get this app to run locally by importing data from a .csv file, this approach wouldn't work online, since Cloud Run wouldn't be able to import it from my computer.

Therefore, in order to share my app with others online, I'd first need to connect it to a database hosted in the cloud. I chose to use ElephantSQL for this purpose, since it offers free PostgreSQL hosting provided that your database isn't too large in size. (See database_generator.ipynb for the steps I took to create this database and import it into ElephantSQL.) Since this process requires both sqlalchemy and psycopg2-binary, I added both of these to my requirements.txt file. (I used psycopg2-binary instead of psycopg to avoid an error message.)

In order to enable Google to access my ElephantSQL database's URL while keeping the value of the URL secure, I enabled the Google Cloud Secret Manager API (see Google Cloud's ["Use secrets"](https://cloud.google.com/run/docs/configuring/secrets) guide for more details) and then entered my ElephantSQL database URL as a new secret. (I did change the 'postgres:' component to 'postgresql:'--see [this link](https://help.heroku.com/ZKNTJQSK/why-is-sqlalchemy-1-4-x-not-connecting-to-heroku-postgres) for an explanation.

However, simply creating the secret was not sufficient: I also needed to add it to my Cloud Run service. I did so by visiting https://console.cloud.google.com/run for my project; selecting 'Edit & Deploy New Revision'; and then clicking "ADD A SECRET REFERENCE" so that I could mount my secret as a volume. (I chose 'projsecrets' as my volume name.) More information about this step can be found in the "Use secrets" guide linked to above.

Note that the Secret Manager Secret Accessor role must be enabled for your service account for your code to work. This is also mentioned in the "Use secrets" guide.
https://cloud.google.com/run/docs/configuring/secrets#access-secret In my case, Google prompted me to enable this access while I was adding my reference to my Cloud Run service, so I didn't have to go into my service account settings to make this update.

In order for my Python script to access this secret, I simply needed to open it as I would with any other file. See the code in app.py for an example. (https://stackoverflow.com/questions/68533094/how-do-i-access-mounted-secrets-when-using-google-cloud-run was a helpful resource for this step.)

One limitation with this approach is that these steps will only work when the app was running online, since the file with the secret isn't available locally. However, I got around this limitation by creating a read_from_online_db Boolean variable within app.py. When set to True (for online deployment), the code would load the variable within its volume on Google; when set to False, the code would instead load this variable from a local file on my computer. There's probably a more elegant way to resolve this discrepancy, but it worked for my use cases.

Note: When going through these steps for an earlier project, I installed the google-cloud-secret-manager library into my Python environment (as advised by ['Using Secret Manager With Python'](https://codelabs.developers.google.com/codelabs/secret-manager-python#3)) and also added it to my requirements.txt file. However, in the case of my current project, I was able to get the code to run on Cloud Run without performing either of these steps.

**Implementing more advanced graphs**

In order to create more interactive graphs, I reviewed the [Basic Callbacks](https://dash.plotly.com/basic-callbacks) component of the Dash walkthrough, along with the dropdown options provided on Plotly's [dcc.Dropdown](https://dash.plotly.com/dash-core-components/dropdown) page. Using these tools and other resources that I found along the way, I was able to revise my graphs to incorporate more interactive features. However, this revision process is still a work in progress.
