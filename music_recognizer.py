import asyncio
from shazamio import Shazam
import os
import subprocess


class MusicRecognizer:
    async def recognize_from_file(self, file_path: str) -> dict:
        try:
            # Конвертируем видео в mp3 используя ffmpeg напрямую
            mp3_path = file_path.rsplit('.', 1)[0] + '.mp3'
            subprocess.run(['ffmpeg', '-i', file_path, '-vn', '-acodec', 'libmp3lame', '-y', mp3_path],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)

            # Создаем экземпляр Shazam
            shazam = Shazam()

            # Распознаем музыку
            result = await shazam.recognize_song(mp3_path)

            if result and result.get('track'):
                track = result['track']

                response = {
                    'title': track.get('title', 'Неизвестно'),
                    'artist': track.get('subtitle', 'Неизвестно'),
                    'album': 'Неизвестно'
                }

                # Получаем информацию об альбоме
                if 'sections' in track:
                    for section in track['sections']:
                        if section.get('type') == 'SONG':
                            for metadata in section.get('metadata', []):
                                if metadata.get('title') == 'Album':
                                    response['album'] = metadata.get('text', 'Неизвестно')
                                    break

                # Добавляем ссылки на стриминговые сервисы
                if 'hub' in track and 'providers' in track['hub']:
                    for provider in track['hub']['providers']:
                        if provider.get('type') == 'SPOTIFY':
                            response['spotify_url'] = provider.get('actions', [{}])[0].get('uri')
                        elif provider.get('type') == 'APPLE_MUSIC':
                            response['apple_music_url'] = provider.get('actions', [{}])[0].get('uri')

                return response
            return None

        except Exception as e:
            print(f"Error recognizing music: {e}")
            return None

        finally:
            # Очистка временных файлов
            if os.path.exists(mp3_path):
                os.remove(mp3_path)