from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col, regexp_replace
from pyspark.sql.types import BooleanType
sc = SparkContext()
spark=SparkSession(sc)

def download_to_s3(url, key):
    import requests
    import boto3
    bucket = "podcast-mp3-bucket"
    try:
    	s3 = boto3.resource('s3')
    	mp3data = requests.get(url).content
    	s3Object = s3.Object(bucket,key)
    	s3Object.put(Body=mp3data)
    	#success
    	return True
    except:
    	#error
    	return False

url_to_s3_udf = udf(lambda x,z: download_to_s3(x,z), BooleanType())

#Get all podcast episodes in Elasticsearch
dfES = spark.read.format('org.elasticsearch.spark.sql')\
    .option('es.nodes', '10.0.0.6:9200, 10.0.0.14:9200, 10.0.0.10:9200')\
    .option('es.resource', "podcast_v1")\
    .option('es.read.metadata', 'true')\
    .load()

dfES = dfES.select(col("_metadata").getItem("_id").alias("idES"), col("downloaded"), col("audiourl"))

#Get list of MP3 files in S3
dfS3 = spark.read.format("binaryFile")\
    .option("pathGlobFilter", "*")\
    .load("s3a://podcast-mp3-bucket/")\
    .drop("content")\
    .withColumn("idS3", regexp_replace(col("path"), "s3a://podcast-mp3-bucket/", ""))

#Figure out which ones need to be downloaded
downloaded = dfES.join(dfS3, dfES.idES == dfS3.idS3, how='left')
need_to_download = downloaded.filter(col("idS3").isNull())
need_to_download = need_to_download.na.drop(subset=["audiourl"])

#Do the download!
new_downloads = new_downloads.repartition(20)
new_downloads = need_to_download.withColumn("downloaded", url_to_s3_udf(col("audiourl"), col("idES")))

#Update Elasticsearch
new_downloads.select(col("downloaded"),col("idES").alias("_id")).write.format('org.elasticsearch.spark.sql')\
        .option('es.nodes', '10.0.0.6:9200, 10.0.0.14:9200, 10.0.0.10:9200')\
        .option('es.port', 9200)\
        .option('es.mapping.id', "_id")\
        .option("es.mapping.exclude", "_id")\
        .option("es.write.operation", "update")\
        .mode("append")\
        .option('es.resource', "podcast_v1")\
        .save()