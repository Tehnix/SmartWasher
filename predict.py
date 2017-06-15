import numpy as np
from sklearn.svm import SVC
import random
from sqlalchemy import desc

from main import AudioDataOriginal, AudioData

groupSize = 200


def fit_model():
    """
    Divide each training set into groups of 200 samples, which is approximately
    5 minutes worth of sampling (more or less). This will allow us to predict
    every 5 minutes.

    """
    # We limit the samples to 2400, which is divisible by our grouping size of
    # 200.
    audioSamples = AudioDataOriginal.query.filter(
        AudioDataOriginal.datetime > '2017-06-14 07:27:54',
        AudioDataOriginal.processedValue.isnot(None)
    ).limit(2400).all()
    # Start grouping the data.
    trainingData = []
    targets = []
    audioList = []
    noiseList = []
    groupSizeCounter = 0
    for sample in audioSamples:
        if groupSizeCounter == groupSize:
            trainingData.append(np.array(audioList))
            targets.append("Running")
            trainingData.append(np.array(noiseList))
            targets.append("Not Running")
            audioList = []
            noiseList = []
        audioList.append(sample.processedValue)
        noiseList.append(sample.noiseValue)
        groupSizeCounter += 1

    # Convert our data into numpy arrays.
    trainingData = np.array(trainingData)
    targets = np.array(targets)

    # Train our model.
    clf = SVC()
    clf.fit(trainingData, targets)
    return clf


def predict_state(clf, samples):
    """
    Predict the data based on the supplied classification model and sample size.

    """
    # Reshape our sample data
    try:
        samples = np.array(samples[:groupSize]).reshape(1, -1)
    except Exception as error:
        print(error)
        print(
            "Sample size was too short! Must contain n = {0} samples.".format(
                groupSize)
        )
        return None
    return clf.predict(samples)


def test_prediction_against_original():
    """Test our model against the original data."""
    clf = fit_model()
    audioSamplesRunning = AudioDataOriginal.query.filter(
        AudioDataOriginal.datetime > '2017-06-14 07:29:54',
        AudioDataOriginal.processedValue.isnot(None)
    ).limit(groupSize).all()
    audioSamplesNotRunning = AudioDataOriginal.query.filter(
        AudioDataOriginal.datetime > '2017-06-14 08:36:58',
        AudioDataOriginal.processedValue.isnot(None)
    ).limit(groupSize).all()

    noiseValues = [-1, 0, 1]

    # Test if we get classified as running, after adding noise.
    samples = []
    for sample in audioSamplesRunning:
        # Add some noise to the sample to test the strength of the model.
        noise = random.choice(noiseValues)
        newSampleValue = sample.audio + noise
        if newSampleValue < 0:
            newSampleValue = 0
        samples.append(newSampleValue)
    predictionRunning = predict_state(clf, samples)

    # Test if we get classified as running, after adding noise.
    samples = []
    for sample in audioSamplesNotRunning:
        # Add some noise to the sample to test the strength of the model.
        noise = random.choice(noiseValues)
        newSampleValue = sample.audio + noise
        if newSampleValue < 0:
            newSampleValue = 0
        samples.append(newSampleValue)
    predictionNotRunning = predict_state(clf, samples)

    print(predictionRunning)
    print(predictionNotRunning)


def predict_current_state(clf):
    """Predict the state of the current sampels."""
    audioSamples = AudioData.query.filter(
        AudioData.processedValue.isnot(None)
    ).order_by(desc(AudioData.id)).limit(200).all()
    samples = []
    for sample in audioSamples:
        samples.append(sample.processedValue)
    return clf.predict(samples)
