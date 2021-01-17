import discord
from discord.ext import commands
from datetime import datetime
import constants as consts
from apiUtil import call_get_request,call_post_request,handle_api_response

class Robinhood(commands.Cog):
    def __init__(self, bot, brokerClass, ENDPOINTS, ENVIRONMENT):
        self.bot = bot
        self.Broker = brokerClass
        self.ENDPOINTS = ENDPOINTS
        self.ENVIRONMENT = ENVIRONMENT

    @commands.command(name='addRobinhood', \
         help='Adds a user\'s robinhood account to their finhub account',
         aliases=['addRobinhoodBroker'])
    @commands.dm_only()
    async def addRobinhoodBroker(self, ctx, robinhood_username=None, robinhood_password=None, mfa=None):
        if robinhood_username is None or robinhood_password is None or mfa is None:
            await ctx.send('Add your robinhood username, password, and MFA code from google auth,'\
            ' ex: `!addRobinhood (robinhood username) (robinhood password) (robinhood MFA code)`')
            return
        # validate user has a finbhub account
        user = await self.Broker.getUser(ctx)
        if user is None:
            await ctx.send(consts.FINHUB_ACCT_NOT_FOUND_FOR_DISCORD_ID)
            return
        found_robinhood = False
        user_broker_accounts = user['brokers']
        for broker in user_broker_accounts:
            if broker['name'] == 'robinhood':
                found_robinhood = True
        if found_robinhood:
            await ctx.send('User already has a robinhood account added to finhub,'\
            ' enter !robinhood to look at your webull account status')
            return
        url = self.ENDPOINTS[self.ENVIRONMENT]['host']+self.ENDPOINTS[self.ENVIRONMENT]['robinhood']['add_account']
        data = {'discordId': ctx.message.author.id, 'username': robinhood_username, "password":robinhood_password, "mfaCode": mfa}
        r = await call_post_request(ctx, url, data=data)
        if await handle_api_response(ctx, r) is None:
            return
        await ctx.send('Succesfully registered robinhood acount, enter `!robinhood` to look at your robinhood account status')

    @commands.command(name='syncRobinhood', \
         help='Connects to the user\'s robinhood account to fetch a new logged in session',
         aliases=['syncrobinhood'])
    @commands.dm_only()
    async def syncWebull(self, ctx, password, mfa_code):
        user = await self.Broker.getUser(ctx)
        if user is None:
            await ctx.send(consts.FINHUB_ACCT_NOT_FOUND_FOR_DISCORD_ID)
            return

        user_broker_accounts = user['brokers']
        found_robinhood = False
        robinhood_account = {}
        for broker in user_broker_accounts:
            if broker['name'] == 'robinhood':
                found_robinhood = True
                robinhood_account = broker
        if not found_robinhood:
            await ctx.send('Run `!addRobinhood` before connecting to account 🙂')
            return
        # call sync endpoint
        url = self.ENDPOINTS[self.ENVIRONMENT]['host']+self.ENDPOINTS[self.ENVIRONMENT]['robinhood']['sync_robinhood']
        data = {'discordId': ctx.message.author.id, 'username': robinhood_account['brokerUsername'], 'password': password, 'mfaCode': mfa_code}
        r = await call_post_request(ctx, url, data=data)
        if await handle_api_response(ctx, r) is None:
            return

        await ctx.send('Robinhood is now synced into your account!, run `!robinhood` for an overview of your account status')

    @commands.command(name='changeRobinhoodUsername', \
         help='Sets the user\'s robinhood username to their finhub account',
         aliases=['setRobinhoodUsername'])
    @commands.dm_only()
    async def changeRobinhoodUsername(self, ctx, robinhoodUsername):
        # validate user has a finbhub account
        user = await self.Broker.getUser(ctx)
        if user is None:
            await ctx.send(consts.FINHUB_ACCT_NOT_FOUND_FOR_DISCORD_ID)
            return

        # check if broker account exists for user,
        # if not then tell them to add an account,
        # otherwise change email to existing webull account
        user_broker_accounts = user['brokers']
        found_robinhood = False
        robinhood_account = {}
        for broker in user_broker_accounts:
            if broker['name'] == 'robinhood':
                found_robinhood = True
                robinhood_account = broker
        if not found_robinhood:
            # tell them to add webull account first
            await ctx.send('Run `!addWebullBroker` before changing email 🙂')
        else:
            # change existing webull email
            pass
    # TODO create syncRobinhood function for when accounts expire
    @commands.command(name='updateRobinhood', \
         help='Manually updates user\'s robinhood account metrics, otherwise metrics will update every hour',
         aliases=['updateR'])
    @commands.dm_only()
    async def updateRobinhood(self, ctx):
        # validate user has a finbhub account
        user = await self.Broker.getUser(ctx)
        if user is None:
            await ctx.send(consts.FINHUB_ACCT_NOT_FOUND_FOR_DISCORD_ID)
            return

        user_broker_accounts = user['brokers']
        found_robinhood = False
        robinhood_account = {}
        for broker in user_broker_accounts:
            if broker['name'] == 'robinhood':
                found_robinhood = True
                robinhood_account = broker
        if not found_robinhood:
            # tell them to add webull account first
            await ctx.send('Run `!addRobinhood` before connecting to account 🙂')
            return
        # TODO CHECK IF EXPIRATION HAS PAST, IF SO THEN SET ACCOUNT TO INACTIVE AND TELL USER
        expiration_date = datetime.strptime(robinhood_account['brokerTokenExpiration'], '%Y-%m-%dT%H:%M:%S.%f%z')
        if expiration_date.date() < datetime.now().date():
            # TODO send API call to change status to inactive
            await ctx.send('Robinhood account session has ended, run `!syncRobinhood` to renew connection')
            return

        # call update endpoint
        url = self.ENDPOINTS[self.ENVIRONMENT]['host']+self.ENDPOINTS[self.ENVIRONMENT]['robinhood']['update_metrics']
        data = {'discordId': ctx.message.author.id}
        r = await call_post_request(ctx, url, data=data)
        if await handle_api_response(ctx, r) is None:
            return

        await ctx.send('Update Successful, run `!robinhood` to look at your updated status')

    @commands.command(name='robinhood', \
         help='Displays account status for robinood, will display metrics if account is active')
    @commands.dm_only()
    async def robinhood(self, ctx):
        # validate user has a finbhub account
        user = await self.Broker.getUser(ctx)
        if user is None:
            await ctx.send(consts.FINHUB_ACCT_NOT_FOUND_FOR_DISCORD_ID)
            return

        user_broker_accounts = user['brokers']
        found_robinhood = False
        robinhood_account = {}
        for broker in user_broker_accounts:
            if broker['name'] == 'robinhood':
                found_robinhood = True
                robinhood_account = broker
        if not found_robinhood:
            # tell them to add webull account first
            await ctx.send('Robinhood Account Status:\n\t• No robinhood account has been added to your finhub profile')
            return
        
        robinhood_status = '{} ✅'.format(robinhood_account['status']) if robinhood_account['status']=='active' else '{}'.format(robinhood_account['status'])
        
        response = '**Robinhood Account**:\n\t• Status: {}\n\t• Email: {}'.format(robinhood_status, robinhood_account['brokerUsername'])
        if robinhood_account['status']=='active':
            expiration_time = datetime.strptime(robinhood_account['brokerTokenExpiration'], '%Y-%m-%dT%H:%M:%S.%f%z')
            response += expiration_time.strftime('\n\t• Account Session Expiration: %d, %b %Y at %H:%M %Z ⏰')

            performance_metrics = robinhood_account['performanceMetrics']
            last_updated_time = datetime.strptime(performance_metrics['lastUpdate'], '%Y-%m-%dT%H:%M:%S.%f%z')
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

        await ctx.send(response)
