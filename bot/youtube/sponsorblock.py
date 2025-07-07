from bot.core.helpers import Common

def get_time_code(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    if hours > 0:
        return f"{hours:02}:{minutes:02}:{seconds:02}"
    else:
        return f"{minutes:02}:{seconds:02}"


def format_segments(sponsor_segments, selfpromo_segments, interaction_segments, intro_segments, outro_segments):
    segments_dict = {
        "Sponsor": sponsor_segments,
        "Selfpromo": selfpromo_segments,
        "Interaction": interaction_segments,
        "Intro": intro_segments,
        "Outro": outro_segments,
    }
    
    result = []
    
    for segment_name, segments in segments_dict.items():
        if segments:
            result.append(f"**{segment_name}**")
            for i, (start, end) in enumerate(segments, 1):
                result.append(f"{start} - start {segment_name.lower()} {i}")
                result.append(f"{end} - end {segment_name.lower()} {i}")
                
    return "\n".join(result)


async def get_sponsor_segments(video_id):
    sponsorblock_api_url = f"https://sponsor.ajay.app/api/skipSegments?videoID={video_id}"
    
    response = await Common.http.get(sponsorblock_api_url)
    data = response.json()
    
    sponsor_segments = []
    selfpromo_segments = []
    interaction_segments = []
    intro_segments = []
    outro_segments = []
    
    for segment in data:
        category = segment['category']
        start_time = get_time_code(segment['segment'][0])
        end_time = get_time_code(segment['segment'][1])
        
        if category == "sponsor":
            sponsor_segments.append((start_time, end_time))
        elif category == "selfpromo":
            selfpromo_segments.append((start_time, end_time))
        elif category == "interaction":
            interaction_segments.append((start_time, end_time))
        elif category == "intro":
            intro_segments.append((start_time, end_time))
        elif category == "outro":
            outro_segments.append((start_time, end_time))
    
    return sponsor_segments, selfpromo_segments, interaction_segments, intro_segments, outro_segments


def get_url_id(url):
    if "youtube.com" in url:
        return url.split('v=')[-1]
    elif "youtu.be" in url:
        return url.split('/')[-1]
    else:
        return "unknown_id"


async def sponsorblock(url):
    url_id = get_url_id(url)
    try:
        sponsor_segments, selfpromo_segments, interaction_segments, intro_segments, outro_segments = await get_sponsor_segments(url_id)
        formatted_str = format_segments(
            sponsor_segments,
            selfpromo_segments,
            interaction_segments,
            intro_segments,
            outro_segments
        )

        return formatted_str
    except:
        return "**No segments**"

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
