<?php
require_once('lib/nusoap.php');

// set default timezone
date_default_timezone_set('Europe/Sofia');

function classifyImage($image) {

    file_put_contents('tmp/img', base64_decode($image));

    $command = escapeshellcmd('python /var/www/soap/classificator/classify.py /var/www/soap/tmp/img');
    $output = shell_exec($command);
    return $output;
}

function getSobel($image) {

    file_put_contents('tmp/img', base64_decode($image));

    $command = escapeshellcmd('python /var/www/soap/sobel/sobel.py /var/www/soap/tmp/img');
    $output = shell_exec($command);
    return $output;
}

// create soap server
$server = new soap_server();

// configure wisdl
$server->configureWSDL("image", "urn:image");

// register classify image method
$server->register("classifyImage",
    array("image" => "xsd:string"),
    array("return" => "xsd:string"),
        "urn:image",
        "urn:image#classifyImage",
        "rpc",
        "encoded",
        "Classify image in a category");

// register get sobel method
$server->register("getSobel",
    array("image" => "xsd:string"),
    array("return" => "xsd:string"),
        "urn:image",
        "urn:image#getSobel",
        "rpc",
        "encoded",
        "Get the Sobel edge detection image");

$server->service($HTTP_RAW_POST_DATA);
