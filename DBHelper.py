import sqlite3
from typing import List
from uuid import uuid4, UUID


class DB:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.conn.row_factory = self.dict_factory  # Can be set to sqlite3.Row for better performance (without the ability to print everything)

        c = self.conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS profiles "
                  "(profile_id TEXT NOT NULL PRIMARY KEY, "
                  "profile_name TEXT NOT NULL, "
                  "user_id TEXT NOT NULL, "
                  "user_name TEXT NOT NULL, "
                  "is_primary INTEGER, "
                  "is_active INTEGER DEFAULT 1, "
                  "skin_b64 TEXT, "
                  "skin_sign TEXT, "
                  "create_time DATETIME DEFAULT (strftime('%d-%m-%Y %H:%M:%S', 'now', 'localtime')), "
                  "update_time DATETIME DEFAULT (strftime('%d-%m-%Y %H:%M:%S', 'now', 'localtime'))) ")

        c.execute("CREATE TABLE IF NOT EXISTS tokens "
                  "(access_token TEXT NOT NULL PRIMARY KEY, "
                  "client_token TEXT, "
                  # "user_id TEXT NOT NULL, "
                  "profile_id TEXT NOT NULL, "
                  "create_time DATETIME DEFAULT (strftime('%d-%m-%Y %H:%M:%S', 'now', 'localtime')), "
                  "update_time DATETIME DEFAULT (strftime('%d-%m-%Y %H:%M:%S', 'now', 'localtime')), "
                  "FOREIGN KEY (profile_id) REFERENCES profiles (profile_id) ON DELETE CASCADE )")

        c.execute("CREATE TABLE IF NOT EXISTS sessions "
                  "(server_id TEXT NOT NULL PRIMARY KEY, "
                  "profile_id TEXT NOT NULL, "
                  "create_time DATETIME DEFAULT (strftime('%d-%m-%Y %H:%M:%S', 'now', 'localtime')), "
                  "update_time DATETIME DEFAULT (strftime('%d-%m-%Y %H:%M:%S', 'now', 'localtime')), "
                  "FOREIGN KEY (profile_id) REFERENCES profiles (profile_id) ON DELETE CASCADE )")

        self.conn.commit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    @staticmethod
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def close(self):
        self.conn.close()

    # Profiles
    def new_profile(self, profile_name: str, is_primary: bool, user_name: str, user_id: UUID or str = None):
        # skin_test = "ewogICJ0aW1lc3RhbXAiIDogMTU5NjU0NzYxNTYyOSwKICAicHJvZmlsZUlkIiA6ICI1OTgzZjkxY2UzY2M0MzdjYjc0ZTZlMTJmNWY0YzNlZCIsCiAgInByb2ZpbGVOYW1lIiA6ICJOaW5nYV9LaXR0eSIsCiAgInNpZ25hdHVyZVJlcXVpcmVkIiA6IGZhbHNlLAogICJ0ZXh0dXJlcyIgOiB7CiAgICAiU0tJTiIgOiB7CiAgICAgICJ1cmwiIDogImh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvNTQyZDI2YTMzMWRlOTA1YjQ1OTU1ZDZiMTFlZTFjZTAwYjEwZjRmMzA5Nzc1ZTUzNGRjNzQzMzNkNmE5ZjI4OCIKICAgIH0KICB9Cn0="
        c = self.conn.cursor()
        c.execute("INSERT INTO profiles "
                   "(profile_id, profile_name, user_id, user_name, is_primary) VALUES"
                   "(?, ?, ?, ?, ?)",
                   (str(uuid4()), profile_name,
                    (str(user_id) if user_id else str(uuid4())),
                    user_name, is_primary))
        self.conn.commit()

    def get_user_by_username(self, username) -> tuple:
        c = self.conn.cursor()
        c.execute("SELECT * FROM profiles WHERE user_name = ?", (username,))
        return c.fetchone()

    # Yggdrasil Tokens
    def new_token(self, profile_id, access_token, client_token):
        c = self.conn.cursor()

        c.execute("INSERT INTO tokens "
                  "(profile_id, access_token, client_token) VALUES"
                  "(?, ?, ?)",
                  (profile_id, access_token, client_token))
        self.conn.commit()

    def get_token(self, access_token):
        c = self.conn.cursor()
        c.execute("SELECT * FROM tokens WHERE access_token = ?", (access_token,))
        return c.fetchone()

    # def set_target_update_time(self, target: str) -> None:
    #     c = self.conn.cursor()
    #
    #     c.execute("UPDATE tagrets "
    #               "SET update_time = (strftime('%d-%m-%Y %H:%M:%S', 'now', 'localtime'))"
    #               "WHERE target = ?", (target,))
    #
    #     if c.rowcount == 0:
    #         c.execute("INSERT INTO tagrets "
    #                   "(target, update_time) "
    #                   "VALUES (?, (strftime('%d-%m-%Y %H:%M:%S', 'now', 'localtime')))",
    #                   (target,))
    #
    #     self.conn.commit()
    #
    # def get_targets(self) -> List[tuple]:
    #     c = self.conn.cursor()
    #     c.execute("SELECT target, update_time FROM tagrets")
    #     return c.fetchall()
    #
    # def get_unresponded_commands(self, target=None) -> List[tuple]:
    #     c = self.conn.cursor()
    #     if target:
    #         c.execute("SELECT id, command, timeout FROM hystori "
    #                   "WHERE output IS NULL "
    #                   "AND target = ?", (target,))
    #         self.set_target_update_time(target)
    #     else:
    #         c.execute("SELECT id, command, timeout FROM hystori WHERE output IS NULL")
    #     return c.fetchall()
    #
    # def new_command(self, target: str, command: str, timeout: int) -> int:
    #     c = self.conn.cursor()
    #     c.execute("INSERT INTO hystori (target, command, timeout) VALUES (?, ?, ?)", (target, command, timeout))
    #     self.conn.commit()
    #     return c.lastrowid
    #
    # def del_command(self, command_id: int):
    #     c = self.conn.cursor()
    #     c.execute("DELETE FROM hystori WHERE id = ?", (command_id,))
    #     self.conn.commit()
    #
    # def set_output(self, command_id: int, output: str) -> None:
    #     c = self.conn.cursor()
    #     c.execute("UPDATE hystori SET output_time = (strftime('%d-%m-%Y %H:%M:%S', 'now', 'localtime')), "
    #               "output = ? "
    #               "WHERE id = ?", (output, command_id))
    #     self.conn.commit()
    #
    # def get_command(self, command_id: int) -> tuple:
    #     c = self.conn.cursor()
    #     c.execute("SELECT command, output FROM hystori WHERE id = ?", (command_id,))
    #     return c.fetchone()
    #
    # def get_command_output(self, command_id: int) -> str:
    #     c = self.conn.cursor()
    #     c.execute("SELECT output FROM hystori WHERE id = ?", (command_id,))
    #     return c.fetchone()[0]
    #
    # def get_all_commands(self) -> List[tuple]:
    #     c = self.conn.cursor()
    #     c.execute("SELECT id, target, command, output, create_time, output_time, timeout FROM hystori")
    #     return c.fetchall()


if __name__ == "__main__":
    db = DB(":memory:")

    db.new_profile("test1", True, "test")

    cu = db.conn.cursor()
    cu.execute("SELECT * FROM profiles")
    print(cu.fetchall())

    while True:
        cu = db.conn.cursor()
        cu.execute(input(">> "))
        cu.fetchall()
    # id1 = db.new_command("test1")
    # db.new_command("test2")
    #
    # print(db.get_unresponded_commands())
    #
    # db.set_output(id1, "output1")
    # print(db.get_command(id1))
    #
    # print(db.get_unresponded_commands())
