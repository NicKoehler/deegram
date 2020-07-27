from __future__ import annotations

from typing import TYPE_CHECKING

import deethon
from telethon import events
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
    raise events.StopPropagation


@bot.on(events.NewMessage(pattern=r"https?://(?:www\.)?deezer\.com/(?:\w+/)?album/(\d+)"))
async def album_link(event: Union[NewMessage.Event, Message]):
    try:
        album = deethon.Album(event.pattern_match.group(1))
    except deethon.errors.DeezerApiError:
        await event.respond("Non trovato")
        raise events.StopPropagation

    await event.respond(
        translate.ALBUM_MSG.format(
            album.title,
            album.artist,
            get_italian_date_format(album.release_date),
            album.total_tracks,
        ),
        file=album.cover_xl,
    )

    quality = users[event.from_id]["quality"]
    msg = await event.reply(translate.DOWNLOAD_MSG)
    tracks = deezer.download_album(album, quality, stream=True)
    await msg.delete()
    async with bot.action(event.chat_id, "audio"):
        for num, track in enumerate(tracks):

            if not track:
                await bot.send_message(event.chat_id, f"Non posso scaricare\n{album.artist} - {album.tracks[num].title}")
                continue

            file_ext = ".mp3" if quality.startswith("MP3") else ".flac"
            file_name = f"{album.artist} - {album.tracks[num].title}{file_ext}"
            upload_status = UploadStatus(event, num + 1, album.total_tracks)
            await upload_status.start()
            r = await upload_file(
                file_name=file_name,
                client=bot,
                file=open(track, 'rb'),
                progress_callback=upload_status.progress
            )
            await upload_status.finished()
            await bot.send_file(
                event.chat_id,
                r,
                attributes=[
                    DocumentAttributeAudio(
                        voice=False,
                        title=album.tracks[num].title,
                        duration=album.tracks[num].duration,
                        performer=album.artist,
                    )
                ],
            )
            await msg.delete()

    await event.reply(translate.END_MSG)
    raise events.StopPropagation


@bot.on(events.NewMessage(pattern=r"https?://(?:www\.)?deezer\.com/(?:\w+/)?playlist/(\d+)"))
async def playlist_link(event: Union[NewMessage.Event, Message]):
    try:

        playlist = deethon.Playlist(event.pattern_match.group(1))
    except deethon.errors.DeezerApiError:
        await event.respond("Non trovato")
        raise events.StopPropagation

    await event.respond(
        translate.PLAYLIST_MSG.format(
            playlist.title,
            playlist.nb_tracks,
        ),
        file=playlist.picture_xl,
    )

    quality = users[event.from_id]["quality"]
    msg = await event.reply(translate.DOWNLOAD_MSG)
    tracks = deezer.download_playlist(playlist, quality, stream=True)

    await msg.delete()
    async with bot.action(event.chat_id, "audio"):
        for num, track in enumerate(tracks):
            if not track:
                await bot.send_message(event.chat_id, f"Non posso scaricare\n{playlist.tracks[num].artist} - {playlist.tracks[num].title}")
                continue
            file_ext = ".mp3" if quality.startswith("MP3") else ".flac"
            file_name = f"{playlist.tracks[num].artist} - {playlist.tracks[num].title}{file_ext}"
            upload_status = UploadStatus(event, num + 1, playlist.nb_tracks)
            await upload_status.start()
            r = await upload_file(
                file_name=file_name,
                client=bot,
                file=open(track, 'rb'),
                progress_callback=upload_status.progress
            )
            await upload_status.finished()
            await bot.send_file(
                event.chat_id,
                r,
                attributes=[
                    DocumentAttributeAudio(
                        voice=False,
                        title=playlist.tracks[num].title,
                        duration=playlist.tracks[num].duration,
                        performer=playlist.tracks[num].artist,
                    )
                ],
            )
            await msg.delete()

    await event.reply(translate.END_MSG)
    raise events.StopPropagation