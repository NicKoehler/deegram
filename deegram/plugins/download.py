from __future__ import annotations

from typing import TYPE_CHECKING

import deethon
from os import remove
from gazpacho import get, Soup
from gazpacho.get import HTTPError
from telethon import events, Button
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
    try:
        file = await bot.loop.run_in_executor(None, deezer.download_track, track, quality, download_status.progress)
    except deethon.errors.DeezerLoginError:
        await event.reply(translate.LOGIN_ERROR)
        users[event.chat_id]["downloading"] = False
        raise events.StopPropagation
    except Exception as e:
        await event.reply(translate.GENERIC_ERROR)
        users[event.chat_id]["downloading"] = False
        raise events.StopPropagation
    finally:
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
    remove(file)
    raise events.StopPropagation


# @bot.on(events.NewMessage(pattern=r"https?://(?:www\.)?deezer\.com/(?:\w+/)?(album|playlist)/(\d+)"))
# async def album_playlist_link(event: Union[NewMessage.Event, Message]):

#     if users[event.chat_id]["downloading"]:
#         await event.reply(translate.USER_IS_DOWNLOADING)
#         raise events.StopPropagation
    
#     # if is an album
#     if event.pattern_match.group(1) == 'album':
#         try:    
#             album_playlist = deethon.Album(event.pattern_match.group(2))
#         except deethon.errors.DeezerApiError:
#             await event.reply("Album non trovato.")
#             raise events.StopPropagation

#         await event.respond(
#             translate.ALBUM_MSG.format(
#                 album_playlist.title,
#                 album_playlist.artist,
#                 get_italian_date_format(album_playlist.release_date),
#                 album_playlist.total_tracks,
#             ),
#             file=album_playlist.cover_xl,
#         )

#     # if is a playlist
#     elif event.pattern_match.group(1) == 'playlist':
#         try:
#             album_playlist = deethon.Playlist(event.pattern_match.group(2))
#         except deethon.errors.DeezerApiError:
#             await event.delete()
#             await event.reply("Playlist non trovata.")
#             raise events.StopPropagation

#         await event.respond(
#             translate.PLAYLIST_MSG.format(
#                 album_playlist.title,
#                 album_playlist.total_tracks,
#             ),
#             file=album_playlist.picture_xl,
#         )

#     quality = users[event.chat_id]["quality"]
#     users[event.chat_id]["downloading"] = True
#     try:
#         for num, track in enumerate(album_playlist.tracks):
#             if users[event.chat_id]["stopped"]:
#                 users[event.chat_id]['stopped'] = False
#                 break
#             download_status = DownloadStatus(event, num + 1, album_playlist.total_tracks)
#             await download_status.start()
#             file = await bot.loop.run_in_executor(None, deezer.download_track, track, quality, download_status.progress)
#             if not file:
#                 await bot.send_message(event.chat_id, f"Non posso scaricare\n{track.artist} - {track.title}")
#                 await download_status.finished()
#                 continue
#             await download_status.finished()
#             file_ext = ".mp3" if quality.startswith("MP3") else ".flac"
#             file_name = track.artist + " - " + track.title + file_ext
#             upload_status = UploadStatus(event, num + 1, album_playlist.total_tracks)
#             await upload_status.start()
            
#             async with bot.action(event.chat_id, 'audio'):
#                 uploaded_file = await upload_file(
#                     file_name=file_name,
#                     client=bot,
#                     file=open(file, 'rb'),
#                     progress_callback=upload_status.progress,
#                 )
#                 await upload_status.finished()
#                 await bot.send_file(
#                     event.chat_id,
#                     uploaded_file,
#                     thumb=track.album.cover_medium,
#                     attributes=[
#                         DocumentAttributeAudio(
#                             voice=False,
#                             title=track.title,
#                             duration=track.duration,
#                             performer=track.artist,
#                         )
#                     ],
#                 )
#             remove(file)
#         await event.reply(translate.END_MSG)
#     except deethon.errors.DeezerLoginError:
#         await event.reply(translate.LOGIN_ERROR)
#     except deethon.errors.DeezerApiError:
#         await event.reply("Playlist troppo grande.")
#     except Exception as e:
#         await event.reply(translate.GENERIC_ERROR)
#     finally:
#         users[event.chat_id]["downloading"] = False
#         raise events.StopPropagation


@bot.on(events.NewMessage(pattern=r"(.+\s)*(https?://[youtu\.be|www\.youtube\.com/watch\?v=].+)"))
async def youtube_link(event: Union[NewMessage.Event, Message]):

    par = {"format": "json", "url": event.pattern_match.group(2)}

    try:
        track_name = get("https://www.youtube.com/oembed", par)['title']

        await event.respond("Vuoi cercare questa canzone? Tocca il tasto qui sotto", buttons=[
            [Button.switch_inline(translate.SEARCH_TRACK, query=track_name, same_peer=True)]
        ])
        raise events.StopPropagation

    except HTTPError:
        pass

@bot.on(events.NewMessage(pattern=r"(.+\s)*(https?://play\.google\.com/music/preview/.+)"))
async def google_play_link(event: Union[NewMessage.Event, Message]):

    try:
        html = get(event.pattern_match.group(2))

        soup = Soup(html)

        title = soup.find('div', {'class': 'title fade-out'})
        artist = soup.find('div', {'class': 'album-artist fade-out'})
        
        await event.respond(
            "Vuoi cercare questa canzone? Tocca il tasto qui sotto",
            buttons=[
                [Button.switch_inline(
                    translate.SEARCH_TRACK,
                    query='%s - %s' % (title.text, artist.text),
                    same_peer=True
                    )
                ]
            ]
        )
        raise events.StopPropagation
    
    except HTTPError:
        pass











@bot.on(events.NewMessage(pattern=r"https?://(?:www\.)?deezer\.com/(?:\w+/)?(album|playlist)/(\d+)"))
async def album_playlist_link(event: Union[NewMessage.Event, Message]):

    if users[event.chat_id]["downloading"]:
        await event.reply(translate.USER_IS_DOWNLOADING)
        raise events.StopPropagation
    
    method = event.pattern_match.group(1)

    # if is an album
    if method == 'album':
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
    elif method == 'playlist':
        try:
            album_playlist = deethon.Playlist(event.pattern_match.group(2))
        except deethon.errors.DeezerApiError:
            await event.delete()
            await event.reply("Playlist non trovata.")
            raise events.StopPropagation

        await event.respond(
            translate.PLAYLIST_MSG.format(
                album_playlist.title,
                album_playlist.total_tracks,
            ),
            file=album_playlist.picture_xl,
        )

    users[event.chat_id]["downloading"] = True
    quality = users[event.from_id]["quality"]
    msg = await event.reply(translate.DOWNLOAD_MSG)

    if method == 'album':
        tracks = deezer.download_album(album_playlist, quality, stream=True)
    if method == 'playlist':
        tracks = deezer.download_playlist(album_playlist, quality, stream=True)

    await msg.delete()
    async with bot.action(event.chat_id, "audio"):
        for num, track in enumerate(tracks):
            if users[event.chat_id]["stopped"]:
                users[event.chat_id]['stopped'] = False
                break

            artist = album_playlist.tracks[num].artist
            title = album_playlist.tracks[num].title

            if not track:
                await bot.send_message(event.chat_id, f"Non posso scaricare\n{artist} - {title}")
                continue

            file_ext = ".mp3" if quality.startswith("MP3") else ".flac"

            file_name = f"{artist} - {title}{file_ext}"
            upload_status = UploadStatus(event, num + 1, album_playlist.total_tracks)
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
                        title=title,
                        duration=album_playlist.tracks[num].duration,
                        performer=artist,
                    )
                ],
            )
            await msg.delete()

    await event.reply(translate.END_MSG)
    users[event.chat_id]["downloading"] = False
    raise events.StopPropagation