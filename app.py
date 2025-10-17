from flask import Flask, render_template, request, redirect, url_for, flash
import pymongo
from pymongo.errors import ConnectionFailure, DuplicateKeyError
from dotenv import load_dotenv
import os
from datetime import datetime
from bson.objectid import ObjectId

app = Flask(__name__)


def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "your-secret-key-here")
    load_dotenv()

    mongo_uri = os.getenv("MONGO_URI")
    client = pymongo.MongoClient(mongo_uri)
    db = client["SWEProj2"]
    trails_collection = db["trails"]

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
        try:
            # Fetch all trails from MongoDB
            trails_cursor = db.trails.find()
            trails = list(trails_cursor)
            
            # Convert MongoDB documents to template-friendly format
            formatted_trails = []
            for trail in trails:
                formatted_trail = {
                    '_id': str(trail['_id']),
                    'name': trail.get('trail_name', ''),
                    'difficulty': trail.get('difficulty', ''),
                    'location': trail.get('location', 'Unknown'),
                    'duration': f"{trail.get('time_taken', '')} {trail.get('time_unit', '')}".strip(),
                    'notes': trail.get('trail_notes', ''),
                    'distance': trail.get('distance', ''),
                    'elevation_gain': trail.get('elevation_gain', ''),
                    'best_time': trail.get('best_time', ''),
                    'created_at': trail.get('created_at', '')
                }
                formatted_trails.append(formatted_trail)
            
            return render_template('all_trails.html', trails=formatted_trails)
            
        except Exception as e:
            print(f"Error fetching trails: {e}")
            flash('Error loading trails. Please try again.', 'error')
            return render_template('all_trails.html', trails=[])
   
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
                location = request.form.get('location', 'Unknown')

                # Validate required fields BEFORE database insertion
                if not trail_name or not difficulty or not time_taken or not trail_notes:
                    flash('Please fill in all required fields!', 'error')
                    return render_template('add_trail.html')

                # Create trail document with timestamp
                trail_doc = {
                    "trail_name": trail_name,
                    "difficulty": difficulty,
                    "time_taken": time_taken,
                    "time_unit": time_unit,
                    "trail_notes": trail_notes,
                    "distance": distance,
                    "elevation_gain": elevation_gain,
                    "best_time": best_time,
                    "location": location,
                    "created_at": datetime.utcnow()
                }

                # Insert into MongoDB
                result = db.trails.insert_one(trail_doc)
                
                if result.inserted_id:
                    flash(f'Trail "{trail_name}" added successfully!', 'success')
                    return redirect(url_for('add_trail'))
                else:
                    flash('Failed to save trail. Please try again.', 'error')
                    return render_template('add_trail.html')
                   
            except ConnectionFailure as e:
                flash('Database connection failed. Please try again later.', 'error')
                print(f"Database connection error: {e}")
                return render_template('add_trail.html')
            except DuplicateKeyError as e:
                flash('A trail with this name already exists.', 'error')
                print(f"Duplicate key error: {e}")
                return render_template('add_trail.html')
            except Exception as e:
                flash(f'An error occurred: {str(e)}', 'error')
                print(f"Error adding trail: {e}")
                return render_template('add_trail.html')
       
        return render_template('add_trail.html')

    @app.route("/edit-trail/<trail_id>", methods=['GET', 'POST'])
    def edit_trail(trail_id):
        if request.method == 'POST':
            try:
                # Get form data
                trail_name = request.form.get('trail_name')
                difficulty = request.form.get('difficulty')
                location = request.form.get('location')
                time_taken = request.form.get('time_taken')
                time_unit = request.form.get('time_unit', '')
                trail_notes = request.form.get('trail_notes')
                distance = request.form.get('distance', '')
                elevation_gain = request.form.get('elevation_gain', '')
                best_time = request.form.get('best_time', '')
               
                # Validate required fields
                if not trail_name or not difficulty or not location or not time_taken or not trail_notes:
                    flash('Please fill in all required fields!', 'error')
                    return redirect(url_for('edit_trail', trail_id=trail_id))

                print(trail_name, difficulty, location, time_taken, trail_notes, distance, elevation_gain, best_time)
               
                updated_data = {
                    'trail_name': trail_name,
                    'difficulty': difficulty,
                    'location': location,
                    'time_taken': time_taken,
                    'time_unit': time_unit,
                    'trail_notes': trail_notes,
                    'distance': distance,
                    'elevation_gain': elevation_gain,
                    'best_time': best_time,
                    'updated_at': datetime.utcnow()
                }
                result = trails_collection.update_one(
                    {'_id': ObjectId(trail_id)},
                    {'$set': updated_data}
                )

                if result.matched_count == 0:
                    flash('Trail not found for update.', 'error')
                    return redirect(url_for('all_trails'))
                if result.modified_count == 0:
                    flash('No changes detected.', 'info')
                    return redirect(url_for('all_trails'))

                flash(f'Trail "{trail_name}" updated successfully!', 'success')
                return redirect(url_for('all_trails'))
                   
            except Exception as e:
                flash(f'An error occurred: {str(e)}', 'error')
                print(f"Error updating trail: {e}")
                return redirect(url_for('edit_trail', trail_id=trail_id))
       
        trail = trails_collection.find_one({'_id': ObjectId(trail_id)})
        if not trail:
            flash('Trail not found!', 'error')
            return redirect(url_for('all_trails'))
        return render_template('edit_trail.html', trail=trail, trail_id=trail_id)
        
    @app.route("/delete-trail/<trail_id>", methods=['GET', 'POST'])
    def delete_trail(trail_id):
        if request.method == 'POST':
            try:
                confirm_delete = request.form.get('confirm_delete')
                
                if confirm_delete == 'true':
                    trail = trails_collection.find_one({'_id': ObjectId(trail_id)})
                    trail_name = trail.get('trail_name', 'Unknown Trail') if trail else 'Unknown Trail'
                    
                    result = trails_collection.delete_one({'_id': ObjectId(trail_id)})
                    
                    if result.deleted_count > 0:
                        flash(f'Trail "{trail_name}" has been deleted successfully.', 'success')
                    else:
                        flash('Trail not found or already deleted.', 'error')
                    
                    flash('Trail deleted successfully!', 'success')
                    return redirect(url_for('all_trails'))
                else:
                    flash('Delete confirmation not received.', 'error')
                    return redirect(url_for('delete_trail', trail_id=trail_id))
                   
            except Exception as e:
                flash(f'An error occurred: {str(e)}', 'error')
                print(f"Error deleting trail: {e}")
                return redirect(url_for('all_trails'))
       
        trail = trails_collection.find_one({'_id': ObjectId(trail_id)})
        if not trail:
            flash('Trail not found!', 'error')
            return redirect(url_for('all_trails'))
        return render_template('delete_trail.html', trail=trail, trail_id=trail_id)

    return app


if __name__ == '__main__':
    app = create_app()
    FLASK_PORT = os.getenv("FLASK_PORT", 5000)
    FLASK_ENV = os.getenv("FLASK_ENV")
   
    print(f"FLASK_ENV: {FLASK_ENV}, FLASK_PORT: {FLASK_PORT}")

    app.run(port=FLASK_PORT, debug=True)