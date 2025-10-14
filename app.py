from flask import Flask, render_template
import pymongo
from dotenv import load_dotenv
import os

app = Flask(__name__)

def create_app():
    app = Flask(__name__)
    load_dotenv()

    load_dotenv()

    mongo_uri = os.getenv("MONGO_URI")

    client = pymongo.MongoClient(mongo_uri)
    db = client["SWEProj2"]

    @app.route("/")
    def hello_world():
        return render_template('index.html')
        
    @app.route("/about")
    def about():
        return render_template('base.html')

    @app.route("/trail")
    def trail():
        return render_template('trail.html')
    
    @app.route("/all-trails")
    def all_trails():
        return render_template('all-trails.html')

    return app
app = create_app()

if __name__ == '__main__':
    FLASK_PORT = os.getenv("FLASK_PORT", 5000)
    FLASK_ENV = os.getenv("FLASK_ENV")
    
    print(f"FLASK_ENV: {FLASK_ENV}, FLASK_PORT: {FLASK_PORT}")

    app.run(port=FLASK_PORT)