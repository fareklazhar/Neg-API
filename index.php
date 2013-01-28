<?php
header("Content-Type: application/json; charset=utf-8");
$cmd = "cd cgi-bin;";
$request = array("train_type" => $_GET["train_type"], "output_type" => $_GET["output_type"], "sentence" => $_GET["sentence"], "src" => $_GET["src"]);
foreach ($request as $key => $val){
  if ($val == "")
    $request[$key] = "NO_REQUEST";
}
$cmd .= '/usr/local/bin/python2.7 identifyNegation.py '. $request["train_type"] . " " . $request["output_type"] . " " . $request["src"] . " " . $request["sentence"] . ";";
$result = shell_exec($cmd);
$_result = explode("**********", $result)[1];
print ($_result);
