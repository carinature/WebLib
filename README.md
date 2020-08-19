# WebLib

site is published at https://karinature.pythonanywhere.com/
(static site is published at https://karinature.github.io/WebLib/)

rf - shell scrypt running the website/application on the local machine         
paste in the bash console: `cd {project_root} && ./rf`
mysql-docker-compose.yml - container with a mysql server
requirements.txt - python libs required for the functionality
flask_app.py - main website application

one_off.py - a scrypt that creates the DB and only needs to be used once - when launching the website 

templates - contains html templates, for the static content
static - contains rest of the static files:
    css - 
        all the original bootstrap-4 files
        bs4-style.css and search-engine-main.css (examples from the web)
        style.css has more specific properties
        Spectral-Regular.ttf is the font currently chosen
    images
    js - 
        all the original bootstrap-4 + JQuery + Popper files
        gui.js - defines the functionality for the dynamic qualities of the static content

        
