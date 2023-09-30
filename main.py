import time
from mysql.connector.errors import OperationalError
from requests.exceptions import ReadTimeout, ConnectionError
from business import print_log
from bot import BotConfig
from database import Database

if __name__ == '__main__':
    database = Database()
    bot = BotConfig(database)
    while True:
        try:
            bot.start()
        except (ReadTimeout, ConnectionError):
            print_log("Error with Internet connection")
            time.sleep(1)
            continue
        except OperationalError:
            print_log("Error with connection to database")
            database.connect_to_database()
            time.sleep(1)
            continue
