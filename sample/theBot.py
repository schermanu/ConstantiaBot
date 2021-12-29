import configparser
import datetime
import asyncio
from discord.ext import commands


import constants as CST

# The bot that receives all commands.
class TheBot(commands.Bot):

    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('?'))
        self.state = BotState()
        self.routines = []
        self.routinesTask = None
        self.routinesTaskStartTime = None
        # By giving no argument, this will be midnight by default.
        self.routinesTriggerTime = datetime.time()
        self.lastRoutinesTriggerDate = None


    def add_routine(self, routine):
        self.routines.append(routine)
        return self

    def set_routines_trigger_time(self, triggerTime):
        self.routinesTriggerTime = triggerTime
        self.restart_routines_task()
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

    def restart_routines_task(self):
        if self.routinesTask is not None:
            self.routinesTask.cancel()
        self.log("restarting routines task")
        self.routinesTask = self.loop.create_task(self.run_routines())

    async def on_ready(self):

        self.log(f'Logged in as {self.user} (ID: {self.user.id})')

        self.load_state()

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

        self.restart_routines_task()

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

        self.save_state()

    def log(self, msg):
        print(f"[bot] {msg}")

    def save_state(self):

        self.state['bot'] = \
            {
                'routinesTriggerTime':
                    "" if self.routinesTriggerTime is None
                    else self.routinesTriggerTime.isoformat(),
                'lastRoutinesTriggerDate':
                    "" if self.lastRoutinesTriggerDate is None
                    else self.lastRoutinesTriggerDate.isoformat(),
            }

        for routine in self.routines:
            routine.save_state(self.state)

        with open(CST.STATE_FILE_PATH, "w+") as stateFile:
            self.state.write(stateFile)

    def load_state(self):

        self.state.read(CST.STATE_FILE_PATH)

        if self.state.has_section('bot'):

            botConfig = self.state['bot']
            self.routinesTriggerTime = botConfig.gettime('routinesTriggerTime')
            self.lastRoutinesTriggerDate = botConfig.getdatetime('lastRoutinesTriggerDate')

            for routine in self.routines:
                routine.load_state(self.state)




# Parser of the bot's state. Allows to save and restore its state after a reboot.
class BotState(configparser.ConfigParser):

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

