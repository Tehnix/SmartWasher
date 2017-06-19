from flask import render_template, jsonify, request
from werkzeug.exceptions import BadRequest
import time
from sqlalchemy import desc
import json

from app import app, db, buildings, AudioData
from predict import fit_model, predict_current_state_of_room

clf = fit_model()


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
        for floorNumber, floor in building.floors.floors.items():
            for room in floor:
                try:
                    prediction = predict_current_state_of_room(
                        clf,
                        building.name,
                        floorNumber,
                        room.name
                    )
                    app.logger.debug(prediction)
                    if 'Not Running' in prediction:
                        room.isFree = True
                    else:
                        room.isFree = False
                    room.isDisabled = False
                except ValueError:
                    room.isDisabled = True
    else:
        building = None
    return render_template(
        'building.html',
        avoidCache=avoidCache,
        buildings=buildings,
        building=building
    )


@app.route('/machine/<string:building>/<int:floor>/<string:room>')
def machine(building, floor, room):
    """Site showing the data of a specific machine."""
    avoidCache = str(int(time.time() * 100000))
    audioSamples = AudioData.query.filter(
        AudioData.processedValue.isnot(None),
        AudioData.building == building,
        AudioData.floor == floor,
        AudioData.room == room,
    ).order_by(desc(AudioData.id)).limit(1000).all()
    samples = []
    times = []
    for sample in audioSamples:
        samples.append(sample.processedValue)
        times.append(sample.id)
    return render_template(
        'machine.html',
        avoidCache=avoidCache,
        building=building,
        floor=floor,
        room=room,
        xJsonData=json.dumps(times),
        yJsonData=json.dumps(samples)
    )


@app.route('/api/data/audio', methods=['POST'])
def apiDataAudio():
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
