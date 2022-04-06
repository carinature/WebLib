# WebLib

site is published at https://karinature.pythonanywhere.com/
(static site is published at https://karinature.github.io/WebLib/)
{project_root} = [...]/Project_Dir

## Instruction for first time loading the project:
note: Make sure the server running the flask uses python3 as default (this can be checked using the command `python --version`).
If not, there are simple guides online, tailored for your operating system.
#### Before running the website app:
**Install requirements** using `pip3 install -r requirements.txt`
note: yor should be on the same dir as requirements.txt file (in {project_root})
#### Running the app
##### If running on a server without sql (e.g. basic local machine):
in project root run the `rf` script. 
Shell command:  `cd {project_root} && ./rf`  
This will use a docker with an sql (on port 3306), and creates an admin port (8080).
##### if running on a server with sql (e.g. pythonanywhere)
just make sure to put the correct file `wsgi.py` in /var/www/{karinature_pythonanywhere_com_}wsgi.py 
[https://www.pythonanywhere.com/user/karinature/files/var/www/karinature_pythonanywhere_com_wsgi.py ] 
Note: It is highly recommended to follow the deployment's server *official* manual/guide.
#### DB Migration (first time)
Currently you can either go to the `{home_url}/csv_to_mysql_route` on your favorite internet explorer 
or run `python db_migration.py`
  
### Loading the site (not first time, after loading db)
Just run thr command `./rf` from project_root, if no sql on machine
or `flask run` from {project_root}

## Instructions for Loading the site on PyhtonAnywhwer.com
#### Creating and loading the web app
###### option 1
On your Dashboard (the landing page after login, or `https://www.pythonanywhere.com/user/{user_name}`), 
on the tabs panel in the top-right corner, click the **Web** link (top right corner).
1. Click **Add a new web app** button.
2. Select **Flask**
3. Select **Python3.7** or **Python3.8**
4. Under **Security:** section click on the **Force HTTPS** toggle button so it will show a blue *Enabled*


You can go ahead and clack on the Green **Reload** button; 
Wait until finished reloading and the reload icon not showing anymore and go to the website page 
(url is in the link above the reload button or can be found in the list under **Web apps** section in the **Dashboard** ).
It will show a minimal page with a welcome message. note: this is not the real website. 

#### Open a **Bash** console 
####### option 1
On your Dashboard (the landing page after login, or `https://www.pythonanywhere.com/user/{user_name}`), 
on the tabs panel in the top-right corner, click the **Consoles** link (top right corner).
Open a bash console: Under the **Start a new console** headline pick **Bash**.
####### option 2
On your Dashboard (the landing page after login, or `https://www.pythonanywhere.com/user/{user_name}`), 
 Under the **Consoles** headline either pick an open Bash console or click **Bash** button.

p.s: don't worry if you need to create or delete console 
(for instance, if you have a beginner account which has a limit of 2 consoles).

#### Downloading project source code 
Go to your Project Working Directory (can be found in **Web** under *Code*, typically it's /home/_{user_name}_)
Inside the console run: `git clone https://github.com/karinature/WebLib.git`
1. `cd ~`
2. `ls` should show you:
    
    README.txt  WebLib  mysite
3. `cp WebLib/ mysite/ -r`
4. `rm -r mysite/`  # this is improtant in cases of low disk space

#####   Configure WSGI file
Go to the **Web** tab (can be found on top-right corner tab panel).
Under **Code:** section click the link to the **WSGI configuration file** 
and override its contents with the one from *user_name_pythonanywhere_com_wsgi.py*
#####   Configure a Production (???)Run
In the **Files** tab open the file __init__.py located in the *app* direcroty (full path: `~/mysite/app/__init__.py`)
Comment out the line `app.config.from_object('config.DevConfig')`
and unComment the line `app.config.from_object('config.ProdConfig')`


##### Create and Use a vireturl env
`mkvirtualenv --python=/usr/bin/python3 my-virtualenv`
and then:` workon my-virtualenv`
###### note: anytime you will use the Bash console you should start with `workon my-virtualenv`, otherwise you won't be able to use the installed packages
Go to the **Web** tab (can be found on top-right corner tab panel).
Under **Virtualenv:** enter in the field the path to the virtualenv.
This will be something like /home/{user_name}/.virtualenvs/my-virtualenv.
######## note: if needed, some more useful info here: https://help.pythonanywhere.com/pages/Virtualenvs/

##### Install Packages
`cd ~/mysite`
run `pip install -r requirements.txt` in the **Bash** console
note: possible issues are listed in the Issues section at the bottom of this README

#### Creating and loading the MySQL DB 
On your Dashboard (the landing page after login, or `https://www.pythonanywhere.com/user/{user_name}`), 
on the tabs panel in the top-right corner, click the **Databases** link (top right corner).
Make sure you're in the MySQL tab/option on the left (not Postgres).
##### Create
Under the **Create a database** headline enter `tiresias_sqldb` (all lower case!) and click **create**.
No need to set a password - it is handled in the project source code.
##### Configure

##### Load
This step make take up to a few hours



###### option 2
Select **Manual configuration**











## structure and file summery
**rf** - shell scrypt running the website/application on the local machine paste in the bash console: `cd {project_root} && ./rf`

**.env** - contains the secrets (variables such as SECRET_KEY)

**config**.py - configurations for the app and initialization 

**\_\_init__**.py - containing the definition of _create_app_

**wsgi**.py - this is where the website application actually created

**mysqldocker-compose.yml** - container with a mysql server

**requirements**.txt - python libs required for the functionality

**db_migration**.py - a scrypt that creates the DB and only needs to be used once - when launching the website 


#### The Following files and folders are within the app folder

**routes**.py - defines the views 

**models**.py - defines the table structures in the DB 

**forms**.py - defines the form structures, eg: search-bar and filter 

**raw_data** - contains the csv files from which the SQL DB is created

**templates** - contains the html templates rendered in _routes.py_

**static** - contains rest of the static files:\
    ***css*** - 
        all the original bootstrap-4 files\
        *bs4-style.css* and search-engine-main.css (examples from the web)\
        *style.css* has more specific properties\
        *Spectral-Regular.ttf* is the font currently chosen\
    ***images***\
    ***js*** - 
        all the original bootstrap-4 + JQuery + Popper files\
        *gui.js* - defines the functionality for the dynamic qualities of the static content\

   
## SQL Server (Local) 
run it:\
`docker-compose up -d -f mysql-docker-compose.yml`

connect to server:\
`mysql -h 127.0.0.1 -u root -P 3306 -p <MYSQL_ROOT_PASSWORD>`

###### If you Stop running containers without removing them They can be started again with
    
stop server:\
`docker-compose stop -f mysql-docker-compose.yml` 
    
start server: \
`docker-compose start -f mysql-docker-compose.yml`

##Isues
##### If the next error is shown, while running docker
    Error starting userland proxy: listen tcp 0.0.0.0:3306: bind: address already in use
run the next command:\
`sudo netstat -laputen | grep :3306`\
and then:\
`sudo systemctl stop PROGRAM_NAME`


##### If the next error is shown, while running docker
    (mysql.connector.errors.ProgrammingError) 1054 (42S22): Unknown column '<col name>' in 'field list'
might be a case of existing table while trying to load new/updated modules to the DB.
try to delete the existing table (in the MySQL console):\
`show tables;`\
`DROP TABLE IF EXISTS <table name>;`


##### If error: 
Sometimes, for some reason or other (like after renaming the database), there will be an error:
`sqlalchemy.exc.ProgrammingError: (mysql.connector.errors.ProgrammingError) 1049 (42000): Unknown database '{database_name}'` ,e.g.    
 
    sqlalchemy.exc.ProgrammingError: (mysql.connector.errors.ProgrammingError) 1049 (42000): Unknown database 'tiresiassqldb'
In that case, if possible, on the SQL server, run the command:
`CREATE DATABASE {database_name};`(e.g. `CREATE DATABASE tiresiassqldb;`)
and run db_migration.py script (`python3 db_migration.py` from {prject_root
or, on your internet explorer, go to the url 

    {home_page}/csv_to_mysql_route
   
or contact the person in charge of database maintenance 

### In PythonAnywhere
##### when running `pip install -r requirements.txt`
in case you've reached disk quota (this can happen in the *Beginner*  account )
try this steps in the bash console:

    deactivate  # this deactivats the virtual env
    rm -rf /home/{user_name}/.virtualenvs/my-virtualenv/
    rm -rf /tmp/* /tmp/.*
    rm -rf */tmp/* */tmp/.*
    du -hs /tmp ~/.[!.]* ~/* | sort -h  # this show disk-usage
    rm -rf /home/{user_name}/.cache/   
    rm -rf ~/.cache/   
    rm -rf */.cache/   
    ####### dont you dare run this, no matter how tempting : rm -rf /home/wildhrushka/.local/
    ####### but if you did... go to **Web**, at the bottom click on the **Delete** button and then **Add a new web app** at the top. no need to repeat the rest of the steps again
when finished cleaning go to your projects home directory {project_home}:
    `cd  /home/{user_name}/mysite/`
recreate the virtual env:
   ` mkvirtualenv --python=/usr/bin/python3 my-virtualenv`
and then either run
`pip install -r requirements.txt`
or `pip install {package_name}` for each of the lines in **reauirements.txt**
(or
1. run `pip install -r requirements.txt` 
2. run `pip install -r requirements.txt` again, 
3. for every requirement from reqs.txt run an individual pip install command)





wsgi.py is found in /var/www/karinature_pythonanywhere_com_wsgi.py 
[https://www.pythonanywhere.com/user/karinature/files/var/www/karinature_pythonanywhere_com_wsgi.py ] 
(no meaning for the wsgi file in `mysite` folder)

#

