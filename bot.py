from config import TOKEN
from logic import DB_Map
import discord
from discord.ext import commands

manager = DB_Map("database.db")
manager.create_user_table()   # pastikan tabel user dibuat saat bot start

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


@bot.event
async def on_ready():
    print("Bot started")


@bot.command()
async def start(ctx):
    await ctx.send(f"Halo, {ctx.author.name}. Ketik **!help_me** untuk melihat daftar perintah.")


@bot.command()
async def help_me(ctx):
    help_text = (
        "**Daftar Perintah:**\n"
        "`!start` — salam pembuka\n"
        "`!show_city <nama kota>` — menampilkan posisi kota di peta\n"
        "`!remember_city <nama kota>` — menyimpan kota ke memori kamu\n"
        "`!show_my_cities` — menampilkan kota-kota yang kamu simpan di peta\n"
    )
    await ctx.send(help_text)


@bot.command()
async def show_city(ctx, city_name: str = "", marker_color: str = "red"):
    if city_name == "":
        return await ctx.send("Masukkan nama kota. Contoh: `!show_city Tokyo blue`")

    path = f"temp_{ctx.author.id}.png"

    if manager.create_graph(path, [city_name], marker_color=marker_color):
        await ctx.send(file=discord.File(path))
    else:
        await ctx.send("Kota tidak ditemukan dalam database.")



@bot.command()
async def show_my_cities(ctx, color="red"):
    cities = manager.select_cities(ctx.author.id)

    if not cities:
        return await ctx.send("Kamu belum menyimpan kota. Gunakan: `!remember_city <nama>`")

    path = f"temp_{ctx.author.id}.png"
    manager.create_graph(path, cities, marker_color=color)

    await ctx.send(f"Peta kota-kota kamu dengan warna **{color}**:")
    await ctx.send(file=discord.File(path))



@bot.command()
async def remember_city(ctx, *, city_name=""):
    if city_name == "":
        return await ctx.send("Format salah. Contoh: `!remember_city Paris`")

    status = manager.add_city(ctx.author.id, city_name)

    if status == 1:
        await ctx.send(f"Kota **{city_name}** berhasil disimpan!")
    elif status == 2:
        await ctx.send("Kota itu sudah tersimpan di memori kamu sebelumnya.")
    else:
        await ctx.send("Kota tidak ditemukan di database.")


if __name__ == "__main__":
    bot.run(TOKEN)
