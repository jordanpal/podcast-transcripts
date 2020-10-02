import feedparser
import urllib.request
from pyspark.sql.functions import udf
from pyspark.sql.types import BooleanType

with open(rssList, 'r') as f:



def download_to_s3(url, bucket, key):
	import requests
	import boto3
	try
		s3 = boto3.resource('s3')
		mp3data = requests.get(url).content
		s3Object = s3.Object(bucket,key)
		s3Object.put(Body=mp3data)
		#success
		return 0
	except:
		#error
		return 1

url_to_s3_udf = udf(lambda x,y,z: download_to_s3(x,y,z), IntegerType())

def parse_rss()
	import feedparser


parsed_RSS = DATAFRAME
df.read(ES-PODCAST-INDEX)

df_new = select episodes not in df

df_new.download_to_s3()

