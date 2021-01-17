import discord
from discord.ext import commands
from datetime import datetime
from apiUtil import call_get_request,call_post_request,handle_api_response

class Webull(commands.Cog):
    def __init__(self, bot, brokerClass, ENDPOINTS, ENVIRONMENT):
        self.bot = bot
        self.Broker = brokerClass
        self.ENDPOINTS = ENDPOINTS
        self.ENVIRONMENT = ENVIRONMENT

    @commands.command(name='addWebull', \
         help='Adds a user\'s webull account to their finhub account',
         aliases=['addWebullBroker'])
    @commands.dm_only()
    async def addWebull(self, ctx, webullEmail=None):
        if webullEmail is None:
            await ctx.send('Add your webull email after the command,'\
            ' ex: `!addWebull webull@gmail.com`')
            return
        # validate user has a finbhub account
        user = await self.Broker.getUser(ctx)
        if user is None:
            await ctx.send('Unable to find a finhub discord server associated with user')
            return
        found_webull = False
        user_broker_accounts = user['brokers']
        for broker in user_broker_accounts:
            if broker['name'] == 'webull':
                found_webull = True
        if found_webull:
            await ctx.send('User already has a webull account added to finhub,'\
            ' enter `!webull` to look at your webull account status')
            return
        url = self.ENDPOINTS[self.ENVIRONMENT]['host']+self.ENDPOINTS[self.ENVIRONMENT]['webull']['add_account']
        data = {'discordId': ctx.message.author.id, 'email': webullEmail}
        r = await call_post_request(ctx, url, data=data)
        if await handle_api_response(ctx, r) is None:
            return
        await ctx.send('Succesfully registered webull acount, enter `!sendWebullMfaCode` to receive MFA needed to login')

    @commands.command(name='changeWebullEmail', \
         help='Sets the user\'s webull email to their finhub account',
         aliases=['setWebullEmail'])
    @commands.dm_only()
    async def changeWebullEmail(self, ctx, webullEmail):
        # validate user has a finbhub account
        user = await self.Broker.getUser(ctx)
        if user is None:
            await ctx.send('Unable to find a finhub discord server associated with user')
            return

        print(f'webull email is {webullEmail}')
        # check if broker account exists for user,
        # if not then tell them to add an account,
        # otherwise change email to existing webull account
        user_broker_accounts = user['brokers']
        found_webull = False
        webull_account = {}
        for broker in user_broker_accounts:
            if broker['name'] == 'webull':
                found_webull = True
                webull_account = broker
        if not found_webull:
            # tell them to add webull account first
            await ctx.send('Run `!addWebull` before changing email 🙂')
        else:
            # change existing webull email
            pass

    @commands.command(name='sendWebullMfaCode', \
        aliases=['sendwebullmfacode', 'sendWebullCode','sendWebullMFA'],\
         help='Sends an MFA code to the user\'s webull email, required '\
         ' to connect to their webull account' )
    @commands.dm_only()
    async def sendWebullMfaCode(self, ctx):
        # validate user has a finbhub account AND that he setup his webull email
        user = await self.Broker.getUser(ctx)
        if user is None:
            await ctx.send('Unable to find a finhub discord server associated with user')
            return
        user_broker_accounts = user['brokers']
        is_valid_webull = False
        webull_account = {}
        for broker in user_broker_accounts:
            if broker['name'] == 'webull' and broker['brokerUsername'] != '' and broker['brokerUsername'] is not None:
                is_valid_webull = True
                webull_account = broker
        if not is_valid_webull:
            await ctx.send('Webull email must be setup before MFA code can be sent')
            return

        url = self.ENDPOINTS[self.ENVIRONMENT]['host']+self.ENDPOINTS[self.ENVIRONMENT]['webull']['send_mfa']
        data = {'discordId': ctx.message.author.id}
        r = await call_post_request(ctx, url, data=data)
        if await handle_api_response(ctx, r) is None:
            return

        await ctx.send('Webull MFA code has been sent to {}, use MFA code to connect to your webull account using `!syncWebull`\nuse `help !syncWebull` for more info'.format(webull_account['brokerUsername']))
    # TODO add overall for both webull and robinhood
    @commands.command(name='syncWebull', \
         help='Connects to the user\'s webull account to sync performance and holdings',
         aliases=['syncwebull'])
    @commands.dm_only()
    async def syncWebull(self, ctx, password, mfaCode):
        # validate user has a finbhub account
        # print("PASSWORD IS:", password.strip('"'))
        user = await self.Broker.getUser(ctx)
        if user is None:
            await ctx.send('Unable to find a finhub discord server associated with user')
            return

        user_broker_accounts = user['brokers']
        found_webull = False
        webull_account = {}
        for broker in user_broker_accounts:
            if broker['name'] == 'webull':
                found_webull = True
                webull_account = broker
        if not found_webull:
            # tell them to add webull account first
            await ctx.send('Run `!addWebull` before connecting to account 🙂')
            return
        # call sync endpoint
        url = self.ENDPOINTS[self.ENVIRONMENT]['host']+self.ENDPOINTS[self.ENVIRONMENT]['webull']['sync_webull']
        data = {'discordId': ctx.message.author.id, 'email': webull_account['brokerUsername'], 'password': password, 'mfaCode': mfaCode}
        r = await call_post_request(ctx, url, data=data)
        if await handle_api_response(ctx, r) is None:
            return

        await ctx.send('Webull is now synced into your account!, run `!webull` for an overview of your account status')

    @commands.command(name='updateWebull', \
         help='Manually updates user\'s webull account metrics, otherwise metrics will update every hour',
         aliases=['updateW'])
    @commands.dm_only()
    async def updateWebull(self, ctx):
        # validate user has a finbhub account
        user = await self.Broker.getUser(ctx)
        if user is None:
            await ctx.send('Unable to find a finhub discord server associated with user')
            return

        user_broker_accounts = user['brokers']
        found_webull = False
        webull_account = {}
        for broker in user_broker_accounts:
            if broker['name'] == 'webull':
                found_webull = True
                webull_account = broker
        if not found_webull:
            # tell them to add webull account first
            await ctx.send('Run `!addWebull` before connecting to account 🙂')
            return
        # TODO CHECK IF EXPIRATION HAS PAST, IF SO THEN SET ACCOUNT TO INACTIVE AND TELL USER
        # call update endpoint
        url = self.ENDPOINTS[self.ENVIRONMENT]['host']+self.ENDPOINTS[self.ENVIRONMENT]['webull']['update_metrics']
        data = {'discordId': ctx.message.author.id}
        r = await call_post_request(ctx, url, data=data)
        if await handle_api_response(ctx, r) is None:
            return

        await ctx.send('Update Successful, run `!webull` to look at your updated status')

    @commands.command(name='webull', \
         help='Displays account status for webull, if connected account will display performance')
    @commands.dm_only()
    async def webull(self, ctx):
        # validate user has a finbhub account
        user = await self.Broker.getUser(ctx)
        if user is None:
            await ctx.send('Unable to find a finhub discord server associated with user')
            return

        user_broker_accounts = user['brokers']
        found_webull = False
        webull_account = {}
        for broker in user_broker_accounts:
            if broker['name'] == 'webull':
                found_webull = True
                webull_account = broker
        if not found_webull:
            # tell them to add webull account first
            await ctx.send('Webull Account Status:\n\t• No webull account has been added to your finhub profile, enter `!help addWebull` to more info')
            return
        
        webull_status = '{} ✅'.format(webull_account['status']) if webull_account['status']=='active' else '{}'.format(webull_account['status'])
        
        response = '**Webull Account**:\n\t• Status: {}\n\t• Email: {}'.format(webull_status, webull_account['brokerUsername'])
        if webull_account['status']=='active':
            expiration_time = datetime.strptime(webull_account['brokerTokenExpiration'], '%Y-%m-%dT%H:%M:%S.%f%z')
            response += expiration_time.strftime('\n\t• Account Session Expiration: %d, %b %Y at %H:%M %Z ⏰')

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
