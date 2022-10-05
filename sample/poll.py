import babel.dates
import discord
import datetime
import constants as CST


# Builder of an embed that will serve as a poll for a given training.
class TrainingPollMsgBuilder:

    def __init__(self, trainingDayNum, description, reactions, color, threadMsgStr):
        # Number of the week day on which the training occurs.
        self.trainingDayNum = trainingDayNum
        # Color to display with the message.
        self.color = color
        self.description = description
        self.reactions = reactions
        self.threadMsgStr = threadMsgStr

    async def build(self, channel):
        # Calculate the date of the next training, for which to send the poll. refDate is tomorrow, in order to send the
        # poll net for next week if trainingDayNum correspond to today's weekNum. For ex.: if today is saturday,
        # the poll for the saturday's training will correspond to next week
        refDate = datetime.datetime.now(tz=CST.USER_TIMEZONE) + datetime.timedelta(days=1)
        trainingDate = get_date_from_weekday(self.trainingDayNum, refDate=refDate)
        trainingDateStr = \
            babel.dates.format_date(trainingDate, format='EEEE d MMMM', locale='fr_FR').capitalize()

        embed = discord.Embed(title=f"{trainingDateStr}", description=self.description, color=self.color)

        msg = await channel.send(embed=embed)
        if self.reactions is not None:
            for reaction in self.reactions:
                await msg.add_reaction(reaction)

        f = await msg.create_thread(name=trainingDateStr, auto_archive_duration=CST.MAX_THREAD_ARCHIVING_DURATION)
        # await f.send(self.threadMsgStr)


# Routine that sends a poll for a training on a given channel, on a given day of the week.
class TrainingPollRoutine:

    def __init__(self, name, displayName, bot, trainingPollMsgBuilder, cmdKeyWord):
        self.name = name
        self.displayName = displayName
        self.bot = bot
        self.trainingPollMsgBuilder = trainingPollMsgBuilder
        self.isEnabled = False
        self.executionDayNum = None
        self.channelId = None
        self.lastExecutionDate = None
        self.cmdKeyWord = cmdKeyWord

    # Enable this routine and set the execution's day number.
    def enable(self, executionDayNum, channelId):
        self.executionDayNum = executionDayNum
        self.channelId = channelId
        self.lastExecutionDate = None
        self.isEnabled = True
        self.log("enabled")

    # Disable this routine.
    def disable(self):
        self.executionDayNum = None
        self.channelId = None
        self.isEnabled = False
        self.log("disabled")

    # If this routine is enabled, send a poll on the set channel,
    # if today is the set execution day.
    async def execute(self):
        self.log(f"{self.displayName} triggerd")
        today = datetime.datetime.now(tz=CST.USER_TIMEZONE)
        # uncomment if use alreadyExecutedToday
        # alreadyExecutedToday = \
        #     False if self.lastExecutionDate is None \
        #     else (self.lastExecutionDate.date() == today.date())
        #

        # self.log(f"isEnabled = {self.isEnabled}")
        # self.log(f"executionDayNum = {self.executionDayNum}")
        # self.log(f"alreadyExecutedToday = {alreadyExecutedToday}")

        if self.isEnabled and today.weekday() == self.executionDayNum:
            canceled_trainings = self.bot.canceledTrainings
            trainingDate = get_date_from_weekday(self.trainingPollMsgBuilder.trainingDayNum)
            training_canceled = False
            for canceled_training in canceled_trainings.keys():
                if trainingDate.strftime("%d/%m") == canceled_training:
                    training_canceled = True
                    continue
            if not training_canceled:
                # comment if use alreadyExecutedToday
                await self.trainingPollMsgBuilder.build(self.bot.get_channel(self.channelId))
                self.lastExecutionDate = datetime.datetime.now(tz=CST.USER_TIMEZONE)

                # uncomment if use alreadyExecutedToday
                # if not alreadyExecutedToday:
                #     await self.trainingPollMsgBuilder.build(self)
                #     self.lastExecutionDate = datetime.datetime.now(tz=CST.USER_TIMEZONE)
                # else:
                #     self.log(f"alreadyExecutedToday = {alreadyExecutedToday}")
            else:
                self.log(f"canceled training")
                self.trainingPollMsgBuilder.description = f"⚠️ **L'entraînement est annulé car {canceled_trainings[canceled_training]}.**"
                self.trainingPollMsgBuilder.reactions = None
                await self.trainingPollMsgBuilder.build(self.bot.get_channel(self.channelId))
                self.lastExecutionDate = datetime.datetime.now(tz=CST.USER_TIMEZONE)
                del self.bot.canceledTrainings[canceled_training]
                await self.bot.save_state()

    def log(self, msg):
        print(f"\t[routine \"{self.displayName}\"] {msg}")

    def save_routines_state(self, state):

        state[self.name] = \
            {
                'isEnabled': "" if self.isEnabled is None else self.isEnabled,
                # isEnabled a forcément une valeur puisqu'il est initialisé a False
                'execDayNum': "" if self.executionDayNum is None else self.executionDayNum,
                'channelId': "" if self.channelId is None else self.channelId,
                'lastExecDate': "" if self.lastExecutionDate is None else self.lastExecutionDate.isoformat(),
            }

    def load_routines_state(self, state):

        if state.has_section(self.name):
            routineConfig = state[self.name]
            self.isEnabled = routineConfig.getboolean('isEnabled')
            self.executionDayNum = routineConfig.getint('execDayNum')
            self.channelId = routineConfig.getint('channelId')
            self.lastExecutionDate = routineConfig.getdatetime('lastExecDate')


# Get the date of the next day associated with the given week day number,
# from the given reference date. If none is provided, today is used.
def get_date_from_weekday(weekDayNum, refDate=None):
    if refDate is None:
        refDate = datetime.datetime.now(tz=CST.USER_TIMEZONE)
    daysBeforeTargetDay = (weekDayNum - refDate.weekday()) % 7
    return refDate + datetime.timedelta(days=daysBeforeTargetDay)


# Format the given time delta into a string.
def format_time_delta(delta: datetime.timedelta):
    res = ''
    days = delta.days
    hours = delta.seconds // 3600
    minutes = (delta.seconds // 60) % 60
    seconds = delta.seconds % 60

    if days > 0: res += f'{days}j '
    if hours > 0: res += f'{hours}h '
    if minutes > 0: res += f'{minutes}m '
    if seconds > 0: res += f'{seconds}s '

    return res.strip()


# Get the name of the next day associated with the given week day number,
# from the given reference date. If none is provided, today is used.
def format_weekday_num(weekDayNum, format='EEEE', refDate=None):
    nextTargetDay = get_date_from_weekday(weekDayNum, refDate)
    return babel.dates.format_date(nextTargetDay, format=format, locale='en')


def format_datetime(dateTime, placeholder='never', format='%d/%m/%Y, %H:%M:%S'):
    return placeholder if dateTime is None else dateTime.strftime(format)


def poll_events(bot):
    @bot.event
    async def on_raw_reaction_add(payload):
        channel = await bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        user = await bot.fetch_user(payload.user_id)
        emoji = payload.emoji
        if payload.channel_id == CST.TRAINING_POLLS_CHANNEL_ID:
            try:
                thread = await bot.fetch_channel(payload.message_id) #thread.id == message_id if thread starts from this message
                mention_msg = await thread.send(f"<@{payload.user_id}>")
                await mention_msg.delete()
                await message.remove_reaction(emoji, user)
            except:
                pass
