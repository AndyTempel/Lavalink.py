import asyncio

import discord
from discord.ext import commands
from utils import lavalink


class Music:
    def __init__(self, bot):
        self.bot = bot
        self.lavalink = lavalink.Client(bot=bot, shard_count=len(self.bot.shards), user_id=self.bot.user.id, password='youshallnotpass', loop=self.bot.loop)

        self.state_keys = {}
        self.validator = ['op', 'guildId', 'sessionId', 'event']

    @commands.command(aliases=['p'])
    async def play(self, ctx, *, query):
        query = query.strip('<>')

        if not query.startswith('http'):
            query = f'ytsearch:{query}'

        tracks = await self.lavalink.get_tracks(query)

        if not self.lavalink.connected:
            await self.lavalink.join(guild_id=ctx.guild.id, channel_id=ctx.author.voice.channel.id)
        
        await self.lavalink.play(track=tracks[0]['track'])

        embed = discord.Embed(title="Now Playing", description=f'[{tracks[0]["info"]["title"]}]({tracks[0]["info"]["uri"]})')
        await ctx.send(embed=embed)
    
    async def on_voice_server_update(self, data):
        self.state_keys.update({ 
            'op': 'voiceUpdate',
            'guildId': data.get('guild_id'),
            'event': data
        })

        await self.verify_and_dispatch()

    async def on_voice_state_update(self, member, before, after):
        if member.id == self.bot.user.id:
            self.state_keys.update({ 'sessionId': after.session_id })
        
        await self.verify_and_dispatch()

    async def verify_and_dispatch(self):
        if all(k in self.state_keys for k in self.validator):
            await self.lavalink.dispatch_voice_update(self.state_keys)
            self.state_keys.clear()

def setup(bot):
    bot.add_cog(Music(bot))