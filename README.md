# yt-dlp Quick Look Remux

A small [yt-dlp](https://github.com/yt-dlp/yt-dlp) postprocessor plugin
that improves macOS Finder Quick Look compatibility with downloaded
videos.

## The problem

On my Mac, Finder Quick Look handles H.264 and HEVC in MP4 normally, but
MP4 files containing VP9 or AV1 can show thumbnails without actually
playing in Quick Look.

The same VP9/AV1 video streams work in an MKV container when an
appropriate MKV Quick Look handler is installed.

This plugin automatically detects those downloads and remuxes them from
MP4 to MKV. FFmpeg copies the existing compressed streams rather than
transcoding them, so the operation is fast and introduces no generation
loss.

## Behavior

  Container   Video codec   Action
  ----------- ------------- -----------------
  MP4         H.264         Leave unchanged
  MP4         HEVC          Leave unchanged
  MP4         VP9           Remux to MKV
  MP4         AV1           Remux to MKV
  Other       Any           Leave unchanged

The plugin recognizes yt-dlp codec identifiers including `vp9`,
`vp09...`, `av1`, and `av01...`.

## Installation

Clone the repository into yt-dlp's user plugin directory:

``` bash
mkdir -p ~/.config/yt-dlp/plugins
cd ~/.config/yt-dlp/plugins
git clone YOUR_REPOSITORY_URL quicklook-remux
```

The resulting plugin should be located at:

``` text
~/.config/yt-dlp/plugins/quicklook-remux/yt_dlp_plugins/postprocessor/quicklook.py
```

yt-dlp will discover the plugin automatically; `--plugin-dirs` is not
required.

## Configuration

Enable the postprocessor in:

``` text
~/.config/yt-dlp/config
```

For example, my configuration is:

``` text
# Use Chrome-compatible requests
--impersonate Chrome

# Use login/session cookies from Safari
--cookies-from-browser safari

# Remux AV1/VP9 MP4s to MKV for Finder Quick Look compatibility
--use-postprocessor QuickLookRemux
```

With that configuration, normal downloads require only:

``` bash
yt-dlp "URL"
```

## Verification

Run yt-dlp with verbose output:

``` bash
yt-dlp -v --simulate "URL"
```

Plugin discovery should appear in the debug output:

``` text
[debug] Post-Processor Plugins: QuickLookRemuxPP
[debug] Plugin directories: .../quicklook-remux/yt_dlp_plugins
```

For an actual AV1 or VP9 MP4 download, the postprocessor should report
something similar to:

``` text
[QuickLookRemux] Quick Look compatibility: remuxing av01... MP4 to MKV
[VideoRemuxer] Remuxing video from mp4 to mkv
```

The resulting MKV retains the original compressed video and audio
streams.

## Quick Look requirement

The plugin does not itself add MKV support to Finder. An appropriate MKV
Quick Look handler is still required if your version/configuration of
macOS does not handle MKV files.

One option is [QuickLook
Video](https://github.com/Marginal/QuickLookVideo), which adds Finder
Quick Look previews and other Finder support for Matroska (`.mkv`) and a
wide range of other non-native media formats and codecs.

With Homebrew, it can be installed with:

``` bash
brew install --cask quicklook-video
```

After installation, run **QuickLook Video** from the Applications folder
and enable its Media Extensions in **System Settings → General → Login
Items & Extensions** if needed.

## Requirements

-   macOS
-   yt-dlp with plugin support
-   FFmpeg and ffprobe
-   An MKV-capable Finder Quick Look handler, if required

Initial setup tested with Apple Silicon, yt-dlp 2026.07.04, Python
3.14.6 arm64, and FFmpeg 9.0.2 arm64.

## Why remux instead of transcode?

Transcoding VP9 or AV1 to H.264 would provide broader compatibility, but
requires substantially more processing, introduces another lossy
encoding generation, and can produce significantly larger files.

For local use, this plugin instead preserves the original VP9/AV1
streams and changes only the container. A separate H.264/AAC copy can be
created when broader sharing compatibility is needed.

## Bypassing the configuration

To run yt-dlp without the normal configuration for a particular
invocation:

``` bash
yt-dlp --ignore-config "URL"
```
