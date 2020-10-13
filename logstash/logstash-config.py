#!/usr/bin/env python3
#Script for generating logstash configuration file
#-Input: should be a text file with one URL per row (pointing to the RSS feed)
#-Output: logstash-config.conf
#The resulting logstash pipeline will check each RSS feed every 3600 seconds.
#It will create a unique identifier (by hashing guid and published fields),
#add fields named downloaded (false) and transcription (nil), then create
#the documents in elasticsearch. Only new episodes will succeed.
#
#The elasticsearch hostnames are hard coded!

import sys
import inspect

podcast_list = sys.argv[1]

top = """#Logstash config for RSS

input {"""

bot = """
}

filter {
  fingerprint {
    method => "MURMUR3"
    source => ["guid", "published"]
    target => "[@metadata][fingerprint]"
  }
  mutate {
    add_field => { downloaded => false }
  }
  mutate {
    add_field => { transcription => null }
  }
  mutate {
    convert => { downloaded => boolean}
  }
}

output {
 elasticsearch {
  index => "podcast_v1"
  action => "create"
  document_id => "%{[@metadata][fingerprint]}"
  hosts => ["10.0.0.6:9200", "10.0.0.10:9200", "10.0.0.14:9200"]
 }
 stdout { codec => rubydebug }

}
"""

with open(podcast_list, "r") as infile:
	with open("logstash-podcast.conf", "w") as outfile:
		outfile.write(top)
		outfile.write("\n")
		for url in infile:
			url = url.rstrip("\n")
			rss_template =f"""
  rss {{
    url => "{url}"
    interval => 3600
  }}
"""
			outfile.write(rss_template)
		outfile.write(bot)
