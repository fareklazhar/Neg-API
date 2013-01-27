<?php
header("Content-Type: application/json; charset=utf-8");
$cmd = "cd ../../negation/src/python/processing/src/;";
$cmd .= '/usr/local/bin/python2.7 SignalIdentification.py '. $_GET["q"] . ";";
$result = shell_exec($cmd);
$_result = explode("**********", $result)[1];
print ($result);
print ($_result);
//$responseJSON = array("status" => "OK", "negation" => $neg, "result" => $result);
//print ($responseJSON);
