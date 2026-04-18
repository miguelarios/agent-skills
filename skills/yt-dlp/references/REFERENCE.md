# yt-dlp Reference

## Format Selection

### Format Strings

Format strings select video/audio qualities:
- `bestvideo+bestaudio` - Best of each, merge
- `bestvideo[height<=1080]+bestaudio` - Limit to 1080p
- `bestvideo[height<=720]+bestaudio` - Limit to 720p
- `bestvideo[ext=mp4]+bestaudio` - Prefer MP4 container
- `bestvideo[fps<=30]+bestaudio` - Limit to 30fps

### Common Format IDs

From `yt-dlp -F <URL>`:
- `137+140` - 1080p video + best audio
- `22+140` - 720p video + best audio
- `18+140` - 360p video + best audio
- `137` - 1080p video only
- `140` - Best audio (m4a)

### Container Formats

- `--merge-output-format mp4` - Force MP4 after merge
- `--merge-output-format mkv` - Force MKV after merge
- `--merge-output-format webm` - Force WebM after merge

## Subtitle Formats

### Format Types

- `vtt` - WebVTT (easiest for parsing)
- `srt` - SubRip (most human-readable)
- `ass` - Advanced SSA (supports styling)
- `json3` - JSON with word-level timestamps (best for LLMs)
- `srv1/srv2/srv3` - JSON transcript formats

### Language Selection

- `--sub-lang en` - English only
- `--sub-lang en,es` - English and Spanish
- `--sub-lang all` - All available
- `--all-subs` - Download all languages

### Subtitle Types

- `--write-subs` - Manual subtitles only
- `--write-auto-subs` - Auto-generated (ASR) subtitles
- Both flags together - Download both types

## Audio Options

### Audio Formats

- `--audio-format mp3` - MP3 output
- `--audio-format m4a` - M4A output
- `--audio-format wav` - WAV output
- `--audio-format best` - Best available

### Audio Quality

- `--audio-quality 0` - Best quality
- `--audio-quality 5` - Higher quality (smaller file)
- `--audio-quality 9` - Lowest quality (smallest file)

## Output Templates

### All Template Variables

- `%(id)s` - Video ID
- `%(title)s` - Video title
- `%(uploader)s` - Channel name
- `%(uploader_id)s` - Channel ID
- `%(playlist_id)s` - Playlist ID
- `%(playlist_index)s` - Position in playlist
- `%(ext)s` - File extension
- `%(autonumber)s` - Auto-incrementing number
- `%(duration)s` - Duration in seconds
- `%(view_count)s` - View count
- `%(like_count)s` - Like count
- `%(upload_date)s` - YYYYMMDD
- `%(release_date)s` - Release date
- `%(timestamp)s` - Unix timestamp

### Template Formatting

```bash
# Zero-pad playlist index (3 digits)
"%(playlist_index)03d - %(title)s.%(ext)s"

# Custom date format
"%(upload_date)s - %(title)s.%(ext)s"

# Sanitized filename (safe for filesystems)
"%(title).%(ext)s" --restrict-filenames
```

## Cookie & Authentication

### Browser Cookies

```bash
--cookies-from-browser chrome    # Chrome
--cookies-from-browser firefox   # Firefox
--cookies-from-browser safari    # Safari
--cookies-from-browser edge      # Edge
--cookies-from-browser brave     # Brave
```

### Cookie File

```bash
--cookies cookies.txt           # From Netscape cookie file
--cookies-from-browser chrome    # Auto-extract
```

### Authentication

```bash
--username "user"
--password "pass"
--two-factor "code"
--netrc                           # Use .netrc file
```

## Download Options

### Rate Limiting

```bash
--rate-limit 2M                 # 2 MB/s max
--rate-limit 500K                 # 500 KB/s max
--limit-rate 2M                   # Same as rate-limit
```

### Concurrency

```bash
--concurrent-fragments 4           # Download 4 fragments at once
--playlist-end 5                  # Download first 5 items
--playlist-start 10                # Start from item 10
```

### Retry & Timeout

```bash
--retries 10                     # Retry 10 times
--fragment-retries 10              # Retry fragments
--socket-timeout 30               # 30 second timeout
```

## Video Sections

### Section Formats

```bash
--download-sections "*00:01:00-00:05:00"       # 1:00 to 5:00
--download-sections "*10:00-15:00"             # 10 to 15 minutes
--download-sections "00:00:00-00:00:30+00:01:00-00:01:30"  # Multiple sections
```

Requires ffmpeg installed.

## File Management

### Filename Sanitization

```bash
--restrict-filenames          # Remove unsafe characters
--no-overwrites              # Skip existing files
--force-overwrites            # Overwrite existing
--continue                   # Resume partial downloads
```

### Organization

```bash
# By uploader (subdirectories)
-o "%(uploader)s/%(title)s.%(ext)s"

# By playlist
-o "%(playlist_title)s/%(playlist_index)03d - %(title)s.%(ext)s"

# By date
-o "%(upload_date[0:4]/%(upload_date[4:2]/%(title)s.%(ext)s"
```

## Post-Processing

### Embedded Metadata

```bash
--embed-metadata           # Embed metadata in file
--embed-thumbnail          # Embed thumbnail
--embed-subs              # Embed subtitles
--embed-chapters           # Embed chapter markers
```

### Post-Processing Commands

```bash
--postprocessor-args "ffmpeg:-metadata title='My Title'"
--exec "echo 'Downloaded: %(filename)s'"
```

## Troubleshooting

### ffmpeg Errors

If merging fails with "ffmpeg not found":
```bash
# Install ffmpeg
apt-get install ffmpeg        # Debian/Ubuntu
brew install ffmpeg         # macOS
```

### Geo-restricted Content

```bash
--geo-bypass               # Bypass geo-restriction
--proxy socks5://127.0.0.1:1080  # Use proxy
```

### Age-gated Content

```bash
--cookies-from-browser chrome
--username "user" --password "pass"
--two-factor "code"
```

### Slow Downloads

```bash
--external-downloader aria2c    # Use aria2c for faster
--concurrent-fragments 8        # More concurrency
--buffer-size 16K              # Larger buffer
```
