import psycopg2
import config
import json


class DB:
    def __init__(self):
        self.connection = psycopg2.connect(dbname=config.dbname, user=config.user, password=config.password)
        self.connection.autocommit = True
        self.cur = self.connection.cursor()

    def db_add_user(self, user_id, user_name):
        with self.connection:
            self.cur.execute(""" SELECT user_id FROM products_data """)
            records = self.cur.fetchall()
            check_list = [record[0] for record in records]
            if user_id not in check_list:
                self.cur.execute(""" INSERT INTO products_data (user_id, user_name) VALUES(%s, %s) """,
                                 (user_id, user_name))

    def db_get_users(self):
        with self.connection:
            self.cur.execute(""" SELECT user_id FROM products_data """)
            users = self.cur.fetchall()
            return [user[0] for user in users]

    def db_delete_user(self, user_id):
        with self.connection:
            self.cur.execute(""" DELETE FROM products_data WHERE user_id = %s """, (user_id,))

    def db_recourse(self, message):
        with self.connection:
            self.cur.execute(""" SELECT list_of_lists FROM products_data WHERE user_id = %s""",
                             (message.from_user.id,))
            dict_of_lists = self.cur.fetchone()[0]
            return dict_of_lists

    def db_update(self, message, dict_of_lists):
        with self.connection:
            self.cur.execute(""" UPDATE products_data SET list_of_lists = %s WHERE user_id = %s """, (
                json.dumps(dict_of_lists), message.from_user.id))

    def db_update_connected(self, message, current_dict, current_title):
        with self.connection:
            # Обновление у себя
            self.cur.execute(""" SELECT list_of_lists FROM products_data WHERE user_id = %s""",
                             (message.from_user.id,))
            dict_of_lists = self.cur.fetchone()[0]
            dict_of_lists[current_title] = current_dict
            self.cur.execute(""" UPDATE products_data SET list_of_lists = %s WHERE user_id = %s """, (
                json.dumps(dict_of_lists), message.from_user.id))
            # Обновление у остальных
            self.cur.execute(""" SELECT connected FROM products_data WHERE user_id = %s""", (message.from_user.id,))
            connections = self.cur.fetchone()[0]
            users = connections[current_title]
            for user in users:
                self.cur.execute(""" SELECT list_of_lists FROM products_data WHERE user_id = %s""",
                                 (user,))
                user_dict_of_lists = self.cur.fetchone()[0]
                user_dict_of_lists[current_title] = current_dict
                self.cur.execute(""" UPDATE products_data SET list_of_lists = %s WHERE user_id = %s """, (
                    json.dumps(user_dict_of_lists), user))

    def db_update_current_list_id(self, message, current_list_id):
        with self.connection:
            self.cur.execute(""" UPDATE products_data SET current_list_id = %s WHERE user_id = %s """,
                             (current_list_id, message.from_user.id))

    def db_get_current_list_id(self, message):
        with self.connection:
            self.cur.execute(""" SELECT current_list_id FROM products_data WHERE user_id = %s""",
                             (message.from_user.id,))
            current_list_id = self.cur.fetchone()[0]
            return current_list_id

    def db_add_connection(self, message, data, current_title):
        with self.connection:
            self.cur.execute(""" UPDATE products_data SET connected = %s WHERE user_id = %s """,
                             (json.dumps(data), message.from_user.id))

            users = data[current_title]
            for user in users:
                self.cur.execute(""" SELECT connected FROM products_data WHERE user_id = %s""", (user,))
                user_connected_data = self.cur.fetchone()[0]
                temp = users.copy() + [message.from_user.id]
                temp.remove(user)
                user_connected_data[current_title] = temp
                self.cur.execute(""" UPDATE products_data SET connected = %s WHERE user_id = %s """,
                                 (json.dumps(user_connected_data), user))

                self.cur.execute(""" SELECT list_of_lists FROM products_data WHERE user_id = %s""",
                                 (user,))
                friend_lists = self.cur.fetchone()[0]
                self.cur.execute(""" SELECT list_of_lists FROM products_data WHERE user_id = %s""",
                                 (message.from_user.id,))
                additional_list = self.cur.fetchone()[0][current_title]
                friend_lists[current_title] = additional_list
                self.cur.execute(""" UPDATE products_data SET list_of_lists = %s WHERE user_id = %s """, (
                    json.dumps(friend_lists), user))

    def db_del_connection(self, message, current_title):
        with self.connection:
            self.cur.execute(""" SELECT owned_lists FROM products_data WHERE user_id = %s""", (message.from_user.id,))
            check_owned_lists = self.cur.fetchone()[0]
            self.cur.execute(""" SELECT connected FROM products_data WHERE user_id = %s""", (message.from_user.id,))
            connections = self.cur.fetchone()[0]
            users = connections[current_title]
            del connections[current_title]
            self.cur.execute("""UPDATE products_data SET connected = %s WHERE user_id = %s """,
                             (json.dumps(connections), message.from_user.id))
            if current_title in check_owned_lists:
                for user in users:
                    self.cur.execute(""" SELECT connected FROM products_data WHERE user_id = %s""", (user,))
                    connections = self.cur.fetchone()[0]
                    del connections[current_title]
                    self.cur.execute("""UPDATE products_data SET connected = %s WHERE user_id = %s """,
                                     (json.dumps(connections), user))
                    self.cur.execute(""" SELECT list_of_lists FROM products_data WHERE user_id = %s""",
                                     (user,))
                    dict_of_lists = self.cur.fetchone()[0]
                    del dict_of_lists[current_title]
                    self.cur.execute(""" UPDATE products_data SET list_of_lists = %s WHERE user_id = %s """,
                                     (json.dumps(dict_of_lists), user))
            else:
                for user in users:
                    self.cur.execute(""" SELECT connected FROM products_data WHERE user_id = %s""", (user,))
                    connections = self.cur.fetchone()[0]
                    connections[current_title].remove(message.from_user.id)
                    if not connections[current_title]:
                        del connections[current_title]
                    self.cur.execute("""UPDATE products_data SET connected = %s WHERE user_id = %s """,
                                     (json.dumps(connections), user))

    def db_get_connections(self, message):
        with self.connection:
            self.cur.execute(""" SELECT connected FROM products_data WHERE user_id = %s""", (message.from_user.id,))
            connections = self.cur.fetchone()[0]
            return connections

    def db_get_owned_titles(self, message):
        with self.connection:
            self.cur.execute(""" SELECT owned_lists FROM products_data WHERE user_id = %s""", (message.from_user.id,))
            owned_titles = self.cur.fetchone()[0]
            return owned_titles

    def db_update_owned_titles(self, message, owned_titles):
        with self.connection:
            self.cur.execute(""" UPDATE products_data SET owned_lists = %s WHERE user_id = %s""",
                             (owned_titles, message.from_user.id,))

    def db_get_friend_titles(self, friend_id):
        with self.connection:
            self.cur.execute(""" SELECT list_of_lists FROM products_data WHERE user_id = %s""",
                             (friend_id,))
            friend_titles = self.cur.fetchone()[0].keys()
            return friend_titles

    def db_get_name_by_id(self, user_id):
        with self.connection:
            self.cur.execute(""" SELECT user_name FROM products_data WHERE user_id = %s """, (user_id,))
            try:
                user_name = self.cur.fetchone()[0]
            except TypeError:
                user_name = f'Пользователь {user_id}'
            return user_name
