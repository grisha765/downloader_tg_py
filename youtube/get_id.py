def get_url_id(url):
    if "youtube.com" in url:
        return url.split('v=')[-1]
    elif "youtu.be" in url:
        return url.split('/')[-1]
    else:
        return "unknown_id"

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
