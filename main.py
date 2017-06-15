from flask import Flask, render_template, url_for, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from werkzeug.exceptions import BadRequest
import logging
import time


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


class AudioDataOriginal(db.Model):
    """
    The database object that will hold both the raw and processed audio data.
    """
    id = db.Column(db.Integer, primary_key=True)
    audio = db.Column(db.Integer)
    processedValue = db.Column(db.Integer)
    noiseValue = db.Column(db.Integer)
    building = db.Column(db.String(255))
    floor = db.Column(db.Integer)
    room = db.Column(db.String(255))
    datetime = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __init__(self, audio, building, floor, room):
        self.audio = audio
        self.processedValue = None
        self.noiseValue = None
        self.building = building
        self.floor = floor
        self.room = room

    def __repr__(self):
        return '<AudioDataOriginal data: {0}, processed: {1}, noise: {6}, location: {2}/{3} {4}, date: {5}'.format(
            self.audio,
            self.processedValue,
            self.building,
            self.floor,
            self.room,
            self.datetime,
            self.noiseValue
        )


class Building():
    def __init__(self, name, floors):
        self.name = name
        self.floors = floors


class Floor():
    def __init__(self):
        self.floors = {}

    def addRoom(self, floor, room):
        if floor not in self.floors:
            self.floors[floor] = [room]
        else:
            self.floors[floor].append(room)


class Room():
    def __init__(self, name):
        self.name = name


room = Room("Washing Room")
floors = Floor()
floors.addRoom(1, room)
w6 = Building("W6", floors)

buildings = {
    w6.name.lower(): w6
}


@app.route('/')
def index():
    """Site showing the status of the various washing machines."""
    avoidCache = str(int(time.time() * 100000))
    return render_template(
        'index.html',
        avoidCache=avoidCache,
        buildings=buildings
    )


@app.route('/building/<string:building>')
def building(building):
    """Site showing the status of the various washing machines."""
    avoidCache = str(int(time.time() * 100000))
    if building.lower() in buildings:
        building = buildings[building.lower()]
    else:
        building = None
    return render_template(
        'building.html',
        avoidCache=avoidCache,
        buildings=buildings,
        building=building
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

        for data in audioData:
            newAudioData = AudioData(
                data,
                building,
                floor,
                room
            )
            db.session.add(newAudioData)
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
