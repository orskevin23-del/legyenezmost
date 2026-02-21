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
                '-vf', 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30',
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
        Create ASS subtitle file with PROPER karaoke effect.
        
        REQUIREMENTS:
        - Only the CURRENTLY spoken word is YELLOW
        - All other words (before AND after) are WHITE
        - NO black boxes - just soft shadow
        - CENTERED at bottom of screen
        """
        # ASS header - CLEAN styling without boxes
        # Key settings:
        # - Alignment=5: MIDDLE CENTER (perfect center like Canva)
        # - PlayResX/Y: 1080x1920 (portrait Full HD)
        # - FontSize=50
        ass_content = """[Script Info]
Title: Karaoke Subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,50,&H00FFFFFF,&H00FFFFFF,&H40000000,&H00000000,1,0,0,0,100,100,0,0,1,2,3,5,20,20,0,1

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
            for i, ts in enumerate(word_timestamps):
                if isinstance(ts, dict) and 'word' in ts:
                    word_timings.append({
                        'word': ts['word'],
                        'start': ts.get('start', 0),
                        'end': ts.get('end', duration)
                    })
                elif isinstance(ts, dict) and 'character' in ts:
                    end_time = ts.get('end_time_ms', duration * 1000) / 1000.0
                    if 'end_time_ms' not in ts and i < len(word_timestamps) - 1:
                        end_time = word_timestamps[i+1].get('start_time_ms', duration * 1000) / 1000.0
                    word_timings.append({
                        'word': ts['character'],
                        'start': ts.get('start_time_ms', 0) / 1000.0,
                        'end': end_time
                    })
        
        # Fallback: distribute evenly
        if not word_timings:
            word_duration = duration / len(words) if words else 1.0
            for i, word in enumerate(words):
                word_timings.append({
                    'word': word,
                    'start': i * word_duration,
                    'end': (i + 1) * word_duration
                })
        
        # Group words (4-5 per line)
        groups = []
        current_group = []
        for wt in word_timings:
            current_group.append(wt)
            if len(current_group) >= 4:
                groups.append(current_group)
                current_group = []
        if current_group:
            groups.append(current_group)
        
        # Generate dialogue - each word gets its own line showing the WHOLE group
        # with ONLY that word highlighted
        for group in groups:
            for idx, current_word in enumerate(group):
                word_start = current_word['start']
                word_end = current_word['end']
                
                # Build text: current word YELLOW, all others WHITE
                # Using {\c&HBBGGRR&} format
                # YELLOW = &H00FFFF (BGR)
                # WHITE = &HFFFFFF (BGR)
                parts = []
                for i, wt in enumerate(group):
                    if i == idx:
                        # CURRENT word - YELLOW
                        parts.append("{\\c&H00FFFF&}" + wt['word'])
                    else:
                        # Other words - WHITE  
                        parts.append("{\\c&HFFFFFF&}" + wt['word'])
                
                # Add \an5 tag to FORCE middle-center alignment
                line_text = "{\\an5}" + " ".join(parts)
                start = FFmpegService.format_ass_time(word_start)
                end = FFmpegService.format_ass_time(word_end)
                
                ass_content += f"Dialogue: 0,{start},{end},Default,,0,0,0,,{line_text}\n"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(ass_content)
        
        logger.info(f"Created karaoke subtitles: {output_path}")
    
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
        # Force style settings - using \an5 inline for PERFECT CENTER
        # FontSize=55 for better visibility
        force_style = "FontName=Arial,FontSize=55,PrimaryColour=&H00FFFFFF,OutlineColour=&H40000000,BackColour=&H00000000,Bold=1,BorderStyle=1,Outline=2,Shadow=3,MarginL=0,MarginR=0,MarginV=0"
        
        cmd = [
            'ffmpeg',
            '-i', str(video_path),
            '-i', str(audio_path),
            '-i', music_path,
            '-filter_complex',
            (
                f'[1:a]volume=1.0[voice];'
                f'[2:a]volume=0.3[music];'
                f'[voice][music]amix=inputs=2:duration=first:dropout_transition=2[audio];'
                f"[0:v]subtitles={subtitle_path}:force_style='{force_style}'[video]"
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
        # Force style settings - using \an5 inline for PERFECT CENTER
        # FontSize=55 for better visibility
        force_style = "FontName=Arial,FontSize=55,PrimaryColour=&H00FFFFFF,OutlineColour=&H40000000,BackColour=&H00000000,Bold=1,BorderStyle=1,Outline=2,Shadow=3,MarginL=0,MarginR=0,MarginV=0"
        
        cmd = [
            'ffmpeg',
            '-i', str(video_path),
            '-i', str(audio_path),
            '-filter_complex',
            f"[0:v]subtitles={subtitle_path}:force_style='{force_style}'[video]",
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
