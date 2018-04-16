from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import logging


app = Flask(__name__)
handler = logging.getLogger('werkzeug')
app.logger.addHandler(handler)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@127.0.0.1:3306/smartwasher'
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
        self.isFree = False


def construct_test_building(name):
    floors = Floor()
    floors.addRoom(1, Room("Washing Room"))
    floors.addRoom(3, Room("Washing Room"))
    floors.addRoom(6, Room("Washing Room"))
    floors.addRoom(9, Room("Washing Room"))
    floors.addRoom(12, Room("Washing Room"))
    return Building(name, floors)


w3 = construct_test_building("W3")
w4 = construct_test_building("W4")
w6 = construct_test_building("W6")

buildings = {
    w3.name.lower(): w3,
    w4.name.lower(): w4,
    w6.name.lower(): w6,
}

# Create the DB and API based on the database objects.
db.create_all()
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
