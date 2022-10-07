#
# # This is mandatory when executing the script in Spyder.
# if any('SPYDER' in name for name in os.environ):
#     import nest_asyncio
#     nest_asyncio.apply()
import theBot
import poll
import os
import constants as CST

bot = theBot.TheBot()

## --- sondages ---
embedDescription = "Les entraînement auront toujours lieu 🤗\n" \
                   "mais préviens quand même si tu viens (✅)\n" \
                   "ça pourra être utile aux coachs \n" \
                   "et tu rejoindras aussi le fil de l'entraînement\n"\
                    "(tu peux annuler ta présence avec ❌ )"
reactions = ["✅", "❌"]
# embedDescriptionPoll = "Préviens de ta présence à l'entraînement : \n" \
#                    "✅ si tu viens\n" \
#                    "☑️ que si on est assez pour des matchs\n" \
#                    "❌ si tu viens pas\n" \
#                    "❔ si tu sais pas encore"
# reactionsPoll = ["✅", "☑", "❌", "❔"]

## ---- sans sondages ---
embedDescriptionNoPoll = "Fini les sondages ! \nLes entraînement auront toujours lieu 🤗 "
reactionsNoPoll = []

# embedDescriptionMondayPoll = "L'entraînement du lundi a toujours lieu, quelque soit le nombre d'inscrits, " \
#                    "le vote est donc facultatif: \n" \
#                    "✅ si tu viens\n" \
#                    "❌ si tu viens pas"
# reactionsMondayPoll = ["✅", "❌"]


threadMsgStr = "**la mention @ here permet d'envoyer une notification à toute personne ayant confirmé sa présence à cet entraînement**"
# threadMsgStr = f"<@&{CST.LICENCIE_ROLE_ID}>\n**Fil de discussion dédié à cet entraînement**"

# mondayPollRoutine = \
#     poll.TrainingPollRoutine("monday_training_poll",
#                              "Monday training poll", bot,
#                              poll.TrainingPollMsgBuilder(0, embedDescriptionMondayPoll, reactionsMondayPoll, 0x31B404, threadMsgStr), "lu")

mondayPollRoutine = \
    poll.TrainingPollRoutine("monday_training_poll",
                             "Monday training poll", bot,
                             poll.TrainingPollMsgBuilder(0, embedDescription, reactions, 0x31B404, threadMsgStr), "lu")

wednesdayPollRoutine = \
    poll.TrainingPollRoutine("wednesday_training_poll",
                             "Wednesday training poll", bot,
                             poll.TrainingPollMsgBuilder(2, embedDescription, reactions, 0x2A3AFF, threadMsgStr), "me")

saturdayPollRoutine = \
    poll.TrainingPollRoutine("saturday_training_poll",
                             "Saturday training poll", bot,
                             poll.TrainingPollMsgBuilder(5, embedDescription, reactions, 0xFF5733, threadMsgStr), "sa")

bot.add_routine(mondayPollRoutine)
bot.add_routine(wednesdayPollRoutine)
bot.add_routine(saturdayPollRoutine)

bot.param.stateHeader = "#state#\n#sauvegarde de l'état du bot\n"  # will be written by the bot
bot.param.configHeader = "#config#"  # will not be written by the bot

bot.run(os.environ['BOT_TOKEN'])

# def main():
#     pass
#
#
# if __name__ == "__main__":
#     main()
