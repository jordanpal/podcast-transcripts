# podcast-transcipts
This project transcribes podcast audio and indexes it for search.

It is designed to run on cloud resources, and therefore requires some cluster setup.

# Cluster setup
The spark cluster workers should need some packages installed. The following should be run on each node:
sudo apt install ffmpeg
sudo apt install swig
sudo apt install libpulse-dev libasound2-dev
sudo apt install python3-pip
pip3 install pydub
pip3 install SpeechRecognition
pip3 install pocketsphinx
pip3 install boto3
pip3 install requests

# Ingestion
Podcast data is ingested via logstash, using the rss plugin.
The ruby gem for that plugin was edited to parse certain fields that used in podcasts, but are not mandatory RSS fields.
A python script (logstash-config.py) to create the logstash configuration is included. It accepts a list.txt which should be a file with one podcast rss url per line and returns logstash-podcast.conf
Logstash should be started by running bin/logstash -f logstash-podcast.conf

# Processing
Once podcast feed data is ingested into elasticsearch with logstash, there are spark applications to download the actual audio to s3 and do transcription.
download_mp3.py will load the podcast index from elasticsearch, then for each mp3 url will download the data into an s3 bucket.
mp3_stt.py will load the mp3s from s3, perform speech recognition, and index the text back into elasticsearch.

# Visualization
Finally, with transcripts availabe in elasticsearch, we can use Kibana to inspect some of the results.
If Kibana is installed, it can be started with sudo systemctl start kibana.service
