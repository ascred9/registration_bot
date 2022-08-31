from threading import Thread

import bot
import database as db
import gitapi

if __name__== '__main__':
    Thread(target=gitapi.GitApi.update_invitations, args=(60, )).start()

    bot = bot.Bot()
    bot.start()

