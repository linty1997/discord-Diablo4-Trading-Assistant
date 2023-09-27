import uuid
from datetime import datetime
import discord


class TradingEmbed:
    def __init__(self, _type, user, title, description, price, currency, _uuid=None):
        self._type = _type
        self.user = user
        self.title = title
        self.description = description
        self.price = price
        self.currency = currency
        if isinstance(_uuid, bytes):
            self.uuid = str(uuid.UUID(bytes=_uuid))
        else:
            self.uuid = _uuid
        self.now = datetime.now()

    def base(self):
        embed = discord.Embed(colour=discord.Colour.blue(), timestamp=self.now)
        embed.set_author(icon_url=self.user.avatar.url, name=f"掛單: {self.user.display_name}")
        embed.set_footer(text=f"{self.uuid}", icon_url=self.user.avatar.url)

        return embed

    def get(self, image_val=None, end_time=None):
        if image_val != "未設置" and image_val is not None:
            image_val = '\n'.join([f'[{k}]({v})' for k, v in image_val.items()])
        if end_time != "未設置" and end_time is not None:
            auction_time = f"<t:{int(end_time.timestamp())}:R>"
        embed = self.base()
        embed.title = "販賣物品設置"
        embed.colour = discord.Colour.green()
        embed.description = f"種類: {self._type}\n下方UUID用於上傳圖片及其他設置\n詳細操作見公告"
        embed.add_field(name="商品標題", value=self.title, inline=False)
        embed.add_field(name="商品價格", value=f"{self.price}\n單位: {self.currency}")
        embed.add_field(name="結束時間", value=end_time)
        embed.add_field(name="商品圖片", value=image_val)
        embed.add_field(name="商品描述", value=self.description, inline=False)

        return embed

    def to_trading_channel(self):
        embed = self.base()
        embed.title = self.title
        embed.add_field(name="商品價格", value=f"{self.price}\n單位: {self.currency}")
        embed.add_field(name="商品賣家", value=f"{self.user.mention}")
        embed.add_field(name="最高出價", value="無")
        embed.add_field(name="結束時間", value=f"未設置")
        embed.add_field(name="商品圖片", value="未添加")
        embed.add_field(name="商品描述", value=self.description, inline=False)

        return embed


def trading_list_embed(string_list: str):
    embed = discord.Embed(colour=0x90dd31, timestamp=datetime.now())
    embed.set_author(name="掛單列表")
    embed.description = string_list

    return embed


