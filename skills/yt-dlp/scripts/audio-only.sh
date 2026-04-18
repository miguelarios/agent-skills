#!/bin/bash
# Download audio only from YouTube
# Usage: ./audio-only.sh <URL> [format]
# Formats: mp3 (default), m4a, wav, best

URL="$1"
FORMAT="${2:-mp3}"  # Default to MP3 if not specified

if [ -z "$URL" ]; then
  echo "Usage: $0 <URL> [format]"
  echo "Formats: mp3 (default), m4a, wav, best"
  exit 1
fi

yt-dlp -x --audio-format "$FORMAT" --audio-quality 0 -o "%(title)s.%(ext)s" "$URL"

echo "✓ Audio downloaded as $FORMAT"
