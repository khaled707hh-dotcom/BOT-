import discord
from discord.ext import commands
import random
import os
import json

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# ====== بيانات ======
money = {}
games_enabled = True

# ====== تحميل / حفظ ======
def load_data():
    global money
    try:
        with open("money.json", "r") as f:
            money = json.load(f)
    except:
        money = {}

def save_data():
    with open("money.json", "w") as f:
        json.dump(money, f, indent=4)

# ====== تشغيل ======
@bot.event
async def on_ready():
    load_data()
    print(f"✅ البوت اشتغل: {bot.user}")

# ====== ترحيب ======
@bot.event
async def on_member_join(member):
    if member.guild.system_channel:
        await member.guild.system_channel.send(f"👋 أهلاً {member.mention}")

# ====== ردود + أوامر ======
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if "السلام عليكم" in message.content:
        await message.channel.send("وعليكم السلام منور")

    if message.content.strip() == "السلام":
        await message.channel.send("السلام")

    await bot.process_commands(message)

# ====== أوامر ======
@bot.command()
async def مرحبا(ctx):
    await ctx.send(f"هلا {ctx.author.mention} 👋")

@bot.command()
async def اوامر(ctx):
    await ctx.send("""
📜 الأوامر:

🎮 ألعاب:
!خمن
!روليت [مبلغ]
!حجر

💰 اقتصاد:
!فلوسي
!راتب

⚙️ تحكم:
!تشغيل_الالعاب
!ايقاف_الالعاب
""")

# ====== تشغيل / إيقاف ======
@bot.command()
@commands.has_permissions(administrator=True)
async def تشغيل_الالعاب(ctx):
    global games_enabled
    games_enabled = True
    await ctx.send("🟢 تم تشغيل الألعاب")

@bot.command()
@commands.has_permissions(administrator=True)
async def ايقاف_الالعاب(ctx):
    global games_enabled
    games_enabled = False
    await ctx.send("🔴 تم إيقاف الألعاب")

# ====== فلوس ======
@bot.command()
async def فلوسي(ctx):
    user_id = str(ctx.author.id)
    bal = money.get(user_id, 0)
    await ctx.send(f"💰 فلوسك: {bal}$")

@bot.command()
@commands.cooldown(1, 60, commands.BucketType.user)
async def راتب(ctx):
    user_id = str(ctx.author.id)
    amount = random.randint(50, 150)
    money[user_id] = money.get(user_id, 0) + amount
    save_data()
    await ctx.send(f"💵 استلمت {amount}$")

# ====== خمن ======
@bot.command()
async def خمن(ctx):
    if not games_enabled:
        await ctx.send("❌ الألعاب مقفلة")
        return

    number = random.randint(1, 10)
    await ctx.send("🎮 خمن رقم من 1 إلى 10")

    def check(m):
        return m.author == ctx.author

    try:
        msg = await bot.wait_for('message', check=check, timeout=10)
        if int(msg.content) == number:
            user_id = str(ctx.author.id)
            money[user_id] = money.get(user_id, 0) + 50
            save_data()
            await ctx.send("🔥 صح! +50$")
        else:
            await ctx.send(f"❌ غلط، الرقم {number}")
    except Exception as e:
        print(e)
        await ctx.send("⏰ انتهى الوقت")

# ====== روليت ======
@bot.command()
async def روليت(ctx, bet: int):
    if not games_enabled:
        await ctx.send("❌ الألعاب مقفلة")
        return

    if bet <= 0:
        await ctx.send("❌ لازم تحط مبلغ موجب")
        return

    user_id = str(ctx.author.id)
    bal = money.get(user_id, 0)

    if bet > bal:
        await ctx.send("❌ ما عندك فلوس كفاية")
        return

    if random.choice([True, False]):
        money[user_id] += bet
        await ctx.send(f"🎰 فزت! +{bet}$")
    else:
        money[user_id] -= bet
        await ctx.send(f"💔 خسرت! -{bet}$")

    save_data()

# ====== حجر ======
@bot.command()
async def حجر(ctx):
    if not games_enabled:
        await ctx.send("❌ الألعاب مقفلة")
        return

    choices = ["حجر", "ورقة", "مقص"]
    bot_choice = random.choice(choices)

    await ctx.send("اكتب: حجر / ورقة / مقص")

    def check(m):
        return m.author == ctx.author

    try:
        msg = await bot.wait_for('message', check=check, timeout=10)
        user_choice = msg.content

        if user_choice not in choices:
            await ctx.send("❌ اختيار غلط")
            return

        user_id = str(ctx.author.id)

        if user_choice == bot_choice:
            await ctx.send(f"🤝 تعادل ({bot_choice})")
        elif (user_choice == "حجر" and bot_choice == "مقص") or \
             (user_choice == "ورقة" and bot_choice == "حجر") or \
             (user_choice == "مقص" and bot_choice == "ورقة"):
            money[user_id] = money.get(user_id, 0) + 30
            save_data()
            await ctx.send(f"🔥 فزت ({bot_choice}) +30$")
        else:
            await ctx.send(f"💔 خسرت ({bot_choice})")

    except Exception as e:
        print(e)
        await ctx.send("⏰ انتهى الوقت")

# ====== أخطاء ======
@راتب.error
async def salary_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏳ انتظر {round(error.retry_after)} ثانية")

# ====== تشغيل ======
bot.run(os.getenv("TOKEN"))