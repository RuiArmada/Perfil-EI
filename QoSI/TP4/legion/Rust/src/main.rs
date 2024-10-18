use serenity::{
    async_trait,
    framework::standard::{
        StandardFramework,
        CommandResult,
        macros::{command, group},
        Args,
    },
    client::{bridge::gateway::ShardManager, Client, Context},
    model::{channel::Message, gateway::Ready, id::ChannelId},
    prelude::*,
};
use reqwest;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::Mutex;
use std::time::{Duration, SystemTime, UNIX_EPOCH};
use tokio::time::sleep;

#[derive(Debug, Deserialize, Serialize)]
struct Config {
    channels: HashMap<String, String>,
    credentials: Credentials,
    guild: Guild,
}

#[derive(Debug, Deserialize, Serialize)]
struct Credentials {
    discord: String,
}

#[derive(Debug, Deserialize, Serialize)]
struct Guild {
    id: String,
}

struct Handler {
    config: Config,
}

impl TypeMapKey for MyShardManagerContainer {
    type Value = Arc<Mutex<MyShardManager>>;
}

struct MyShardManagerContainer;

struct MyShardManager {
    shard_manager: Arc<Mutex<ShardManager>>,
    runners: HashMap<u64, Runner>,
}

struct Runner {
    id: u64,
    latency: Option<Duration>,
}

#[group]
#[commands(ping, shutdown)]
struct General;

#[command]
async fn ping(ctx: &Context, msg: &Message) -> CommandResult {
    msg.reply(ctx, "Pong!").await?;
    Ok(())
}

#[command]
async fn shutdown(ctx: &Context, msg: &Message, _: Args) -> CommandResult {
    if let Ok(current_user) = ctx.http.get_current_user().await {
        if msg.author.id == current_user.id {
            let data_read = ctx.data.read().await;
            if let Some(shard_manager) = data_read.get::<MyShardManagerContainer>() {
                let mut manager = shard_manager.lock().await;
                manager.shard_manager.lock().await.shutdown_all().await;
                msg.reply(ctx, "Shutting down...").await?;

                // Signal that the bot should shut down.
                return Ok(());
            }
            msg.reply(ctx, "Failed to fetch shard manager.").await?;
        } else {
            msg.reply(ctx, "You do not have permission to perform this operation.").await?;
        }
    } else {
        msg.reply(ctx, "Failed to fetch current user information.").await?;
    }
    Ok(())
}

#[async_trait]
impl EventHandler for Handler {
    async fn ready(&self, ctx: Context, _ready: Ready) {
        println!("Bot is ready. Setting up handlers...");
        sleep(Duration::from_secs(5)).await;

        let public_ip = match reqwest::get("https://api.ipify.org").await {
            Ok(resp) => resp.text().await.unwrap_or_else(|_| "Error fetching IP".to_string()),
            Err(_) => "Error fetching IP".to_string(),
        };

        if let Some(shard_manager_container) = ctx.data.read().await.get::<MyShardManagerContainer>() {
            let mut shard_manager = shard_manager_container.lock().await;
            shard_manager.runners.insert(0, Runner { id: 0, latency: Some(Duration::from_millis(150)) });
            println!("Simulated latency set for Runner ID 0");
        }

        let latency = calculate_latency(&ctx).await;
        println!("Calculated latency: {:.2}ms", latency);

        let hostname_str = "zephyrus";
        println!("Using static hostname: {}", hostname_str);

        let timestamp = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_millis();
        let json_string = format!(
            "```json\n{{\"latency\": {:.2}, \"public_ip\": \"{}\", \"hostname\": \"{}\", \"lang\": \"rust\", \"timestamp\": {} }}\n```",
            latency,
            public_ip,
            hostname_str,
            timestamp
        );

        if let Some(channel_id_str) = self.config.channels.get(hostname_str) {
            if let Ok(channel_id) = channel_id_str.parse::<u64>() {
                let channel_id = ChannelId(channel_id);
                if let Err(why) = channel_id.say(&ctx.http, &json_string).await {
                    println!("Error sending message: {:?}", why);
                } else {
                    println!("Message sent successfully to channel ID {}", channel_id);
                    // Desligar imediatamente após enviar a mensagem
                    let data_read = ctx.data.read().await;
                    if let Some(shard_manager) = data_read.get::<MyShardManagerContainer>() {
                        let mut manager = shard_manager.lock().await;
                        manager.shard_manager.lock().await.shutdown_all().await;
                    }
                    return; // Encerra a função ready para não continuar o processamento
                }
            } else {
                println!("Invalid channel ID format in config");
            }
        } else {
            println!("No channel configured for hostname: {}", hostname_str);
        }
    }
}

async fn calculate_latency(ctx: &Context) -> f64 {
    let data_read = ctx.data.read().await;
    if let Some(shard_manager_container) = data_read.get::<MyShardManagerContainer>() {
        let shard_manager = shard_manager_container.lock().await;

        let latencies: Vec<f64> = shard_manager.runners.values()
            .filter_map(|runner| runner.latency)
            .map(|latency| latency.as_secs_f64() * 1000.0)
            .collect();

        let total_latency: f64 = latencies.iter().sum();
        let count = latencies.len() as f64;

        if count > 0.0 {
            return total_latency / count;
        }
    }
    0.0  // Default return value
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let config: Config = serde_yaml::from_reader(std::fs::File::open("config.yaml")?)?;

    let framework = StandardFramework::new()
        .configure(|c| c.prefix("!"))
        .group(&GENERAL_GROUP);

    let handler = Handler { config };
    let intents = GatewayIntents::GUILDS | GatewayIntents::GUILD_MESSAGES;
    let mut client = Client::builder(&handler.config.credentials.discord, intents)
        .event_handler(handler)
        .framework(framework)
        .await?;

    {
        let mut data = client.data.write().await;
        let my_shard_manager = MyShardManager {
            shard_manager: client.shard_manager.clone(),
            runners: HashMap::new(),
        };
        data.insert::<MyShardManagerContainer>(Arc::new(Mutex::new(my_shard_manager)));
    }

    println!("Starting client...");
    client.start().await.map_err(Into::into)
}
