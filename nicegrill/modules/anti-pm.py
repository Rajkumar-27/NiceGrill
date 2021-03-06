#    This file is part of NiceGrill.

#    NiceGrill is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    NiceGrill is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with NiceGrill.  If not, see <https://www.gnu.org/licenses/>.

import logging
from nicegrill import utils
from database import antipmdb as nicedb
from telethon import functions, tl


class AntiPM:

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.ERROR)

    FLOOD_CTRL = 0
    ALLOWED = []
    USERS_AND_WARNS = {}

    WARNING = (
        "<b>I have not allowed you to PM, please ask or say whatever</b>"
        "<b> it is in a group chat or at least ask for my permission to PM</b>\n\n"
        "<b>I'm letting you off the hook for this time but be warned that </b>"
        "<b>you will be blocked & reported spam if you continue.</b>")

    BLOCKED = (
        "<b>I have warned you several times now. However, you did not stop </b>"
        "<b>spamming my chat. Therefore, you have been blocked and reported </b>"
        "<b>as spam. Good luck!</b>")

    async def antipmxxx(message):
        switch = utils.get_arg(message).lower()
        if switch == "on":
            await nicedb.delete("AntiPM")
            await nicedb.set_antipm(True)
            await message.edit("<i>AntiPM turned on</i>")
        elif switch == "off":
            await nicedb.delete("AntiPM")
            await nicedb.set_antipm(False)
            await message.edit("<i>AntiPM turned off</i>")
        else:
            await message.edit("<i>It's either on or off, pick one</i>")
            return

    async def approvexxx(message):
        """Allows that person to PM you, you can either reply to user,
type their username or use this in their chat"""
        id = None if not utils.get_arg(message) else (await message.client.get_entity(utils.get_arg(message))).id
        reply = None if not message.is_reply else (await message.get_reply_message()).sender_id
        chat = None if not hasattr(
            message.to_id, "user_id") else message.chat_id
        if not reply and not id and not chat:
            await message.edit("<b>No user found</b>")
            return
        pick = reply or id or chat
        if pick == (await message.client.get_me()).id:
            await message.edit("<b>Why would you wanna approve yourself?</b>")
            return
        if await nicedb.check_approved(pick):
            await message.edit("<i>User is already approved</i>")
            return
        else:
            await nicedb.approve(pick)
            await message.edit(
                "<a href=tg://user?id={}>{}</a> <b>is approved to PM you now</b>"
                .format(pick, (await message.client.get_entity(pick)).first_name))

    async def disapprovexxx(message):
        """Prevents that person to PM you, you can either reply to user,
type their username or use this in their chat"""
        id = None if not utils.get_arg(message) else (await message.client.get_entity(utils.get_arg(message))).id
        reply = None if not message.is_reply else (await message.get_reply_message()).sender_id
        chat = None if not hasattr(
            message.to_id, "user_id") else message.chat_id
        if not reply and not id and not chat:
            await message.edit("<b>No user found</b>")
            return
        pick = reply if not id and not chat else id or chat
        if pick == (await message.client.get_me()).id:
            await message.edit("<b>Why would you wanna disapprove yourself?</b>")
            return
        if not await nicedb.check_approved(pick):
            await message.edit("<i>User is not approved</i>")
            return
        else:
            await nicedb.disapprove(pick)
            await message.edit(
                "<a href=tg://user?id={}>{}</a> <b>is disapproved to PM you now</b>"
                .format(pick, (await message.client.get_entity(pick)).first_name))

    async def blockxxx(message):
        """Simply blocks the person..duh!!"""
        id = None if not utils.get_arg(message) else (await message.client.get_entity(utils.get_arg(message))).id
        reply = None if not message.is_reply else (await message.get_reply_message()).sender_id
        chat = None if not hasattr(
            message.to_id, "user_id") else message.chat_id
        if not reply and not id and not chat:
            await message.edit("<i>No user found</i>")
            return
        pick = reply or id or chat
        if pick == (await message.client.get_me()).id:
            await message.edit("<i>Why would you wanna block yourself?</i>")
            return
        await message.client(functions.contacts.BlockRequest(id=pick))
        if await nicedb.check_approved(pick):
            await nicedb.disapprove(pick)
        await message.edit(
            "<a href=tg://user?id={}>{}</a> <i>has been blocked</i>"
            .format(pick, (await message.client.get_entity(pick)).first_name))

    async def unblockxxx(message):
        """Simply unblocks the person..duh!!"""
        id = None if not utils.get_arg(message) else (await message.client.get_entity(utils.get_arg(message))).id
        reply = None if not message.is_reply else (await message.get_reply_message()).sender_id
        chat = None if not hasattr(
            message.to_id, "user_id") else message.chat_id
        if not reply and not id and not chat:
            await message.edit("<i>No user found</i>")
            return
        pick = reply or id or chat
        if pick == (await message.client.get_me()).id:
            await message.edit("<i>Why would you wanna unblock yourself?</i>")
            return
        await message.client(functions.contacts.UnblockRequest(id=pick))
        await message.edit(
            "<a href=tg://user?id={}>{}</a> <i>has been unblocked</i>"
            .format(pick, (await message.client.get_entity(pick)).first_name))

    async def notifsxxx(message):
        """Ah this one again...It turns on/off tag notification
sounds from unwanted PMs. It auto-sends a
a message in your name until that user gets blocked or approved"""
        val = utils.get_arg(message)
        if not val:
            await message.edit("<i>Please type on/off</i>")
            return
        if val == "off":
            await nicedb.delete("Notifications")
            await nicedb.set_notif(False)
            await message.edit("<i>Notifications from unapproved PMs muted</i>")
        if val == "on":
            await nicedb.delete("Notifications")
            await nicedb.set_notif(True)
            await message.edit("<i>Notifications from unapproved PMs unmuted</i>")

    async def setlimitxxx(message):
        """This one sets a max. message limit for unwanted
PMs and when they go beyond it, bamm!"""
        limit = int(utils.get_arg(message))
        if not limit or not str(limit).isdigit():
            await message.edit("<i>Please type a number</i>")
            return
        if limit > 0:
            await nicedb.delete("Limit")
            await nicedb.set_limit(limit)
            await message.edit("<i>Max. PM message limit successfully updated</i>")

    async def superblockxxx(message):
        """If unwanted users spams your chat, the chat
will be deleted when the idiot passes the message limit"""
        val = utils.get_arg(message)
        if not val:
            await message.edit("<i>Please type on/off</i>")
            return
        if val == "on":
            await nicedb.delete("SuperBlock")
            await nicedb.set_sblock(True)
            await message.edit("<i>Chats from unapproved PMs will be removed</i>")
        if val == "off":
            await nicedb.delete("SuperBlock")
            await nicedb.set_sblock(False)
            await message.edit("<i>Chats from unapproved PMs will not be removed anymore</i>")
        setPM(command)

    async def watchout(message):
        if message.sender_id != (await message.client.get_me()).id and isinstance(message.to_id, tl.types.PeerUser):
            if getattr(message.sender, "bot", None) or not await nicedb.check_antipm():
                return
            user = (await message.get_sender()).id
            if await nicedb.check_approved(user):
                return
            if not await nicedb.check_notifs():
                await message.client.send_read_acknowledge(message.chat_id)
            user_warns = 0 if user not in AntiPM.USERS_AND_WARNS else AntiPM.USERS_AND_WARNS[
                user]
            if user_warns <= await nicedb.check_limit() - 2:
                user_warns += 1
                AntiPM.USERS_AND_WARNS.update({user: user_warns})
                if not AntiPM.FLOOD_CTRL > 0:
                    AntiPM.FLOOD_CTRL += 1
                else:
                    AntiPM.FLOOD_CTRL = 0
                    return
                async for msg in message.client.iter_messages(entity=message.chat_id,
                                                             from_user='me',
                                                             search="I have not allowed you to PM",
                                                             limit=1):
                    await msg.delete()
                await message.reply(AntiPM.WARNING)
                return
            await message.reply(AntiPM.BLOCKED)
            await message.client(functions.messages.ReportSpamRequest(peer=message.sender_id))
            await message.client(functions.contacts.BlockRequest(id=message.sender_id))
            if await nicedb.check_sblock():
                await message.client.delete_dialog(entity=message.chat_id, revoke=True)
            AntiPM.USERS_AND_WARNS.update({user: 0})
