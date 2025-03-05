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
    ctx.send("une question intéressante, je vais me renseigner :cat2:")
    # Send the processed content back to the channel
    if processed_content != "":
        await ctx.send(processed_content)
    else:
        await ctx.send("Je donne ma langue au chat ! :crying_cat_face:")

@bot.command()
async def ind(ctx, *, message_content):
    # Capture the content of the message after the command
    processed_content = callFromDiscordInduc(message_content)
    ctx.send("une question intéressante, je vais me renseigner :cat2:")
    # Send the processed content back to the channel
    if(processed_content != ""):
        await ctx.send(processed_content)
    else :
        await ctx.send("Je donne ma langue au chat ! :crying_cat_face:")

@bot.command()
async def all(ctx, *, message_content):
    # Capture the content of the message after the command
    processed_content = callFromDiscordAll(message_content)
    ctx.send("une question intéressante, je vais me renseigner :cat2:")
    # Send the processed content back to the channel
    if(processed_content != ""):
        ctx.send("AhAh , je connais la réponse ! :smirk_cat:")
        await ctx.send(processed_content)
    else :
        await ctx.send("Je donne ma langue au chat ! :crying_cat_face:")

@bot.command()
async def help(ctx, *, message_content):
    await ctx.send("Pour faire une inferérence sur une relation\n - tapez !ind sujet relation objet pour fair un induction\n - tapez !sym relation pour faire une synonimie\n - tapez !all sujet relation objet pour tout chercher\n")

#callFromDiscordAll
#read the token from the file
file = open("token.txt", "r")
token = file.read()
file.close()
bot.run(token)
