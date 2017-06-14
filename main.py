from flask import Flask, render_template, url_for, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from werkzeug.exceptions import BadRequest
import logging


app = Flask(__name__)
handler = logging.getLogger('werkzeug')
app.logger.addHandler(handler)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@127.0.0.1:8889/smartwasher'
db = SQLAlchemy(app)


class AudioData(db.Model):
    """
    The database object that will hold both the raw and processed audio data.
    """
    id = db.Column(db.Integer, primary_key=True)
    audio = db.Column(db.Integer)
    processedValue = db.Column(db.Integer)
    building = db.Column(db.String(255))
    floor = db.Column(db.Integer)
    room = db.Column(db.String(255))
    datetime = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __init__(self, audio, building, floor, room):
        self.audio = audio
        self.processedValue = None
        self.building = building
        self.floor = floor
        self.room = room

    def __repr__(self):
        return '<AudioData data: {0}, processed: {1}, location: {2}/{3} {4}, date: {5}'.format(
            self.audio,
            self.processedValue,
            self.building,
            self.floor,
            self.room,
            self.datetime
        )


class PiezoData(db.Model):
    """
    The database object that will hold both the raw and processed audio data.
    """
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer)
    processedValue = db.Column(db.Integer)
    building = db.Column(db.String(255))
    floor = db.Column(db.Integer)
    room = db.Column(db.String(255))
    datetime = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __init__(self, value, building, floor, room):
        self.value = value
        self.processedValue = None
        self.building = building
        self.floor = floor
        self.room = room

    def __repr__(self):
        return '<AudioData data: {0}, processed: {1}, location: {2}/{3} {4}, date: {5}'.format(
            self.value,
            self.processedValue,
            self.building,
            self.floor,
            self.room,
            self.datetime
        )


@app.route('/')
def index():
    """Site showing the status of the various washing machines."""
    staticCssPath = url_for('static', filename='style.css')
    testValue = "Yes!"
    return render_template(
        'index.html',
        staticCssPath=staticCssPath,
        testValue=testValue
    )


@app.route('/api/data/audio', methods=['POST'])
def ApiDataAudio():
    try:
        jsonData = request.get_json()
    except BadRequest as error:
        errorMessage = {
            'status': 'error',
            'message': 'invalid json',
            'jsonError': str(error)
        }
        app.logger.debug(errorMessage)
        return jsonify(errorMessage)
    missingFields = []
    try:
        building = jsonData['building']
        floor = jsonData['floor']
        room = jsonData['room']
        audioData = jsonData['audioData']
        piezoData = jsonData['piezoData']

        for data in audioData:
            newAudioData = AudioData(
                data,
                building,
                floor,
                room
            )
            db.session.add(newAudioData)
        for data in piezoData:
            newPiezoData = PiezoData(
                data,
                building,
                floor,
                room
            )
            db.session.add(newPiezoData)
        db.session.commit()
    except KeyError as error:
        if 'building' not in jsonData:
            missingFields.append('building')
        if 'floor' not in jsonData:
            missingFields.append('floor')
        if 'room' not in jsonData:
            missingFields.append('room')
        if 'audioData' not in jsonData:
            missingFields.append('audioData')
        if 'piezoData' not in jsonData:
            missingFields.append('piezoData')
        errorMessage = {
            'status': 'error',
            'message': 'missing fields',
            'missingFields': missingFields
        }
        app.logger.debug(errorMessage)
        return jsonify(errorMessage)
    return jsonify({'status': 'ok'})


# Create the DB and API based on the database objects.
db.create_all()
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
