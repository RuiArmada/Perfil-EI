const { Client, GatewayIntentBits } = require('discord.js');
const axios = require('axios');
const yaml = require('yaml');
const fs = require('fs');

function loadConfig() {
    try {
        const file = fs.readFileSync('config.yaml', 'utf8');
        return yaml.parse(file);
    } catch (error) {
        console.error('Failed to load configuration:', error);
        process.exit(1);
    }
}

const config = loadConfig();

const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent
    ]
});

client.once('ready', async () => {
    console.log('Bot is ready! Setting up handlers...');
    console.log('Checking WebSocket status:', client.ws.status);

    await new Promise(resolve => setTimeout(resolve, 10000)); // Wait to ensure stability

    try {
        const publicIpResponse = await axios.get('https://api.ipify.org');
        const publicIp = publicIpResponse.data;
        console.log('Public IP resolved:', publicIp);

        const startTime = Date.now();
        const channel = client.channels.cache.get("1233511513025679453") || await client.channels.fetch("1233511513025679453");

        if (!channel) throw new Error("Channel is not accessible with the provided ID.");

        const msg = await channel.send('Ping?');
        const latency = Date.now() - startTime;
        await msg.delete();
        console.log(`Measured Latency: ${latency}ms`);

        const timestamp = Date.now(); // Unix timestamp in milliseconds
        const jsonMessage = `{"latency": ${latency}, "public_ip": "${publicIp}", "hostname": "zephyrus", "lang": "nodejs", "timestamp": ${timestamp}}`;
        console.log('Formatted JSON message:', jsonMessage);

        await channel.send(`\`\`\`json\n${jsonMessage}\n\`\`\``);
        console.log('Message sent successfully to channel ID:', channel.id);

        // Exit the process after the message is sent
        process.exit(0);
    } catch (error) {
        console.error('Error during operations:', error);
        process.exit(1); // Exit with error code 1 if there's an issue
    }
});

client.login(config.credentials.discord);
