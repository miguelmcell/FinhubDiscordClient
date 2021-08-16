import discord
import os
import json
from discord.ext import commands
from webull import Webull
from robinhood import Robinhood
from apiUtil import call_get_request,call_post_request,handle_api_response
from datetime import datetime
from dateutil import parser
from dotenv import load_dotenv

ENDPOINTS = {}
load_dotenv()
endpoints_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),'resources','endpoints.json')
ENVIRONMENT = os.getenv('ENVIRONMENT')

class Brokers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        global ENDPOINTS
        with open(endpoints_path) as file:
            data = file.read()
        ENDPOINTS = json.loads(data)
        self.bot.add_cog(Webull(self.bot, self, ENDPOINTS, ENVIRONMENT))
        self.bot.add_cog(Robinhood(self.bot, self, ENDPOINTS, ENVIRONMENT))

    @staticmethod
    async def getUser(ctx):
        url = ENDPOINTS[ENVIRONMENT]['host']+ENDPOINTS[ENVIRONMENT]['finhub_get_user']
        headers = {"discordId": str(ctx.message.author.id)}
        r = await call_get_request(ctx, url, headers=headers)
        if await handle_api_response(ctx, r) is None:
            return
        if r.text == '':
            # No user was found
            return None
        response = r.json()
        return response

    @commands.command(name='overview', \
         help='Displays overview status for all broker accounts, will display metrics if account is active',
         aliases=['all'])
    @commands.dm_only()
    async def overview(self, ctx):
        # validate user has a finbhub account
        user = await self.getUser(ctx)
        if user is None:
            await ctx.send('Unable to find a finhub discord server associated with user')
            return

        user_broker_accounts = user['brokers']
        found_robinhood = False
        found_webull = False
        robinhood_account = {}
        webull_account = {}
        for broker in user_broker_accounts:
            if broker['name'] == 'robinhood':
                found_robinhood = True
                robinhood_account = broker
            elif broker['name'] == 'webull':
                found_webull = True
                webull_account = broker
        if found_webull is False and found_robinhood is False:
            await ctx.send('No brokers have been added to this account')
            return
        
        response = ''

        if found_robinhood:
            robinhood_status = '{} ✅'.format(robinhood_account['status']) if robinhood_account['status']=='active' else '{}'.format(robinhood_account['status'])
            
            response += '\n**Robinhood Account**:\n\t• Status: {}\n\t• Email: {}'.format(robinhood_status, robinhood_account['brokerUsername'])
            if robinhood_account['status']=='active':
                expiration_time = parser.parse(robinhood_account['brokerTokenExpiration'])
                response += expiration_time.strftime('\n\t• Account Session Expiration: %d, %b %Y at %H:%M %Z') + ' ⏰'

                performance_metrics = robinhood_account['performanceMetrics']
                last_updated_time = parser.parse(performance_metrics['lastUpdate'])
                last_updated_response = last_updated_time.strftime('%d, %b %Y at %H:%M %Z')

                performance_response = '\n**Performance**:\n\t• Last Time Updated: {}\n\t• Overall: {:0.2f}%\
                    \n\t• Daily: {:0.2f}%\n\t• Weekly: {:0.2f}%\n\t• Monthly: {:0.2f}%'\
                    .format(last_updated_response, performance_metrics['overall'], performance_metrics['daily'],\
                    performance_metrics['weekly'], performance_metrics['monthly'])
                stock_positions_response = '\n**Positions**:' if len(robinhood_account['positions']) > 0 else '\n**No positions**'
                for position in robinhood_account['positions']:
                    position['percentage'] = float(position['percentage'])
                    stock_positions_response += '\n\t• {}\n\t\t• Portfolio Percentage: {}%'.format(position['stockName'], position['percentage'])
                response += performance_response + stock_positions_response
            if found_webull:
                response += '\n------------------------'

        if found_webull:
            webull_status = '{} ✅'.format(webull_account['status']) if webull_account['status']=='active' else '{}'.format(webull_account['status'])
            
            response += '\n**Webull Account**:\n\t• Status: {}\n\t• Email: {}'.format(webull_status, webull_account['brokerUsername'])
            if webull_account['status']=='active':
                expiration_time = datetime.strptime(webull_account['brokerTokenExpiration'], '%Y-%m-%dT%H:%M:%S.%f%z')
                response += expiration_time.strftime('\n\t• Account Session Expiration: %d, %b %Y at %H:%M %Z') + ' ⏰'

                performance_metrics = webull_account['performanceMetrics']
                last_updated_time = datetime.strptime(performance_metrics['lastUpdate'], '%Y-%m-%dT%H:%M:%S.%f%z')
                last_updated_response = last_updated_time.strftime('%d, %b %Y at %H:%M %Z')

                performance_response = '\n**Performance**:\n\t• Last Time Updated: {}\n\t• Overall: {:0.2f}%\
                    \n\t• Daily: {:0.2f}%\n\t• Weekly: {:0.2f}%\n\t• Monthly: {:0.2f}%'\
                    .format(last_updated_response, performance_metrics['overall'], performance_metrics['daily'],\
                    performance_metrics['weekly'], performance_metrics['monthly'])
                stock_positions_response = '\n**Positions**:' if len(webull_account['positions']) > 0 else '\n**No positions**'
                for position in webull_account['positions']:
                    position['percentage'] = float(position['percentage'])
                    stock_positions_response += '\n\t• {}\n\t\t• Portfolio Percentage: {}%'.format(position['stockName'], position['percentage'])
                response += performance_response + stock_positions_response

        await ctx.send(response)
