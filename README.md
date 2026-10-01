# HyperFrameClaude

A [HyperFrames](https://hyperframes.heygen.com) project that renders an HTML composition to MP4.

The current video is **Benny the Snail's Big Delivery**, a 58-second narrated children's story at 1920x1080 and 30fps. Benny, the slowest snail in the garden, has to deliver a birthday leaf before sunset. Rabbit and Squirrel race ahead but get distracted, and Benny arrives just in time.

## Edit the video

- **`index.html`** is the timeline. It places the scenes, the narration clips, the sound effects and the music. Each clip's `data-start` and `data-duration` set when it plays, in seconds.
- **`compositions/world.html`** is the garden backdrop that runs under the whole story. The sun sets and the sky turns from day to sunset to dusk.
- **`compositions/s1-title.html` to `s8-end.html`** are the eight scenes. Each one holds its characters (drawn as inline SVG), speech-bubble text, and a GSAP timeline whose times are relative to the start of that scene.

Preview your changes live in the browser with:

```bash
npm run dev
```

Before rendering, run the composition checks:

```bash
npx hyperframes lint    # static checks only
npm run check           # lint plus runtime, layout, motion and contrast checks
```

### Sound

| Track | Files | Notes |
| --- | --- | --- |
| Narration | `assets/audio/narration/s1.mp3` to `s8.mp3` | One clip per scene, text in `story/narration.tsv` |
| Sound effects | `assets/audio/sfx/` | Chime, pop, sparkle and whoosh, timed to story moments |
| Music | `assets/audio/music/musicbox.mp3` | Original tune made by `story/musicbox.py` |

The music automatically dips under the narration. To change a narration line, edit `story/narration.tsv` and regenerate that clip:

```bash
pip install kokoro-onnx soundfile    # one-time, for the local voice model
npx hyperframes tts "New line here." -v bf_emma -s 0.92 -o s2.wav
ffmpeg -i s2.wav -ac 1 -b:a 96k assets/audio/narration/s2.mp3
```

If the new clip is a different length, update its `data-duration` in `index.html` (and the scene's length if needed). Then refresh the music dip by running `carve.mjs` from the `hyperframes-audio` skill (`node <skill>/scripts/carve.mjs --comp index.html --bed music-bed`), or by re-running the carve in Studio. Audio sources and licenses are listed in `assets/audio/CREDITS.md`.

## Render locally

You need Node 22+ and FFmpeg (`brew install ffmpeg` or `sudo apt install ffmpeg`).

```bash
npx hyperframes render --quality draft --output draft.mp4   # quick preview
npx hyperframes render --quality high --output video.mp4    # final quality
```

`npm run render` renders with the project's pinned CLI version into `renders/`. Rendered videos and `renders/` are git-ignored.

## Render on GitHub Actions

The workflow in `.github/workflows/render.yml` lints the composition, renders `video.mp4` at high quality, and uploads it as a workflow artifact. It runs in two cases:

- **Manually**: on the repo's **Actions** tab, pick **Render video**, then **Run workflow**.
- **On a version tag**: push a tag that starts with `v`. The video is also attached to a GitHub Release for that tag.

  ```bash
  git tag v1.0.0
  git push origin v1.0.0
  ```

## Download the MP4

- **From any run**: open the run on the **Actions** tab and download the `video` artifact under **Artifacts**. GitHub delivers it as a zip that contains `video.mp4`. Artifacts expire after 90 days by default.
- **From a release**: open **Releases** and download `video.mp4` from the release's assets.
