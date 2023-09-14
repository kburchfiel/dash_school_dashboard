# Dash School Dashboard

Released under the MIT license

This project shows how to build a simple set of interactive school dashboards using Plotly and Dash. These dashboards, hosted on Google Cloud Run [via this link](https://dsd-vtwzngx2pa-uc.a.run.app/), display fictional data for a made-up school district. The dashboard pages (which may take a little while to load) show enrollment counts, test results, and graduation outcomes for the district; in addition, they allow users to modify the filter and comparison settings to alter the appearance of the charts.

My blog post on these dashboards can be found [here](https://wordpress.com/post/kburchfiel3.wordpress.com/557). 

## Usage Examples:

### Choosing how to compare data:
![](https://raw.githubusercontent.com/kburchfiel/dash_school_dashboard/main/usage_examples/dsd_comparisons.gif)

### Changing dashboard filters:
![](https://raw.githubusercontent.com/kburchfiel/dash_school_dashboard/main/usage_examples/dsd_filters.gif)

### Navigating between dashboards:
![](https://raw.githubusercontent.com/kburchfiel/dash_school_dashboard/main/usage_examples/dsd_page_navigation.gif)

### Setting color and pattern options:
![](https://raw.githubusercontent.com/kburchfiel/dash_school_dashboard/main/usage_examples/dsd_setting_color_and_pattern.gif)

### Logging in and out:
![](https://raw.githubusercontent.com/kburchfiel/dash_school_dashboard/main/usage_examples/dsd_logging_in_and_out.gif)


# How These Dashboards Were Built

This guide explains how I created a simple Plotly dashboard; uploaded it to Cloud Run; connected it to an ElephantSQL database; and expanded the app into a multi-page setup. I hope you will find these steps useful in developing your own Dash apps.

## Part 1: Configuring a Basic Dashboard

I started my project by writing code that would prove useful in my Dash app, even though it wasn't Dash-specific. First, I created a database table within [database_generator.ipynb](https://github.com/kburchfiel/dash_school_dashboard/blob/main/database_generator.ipynb), then saved it to a .csv file. Next, I wrote some code that could produce visualizations of this database table. This code, which can be found within the `create_pivot_for_charts()` and `create_interactive_bar_chart_and_table()` code within [app_functions_and_variables.py](https://github.com/kburchfiel/dash_school_dashboard/blob/main/dsd/app_functions_and_variables.py) file, plays a central role in my Dash app. 

Now that I had some code in place for my program, I switched my attention to getting a demo Dash application set up both locally and in the cloud. The official [Dash Tutorial](https://dash.plotly.com/installation) proved very helpful here.

My first priority was to create a simple dashboard that I could successfully port to Google Cloud Run. Hosting a Dash app on Cloud Run isn't too difficult once you get the hang of it, but it does involve a number of steps, which I'll list below.

To start building this dashboard, I first created a new Python environment as suggested in the tutorial's [Dash Installation](https://dash.plotly.com/installation) section. Activating this environment, which I called 'dashschooldashboard, required only two steps: 

`conda create --name dashschooldashboard`

`conda activate dashschooldashboard`

([Source](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-with-commands))

Using Miniforge and conda, I then installed pandas, dash, and jupyter-dash into this library, as recommended in the Dash tutorial. (I also used pip to install gunicorn since this was recommended by a tutorial that I'll discuss later on.)

Next, I copied the demo app code in the tutorial's [Minimal App](https://dash.plotly.com/minimal-app) section into a new Python file called app.py, which in turn was placed into a folder named 'dsd' (short for 'dash_school_dashboard'). I then ran this Dash app locally; steps for doing so can be found within Dash's [Minimal Dash App](https://dash.plotly.com/minimal-app) documentation page. 

*Note: I received a 'Service Unavailable' message in my Cloud Run version of this app when trying to use a name other than app.py. Therefore, I recommend sticking to app.py as the program's name.*

## Part 2: Deploying the app on Cloud Run

I then switched my focus to hosting my project online via Google Cloud Run. In the past, I would have used Heroku for this step, but their [pricing data](https://www.heroku.com/pricing) indicates that it will cost at least $5 a month to run an app there. My Cloud Run setup, on the other hand, can cost only pennies per month (if that) depending on how frequently the app is used. (I do appreciate that Heroku has price caps for many of their hosting packages, so it could very well be the better option in case your Dash app is accessed frequently). 

I started the hosting process by getting a sample Dash app to run online; after that was complete, I could update the code to get my own app to run. Here are the steps I took to port my Dash app to Cloud Run:

1. First, I created a new Google Cloud project within my [Google Cloud Console](https://console.cloud.google.com/), which I named 'kburchfiel-dash-apps'. I then set up the Google Cloud Command Line Interface (CLI) on my computer; this tool allows me to run my Python project online via Google Cloud Run. (See ['Install the gcloud CLI'](https://cloud.google.com/sdk/docs/install) for more information.) Instead of using the bundled version of Python, I updated my Windows system PATH file with the Python environment I wanted to use. [This guide](https://leifengblog.net/blog/Installing-Google-Cloud-SDK-to-Use-Python-from-Anaconda/) explains how to accomplish this step. 

1. Next, as instructed by the [Cloud Run setup guide](https://cloud.google.com/run/docs/setup), I enabled the Cloud Run API for this new project. (If you don't complete this step now, you'll still be prompted to do so when deploying your app, so you can skip this part if you'd like.)

1. With these setup tasks out of the way, I then followed the steps shown in Google's [Deploy a Python service to Cloud Run](https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-service) article, but made a couple changes along the way based on the [Dash Heroku deployment guide](https://dash.plotly.com/deployment#heroku-for-sharing-public-dash-apps-for-free) and on Arturo Tagle Correa's [Deploying Dash to Google Cloud Run in 5 minutes](https://medium.com/kunder/deploying-dash-to-cloud-run-5-minutes-c026eeea46d4) guide. These changes were necessary because the Deploy a Python Service to Cloud Run guide uses a Flask app as its example rather than Dash (which I believe is also based on Flask). This quote from the Dash Heroku guide also helped clarify things for me: 

    *"Note that app refers to the filename app.py. server refers to the variable server inside that file."*

    (By the way, I didn't follow all of the steps in Arturo's guide because his method involves installing Docker desktop. However, Docker is not free for certain commercial use cases. The above steps did not require that I install Docker desktop.)

    One note before I go through these changes: The guide explains that you need to enter 'gcloud config set project PROJECT_ID' within the CLI in order to select your project, and that you should "Replace PROJECT_ID with the name of the project you created for this quickstart." However, make sure to replace Project ID with the project's ID, not its name, as the two won't always be the same! 
    
    (To find your project's ID, go to https://console.cloud.google.com/welcome and select your project within the top dropdown menu. You'll then be taken to a 'Welcome' page that shows your project's name (e.g. sample-app) and its ID (e.g. sample-app-398021). The ID will also be shown below the project name when you first creating your project.)

    Now, without further ado, here are the changes I made to the steps shown in the Cloud Run guide:

    1. Instead of using the main.py file shown in the Google article, I used the app.py example found [within the Layout section of the Plotly tutorial](https://dash.plotly.com/layout#more-about-html-components). (As discussed earlier, I also used the name 'app.py' instead of 'main.py'.) I then added  "server = app.server" under "app = Dash(\_\_name\_\_)" within this file, as this is seen in both Arturo's guide and Dash's Heroku deployment tutorial. 

    1. I used pip to install gunicorn into my virtual environment as shown in the Heroku deployment guide (although I'm not sure this was necessary, since I also added it to my requirements.txt file.)

    1. To create my requirements.txt file, I simply typed in:

        ```
        dash

        pandas

        gunicorn
        ```

    1. I changed the final part of the Dockerfile example in the Google guide from "main:app" to "app:server", since (1) I was receiving error messages relating to gunicorn's inability to find 'main,'* and (2) [Arturo's guide](https://medium.com/kunder/deploying-dash-to-cloud-run-5-minutes-c026eeea46d4) showed app:server here as well. Note that the Heroku Procfile shown in the Heroku deployment guide also ends in app:server. By the way, don't forget to capitalize 'Dockerfile' within your project directory!

        *Note: when running Flask apps (not Dash apps) via Cloud Run, if you change the name of your app from 'main.py' to something else (e.g. 'app.py'), you'll also need to change the 'main' part of main:app in the Dockerfile to the name of your app (e.g. main:app --> app:app in the case of app.py). Otherwise, you'll receive an error message such as "no module named 'main'". However, since we're building a Dash app here, we don't need to make this change.*

1. Once I made these changes, I was able to successfully deploy my app to Cloud Run. I did so by opening my command prompt, navigating to the folder containing my app.py file, and entering:

    `gcloud run deploy --source .`

    (Note that the space and period after 'source' are part of the command and must be included. You may also need to enter gcloud auth login if you haven't logged in already.)

    For guidance on what to enter within the Cloud Console after this command, visit [this section](https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-service#deploy) of Google's Deploy a Python Service to Cloud Run guide.

    When asked to provide a service name, I could just hit Enter to choose the default option. ([Source](https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-service))

    If the Artifact Registry API was not enabled earlier, I would see a message like "API [artifactregistry.googleapis.com] not enabled on project [kburchfiel-dash-apps]. Would you like to enable and retry (this will take a few minutes)? (y/N)? 

1. Ideally, after the CLI finished processing my request, I would see a message similar to the following:

    *"Service [dsd] revision [dsd-00003-qah] has been deployed and is serving 100 percent of traffic.
    Service URL: https://dsd-vtwzngx2pa-uc.a.run.app"*

1. I would then click on the service URL (which will be different from the above URL in your case). If everything went well, I would see a copy of the current version of my app, now hosted online for anyone to view and interact with. However, in many cases, I would instead see a black page with a 'Service Unavailable' message. This meant that an error in my app's code or another file was preventing Cloud Run from deploying my app.

1. When these errors arose, I could debug them using my project's log at https://console.cloud.google.com/logs/ . Sometimes, the most useful error messages were listed under the 'Default' severity category rather than the 'Error category,' so it was helpful to look at all of the messages rather than just those labeled 'error'. Trying to run the app locally could also help, as an error that you encounter during local debugging can also be the explanation for an issue with the cloud-based version of the app.

1. In order to limit the cost of my project, I usually delete older versions of my app from Google's storage after each new deployment. I can do so by going to console.cloud.google.com, navigating to the Cloud Storage section, and deleting obsolete copies of my app. Similarly, I can go to https://console.cloud.google.com/artifacts/docker/ to delete obsolete Docker containers. (To identify any other services, such as Cloud Run, that are incurring charges, I can go to https://console.cloud.google.com/billing)

## Part 3: Updating the sample Dash app with my own dashboard code 

Now that I had successfully deployed a sample Dash app to Cloud Run, I revised my app.py file to incorporate my school dashboard code. Although I could get this app to run locally by importing data from a .csv file, this approach wouldn't work online, since Cloud Run wouldn't be able to import it from my computer.

Therefore, in order to share my app with others online, I'd first need to connect it to a database hosted in the cloud. I chose to use [ElephantSQL](https://www.elephantsql.com/) for this purpose, since it offers free PostgreSQL hosting provided that your database isn't too large in size. (See [database_generator.ipynb](https://github.com/kburchfiel/dash_school_dashboard/blob/main/database_generator.ipynb) for the steps I took to create this database and import it into ElephantSQL.) Since this process requires both sqlalchemy and psycopg2-binary, I added both of these to my requirements.txt file. (I used psycopg2-binary instead of psycopg to avoid an error message.)

In order to enable Google to access my ElephantSQL database's URL while keeping the value of the URL secure, I enabled the Google Cloud Secret Manager API (see Google Cloud's ["Use secrets"](https://cloud.google.com/run/docs/configuring/secrets) guide for more details) and then entered my ElephantSQL database URL as a new secret. (I did change the 'postgres:' component to 'postgresql:'; see [this link](https://help.heroku.com/ZKNTJQSK/why-is-sqlalchemy-1-4-x-not-connecting-to-heroku-postgres) for an explanation.

However, merely creating the secret was not sufficient: I also needed to add it to my Cloud Run service. I did so by visiting https://console.cloud.google.com/run for my project; selecting 'Edit & Deploy New Revision'; and then clicking "ADD A SECRET REFERENCE" so that I could mount my secret as a volume. (I chose 'projsecrets' as my volume name.) More information about this step can be found in the "Use secrets" guide shared above.

Note that the Secret Manager Secret Accessor role must be enabled for your service account for your code to work. This is also mentioned in the "Use secrets" guide.
https://cloud.google.com/run/docs/configuring/secrets#access-secret In my case, however, Google prompted me to enable this access while I was adding my reference to my Cloud Run service, so I didn't have to go into my service account settings to make this update.

In order for my Python script to access this secret, I simply needed to open it as I would with any other file. See the code in [app_functions_and_variables.py](https://github.com/kburchfiel/dash_school_dashboard/blob/main/dsd/app_functions_and_variables.py) for an example. (https://stackoverflow.com/questions/68533094/how-do-i-access-mounted-secrets-when-using-google-cloud-run was a helpful resource for this step.)

One limitation with this approach is that these steps will only work when the app was running online, since the file with the secret isn't available locally. However, I got around this limitation by creating a read_from_online_db Boolean variable within app.py. When set to True, the code would load the variable within its volume on Google; when set to False, the code would instead load this variable from a local file on my computer. 

*Note: When going through these steps for an earlier project, I installed the google-cloud-secret-manager library into my Python environment (as advised by ['Using Secret Manager With Python'](https://codelabs.developers.google.com/codelabs/secret-manager-python#3)) and also added it to my requirements.txt file. However, in the case of my current project, I was able to get the code to run on Cloud Run without performing either of these steps.*


## Part 4: Implementing more advanced graphs and features

Now that I had the fundamentals of my app in place and had enabled it to work both on Cloud Run and on my computer, I could focus my attention on developing more advanced graphs while keeping the codebase manageable. 

In order to create more interactive graphs, I reviewed the [Basic Callbacks](https://dash.plotly.com/basic-callbacks) component of the Dash walkthrough, along with the dropdown options provided on Plotly's [dcc.Dropdown](https://dash.plotly.com/dash-core-components/dropdown) page. Using these tools and other resources that I found along the way, I was able to revise my graphs to incorporate more interactive features, such as filters and multiple comparison options.

The core functions that drive these interactive graphs are located not in the app.py file nor in the individual files for each dashboard, but instead in a file called [app_functions_and_variables.py](https://github.com/kburchfiel/dash_school_dashboard/blob/main/dsd/app_functions_and_variables.py). By defining the functions here, I can easily use them in multiple files, thus saving many lines of code and simplifying the dashboard update process. app_functions_and_variables.py also stores functions for adding in shared layout components, which further simplifies my codebase.

I also added in Dash's [pages feature](https://dash.plotly.com/urls), which not only simplifies the user experience (by dividing the charts into separate webpages) but also makes the code for each dashboard simpler.

In addition, I added a login feature to my app--not because there was any confidential data to protect (indeed, the data in the dashboards is made up), but rather to demonstrate how Dash apps can be password protected. I could have used Dash's free [Basic Auth](https://dash.plotly.com/authentication) feature, but I chose to try out a more sophisticated implementation developed by [Nader Elshehabi](https://github.com/naderelshehabi/dash-flask-login) and [Bryan/Jinnyzor](https://community.plotly.com/t/dash-app-pages-with-flask-login-flow-using-flask/69507/38). This setup uses the flask-login package to create an authentication system that functions outside of the Dash app. I am very grateful to both Nader and Jinnyzor for making their code available for others to use.

## Conclusion

I learned a great deal in the process of developing these fictional dashboards. I hope that the final codebase is simple enough for relative newcomers to Plotly and Dash to understand apply, yet complex enough to help meet real-world visualization needs.





