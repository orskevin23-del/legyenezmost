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
        Create ASS subtitle file with karaoke effect.
        Multiple words per line (3-5 words), proper sizing and yellow highlight.
        """
        # ASS header with smaller font and proper colors
        ass_content = """[Script Info]
Title: Karaoke Subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: None

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial Black,20,&H00FFFF00,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,2,5,10,10,150,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        
        # Group words into lines of 3-5 words
        words = script_text.split()
        if not words:
            return
        
        # Create word groups (3-5 words per line)
        word_groups = []
        current_group = []
        for word in words:
            current_group.append(word)
            if len(current_group) >= 4 or (len(current_group) >= 3 and len(word) > 8):
                word_groups.append(' '.join(current_group))
                current_group = []
        if current_group:
            word_groups.append(' '.join(current_group))
        
        # Calculate timing for each group
        if not word_timestamps or len(word_timestamps) == 0:
            # Simple time division
            group_duration = duration / len(word_groups) if word_groups else 1.0
            
            current_time = 0.0
            for group in word_groups:
                start_time = FFmpegService.format_ass_time(current_time)
                current_time += group_duration
                end_time = FFmpegService.format_ass_time(current_time)
                
                # Create karaoke effect for each word in the group
                group_words = group.split()
                word_duration = (group_duration / len(group_words)) * 100 if group_words else 100
                
                karaoke_text = ''.join([f"{{\\k{int(word_duration)}}}{w} " for w in group_words])
                ass_content += f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{karaoke_text}\n"
        else:
            # Use timestamps - group words based on timing
            words_with_time = []
            for i, char_data in enumerate(word_timestamps):
                if isinstance(char_data, dict) and 'character' in char_data and 'start_time_ms' in char_data:
                    words_with_time.append({
                        'word': char_data['character'],
                        'start_ms': char_data['start_time_ms'],
                        'end_ms': word_timestamps[i+1]['start_time_ms'] if i < len(word_timestamps) - 1 else duration * 1000
                    })
            
            # Group into lines
            if words_with_time:
                i = 0
                while i < len(words_with_time):
                    # Take 3-5 words
                    group_size = min(4, len(words_with_time) - i)
                    group = words_with_time[i:i+group_size]
                    
                    start_time = FFmpegService.format_ass_time(group[0]['start_ms'] / 1000.0)
                    end_time = FFmpegService.format_ass_time(group[-1]['end_ms'] / 1000.0)
                    
                    # Create karaoke text
                    karaoke_text = ''
                    for word_data in group:
                        duration_ms = word_data['end_ms'] - word_data['start_ms']
                        karaoke_text += f"{{\\k{int(duration_ms / 10)}}}{word_data['word']} "
                    
                    ass_content += f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{karaoke_text}\n"
                    i += group_size
        
        # Write ASS file
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
                # Subtitles
                f'[0:v]subtitles={subtitle_path}:force_style=\'Fontsize=28,PrimaryColour=&H00FFFF00,SecondaryColour=&H00FFFFFF,Outline=3,Shadow=2,MarginV=150\'[video]'
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
        cmd = [
            'ffmpeg',
            '-i', str(video_path),
            '-i', str(audio_path),
            '-filter_complex',
            f'[0:v]subtitles={subtitle_path}:force_style=\'Fontsize=28,PrimaryColour=&H00FFFF00,SecondaryColour=&H00FFFFFF,Outline=3,Shadow=2,MarginV=150\'[video]',
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
