import os
import json
import requests
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
ENVIRONMENT = os.getenv('ENVIRONMENT')
ENDPOINTS = {}
endpoints_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),'resources','endpoints.json')

bot = commands.Bot(command_prefix='!')

def setup_init():
    ### Loading endpoints file
    global ENDPOINTS
    with open(endpoints_path) as file:
        data = file.read()
    ENDPOINTS = json.loads(data)

def is_dm(ctx):
    return not ctx.message.guild
### Check and handle any non-200 responses
async def handle_api_response(ctx, r):
    if r is None:
        print('couldnt contact server')
    if r.status_code == 200:
        return r
    elif r.status_code == 401:
        print('[401] Unauthorized request:', r)
        await ctx.send('[401] Unauthorized request 🔒')
    else:
        print(r)
        print('Other: response code:', r.status_code)
    return None
### Run get request while handling errors
async def call_get_request(ctx, url, params={}):
    r = None
    try:
        r = requests.get(url = url, params = params)
    except Exception as e:
        if 'Max retries exceeded with url' in str(e):
            await ctx.send('Hello anyone there? 👀 👀 👀 [Unable to contact backend]')
        else:
            print(e)
            await ctx.send('Unknown exception for API call request, check logs')
    return r
### Run get request while handling errors
async def call_post_request(ctx, url, data={}):
    r = None
    try:
        r = requests.post(url = url, json = data)
    except Exception as e:
        if 'Max retries exceeded with url' in str(e):
            await ctx.send('Hello anyone there? 👀 👀 👀 [Unable to contact backend]')
        else:
            print(e)
            await ctx.send('Unknown exception for API post request, check logs')
    return r

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name='health', help='Provides status of finhub backend')
async def check_health(ctx):
    if is_dm(ctx):
        await ctx.send('cant call this command in DM')
        return
    url = ENDPOINTS[ENVIRONMENT]['host']+ENDPOINTS[ENVIRONMENT]['finhub_test_status']
    r = await call_get_request(ctx, url)
    if await handle_api_response(ctx, r) is None:
        return
    ### r should now be a valid response
    if r.json() == 'OK':
        await ctx.send('Finhub is active ✅')
    else:
        await ctx.send('Unexpected response from finhub status')

@bot.command(name='signUp', help='Signs up the user to the server\'s finhub group')
async def signup_user(ctx):
    if is_dm(ctx):
        await ctx.send('cant call this command in DM')
        return
    url = ENDPOINTS[ENVIRONMENT]['host']+ENDPOINTS[ENVIRONMENT]['finhub_signup_user']
    data = {}
    # print(ctx.message.author.id)
    # print(ctx.message.guild.id)
    # print(ctx.message.guild.name)
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
        await ctx.send('Successfully signed up {} to **{}**\'s finhub group 🎉 💯 🗣️'.format(ctx.message.author.name, ctx.message.guild.name))
    else:
        print('Unkown response from signup: {}, {}'.format(r, r.content.decode('utf-8')))


@bot.command(name='listUsers', help='Lists all active finhub users within server')
async def list_users(ctx):
    if is_dm(ctx):
        await ctx.send('cant call this command in DM')
        return
    url = ENDPOINTS[ENVIRONMENT]['host']+ENDPOINTS[ENVIRONMENT]['finhub_list_users']
    r = await call_get_request(ctx, url)
    if await handle_api_response(ctx, r) is None:
        return
    ### r should now be a valid response
    print('Success!', r.json())

setup_init()
bot.run(TOKEN)
