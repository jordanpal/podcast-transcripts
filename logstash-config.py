import sys
import inspect

podcast_list = sys.argv[1]

top = """#Logstash config for RSS

input {"""

bot = """
}

filter {

}

output {
 elasticsearch {
  index => "podcast"
  action => "create"
  hosts => ["10.0.0.6:9200", "10.0.0.10:9200", "10.0.0.14:9200"]
  workers => 2
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
