import json
import requests
from bs4 import BeautifulSoup


USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0"

def fetch_video_link(url: str) -> str:
    try:
        # get
        response = requests.get(url, headers={"User-Agent": USER_AGENT})
        if response.status_code != 200:
            return None

        # parese
        soup = BeautifulSoup(response.text, "html.parser")
        packaged_media_plain = soup.find(attrs={"packaged-media-json": True}).get("packaged-media-json")
        packaged_media = json.loads(packaged_media_plain)
        videos = packaged_media.get("playbackMp4s", {}).get("permutations", [])

        # pick the highest resolution
        if videos:
            return videos[-1]["source"]["url"]

    except Exception as _:
        return None



# print(fetch_video_link("https://www.reddit.com/r/anthroswim/comments/1g6bir5/one_must_imagine_the_dogman_happy_poppaboi/"))
print(fetch_video_link("https://www.reddit.com/r/Brawlhalla/comments/s9nof2/all_fixes_for_brawlhalla_fps_drops/"))