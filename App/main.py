
import os, csv
from flask import request, g
from flask_jwt_extended import jwt_required
from flask import Flask, render_template
from flask_uploads import DOCUMENTS, IMAGES, TEXT, UploadSet, configure_uploads
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage

from App.database import init_db
from App.config import load_config
from App.views import views
from App.controllers import (
    setup_jwt,
    add_auth_context
)

def add_views(app):
    for view in views:
        app.register_blueprint(view)
app = Flask(__name__)
def create_app(overrides={}):
    app = Flask(__name__, static_url_path='/static')
    load_config(app, overrides)
    CORS(app)
    add_auth_context(app)
    photos = UploadSet('photos', TEXT + DOCUMENTS + IMAGES)
    configure_uploads(app, photos)
    add_views(app)
    init_db(app)
    jwt = setup_jwt(app)
    
    @jwt.invalid_token_loader
    @jwt.unauthorized_loader
    def custom_unauthorized_response(error):
        return render_template('401.html', error=error), 401
    
    app.app_context().push()
    return app


def initialize_db():
    db.drop_all()
    db.create_all()
    with open('WorkoutDataset.csv', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            exercise = Exercises(
                id=int(row['id']),
                title=row['title'],
                desc=row['desc'],
                type=row['type'],
                bodypart=row['bodypart'],
                equipment=row['equipment'],
                level=row['level'],
                rating=int(row['rating']),
                rating_desc=row['rating_desc']
            )
            db.session.add(exercise)
    db.session.commit()



#**************Routes****************
        #Route to access all Excercises
'''
@app.route('/exercises', methods=['GET'])
@jwt_required()  
def get_exercises():
    try:
        exercises = Exercises.query.all()
        exercise_list = [exercise.get_json() for exercise in exercises]
        return jsonify(exercise_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
'''

@app.route('/exercises', methods=['GET'])
@jwt_required()  # Requires JWT token for access
def get_exercises():
    try:
        exercises = Exercises.query.all()
        return render_template('exercises.html', exercises=exercises)
    except Exception as e:
        return render_template('401.html', error=str(e)), 500


# Route to get logged-in user's routines
@app.route('/user_routines', methods=['GET'])
def get_user_routines():
    try:
        user_id = g.user.id  
        user_routines = UserRoutine.get_user_routines(user_id)
        user_routines_json = [{'id': ur.id, 'exercise_id': ur.exercise_id, 'routine_name': ur.routine_name, 'user_id': ur.user_id} for ur in user_routines]
        return jsonify(user_routines_json), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
