import uuid
import discord
import os
from core.models import Trading
from core.db import TradingDB
from components.embeds import TradingEmbed
from core.trading_utils import update_message, trading_setting, get_trading_content, get_message_url


class TradingModal(discord.ui.Modal):
    def __init__(self, _type, form_title="", price="", currency="", description="", version="",
                 _uuid=None, update=False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._type = _type
        self.title = form_title
        self.price = price
        self.currency = currency
        self.description = description
        self.version = version
        self.uuid = _uuid
        self.update = update

        self.add_item(discord.ui.InputText(label="標題", placeholder="請輸入商品標題",
                                           min_length=1, max_length=30, value=self.title))
        self.add_item(discord.ui.InputText(label="價格", placeholder="請輸入商品價格, 僅限輸入數字",
                                           min_length=1, max_length=20, value=self.price))
        self.add_item(discord.ui.InputText(label="貨幣", placeholder="請輸入交易用的貨幣名稱",
                                           min_length=1, max_length=5, value=self.currency))
        if not self.update:
            self.add_item(discord.ui.InputText(label="版本", placeholder="永恆界域為 0, S1 則輸入 1. 僅限輸入數字",
                                               min_length=1, max_length=2, value=self.version))
        self.add_item(discord.ui.InputText(label="描述", placeholder="請輸入商品描述", min_length=1, max_length=2000,
                                           style=discord.InputTextStyle.long, value=self.description))

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, invisible=False)
        title = self.children[0].value
        price = self.children[1].value
        currency = self.children[2].value
        if not self.update:
            version = self.children[3].value
            description = self.children[4].value
        else:
            version = self.version
            description = self.children[3].value

        # TODO: 保存到數據庫
        trading_db = TradingDB(interaction)
        content = {"title": title, "price": price, "currency": currency, "description": description}
        if not self.update:
            trading = Trading(id=uuid.uuid4().bytes, creator_id=interaction.user.id, title=title, version=version,
                              content=content, status=True, item_type=self._type, start_price=price)
            trading_results = trading_db.upsert(trading)
            self.uuid = trading_results.id
        else:
            trading_results = trading_db.get_trading(interaction, self.uuid)
            trading_results.start_price = price
            trading_results.content = content
            trading_results.title = title

        # TODO: 生成embed
        embed_obj = TradingEmbed(_type=self._type, user=interaction.user, title=title, description=description,
                                 price=price, currency=currency, _uuid=self.uuid)
        embed = embed_obj.get(trading_results.image_url, trading_results.end_time)
        trading_embed = embed_obj.to_trading_channel()

        # TODO: 發送訊息至交易頻道及回覆訊息
        if not self.update:
            trading_channel_id = trading_setting(f"V{version}").get(self._type)
            trading_channel = interaction.client.get_channel(int(trading_channel_id))
            msg = await trading_channel.send(embed=trading_embed, view=TradingBuyButtonView())

            # TODO: 更新數據庫
            trading_results.message_id = msg.id
        trading_results.trading_embed = trading_embed.to_dict()
        trading_db.upsert(trading_results)
        trading_db.close()

        if self.update:
            await update_message(interaction, self.uuid)
        await interaction.followup.send(embeds=[embed], ephemeral=True)


class TradingBuyButtonView(discord.ui.View):
    def __init__(self, disabled=False, emoji='<a:ringabell:1049838012302897193>'):
        super().__init__(timeout=None)
        button = discord.ui.Button(label="購買/出價",
                                   style=discord.ButtonStyle.green,
                                   emoji=emoji,
                                   disabled=disabled,
                                   custom_id="trading_buy_button")
        button.callback = self.button_callback
        self.add_item(button)

    async def button_callback(self, interaction):
        trading_db = TradingDB(interaction)
        trading = trading_db.get_trading_by_message_id(interaction.message.id)
        if trading is None or not trading.status:
            await interaction.response.send_message("此商品已下架", ephemeral=True)
            return
        price = format(trading.start_price, '.2f').rstrip('0').rstrip('.')
        modal = TradingBidModal(title="報價表", price=price)
        trading_db.close()
        await interaction.response.send_modal(modal)


class TradingBidModal(discord.ui.Modal):
    def __init__(self, price=None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(discord.ui.InputText(label="輸入出價", placeholder="請輸入出價, 預設為標價", max_length=20,
                                           value=price))

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, invisible=False)
        trading_db = TradingDB(interaction)
        trading = trading_db.get_trading_by_message_id(interaction.message.id)
        trading_channel_id = trading_setting(f"V{trading.version}").get("Trading")
        trading_channel = interaction.client.get_channel(int(trading_channel_id))
        trading_title, trading_price, trading_currency, trading_description = get_trading_content(trading)
        seller = interaction.guild.get_member(trading.creator_id)
        buyer = interaction.user
        if trading.max_price is None:
            trading.max_price = self.children[0].value
        elif float(self.children[0].value) > float(trading.max_price):
            trading.max_price = self.children[0].value
        trading.last_bidder_id = buyer.id
        trading_db.upsert(trading)
        trading_db.close()
        await update_message(interaction, trading.id)
        message_url = get_message_url(interaction)
        await trading_channel.send(f"{seller.mention}\n出價人: {buyer.mention}\n"
                                   f"`出價:{self.children[0].value} {trading_currency}`\n"
                                   f"`想購買 [{trading.title}]`\n"
                                   f"`訊息:`{message_url}")
        await interaction.followup.send(f"`出價: {self.children[0].value}`", ephemeral=True)


class TradingSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        custom_id="selectTrading",
        placeholder="選擇要添加的物品種類",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                label="野蠻人",
                description="野蠻人的相關裝備物品"
            ),
            discord.SelectOption(
                label="德魯伊",
                description="德魯伊的相關裝備物品"
            ),
            discord.SelectOption(
                label="死靈法師",
                description="死靈法師的相關裝備物品"
            ),
            discord.SelectOption(
                label="俠盜",
                description="俠盜的相關裝備物品"
            ),
            discord.SelectOption(
                label="魔法使",
                description="魔法使的相關裝備物品"
            ),
            discord.SelectOption(
                label="飾品",
                description="任何職業飾品"
            ),
            discord.SelectOption(
                label="其他",
                description="其餘任何未列出之可交易物品"
            )
        ]
    )
    async def select_callback(self, select, interaction):
        val = select.values[0]
        await interaction.response.send_modal(TradingModal(_type=val, title=f"{val} 物品設置"))
