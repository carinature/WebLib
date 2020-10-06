from app import create_app
import os

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))

app = create_app()

if __name__ == "__main__":
    app.run(host='0.0.0.0')
