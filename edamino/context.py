from .client import Client
from .objects import Message
from .api import Embed, LinkSnippet
from typing import (
    List,
    Optional,
    Literal
)
from contextlib import asynccontextmanager, contextmanager
from ujson import dumps
from aiohttp import ClientWebSocketResponse
import time

class Context:
    __slots__ = ('msg', 'client', 'ws')

    def __init__(self, msg: Message, client: Client, ws: ClientWebSocketResponse) -> None:
        self.msg = msg
        self.client = client
        self.ws = ws

    async def reply(self,
                    message: Optional[str] = None,
                    message_type: int = 0,
                    ref_id: Optional[int] = None,
                    mentions: Optional[List[str]] = None,
                    embed: Optional[Embed] = None,
                    link_snippets_list: Optional[List[LinkSnippet]] = None):
        return await self.client.send_message(message=message,
                                              chat_id=self.msg.threadId,
                                              reply=self.msg.messageId,
                                              message_type=message_type,
                                              ref_id=ref_id,
                                              mentions=mentions,
                                              embed=embed,
                                              link_snippets_list=link_snippets_list)

    async def send_image(self, image: bytes):
        return await self.client.send_image(image, chat_id=self.msg.threadId)

    async def send_gif(self, gif):
        return await self.client.send_gif(gif, chat_id=self.msg.threadId)

    async def send_audio(self, audio: bytes):
        return await self.client.send_audio(audio, chat_id=self.msg.threadId)

    async def download_from_link(self, link: str):
        return await self.client.download_from_link(link)

    async def send(self,
                   message: Optional[str] = None,
                   message_type: int = 0,
                   ref_id: Optional[int] = None,
                   mentions: Optional[List[str]] = None,
                   embed: Optional[Embed] = None,
                   link_snippets_list: Optional[List[LinkSnippet]] = None,
                   reply: Optional[str] = None,
                   chatid: Optional[str] = None):
        return await self.client.send_message(message=message,
                                              chat_id=self.msg.threadId if chatid is None else chatid,
                                              message_type=message_type,
                                              ref_id=ref_id,
                                              mentions=mentions,
                                              embed=embed,
                                              link_snippets_list=link_snippets_list,
                                              reply=reply)

    async def get_user_info(self, userId: str = None):
        return await self.client.get_user_info(self.msg.uid if userId is None else userId)

    async def invite(self, chat_id: str):
        return await self.client.invite_to_chat(uids=[self.msg.uid], chat_id=chat_id)

    async def follow(self):
        return await self.client.follow([self.msg.uid])

    async def unfollow(self):
        return await self.client.unfollow(self.msg.uid)

    async def delete_message(self, message_id: str = None, as_staff: bool = False, reason: Optional[str] = None):
        return await self.client.delete_message(chat_id=self.msg.threadId,
                                          message_id=self.msg.messageId if message_id is None else message_id,
                                          reason=reason,
                                          as_staff=as_staff)

    async def kick(self, userId: str = None, allow_rejoin: bool = True):
        return await self.client.kick_from_chat(self.msg.threadId, self.msg.uid if userId is None else userId, allow_rejoin)

    async def join_community(self, code: Optional[str] = None):
        return await self.client.join_community(code)

    async def leave_community(self):
        return await self.client.leave_community()

    async def join_chat(self, chatid: str = None):
        return await self.client.join_chat(self.msg.threadId if chatid is None else chatid)

    async def leave_chat(self, chatid: str = None):
        return await self.client.leave_chat(self.msg.threadId if chatid is None else chatid)

    async def get_info_link(self, link: str):
        return await self.client.get_info_link(link)

    async def get_from_id(self, object_id: str, object_type: int = 0):
        return await self.client.get_from_id(object_id, object_type=object_type)

    async def get_user_blogs(self, start: int = 0, size: int = 25):
        return await self.client.get_user_blogs(self.msg.uid, start=start, size=size)

    @asynccontextmanager
    async def typing(self, chat_type: Literal[0, 1, 2] = 2):
        data = {
            "o": {
                "actions": ["Typing"],
                "target": f"ndc://x{self.msg.ndcId}/chat-thread/{self.msg.threadId}",
                "ndcId": self.msg.ndcId,
                "params": {"threadType": chat_type},
                "id": "2713213"
            },
            "t": 304
        }

        try:
            await self.ws.send_str(dumps(data))
            yield
        finally:
            data['t'] = 306
            await self.ws.send_str(dumps(data))

    @asynccontextmanager
    async def recording(self, chat_type: int = 2):
        data = {
            "o": {
                "actions": ["Recording"],
                "target": f"ndc://x{self.msg.ndcId}/chat-thread/{self.msg.threadId}",
                "ndcId": self.msg.ndcId,
                "params": {
                    "threadType": chat_type
                },
                "id": "161486614"
            },
            "t": 304
        }
        try:
            await self.ws.send_str(dumps(data))
            yield
        finally:
            data['t'] = 306
            await self.ws.send_str(dumps(data))

    async def get_chat_messages(self, size: int = 25, page_token: Optional[str] = None):
        return await self.client.get_chat_messages(self.msg.threadId, size, page_token)

    async def start_chat(self,
                         content: Optional[str] = None,
                         chat_type: int = 0,
                         is_global: bool = False,
                         publish_to_global: bool = False):
        return await self.client.start_chat(invitee_ids=[self.msg.uid],
                                            content=content,
                                            chat_type=chat_type,
                                            is_global=is_global,
                                            publish_to_global=publish_to_global)

    async def send_sticker(self, sticker_id: str):
        return await self.client.send_sticker(self.msg.threadId, sticker_id)

    async def get_chat_info(self):
        return await self.client.get_chat_info(self.msg.threadId)

    @contextmanager
    def set_ndc(self, ndc_id: int = 0):
        try:
            self.client.set_ndc(ndc_id)
            yield
        finally:
            self.client.set_ndc(self.msg.ndcId)

    async def get_message_info(self):
        return await self.client.get_message_info(self.msg.threadId, self.msg.messageId)

    async def actions(self, actions: List[str], thread_type: int, chat_id: Optional[str] = None,
                      ndc_id: Optional[int] = None):
        data = {
            "o": {
                "actions": actions,
                "target": f"ndc://x{self.msg.ndcId}/chat-thread/{self.msg.threadId if chat_id is None else chat_id}",
                "ndcId": self.msg.ndcId if ndc_id is None else ndc_id,
                "params": {
                    "duration": 12800,
                    "membershipStatus": 1,
                    "threadType": thread_type
                },
                "id": "1715976"
            },
            "t": 306
        }
        await self.ws.send_json(data)

    async def join_channel(self, channel_type: int, chat_id: Optional[str] = None, ndc_id: Optional[int] = None):
        data = {
            "o": {
                "ndcId": self.msg.ndcId if ndc_id is None else ndc_id,
                "threadId": self.msg.threadId if chat_id is None else chat_id,
                "channelType": channel_type,
                "id": "10335436"
            },
            "t": 108
        }
        await self.ws.send_json(data)

    async def create_channel(self,
                             chat_id: Optional[str] = None,
                             ndc_id: Optional[int] = None):
        data = {
            "o": {
                "id": "1300666754",
                "ndcId": self.msg.ndcId if ndc_id is None else ndc_id,
                "threadId": self.msg.threadId if chat_id is None else chat_id,
            },
            "t": 200
        }
        await self.ws.send_json(data)

    async def play_video(self,
                         background: str,
                         path: str,
                         title: str,
                         duration: float,
                         chat_id: Optional[str] = None,
                         ndc_id: Optional[int] = None):
        await self.create_channel(chat_id, ndc_id)
        data = {
            "o": {
                "ndcId": self.msg.ndcId if ndc_id is None else ndc_id,
                "threadId": self.msg.threadId if chat_id is None else chat_id,
                "playlist": {
                    "currentItemIndex": 0,
                    "currentItemStatus": 1,
                    "items": [{
                        "author": None,
                        "duration": duration,
                        "isDone": False,
                        "mediaList": [[100, background, None]],
                        "title": title,
                        "type": 1,
                        "url": f"file://{path}"
                    }]
                },
                "id": "3423239"
            },
            "t": 120
        }

        await self.ws.send_json(data)

    async def play_video_is_done(self,
                                 background: str,
                                 path: str,
                                 title: str,
                                 duration: float,
                                 chat_id: Optional[str] = None,
                                 ndc_id: Optional[int] = None):
        data = {
            "o": {
                "ndcId": self.msg.ndcId if ndc_id is None else ndc_id,
                "threadId": self.msg.threadId if chat_id is None else chat_id,
                "playlist": {
                    "currentItemIndex": 0,
                    "currentItemStatus": 2,
                    "items": [{
                        "author": None,
                        "duration": duration,
                        "isDone": True,
                        "mediaList": [[100, background, None]],
                        "title": title,
                        "type": 1,
                        "url": f"file://{path}"
                    }]
                },
                "id": "3423239"
            },
            "t": 120
        }
        await self.ws.send_json(data)

    async def join_thread(self, join_role: int = 1, chat_id: Optional[str] = None, ndc_id: Optional[int] = None):
        data = {
            "o": {
                "ndcId": self.msg.ndcId if ndc_id is None else ndc_id,
                "threadId": self.msg.threadId if chat_id is None else chat_id,
                "joinRole": join_role,
                "id": "10335106"
            },
            "t": 112
        }
        await self.ws.send_json(data)

    async def edit_profile(self, *args, **kwargs):
        return await self.client.edit_profile(*args, **kwargs)

    async def get_chats(self, start: int = 0, size: int = 25):
        return await self.client.get_chats(start, size)

    async def get_chat_users(self, start: int = 0, size: int = 25):
        return await self.client.get_chat_users(self.msg.threadId, start, size)
    
    async def subscribe(self):
        return await self.client.subscribe(user_id = self.msg.author.uid, auto_renew = False)

    async def get_public_chats(self, start: int = 0, size: int = 25):
        return await self.client.get_public_chats(start, size)

    async def block(self, userId: str):
        return await self.client.block(self.msg.uid if userId is None else userId)
    
    async def unblock(self, userId: str):
        return await self.client.unblock(self.msg.uid if userId is None else userId)
    
    async def get_notices(self, start: int = 0, size: int = 25):
        return await self.client.get_notices(start, size)

    async def promotion(self, noticeId: str, type: str = "accept"):
        return await self.client.promotion(noticeId, type)
    
    async def set_bubble(self, chat_id: str = None, bubble_id: str = None, apply_to_all: bool = False):
        return await self.client.set_bubble(self.msg.threadId if chat_id is None else chat_id, bubble_id, apply_to_all)

    async def ban(self, userId: str, reason: str):
        return await self.client.ban(self.msg.uid if userId is None else userId, reason)

    async def unban(self, userId: str, reason: str):
        return await self.client.unban(self.msg.uid if userId is None else userId, reason)
    
    async def comment_profile(self, userId: str, message: str):
        return await self.client.comment_profile(self.msg.uid if userId is None else userId, message)
    
    async def get_wallet_info(self):
        return await self.client.get_wallet_info()
    
    async def invite_to_vc(self, chat_id: str = None, userId: str = None):
        return await self.client.invite_to_vc(self.msg.threadId if chat_id is None else chat_id, self.msg.uid if userId is None else userId)

    async def apply_avatar_frame(self, avatarId: str, applyToAll: bool = True):
        return await self.client.apply_avatar_frame(avatarId, applyToAll)
    
    async def delete_blog(self, blogId: str):
        return await self.client.delete_blog(blogId)
    
    async def get_community_user_stats(self, type: str, start: int = 0, size: int = 25):
        return await self.client.get_community_user_stats(type, start, size)

    async def get_my_communities(self, start: int = 0, size: int = 25):
        return await self.client.get_my_communities(start, size)
    
    async def send_coins(self, coins: int, blog_id: Optional[str] = None, chat_id: Optional[str] = None, object_id: Optional[str] = None, transaction_id: Optional[str] = None):
        return await self.client.send_coins(coins, blog_id, chat_id, object_id, transaction_id)

    async def get_community_stats(self):
        return await self.client.get_my_communities()
    
    async def request_join_community(self, comId: str, message: str = None):
        return await self.client.request_join_community(comId, message)

    async def transfer_host(self, chat_id: str = None, userId: list = None):
        return await self.client.transfer_host(self.msg.threadId if chat_id is None else chat_id, [self.msg.uid] if userId is None else userId)

    async def warn(self, userId: str, reason: str = None):
        return await self.client.warn(userId, reason)

    async def strike(self, userId: str, time: int, title: str = None, reason: str = None):
        return await self.client.strike(userId, time, title, reason)

    async def promote_rank(self, userId: str, rank: str = "curator"):
        return await self.client.promote_rank(self.msg.uid if userId is None else userId, rank)

    async def set_view_only_chat(self, view_only: Literal['enable', 'disable']):
        return await self.client.set_view_only_chat(self.msg.threadId, view_only)

    async def set_cohosts(self, users: list):
        return await self.client.set_cohosts(self.msg.threadId, users)

    async def like_blog(self, blog_id: str):
        return await self.client.like_blog(blog_id)
    
    async def like_wiki(self, wiki_id: str):
        return await self.client.like_wiki(wiki_id)

    async def show_online(self, ndcId=None):
        if ndcId is None: ndcId = self.client.uid

        data = {
            'o' : {
                "actions" : ["Browsing"],
                "target"  : f"ndc://x{ndcId}/",
                "ndcId"   : ndcId,
                "id"      : "82333",
                "timestamp" : int(time.time() * 1000)
            },
            't' : 304
        }

        data['t'] = 306
        await self.ws.send_json(data)
        data['t'] = 304
        await self.ws.send_json(data)
        return
