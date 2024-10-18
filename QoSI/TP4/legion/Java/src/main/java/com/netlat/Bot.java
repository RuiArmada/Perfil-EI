package com.netlat;

import net.dv8tion.jda.api.*;
import net.dv8tion.jda.api.entities.channel.concrete.TextChannel;
import net.dv8tion.jda.api.events.session.ReadyEvent;
import net.dv8tion.jda.api.hooks.ListenerAdapter;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;

import javax.security.auth.login.LoginException;

import java.io.FileNotFoundException;
import java.io.IOException;

public class Bot extends ListenerAdapter {
    private JDA jda;
    private Config config;

    public Bot(String configFile) throws LoginException, FileNotFoundException {
        config = new Config(configFile);
        jda = JDABuilder.createDefault(config.getDiscordToken())
                .addEventListeners(this)
                .build();
    }

    @Override
    public void onReady(ReadyEvent event) {

        String publicIp = fetchPublicIP();
        long timestamp = System.currentTimeMillis(); // Getting the current Unix timestamp

        // Constructing the JSON message with additional 'lang' field and 'timestamp'
        String jsonMessage = String.format(
                "{\"latency\": %d, \"public_ip\": \"%s\", \"hostname\": \"%s\", \"lang\": \"java\", \"timestamp\": %d}",
                jda.getGatewayPing(), publicIp, getHostName(), timestamp);

        // Assuming the hostname maps directly to channel keys in the configuration
        Long channelId = config.getChannels().get("zephyrus");
        // we need to change the key because hostname may be null
        // Long channelId = config.getChannels().get(getHostName());
        System.out.println("Sending message to channel ID: " + channelId);
        if (channelId != null) {
            TextChannel channel = jda.getTextChannelById(channelId);
            if (channel != null) {
                channel.sendMessage(String.format("```json\n%s\n```", jsonMessage)).queue();
            } else {
                System.out.println("Channel not found for ID: " + channelId);
            }
        } else {
            System.out.println("No channel configured for hostname: " + getHostName());
        }
    }

    private String fetchPublicIP() {
        OkHttpClient client = new OkHttpClient();
        Request request = new Request.Builder()
                .url("https://api.ipify.org")
                .build();
        try (Response response = client.newCall(request).execute()) {
            return response.body().string();
        } catch (IOException e) {
            System.out.println("Failed to fetch public IP: " + e.getMessage());
            return "Error";
        }
    }

    private String getHostName() {
        // Tries to fetch Windows environment variable first, then Unix/Linux.
        return System.getenv("COMPUTERNAME") != null ? System.getenv("COMPUTERNAME") : System.getenv("HOSTNAME");
    }

    public static void main(String[] args) {
        if (args.length < 1) {
            System.out.println("Usage: java -jar discord-bot.jar <configFilePath>");
            return;
        }
        String configFilePath = args[0];
        try {
            new Bot(configFilePath);
        } catch (LoginException | FileNotFoundException e) {
            System.out.println("Failed to start the Discord bot: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
