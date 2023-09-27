import os
from datetime import datetime, timedelta
import yaml
import discord
from core.db import TradingDB
from core.models import Trading


def trading_setting(val=None):
    with open('trading.yaml', 'r') as f:
        trading = yaml.safe_load(f)
    if val:
        return trading.get(val)
    return trading


def get_message_url(ctx):
    return f"https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}/{ctx.message.id}"


def update_trading(ctx, _uuid, trading: Trading):
    trading.upsert(trading)
    trading.close()


def update_image(ctx, _uuid, file):
    file_data = {file.filename: file.url}
    trading_db = TradingDB(ctx)
    trading = trading_db.get_trading(ctx, _uuid)
    if trading.image_url:
        updated_image_url = trading.image_url.copy()
        updated_image_url.update(file_data)
        trading.image_url = updated_image_url
    else:
        trading.image_url = file_data
    trading_db.upsert(trading)


def delete_image(ctx, _uuid, filename):
    trading_db = TradingDB(ctx)
    trading = trading_db.get_trading(ctx, _uuid)
    if trading.image_url:
        updated_image_url = trading.image_url.copy()
        updated_image_url.pop(filename)
        trading.image_url = updated_image_url
        trading_db.upsert(trading)
    else:
        raise Exception("Trading image not found.")


async def update_message(ctx, _uuid, close=False):
    trading_db = TradingDB(ctx)
    trading = trading_db.get_trading(ctx, _uuid, close)
    trading_embed = discord.Embed.from_dict(trading.trading_embed)
    trading_image_url = trading.image_url
    trading_channel_id = trading_setting(f"V{trading.version}").get(trading.item_type)
    trading_message_id = int(trading.message_id)
    trading_channel = ctx.guild.get_channel(int(trading_channel_id))
    trading_message = await trading_channel.fetch_message(trading_message_id)

    if not trading.status:
        return trading_message
    if trading.status and trading.message_id and trading.trading_embed:
        for field in trading_embed.fields:
            if field.name == "商品圖片" and trading_image_url:
                image_urls_str = ''
                if len(trading_image_url) == 1:
                    trading_embed.set_image(url=list(trading_image_url.values())[0])
                if len(trading_image_url) < 1:
                    trading_embed.set_image(url='')
                if len(trading_image_url) >= 1:
                    image_urls_str = '\n'.join([f'[{k}]({v})' for k, v in trading_image_url.items()])
                field.value = image_urls_str

            if field.name == "結束時間":
                _time = f"<t:{int((trading.end_time - timedelta(hours=8)).timestamp())}:R>"\
                    if trading.end_time else '未設定'
                field.value = _time
            if field.name == "最高出價":
                if trading.last_bidder_id and trading.max_price:
                    price = format(trading.max_price, '.2f').rstrip('0').rstrip('.')
                    last_bidder_user = ctx.guild.get_member(int(trading.last_bidder_id))
                    val = f"{last_bidder_user.mention}\n{price}"
                else:
                    val = '無'
                field.value = val

        await trading_message.edit(embed=trading_embed)

    trading_db.close()


def get_trading_content(trading: Trading):
    trading_content = trading.content
    title = trading_content['title']
    price = trading_content['price']
    currency = trading_content['currency']
    description = trading_content['description']
    return title, price, currency, description


def parse_date(date_string):
    formats = ["%Y/%m/%d %H:%M:%S",  # 完全格式
               "%Y/%m/%d %H:%M",  # 無秒數
               "%m/%d %H:%M:%S",  # 無年份
               "%m/%d %H:%M"]  # 無年份和秒數
    current_year = datetime.now().year
    date_time_obj = None

    for fmt in formats:
        try:
            date_time_obj = datetime.strptime(date_string, fmt)
            if fmt.count('Y') == 0:  # 如果格式中沒有年份，設為當前年份
                date_time_obj = date_time_obj.replace(year=current_year)
            if fmt.count('S') == 0:  # 如果格式中沒有秒數，設為0
                date_time_obj = date_time_obj.replace(second=0)
            break
        except ValueError:
            pass

    if date_time_obj is None:
        raise ValueError(f"輸入的日期時間字符串 '{date_string}' 不符合任何可接受的格式")

    return date_time_obj








