import discord
from components.views import TradingSelectView
from core.interface import update_trading_form, close_trading


class TradingSellButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        trading_button = discord.ui.Button(label="販賣物品",
                                           style=discord.ButtonStyle.primary,
                                           emoji='<a:8_:910909126404608010>',
                                           custom_id="trading_button")

        trading_close_button = discord.ui.Button(label="關閉販賣物品",
                                                 style=discord.ButtonStyle.red,
                                                 emoji='<a:threepointsanima:1002490828398284860>',
                                                 custom_id="trading_close_button")


        trading_close_button.callback = self.trading_close_button_callback
        trading_button.callback = self.trading_button_callback
        self.add_item(trading_button)
        self.add_item(trading_close_button)


    async def trading_close_button_callback(self, interaction):
        await interaction.response.send_modal(TradingButtonModalView(name="close", title="關閉販賣物品"))

    async def trading_button_callback(self, interaction):
        await interaction.response.send_message("**請於下列選單選取要販售的種類**\n`30 秒未選擇將刪除此訊息`",
                                                view=TradingSelectView(), ephemeral=True, delete_after=30)


class TradingButtonModalView(discord.ui.Modal):
    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name

        self.add_item(discord.ui.InputText(label="uuid", placeholder="請輸入商品的 UUID",
                                           min_length=36, max_length=36))

    async def callback(self, interaction: discord.Interaction):
        _uuid = self.children[0].value
        if self.name == "close":
            await close_trading(interaction, _uuid, btn=True)
        return
