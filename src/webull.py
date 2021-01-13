import discord
from discord.ext import commands
from apiUtil import call_get_request,call_post_request,handle_api_response

class Webull(commands.Cog):
    def __init__(self, bot, brokerClass, ENDPOINTS, ENVIRONMENT):
        self.bot = bot
        self.Broker = brokerClass
        self.ENDPOINTS = ENDPOINTS
        self.ENVIRONMENT = ENVIRONMENT

    @commands.command(name='addWebullBroker', \
         help='Adds a user\'s webull account to their finhub account',
         aliases=['addWebull'])
    @commands.dm_only()
    async def addWebullBroker(self, ctx, webullEmail=None):
        if webullEmail is None:
            await ctx.send('Add your webull email after the command,'\
            ' ex: `!addWebullBroker webull@gmail.com`')
            return
        # validate user has a finbhub account
        user = await self.Broker.getUser(ctx)
        if user is None:
            await ctx.send('Unable to find a finhub discord server associated with user')
            return
        elif user['discordId'] != str(ctx.message.author.id):
            await ctx.send('Request discordId does not match own userId')
            return
        # TODO check if a webull broker already exists for this finhub account
        found_webull = False
        user_broker_accounts = user['brokers']
        for broker in user_broker_accounts:
            if broker['name'] == 'webull':
                found_webull = True
        if found_webull:
            await ctx.send('User already has a webull account added to finhub,'\
            ' enter !webull to look at your webull account status')
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
        elif user['discordId'] != str(ctx.message.author.id):
            await ctx.send('Request discordId does not match own userId')
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
            await ctx.send('Run `!addWebullBroker` before changing email 🙂')
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
        elif user['discordId'] != str(ctx.message.author.id):
            await ctx.send('Request discordId does not match own userId')
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

        await ctx.send('Webull MFA code has been sent to {}, use MFA code to connect to your webull account using `!syncWebull`\nuse `help !connect` for more info'.format(webull_account['brokerUsername']))

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
        elif user['discordId'] != str(ctx.message.author.id):
            await ctx.send('Request discordId does not match own userId')
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
            await ctx.send('Run `!addWebullBroker` before connecting to account 🙂')
            return
        # call sync endpoint
        url = self.ENDPOINTS[self.ENVIRONMENT]['host']+self.ENDPOINTS[self.ENVIRONMENT]['webull']['sync_webull']
        data = {'discordId': ctx.message.author.id, 'email': webull_account['brokerUsername'], 'password': password, 'mfaCode': mfaCode}
        r = await call_post_request(ctx, url, data=data)
        if await handle_api_response(ctx, r) is None:
            return

        await ctx.send('Webull is now synced into your account!, run `!status` for an overview of your account status')
