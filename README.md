## OVERVIEW: 
This is the backend service used by the Differential Altimetry Android application. The android application can be viewed on [Github](https://github.com/krtonga/differential-altimetry-android) or downloaded via the [App Store](https://play.google.com/apps/testing/krtonga.github.io.differentialaltimetryandroid). The link to the arduino code is in the Android Application README. 


## DEVELOPMENT:
This is a basic flask server. To run locally, use the following commands:
 ```bash
 #setup the virtual environment
 pip3 install virtualenv
 virtualenv venv
 pip3 install -r requirements.txt
 
 #start the virtual environment
 source venv/bin/activate
 export FLASK_APP=diffaltimetry.py
 
 #setup an empty db
 python db_create.py
 
 #run on localhost
 python diffaltimetry.py
```
 
After updating database models don't forget to generate and run migration scripts:
 ```bash
 flask db migrate -m "thing you did"
 flask db upgrade
 ```
 
And write some tests while you're at it!
 ```bash
 # run existing tests with
 python tests/test_api.py
 python tests/test_auth.py
 ```

## Cloud setup - testing changes
At the moment there's a test instance running on diffalt.org. That's a Digital Ocean droplet running Ubuntu 16.04, with the Flask app being served via uWSGI behind an nginx reverse proxy.

The diffalt.org server is running on the ```cloud``` branch of the Git repo. To test new changes, merge them into that branch, ssh into the server (diffalt@diffalt.org) with the password that you know if you have any business in there, and:

- Navigate to /home/diffalt/differential-altimetry-flask
- ```git pull``` to bring in the changes on the cloud branch, then:

```
sudo systemctl restart diffaltimetry.service 
sudo systemctl restart nginx
```

Unless you've fucked something up, that'll restart the app with the new changes from the ```cloud``` branch of the Github. Test away.

Something not working as expected? Logs can be found at `/var/log/syslog`
 
### APPRECIATIONS:
Thank you to [The Flask Mega-Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world) and all the tall boys on the Diff-Alt team.