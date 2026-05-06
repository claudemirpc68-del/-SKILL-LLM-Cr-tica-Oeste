import yt_dlp
import json
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi

class YouTubeFetcher:
    def __init__(self, channel_url="https://www.youtube.com/@RevistaOeste/streams"):
        self.channel_url = channel_url
        self.ydl_opts = {
            'quiet': True,
            'extract_flat': True,
            'force_generic_extractor': False,
        }

    def fetch_new_videos(self, limit=5):
        """Busca os vídeos mais recentes do canal."""
        print(f"Buscando vídeos de: {self.channel_url}")
        
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            try:
                info = ydl.extract_info(self.channel_url, download=False)
                if 'entries' in info:
                    videos = info['entries'][:limit]
                    return [
                        {
                            "id": v.get("id"),
                            "title": v.get("title"),
                            "url": f"https://www.youtube.com/watch?v={v.get('id')}",
                            "publish_date": v.get("upload_date", datetime.now().strftime("%Y%m%d"))
                        } for v in videos
                    ]
            except Exception as e:
                print(f"Erro ao coletar vídeos: {e}")
                return []

    def get_video_details(self, video_id):
        """Extrai descrição e transcrição usando motor de alta velocidade."""
        # Tenta pegar a transcrição primeiro (mais rica para a IA)
        transcript_text = ""
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['pt'])
            transcript_text = " ".join([t['text'] for t in transcript])
        except Exception as e:
            print(f"Aviso: Transcrição não disponível para {video_id} (Pode ser uma live agendada ou sem legenda).")

        # Puxa metadados básicos via yt-dlp (rápido se não baixar legendas)
        opts = {'skip_download': True, 'quiet': True}
        with yt_dlp.YoutubeDL(opts) as ydl:
            try:
                info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
                
                # Se for agendado (upcoming), retornamos None para o main.py ignorar
                if info.get('live_status') == 'is_upcoming':
                    return None

                return {
                    "title": info.get("title"),
                    "description": info.get("description"),
                    "transcript": transcript_text,
                    "content_combined": (transcript_text + " " + (info.get("description") or ""))[:10000] # Limite para a IA
                }
            except Exception as e:
                print(f"Erro ao extrair metadados: {e}")
                return None

if __name__ == "__main__":
    fetcher = YouTubeFetcher()
    recent_videos = fetcher.fetch_new_videos(limit=2)
    print(json.dumps(recent_videos, indent=2))
