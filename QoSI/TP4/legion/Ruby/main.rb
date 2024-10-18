require 'discordrb'
require 'yaml'
require 'net/http'
require 'uri'
require 'json'

# Load configuration from config.yaml
config = YAML.load_file('config.yaml')

bot = Discordrb::Bot.new token: config['credentials']['discord']

bot.ready do |event|
  puts 'Bot is ready! Setting up handlers...'
  puts "WebSocket status: #{bot.profile.status}"

  channel_id = config['channels']['zephyrus']
  channel = bot.channel(channel_id)
  unless channel
    puts 'Channel is not accessible with the provided ID.'
    bot.stop
  else
    startTime = Time.now.to_i

    # Send a ping message
    msg = channel.send_message('Ping?')
    sleep(1)  # Give some time for message delivery
    endTime = Time.now.to_i
    latency = (endTime - startTime) * 1000

    # Delete the ping message
    msg.delete

    puts "Measured Latency: #{latency}ms"

    uri = URI('https://api.ipify.org')
    response = Net::HTTP.get_response(uri)
    if response.is_a?(Net::HTTPSuccess)
      public_ip = response.body
      timestamp = Time.now.to_i * 1000
      json_message = {
        latency: format('%.2f', latency),
        public_ip: public_ip,
        hostname: 'zephyrus',
        lang: 'ruby',
        timestamp: timestamp
      }.to_json

      puts "Formatted JSON message: #{json_message}"
      # Send the detailed information message
      channel.send_message("```json\n#{json_message}\n```")
      puts "Message sent successfully to channel ID: #{channel.id}"

      # Stop the bot after sending the message
      bot.stop
    else
      puts "Error fetching public IP: #{response.code} #{response.message}"
      # Stop the bot if there is an error fetching the IP
      bot.stop
    end
  end
end

begin
  bot.run
rescue OpenSSL::SSL::SSLError => ssl_error
  puts "SSL Error occurred: #{ssl_error.message}"
  puts "Attempting to reconnect..."
  sleep(5)  # Wait 5 seconds before attempting to reconnect
  retry
rescue StandardError => e
  puts "An error occurred: #{e.message}"
ensure
  bot.stop
end
