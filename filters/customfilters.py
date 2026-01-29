import os

from aiogram.filters import Filter
from aiogram import Bot, types

boss = os.getenv('BOSS')

class BossFilter(Filter):
    def __init__(self) -> None:
        pass

    async def __call__(self, message: types.Message) -> bool:
        return str(message.from_user.id) in boss


class ChatTypeFilter(Filter):
    def __init__(self, allowed_types: list[str]) -> None:
        self.allowed_types = allowed_types

    async def __call__(self, message: types.Message) -> bool:
        return message.chat.type in self.allowed_types
