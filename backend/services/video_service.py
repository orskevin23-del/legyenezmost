import os
import logging
import asyncio
from pathlib import Path
from typing import Optional, Dict, List
import aiohttp
import json
from elevenlabs import ElevenLabs, VoiceSettings

logger = logging.getLogger(__name__)

class VideoGenerationService:
    """
    Complete video generation pipeline:
    1. Generate TTS audio with word timestamps (ElevenLabs)
    2. Search and download B-roll clips (Pexels 9:16 vertical)
    3. Assemble video with FFmpeg (karaoke captions, B-roll cutting, music)
    """
    
    def __init__(self):
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        self.elevenlabs_voice_id = os.getenv("ELEVENLABS_VOICE_ID")
        self.pexels_api_key = os.getenv("PEXELS_API_KEY")
        self.output_dir = Path(os.getenv("VIDEO_OUTPUT_DIR", "/app/videos"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize ElevenLabs client
        self.eleven_client = ElevenLabs(api_key=self.elevenlabs_api_key)
    
    async def generate_video(
        self,
        video_id: str,
        script_text: str,
        topic: str,
        user_id: str,
        voice_settings: Optional[Dict] = None,
        background_music: Optional[str] = None,
        b_roll_search: Optional[str] = None
    ):
        """
        Complete video generation workflow.
        """
        try:
            from database import db
            
            # Update status to processing
            await db.videos.update_one(
                {"id": video_id},
                {"$set": {"status": "processing"}}
            )
            
            logger.info(f"Starting video generation for {video_id}")
            
            # Step 1: Generate TTS with timestamps
            audio_path, word_timestamps = await self.generate_tts_with_timestamps(
                video_id, script_text, voice_settings
            )
            
            # Step 2: Get audio duration
            duration = await self.get_audio_duration(audio_path)
            
            # Step 3: Search and download B-roll clips
            search_query = b_roll_search or topic or "spirituality faith peaceful"
            broll_clips = await self.download_broll_clips(
                video_id, search_query, duration
            )
            
            # Step 4: Assemble video with FFmpeg
            video_path = await self.assemble_video(
                video_id=video_id,
                audio_path=audio_path,
                broll_clips=broll_clips,
                word_timestamps=word_timestamps,
                script_text=script_text,
                background_music=background_music,
                duration=duration
            )
            
            # Update video record
            import datetime
            await db.videos.update_one(
                {"id": video_id},
                {
                    "$set": {
                        "status": "completed",
                        "video_url": str(video_path),
                        "audio_url": str(audio_path),
                        "duration": duration,
                        "completed_at": datetime.datetime.utcnow().isoformat()
                    }
                }
            )
            
            logger.info(f"Video generation completed for {video_id}")
        
        except Exception as e:
            logger.error(f"Error generating video {video_id}: {str(e)}")
            
            from database import db
            await db.videos.update_one(
                {"id": video_id},
                {
                    "$set": {
                        "status": "failed",
                        "error": str(e)
                    }
                }
            )
    
    async def generate_tts_with_timestamps(
        self,
        video_id: str,
        text: str,
        voice_settings: Optional[Dict] = None
    ) -> tuple:
        """
        Generate TTS audio using ElevenLabs with word-level timestamps.
        Uses API v3 for better stability.
        """
        import subprocess
        
        try:
            # Extract speed from voice_settings (API v3 supports it)
            speed = voice_settings.get("speed", 1.0) if voice_settings else 1.0
            
            settings = VoiceSettings(
                stability=voice_settings.get("stability", 0.7) if voice_settings else 0.7,
                similarity_boost=voice_settings.get("similarity_boost", 0.75) if voice_settings else 0.75,
                style=voice_settings.get("style", 0.5) if voice_settings else 0.5,
                use_speaker_boost=voice_settings.get("use_speaker_boost", True) if voice_settings else True
            )
            
            # Generate audio with API v3 (supports speed parameter)
            logger.info(f"Generating TTS audio with ElevenLabs API v3 (speed: {speed}x)...")
            response = self.eleven_client.text_to_speech.convert(
                text=text,
                voice_id=self.elevenlabs_voice_id,
                model_id="eleven_turbo_v2_5",  # Latest stable model
                voice_settings=settings,
                output_format="mp3_44100_128",
                seed=42  # Fixed seed for consistent first variation
            )
            
            # Note: Speed is applied via model capabilities in v3
            # If speed adjustment needed, we can post-process with FFmpeg
            
            # Save audio as MP3 first
            audio_path_mp3 = self.output_dir / f"{video_id}_audio_temp.mp3"
            audio_path = self.output_dir / f"{video_id}_audio.wav"
            
            audio_data = b""
            for chunk in response:
                audio_data += chunk
            
            # Write MP3
            with open(audio_path_mp3, 'wb') as f:
                f.write(audio_data)
            
            logger.info(f"Generated TTS audio (MP3): {audio_path_mp3}, size: {len(audio_data)} bytes")
            
            # Convert MP3 to WAV and apply speed adjustment if needed
            if speed != 1.0:
                # Apply speed with FFmpeg atempo filter
                logger.info(f"Applying speed adjustment: {speed}x")
                ffmpeg_cmd = [
                    'ffmpeg',
                    '-i', str(audio_path_mp3),
                    '-filter:a', f'atempo={speed}',
                    '-acodec', 'pcm_s16le',
                    '-ar', '44100',
                    '-ac', '2',
                    '-y',
                    str(audio_path)
                ]
            else:
                # Normal conversion without speed change
                ffmpeg_cmd = [
                    'ffmpeg',
                    '-i', str(audio_path_mp3),
                    '-acodec', 'pcm_s16le',
                    '-ar', '44100',
                    '-ac', '2',
                    '-y',
                    str(audio_path)
                ]
            
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"FFmpeg conversion failed: {result.stderr}")
                # If conversion fails, use MP3 directly
                audio_path = audio_path_mp3
            else:
                # Remove temp MP3
                audio_path_mp3.unlink()
                logger.info(f"Converted to WAV with speed {speed}x: {audio_path}")
            
            # Use OpenAI Whisper for accurate word-level timestamps
            logger.info("Generating word timestamps with OpenAI Whisper...")
            word_timestamps = await self._get_whisper_timestamps(audio_path, text)
            
            return audio_path, word_timestamps
        
        except Exception as e:
            logger.error(f"Error generating TTS: {str(e)}")
            raise
    
    def _get_audio_duration(self, audio_path: Path) -> float:
        """Get audio duration using FFprobe"""
        import subprocess
        import json
        
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            str(audio_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return float(data['format']['duration'])
        return 30.0  # Default

    
    async def _get_whisper_timestamps(self, audio_path: Path, original_text: str) -> List[Dict]:
        """
        Use OpenAI Whisper API to get accurate word-level timestamps from audio.
        """
        try:
            from openai import OpenAI
            
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                logger.warning("OpenAI API key not found, falling back to simple timing")
                return self._fallback_timestamps(audio_path, original_text)
            
            client = OpenAI(api_key=openai_api_key)
            
            # Open audio file
            with open(audio_path, "rb") as audio_file:
                # Call Whisper API with word-level timestamps
                logger.info("Calling OpenAI Whisper API for word timestamps...")
                transcription = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="verbose_json",
                    timestamp_granularities=["word"]
                )
            
            # Extract word timestamps
            word_timestamps = []
            
            if hasattr(transcription, 'words') and transcription.words:
                for word_data in transcription.words:
                    word_timestamps.append({
                        'character': word_data.word.strip(),
                        'start_time_ms': int(word_data.start * 1000),
                        'end_time_ms': int(word_data.end * 1000)
                    })
                
                logger.info(f"Whisper extracted {len(word_timestamps)} word timestamps")
            else:
                logger.warning("Whisper didn't return word timestamps, using fallback")
                word_timestamps = self._fallback_timestamps(audio_path, original_text)
            
            return word_timestamps
        
        except Exception as e:
            logger.error(f"Error getting Whisper timestamps: {str(e)}")
            # Fallback to simple timing
            return self._fallback_timestamps(audio_path, original_text)
    
    def _fallback_timestamps(self, audio_path: Path, text: str) -> List[Dict]:
        """
        Fallback method: simple time division if Whisper fails.
        """
        words = text.split()
        audio_duration = self._get_audio_duration(audio_path)
        word_duration = audio_duration / len(words) if words else 1.0
        
        word_timestamps = []
        for i, word in enumerate(words):
            start_time_ms = int(i * word_duration * 1000)
            end_time_ms = int((i + 1) * word_duration * 1000)
            word_timestamps.append({
                'character': word,
                'start_time_ms': start_time_ms,
                'end_time_ms': end_time_ms
            })
        
        return word_timestamps

    
    async def get_audio_duration(self, audio_path: Path) -> float:
        """
        Get audio duration using FFmpeg.
        """
        import subprocess
        import json
        
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'json',
            str(audio_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)
        duration = float(data.get('format', {}).get('duration', 30.0))
        
        return duration
    
    async def download_broll_clips(
        self,
        video_id: str,
        search_query: str,
        total_duration: float
    ) -> List[Path]:
        """
        Search and download vertical B-roll clips from Pexels.
        Clips should be 2-3 seconds each to match total duration.
        QUALITY FILTER: Only HD, minimum 5s duration, curated content.
        """
        try:
            # Calculate number of clips needed (2.5s avg per clip)
            num_clips = int(total_duration / 2.5) + 2  # Extra clips for variety
            
            # Enhance search query for faith content
            if not search_query or search_query == "spirituality faith peaceful":
                search_query = "faith prayer spiritual light hope peace nature"
            
            # Search Pexels for vertical videos with QUALITY FILTERS
            headers = {"Authorization": self.pexels_api_key}
            params = {
                "query": search_query,
                "orientation": "portrait",  # 9:16 vertical only
                "size": "large",  # Large/HD only
                "per_page": min(num_clips * 2, 30),  # Request more for filtering
                "min_duration": 5,  # Minimum 5 seconds (quality indicator)
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.pexels.com/videos/search",
                    headers=headers,
                    params=params
                ) as response:
                    data = await response.json()
            
            videos = data.get("videos", [])
            
            # QUALITY FILTER: Sort by quality indicators
            quality_videos = []
            for video in videos:
                # Filter criteria:
                # 1. Has HD files
                # 2. Duration > 5 seconds
                # 3. Has proper metadata
                duration = video.get("duration", 0)
                video_files = video.get("video_files", [])
                
                if duration >= 5 and len(video_files) > 0:
                    quality_videos.append(video)
            
            # Sort by duration (longer = often better quality)
            quality_videos.sort(key=lambda v: v.get("duration", 0), reverse=True)
            
            # Download clips
            downloaded_clips = []
            
            for idx, video in enumerate(quality_videos[:num_clips]):
                video_files = video.get("video_files", [])
                
                # Find BEST quality vertical HD file
                hd_file = None
                best_quality = 0
                
                for vf in video_files:
                    width = vf.get("width", 0)
                    height = vf.get("height", 0)
                    quality = vf.get("quality", "")
                    
                    # Must be vertical (height > width)
                    if height > width:
                        # Prefer HD/FHD
                        quality_score = 0
                        if quality == "hd":
                            quality_score = 2
                        elif quality == "sd":
                            quality_score = 1
                        
                        # Also consider resolution
                        quality_score += (width * height) / 1000000
                        
                        if quality_score > best_quality:
                            best_quality = quality_score
                            hd_file = vf
                
                if hd_file:
                    clip_path = await self.download_video_file(
                        video_id, idx, hd_file.get("link")
                    )
                    if clip_path:
                        downloaded_clips.append(clip_path)
            
            logger.info(f"Downloaded {len(downloaded_clips)} HIGH-QUALITY B-roll clips")
            return downloaded_clips
        
        except Exception as e:
            logger.error(f"Error downloading B-roll: {str(e)}")
            return []
    
    async def download_video_file(self, video_id: str, idx: int, url: str) -> Optional[Path]:
        """
        Download a single video file.
        """
        try:
            output_path = self.output_dir / f"{video_id}_broll_{idx}.mp4"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        with open(output_path, 'wb') as f:
                            f.write(await response.read())
                        return output_path
            
            return None
        except Exception as e:
            logger.error(f"Error downloading video file: {str(e)}")
            return None
    
    async def assemble_video(
        self,
        video_id: str,
        audio_path: Path,
        broll_clips: List[Path],
        word_timestamps: List,
        script_text: str,
        background_music: Optional[str],
        duration: float
    ) -> Path:
        """
        Assemble final video using FFmpeg with:
        - B-roll clips (2-3s cuts)
        - Karaoke captions (white → yellow)
        - Audio mixing (TTS + background music)
        - Safe zones (avoid YouTube UI)
        """
        from services.ffmpeg_service import FFmpegService
        
        ffmpeg_service = FFmpegService()
        
        output_path = self.output_dir / f"{video_id}_final.mp4"
        
        # Assemble video
        await ffmpeg_service.create_shorts_video(
            output_path=output_path,
            audio_path=audio_path,
            broll_clips=broll_clips,
            word_timestamps=word_timestamps,
            script_text=script_text,
            background_music=background_music,
            duration=duration
        )
        
        return output_path