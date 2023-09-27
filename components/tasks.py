from core.interface import check_trading_end_time
from discord.ext import tasks
import os
import logging

logger = logging.getLogger('discord')


class CheckTradingEndTimeTasks:
    def __init__(self, bot):
        self.bot = bot
        self.check_trading_end_time.start()

    def cog_unload(self):
        self.check_trading_end_time.cancel()

    @tasks.loop(seconds=5)
    async def check_trading_end_time(self):
        try:
            await check_trading_end_time(self.bot)
        except Exception as e:
            logger.error(f"Error in check trading end time task: {e}")








