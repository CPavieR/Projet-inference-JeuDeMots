import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)#

@bot.event
async def on_ready():
    print(f'Bot connecté en tant que {bot.user}')

@bot.command()
async def salut(ctx):
    #print the massege
    await ctx.send('Salut !')
    
@bot.command()
async def secret(ctx):
    
    await ctx.send("ssdrfg")

#read the token from the file
file = open("token.txt", "r")
token = file.read()
file.close()
bot.run(token)
