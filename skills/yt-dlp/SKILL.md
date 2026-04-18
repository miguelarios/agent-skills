---
name: yt-dlp
description: Download YouTube videos, audio only, transcripts, subtitles, or playlists with quality control. Use when user asks to: (1) "download from YouTube", "get YouTube audio", "extract transcript/subtitles", "download playlist", or (2) mentions YouTube URL with any media extraction need. Handles format selection, playlist batching, and metadata embedding.
---

# yt-dlp

## Quick Decision Guide

**What do you need?**

- **"Download video"** → Format selection section → Choose quality preset
- **"Audio only"** → Audio downloads section → Pick format
- **"Transcript"** → Subtitles section → Get auto or manual subs
- **"Playlist"** → Advanced section → Playlist commands
- **"Age-gated content"** → Troubleshooting section → Use cookies
- **"Download clip"** → Advanced section → `--download-sections`
- **"Batch URLs"** → Advanced section → Text file downloads

## Prerequisites

- **ffmpeg** - Required for merging video/audio streams and downloading video clips
  - Install: `apt-get install ffmpeg` (Debian/Ubuntu) or `brew install ffmpeg` (macOS)
  - Needed for: Format selection with `+`, `--merge-output-format`, and `--download-sections`

## Common Workflows

### Best Quality Video + Audio
```bash
yt-dlp -f "bestvideo+bestaudio" -o "%(title)s.%(ext)s" <URL>
```

### Audio Only (MP3)
```bash
yt-dlp -x --audio-format mp3 --audio-quality 0 -o "%(title)s.%(ext)s" <URL>
```

### Playlist Audio (Numbered)
```bash
yt-dlp -x --audio-format mp3 -o "%(playlist_index)03d - %(title)s.%(ext)s" <PLAYLIST_URL>
```

## Format Selection

**List available formats first:**
```bash
yt-dlp -F <URL>
```

**Quality presets:**
```bash
# Best overall (merge streams)
yt-dlp -f "bestvideo+bestaudio" <URL>

# 1080p max (MP4)
yt-dlp -f "bestvideo[height<=1080]+bestaudio" --merge-output-format mp4 <URL>

# 720p max
yt-dlp -f "bestvideo[height<=720]+bestaudio" <URL>

# Prefer MP4 container
yt-dlp -f "bestvideo[ext=mp4]+bestaudio" <URL>

# Limit to 30fps
yt-dlp -f "bestvideo[fps<=30]+bestaudio" <URL>
```

**Specific format IDs (from `-F` output):**
```bash
yt-dlp -f 137+140 -o "%(title)s.%(ext)s" <URL>
```

**Common IDs:**
- `137+140` — 1080p video + best audio
- `22+140` — 720p video + best audio
- `137` — 1080p video only
- `140` — Best audio (m4a)

## Subtitles & Transcripts

### Transcript Only (No Video)

**Auto-generated (ASR):**
```bash
yt-dlp --write-auto-subs --skip-download --sub-lang en -o "%(title)s" <URL>
```

**Manual captions:**
```bash
yt-dlp --write-subs --skip-download --sub-lang en -o "%(title)s" <URL>
```

**Format selection:**
```bash
# VTT (programmatically parseable)
yt-dlp --write-auto-subs --skip-download --sub-lang en --sub-format vtt -o "%(title)s" <URL>

# SRT (human-readable)
yt-dlp --write-auto-subs --skip-download --sub-lang en --convert-subs srt -o "%(title)s" <URL>

# JSON3 (word-level timestamps for LLMs)
yt-dlp --write-auto-subs --skip-download --sub-lang en --sub-format json3 -o "%(title)s" <URL>
```

**All languages:**
```bash
yt-dlp --write-auto-subs --skip-download --all-subs -o "%(title)s" <URL>
```

**List available:**
```bash
yt-dlp --list-subs <URL>
```

### Embedded Subtitles

**Download with subtitles embedded:**
```bash
yt-dlp --write-subs --embed-subs --sub-lang en -o "%(title)s.%(ext)s" <URL>
```

**Subtitle types:**
- `--write-subs` — Manual captions
- `--write-auto-subs` — Auto-generated (ASR)
- Both together — Download both types

## Advanced Options

### Video Clips (requires ffmpeg)

```bash
# Single clip
yt-dlp --download-sections "*00:01:00-00:05:00" -o "%(title)s_clip.%(ext)s" <URL>

# Multiple clips
yt-dlp --download-sections "00:00:00-00:00:30+00:01:00-00:01:30" -o "%(title)s_clips.%(ext)s" <URL>
```

### Age-Gated Content

**Browser cookies:**
```bash
yt-dlp --cookies-from-browser chrome -o "%(title)s.%(ext)s" <URL>
```

**Supported:** chrome, firefox, safari, edge, brave

### Batch & Organization

**Batch from text file:**
```bash
yt-dlp -a urls.txt -o "%(uploader)s/%(title)s.%(ext)s"
```

**Organize by uploader:**
```bash
yt-dlp -o "%(uploader)s/%(title)s.%(ext)s" <URL>
```

**Include upload date:**
```bash
yt-dlp -o "%(upload_date)s - %(title)s.%(ext)s" <URL>
```

## Error Handling

**Common issues:**

- `ffmpeg not found` during merge — Install ffmpeg (see Prerequisites)
- `ERROR: unable to download video` — Try `--cookies-from-browser` for age-gated content
- Slow downloads — Add `--rate-limit 2M` or `--concurrent-fragments 4`
- Geo-restricted — Add `--geo-bypass` or use proxy
- **403 Forbidden on embedded streams** — Add Referer/Origin headers (see below)

### Protected Streams (Mux, Vimeo WISTIA, etc.)

Some embedded video players reject direct downloads with 403 Forbidden. Fix by adding browser context headers:

```bash
yt-dlp \
  --add-header "Referer:<page-url-where-video-is-embedded>" \
  --add-header "Origin:<page-domain>" \
  '<video-stream-url>'
```

**Example (Mux stream from Maven):**
```bash
yt-dlp \
  --add-header "Referer:https://maven.com/p/e57c03/..." \
  --add-header "Origin:https://maven.com" \
  'https://stream.mux.com/...m3u8?token=...'
```

**Why this works:** The server checks that requests come from the expected page. Without these headers, it looks like a direct scraper attempt and gets blocked.

## Key Notes

- `--skip-download` — Get transcript/subtitle files without downloading video
- `--write-auto-subs` — Auto-generated captions available on most YouTube videos
- Format formats: `vtt` (programmatically), `srt` (human-readable), `json3` (LLM-optimized)
- Merging: Use `+` to combine streams (requires ffmpeg)
- Merge format: `--merge-output-format mp4` forces MP4 container

## Reference

See [references/REFERENCE.md](references/REFERENCE.md) for detailed format options, output templates, and advanced flags.
