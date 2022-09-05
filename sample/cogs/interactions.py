import asyncio
import ast
import discord
from discord.ext import commands
from discord.commands import Option, SlashCommandGroup

import constants as CST


class Interactions(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # --------------------- slash commands ---------------------
    # called using / in discord (they can take up to an hour to appear in discord)

    # @commands.slash_command(brief='This is the brief description',
    #                         description="Get the last message of a text channel")
    # async def _get_last_message(self, ctx: discord.ApplicationContext,
    #                             identifiant: Option(str,
    #                                                 description="id of the channel",
    #                                                 required=True,
    #                                                 default=None)):
    #     """Get the last message of a text channel."""
    #     channel = ctx.bot.get_channel(int(identifiant))
    #     if channel is None:
    #         await ctx.respond('Could not find that channel.')
    #         return
    #
    #     message = await channel.fetch_message(
    #         channel.last_message_id)
    #     # NOTE: channel.last_message_id could return None; needs a check
    #
    #     await ctx.respond(
    #         f'Last message in {channel.name} sent by {message.author.name}:\n'
    #         + message.content)
    #
    #     # await ctx.message.delete()

    @commands.slash_command(name="copy_reactions", brief="Copy the message's reactions",
                            description="Copy the reactions of a given message, and delete user's reactions.")
    async def _copy_reactions(self, ctx: discord.ApplicationContext,
                              msg_id: Option(str,
                                             description="Id of the message (need to activate dev option, "
                                                         "then copy id on the message options)",
                                             required=False,
                                             default=1)):
        response = await ctx.respond("working...")
        if msg_id == 1:
            msgs = await ctx.channel.history(limit=2).flatten()
            msg = msgs[1]
        else:
            msg = await ctx.fetch_message(msg_id)

        for reaction in msg.reactions:
            await msg.add_reaction(reaction.emoji)
            # remove the reactions made by the author of the message
            async for user in reaction.users():
                if user == ctx.author:
                    await msg.remove_reaction(reaction.emoji, user)
        await ctx.delete()

    # @commands.slash_command(name='clean_test_channel', description="Clear everything in the test channel")
    # async def _clean_test_channel(self, ctx: discord.ApplicationContext):
    #     respond = await ctx.respond("working...")
    #     for thread in ctx.bot.get_channel(CST.TEST_CHANNEL_ID).threads:
    #         await thread.delete()
    #     for msg in await ctx.bot.get_channel(CST.TEST_CHANNEL_ID).history().flatten():
    #         await msg.delete()

    # @commands.slash_command(description="Hello test")
    # async def _tes(self, ctx: discord.ApplicationContext):
    #     await ctx.respond("coucou tes")

    # @commands.slash_command(name='stop_archiving', description="Stop l'archivage du fil")
    # async def _stop_archiving(self, ctx: discord.ApplicationContext,
    #                           thread: Option(str,
    #                                          description="Id or name of the thread. "
    #                                                      "Not necessary if command done in the thread",
    #                                          required=False,
    #                                          default=None)):
    #     threadId = None
    #     if thread is None:
    #         if ctx.channel.type.value == 11:  # type 11 corresponds to thread channels
    #             threadId = ctx.channel.id
    #         else:
    #             response = await ctx.respond("This channel is not a thread. "
    #                                          "Consider writing this command into a thread, or give the thread"
    #                                          " name as argument.")
    #     else:
    #         try:
    #             if not thread.isdigit():
    #                 thread = thread.replace('<', '').replace('>', '').replace('#', '')
    #             threadId = int(thread)
    #             thread = ctx.bot.get_channel(threadId)
    #             if thread.type.value == 11:
    #                 threadId = thread.id
    #             else:
    #                 response = await ctx.respond("Given channel is not a thread. "
    #                                              "Consider writing this command into a thread, "
    #                                              "or give the thread name as argument.")
    #         except:
    #             response = await ctx.respond("couldn't find the channel")
    #     # HH
    #     if threadId is not None:
    #         if ctx.bot.protectedThreads.count(threadId) == 0:
    #             ctx.bot.protectedThreads.append(threadId)
    #             response = await ctx.respond("Thread added !")
    #             await ctx.bot.reset_archiving_timer()
    #         else:
    #             response = await ctx.respond("Thread already registered")

    # --------------------- normal commands ---------------------
    # called using ? in discord

    # @commands.command(name="copy_msg", descrtiption="copie le message ")
    # async def copy_msg(self, ctx: commands.Context, msgId):
    #     msg = await ctx.fetch_message(msgId)
    #     await ctx.send(msg.content)

    @commands.command(brief="Copy the reactions of a given message.")  # for polls
    async def react(self, ctx: commands.Context):
        if ctx.message.reference is None:
            warning = await ctx.reply("❌ The command message needs to be a response of the message to react to.")
            await asyncio.sleep(5)
            await warning.delete()
        else:
            msg = await ctx.fetch_message(ctx.message.reference.resolved.id)
            for reaction in msg.reactions:
                await msg.add_reaction(reaction.emoji)
                # remove the reactions made by the author of the message
                async for user in reaction.users():
                    if user == ctx.message.author:
                        await msg.remove_reaction(reaction.emoji, user)

        await ctx.message.delete()
        # async for message in ctx.channel.history(author=ctx.guild.get_member(913556318768463893)):
        #     print(message.created_at, message.author.name, message.content)
        # member = ctx.message.author
        # msg = discord.utils.get(await ctx.history(limit=100).flatten(), author=member)
        # await ctx.send(msg.author)
        # botMember = await ctx.channel.fetch_members(913556318768463893)

    # @commands.command(brief="Stop thread archiving")
    # async def stop_archiving(self, ctx: commands.Context, threadIdStr=None):
    #     threadId = None
    #     if threadIdStr is None:
    #         if ctx.channel.type.value == 11:  # type 11 corresponds to thread channels
    #             threadId = ctx.channel.id
    #     else:
    #         try:
    #             if not threadIdStr.isdigit():
    #                 threadIdStr = threadIdStr.replace('<', '').replace('>', '').replace('#', '')
    #             threadId = int(threadIdStr)
    #             thread = ctx.bot.get_channel(threadId)
    #             if not thread.type.value == 11:
    #                 threadId = None
    #         except:
    #             threadId = None
    #
    #     if threadId is not None:
    #         if ctx.bot.protectedThreads.count(threadId) == 0:
    #             ctx.bot.protectedThreads.append(threadId)
    #             await ctx.bot.reset_archiving_timer()
    #             respond = await ctx.send("Thread added !")
    #         else:
    #             respond = await ctx.send("Thread already registered")
    #     else:
    #         respond = await ctx.send("This channel is not a thread. "
    #                                  "Consider writing this command into a thread, or give the thread id as argument.")
    #     await asyncio.sleep(5)
    #     await ctx.message.delete()
    #     await respond.delete()

    # @commands.command(brief="stop thread archiving in the channel",
    #                   description="Allow all threads in this channel to avoid being archived")
    # async def protect_channel(self, ctx: commands.Context, channel_id_str=None):
    #     channel_id = None
    #     if channel_id_str is None:
    #         if ctx.channel.type.value == 0:  # type 0 corresponds to text channels
    #             channel_id = ctx.channel.id
    #     else:
    #         try:
    #             if not channel_id_str.isdigit():
    #                 channel_id_str = channel_id_str.replace('<', '').replace('>', '').replace('#', '')
    #             channel_id = int(channel_id_str)
    #             channel = ctx.bot.get_channel(channel_id)
    #             if not channel.type.value == 0:
    #                 channel_id = None
    #         except:
    #             channel_id = None
    #
    #     if channel_id is not None:
    #         if ctx.bot.noArchivingChannels.count(channel_id) == 0:
    #             ctx.bot.noArchivingChannels.append(channel_id)
    #             await ctx.bot.reset_archiving_timer()
    #             respond = await ctx.send("Channel added !")
    #         else:
    #             respond = await ctx.send("Channel already registered")
    #     else:
    #         respond = await ctx.send("Didn't find the channel. Consider writing this command into a channel, "
    #                                  "or give the channel id as argument.")
    #     await asyncio.sleep(5)
    #     await ctx.message.delete()
    #     await respond.delete()
    #
    # @commands.command(brief="Remove this channel from protected list")
    # async def remove_protection(self, ctx: commands.Context, channel_id_str=None):
    #     channel_id = None
    #     if channel_id_str is None:
    #         if ctx.channel.type.value == 0 or ctx.channel.type.value == 11:
    #             channel_id = ctx.channel.id
    #             channel = ctx.channel
    #     else:
    #         try:
    #             if not channel_id_str.isdigit():
    #                 channel_id_str = channel_id_str.replace('<', '').replace('>', '').replace('#', '')
    #             channel_id = int(channel_id_str)
    #             channel = ctx.bot.get_channel(channel_id)
    #         except:
    #             channel_id = None
    #
    #     if channel_id is not None:
    #         if channel.type.value == 0:
    #             if ctx.bot.noArchivingChannels.count(channel_id) == 0:
    #                 response = await ctx.send("Channel not registered !")
    #             else:
    #                 ctx.bot.noArchivingChannels.remove(channel_id)
    #                 response = await ctx.send("Channel removed")
    #         elif channel.type.value == 11:
    #             if ctx.bot.protectedThreads.count(channel_id) == 0:
    #                 response = await ctx.send("Thread not registered !")
    #             else:
    #                 ctx.bot.protectedThreads.remove(channel_id)
    #                 response = await ctx.send("Thread removed")
    #     else:
    #         response = await ctx.send("Didn't find the channel. Consider writing this command into a channel, "
    #                                   "or give the channel id as argument.")
    #     await ctx.bot.save_state()
    #     await asyncio.sleep(5)
    #     await ctx.message.delete()
    #     await response.delete()

    @commands.command(name='clear', brief="Clear everything in the test channel")
    async def clean_test_channel(self, ctx: commands.Context):
        # respond = await ctx.respond("working...")
        for thread in ctx.bot.get_channel(CST.TEST_CHANNEL_ID).threads:
            await thread.delete()
        for msg in await ctx.bot.get_channel(CST.TEST_CHANNEL_ID).history().flatten():
            await msg.delete()

    @commands.command(name='embed_from_dict', brief="Create an embed from a python dictionary. Need to respond to a "
                                                    "message")
    async def embed_from_dict(self, ctx: commands.Context, channel_id_str: str = None):
        # respond = await ctx.respond("working...")
        channel = None
        if channel_id_str is None:
            channel = ctx.channel
        else:
            try:
                if not channel_id_str.isdigit():
                    channel_id_str = channel_id_str.replace('<', '').replace('>', '').replace('#', '')
                channel_id = int(channel_id_str)
                channel = ctx.bot.get_channel(channel_id)
            except:
                await ctx.send("❌ error with channel reference ")
        if ctx.message.reference is None:
            await ctx.send("❌ need to respond to a message ")
        else:
            msg = await ctx.fetch_message(ctx.message.reference.resolved.id)
            content = msg.content
            try:
                dico = ast.literal_eval(content)
                embed = discord.Embed.from_dict(data=dico)
                try:
                    if channel:
                        await channel.send(embed=embed)
                except:
                    await ctx.send("❌ didn't find the channel")
            except:
                await ctx.send("❌ syntax error\nFormat should be:\n "
                               "`{ 'color': 2466394, 'type': 'rich',\n"
                               "'title':'...',\n"
                               "'description': '...',\n"
                               "'fields': [{'name': '...', 'value': '...', 'inline': False},{'name': '...', 'value': "
                               "'[hyperlien](https://google.fr)', 'inline': False}] "
                               "\n}`")

    @commands.command(name='embed_to_dict', brief="give the python dictionary that can create this embed. Need to "
                                                  "respond to a message")
    async def embed_to_dict(self, ctx: commands.Context):
        if ctx.message.reference is None:
            await ctx.send("❌ need to respond to a message ")
        else:
            msg = await ctx.fetch_message(ctx.message.reference.resolved.id)
            if msg.embeds==[]:
                await ctx.send("❌ no embed found")
            else:
                embeddict = discord.Embed.to_dict(msg.embeds[0])
                await ctx.send(embeddict)


def setup(bot):
    bot.add_cog(Interactions(bot))
