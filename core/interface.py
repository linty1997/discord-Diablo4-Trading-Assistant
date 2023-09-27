import uuid as uuid_lib
from datetime import datetime, timedelta
from components.embeds import TradingEmbed, trading_list_embed
from components.views import TradingBuyButtonView, TradingModal
from core.db import TradingDB
from core.models import Trading
from core.trading_utils import update_message, trading_setting, delete_image, get_trading_content, parse_date


async def update_trading_form(ctx, uuid: str):
    try:
        trading = TradingDB(ctx).get_trading(ctx, uuid)
        trading_id = trading.id
        trading_item_type = trading.item_type
        trading_title, trading_price, trading_currency, trading_description = get_trading_content(trading)
        modal = TradingModal(trading_item_type, trading_title, trading_price,
                             trading_currency, trading_description, trading.version,
                             _uuid=trading_id, update=True, title=f"{trading_item_type} 物品更新")

    except Exception as e:
        print(e)
        await ctx.respond("`更新交易表單發生錯誤.`", ephemeral=True)
    else:
            await ctx.send_modal(modal)


async def get_trading_list(ctx):
    await ctx.defer(ephemeral=True)
    try:
        trading_db = TradingDB(ctx)
        trading_list = trading_db.get_tradings_by_user(ctx.user.id)
        trading_db.close()
        embed_val = ""
        for trading in trading_list:
            trading_id = str(uuid_lib.UUID(bytes=trading.id))
            trading_title = trading.title
            embed_val += f"{trading_title}\n{trading_id}\n\n"
        embed_val = "無資料" if embed_val == "" else embed_val
        embed = trading_list_embed(embed_val)
    except Exception as e:
        print(e)
        await ctx.send_followup("`取得交易列表發生錯誤.`", ephemeral=True)
    else:
        await ctx.send_followup(embed=embed, ephemeral=True)


async def get_trading_form(ctx, uuid: str):
    await ctx.defer(ephemeral=True)
    try:
        trading = TradingDB(ctx).get_trading(ctx, uuid)
        if trading is None:
            await ctx.send_followup("`查無資料, 檢查 uuid 是否正確, 僅限本人使用.`", ephemeral=True)
            return

        trading_id = trading.id
        trading_item_type = trading.item_type
        trading_title, trading_price, trading_currency, trading_description = get_trading_content(trading)
        trading_embed = TradingEmbed(trading_item_type, ctx.user, trading_title, trading_description, trading_price,
                                     trading_currency, trading_id)
        embed = trading_embed.get(trading.image_url, trading.end_time)
    except Exception as e:
        print(e)
        await ctx.send_followup("`取得交易表單發生錯誤.`", ephemeral=True)
    else:
        await ctx.send_followup(embed=embed, ephemeral=True)


async def set_end_time(ctx, uuid: str, end_time: str):
    await ctx.defer(ephemeral=True)
    try:
        if end_time == "0":
            end_time = None
        else:
            end_time = parse_date(end_time)
        trading_db = TradingDB(ctx)
        trading = trading_db.get_trading(ctx, uuid)
        if trading is None:
            await ctx.send_followup("`查無資料, 檢查 uuid 是否正確, 僅限本人使用.`", ephemeral=True)
            return
        trading.end_time = end_time
        trading_db.upsert(trading)

    except ValueError as e:
        print(e)
        await ctx.send_followup(e, ephemeral=True)
    except Exception as e:
        print(e)
        await ctx.send_followup("`發生錯誤, 檢查 uuid 是否正確.`", ephemeral=True)
    else:
        await ctx.send_followup("`設定拍賣結束時間成功.`", ephemeral=True)
        await update_message(ctx, uuid)


async def del_image(ctx, uuid: str, filename):
    await ctx.defer(ephemeral=True)
    try:
        delete_image(ctx, uuid, filename)
    except Exception as e:
        print(e)
        await ctx.send_followup("`刪除圖片發生錯誤, 檢查 uuid & 檔名(含副檔名) 是否正確.`", ephemeral=True)
    else:
        await ctx.send_followup("`刪除圖片成功.`", ephemeral=True)
        await update_message(ctx, uuid)


async def close_trading(ctx, uuid: str, btn=False):
    if btn:
        _ctx = ctx.response
    else:
        _ctx = ctx
    await _ctx.defer(ephemeral=True)
    try:
        trading_db = TradingDB(ctx)
        trading = trading_db.get_trading(ctx, uuid)
        if trading is None:
            if btn:
                await ctx.followup.send("`查無資料, 檢查 uuid 是否正確, 僅限本人使用.`", ephemeral=True)
            else:
                await _ctx.send_followup("`查無資料, 檢查 uuid 是否正確, 僅限本人使用.`", ephemeral=True)
            return
        trading.status = False
        trading_db.upsert(trading)
    except Exception as e:
        print(e)
        if btn:
            await ctx.followup.send("`關閉交易發生錯誤.`", ephemeral=True)
        else:
            await _ctx.send_followup("`關閉交易發生錯誤.`", ephemeral=True)
    else:
        if btn:
            await ctx.followup.send("`關閉交易成功.`", ephemeral=True)
        else:
            await _ctx.send_followup("`關閉交易成功.`", ephemeral=True)
        trading_message = await update_message(ctx, uuid, close=True)
        await trading_message.edit(view=TradingBuyButtonView(disabled=True))


async def check_trading_end_time(ctx):
    now = datetime.utcnow() + timedelta(hours=8)
    now_timestamp = now.timestamp()
    trading_db = TradingDB(ctx)
    trading_list = trading_db.get_tradings()
    for trading in trading_list:
        if trading.end_time is None:
            continue
        end_time = trading.end_time.timestamp()
        if end_time < now_timestamp:
            trading.status = False
            trading_channel_id = trading_setting(f"V{trading.version}").get(trading.item_type)
            trading_channel = ctx.get_channel(int(trading_channel_id))
            trading_message = await trading_channel.fetch_message(trading.message_id)
            view = TradingBuyButtonView(disabled=True)
            await trading_message.edit(view=view)
            trading_db.upsert(trading)

    trading_db.close()
    return

