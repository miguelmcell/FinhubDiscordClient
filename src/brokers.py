import discord
import os
import json
from discord.ext import commands
from webull import Webull
from apiUtil import call_get_request,call_post_request,handle_api_response
from dotenv import load_dotenv

ENDPOINTS = {}
load_dotenv()
endpoints_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),'resources','endpoints.json')
ENVIRONMENT = os.getenv('ENVIRONMENT')

class Brokers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.add_cog(Webull(self.bot, self))
        global ENDPOINTS
        with open(endpoints_path) as file:
            data = file.read()
        ENDPOINTS = json.loads(data)

    @staticmethod
    async def getUser(ctx):
        url = ENDPOINTS[ENVIRONMENT]['host']+ENDPOINTS[ENVIRONMENT]['finhub_get_user']
        headers = {"discordId": str(ctx.message.author.id)}
        r = await call_get_request(ctx, url, headers=headers)
        print('first print:', r)
        if await handle_api_response(ctx, r) is None:
            return
        if r.text == '':
            # No user was found
            return None
        response = r.json()
        return response
