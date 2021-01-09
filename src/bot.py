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
    
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name='health', help='Provides status of finhub backend')
async def check_health(ctx):
    if is_dm(ctx):
        await ctx.send('cant call function in DM')
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

# async def check_health(ctx, a_number: int, another: int):
#     # print(ctx)
#     await ctx.send('hello!'+str(a_number+another))
setup_init()
bot.run(TOKEN)
