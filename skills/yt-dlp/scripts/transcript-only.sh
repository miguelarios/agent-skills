#!/bin/bash
# Download transcript only (no video) from YouTube
# Usage: ./transcript-only.sh <URL> [format]
# Formats: vtt (default), srt, json3

URL="$1"
FORMAT="${2:-vtt}"  # Default to VTT if not specified

if [ -z "$URL" ]; then
  echo "Usage: $0 <URL> [format]"
  echo "Formats: vtt (default), srt, json3"
  exit 1
fi

yt-dlp --write-auto-subs --skip-download --sub-lang en --sub-format "$FORMAT" -o "%(title)s" "$URL"

echo "✓ Transcript downloaded as $FORMAT"
