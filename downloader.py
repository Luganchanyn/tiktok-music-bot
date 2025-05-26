import os
import yt_dlp
from config import DOWNLOADS_DIR

class TikTokDownloader:
    def __init__(self):
        self.ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(DOWNLOADS_DIR, '%(id)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
        }

    async def download_video(self, url: str) -> str:
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_path = os.path.join(DOWNLOADS_DIR, f"{info['id']}.{info['ext']}")
                return video_path
        except Exception as e:
            print(f"Error downloading video: {e}")
            return None