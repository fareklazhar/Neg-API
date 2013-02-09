<?php
header("Content-Type: application/json; charset=utf-8");

function e( $s ){
  $s = str_replace("\"", "", $s);
  return escapeshellarg($s);
}

$cmd = "cd cgi-bin;";
$request = array("train_type" => e($_GET["train_type"]), "output_type" => e($_GET["output_type"]), "sentence" => e($_GET["sentence"]), "src" => e($_GET["src"]));
foreach ($request as $key => $val){
  if ($val == "''")
    $request[$key] = "NO_REQUEST";
}
$cmd .= '/usr/local/bin/python2.7 identifyNegation.py '. $request["train_type"] . " " . $request["output_type"] . " " . $request["src"] . " " . $request["sentence"] . ";";
$result = shell_exec($cmd);
$_result = explode("**********", $result)[1];
print ($_result);
//var_dump($request);
//print ($result);
