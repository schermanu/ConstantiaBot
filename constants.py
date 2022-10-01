# Constantes utilisées par le bot, pour éviter de les écrire dans le code
# une variable par ligne, sans commentaires sur la ligne
from dateutil import tz

# id du salon discord dédié au paramétrage du bot #paramètres-du-bot
CONFIG_CHANNEL_ID = 925507525992931378

# Identifier of the Discord channel dedicated to training polls.
TRAINING_POLLS_CHANNEL_ID = 913522652239519775

# Identifier of the Discord channel dedicated to tests.
TEST_CHANNEL_ID = 926902411501645884

# LICENCIE_ROLE_ID = 898137491780014090

# Maximum duration of any sleep (in seconds).
# IMPORTANT: there seems to be a bug with asyncio, making that any wait longer
# than 24 hours (ie. 86400 seconds) never actually ends. That's why this setting
# exists and should always be less than 86400.
MAX_SLEEP_DURATION = 3600
# Time zone to use when receiving dates from the user, or displaying them to him.

MAX_THREAD_ARCHIVING_DURATION = 60 * 24 * 7 # should be 1h, 1 day, 3 days if boosted lvl1, 7days if lvl2

USER_TIMEZONE = tz.gettz('Europe/Paris')

