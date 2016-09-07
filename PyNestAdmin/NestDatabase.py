import sqlite3
# from contextlib import closing


class NestDatabase(object):
    def __init__(self, config, force=False):
        self.config = config
        self.force = force
        self.database = 'nest_data.db'


    def init_db(self):
        result = {}
        if self.force:
            try:
                con = sqlite3.connect(self.database)
                cur = con.cursor()
                cur.executescript("""
                    drop table if exists data;
                    create table data (
                      id integer primary key autoincrement,
                      time_stamp integer,
                      structure_serial text,
                      device_serial text,
                      heating integer,
                      cooling integer,
                      target_temp integer,
                      target_humidity integer,
                      current_temp integer,
                      humidity integer,
                      outside_temp integer,
                      outside_humidity integer,
                      outside_wind_speed integer,
                      outside_wind_dir text,
                      away integer,
                      mode text,
                      battery_level real
                    );
                    """)
                cur.close()
                result['message'] = "Database initialized!"
            except:
                result['message'] = "There was an error."
        else:
            result['message'] = "This will delete your nest history! To confirm, run command with: --force"
        return result

    def dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def get_data(self):
        con = sqlite3.connect(self.database)
        con.row_factory = self.dict_factory
        cur = con.cursor()
        cur.execute("select * from data")
        data_list = cur.fetchall()
        data = {}
        for item in data_list:
            data[item['id']] = item
        con.close()
        return data

    def get_data_by_serial(self, serial):
        con = sqlite3.connect(self.database)
        con.row_factory = self.dict_factory
        cur = con.cursor()
        cur.execute("select * from data where device_serial = '{}'".format(serial))
        data_list = cur.fetchall()
        data = []
        for item in data_list:
            data.append(item)
        con.close()
        return data

    def get_serial(self):
        con = sqlite3.connect(self.database)
        con.row_factory = self.dict_factory
        cur = con.cursor()
        cur.execute("select device_serial, min(id) from data")
        data_list = cur.fetchall()
        data = {}
        for item in data_list:
            data[item['id']] = item
        con.close()
        return data