import discord
from discord.ext import commands

class Webull(commands.Cog):
    def __init__(self, bot, brokerClass):
        self.bot = bot
        self.Broker = brokerClass

    @commands.command(name='sendWebullMfaCode', aliases=['sendwebullmfacode', 'sendWebullCode','sendWebullMFA'])
    @commands.dm_only()
    async def sendWebullMfaCode(self, ctx):
        # validate user has an account AND that he setup his webull email
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

        await ctx.send('Webull MFA code has been send to {}'.format(webull_account['brokerUsername']))
