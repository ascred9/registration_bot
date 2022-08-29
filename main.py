import bot
import database as db

if __name__== '__main__':
    db.Database.read_all()
    bot = bot.Bot()
    bot.start()

