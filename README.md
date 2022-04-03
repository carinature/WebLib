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
  
## Loading the site (not first time, after loading db)
Just run thr command `./rf` from project_root, if no sql on machine
or `flask run` from {project_root}

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
##### If the next error is shown, while runnig docker
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
wsgi.py is found in /var/www/karinature_pythonanywhere_com_wsgi.py 
[https://www.pythonanywhere.com/user/karinature/files/var/www/karinature_pythonanywhere_com_wsgi.py ] 
(no meaning for the wsgi file in `mysite` folder)

