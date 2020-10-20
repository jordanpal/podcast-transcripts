from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col, sum
from pyspark.sql.types import StringType
import boto3
import io
from pydub import AudioSegment
from pydub.silence import split_on_silence
import speech_recognition as sr
from elasticsearch import Elasticsearch
sc = SparkContext()
spark=SparkSession(sc)

def download_from_s3(key, bucket="podcast-mp3-bucket"):
    s3 = boto3.resource('s3')
    mp3data = io.BytesIO()
    s3.Bucket(bucket).download_fileobj(key, mp3data)
    return mp3data.getvalue()

def convertToWav(audiomp3):
    """Converts mp3 to wav in memory. Must have pydub, ffmpeg installed."""
    mp3Audio = io.BytesIO(audiomp3)
    wavAudio = io.BytesIO()
    audio = AudioSegment.from_mp3(mp3Audio)
    audio = audio.set_channels(1)
    audio = audio.set_frame_rate(16000)
    audio.export(wavAudio, format= "wav")
    return wavAudio.getvalue()

def split_and_recognize(binary):
    """
    Performs automated speech recognition on input WAV audio bytes.
    Uses CMUSphinx for ASR, see https://cmusphinx.github.io/.
    Requires speech_recognition and pocketsphix python packages.
    Requires swig to be installed. Also possibly libpulse-dev libasound2-dev.
    """
    r = sr.Recognizer()
    bigWav = AudioSegment(binary)
    chunks = split_on_silence(bigWav, min_silence_len = 500, silence_thresh = bigWav.dBFS-14, keep_silence=500)
    whole_text = ""
    num = len(chunks)
    for i, audio_chunk in enumerate(chunks):
        chunk_audio = audio_chunk.export(io.BytesIO(), format="wav")
        chunk_audio.seek(0)
        with sr.AudioFile(chunk_audio) as source:
            audio = r.record(source)
        try:
            text = r.recognize_sphinx(audio)
            whole_text += f"{text} "
        except:
            msg = "<inaudible>"
            whole_text += msg
        chunk_audio.close()
    return whole_text

def download_convert_recognize(key):
    print(f"Downloading {key}...")
    mp3 = download_from_s3(key)
    print("Done. Converting to WAV...")
    wav = convertToWav(mp3)
    print("Done. Transcribing...")
    text = split_and_recognize(wav)
    print(f"Done with {key}!")
    return text

def update_elasticsearch(id, index, text):
    es = Elasticsearch(['10.0.0.6:9200', '10.0.0.14:9200', '10.0.0.10:9200'])
    body = { 'doc': { 'transcription': text } }
    try:
        es.update(index, id, body)
        print(f"Wrote {id} to ES.")
        return 0
    except:
    	print(f"Error writing {id}.")
    	return 1

def s3_transcribe_ES(id, index='podcast_v1'):
    text = download_convert_recognize(id)
    success = update_elasticsearch(id, index, text)
    return success


speech_recognition_udf = udf(lambda z: s3_transcribe_ES(z), StringType())

#Read in podcasts data from Elasticsearch
dfES = spark.read.format('org.elasticsearch.spark.sql')\
    .option('es.nodes', '10.0.0.6:9200, 10.0.0.14:9200, 10.0.0.10:9200')\
    .option('es.resource', "podcast_v1")\
    .option('es.read.metadata', 'true')\
    .load()

#Select podcast episodes that are downloaded but without a transcription yet
dfES = dfES.select(col("_metadata").getItem("_id").alias("id"), col("downloaded"), col("audiourl"), col("transcription"))
dfES = dfES.fillna("null", subset=["transcription"])
todo = dfES.filter(col("transcription") == "null").filter(col("downloaded") == True).select(col("id"))

#Repartition so that each row gets it own partition (STT is embarrasingly parallel)
rows = todo.count()
todo = todo.repartition(rows)

#Transcribe, adding a column denoting whether the operation was a success
transcribed = todo.withColumn("transcription", speech_recognition_udf(col("id")))
transcribed.agg(sum(col("id"))).collect()[0][0]


