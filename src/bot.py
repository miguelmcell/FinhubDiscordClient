import os
import json
from discord.ext import commands
from dotenv import load_dotenv
import discord
from brokers import Brokers
from apiUtil import call_get_request,call_post_request,handle_api_response

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
ENVIRONMENT = os.getenv('ENVIRONMENT')
ENDPOINTS = {}
endpoints_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),'resources','endpoints.json')

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.members = True
help_command = commands.DefaultHelpCommand(
    no_category = 'Main Commands'
)
bot = commands.Bot(command_prefix='!', help_command=help_command, intents =intents, description='Finhub Discord Client')
if __name__ == '__main__':
    bot.add_cog(Brokers(bot))

def setup_init():
    ### Loading endpoints file
    global ENDPOINTS
    with open(endpoints_path) as file:
        data = file.read()
    ENDPOINTS = json.loads(data)

def is_dm(ctx):
    return not ctx.message.guild

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name='health', help='Provides status of finhub backend')
@commands.guild_only()
async def check_health(ctx):
    url = ENDPOINTS[ENVIRONMENT]['host']+ENDPOINTS[ENVIRONMENT]['finhub_test_status']
    r = await call_get_request(ctx, url)
    if await handle_api_response(ctx, r) is None:
        return
    ### r should now be a valid response
    if r.json() == 'OK':
        await ctx.send('Finhub is active ✅')
    else:
        await ctx.send('Unexpected response from finhub status')

@bot.command(name='signUp', help='Signs up the user to the server\'s finhub group', aliases=['register, signup'])
@commands.guild_only()
async def signup_user(ctx):
    url = ENDPOINTS[ENVIRONMENT]['host']+ENDPOINTS[ENVIRONMENT]['finhub_signup_user']
    data = {}

    data['discordId'] = ctx.message.author.id
    data['guildId'] = ctx.message.guild.id
    data['guildName'] = ctx.message.guild.name
    r = await call_post_request(ctx, url, data)
    if await handle_api_response(ctx, r) is None:
        return
    ## r should now be a valid response
    if 'Existing user added to new finhub group' in r.content.decode('utf-8'):
        print('Succesfully added {} '.format(ctx.message.author.name))
        await ctx.send('Successfully added {} to **{}**\'s finhub group 🎉 💯 🗣️'.format(ctx.message.author.name, ctx.message.guild.name))
    elif 'User already in given finhub group' in r.content.decode('utf-8'):
        print('{} is already in **{}**\'s finhub group'.format(ctx.message.author.name, ctx.message.guild.name))
        await ctx.send('{} is already in **{}**\'s finhub group 🤷'.format(ctx.message.author.name, ctx.message.guild.name))
    elif 'OK' in r.content.decode('utf-8'):
        print('Succesfully signed up {}'.format(ctx.message.author.name))
        await ctx.message.author.create_dm()
        await ctx.message.author.dm_channel.send(f'Yo, If you\'ve'\
        ' already configured your brokers for another discord server that'\
        ' uses finhub then you\'re already set, otherwise to learn how to'\
        ' sync your robinhood account, enter `!robinhoodSteps`, as for webull'\
        ' enter `!webullSteps` or `!help addWebullBroker` for a walkthrough.'\
        ' \n**Its recommended to deletete any sensitive broker credentials once'\
        ' your broker accounts have been synced, your password will not be'\
        ' stored in your finhub account**')
        await ctx.send('Successfully signed up {} to **{}**\'s finhub group 🎉 💯 🗣️\nI DMd you instructions on how to configure your brokers on your account'.format(ctx.message.author.name, ctx.message.guild.name))
    else:
        print('Unkown response from signup: {}, {}'.format(r, r.content.decode('utf-8')))


@bot.command(name='listUsers', help='Lists all active finhub users within server', aliases=['users'])
@commands.guild_only()
async def list_users(ctx):
    url = ENDPOINTS[ENVIRONMENT]['host']+ENDPOINTS[ENVIRONMENT]['finhub_list_users']
    headers = {"guildId": str(ctx.message.guild.id)}
    r = await call_get_request(ctx, url, headers=headers)
    if await handle_api_response(ctx, r) is None:
        return
    ### r should now be a valid response
    r = r.json()
    if len(r) == 0:
        await ctx.send('No active finhub members in **{}** 😔'.format(ctx.message.guild.name))
        return
    # Map IDs to user names
    guild_members = {}
    for member in  ctx.guild.members:
        guild_members[str(member.id)] = member.name
    response = 'Active finhub members in **{}**:'.format(ctx.message.guild.name)
    for i in r:
        response = response + '\n\t• {}'.format(guild_members[i.strip('\'')])
    await ctx.send(response)

setup_init()
bot.run(TOKEN)
