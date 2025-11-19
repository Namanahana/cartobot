import sqlite3
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import cartopy.crs as ccrs


class DB_Map:
    def __init__(self, database):
        self.database = database

    def create_user_table(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users_cities (
                    user_id INTEGER,
                    city_id TEXT,
                    UNIQUE(user_id, city_id)
                )
            ''')
            conn.commit()

    def add_city(self, user_id, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM cities WHERE city=?", (city_name,))
            city_data = cursor.fetchone()

            if not city_data:
                return 0  # kota tidak ditemukan

            city_id = city_data[0]

            # cek apakah sudah ada
            cursor.execute("SELECT * FROM users_cities WHERE user_id=? AND city_id=?", (user_id, city_id))
            if cursor.fetchone():
                return 2  # sudah tersimpan

            conn.execute('INSERT INTO users_cities VALUES (?, ?)', (user_id, city_id))
            conn.commit()
            return 1  # sukses

    def select_cities(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT cities.city 
                FROM users_cities
                JOIN cities ON users_cities.city_id = cities.id
                WHERE user_id = ?
            ''', (user_id,))
            return [row[0] for row in cursor.fetchall()]

    def get_coordinates(self, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT lat, lng FROM cities WHERE city=?", (city_name,))
            return cursor.fetchone()

    def create_graph(self, path, cities, marker_color="red"):
        coords = []

        for c in cities:
            data = self.get_coordinates(c)
            if data:
                coords.append((c, data[0], data[1]))

        if not coords:
            return False

        plt.figure(figsize=(8, 6))
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.stock_img()
        ax.coastlines()

        for name, lat, lng in coords:
            ax.plot(lng, lat, marker='o', markersize=6, color=marker_color)
            ax.text(lng + 0.5, lat + 0.5, name, fontsize=9, color=marker_color)

        plt.savefig(path, dpi=200)
        plt.close()
        return True

    def draw_distance(self, city1, city2):
        pass  # bisa ditambahkan jika ingin fitur jarak
