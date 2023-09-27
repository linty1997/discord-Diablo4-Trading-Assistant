from components.settings_view import TradingSellButtonView
from discord.ext import commands
from components.views import TradingBuyButtonView
from components.views import TradingSelectView


class Events(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(TradingBuyButtonView())
        self.bot.add_view(TradingSellButtonView())
        self.bot.add_view(TradingSelectView())


def setup(bot):
    bot.add_cog(Events(bot))

