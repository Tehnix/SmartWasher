import random

from app import db, AudioDataOriginal


def process_original_data():
    """
    Go through all the samples and find the highest value in each batch. We
    then update the `processedValue` of this record to indicate that it's the
    one we want to use.

    All batches have the same `datetime` value in the database. That said, the
    time actually is indicative of the time the data was received, meaning close
    to the time of the last sample. Each sample is then $10 ms * n$ older, where
    n is $the_newest_sample_id - the_old_sample_id$.

    """
    audioSamples = AudioDataOriginal.query.filter().all()

    currentSampleDatetime = None
    maxValueRecord = None
    for sample in audioSamples:
        if currentSampleDatetime is None:
            currentSampleDatetime = sample.datetime
        if maxValueRecord is None:
            maxValueRecord = sample
        # Check if we've reached a new sample batch.
        if currentSampleDatetime != sample.datetime:
            # If we reach a new sample batch, update the `processedValue` of the
            # record held in `maxValueRecord` to be the `audio` value.
            maxValueRecord.processedValue = maxValueRecord.audio
            # Update to the first value of the new sample batch.
            currentSampleDatetime = sample.datetime
            maxValueRecord = sample
        elif sample.audio > maxValueRecord.audio:
            # If not, then check if the value is higher than the current one
            # and overwrite if so.
            maxValueRecord = sample
    # Update the last record, since this won't be caught in the if statement
    # inside the loop (it compares the current.datetime vs a new.datetime after
    # all).
    maxValueRecord.processedValue = maxValueRecord.audio
    db.session.commit()


def create_noise_data_from_original():
    """
    Since we only have a small data set for "not washing", we create a data set
    to indicate the state of "not washing". This is done by taking the original
    data between the `datetime` (including):
    - '2017-06-14 07:26:24'
    - '2017-06-14 07:27:54'

    We then use this data, pick a random element for it, and assign it to the
    original data `noiseValue`.

    """
    # Get the noise values we'll choose from.
    noiseValues = AudioDataOriginal.query.filter(
        AudioDataOriginal.datetime >= '2017-06-14 07:26:24',
        AudioDataOriginal.datetime <= '2017-06-14 07:27:54',
    ).all()
    # Add a noise value to each record with a `processedValue`, as these are the
    # only ones used in the model generation later on.
    audioSamples = AudioDataOriginal.query.filter(
        AudioDataOriginal.datetime > '2017-06-14 07:27:54',
        AudioDataOriginal.processedValue.isnot(None)
    ).all()
    for sample in audioSamples:
        noiseRecord = random.choice(noiseValues)
        sample.noiseValue = noiseRecord.audio
    db.session.commit()
