from asyncio import sleep

from telethon import Button, events

from .. import bot, users

search_buttons = [
    [
        Button.switch_inline("Cerca una traccia 🎧", same_peer=True),
        Button.switch_inline("Cerca un album 💽", query=".a: ", same_peer=True),
    ],
    [Button.inline("❌")],
]


@bot.on(events.NewMessage(pattern="/impostazioni"))
async def settings(event):
    if hasattr(event, "query"):
        answer = event.edit
    else:
        answer = event.respond
    await answer(
        "Impostazioni:",
        buttons=[[Button.inline("Qualità 🎧", data="q")], [Button.inline("❌")]],
    )
    raise events.StopPropagation


@bot.on(events.CallbackQuery(pattern="q"))
async def settings_quality(event):
    q = users[event.query.user_id]["quality"]
    a = "Lossless (FLAC)"
    b = "Alta (MP3 320 KBPS)"
    c = "Media (MP3 256 KBPS)"
    d = "Bassa (MP3 128 KBPS)"
    s = " ✅"

    if q == "FLAC":
        a += s
    elif q == "MP3_320":
        b += s
    elif q == "MP3_256":
        c += s
    elif q == "MP3_128":
        d += s

    await event.edit(
        "Selezione la qualità: ",
        buttons=[
            [Button.inline(a, data="FLAC"), Button.inline(b, data="MP3_320")],
            [Button.inline(c, data="MP3_256"), Button.inline(d, data="MP3_128")],
            [Button.inline("◀️"), Button.inline("❌")],
        ],
    )


@bot.on(events.CallbackQuery(pattern=r"(FLAC|MP3_\d{3})"))
async def callback(event):
    q = event.data.decode("utf-8")
    if users[event.query.user_id]["quality"] != q:
        users[event.query.user_id]["quality"] = q
        await event.answer("Fatto!")
        await settings_quality(event)
    else:
        await event.answer("Già selezionata!")


@bot.on(events.CallbackQuery(pattern="❌"))
async def cancel(event):
    await event.edit("Annullato.")
    await sleep(1.5)
    await event.delete()


@bot.on(events.CallbackQuery(pattern="◀️"))
async def back_to_settings(event):
    await settings(event)
