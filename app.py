from flask import Flask, render_template, request, redirect, url_for, flash
import pymongo
from dotenv import load_dotenv
import os
from datetime import datetime

app = Flask(__name__)

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "your-secret-key-here")
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
    
    @app.route("/add-trail", methods=['GET', 'POST'])
    def add_trail():
        if request.method == 'POST':
            try:
                # Get form data
                trail_name = request.form.get('trail_name')
                difficulty = request.form.get('difficulty')
                time_taken = request.form.get('time_taken')
                time_unit = request.form.get('time_unit')
                trail_notes = request.form.get('trail_notes')
                distance = request.form.get('distance', '')
                elevation_gain = request.form.get('elevation_gain', '')
                best_time = request.form.get('best_time', '')
                
                # Validate required fields
                if not trail_name or not difficulty or not time_taken or not trail_notes:
                    flash('Please fill in all required fields!', 'error')
                    return render_template('add_trail.html')
                
                # For now, just show success message (MongoDB will be implemented later)
                flash(f'Trail "{trail_name}" added successfully!', 'success')
                return redirect(url_for('add_trail'))
                    
            except Exception as e:
                flash(f'An error occurred: {str(e)}', 'error')
                print(f"Error adding trail: {e}")
                return render_template('add_trail.html')
        
        return render_template('add_trail.html')

    return app

if __name__ == '__main__':
    app = create_app()
    FLASK_PORT = os.getenv("FLASK_PORT", 5000)
    FLASK_ENV = os.getenv("FLASK_ENV")
    
    print(f"FLASK_ENV: {FLASK_ENV}, FLASK_PORT: {FLASK_PORT}")

    app.run(port=FLASK_PORT, debug=True)