import sqlite3


class User:
    def __init__(self):
        """
        mediator between telegram data and database
        :param id: telegram id to contact with student
        :param name: usually telegram names are strange
        :param email: university mail
        :param git_name: github account
        :param points: if make connection between website and this database we can send student points
        """
        self.ind = 0
        self.name = str()
        self.grp = 0
        self.email = str()
        self.git = str()
        self.points = 0

    def __str__(self):
        return f"Имя: {self.name}\n" \
            f"Группа: {self.grp},\n" \
            f"email: {self.email},\n" \
            f"git: {self.git}\n"

    def set_ind(self, ind: int):
        self.ind = ind

    def set_name(self, name: str):
        self.name = name

    def set_grp(self, grp: int):
        self.grp = grp

    def set_mail(self, email: str):
        self.email = email

    def set_git(self, git: str):
        self.git = git

    def set_points(self, points: int):
        self.points = points

    def set_data(self, data):
        self.set_ind(data[0])
        self.set_name(data[1])
        self.set_grp(data[2])
        self.set_mail(data[3])
        self.set_git(data[4])
        self.set_points(data[5])

    def get_ind(self):
        return self.ind

    def get_name(self):
        return self.name

    def get_grp(self):
        return self.grp

    def get_email(self):
        return self.email

    def get_git(self):
        return self.git

    def get_points(self):
        return self.points

    def get_data(self):
        data = list()
        data.append(self.get_ind())
        data.append(self.get_name())
        data.append(self.get_grp())
        data.append(self.get_email())
        data.append(self.get_git())
        data.append(self.get_points())
        return data


def connection(func):
    def wrapper(*args):
        cls = args[0]
        flag = False
        try:
            if not cls.connect:  # check if connection was opened before
                cls.connect = sqlite3.connect('data/users.db')
                cls.cursor = cls.connect.cursor()
                flag = True
        except Exception as e:  # initialization
            print(e)
            cls.connect = sqlite3.connect('data/users.db')
            cls.cursor = cls.connect.cursor()

            cls.cursor.execute("""CREATE TABLE IF NOT EXISTS users(
                ind INTEGER, name TEXT, grp INTEGER, email TEXT, git TEXT, points INTEGER
            )""")
            cls.connect.commit()
            flag = True

        res = func(*args)

        if flag:
            cls.connect.close()
            cls.connect = None

        return res

    return wrapper


class Database:
    def __init__(self):
        Database.connect = None
        Database.cursor = None

    @classmethod
    @connection
    def get_user(cls, ind):
        cls.cursor.execute(f"SELECT * FROM users WHERE ind = {ind}")
        data = cls.cursor.fetchone()
        if not data:
            return False
        else:
            user = User()
            user.set_data(data)
            return user

    @classmethod
    @connection
    def add_user(cls, user):
        if not cls.get_user(user.get_ind()):
            cls.cursor.execute("INSERT INTO users VALUES(?, ?, ?, ?, ?, ?);",
                               [user.get_ind(), user.get_name(), user.get_grp(),
                                user.get_email(), user.get_git(), user.get_points()])
            cls.connect.commit()
            return True
        else:
            return False

    @classmethod
    @connection
    def change_data(cls, ind, pair):
        """
        if student or professor wanna change some information about user
        :param ind: telegram index of user
        :param pair: [name, value], name is data name (name, email and etc.)
        :return: True if it is changed, else False
        """
        user = cls.get_user(ind)
        if user:
            if isinstance(pair[1], str):
                cls.cursor.execute(f"UPDATE users SET {pair[0]} = '{pair[1]}' WHERE ind = {ind};")
            if isinstance(pair[1], int):
                cls.cursor.execute(f"UPDATE users SET {pair[0]} = {pair[1]} WHERE ind = {ind};")
            cls.connect.commit()
            return True
        return False

    @classmethod
    @connection
    def read_all(cls):
        cls.cursor.execute("SELECT * FROM users")
        users_data = cls.cursor.fetchall()
        for user_data in users_data:
            print(user_data)
        return True

    @classmethod
    @connection
    def remove_user(cls, ind):
        if cls.get_user(ind):
            cls.cursor.execute(f"DELETE FROM users WHERE ind = {ind}")
            cls.connect.commit()
            return True
        else:
            return False
