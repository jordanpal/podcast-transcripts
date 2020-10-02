from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col, concat_ws, collect_list
from pyspark.sql.functions import explode
from pyspark.sql.types import StringType, BinaryType, ArrayType
sc = SparkContext()
spark=SparkSession(sc)

def convertToWav(audiomp3):
    import io
    from pydub import AudioSegment
    mp3Audio = io.BytesIO(audiomp3)
    wavAudio = io.BytesIO()
    audio = AudioSegment.from_mp3(mp3Audio)
    audio = audio.set_channels(1)
    audio = audio.set_frame_rate(16000)
    audio.export(wavAudio, format= "wav")
    return wavAudio.getvalue()

def splitWav(bigWav, sec=30):
    import io
    from pydub import AudioSegment
    from pydub.utils import make_chunks
    big = io.BytesIO(bigWav)
    chunk_length_ms = sec*1000
    chunks = make_chunks(AudioSegment(bigWav), chunk_length_ms)
    output = [chunk.export(io.BytesIO(), format="wav") for chunk in chunks]
    return [x.getvalue() for x in output]

def recognize(binary):
    import speech_recognition as sr
    import io
    s = io.BytesIO(binary)
    r = sr.Recognizer()
    with sr.AudioFile(s) as source:
        audio = r.record(source)
    try:
        print("Transcribing...")
        text = r.recognize_sphinx(audio)
        print("Done!")
        return text
    except:
        msg = "no_transcription_available"
        print("Darn! Could not transcribe audio.")
        return msg

sttudf = udf(lambda z:recognize(z), StringType())
splitudf = udf(lambda x: splitWav(x), ArrayType(BinaryType()))
convertudf = udf(lambda x: convertToWav(x), BinaryType())

df = spark.read.format("binaryFile").option("pathGlobFilter", "DTNS*.mp3").option("recursiveFileLookup", "true").load("s3a://jordan-podcast-s3/")
df = df.withColumn("WAVAudio", convertudf(df.content)).drop("modificationTime","length","content")
df = df.withColumn("splitwavs", splitudf(df.WAVAudio)).drop("WAVAudio")
df = df.withColumn("splitwavs", explode(df.splitwavs))
df = df.repartition(36)
df = df.withColumn("transcriptions", sttudf(df.splitwavs)).drop("splitwavs")
df = df.groupby("path").agg(collect_list('transcriptions').alias("transcriptions"))
df = df.withColumn("transcriptions", concat_ws(" ", "transcriptions"))
df.write.format('org.elasticsearch.spark.sql')\
        .option('es.nodes', '10.0.0.6:9200, 10.0.0.14:9200, 10.0.0.10:9200')\
        .option('es.port', 9200)\
        .option('es.resource', "podcast2/test")\
        .save()