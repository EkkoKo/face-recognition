import face_recognition
from flask import Flask, jsonify, request
import numpy as np
import os.path

DB_NAME = "db.json"

app = Flask(__name__)


def add_face_encoding(face_encoding, name):
    if not os.path.isfile(DB_NAME):
        db = {"face_encodings": [], "names": []}
    else:
        with open(DB_NAME, 'r') as f:
            db = json.load(f)
    db['face_encodings'].append(face_encoding.tolist())
    db['names'].append(name)
    with open(DB_NAME, 'w') as f:
        json.dump(db, f)


def get_db():
    if not os.path.isfile(DB_NAME):
        return [], []

    with open(DB_NAME, 'r') as f:
        db = json.load(f)
    known_face_encodings = db['face_encodings']
    known_face_names = db['names']
    return known_face_encodings, known_face_names


def add_face(file_stream, name):
    image = face_recognition.load_image_file(file_stream)
    face_encoding = face_recognition.face_encodings(image)[0]
    add_face_encoding(face_encoding, name)
    return name + " has been added to db!"


def detect_faces_in_image(file_stream):
    image = face_recognition.load_image_file(file_stream)

    known_face_encodings, known_face_names = get_db()

    face_locations = face_recognition.face_locations(image)
    face_encodings = face_recognition.face_encodings(image, face_locations)
    faces_found = []

    # Loop through each face found in the unknown image
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # See if the face is a match for the known face(s)
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

        name = "Unknown"

        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        if len(face_distances) > 0:
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]
        faces_found.append({"name": name, "location": [top, right, bottom, left]})
    return faces_found


@app.route('/add_face', methods=['POST'])
def add_face_route():
    if 'image' not in request.files:
        return "Please add 'image' to files", 400
    try:
        image = request.files['image']
    except:
        return "ERROR In Loading Image", 500
    if 'json' not in request.files:
        return "Please add 'json' with name to files", 400
    name = json.load(request.files['json'])['name']
    try:
        add_face_result = add_face(image, name)
    except:
        return "ERROR In Adding Face", 500
    return add_face_result, 200


@app.route('/detect_faces', methods=['GET', 'POST'])
def detect_faces_route():
    app.logger.info(str(request.files))
    if 'image' not in request.files:
        return "Please add 'image' to files", 400
    try:
        image = request.files['image']
    except:
        return "ERROR In Loading Image", 500
    try:
        result = detect_faces_in_image(image)

    except:
        return "ERROR In Detecting Faces", 500
    return jsonify(result), 200

@app.route('/health_check', methods=['GET', 'POST'])
def health_check():
    return "OK", 200

@app.route('/flush_db', methods=['GET', 'POST'])
def flush_db():
    db = {"face_encodings": [], "names": []}
    with open(DB_NAME, 'w') as f:
        json.dump(db, f)
    return "DB Was Flushed!", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
