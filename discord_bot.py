from currency_grabber import get_currency_rate
import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv
from datetime import datetime


load_dotenv()
CHANNEL_ID = os.getenv("CHANNEL_ID")
OWNER_USER_ID = os.getenv("OWNER_USER_ID")
DISCORD_TOKEN = os.getenv("TOKEN")
CURRENCY_URL = os.getenv("CURRENCY_URL")
CURRENCY_NAME = os.getenv("CURRENCY_NAME")
CURRENCY_A_SYMBOL = os.getenv("CURRENCY_A_SYMBOL")
CURRENCY_B_SYMBOL = os.getenv("CURRENCY_B_SYMBOL")


with open("data.txt", "r") as file:
    data = file.read().split("\n")
    is_on = data[0].split("=")[1] == "True"
    alert_if_target_below_value = float(data[1].split("=")[1])
    previous_currency_rate = float(data[2].split("=")[1])
    only_display_change = data[3].split("=")[1] == "True"


bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# Async function that waits a minute before sending the currency rate
async def send_currency_rate():
    global previous_currency_rate
    if is_on:
        channel = bot.get_channel(int(CHANNEL_ID))
        date_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        rate = get_currency_rate(CURRENCY_NAME, CURRENCY_URL)
        if type(rate) == str:
            await channel.send(f"{owner.mention}: {rate}")
            await asyncio.sleep(60)
            await send_currency_rate()
            return
        if not only_display_change or rate != previous_currency_rate:
            if rate != previous_currency_rate:
                previous_currency_rate = rate
            owner = await bot.fetch_user(int(OWNER_USER_ID))
            if rate < alert_if_target_below_value:
                # Send with mention
                await channel.send(f"`{date_time_str}`: Current {CURRENCY_B_SYMBOL} to {CURRENCY_A_SYMBOL} rate is **{rate:.2f}**, threshold is <= {alert_if_target_below_value:.2f}. {owner.mention}")
            else:
                await channel.send(f"`{date_time_str}`: Current {CURRENCY_B_SYMBOL} to {CURRENCY_A_SYMBOL} rate is **{rate:.2f}**, threshold is <= {alert_if_target_below_value:.2f}.")
            with open("data.txt", "w") as file:
                file.write(f"is_on={is_on}\n")
                file.write("alert_if_target_below_value="+str(alert_if_target_below_value)+"\n")
                file.write("previous_currency_rate="+str(previous_currency_rate)+"\n")
                file.write(f"only_display_change={only_display_change}")
        await asyncio.sleep(60)
        await send_currency_rate()
        return

# Bot command that triggers the bot to start sending the currency rate
@bot.command(name="start", help="Starts the bot to send the currency rate")
async def start(ctx):
    global is_on
    if is_on:
        await ctx.send("Bot is already running")
    else:
        is_on = True
        with open("data.txt", "w") as file:
            file.write("is_on=True\n")
            file.write("alert_if_target_below_value="+str(alert_if_target_below_value))
            file.write("previous_currency_rate="+str(previous_currency_rate))
            file.write("only_display_change="+str(only_display_change))
        await ctx.send("Bot started")
        await send_currency_rate()

# Bot command that triggers the bot to stop sending the currency rate
@bot.command(name="stop", help="Stops the bot from sending the currency rate")
async def stop(ctx):
    global is_on
    if is_on:
        is_on = False
        with open("data.txt", "w") as file:
            file.write("is_on=False\n")
            file.write("alert_if_target_below_value="+str(alert_if_target_below_value))
            file.write("previous_currency_rate="+str(previous_currency_rate))
            file.write("only_display_change="+str(only_display_change))
        await ctx.send("Bot stopped")
    else:
        await ctx.send("Bot is not running")

# Bot command that adjusts the threshold for the bot to send an alert
@bot.command(name="threshold", help="Sets the threshold for the bot to send an alert")
async def threshold(ctx, value):
    # Be defensive, check if the value is a number
    try:
        value = float(value)
    except:
        await ctx.send("Please input a number")
        return
    global alert_if_target_below_value
    alert_if_target_below_value = value
    with open("data.txt", "w") as file:
        file.write("is_on="+str(is_on)+"\n")
        file.write("alert_if_target_below_value="+str(alert_if_target_below_value))
        file.write("previous_currency_rate="+str(previous_currency_rate))
        file.write("only_display_change="+str(only_display_change))
    await ctx.send(f"Threshold set to {alert_if_target_below_value:.2f}")

# Bot command that shows the current threshold, that displays command function when !help is called
@bot.command(name="status", help="Shows the current threshold")
async def status(ctx):
    await ctx.send(f"Bot is currently {'running' if is_on else 'stopped'}")
    await ctx.send(f"Threshold is currently set to {alert_if_target_below_value:.2f}")
    await ctx.send(f"Only display change is set to {only_display_change}")
    await ctx.send(f"Previous currency rate is {previous_currency_rate:.2f}")

# Bot command that toggles the only_display_change variable
@bot.command(name="toggle", help="Toggles the only_display_change variable")
async def toggle(ctx):
    global only_display_change
    only_display_change = not only_display_change
    with open("data.txt", "w") as file:
        file.write("is_on="+str(is_on)+"\n")
        file.write("alert_if_target_below_value="+str(alert_if_target_below_value))
        file.write("previous_currency_rate="+str(previous_currency_rate))
        file.write("only_display_change="+str(only_display_change))
    await ctx.send(f"Only display change is set to {only_display_change}")

# Show bot on connect, send message to the channel
@bot.event
async def on_connect():
    channel = await bot.fetch_channel(int(CHANNEL_ID))
    await channel.send("Bot is now connected")
    await channel.send(f"Initial Configuration: is_on={is_on}, alert_if_target_below_value={alert_if_target_below_value:.2f}, only_display_change={only_display_change}, previous_currency_rate={previous_currency_rate:.2f}")
    if is_on:
        await send_currency_rate()



bot.run(DISCORD_TOKEN)
