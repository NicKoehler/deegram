from __future__ import annotations

from typing import TYPE_CHECKING

import deethon
import requests
from telethon import events, Button
from json.decoder import JSONDecodeError
from telethon.tl.types import DocumentAttributeAudio

from .. import bot, users, deezer
from ..helper.download_status import DownloadStatus
from ..helper.upload_status import UploadStatus
from ..utils import translate
from ..utils.fast_download import upload_file
from ..utils.bot_utils import get_italian_date_format

if TYPE_CHECKING:
    from typing import Union
    from telethon.tl.patched import Message
    from telethon.events import NewMessage


@bot.on(events.NewMessage(pattern=r"https?://(?:www\.)?deezer\.com/(?:\w+/)?track/(\d+)"))
async def track_link(event: Union[NewMessage.Event, Message]):

    if users[event.chat_id]["downloading"]:
        await event.reply(translate.USER_IS_DOWNLOADING)
        raise events.StopPropagation

    try:
        track = deethon.Track(event.pattern_match.group(1))
    except deethon.errors.DeezerApiError:
        await event.reply("Traccia non trovata.")
        raise events.StopPropagation
    await event.respond(
        translate.TRACK_MSG.format(
            track.title,
            track.artist,
            track.album.title,
            get_italian_date_format(track.release_date)
        ),
        file=track.album.cover_xl)
    quality = users[event.chat_id]["quality"]
    users[event.chat_id]["downloading"] = True
    download_status = DownloadStatus(event)
    await download_status.start()
    file = await bot.loop.run_in_executor(None, deezer.download_track, track, quality, download_status.progress)
    await download_status.finished()
    file_ext = ".mp3" if quality.startswith("MP3") else ".flac"
    file_name = track.artist + " - " + track.title + file_ext
    upload_status = UploadStatus(event)
    await upload_status.start()
    async with bot.action(event.chat_id, 'audio'):
        uploaded_file = await upload_file(
            file_name=file_name,
            client=bot,
            file=open(file, 'rb'),
            progress_callback=upload_status.progress,
        )
        await upload_status.finished()
        await bot.send_file(
            event.chat_id,
            uploaded_file,
            thumb=track.album.cover_medium,
            attributes=[
                DocumentAttributeAudio(
                    voice=False,
                    title=track.title,
                    duration=track.duration,
                    performer=track.artist,
                )
            ],
        )
    await event.reply(translate.END_MSG)
    users[event.chat_id]["downloading"] = False
    raise events.StopPropagation


@bot.on(events.NewMessage(pattern=r"https?://(?:www\.)?deezer\.com/(?:\w+/)?(album|playlist)/(\d+)"))
async def track_link(event: Union[NewMessage.Event, Message]):

    if users[event.chat_id]["downloading"]:
        await event.reply(translate.USER_IS_DOWNLOADING)
        raise events.StopPropagation
    
    # if is an album
    if event.pattern_match.group(1) == 'album':
        try:    
            album_playlist = deethon.Album(event.pattern_match.group(2))
        except deethon.errors.DeezerApiError:
            await event.reply("Album non trovato.")
            raise events.StopPropagation

        await event.respond(
            translate.ALBUM_MSG.format(
                album_playlist.title,
                album_playlist.artist,
                get_italian_date_format(album_playlist.release_date),
                album_playlist.total_tracks,
            ),
            file=album_playlist.cover_xl,
        )

    # if is a playlist
    elif event.pattern_match.group(1) == 'playlist':
        try:
            album_playlist = deethon.Playlist(event.pattern_match.group(2))
        except deethon.errors.DeezerApiError:
            await event.reply("Playlist non trovata.")
            raise events.StopPropagation

        await event.respond(
            translate.PLAYLIST_MSG.format(
                album_playlist.title,
                album_playlist.total_tracks,
            ),
            file=album_playlist.picture_xl,
        )

    quality = users[event.chat_id]["quality"]
    users[event.chat_id]["downloading"] = True

    for num, track in enumerate(album_playlist.tracks):
        if users[event.chat_id]["stopped"]:
            users[event.chat_id]['stopped'] = False
            break
        download_status = DownloadStatus(event, num + 1, album_playlist.total_tracks)
        await download_status.start()
        file = await bot.loop.run_in_executor(None, deezer.download_track, track, quality, download_status.progress)

        if not file:
            await bot.send_message(event.chat_id, f"Non posso scaricare\n{track.artist} - {track.title}")
            await download_status.finished()
            continue

        await download_status.finished()
        file_ext = ".mp3" if quality.startswith("MP3") else ".flac"
        file_name = track.artist + " - " + track.title + file_ext
        upload_status = UploadStatus(event, num + 1, album_playlist.total_tracks)
        await upload_status.start()
        
        async with bot.action(event.chat_id, 'audio'):
            uploaded_file = await upload_file(
                file_name=file_name,
                client=bot,
                file=open(file, 'rb'),
                progress_callback=upload_status.progress,
            )
            await upload_status.finished()
            await bot.send_file(
                event.chat_id,
                uploaded_file,
                thumb=track.album.cover_medium,
                attributes=[
                    DocumentAttributeAudio(
                        voice=False,
                        title=track.title,
                        duration=track.duration,
                        performer=track.artist,
                    )
                ],
            )

    await event.reply(translate.END_MSG)
    users[event.chat_id]["downloading"] = False
    raise events.StopPropagation


@bot.on(events.NewMessage(pattern=r"(.+)?(https?://www\.youtube\.com/watch\?v=.+)"))
async def youtube_link(event: Union[NewMessage.Event, Message]):

    if users[event.chat_id]["downloading"]:
        await event.reply(translate.USER_IS_DOWNLOADING)
        raise events.StopPropagation

    par = {"format": "json", "url": event.pattern_match.group(2)}
    try:
        track_name = requests.get("https://www.youtube.com/oembed", par).json()['title']

        await event.respond("Vuoi cercare questa canzone? Tocca il tasto qui sotto", buttons=[
            [Button.switch_inline(translate.SEARCH_TRACK, query=track_name, same_peer=True)]
        ])
        raise events.StopPropagation

    except JSONDecodeError:
        pass