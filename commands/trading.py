from components.settings_view import TradingSellButtonView
from core.interface import *
from discord.commands import slash_command, Option, OptionChoice
from discord.ext import commands
from core.trading_utils import *


class Trading(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # TODO: Admin Trading Command
    trading_setting = discord.SlashCommandGroup("trading_setting",
                                                "Setting admin trading.",
                                                default_member_permissions=discord.Permissions(administrator=True))

    # setting trading button
    @trading_setting.command(description="Set trading button.")
    async def button(self, ctx):
        await ctx.respond(view=TradingSellButtonView())

    # TODO: User Trading Command
    trading = discord.SlashCommandGroup("trading", "Setting trading parameter.")

    # trading update image
    @trading.command(description="上傳交易物品的圖片.")
    async def image(self, ctx, uuid: str, file: Option(discord.Attachment, "Trading image.", required=True)):
        try:
            update_image(ctx, uuid, file)
        except Exception as e:
            print(e)
            await ctx.respond("`上傳圖片發生錯誤, 檢查 uuid 是否正確.`", ephemeral=True)
        else:
            await ctx.respond("`上傳圖片成功.`", ephemeral=True)
            await update_message(ctx, uuid)

    # delete trading image
    @trading.command(description="刪除交易物品的圖片.")
    async def delete_image(self, ctx, uuid: str, filename: str):
        await del_image(ctx, uuid, filename)

    # update trading form
    @trading.command(description="更新交易表單.")
    async def update_form(self, ctx, uuid: str):
        await update_trading_form(ctx, uuid)

    # get trading form
    @trading.command(description="取得交易表單.")
    async def get_form(self, ctx, uuid: str):
        await get_trading_form(ctx, uuid)

    # setting auction end time
    @trading.command(description="設定拍賣結束時間.")
    async def end_time(self, ctx, uuid: str, end_time: str):
        await set_end_time(ctx, uuid, end_time)

    # close trading
    @trading.command(description="關閉交易.")
    async def close(self, ctx, uuid: str):
        await close_trading(ctx, uuid)

    # get trading list
    @trading.command(description="取得交易列表.")
    async def list(self, ctx):
        await get_trading_list(ctx)


def setup(bot):
    bot.add_cog(Trading(bot))
