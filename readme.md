# downloader_tg_py

This project is a YouTube downloader bot for Telegram. It allows users to download videos or audio from YouTube, manage their subscribed channels, and receive notifications and downloads about new videos.

### Initial Setup

1. **Clone the repository**: Clone this repository using `git clone`.
2. **Create Virtual Env**: Create a Python Virtual Environment `venv` to download the required dependencies and libraries.
3. **Download Dependencies**: Download the required dependencies into the Virtual Environment `venv` using `pip`.

```shell
git clone https://github.com/grisha765/downloader_tg_py.git
cd downloader_tg_py
python -m venv .venv
.venv/bin/python -m pip install uv
.venv/bin/python -m uv sync
```

## Usage

### Deploy

- Run the bot:
    ```bash
    TG_TOKEN="telegram_bot_token" uv run main.py
    ```

- Other working env's:
    ```env
    LOG_LEVEL="INFO"
    TG_ID="your_telegram_api_id"
    TG_HASH="your_telegram_api_hash"
    TG_TOKEN="your_telegram_bot_token"
    DB_PATH="data.db"
    HTTP_PROXY="http://login:password@123.45.678.910:1234"
    ```

#### Container

- Pull container:
    ```bash
    podman pull ghcr.io/grisha765/downloader_tg_py:latest
    ```

- Deploy in container:
    ```bash
    mkdir -p $HOME/database/ && \
    podman run --tmpfs /tmp \
    --name downloader_tg_py \
    -v $HOME/database/:/app/database/:z \
    -e TG_TOKEN="your_telegram_bot_token" \
    ghcr.io/grisha765/downloader_tg_py:latest
    ```
## Features

- **Download Videos**:
  Users can download YouTube videos in various qualities.
- **Channel Subscription**:
  Users can subscribe to YouTube channels and receive notifications and downloads when new videos are uploaded.
- **SponsorBlock Integration**:
  Automatically reads sponsored segments in downloaded videos.
- **Customizable**:
  Configure log level, http proxy, and more through environment variables. Also configuration of notifications about new videos the user has.
