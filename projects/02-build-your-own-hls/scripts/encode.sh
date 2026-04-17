#!/bin/bash

# Project 2: HLS Encoding Script
# This script converts a single MP4 into HLS segments in 3 resolutions.

INPUT_FILE=${1:-"../../samples/sample1.mp4"}

if [ ! -f "$INPUT_FILE" ]; then
    echo "❌ Error: Input file not found at $INPUT_FILE"
    echo "Usage: ./encode.sh <input_file.mp4> (or place sample1.mp4 in root samples/)"
    exit 1
fi

OUTPUT_DIR="../output"
mkdir -p "$OUTPUT_DIR"

echo "🎬 Starting HLS Encoding for $INPUT_FILE..."

# 1. Generate 360p (Low), 720p (Medium), and 1080p (High) versions
# -g 48: Ensures a Keyframe every 48 frames (for 2s segments at 24fps)
# -sc_threshold 0: Disables scene change detection for uniform GOP
# -hls_time 2: 2 second segments

ffmpeg -i "$INPUT_FILE" \
  -filter_complex \
  "[0:v]split=3[v1][v2][v3]; \
  [v1]scale=w=640:h=360[v1out]; \
  [v2]scale=w=1280:h=720[v2out]; \
  [v3]scale=w=1920:h=1080[v3out]; \
  [0:a]asplit=3[a1][a2][a3]" \
  -map "[v1out]" -c:v:0 libx264 -b:v:0 800k -maxrate:v:0 856k -bufsize:v:0 1200k \
  -map "[v2out]" -c:v:1 libx264 -b:v:1 2800k -maxrate:v:1 2996k -bufsize:v:1 4200k \
  -map "[v3out]" -c:v:2 libx264 -b:v:2 5000k -maxrate:v:2 5350k -bufsize:v:2 7500k \
  -map "[a1]" -c:a:0 aac -b:a:0 128k \
  -map "[a2]" -c:a:1 aac -b:a:1 128k \
  -map "[a3]" -c:a:2 aac -b:a:2 128k \
  -f hls \
  -hls_time 2 \
  -hls_playlist_type vod \
  -hls_segment_filename "$OUTPUT_DIR/v%v/segment%03d.ts" \
  -master_pl_name master.m3u8 \
  -var_stream_map "v:0,a:0 v:1,a:1 v:2,a:2" \
  "$OUTPUT_DIR/v%v/index.m3u8"

echo "✅ HLS Generation Complete! Check the 'output' directory."
echo "🔗 Serve the folder and open 'master.m3u8' in an HLS-compatible player."
