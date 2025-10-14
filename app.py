from flask import Flask, render_template
import pymongo
from dotenv import load_dotenv
import os

app = Flask(__name__)

def create_app():
    app = Flask(__name__)
    load_dotenv()

    # client =

    @app.route("/")
    def hello_world():
        return render_template('index.html')
        
    @app.route("/about")
    def about():
        return render_template('base.html')

app = create_app()

if __name__ == '__main__':
    FLASK_PORT = os.getenv("FLASK_PORT", 5000)
    FLASK_ENV = os.getenv("FLASK_ENV")
    
    print(f"FLASK_ENV: {FLASK_ENV}, FLASK_PORT: {FLASK_PORT}")

    app.run(port=FLASK_PORT)