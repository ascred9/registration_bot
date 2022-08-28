import environs
from telebot import TeleBot, types
import emoji

import database as db

teachers = {
    178959512:  [21313, 21314],  # A. Semenov
    899124117:  [21307, 21308],  # N. Okhotnikov
    829365853:  [21301, 21302],  # M. Tolkachev
    640424251:  [21306, 21309],  # Y. Savchenko
    1702643924: [21305, 21310, 21311, 21312],  # S. Gribanov
    91551104:   [21303, 21304]   # N. Petrov
}

class Bot:
    def __init__(self):
        env = environs.Env()
        env.read_env('data/.env')
        BOT_TOKEN = env('BOT_TOKEN')
        self.bot = TeleBot(token=BOT_TOKEN)

        @self.bot.message_handler(commands=['start'])
        def start_chat(message):
            if self.auth_admin(message):
                text = "Приветствую, *преподаватель*!\n" \
                       "Это *Бот-помощник*, который поможет зарегестрировать студентов на курс по программирвоанию" \
                       " Cpp and Python для 2-го курса ФФ НГУ."
                self.bot.send_message(message.chat.id, text, parse_mode="Markdown",
                                      reply_markup=self.admin_start_markup())
            else:
                text = "*Приветствую!*\n" \
                       "Это *Бот-помощник*, который поможет зарегестрироваться на курс по программированию" \
                       " Cpp and Python для 2-го курса ФФ НГУ"
                self.bot.send_message(message.chat.id, text, parse_mode="Markdown",
                                      reply_markup=self.start_markup())

        @self.bot.callback_query_handler(func=lambda callback: True)
        def callback_handler(call):
            self.bot.delete_message(call.from_user.id, call.message.message_id)
            if call.data == "info":
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
                text = "*Приветствую!*\n" \
                       "Это *Бот-помощник*, который поможет зарегестрироваться на курс по программированию" \
                       " Cpp and Python для 2-го курса ФФ НГУ"
                self.bot.send_message(call.message.chat.id, text, parse_mode="Markdown",
                                      reply_markup=self.start_markup())
            elif call.data == "reg":
                user = db.Database.get_user(call.from_user.id)
                if user:
                    if user.get_confirm():
                        self.bot.send_message(call.message.chat.id, "Вы уже подтверждены!\n" + str(user),
                                              reply_markup=self.start_markup())
                        return True

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
                    text = "Как вас зовут? Пожалуйста, введите полное *ФИО*"
                    msg = self.bot.send_message(call.message.chat.id, text, parse_mode="Markdown")
                    self.bot.register_next_step_handler(msg, process_name)
            elif call.data == "wanna_change":
                text = "Как вас зовут? Пожалуйста, введите полное *ФИО*"
                msg = self.bot.send_message(call.message.chat.id, text, parse_mode="Markdown")
                self.bot.register_next_step_handler(msg, process_name)
            elif call.data == "confirm_user":
                users = []
                for group in teachers.get(call.from_user.id):
                    users.extend(list(filter(lambda u: not u.get_confirm(), db.Database.get_users_from_group(group))))

                if len(users) == 0:
                    self.bot.send_message(call.message.chat.id, "Новых студентов нет!",
                                          reply_markup=self.admin_start_markup())
                    return True

                text = str()
                for idx, user in enumerate(users):
                    text += f"*{idx+1} студент*:\n{user}"

                msg = self.bot.send_message(call.message.chat.id, "Введите номер студента:\n" + text +
                                            "\n*!Введите ерунду, если хотите вернуться назад!*",
                                            parse_mode="Markdown")
                self.bot.register_next_step_handler(msg, process_user_confirm, users, msg.id)
            elif call.data == "remove_user":
                users = []
                for group in teachers.get(call.from_user.id):
                    users.extend(list(filter(lambda u: u.get_confirm(), db.Database.get_users_from_group(group))))

                if len(users) == 0:
                    self.bot.send_message(call.message.chat.id, "Подтвержденных тудентов нет!",
                                          reply_markup=self.admin_start_markup())
                    return True

                text = str()
                for idx, user in enumerate(users):
                    text += f"*{idx+1} студент*:\n{user}"

                msg = self.bot.send_message(call.message.chat.id, "Введите номер студента:\n" + text +
                                            "\n*!Введите ерунду, если хотите вернуться назад!*",
                                            parse_mode="Markdown")
                self.bot.register_next_step_handler(msg, process_user_remove, users, msg.id)


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

            if user.get_email().endswith("@g.nsu.ru") and not user.get_confirm():
                # Send message to master
                for master_id, groups in teachers.items():
                    if user.get_grp() not in groups:
                        continue
                    self.bot.send_message(master_id, "Новый студент")
                    return True

                # in strange case send it to all masters
                #for master_id in teachers.txt.keys():
                #    self.bot.send_message(master_id, "Новый странный студент. ")

        def process_user_confirm(message, users, old_msg_id):
            self.bot.delete_message(message.from_user.id, old_msg_id)
            self.bot.delete_message(message.from_user.id, message.message_id)
            if not message.text.isdigit() or not (0 < int(message.text) < len(users)+1):
                self.bot.send_message(message.chat.id, "Неверный ввод!", reply_markup=self.admin_start_markup())
                return True

            user = users[int(message.text) - 1]
            db.Database.change_data(user.get_ind(), ["confirm", True])
            self.bot.send_message(message.chat.id, "Студент подтвержден!", reply_markup=self.admin_start_markup())

        def process_user_remove(message, users, old_msg_id):
            self.bot.delete_message(message.from_user.id, old_msg_id)
            self.bot.delete_message(message.from_user.id, message.message_id)
            if not message.text.isdigit() or not (0 < int(message.text) < len(users)+1):
                self.bot.send_message(message.chat.id, "Неверный ввод!", reply_markup=self.admin_start_markup())
                return True

            user = users[int(message.text) - 1]
            db.Database.change_data(user.get_ind(), ["confirm", False])
            self.bot.send_message(message.chat.id, "Студент удален!", reply_markup=self.admin_start_markup())

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

    @staticmethod
    def admin_start_markup():
        markup = types.InlineKeyboardMarkup()
        markup.width = 1
        markup.add(
            types.InlineKeyboardButton("Подтвердить студентов" + emoji.emojize(":check_mark:"),
                                       callback_data="confirm_user"),
            types.InlineKeyboardButton("Удалить студентов" + emoji.emojize(":cross_mark:"), callback_data="remove_user")
        )
        return markup

    @staticmethod
    def auth_admin(message):
        if message.from_user.id in teachers.keys():
            return True


if __name__== '__main__':
    db.Database.read_all()
    bot = Bot()
    bot.start()
