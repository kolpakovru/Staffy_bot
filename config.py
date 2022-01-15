# ------------ config of Bot --------
#
# ---------Config for Staffy Bot -----------
#

import pymongo

token = ''  # токен бота
TIMEZONE = 'Europe/Moscow'                                # пока не использую
TIMEZONE_COMMON_NAME = 'Moscow'                           # пока не использую


# --- Подключение к БД
client = pymongo.MongoClient('', 27017)
db = client['Staff_food']
users_collection = db['users']
