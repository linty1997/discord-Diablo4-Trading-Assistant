from discord.ext import commands
import discord
from dotenv import load_dotenv
import os
import logging
from components.tasks import CheckTradingEndTimeTasks

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='bot.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

##############################

intents = discord.Intents.all()

token = os.getenv('TOKEN')
bot = discord.Bot(intents=intents)


for filename in os.listdir('./commands'):
    if filename.endswith('.py'):
        bot.load_extension(f'commands.{filename[:-3]}')
        print(f"load: {filename}")


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(name=f"Welcome!",
                                                        type=discord.ActivityType.watching))
    logger.info(f"機器人已上線 ID : {bot.user}")
    CheckTradingEndTimeTasks(bot)


@bot.event
async def shutdown():
    logger.info("正在關閉與 Discord 的連結...")


@bot.event
async def close():
    logger.info("中斷連結...")


@bot.event
async def on_error(event, *args, **kwargs):
    raise event


@bot.event
async def on_application_command_error(ctx, event):
    interaction = ctx.interaction
    try:
        if isinstance(event, discord.ext.commands.CommandOnCooldown):
            await interaction.response.send_message(f"{event}", ephemeral=True)
            return
        if isinstance(event, discord.ext.commands.MissingPermissions):
            await interaction.response.send_message(f"{event}", ephemeral=True)
            return
        if isinstance(event, discord.ext.commands.MissingRole):
            await interaction.response.send_message(f"{event}", ephemeral=True)
            return
        if isinstance(event, AttributeError):
            return
        if isinstance(event, TypeError):
            return

        await interaction.response.send_message(event, ephemeral=True)

    except Exception as e:
        logger.error(e)

    raise event


@bot.event
async def on_resumed():
    logger.info("機器人已恢復.")


@bot.event
async def on_disconnect():
    logger.info("機器人斷開連結.")


bot.run(token)


#                       _oo0oo_
#                      o8888888o
#                      88" . "88
#                      (| -_- |)
#                      0\  =  /0
#                    ___/`---'\___
#                  .' \\|     |// '.
#                 / \\|||  :  |||// \
#                / _||||| -:- |||||- \
#               |   | \\\  -  /// |   |
#               | \_|  ''\---/''  |_/ |
#               \  .-\__  '-'  ___/-. /
#             ___'. .'  /--.--\  `. .'___
#          ."" '<  `.___\_<|>_/___.' >' "".
#         | | :  `- \`.;`\ _ /`;.`/ - ` : | |
#         \  \ `_.   \_ __\ /__ _/   .-` /  /
#     =====`-.____`.___ \_____/___.-`___.-'=====
#                       `=---='
#
#
#     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#               佛祖保佑         永無BUG

