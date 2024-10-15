# downloader_tg_py

This project is a YouTube downloader bot for Telegram. It allows users to download videos or audio from YouTube, manage their subscribed channels, and receive notifications about new videos.

### Initial Setup

1. **Clone the repository**: Clone this repository using `git clone`.
2. **Create Virtual Env**: Create a Python Virtual Environment `venv` to download the required dependencies and libraries.
3. **Download Dependencies**: Download the required dependencies into the Virtual Environment `venv` using `pip`.

```shell
git clone https://github.com/grisha765/downloader_tg_py.git
cd downloader_tg_py
python3 -m venv .venv
venv/bin/pip install -r requirements.txt
```

## Usage

### Deploy

- Run the bot:
    ```bash
    TG_TOKEN="telegram_bot_token" python main.py
    ```

- Other working env's:
    ```env
    LOG_LEVEL="INFO"
    TG_ID="your_telegram_api_id"
    TG_HASH="your_telegram_api_hash"
    TG_TOKEN="your_telegram_bot_token"
    NOTIFY_TIMEOUT=900
    ```

- Deploy in container:
    ```bash
    podman pull ghcr.io/grisha765/downloader_tg_py:latest
    mkdir -p $HOME/database/ && \
    podman run \
    --name downloader_tg_py \
    -v $HOME/database/:/app/database/:z \
    -e TG_TOKEN="your_telegram_bot_token" \
    ghcr.io/grisha765/downloader_tg_py:latest
    ```

### Commands

- `/sponsor`: Toggle SponsorBlock feature on or off.
- `/addchannel <channel_url>`: Add a YouTube channel to your subscription list.
- `/delchannel <channel_url>`: Remove a YouTube channel from your subscription list.
- Send any YouTube video URL in a private message to get download options.

### Examples

- **Download a Video**: Send a YouTube video URL in a private message to the bot. The bot will respond with download options for different video qualities and an audio-only option.
- **Subscribe to a Channel**: Use the `/addchannel <channel_url>` command to subscribe to a YouTube channel. The bot will notify you when a new video is uploaded to the subscribed channel.

## Advantages

- **Easy to Use**: Simple commands and interaction through Telegram make it easy for anyone to use.
- **Automatic Updates**: Stay updated with new videos from your favorite channels without any manual effort.
- **Quality Selection**: Choose the desired quality for video downloads.
- **Sponsor Skipping**: Skip unwanted sponsor segments automatically.

## Features

- **Download Videos and Audio**: Users can download YouTube videos in various qualities or as audio files.
- **Channel Subscription**: Users can subscribe to YouTube channels and receive notifications when new videos are uploaded.
- **SponsorBlock Integration**: Automatically skip sponsored segments in downloaded videos.
- **Customizable**: Configure log level, timeout for notifications, and more through environment variables.

## Contributing

Contributions are welcome! Please fork the repository and submit pull requests.
