import os

class Config:
    log_level: str = "INFO"
    tg_id: str = '1'
    tg_hash: str = 'b6b154c3707471f5339bd661645ed3d6'
    tg_token: str = 'None'
    db_path: str = 'data.db'
    http_proxy: str = ''
    
    @classmethod
    def load_from_env(cls):
        for key in cls.__annotations__:
            env_value = os.getenv(key.upper())
            if env_value is not None:
                current_value = getattr(cls, key)
                if isinstance(current_value, int):
                    setattr(cls, key, int(env_value))
                elif isinstance(current_value, float):
                    setattr(cls, key, float(env_value))
                elif isinstance(current_value, list):
                    setattr(cls, key, env_value.split(","))
                else:
                    setattr(cls, key, env_value)

Config.load_from_env()

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
