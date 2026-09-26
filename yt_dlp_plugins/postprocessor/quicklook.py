from yt_dlp.postprocessor.ffmpeg import FFmpegVideoRemuxerPP


class QuickLookRemuxPP(FFmpegVideoRemuxerPP):
    """
    Remux MP4 files containing VP9 or AV1 video to MKV for
    better macOS Finder Quick Look compatibility.

    No video or audio transcoding is performed.
    """

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