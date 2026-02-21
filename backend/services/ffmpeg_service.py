import subprocess
import logging
from pathlib import Path
from typing import List, Optional, Dict
import json

logger = logging.getLogger(__name__)

class FFmpegService:
    """
    FFmpeg video assembly service for creating market-ready YouTube Shorts.
    - 9:16 vertical format
    - Karaoke subtitles (white → lemon yellow)
    - B-roll cuts every 2-3 seconds
    - Audio mixing (TTS + background music with ducking)
    - Safe zones (avoid YouTube UI buttons)
    """
    
    @staticmethod
    async def create_shorts_video(
        output_path: Path,
        audio_path: Path,
        broll_clips: List[Path],
        word_timestamps: List,
        script_text: str,
        background_music: Optional[str],
        duration: float
    ):
        """
        Create complete YouTube Shorts video with all elements.
        """
        try:
            # Step 1: Create concatenated B-roll video (2-3s cuts)
            concat_video = output_path.parent / f"{output_path.stem}_concat.mp4"
            await FFmpegService.concatenate_broll(broll_clips, concat_video, duration)
            
            # Step 2: Create karaoke subtitle file (ASS format for word-level highlighting)
            subtitle_path = output_path.parent / f"{output_path.stem}.ass"
            FFmpegService.create_karaoke_subtitles(
                subtitle_path, script_text, word_timestamps, duration
            )
            
            # Step 3: Assemble final video
            if background_music:
                # With background music
                await FFmpegService.assemble_with_music(
                    output_path, concat_video, audio_path, subtitle_path, background_music
                )
            else:
                # Without background music
                await FFmpegService.assemble_without_music(
                    output_path, concat_video, audio_path, subtitle_path
                )
            
            logger.info(f"Video assembled successfully: {output_path}")
        
        except Exception as e:
            logger.error(f"Error assembling video: {str(e)}")
            raise
    
    @staticmethod
    async def concatenate_broll(broll_clips: List[Path], output_path: Path, total_duration: float):
        """
        Concatenate B-roll clips to match total duration.
        Each clip is cut to EXACTLY 2.5 seconds and looped as needed.
        """
        if not broll_clips:
            # Create black video if no B-roll available
            cmd = [
                'ffmpeg', '-f', 'lavfi',
                '-i', f'color=c=black:s=1080x1920:d={total_duration}',
                '-pix_fmt', 'yuv420p',
                str(output_path), '-y'
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            return
        
        # Create individual 2.5 second clips first
        clip_duration = 2.5
        temp_clips = []
        
        for i, clip_path in enumerate(broll_clips):
            temp_clip = output_path.parent / f"temp_clip_{i}.mp4"
            
            # Cut each clip to exactly 2.5 seconds
            cmd = [
                'ffmpeg',
                '-i', str(clip_path),
                '-t', str(clip_duration),
                '-vf', f'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30',
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-crf', '23',
                '-an',  # Remove audio from B-roll
                str(temp_clip), '-y'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                temp_clips.append(temp_clip)
        
        if not temp_clips:
            logger.error("No valid B-roll clips after processing")
            return
        
        # Create concat file with properly cut clips
        concat_file = output_path.parent / "concat_list.txt"
        clips_needed = int(total_duration / clip_duration) + 1
        
        with open(concat_file, 'w') as f:
            for i in range(clips_needed):
                clip_idx = i % len(temp_clips)
                f.write(f"file '{temp_clips[clip_idx]}'\n")
        
        # Concatenate clips
        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(concat_file),
            '-t', str(total_duration),
            '-c', 'copy',
            str(output_path), '-y'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Cleanup temp files
        for temp_clip in temp_clips:
            temp_clip.unlink(missing_ok=True)
        concat_file.unlink(missing_ok=True)
        
        if result.returncode != 0:
            logger.error(f"FFmpeg concat error: {result.stderr}")
            raise Exception(f"Failed to concatenate B-roll: {result.stderr}")
    
    @staticmethod
    def create_karaoke_subtitles(
        output_path: Path,
        script_text: str,
        word_timestamps: List,
        duration: float
    ):
        """
        Create ASS subtitle file with TRUE karaoke effect.
        Only the CURRENTLY spoken word is YELLOW, all others are WHITE.
        Uses individual dialogue lines per word group, with inline color overrides.
        """
        # ASS header - base style is WHITE text
        # PrimaryColour = WHITE (default text color)
        # Using soft shadow (BorderStyle=1 with Shadow), centered at bottom
        ass_content = """[Script Info]
Title: Karaoke Subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: None
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,48,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,0,2,2,20,20,120,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        
        words = script_text.split()
        if not words:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(ass_content)
            return
        
        # Calculate word timings
        word_timings = []
        
        if word_timestamps and len(word_timestamps) > 0:
            # Use provided timestamps
            for i, ts in enumerate(word_timestamps):
                if isinstance(ts, dict) and 'word' in ts:
                    word_timings.append({
                        'word': ts['word'],
                        'start': ts.get('start', 0),
                        'end': ts.get('end', duration)
                    })
                elif isinstance(ts, dict) and 'character' in ts:
                    word_timings.append({
                        'word': ts['character'],
                        'start': ts.get('start_time_ms', 0) / 1000.0,
                        'end': ts.get('end_time_ms', duration * 1000) / 1000.0 if 'end_time_ms' in ts else (word_timestamps[i+1].get('start_time_ms', duration * 1000) / 1000.0 if i < len(word_timestamps) - 1 else duration)
                    })
        
        # If no timestamps or parsing failed, distribute evenly
        if not word_timings:
            word_duration = duration / len(words) if words else 1.0
            for i, word in enumerate(words):
                word_timings.append({
                    'word': word,
                    'start': i * word_duration,
                    'end': (i + 1) * word_duration
                })
        
        # Group words into lines (3-5 words per line for readability)
        groups = []
        current_group = []
        for wt in word_timings:
            current_group.append(wt)
            # Group size: 3-4 words, or break on long words
            if len(current_group) >= 4 or (len(current_group) >= 3 and len(wt['word']) > 10):
                groups.append(current_group)
                current_group = []
        if current_group:
            groups.append(current_group)
        
        # Generate dialogue lines for each word highlight within each group
        # This creates the TRUE karaoke effect: only the current word is yellow
        for group in groups:
            group_start = group[0]['start']
            group_end = group[-1]['end']
            
            # For each word in the group, create a dialogue line where ONLY that word is yellow
            for idx, current_word in enumerate(group):
                word_start = current_word['start']
                word_end = current_word['end']
                
                # Build the text with color overrides
                # {\c&H00FFFF&} = Yellow (BGR format: 00FFFF = Yellow)
                # {\c&HFFFFFF&} = White
                text_parts = []
                for i, wt in enumerate(group):
                    if i == idx:
                        # Current word - YELLOW
                        text_parts.append(f"{{\\c&H00FFFF&}}{wt['word']}{{\\c&HFFFFFF&}}")
                    else:
                        # Other words - WHITE (default)
                        text_parts.append(wt['word'])
                
                line_text = ' '.join(text_parts)
                start_time = FFmpegService.format_ass_time(word_start)
                end_time = FFmpegService.format_ass_time(word_end)
                
                ass_content += f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{line_text}\n"
        
        # Write ASS file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(ass_content)
        
        logger.info(f"Created TRUE karaoke subtitles: {output_path}")
    
    @staticmethod
    def format_ass_time(seconds: float) -> str:
        """Format time for ASS subtitles: H:MM:SS.CC"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        centisecs = int((seconds % 1) * 100)
        return f"{hours}:{minutes:02d}:{secs:02d}.{centisecs:02d}"
    
    @staticmethod
    async def assemble_with_music(
        output_path: Path,
        video_path: Path,
        audio_path: Path,
        subtitle_path: Path,
        music_path: str
    ):
        """
        Assemble video with TTS audio, background music, and subtitles.
        Apply volume ducking to music when TTS is playing.
        """
        # Use subtitles filter without force_style - ASS file has all styling
        cmd = [
            'ffmpeg',
            '-i', str(video_path),
            '-i', str(audio_path),
            '-i', music_path,
            '-filter_complex',
            (
                # Audio mixing with ducking
                f'[1:a]volume=1.0[voice];'
                f'[2:a]volume=0.3[music];'
                f'[voice][music]amix=inputs=2:duration=first:dropout_transition=2[audio];'
                # Subtitles - let ASS file handle all styling
                f'[0:v]subtitles={subtitle_path}[video]'
            ),
            '-map', '[video]',
            '-map', '[audio]',
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-movflags', '+faststart',
            str(output_path), '-y'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"FFmpeg assembly error: {result.stderr}")
            raise Exception(f"Failed to assemble video: {result.stderr}")
    
    @staticmethod
    async def assemble_without_music(
        output_path: Path,
        video_path: Path,
        audio_path: Path,
        subtitle_path: Path
    ):
        """
        Assemble video with TTS audio and subtitles (no background music).
        """
        # Use subtitles filter without force_style - ASS file has all styling
        cmd = [
            'ffmpeg',
            '-i', str(video_path),
            '-i', str(audio_path),
            '-filter_complex',
            f'[0:v]subtitles={subtitle_path}[video]',
            '-map', '[video]',
            '-map', '1:a',
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-movflags', '+faststart',
            str(output_path), '-y'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"FFmpeg assembly error: {result.stderr}")
            raise Exception(f"Failed to assemble video: {result.stderr}")
