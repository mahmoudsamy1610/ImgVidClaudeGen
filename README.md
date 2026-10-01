# HyperFrameClaude

A [HyperFrames](https://hyperframes.heygen.com) project that renders an HTML composition to MP4.

The current video is **بيني الحلزون والمشوار الكبير** (Benny the Snail's Big Delivery), a 98-second children's story narrated in Egyptian Arabic, at 1920x1080 and 30fps. Benny, the slowest snail in the garden, has to deliver a birthday leaf before sunset. Rabbit and Squirrel race ahead but get distracted, and Benny arrives just in time.

## Edit the video

- **`index.html`** is the timeline. It places the scenes, the narration clips, the sound effects and the music. Each clip's `data-start` and `data-duration` set when it plays, in seconds.
- **`compositions/world.html`** is the garden backdrop that runs under the whole story. The sun sets and the sky turns from day to sunset to dusk.
- **`compositions/s1-title.html` to `s8-end.html`** are the eight scenes. Each one holds its characters (drawn as inline SVG), the Arabic speech-bubble text (right-to-left, in the bundled Baloo Bhaijaan 2 font), and a GSAP timeline whose times are relative to the start of that scene.

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
| Narration | `assets/audio/narration/s1.mp3` to `s8.mp3` | One clip per scene, Egyptian Arabic text in `story/narration.tsv` |
| Sound effects | `assets/audio/sfx/` | Chime, pop, sparkle and whoosh, timed to story moments |
| Music | `assets/audio/music/musicbox.mp3` | Original tune made by `story/musicbox.py` |

The music automatically dips under the narration.

The narration is generated on GitHub by `.github/workflows/narration.yml`, using Microsoft Edge's Egyptian Arabic voice `ar-EG-SalmaNeural` through the [edge-tts](https://github.com/rany2/edge-tts) tool. Note that edge-tts uses an unofficial interface to Microsoft's read-aloud service. To change a line, edit it in `story/narration.tsv` (one `scene<TAB>text` per line) and push. The workflow regenerates the clips, records their lengths in `story/narration-durations.tsv`, and commits both back to the branch. You can also run it from the **Actions** tab under **Generate narration**.

The workflow's own commit doesn't start a new video render (GitHub doesn't trigger workflows from commits made by workflows), so pull the new clips, check their timing, and push again to render. If a new clip is a different length, update its `data-duration` in `index.html` (and the scene's length if needed). Then refresh the music dip by running `carve.mjs` from the `hyperframes-audio` skill (`node <skill>/scripts/carve.mjs --comp index.html --bed music-bed`), or by re-running the carve in Studio. Audio sources and licenses are listed in `assets/audio/CREDITS.md`.

## Render locally

You need Node 22+ and FFmpeg (`brew install ffmpeg` or `sudo apt install ffmpeg`).

```bash
npx hyperframes render --quality draft --output draft.mp4   # quick preview
npx hyperframes render --quality high --output video.mp4    # final quality
```

`npm run render` renders with the project's pinned CLI version into `renders/`. Rendered videos and `renders/` are git-ignored.

## Render on GitHub Actions

The workflow in `.github/workflows/render.yml` lints the composition, renders `video.mp4` at high quality, and publishes it. It runs in three cases:

- **On every push to any branch.** The video is uploaded as an artifact, and the branch's preview pre-release (`preview-<branch>`, with `/` replaced by `-`) is replaced with the new render. If you push again while a render is still running, the older run is cancelled.
- **Manually.** On the repo's **Actions** tab, pick **Render video**, then **Run workflow**.
- **On a version tag.** Push a tag that starts with `v`. The video is also attached to a GitHub Release for that tag.

  ```bash
  git tag v1.0.0
  git push origin v1.0.0
  ```

## Download the MP4

Every run lists its download links in the run's **Summary** on the **Actions** tab.

- **Latest render of a branch (stable link).** Each branch has a link that always serves its newest render as a plain MP4:

  ```
  https://github.com/mahmoudsamy1610/HyperFrameClaude/releases/download/preview-main/video.mp4
  ```

  For another branch, replace `main` with the branch name, with `/` replaced by `-`. The previews are also listed under **Releases**, marked as pre-releases.
- **A specific run.** Open the run on the **Actions** tab and download the `video` artifact under **Artifacts**. GitHub delivers it as a zip that contains `video.mp4`. Artifacts expire after 90 days by default.
- **A version release.** Open **Releases** and download `video.mp4` from the release's assets.

The repository is private, so all of these links only work for people signed in to GitHub with access to the repo.
