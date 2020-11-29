from abc import ABC
from tempfile import NamedTemporaryFile
from typing import Optional

from httpx import AsyncClient
from moviepy.editor import AudioFileClip, VideoFileClip  # pylint: disable=import-error

from rvg.constants import REDDIT_HOST, USER_AGENT_HEADER


class RedditEntry(ABC):

    def __init__(
        self,
        dash_id: str,
        entry_id: str,
    ):
        self.entry_id = entry_id
        self.name = entry_id.split('DASH_')[1] if 'DASH_' in entry_id else entry_id

        self.entry_size: Optional[int] = None

        self._client = AsyncClient(base_url=f'https://{REDDIT_HOST}/{dash_id}', headers=USER_AGENT_HEADER)

    @classmethod
    async def make(
        cls,
        dash_id: str,
        entry_id: str,
    ) -> 'cls':
        self = cls(dash_id, entry_id)
        await self.read_entry_size()
        return self

    async def read_entry_size(self) -> int:
        response = await self._client.head(self.entry_id)
        response.raise_for_status()
        self.entry_size = int(response.headers['Content-Length'])
        return self.entry_size

    async def read_entry_data(self) -> bytes:
        response = await self._client.get(self.entry_id)
        response.raise_for_status()
        return response.read()


class RedditAudio(RedditEntry):
    ...


class RedditVideo(RedditEntry):

    def __init__(self, dash_id: str, entry_id: str, audio: Optional[RedditAudio] = None):
        super().__init__(dash_id, entry_id)
        self.audio: Optional[RedditAudio] = audio

    @property
    async def size(self) -> Optional[int]:
        video_size: Optional[int] = None
        if self.entry_size:
            video_size = self.entry_size
            if self.audio:
                audio_size = self.audio.entry_size if self.audio.entry_size else await self.audio.read_entry_size()
                video_size += audio_size
        return video_size

    async def download(self) -> bytes:

        video_data = await self.read_entry_data()
        if not self.audio:
            return video_data

        with NamedTemporaryFile(
                prefix='rvg_video_',
                suffix='.mp4',
        ) as video_temp, NamedTemporaryFile(
                prefix='rvg_audio_',
                suffix='.mp4',
        ) as audio_temp, NamedTemporaryFile(
                prefix='rvg_output_',
                suffix='.mp4',
        ) as output_temp:

            video_temp.write(video_data)
            audio_temp.write(await self.audio.read_entry_data())

            my_clip = VideoFileClip(video_temp.name)
            audio_background = AudioFileClip(audio_temp.name)
            final_clip = my_clip.set_audio(audio_background)
            final_clip.write_videofile(output_temp.name)
            return output_temp.read()
