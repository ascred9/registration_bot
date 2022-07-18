import environs
from telebot import TeleBot, types
import emoji

import database as db


class Bot:
    def __init__(self):
        env = environs.Env()
        env.read_env('data/.env')
        BOT_TOKEN = env('BOT_TOKEN')
        self.bot = TeleBot(token=BOT_TOKEN)

        @self.bot.message_handler(commands=['start'])
        def start_chat(message):
            text = "Приветствую!\n" \
                   "Это Бот-помощник, который поможет зарегестрироваться на курс по программированию" \
                   " Cpp and Python для 2-го курса ФФ НГУ"
            self.bot.send_message(message.chat.id, text, reply_markup=self.start_markup())

        @self.bot.callback_query_handler(func=lambda callback: True)
        def callback_handler(call):
            if call.data == "info":
                self.bot.delete_message(call.from_user.id, call.message.message_id)
                with open("data/about.txt", 'rb') as f:
                    text = f.read()
                markup = types.InlineKeyboardMarkup()
                markup.width = 1
                markup.add(
                    types.InlineKeyboardButton("Назад" + emoji.emojize(":BACK_arrow:"),
                                               callback_data="back_to_start")
                )
                self.bot.send_message(call.message.chat.id, text, reply_markup=markup)
            elif call.data == "back_to_start":
                self.bot.delete_message(call.from_user.id, call.message.message_id)
                text = "Приветствую!\n" \
                       "Это Бот-помощник, который поможет зарегестрироваться на курс по программированию" \
                       " Cpp and Python для 2-го курса ФФ НГУ"
                self.bot.send_message(call.message.chat.id, text, reply_markup=self.start_markup())
            elif call.data == "reg":
                self.bot.delete_message(call.from_user.id, call.message.message_id)
                user = db.Database.get_user(call.from_user.id)
                if user:
                    markup = types.InlineKeyboardMarkup()
                    markup.width = 1
                    markup.add(
                        types.InlineKeyboardButton("Хочу изменить" + emoji.emojize(":scroll:"),
                                                   callback_data="wanna_change"),
                        types.InlineKeyboardButton("Назад" + emoji.emojize(":BACK_arrow:"),
                                                   callback_data="back_to_start")
                    )
                    self.bot.send_message(call.message.chat.id, "Вы уже зарегестрированы!\n" + str(user),
                                          reply_markup=markup)
                else:
                    text = "Как вас зовут? Пожалуйста, введите полное ФИО"
                    msg = self.bot.send_message(call.message.chat.id, text)
                    self.bot.register_next_step_handler(msg, process_name)
            elif call.data == "wanna_change":
                self.bot.delete_message(call.from_user.id, call.message.message_id)
                text = "Как вас зовут? Пожалуйста, введите полное ФИО"
                msg = self.bot.send_message(call.message.chat.id, text)
                self.bot.register_next_step_handler(msg, process_name)

        def process_name(message):
            user = db.User()
            user.set_ind(message.from_user.id)
            user.set_name(message.text)
            if not db.Database.add_user(user):
                db.Database.change_data(message.from_user.id, ["name", message.text])
            text = "Введите номер вашей группы"
            msg = self.bot.send_message(message.chat.id, text)
            self.bot.register_next_step_handler(msg, process_group)

        def process_group(message):
            db.Database.change_data(message.from_user.id, ["grp", message.text])
            text = "Введите вашу университетскую почту"
            msg = self.bot.send_message(message.chat.id, text)
            self.bot.register_next_step_handler(msg, process_email)

        def process_email(message):
            db.Database.change_data(message.from_user.id, ["email", message.text])
            text = "Осталось ввести только имя вашего аккаунта на github"
            msg = self.bot.send_message(message.chat.id, text)
            self.bot.register_next_step_handler(msg, process_git)

        def process_git(message):
            db.Database.change_data(message.from_user.id, ["git", message.text])
            db.Database.read_all()
            markup = types.InlineKeyboardMarkup()
            markup.width = 1
            markup.add(
                types.InlineKeyboardButton("Хочу изменить" + emoji.emojize(":scroll:"),
                                           callback_data="wanna_change"),
                types.InlineKeyboardButton("Назад" + emoji.emojize(":BACK_arrow:"),
                                           callback_data="back_to_start")
            )
            user = db.Database.get_user(message.from_user.id)
            text = "Спасибо за регистрацию на наш курс!\n" + str(user)
            self.bot.send_message(message.chat.id, text, reply_markup=markup)

    def start(self):
        self.bot.infinity_polling()

    @staticmethod
    def start_markup():
        markup = types.InlineKeyboardMarkup()
        markup.width = 1
        markup.add(
            types.InlineKeyboardButton("О курсе" + emoji.emojize(":magnifying_glass_tilted_left:"), callback_data="info"),
            types.InlineKeyboardButton("Регистрация" + emoji.emojize(":graduation_cap:"), callback_data="reg")
        )
        return markup


if __name__== '__main__':
    db.Database.read_all()
    bot = Bot()
    bot.start()
