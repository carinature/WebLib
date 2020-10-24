# WebLib

site is published at https://karinature.pythonanywhere.com/
(static site is published at https://karinature.github.io/WebLib/)
   
## SQL Server (Local) 
    run it:
`docker-compose up -d -f mysql-docker-compose.yml`

    connect to server
`mysql -h 127.0.0.1 -u root -P 3306 -p <MYSQL_ROOT_PASSWORD>`

###### If you Stop running containers without removing them They can be started again with
    
    stop server:
`docker-compose stop -f mysql-docker-compose.yml` 
    
    start server: 
`docker-compose start -f mysql-docker-compose.yml`

##### If the next error is shown 
    Error starting userland proxy: listen tcp 0.0.0.0:3306: bind: address already in use
run the next command:
`sudo netstat -laputen | grep ':3306`
and then:
`sudo systemctl stop PROGRAM_NAME`


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

**routs**.py - defines the views 

**models**.py - defines the table structures in the DB 

**forms**.py - defines the form structures, eg: search-bar and filter 

**raw_data** - contains the csv files from which the SQL DB is created

**templates** - contains the html templates rendered in _routs.py_

**static** - contains rest of the static files:
    ***css*** - 
        all the original bootstrap-4 files
        *bs4-style.css* and search-engine-main.css (examples from the web)
        *style.css* has more specific properties
        *Spectral-Regular.ttf* is the font currently chosen
    ***images***
    ***js*** - 
        all the original bootstrap-4 + JQuery + Popper files
        *gui.js* - defines the functionality for the dynamic qualities of the static content

     