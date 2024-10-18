<?php
require 'vendor/autoload.php';

use Discord\Discord;
use Discord\Parts\Channel\Message;
use Discord\WebSockets\Event;
use GuzzleHttp\Client;

// Create a new Discord instance with your bot's token
$discord = new Discord([
    'token' => 'YOUR_BOT_TOKEN' // Replace 'YOUR_BOT_TOKEN' with your actual Discord bot token
]);

$discord->on('ready', function (Discord $discord) {
    echo "Bot is ready!", PHP_EOL;

    // Retrieve a channel by its ID and send a message
    $channel = $discord->getChannel('id'); // Replace with your channel ID
    if (!$channel) {
        echo "Channel not found or inaccessible with the provided ID.", PHP_EOL;
        return;
    }

    $channel->sendMessage('Ping?')->then(function (Message $message) use ($discord, $channel) {
        $startTime = microtime(true);

        // Delay to simulate ping and then edit the message with latency
        $discord->getLoop()->addTimer(3, function () use ($message, $startTime, $channel) {
            $endTime = microtime(true);
            $latency = ($endTime - $startTime) * 1000;

            // Delete the initial message
            $message->delete();

            // Get public IP using GuzzleHttp and send a JSON message
            $client = new Client();
            $response = $client->request('GET', 'https://api.ipify.org');
            $publicIp = $response->getBody();

            $timestamp = round(microtime(true) * 1000);
            $jsonMessage = json_encode([
                'latency' => number_format($latency, 2, '.', ''),
                'public_ip' => (string)$publicIp,
                'hostname' => 'zephyrus',
                'lang' => 'php',
                'timestamp' => $timestamp
            ]);

            // Send the formatted JSON message
            $channel->sendMessage("```json\n$jsonMessage\n```");
            echo "Message sent successfully to channel ID: {$channel->id}", PHP_EOL;
        });
    });
});

$discord->run();
