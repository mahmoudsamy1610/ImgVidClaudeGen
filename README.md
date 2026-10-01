# HyperFrameClaude

A [HyperFrames](https://hyperframes.heygen.com) project that renders an HTML composition to MP4. The sample is a 10-second, 1920x1080, 30fps title card: a dark background, a title that fades in, a subtitle that slides up, and a fade-out at the end.

## Edit the video

Everything lives in `index.html`:

- **Text and styling**: the `#title` and `#subtitle` elements and the `<style>` block.
- **Timing and animation**: the GSAP timeline in the `<script>` at the bottom. The third argument of each tween is its start time in seconds.
- **Length, size and frame rate**: the `data-duration`, `data-width`, `data-height` and `data-fps` attributes on `#root`.

Preview your changes live in the browser with:

```bash
npm run dev
```

Before rendering, run the composition checks:

```bash
npx hyperframes lint    # static checks only
npm run check           # lint plus runtime, layout, motion and contrast checks
```

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
