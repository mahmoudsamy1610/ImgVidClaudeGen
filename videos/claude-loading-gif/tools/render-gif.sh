#!/usr/bin/env bash
# Renders claude-loading.gif at an even 50 fps (every frame 2/100 s).
# The HyperFrames GIF output caps the frame rate and mixes 3/100 s and 4/100 s
# frame delays, which looks slightly jerky, so this renders PNG frames and
# encodes the GIF with FFmpeg using one shared palette and no dithering.
# Run from videos/claude-loading-gif/. Needs Node and FFmpeg.
set -euo pipefail
cd "$(dirname "$0")/.."
frames="$(mktemp -d)"
trap 'rm -rf "$frames"' EXIT
npx --yes hyperframes@0.8.106 render --format png-sequence --fps 50 --output "$frames/png"
ffmpeg -v error -y -framerate 50 -i "$frames/png/frame_%06d.png" \
  -vf "palettegen=max_colors=128:stats_mode=full:reserve_transparent=0" "$frames/palette.png"
ffmpeg -v error -y -framerate 50 -i "$frames/png/frame_%06d.png" -i "$frames/palette.png" \
  -lavfi "paletteuse=dither=none:diff_mode=rectangle" -loop 0 claude-loading.gif
echo "wrote $(pwd)/claude-loading.gif"
