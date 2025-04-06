# File: flask_app.py
# Swagger API URL: http://localhost:5000/apidocs
from application import create_app
from config import ProductionConfig
import os
from dotenv import load_dotenv

load_dotenv()

app = create_app(ProductionConfig)

if __name__ == "__main__":
    app.run(debug=True)
