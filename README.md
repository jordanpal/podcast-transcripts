# PodText

## Table of Contents
1. [Summary](README.md#summary)
2. [Links](README.md#links)
3. [Setup](README.md#setup)
4. [Data](README.md#data)


## Summary
### Introduction
Podcasting is a popular and growing medium, with over $1B in advertising revenue expected in 2021. However, podcast metadata spread around various sources which makes it difficult to perform analytics for brands interested in advertising in the space. Furthermore, one missing piece of data that could be used for analytics (or by interested consumers or bored data scientists...) is full transcriptions of the episodes. While some authors provide transcripts of their podcasts, it is not common practice, and there is currently no way to quickly search transcripts.

This project aims to index podcast transcripts for search, along with other metadata. In order to make these text documents easy and fast to search, the main design choice was made to use an Elasticsearch index for the podcast data. Other pieces of technology followed from that decision:

* Logstash is used to ingest podcast RSS feeds into Elasticsearch
* Spark is used to process the raw audio files into text
* Speech recognition is done with CMU Sphinx (as a UDF in Spark)
* Audio files are saved in S3
* Kibana is used to visualize the data

### Tech Stack
![tech-stack](https://github.com/jordanpal/podcast-transcripts/blob/main/images/techstack.png)

## Setup
In order to run the scripts the following tools must be setup and connected to each other. In my case, everything was set up on AWS EC2 resources:
* Elasticsearch cluster (mostly default settings suffices)
* Logstash instance with custom RSS plugin installed (can be co-located with ES)
 * The ruby gem in the logstash dir has been edited to ingest podcast data more effectively. One should install the logstash-rss plugin, then update that file with the one here.
 * logstash-config.py is included to create a logstash.conf file for this pipeline. It reads a text file containing a podcast RSS feed URL on each line.
* Apache Spark cluster 
 * Spark workers should have the following installed via package manager and via pip:
  * (apt or similar) ffmpeg, swig, libpulse-dev libasound2-dev, python3-pip
  * (pip) pydub, SpeechRecognition, pocketsphinx, boto3, requests
 * (optional) Airflow can be installed to manage Spark workflow
* Kibana installed for visualizations

Once everything is installed, the Elasticsearch, Logstash, and Kibana services can be started. If logstash was configured properly, it will ingest RSS data and populate an Elasticsearch index with podcast metadata (can be quickly checked in Kibana).

In order to start making transcripts, one can use the spark programs in the data-processing directory. The script download_mp3s.py gets all the episodes from Elasticsearch and downloads an MP3 into S3 for each if it does not yet exist. Then, transcribe_S3_to_ES.py finds all the episodes which have an MP3 but no transcription, and uses CMU Sphinx to transcribe each episode, putting the results back into Elasticsearch.

### Links
* [Slide deck](https://docs.google.com/presentation/d/184ZNp0H7c3CU6LVKQQr50YVztggaJfLRC9j8nk8rgT4/edit?usp=sharing)
* [Live webapp](http://transcript-podcast.xyz/)
* [Elasticsearch](https://www.elastic.co/)
* [CMU Sphinx](https://cmusphinx.github.io/)