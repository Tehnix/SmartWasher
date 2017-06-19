import random

from app import db, AudioDataOriginal, AudioData


groupSize = 200


def get_noise_values():
    noiseValues = AudioDataOriginal.query.filter(
        AudioDataOriginal.datetime >= '2017-06-14 07:26:24',
        AudioDataOriginal.datetime <= '2017-06-14 07:27:54',
    ).all()
    return noiseValues


def get_audio_samples():
    audioSamples = AudioDataOriginal.query.filter(
        AudioDataOriginal.datetime > '2017-06-14 07:27:54',
        AudioDataOriginal.processedValue.isnot(None)
    ).limit(2400).all()
    return audioSamples


def add_silent_values(noiseValues):
    """
    Add a group of 200 "not running" samples (what we defined our model to use)
    to the database, so that we can demo the prediction model.

    For this, we can simply rely on the noise values and random insert these.

    """
    for i in range(0, groupSize):
        noiseRecord = random.choice(noiseValues)
        noiseValue = noiseRecord.audio
        newSample = AudioData(
            noiseValue,
            "W6",
            1,
            "Washing Room"
        )
        newSample.processedValue = noiseValue
        newSample.noiseValue = noiseValue
        db.session.add(newSample)
    db.session.commit()


def add_running_values(audioSamples, step):
    """
    Add a group of 200 "running" samples (what we defined our model to use)
    to the database, so that we can demo the prediction model.

    We add noise to each value, and require a step value indicating which stage
    of the "running" phase we are in, starting at 0.

    """
    if (step + 1) * groupSize > 2400:
        print("We've reached the end of the run!")
        return None
    samples = audioSamples[step * groupSize: (step + 1) * groupSize]
    noiseValues = [-1, 0, 1]
    for sample in samples:
        # Add noise to the sample.
        noiseValue = random.choice(noiseValues)
        value = sample.audio + noiseValue
        if value < 0:
            value = 0
        newSample = AudioData(
            value,
            "W6",
            1,
            "Washing Room"
        )
        newSample.processedValue = value
        db.session.add(newSample)
    db.session.commit()
