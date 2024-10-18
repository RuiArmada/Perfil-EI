local discordia = require('discordia')
local http = require('http')
local fs = require('fs')
local json = require("dkjson")

function httpGET(url, callback)
    coroutine.wrap(function()
        url = http.parseUrl(url)
        local req = (url.protocol == 'https' and https or http).get(url, function(res)
            local body = {}
            res:on('data', function(s)
                body[#body + 1] = s
            end)
            res:on('end', function()
                res.body = table.concat(body)
                coroutine.wrap(callback)(res)   
            end)
            res:on('error', function(err)
                coroutine.wrap(callback)(res, err)  
            end)
        end)
        req:on('error', function(err)
            coroutine.wrap(callback)(nil, err)   
        end)
    end)()
end

-- Load configuration from JSON file
local function loadConfig()
    local file = fs.readFileSync('config.json')
    local data, pos, err = json.decode(file, 1, nil)
    if err then
        error("Failed to load configuration: " .. err)
    end
    return data
end

local config = loadConfig()

local client = discordia.Client()

client:on('ready', function()
    print('Bot is ready! Setting up handlers...')
    print('WebSocket status:', client.user.status)

    local startTime = os.time()
    local channelId = config.channels.zephyrus  -- Accessing channel ID from the config
    local channel = client:getChannel(channelId)
    if not channel then error("Channel is not accessible with the provided ID.") end

    local msg = channel:send('Ping?')
    discordia.Clock():waitFor('', 3000)
    local endTime = os.time()
    local latency = (endTime - startTime) * 1000
    msg:delete()

    print('Measured Latency:', latency..'ms')

    httpGET('https://api.ipify.org', function(res, err)
        if err then
            print('Error:', err)
        else
            local publicIp = (res.body)
            local timestamp = os.time() * 1000
            local jsonMessage = json.encode({
                latency = string.format("%.2f", latency),
                public_ip = publicIp,
                hostname = 'zephyrus',
                lang = 'luvit',
                timestamp = timestamp
            })

            print('Formatted JSON message:', jsonMessage)
            channel:send('```json\n'..jsonMessage..'\n```')
            print('Message sent successfully to channel ID:', channel.id)
            client:stop()  -- Shutdown the bot after sending the message
        end
    end)
end)

local token = config.credentials.discord  -- Accessing token from the config
client:run('Bot ' .. token)
