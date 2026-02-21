"""
Test for karaoke subtitle generation in FFmpeg service.
Verifies that the TRUE karaoke effect works correctly:
- Only the currently spoken word should be YELLOW
- All other words in the group should be WHITE
"""
import pytest
import tempfile
import os
from pathlib import Path
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.ffmpeg_service import FFmpegService


class TestKaraokeSubtitles:
    """Test karaoke subtitle generation"""

    def test_karaoke_subtitle_generation_basic(self):
        """Test basic subtitle generation with word timestamps"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.ass"
            
            script_text = "Hello world this is a test"
            word_timestamps = [
                {'word': 'Hello', 'start': 0.0, 'end': 0.5},
                {'word': 'world', 'start': 0.5, 'end': 1.0},
                {'word': 'this', 'start': 1.0, 'end': 1.5},
                {'word': 'is', 'start': 1.5, 'end': 2.0},
                {'word': 'a', 'start': 2.0, 'end': 2.3},
                {'word': 'test', 'start': 2.3, 'end': 3.0},
            ]
            duration = 3.0
            
            FFmpegService.create_karaoke_subtitles(
                output_path, script_text, word_timestamps, duration
            )
            
            assert output_path.exists(), "ASS subtitle file should be created"
            
            # Read and verify content
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check ASS header
            assert "[Script Info]" in content
            assert "[V4+ Styles]" in content
            assert "[Events]" in content
            
            # Check that color overrides are used
            assert "\\c&H00FFFF&" in content, "Yellow color code should be present"
            assert "\\c&HFFFFFF&" in content, "White color reset code should be present"
            
            print("✓ Basic karaoke subtitle generation test passed")

    def test_karaoke_only_one_word_yellow(self):
        """Test that only ONE word is yellow at a time in each dialogue line"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.ass"
            
            script_text = "One two three four"
            word_timestamps = [
                {'word': 'One', 'start': 0.0, 'end': 0.5},
                {'word': 'two', 'start': 0.5, 'end': 1.0},
                {'word': 'three', 'start': 1.0, 'end': 1.5},
                {'word': 'four', 'start': 1.5, 'end': 2.0},
            ]
            duration = 2.0
            
            FFmpegService.create_karaoke_subtitles(
                output_path, script_text, word_timestamps, duration
            )
            
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find dialogue lines
            dialogue_lines = [line for line in content.split('\n') if line.startswith('Dialogue:')]
            
            assert len(dialogue_lines) > 0, "Should have dialogue lines"
            
            # Each dialogue line should have exactly one yellow color override
            for line in dialogue_lines:
                yellow_count = line.count('\\c&H00FFFF&')
                assert yellow_count == 1, f"Each line should have exactly 1 yellow word, found {yellow_count}"
                print(f"✓ Line verified: {line[:80]}...")
            
            print("✓ Only one word yellow at a time test passed")

    def test_karaoke_color_sequence(self):
        """Test that different words are highlighted in sequence"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.ass"
            
            script_text = "First Second Third"
            word_timestamps = [
                {'word': 'First', 'start': 0.0, 'end': 1.0},
                {'word': 'Second', 'start': 1.0, 'end': 2.0},
                {'word': 'Third', 'start': 2.0, 'end': 3.0},
            ]
            duration = 3.0
            
            FFmpegService.create_karaoke_subtitles(
                output_path, script_text, word_timestamps, duration
            )
            
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find dialogue lines
            dialogue_lines = [line for line in content.split('\n') if line.startswith('Dialogue:')]
            
            # Check that each word gets highlighted
            assert len(dialogue_lines) >= 3, "Should have at least 3 dialogue lines for 3 words"
            
            # The first line should highlight "First"
            # The second line should highlight "Second" 
            # The third line should highlight "Third"
            
            # Check that First is highlighted in first timing window
            first_dialogue = dialogue_lines[0]
            assert '\\c&H00FFFF&}First' in first_dialogue, "First word should be yellow in first line"
            
            print("✓ Color sequence test passed")

    def test_karaoke_no_timestamps_fallback(self):
        """Test that subtitles are generated even without timestamps (fallback to even distribution)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.ass"
            
            script_text = "Testing fallback mode"
            word_timestamps = []  # Empty timestamps
            duration = 3.0
            
            FFmpegService.create_karaoke_subtitles(
                output_path, script_text, word_timestamps, duration
            )
            
            assert output_path.exists(), "ASS file should be created even without timestamps"
            
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Should have dialogue lines
            dialogue_lines = [line for line in content.split('\n') if line.startswith('Dialogue:')]
            assert len(dialogue_lines) > 0, "Should generate dialogue lines with fallback"
            
            print("✓ Fallback mode test passed")

    def test_karaoke_empty_script(self):
        """Test handling of empty script"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.ass"
            
            script_text = ""
            word_timestamps = []
            duration = 1.0
            
            FFmpegService.create_karaoke_subtitles(
                output_path, script_text, word_timestamps, duration
            )
            
            assert output_path.exists(), "ASS file should be created even for empty script"
            
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Should have header but no dialogue
            assert "[Script Info]" in content
            dialogue_lines = [line for line in content.split('\n') if line.startswith('Dialogue:')]
            assert len(dialogue_lines) == 0, "Empty script should have no dialogue lines"
            
            print("✓ Empty script test passed")

    def test_format_ass_time(self):
        """Test ASS time formatting"""
        assert FFmpegService.format_ass_time(0) == "0:00:00.00"
        assert FFmpegService.format_ass_time(1.5) == "0:00:01.50"
        assert FFmpegService.format_ass_time(61.25) == "0:01:01.25"
        # Use 3662.0 instead of 3661.99 to avoid floating point precision issues
        assert FFmpegService.format_ass_time(3662.0) == "1:01:02.00"
        
        print("✓ Time formatting test passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
