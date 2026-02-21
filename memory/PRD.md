# Legyenez - YouTube Shorts Video Factory

## Original Problem Statement
Video generation platform for YouTube Shorts in the German faith niche. Features include:
- AI script generation with ML optimization
- ElevenLabs TTS with word timestamps
- Pexels B-roll video search and download
- FFmpeg video assembly with karaoke subtitles
- Multi-language UI support (HU, DE, EN, PL, NL)

## Core Requirements
1. **Script Generator**: AI-powered German faith-niche scripts with ML optimization
2. **Video Factory**: Complete video pipeline (TTS + B-roll + karaoke subtitles)
3. **Hook Library**: Performance-tracked hook collection
4. **Analytics**: CSV import from Notion, performance metrics
5. **Multi-language (i18n)**: Full support for Hungarian, German, English, Polish, Dutch

## User Personas
- German faith content creators
- YouTube Shorts producers
- Multi-language European audience

## Architecture
- **Frontend**: React + TailwindCSS + shadcn/ui
- **Backend**: FastAPI + MongoDB
- **External APIs**: OpenAI Whisper, ElevenLabs TTS, Pexels Videos

## What's Been Implemented

### Completed (2026-02-21)
- [x] **Translations (i18n) Fix** - All translation keys for EN, PL, NL languages added to LanguageContext.js
  - Script Generator page fully translates to all 5 languages
  - Navigation sidebar, form labels, buttons, messages all translated
  
- [x] **Karaoke Subtitle Effect Fix** - Complete rewrite of create_karaoke_subtitles()
  - Only the CURRENTLY spoken word is YELLOW
  - All other words remain WHITE
  - Proper ASS format with inline color overrides
  - 6 unit tests passing

### Previously Completed
- [x] OpenAI Whisper integration for word-level timestamps
- [x] ElevenLabs TTS with voice settings and speed control
- [x] Pexels B-roll search with quality filters
- [x] FFmpeg video assembly pipeline
- [x] Script editing before video generation
- [x] Voice preferences save/load
- [x] Mobile-responsive dashboard grid

## Prioritized Backlog

### P0 (Critical)
- [ ] **Full-site i18n** - Translate remaining pages (VideoFactory, HookLibrary, Analytics, Settings)
- [ ] **End-to-end video generation test** - Verify complete pipeline works with new karaoke effect

### P1 (Important)
- [ ] ElevenLabs "first variation" verification with static seed
- [ ] Subtitle styling refinement (font size, shadow blur, centering)

### P2 (Nice to have)
- [ ] Pexels quality filter improvements
- [ ] Background music integration testing

## API Keys (stored in backend/.env)
- OPENAI_API_KEY (Whisper)
- ELEVENLABS_API_KEY
- PEXELS_API_KEY

## Key Files
- `/app/frontend/src/contexts/LanguageContext.js` - All translations
- `/app/backend/services/ffmpeg_service.py` - Video/subtitle assembly
- `/app/backend/services/video_service.py` - Video generation pipeline

## Test Files
- `/app/backend/tests/test_karaoke_subtitles.py` - 6 unit tests for subtitle generation
