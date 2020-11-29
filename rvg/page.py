from logging import getLogger
from typing import Optional, List
from urllib.parse import urlparse
from xml.etree import ElementTree

from httpx import AsyncClient

from rvg.constants import USER_AGENT_HEADER, REDDIT_HOST
from rvg.entries import RedditVideo, RedditAudio

logger = getLogger(__name__)

# <meta property="twitter:title" content="r/AnimalsBeingBros - The Best Good Boy With Two Legs" />


class RedditPage:

    def __init__(self, url: str):
        self.url = url
        self.client = AsyncClient(headers=USER_AGENT_HEADER)

    def _parse_dash_playlist(
        self,
        dash_playlist_raw: str,
    ) -> List[str]:
        xml_tree = ElementTree.fromstring(dash_playlist_raw)
        dash_scheme = '{urn:mpeg:dash:schema:mpd:2011}'

        representations = xml_tree.findall(
            f'{dash_scheme}Period/{dash_scheme}AdaptationSet/{dash_scheme}Representation/{dash_scheme}BaseURL')
        if representations:
            return list(base.text for base in representations)
        return list()

    async def read_dash_id(self) -> Optional[str]:
        parsed_url = urlparse(self.url)
        data_url = f'{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}.json'
        response = await self.client.get(url=data_url)
        response.raise_for_status()
        json_data = response.json()
        for data in json_data:
            for child in data['data']['children']:
                if not child['data'].get('media') or not child['data']['media'].get('reddit_video'):
                    continue
                dash_url = child['data']['media']['reddit_video'].get('dash_url')
                if dash_url:
                    parsed_dash_url = urlparse(dash_url)
                    return parsed_dash_url.path.strip('/').split('/')[0]
        return None

    async def videos_entries(self) -> List[RedditVideo]:
        parsed_url = urlparse(self.url)
        dash_id = await self.read_dash_id()
        response = await self.client.get(f'{parsed_url.scheme}://{REDDIT_HOST}/{dash_id}/DASHPlaylist.mpd')
        response.raise_for_status()
        dash_entries = self._parse_dash_playlist(response.text)

        audio_entry = None
        video_entries: List[RedditVideo] = []

        for entry_id in dash_entries:
            if 'audio' in entry_id:
                audio_entry = await RedditAudio.make(dash_id=dash_id, entry_id=entry_id)
                continue
            video_entries.append(await RedditVideo.make(dash_id=dash_id, entry_id=entry_id))

        if audio_entry:
            for video_entry in video_entries:
                video_entry.audio = audio_entry

        return video_entries
