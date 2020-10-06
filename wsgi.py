
import os
project_home = os.path.dirname(os.path.abspath(__file__))

# add your project directory to the sys.path
import sys
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

from dotenv import load_dotenv
load_dotenv(os.path.join(project_home, '.env'))

from app import create_app
app = create_app()

# if __name__ == "__main__":
#     app.run(host='0.0.0.0')
