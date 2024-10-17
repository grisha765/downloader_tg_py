import os

class Config:
    log_level: str = "INFO"
    tg_id: str = '1'
    tg_hash: str = 'b6b154c3707471f5339bd661645ed3d6'
    tg_token: str = 'None'
    db_path: str = ''
    download_path: str = '/tmp'
    notify_timeout: int = 900
    tests: str = 'False'
    
    @classmethod
    def load_from_env(cls):
        for key, value in cls.__annotations__.items():
            env_value = os.getenv(key.upper())
            if env_value is not None:
                if isinstance(value, int):
                    setattr(cls, key, int(env_value))
                else:
                    setattr(cls, key, env_value)
        cls.update_db_path()

    @classmethod
    def update_db_path(cls):
        if not cls.db_path:
            cls.db_path = f'sqlite://{cls.tg_token[:10]}.db'

Config.load_from_env()

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
