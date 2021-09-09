# © lambda#0987 <lambda@lambda.dance>
# SPDX-License-Identifier: AGPL-3.0-or-later

import contextlib

import nextcord
from nextcord.ext import commands

import utils


class Meta(commands.Cog):
    # TODO does this need to be configurable?
    INVITE_DURATION_SECONDS = 60 * 60 * 3
    MAX_INVITE_USES = 5

    def __init__(self, bot):
        self.bot = bot
        self.support_channel = None
        self.task = bot.loop.create_task(self.cache_invite_channel())

    def cog_unload(self):
        self.task.cancel()

    async def cache_invite_channel(self):
        self.support_channel = ch = await self.bot.fetch_channel(self.bot.config['support_server_invite_channel'])
        return ch

    @commands.command()
    async def support(self, context):
        """Directs you to the support server."""
        ch = self.support_channel or await self.cache_invite_channel()

        reason = f'Created for {context.author} (ID: {context.author.id})'
        invite = await ch.create_invite(
            max_age=self.INVITE_DURATION_SECONDS,
            max_uses=self.MAX_INVITE_USES,
            reason=reason,
        )

        try:
            await context.author.send(f'Official support server invite: {invite}')
        except nextcord.Forbidden:
            with contextlib.suppress(nextcord.HTTPException):
                await context.message.add_reaction(utils.SUCCESS_EMOJIS[True])
            with contextlib.suppress(nextcord.HTTPException):
                await context.send('Unable to send invite in DMs. Please allow DMs from server members.')
        else:
            try:
                await context.message.add_reaction('📬')
            except nextcord.HTTPException:
                with contextlib.suppress(nextcord.HTTPException):
                    await context.send('📬')

    @commands.command(aliases=['inv']) # https://discordapi.com/permissions.html
    async def invite(self, context):
        """Gives you a link to add me to your server."""

        await context.send('<%s>' % nextcord.utils.oauth_url(self.bot.user.id, permissions=nextcord.Permissions(permissions=1074056256)))


def setup(bot):
    bot.add_cog(Meta(bot))

    if not bot.config.get('support_server_invite_channel'):
        bot.remove_command('support')
