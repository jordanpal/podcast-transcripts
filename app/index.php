<?php
require __DIR__ . '/vendor/autoload.php';
use Elasticsearch\ClientBuilder;

$hosts = [
'host' => '10.0.0.6', // or your domain name
'port' => '9200', // or another port
'scheme' => 'http', // or https
];

$client = Elasticsearch\ClientBuilder::create()
                        ->setHosts($hosts)
                        ->build();
if(isset($_GET['q'])) { // (4)

$q = $_GET['q'];

$params = [
        'index' => 'podcast_v1',
        'body' => [
                'query' => [
                        'match' => [
                                'transcription' => $q
                        ],
                ],
        ],
];

$response = $client->search($params);
$hits = count($response['hits']['hits']);
$result = null;
$i = 0;

while ($i < $hits) {
        $result[$i] = $response['hits']['hits'][$i]['_source'];
        $i++;
}
foreach ($result as $key => $value) {
        echo "Title: " . $value['title'] . "<br>";
        echo "Published: " . $value['published'] . "<br>";
        echo "<a href=\"" . $value['audiourl'] . "\">Download mp3</a><br>";
        echo "Transcript: " . $value['transcription'] . "<br>";
        echo "<hr>";
}
}
?>

<!-- HTML STARTS HERE -->
<!DOCTYPE>
<html>
    <head>
        <meta charset="utf-8">
        <title>Transcript Search</title>
        <link rel="stylesheet" href="css/main.css">
    </head>
    <body>
        <H2> Search Podcast Transcripts!</H2>
        <!--<H4> Or, check out Kibana: <a href="http://transcript-podcast.xyz/kibana/">http://transcript-podcast.xyz/kibana/</a></H4>-->
        <form action="index.php" method="get" autocomplete="off">
            <label>
                Enter a search term:
                <input type="text" name="q">
            </label>
            <input type="submit" value="search">
        </form>
<H4>The search box is backed by an Elasticsearch index. You can explore the full data with an example Kibana dashboard below, or check out the full Kibana app here: <a href="http://transcript-podcast.xyz/kibana/">http://transcript-podcast.xyz/kibana/</a>.</H4>
<iframe src="http://transcript-podcast.xyz/kibana/app/dashboards#/view/3e1e8410-0a54-11eb-ac9c-cdc7d5c12984?embed=true&_g=(filters:!(),refreshInterval:(pause:!t,value:0),time:(from:now-10y,to:now))&_a=(description:'',filters:!(),fullScreenMode:!f,options:(hidePanelTitles:!f,useMargins:!t),query:(language:kuery,query:''),timeRestore:!f,title:'Example%20Dashboard',viewMode:view)" height=100% width=100%></iframe>
    </body>
</html>

