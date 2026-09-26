# yt-dlp Quick Look Remux

A small [yt-dlp](https://github.com/yt-dlp/yt-dlp) postprocessor plugin
for improving macOS Finder Quick Look compatibility with downloaded
videos.

## The problem

macOS Finder Quick Look handles common MP4 video codecs such as H.264
and HEVC well, but on my Mac, MP4 files containing VP9 or AV1 video
would show Finder thumbnails without playing in Quick Look.

The same VP9/AV1 video streams work when placed in an MKV container with
an appropriate MKV Quick Look handler installed.

Since changing the container does not require video transcoding, yt-dlp
can automatically remux affected downloads from MP4 to MKV with FFmpeg
stream copy. This is fast and does not introduce generation loss.

## Behavior

The postprocessor examines the final file produced by yt-dlp.

  Container   Video codec   Action
  ----------- ------------- -----------------
  MP4         H.264         Leave unchanged
  MP4         HEVC          Leave unchanged
  MP4         VP9           Remux to MKV
  MP4         AV1           Remux to MKV
  Other       Any           Leave unchanged

The plugin recognizes codec identifiers encountered in yt-dlp metadata,
including `vp9`, `vp09...`, `av1`, and `av01...`.

The operation is a **remux, not a transcode**. The existing compressed
video and audio streams are copied into the MKV container.

## Repository structure

``` text
yt-dlp-quicklook-remux/
├── README.md
└── yt_dlp_plugins/
    └── postprocessor/
        └── quicklook.py
```

## Plugin

Create `yt_dlp_plugins/postprocessor/quicklook.py` with:

``` python
from yt_dlp.postprocessor.ffmpeg import FFmpegVideoRemuxerPP


class QuickLookRemuxPP(FFmpegVideoRemuxerPP):
    """Remux VP9/AV1 MP4 files to MKV without transcoding."""

    def __init__(self, downloader=None):
        super().__init__(downloader, preferedformat='mkv')

    def run(self, info):
        ext = (info.get('ext') or '').lower()
        vcodec = (info.get('vcodec') or '').lower()

        needs_remux = (
            ext == 'mp4'
            and vcodec.startswith(('vp9', 'vp09', 'av1', 'av01'))
        )

        if not needs_remux:
            self.to_screen(
                f'Quick Look remux not needed: '
                f'{ext or "unknown"} / {vcodec or "unknown codec"}'
            )
            return [], info

        self.to_screen(
            f'Quick Look compatibility: remuxing '
            f'{vcodec} MP4 to MKV'
        )

        return super().run(info)
```

## Installation

yt-dlp supports plugin packages containing a `yt_dlp_plugins` namespace
directory. On macOS, one recommended user plugin location is:

``` text
~/.config/yt-dlp/plugins/<package-name>/yt_dlp_plugins/
```

Clone or copy this repository so the installed plugin ends up at:

``` text
~/.config/yt-dlp/plugins/quicklook-remux/yt_dlp_plugins/postprocessor/quicklook.py
```

For example:

``` bash
mkdir -p ~/.config/yt-dlp/plugins
cd ~/.config/yt-dlp/plugins
git clone YOUR_REPOSITORY_URL quicklook-remux
```

Run yt-dlp with `-v` to verify discovery. The debug output should
contain something similar to:

``` text
[debug] Post-Processor Plugins: QuickLookRemuxPP
[debug] Plugin directories: .../quicklook-remux/yt_dlp_plugins
```

## yt-dlp configuration

Postprocessor plugins must be enabled with `--use-postprocessor`.

On macOS, yt-dlp's recommended user configuration location is:

``` text
~/.config/yt-dlp/config
```

Example configuration:

``` text
# Use Chrome-compatible requests
--impersonate Chrome

# Use login/session cookies from Safari
--cookies-from-browser safari

# Remux AV1/VP9 MP4s to MKV for Finder Quick Look compatibility
--use-postprocessor QuickLookRemux
```

With this configuration, normal downloads require only:

``` bash
yt-dlp "URL"
```

The plugin is discovered automatically from the standard plugin
directory, so `--plugin-dirs` is not required.

## Verifying the remux

For an actual AV1 or VP9 MP4 download, the postprocessor should report
something similar to:

``` text
[QuickLookRemux] Quick Look compatibility: remuxing av01... MP4 to MKV
[VideoRemuxer] Remuxing video from mp4 to mkv
```

The resulting `.mkv` contains the original compressed media streams;
FFmpeg changes the container rather than re-encoding the video.

You can inspect the resulting streams with:

``` bash
ffprobe "video.mkv"
```

## Why not transcode to H.264?

Transcoding AV1 or VP9 to H.264 produces a more broadly compatible MP4,
but it requires substantially more processing, introduces another lossy
encoding generation, and may require substantially more storage for
comparable quality.

For local storage, keeping the original VP9/AV1 stream and changing only
the container is preferable. When a broadly shareable copy is needed, an
H.264/AAC MP4 can be created separately.

## Quick Look requirement

This plugin solves the **VP9/AV1-in-MP4 container problem** by producing
MKV instead.

It does not itself add MKV support to Finder. If your version of macOS
does not Quick Look MKV files natively, you will still need an
appropriate MKV Quick Look handler.

## Requirements

-   macOS
-   yt-dlp with plugin support
-   FFmpeg and ffprobe
-   An MKV-capable Finder Quick Look handler, if required by your macOS
    setup

Initial setup tested with:

-   Apple Silicon / arm64
-   yt-dlp 2026.07.04
-   Python 3.14.6 arm64
-   FFmpeg 9.0.2 arm64

## Disabling the configuration

yt-dlp supports `--ignore-config` when you want to bypass your normal
configuration for a particular invocation:

``` bash
yt-dlp --ignore-config "URL"
```

## Notes

The plugin intentionally has a narrow scope. It only remuxes an MP4 when
yt-dlp reports a VP9 or AV1 video codec. H.264/HEVC MP4 files and other
containers are left untouched.
