import discord
from discord.ext import commands
from temp import callFromDiscord
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)#

@bot.event
async def on_ready():
    print(f'Bot connecté en tant que {bot.user}')

@bot.command()
async def salut(ctx):
    
    await ctx.send('Salut !')
    
@bot.command()
async def secret(ctx, *, message_content):
    # Capture the content of the message after the command
    processed_content = callFromDiscord(message_content)

    # Send the processed content back to the channel
    await ctx.send(processed_content)

#read the token from the file
file = open("token.txt", "r")
token = file.read()
file.close()
bot.run(token)
