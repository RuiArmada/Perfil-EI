
![Logo](https://mayorx.xyz/Media/disqosi/logo.png)


# NetLat

A network analysis tool created to measure Applicational Latency vs Network Latency in Discord Bots and to verify if the network has any traffic shapping implemented.

The project was guided by the decision to shift focus from a previous study on latency in gaming footage to creating a practical and innovative monitoring tool integrated with Discord. This choice allowed the project to align with real-world applications and the needs of online gaming communities, where performance levels are crucial.

The core functionalities of the system include task management through a dedicated communication channel on Discord, configuration management, and real-time updates facilitated by the main bot. The architecture supports various bots programmed in multiple languages, showcasing adaptability and robustness across different technology stacks. Moreover, a comprehensive testing and development process was undertaken to address challenges such as documentation variability and dependency management.

The final product features a dashboard that provides an interactive interface for data analysis and performance monitoring, helping users visualize data effectively and make informed decisions based on the network conditions observed.

This tool not only meets its intended objectives by providing detailed insights into network behavior and latency patterns but also sets the stage for further enhancements that could include more automated features and advanced data analytics capabilities.
## Functionalities

### Servers
#### `Main` Server
The main server has the following functions

- Receive the packets sent by the `Workers`
- Analyze the packets for time it took to transfer them from the `Worker` to the `Server`
- Analyze packets for changes in `TOS/DiffServ`
- Generate an interactive dashboard to visualize the datasets.

#### `Worker` Server
The main objective of the Worker server is to:

- Capture the `discord.{city}.media.` DNS request in order get the "approximate" nearest server.
- Ping Discord's media server.
- Create packets of different types such as RTP and HTTP and set the `TOS/DiffServ` bits to different values to calculate if the packet was altered mid trip.


### Bots
#### `Server` Bot
The Server bot has two main functions:
- Scrape all the worker channels and create a dataset file.
- Test the API latency of his own.

#### `Main` Bots
The "Main" bots have only two functions as well:
- Create the channel per "Worker" where to store the latency data.
- Get API latency for Python in that Worker.

#### `Worker` Bots (WIP)
The function of the Worker bots is to send the different latencies of each of the other language bots to the Worker Channel.
## Screenshots

![Main Latency Dashboard](https://mayorx.xyz/Media/disqosi/lat-disc-all.png)
*Fig.1 - Discord Latency Dashboard per region.*

![NYC Latency Dashboard](https://mayorx.xyz/Media/disqosi/lat-disc-nyc1.png)
*Fig.2 - Discord Latency Dashboard in New York City*

![DNS Amsterdan Latency Dashboard](https://mayorx.xyz/Media/disqosi/lat-dns-ams3.png)
*Fig.3 - DNS Latency Dashboard from Amsterdan to Braga*

![RTP Toronto Latency Dashboard](https://mayorx.xyz/Media/disqosi/lat-rtp-tor1-tos.png)
*Fig.4 - RTP Latency and `TOS/DiffServ` analisis Dashboard from Toronto to Braga*

## Prerequisites (WIP)

For this project there are some prerequisites required due to the usage of Discord bots, Digital Ocean droplets and Github to test the latencies and network shapping.

### Github

Required: __Github_user_Token (Fine-grain)__


### Digital Ocean

Required: __DigitalOcean__user_token__

### Discord

Required: __Discord_Bot_Tokens__
## Run

Clone the project

```bash
$ git clone https://github.com/MayorX500/disQoSi
```

Go to the project directory

```bash
$ cd disQoSi
```

Create and activate an python enviroment

```bash
$ python3 -m venv enviroment

$ source enviroment/bin/activate
```

Install dependencies
```bash
$ pip install -r requirements.txt
```

### Launch Modes:

#### Command Center
Run the `Main` server

```bash
$ sudo python3 netlat server --interface <interface> -s
```

Run the `Main` Discord Bot
```bash
$ sudo python3 netlat bot -b -r server
```

Launch `Legion` of bots (*wip)
```bash
$ python3 legion
```

#### Workers
##### Worker Automatic Lauch
By default if you use the flag `-s` (worker spawn) in the `Main` server all workers must be initialized correctly.

##### Worker Manual Launch
Run program in worker mode:
```bash
$ sudo python3 netlat worker --interface <interface>
```
Run bot in worker mode:
```bash
$ sudo python3 netlat bot -b -r main
```
Run legion of bots:
```bash
$ python3 legion
```

#### Dashboard
To run the dashboard

```bash
$ python3 dashboard_app
```
## Authors

- [@Carlos Gomes](https://github.com/cgomes-pt)
- [@Miguel Gomes](https://github.com/MayorX500)
- [@Rui Armada](https://github.com/RuiArmada)
