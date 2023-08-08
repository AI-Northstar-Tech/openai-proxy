from proxy_app.app import app
from waitress import serve
import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=5000)
