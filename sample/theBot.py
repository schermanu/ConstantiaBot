import io
import os
import configparser
import datetime
import asyncio
import json

import discord
from discord.ext import commands
import constants as CST


# The bot that receives all commands.
# class TheBot(commands.Bot):
class TheBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('?'), case_insensitive=False,
                         intents=discord.Intents.all())
        self.param = BotParameters()
        self.canceledTrainings = {}
        #self.protectedThreads = []
        #self.noArchivingChannels = []  # channels where all threads are protected from archiving
        self.routines = []
        self.routinesTask = None
        self.routinesTaskStartTime = None
        # By giving no argument, this will be midnight by default.
        self.routinesTriggerTime = datetime.time()
        self.lastRoutinesTriggerDate = None
        self.load_commands()

    def load_commands(self):

        @self.command()
        async def reload(ctx):
            for filename in os.listdir('./sample/cogs'):
                if filename.endswith('.py'):
                    self.unload_extension(f'cogs.{filename[:-3]}')  # remove the 3 last char that correspond to '.py'
                    self.load_extension(f'cogs.{filename[:-3]}')
            print('reload done')

        for filename in os.listdir('./sample/cogs'):
            if filename.endswith('.py'):
                self.load_extension(f'cogs.{filename[:-3]}')
        # print(len(self.pending_application_commands))

    async def on_ready(self):

        self.log(f'Logged in as {self.user} (ID: {self.user.id})')

        await self.load_state_and_config()

        # If a routines trigger time is set.
        # DISABLED: since the script is currently hosted on Heroku, and Heroku
        # restarts its virtual hosts every day (resetting the state file),
        # we don't want the bot to think it missed the last trigger on every reboot.
        if False and self.routinesTriggerTime is not None:

            # Calculate the date of the previous trigger,
            # which is the date of the next trigger minus one day,
            # since the routines are triggered once a day.
            previousTriggerDate = self.get_next_trigger_date() - datetime.timedelta(days=1)

            # If the last routines trigger happened before the supposed previous trigger date,
            # that means the bot missed a trigger, so try to make up for it
            # by running the routines now.
            if (self.lastRoutinesTriggerDate is None
                    or self.lastRoutinesTriggerDate < previousTriggerDate):
                await self.run_routines_once()

        await self.restart_routines_task()
        # await self.reset_archiving_timer()

    # ----------poll routine functions-------------

    def add_routine(self, routine):
        self.routines.append(routine)
        return self

    async def set_routines_trigger_time(self, triggerTime):
        self.routinesTriggerTime = triggerTime
        await self.restart_routines_task()
        return self

    def get_next_trigger_date(self):
        now = datetime.datetime.now(tz=CST.USER_TIMEZONE)
        triggerDate = datetime.datetime.combine(now, self.routinesTriggerTime, tzinfo=CST.USER_TIMEZONE)
        # If the trigger time has passed for today, consider tomorrow's trigger time.
        if triggerDate < now:
            triggerDate += datetime.timedelta(days=1)
        return triggerDate

    def get_time_until_routines_trigger(self):
        return self.get_next_trigger_date() - datetime.datetime.now(tz=CST.USER_TIMEZONE)

    async def restart_routines_task(self):
        if self.routinesTask is not None:
            self.routinesTask.cancel()
        self.log("restarting routines task")
        self.routinesTask = self.loop.create_task(self.run_routines())

    async def run_routines(self):

        await self.wait_until_ready()

        self.routinesTaskStartTime = datetime.datetime.now(tz=CST.USER_TIMEZONE)

        while not self.is_closed():

            waitDuration = self.get_time_until_routines_trigger().seconds

            self.log(f"waiting until {self.routinesTriggerTime}")

            # Wait until the next trigger time, while checking in regularly
            # to avoid a bug with asyncio, that makes a wait never end, when
            # it's longer than 24 hours.
            while waitDuration > 0:
                timeUntilNextCheckin = min(waitDuration, CST.MAX_SLEEP_DURATION)
                await asyncio.sleep(timeUntilNextCheckin)
                waitDuration -= timeUntilNextCheckin

            await self.run_routines_once()

            # This is to ensure not to spam routines during the second
            # that is just right on the trigger time.
            await asyncio.sleep(1)

    async def run_routines_once(self):

        self.log("executing routines")
        self.lastRoutinesTriggerDate = datetime.datetime.now(tz=CST.USER_TIMEZONE)

        for routine in self.routines:
            await routine.execute()

        # await self.reset_archiving_timer()
        await self.save_state()

    def log(self, msg):
        print(f"[bot] {msg}")

    # ---------------reset thread archiving timers----------
    # this version of the function reset the thread timers for all threads in the server.
    async def reset_archiving_timer(self):
        for guild in self.guilds:
            for channel in guild.channels:
                if channel.type.name == 'text':
                    for thread in channel.threads:
                        if thread.auto_archive_duration != 60:
                            try:
                                if not thread.archived:
                                    await thread.edit(auto_archive_duration=60)
                                    await thread.edit(auto_archive_duration=CST.MAX_THREAD_ARCHIVING_DURATION)
                            except:
                                pass


    # this version of the function reset the thread timers for threads in self.noArchivingChannels and self.protectedThreads.
    # async def reset_archiving_timer(self):
    #     protected_channels = []
    #     for no_archiving_channels_id in self.noArchivingChannels:
    #         try:
    #             protected_channels.append(self.get_channel(no_archiving_channels_id))
    #         except:
    #             self.noArchivingChannels.remove(no_archiving_channels_id)
    #
    #     for protected_channel in protected_channels:
    #         for thread in protected_channel.threads:
    #             try:
    #                 if not thread.archived:
    #                     await thread.edit(auto_archive_duration=60)
    #                     await thread.edit(auto_archive_duration=CST.MAX_THREAD_ARCHIVING_DURATION)
    #             except:
    #                 pass
    #
    #     for thread_id in self.protectedThreads:
    #         try:
    #             thread = self.get_channel(thread_id)
    #             already_protected = False
    #             for protected_channel in protected_channels:
    #                 if thread.parent == protected_channel:
    #                     already_protected = True
    #                     continue
    #             if not already_protected:
    #                 if not thread.archived:
    #                     await thread.edit(auto_archive_duration=60)
    #                     await thread.edit(auto_archive_duration=4320)
    #                 else:
    #                     self.protectedThreads.remove(thread_id)
    #             else:
    #                 self.protectedThreads.remove(thread_id)
    #         except:
    #             self.protectedThreads.remove(thread_id)
    #     await self.save_state()

    # ----------------bot startup config --------------

    async def load_state_and_config(self):
        botStateStr, botConfigStr = await self.param.load_param_msgs(self)
        self.param.state.read_string(botStateStr)
        self.param.config.read_string(botConfigStr)

        self.canceledTrainings = {} if not self.param.state.has_section('canceled_trainings') \
            else json.loads(self.param.state['canceled_trainings'].get('dates'))
        # self.canceledTrainings = [] if not self.param.config.has_section('canceled_trainings') \
        #     else self.param.config['canceled_trainings'].get('dates').split()

        if self.param.state.has_section('bot'):
            botStateConfig = self.param.state['bot']
            self.routinesTriggerTime = botStateConfig.gettime('routinesTriggerTime')
            self.lastRoutinesTriggerDate = botStateConfig.getdatetime('lastRoutinesTriggerDate')
            # self.protectedThreads = [] if botStateConfig.get('protectedThreads') is None \
            #     else list(map(int, botStateConfig.get('protectedThreads').split()))
            # self.noArchivingChannels = [] if botStateConfig.get('noArchivingChannels') is None \
            #     else list(map(int, botStateConfig.get('noArchivingChannels').split()))

            for routine in self.routines:
                routine.load_routines_state(self.param.state)

    async def save_state(self):
        self.param.state['bot'] = \
            {
                'routinesTriggerTime':
                    "" if self.routinesTriggerTime is None
                    else self.routinesTriggerTime.isoformat(),
                'lastRoutinesTriggerDate':
                    "" if self.lastRoutinesTriggerDate is None
                    else self.lastRoutinesTriggerDate.isoformat(),
                # 'protectedThreads':
                #     "" if self.protectedThreads is None
                #     else ' '.join(map(str, self.protectedThreads)),
                # 'noArchivingChannels':
                #     "" if self.noArchivingChannels is None
                #     else ' '.join(map(str, self.noArchivingChannels)),
            }

        self.param.state['canceled_trainings'] = {
            'dates': {} if self.canceledTrainings is None else json.dumps(self.canceledTrainings)
        }

        for routine in self.routines:
            routine.save_routines_state(self.param.state)
        await self.param.write_state(self)


# Parser of the bot's state. Allows to save and restore its state after a reboot.
class ConfigurationParser(configparser.ConfigParser):

    def __init__(self):
        super().__init__(
            converters=
            {
                'int': self.parse_int,
                'datetime': self.parse_iso_datetime,
                'time': self.parse_time,
            })

    def parse_int(self, s):
        try:
            return int(s)
        except (ValueError, TypeError):
            return None

    def parse_iso_datetime(self, s):
        try:
            return datetime.datetime.fromisoformat(s)
        except (ValueError, TypeError):
            return None

    def parse_time(self, s):
        try:
            return datetime.time.fromisoformat(s)
        except (ValueError, TypeError):
            return None

    # def get_dates(self):
    #     if self.has_section('canceled_trainings'):
    #         canceled_trainings_cat = self['canceled_trainings']
    #         canceled_trainings_str = canceled_trainings_cat.get('dates')
    #         dates = canceled_trainings_str.split()
    #     else:
    #         dates = None
    #     return dates


class BotParameters:
    def __init__(self):
        self.state = ConfigurationParser()
        self.config = ConfigurationParser()
        self.paramMessages = {}
        self.stateHeader = ""
        self.configHeader = ""

    async def write_state(self, bot):

        buf = io.StringIO("")
        self.state.write(buf)  # utilisation d'un buffer car la methode write() de configParser
        # ne permet pas d'ecrire dans une string
        strToWrite = buf.getvalue()
        buf.close()
        stateMsg = self.paramMessages["state"]
        if stateMsg is None:
            self.paramMessages["state"] = await bot.get_channel(CST.CONFIG_CHANNEL_ID).send(
                self.stateHeader + strToWrite)

        elif stateMsg.author == bot.user:
            await stateMsg.edit(self.stateHeader + strToWrite)
        else:
            await stateMsg.delete()
            self.paramMessages["state"] = await bot.get_channel(CST.CONFIG_CHANNEL_ID).send(
                self.stateHeader + strToWrite)
        # need to remove other messages?

    async def load_param_msgs(self, bot):
        allMsg = await bot.get_channel(CST.CONFIG_CHANNEL_ID).history().flatten()
        # botMessages = [msg for msg in allMsg if msg.author == self.user]
        # notBotMessage = [msg for msg in allMsg if msg not in botMessages]
        botStateStr = ""
        botConfigStr = ""
        for msg in allMsg:
            # check only the firsts 7 characters to avoid checking the comments
            if msg.content.startswith(self.stateHeader[0:6]):
                self.paramMessages["state"] = msg
                botStateStr = msg.content
                break
        if botStateStr == "":
            self.paramMessages["state"] = None
        for msg in allMsg:
            # the header doesn't contain comments here
            if msg.content.startswith(self.configHeader):
                self.paramMessages["config"] = msg
                botConfigStr = msg.content
                break
        if botConfigStr == "":
            self.paramMessages["config"] = None
        # print(f"state:\n{botStateStr}\n")
        # print(f"config:\n{botConfigStr}")
        return botStateStr, botConfigStr
