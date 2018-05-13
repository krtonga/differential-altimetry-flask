## OVERVIEW: 
This is the backend service used by the Differential Altimetry Android application. The android application can be viewed on [Github](https://github.com/krtonga/differential-altimetry-android) or downloaded via the [App Store](https://play.google.com/apps/testing/krtonga.github.io.differentialaltimetryandroid). The link to the arduino code is in the Android Application README. 


## DEVELOPMENT:
This is a basic flask server. To run locally, use the following commands:
 ```bash
 #setup the virtual environment
 pip install virtualenv
 virtualenv venv
 pip install -r requirements.txt
 
 #start the virtual environment
 source venv/bin/activate
 export FLASK_APP=diffaltimetry.py
 
 #setup an empty db
 python db_create.py
 
 #run on localhost
 flask run
 ```
 
After updating database models don't forget to generate and run migration scripts:
 ```bash
 flask db migrate -m "thing you did"
 flask db upgrade
 ```
 
And write some tests while you're at it!
 ```bash
 # run existing tests with
 python test_api.py
 ```
 
 
### APPRECIATIONS:
Thank you to [The Flask Mega-Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world) and the team.