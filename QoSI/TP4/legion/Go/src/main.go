package main

import (
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"os/signal"
	"time"

	"github.com/bwmarrin/discordgo"
	"gopkg.in/yaml.v2"
)

// Config holds all configuration for our Discord bot
type Config struct {
	Channels    map[string]string `yaml:"channels"`
	Credentials struct {
		Discord string `yaml:"discord"`
	} `yaml:"credentials"`
	Guild struct {
		ID string `yaml:"id"`
	} `yaml:"guild"`
}

// NewConfig reads configuration from a YAML file and returns a configuration object and an error
func NewConfig(filename string) (*Config, error) {
	data, err := ioutil.ReadFile(filename)
	if err != nil {
		return nil, err
	}

	var config Config
	err = yaml.Unmarshal(data, &config)
	if err != nil {
		return nil, err
	}

	return &config, nil
}

func main() {
	config, err := NewConfig("config.yaml")
	if err != nil {
		fmt.Printf("Failed to load configuration: %v\n", err)
		return
	}

	dg, err := discordgo.New("Bot " + config.Credentials.Discord)
	if err != nil {
		fmt.Printf("Error creating Discord session: %v\n", err)
		return
	}

	dg.AddHandler(func(s *discordgo.Session, r *discordgo.Ready) {
		fmt.Println("Bot is ready. Setting up handlers...")
		go readyHandler(s, config)
	})

	err = dg.Open()
	if err != nil {
		fmt.Printf("Error opening connection to Discord: %v\n", err)
		return
	}
	defer dg.Close()

	fmt.Println("Bot is now running. Press CTRL-C to exit.")

	stop := make(chan os.Signal, 1)
	signal.Notify(stop, os.Interrupt)
	<-stop

	fmt.Println("Bot is shutting down.")
}

func readyHandler(s *discordgo.Session, config *Config) {
	publicIP := getPublicIP()
	fmt.Printf("Resolved public IP: %s\n", publicIP)

	hostname := "zephyrus"
	fmt.Printf("Resolved hostname: %s\n", hostname)

	latency := s.HeartbeatLatency().Seconds() * 1000
	fmt.Printf("Resolved latency: %fms\n", latency)

	timestamp := time.Now().Unix()
	jsonMessage := fmt.Sprintf("{\"latency\": %f, \"public_ip\": \"%s\", \"hostname\": \"%s\", \"lang\": \"go\", \"timestamp\": %d}", latency, publicIP, hostname, timestamp)
	fmt.Println("Formatted JSON message:", jsonMessage)

	channelID, exists := config.Channels[hostname]
	if exists {
		fmt.Printf("Attempting to send a message to channel ID %s\n", channelID)
		_, err := s.ChannelMessageSend(channelID, fmt.Sprintf("```json\n%s\n```", jsonMessage))
		if err != nil {
			fmt.Printf("Failed to send message to channel %s: %v\n", channelID, err)
		} else {
			fmt.Println("Message sent successfully.")
		}
	} else {
		fmt.Printf("No channel configured for hostname: %s\n", hostname)
	}

	// Command to close the session and exit the program
	s.Close()
	os.Exit(0) // Exit after sending the message
}

func getPublicIP() string {
	resp, err := http.Get("https://api.ipify.org")
	if err != nil {
		fmt.Printf("Failed to get public IP: %v\n", err)
		return "Error"
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		fmt.Printf("Failed to read response body: %v\n", err)
		return "Error"
	}
	return string(body)
}
