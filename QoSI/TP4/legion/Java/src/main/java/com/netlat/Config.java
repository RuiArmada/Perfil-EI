package com.netlat;

import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.InputStream;
import java.util.Map;
import org.yaml.snakeyaml.Yaml;

public class Config {
    private Map<String, Long> channels;
    private String discordToken;
    private Long guildId;

    @SuppressWarnings("unchecked")
    public Config(String filename) throws FileNotFoundException {
        InputStream inputStream = new FileInputStream(filename);
        Yaml yaml = new Yaml();
        Map<String, Object> data = yaml.load(inputStream);
    
        this.channels = (Map<String, Long>) data.get("channels");
        Map<String, String> credentials = (Map<String, String>) data.get("credentials");
        this.discordToken = credentials.get("discord");
        Map<String, Long> guild = (Map<String, Long>) data.get("guild");
        this.guildId = guild.get("id");
    }

    public Map<String, Long> getChannels() {
        return channels;
    }

    public String getDiscordToken() {
        return discordToken;
    }

    public Long getGuildId() {
        return guildId;
    }
}
