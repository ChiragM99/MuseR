# MuseR

# Machine Learning Music Recommendation App

To run the app:

# Installation on Windows PowerShell

1. Install python3 on your computer

2. Open terminal

3. Install pip: python get-pip.py

4. Locate to an empty "main" directory to add project folder

5. Add MuseR Project folder to directory

6. Install virtual enviroment: pip install virtualenv env

7. Go to env directory

8. Activate the virtualenv: ./Scripts/activate

9. Go back to the main directory and add the project folder.

10. Go to the project directory where requirements.txt is located

11. Install dependancies: pip install -r requirements.txt

12. Run localhost server: python manage.py runserver


# API Key

A client secret and ID is required from the Spotify for Developers website. This is obtained by creating a Spotify account 
and navigating to the Spotify for Developers page. From there this, the Django app must be registered and a client ID and Secret
will be given. These must be entered into the respetive settings.py variables (line  called CLIENT_ID and CLIENT_SECRET, for the API to function.
These client credentials are sensitive information and are therefore not shared.

Spotify credentials can be obtained here: https://developer.spotify.com/documentation/general/guides/app-settings/
settings.py is located at: MuseR/settings.py

# Admin

To access the Django admin page enter /admin from root URL.
Enter the login details:

Username: admin
Password: admin
