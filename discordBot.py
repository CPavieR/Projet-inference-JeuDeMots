import discord
from discord.ext import commands
from temp import callFromDiscordAll, callFromDiscordInduc
from temp import callFromDiscordSym
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
async def sym(ctx, *, message_content):
    # Capture the content of the message after the command
    processed_content = callFromDiscordSym(message_content)

    # Send the processed content back to the channel
    if processed_content != "":
        await ctx.send(processed_content)
    else:
        await ctx.send("Je n'ai rien trouvé")

@bot.command()
async def ind(ctx, *, message_content):
    # Capture the content of the message after the command
    processed_content = callFromDiscordInduc(message_content)

    # Send the processed content back to the channel
    if(processed_content != ""):
        await ctx.send(processed_content)
    else :
        await ctx.send("Je n'ai rien trouvé")

@bot.command()
async def all(ctx, *, message_content):
    # Capture the content of the message after the command
    processed_content = callFromDiscordAll(message_content)

    # Send the processed content back to the channel
    if(processed_content != ""):
        await ctx.send(processed_content)
    else :
        await ctx.send("Je n'ai rien trouvé")


#callFromDiscordAll
#read the token from the file
file = open("token.txt", "r")
token = file.read()
file.close()
bot.run(token)
