from telethon import Button, events

from typing import Union
from telethon.tl.patched import Message
from telethon.events import NewMessage

from .. import bot, users

@bot.on(events.NewMessage(pattern='/stop'))
async def stop(event: Union[NewMessage.Event, Message]):
    user_id = event.message.from_id
    if not users[user_id]['downloading'] or users[user_id]['stopped']:
        pass
    else:
        users[user_id]['stopped'] = True
        await event.respond("Fermerò il download dopo il prossimo invio.")

    raise events.StopPropagation