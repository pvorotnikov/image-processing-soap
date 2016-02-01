<?php
require_once('lib/nusoap.php');

// set default timezone
date_default_timezone_set('Europe/Sofia');

function classifyImage($image) {
    $command = escapeshellcmd('python /var/www/soap/classificator/classify.py /var/www/soap/tmp/query-city.jpg');
    $output = shell_exec($command);
    return $output;
}

// create soap server
$server = new soap_server();

// configure wisdl
$server->configureWSDL("image", "urn:image");

$server->register("classifyImage",
    array("image" => "xsd:string"),
    array("return" => "xsd:string"),
        "urn:image",
        "urn:image#classifyImage",
        "rpc",
        "encoded",
        "Classify image in a category");

$server->service($HTTP_RAW_POST_DATA);
