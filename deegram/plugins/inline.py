import logging

from telethon import events
from telethon.tl.types import InputWebDocument

from .. import bot
from ..utils.fetch import fetch_json

logger = logging.getLogger(__name__)


@bot.on(events.InlineQuery)
async def inline(event):
    builder = event.builder
    s = []
    text = event.text

    if text.startswith(".a"):
        album_name = ' '.join(text.split()[1:])
        if not album_name:
            return
        album_name = event.text.replace(".a", "").strip()
        logger.debug(f'Sto cercando l\'album: {album_name}')
        api_search_link = "https://api.deezer.com/search/album?q=" + album_name

        data = await fetch_json(api_search_link)

        for match in data["data"]:
            s += (
                builder.article(
                    title=match["title"],
                    text=match["link"],
                    description=f"Artista: {match['artist']['name']} ({match['nb_tracks']})",
                    thumb=InputWebDocument(
                        url=match["cover_medium"],
                        size=0,
                        mime_type="image/jpeg",
                        attributes=[],
                    ),
                ),
            )

    elif text.startswith(".p"):
        playlist_name = ' '.join(text.split()[1:])
        if len(playlist_name) < 1:
            return
        logger.debug(f'Sto cercando la playlist: {playlist_name}')
        api_search_link = "https://api.deezer.com/search/playlist?q=" + playlist_name

        data = await fetch_json(api_search_link)

        for match in data["data"]:
            s += (
                builder.article(
                    title=match["title"],
                    text=match["link"],
                    description=f"Tracce: {match['nb_tracks']}",
                    thumb=InputWebDocument(
                        url=match["picture_medium"],
                        size=0,
                        mime_type="image/jpeg",
                        attributes=[],
                    ),
                ),
            )

    elif len(text) > 1:

        logger.debug(f'Sto cercando la traccia: {text}')
        api_search_link = "https://api.deezer.com/search?q=" + text

        data = await fetch_json(api_search_link)

        for match in data["data"]:
            s += (
                builder.article(
                    title=match["title"],
                    text=match["link"],
                    description=f"Artista: {match['artist']['name']}\nAlbum: {match['album']['title']}",
                    thumb=InputWebDocument(
                        url=match["album"]["cover_medium"],
                        size=0,
                        mime_type="image/jpeg",
                        attributes=[],
                    ),
                ),
            )
    if s:
        try:
            await event.answer(s)
        except TypeError:
            pass
