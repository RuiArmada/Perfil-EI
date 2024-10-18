#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' 

echo "${YELLOW}Checking if Ruby is installed${YELLOW}"
# ! Ruby
if [ -d "$HOME/.rbenv" ]; then
    export PATH="$HOME/.rbenv/bin:$PATH"
    eval "$(rbenv init -)"
fi

if rbenv versions | grep -q '3.1.2'; then
    echo "${GREEN}Ruby is already installed!${GREEN}"
else
    echo "${RED}Downloading Ruby${RED}"

    sudo apt-get update -y
    sudo apt-get install -y git curl autoconf bison build-essential libssl-dev libyaml-dev libreadline6-dev zlib1g-dev libncurses5-dev libffi-dev libgdbm6 libgdbm-dev libdb-dev

    if [ ! -d "$HOME/.rbenv" ]; then
        git clone https://github.com/rbenv/rbenv.git ~/.rbenv
        echo 'export PATH="$HOME/.rbenv/bin:$PATH"' >> ~/.bashrc
        export PATH="$HOME/.rbenv/bin:$PATH"
        eval "$(rbenv init -)"

        git clone https://github.com/rbenv/ruby-build.git ~/.rbenv/plugins/ruby-build
        echo 'export PATH="$HOME/.rbenv/plugins/ruby-build/bin:$PATH"' >> ~/.bashrc
        export PATH="$HOME/.rbenv/plugins/ruby-build/bin:$PATH"
    fi

    ~/.rbenv/bin/rbenv install 3.1.2
    ~/.rbenv/bin/rbenv global 3.1.2
    
    eval "$(rbenv init -)"
    echo "${RED}Downloading dependencies + discordrb${RED}"

    gem install bundler
    gem install yaml
    gem install discordrb

fi

# ! Node 
echo "${YELLOW}Checking if Node is installed${YELLOW}"

if [ ! -d "$HOME/.nvm" ]; then
    echo "Downloading nvm..."
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
fi

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  

if nvm current | grep -qv 'none'; then
    echo "${GREEN}Node is already installed!${GREEN}"
else
    echo "${RED}Downloading Node.js${RED}"
    nvm install node
    nvm alias default node
fi

# Verificar se discord.js está instalado
if npm list -g | grep -q 'discord.js'; then
    echo "${GREEN}Discord.js is already installed!${GREEN}"
else
    echo "${RED}Downloading discord.js${RED}"

    npm install -g discord.js
fi

# ! Go
echo "${YELLOW}Checking if Go is installed${YELLOW}"
if ! type "go" > /dev/null; then
    echo "${RED}Downloading Go${RED}"
    sudo apt-get install -y golang
fi

echo "${YELLOW}Downloading Go dependencies for the bot${YELLOW}"
go get github.com/bwmarrin/discordgo
go get gopkg.in/yaml.v2

echo "${GREEN}Everything is downloaded!${GREEN}"

# ! Lua and Luvit
echo "${YELLOW}Checking if Luvit is installed${YELLOW}"
if ! type "luvit" > /dev/null; then
    echo "${RED}Downloading Luvit${RED}"
    # Installation steps for Luvit
    curl -L https://github.com/luvit/lit/raw/master/get-lit.sh | sh
    ./lit make github.com/luvit/luvit luvit
    sudo mv luvit /usr/local/bin
    sudo mv lit /usr/local/bin
    sudo mv luvi /usr/local/bin
fi

# Install discordia via lit
if [ "$(lit ls | grep discordia)" = "" ]; then
    echo "${YELLOW}Installing Discordia${YELLOW}"
    lit install SinisterRectus/discordia
fi

# Install dkjson via luarocks
echo "${YELLOW}Checking if dkjson is installed${YELLOW}"
if ! type "luarocks" > /dev/null; then
    echo "${RED}Installing LuaRocks for dkjson dependency${RED}"
    sudo apt-get install -y luarocks
fi

if [ "$(luarocks list | grep dkjson)" = "" ]; then
    echo "${YELLOW}Installing dkjson${YELLOW}"
    sudo luarocks install dkjson
fi

echo "${YELLOW}Setting up the Lua bot script${YELLOW}"
# TODO: Ensure the bot script is present and permissions are set
BOT_SCRIPT_PATH="/path/to/your/bot.lua"

if [ ! -f "$BOT_SCRIPT_PATH" ]; then
    echo "${RED}Lua bot script not found at $BOT_SCRIPT_PATH${RED}"
else
    echo "${GREEN}Lua bot script is ready at $BOT_SCRIPT_PATH${GREEN}"
    chmod +x $BOT_SCRIPT_PATH
fi

echo "${GREEN}Lua environment setup complete. Bot is ready to run!${GREEN}"


# ! Rust

# Check for Rust installation
echo "${YELLOW}Checking if Rust is installed${YELLOW}"
if ! command -v cargo &> /dev/null; then
    echo "${RED}Rust is not installed, installing now...${RED}"
    curl https://sh.rustup.rs -sSf | sh -s -- -y
    source $HOME/.cargo/env
    echo "Please log out and back in to finalize the Rust installation, or run 'source $HOME/.cargo/env'"
else
    echo "${GREEN}Rust is already installed.${GREEN}"
fi
# TODO: Ensure the bot script is present and permissions are set
PROJECT_DIR="${1:-/path/to/your/rust/project}"  # Allow overriding via script argument
if [ ! -d "$PROJECT_DIR" ]; then
    echo "${YELLOW}Setting up the Rust project directory at ${PROJECT_DIR}${YELLOW}"
    mkdir -p "$PROJECT_DIR"
    cd "$PROJECT_DIR"
    cargo init --bin
fi

cd "$PROJECT_DIR"
echo "${YELLOW}Updating Cargo.toml with necessary dependencies${YELLOW}"
cat >> Cargo.toml <<EOL
[dependencies]
serenity = "0.10"
reqwest = "0.11"
tokio = { version = "1", features = ["full"] }
serde = { version = "1.0", features = ["derive"] }
serde_yaml = "0.8"
EOL

echo "${YELLOW}Building the project to download and compile dependencies${YELLOW}"
if ! cargo build; then
    echo "${RED}Failed to build the Rust project. Please check the output for errors.${RED}"
else
    echo "${GREEN}Rust environment setup complete. Bot is ready to be developed!${GREEN}"
fi

# ! PHP

# Check for PHP installation
echo "${YELLOW}Checking if PHP is installed${YELLOW}"
if ! command -v php > /dev/null; then
    echo "${RED}PHP is not installed, installing now...${RED}"
    sudo apt-get update
    sudo apt-get install -y php php-cli php-curl
else
    echo "${GREEN}PHP is already installed.${GREEN}"
fi

# Check for Composer installation
echo "${YELLOW}Checking if Composer is installed${YELLOW}"
if ! command -v composer > /dev/null; then
    echo "${RED}Composer is not installed, installing now...${RED}"
    php -r "copy('https://getcomposer.org/installer', 'composer-setup.php');"
    php composer-setup.php --quiet
    sudo mv composer.phar /usr/local/bin/composer
    php -r "unlink('composer-setup.php');"
else
    echo "${GREEN}Composer is already installed.${GREEN}"
fi

# TODO: Ensure the bot script is present and permissions are set
PROJECT_DIR="/path/to/your/php/project"
if [ ! -d "$PROJECT_DIR" ]; then
    echo "${YELLOW}Creating the PHP project directory at ${PROJECT_DIR}${YELLOW}"
    mkdir -p "$PROJECT_DIR"
fi

# Navigate to the project directory
cd "$PROJECT_DIR"

# Create or update the composer.json file for required packages
echo "${YELLOW}Setting up or updating composer.json with required packages${YELLOW}"
cat > composer.json <<EOL
{
    "require": {
        "team-reflex/discord-php": "^6.0",
        "guzzlehttp/guzzle": "^7.0"
    }
}
EOL

# Install or update packages
echo "${YELLOW}Installing or updating required packages via Composer${YELLOW}"
composer install

echo "${GREEN}PHP environment setup complete. Bot is ready to be developed!${GREEN}"
