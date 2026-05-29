import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import os

# =========================
# BOT SETTINGS
# =========================

TOKEN = "8978008603:AAEHkkpwbmevTaPrmxQWWJj0PMeyJKKfNgs"
CHANNEL_USERNAME = "@crazymithx"
ADMIN_ID = 8406158643
QR_IMAGE_URL = "https://i.postimg.cc/t4L4g7cK/IMG-20260528-182945.jpg"
BOT_NAME = "ICSART"
SUPPORT_USERNAME = "Crazyoffical8"
REFER_BONUS = 20

bot = telebot.TeleBot(TOKEN)

# =========================
# DATABASE
# =========================

USERS_FILE = "users.json"

if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({}, f)

with open(USERS_FILE, "r") as f:
    users = json.load(f)

# Admin pending reply state
pending_replies = {}

# =========================
# SAVE USERS
# =========================

def save_users():
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

# =========================
# HELPER: Get or create user
# =========================

def get_user(user_id):
    user_id = str(user_id)
    if user_id not in users:
        users[user_id] = {}
    defaults = {
        "name": "Unknown",
        "username": "",
        "credits": 50,
        "verified": False,
        "premium": False,
        "total_scripts": 0,
        "referred_by": None,
        "referrals": []
    }
    changed = False
    for key, value in defaults.items():
        if key not in users[user_id]:
            users[user_id][key] = value
            changed = True
    if changed:
        save_users()
    return users[user_id]

def update_user_info(from_user):
    user = get_user(str(from_user.id))
    user["name"] = from_user.first_name or "Unknown"
    user["username"] = from_user.username or ""
    save_users()
    return user

# =========================
# HELPER: Build main menu
# =========================

def build_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(InlineKeyboardButton("📢 Join Channel", url="https://t.me/crazymithx"))
    kb.add(InlineKeyboardButton("✅ Verify", callback_data="verify"))
    kb.add(
        InlineKeyboardButton("🪙 Credits", callback_data="credits_btn"),
        InlineKeyboardButton("👤 Profile", callback_data="profile_btn")
    )
    kb.add(
        InlineKeyboardButton("📜 History", callback_data="history_btn"),
        InlineKeyboardButton("👥 Refer", callback_data="refer_btn")
    )
    kb.add(
        InlineKeyboardButton("💎 Premium", callback_data="buy"),
        InlineKeyboardButton("🆘 Support", url="https://t.me/" + SUPPORT_USERNAME)
    )
    return kb

# =========================
# ALL COMMANDS - Pehle define karo
# =========================

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.chat.id)
    args = message.text.split()
    is_new = user_id not in users
    user = update_user_info(message.from_user)

    if is_new and len(args) > 1:
        referrer_id = args[1]
        if referrer_id != user_id and referrer_id in users:
            user["referred_by"] = referrer_id
            users[referrer_id]["credits"] += REFER_BONUS
            users[referrer_id]["referrals"].append(user_id)
            save_users()
            try:
                bot.send_message(int(referrer_id), "🎉 New Referral! +" + str(REFER_BONUS) + " Credits Mila!")
            except:
                pass

    status = "⭐ Premium" if user["premium"] else "🆓 Free"
    text = (
        "╔══════════════╗\n"
        "    🎨 " + BOT_NAME + "\n"
        "╚══════════════╝\n\n"
        "👋 Hello " + user["name"] + "!\n\n"
        "👤 Status: " + status + "\n"
        "🪙 Credits: " + str(user["credits"]) + "\n"
        "📜 Total Scripts: " + str(user["total_scripts"]) + "\n\n"
        "✍️ Script bhejo aur process karo!"
    )
    bot.send_message(message.chat.id, text, reply_markup=build_menu())


@bot.message_handler(commands=['profile'])
def profile(message):
    user = update_user_info(message.from_user)
    status = "⭐ Premium" if user["premium"] else "🆓 Free"
    uname = "@" + user.get("username", "") if user.get("username") else "N/A"
    text = (
        "👤 PROFILE\n\n"
        "🙍 Name: " + user.get("name", "Unknown") + "\n"
        "📛 Username: " + uname + "\n"
        "🆔 ID: " + str(message.chat.id) + "\n"
        "🪙 Credits: " + str(user["credits"]) + "\n"
        "🏷️ Status: " + status + "\n"
        "📜 Scripts: " + str(user["total_scripts"]) + "\n"
        "✅ Verified: " + str(user["verified"]) + "\n"
        "👥 Referrals: " + str(len(user.get("referrals", [])))
    )
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['credits'])
def credits_cmd(message):
    user = get_user(str(message.chat.id))
    bot.send_message(message.chat.id, "🪙 Credits: " + str(user["credits"]) + "\n\n💡 1 Word = 1 Credit")


@bot.message_handler(commands=['help'])
def help_cmd(message):
    bot.send_message(
        message.chat.id,
        "📖 COMMANDS\n\n"
        "/start - Main Menu\n"
        "/profile - Profile dekho\n"
        "/credits - Credits dekho\n"
        "/help - Help\n\n"
        "✍️ Koi bhi text bhejo script ke liye!\n"
        "💡 1 Word = 1 Credit"
    )


# =========================
# ADMIN COMMANDS - Pehle define karo
# =========================

@bot.message_handler(commands=['stats'])
def stats(message):
    if message.chat.id != ADMIN_ID:
        return
    total = len(users)
    premium = sum(1 for u in users.values() if u.get("premium"))
    verified = sum(1 for u in users.values() if u.get("verified"))
    scripts = sum(u.get("total_scripts", 0) for u in users.values())
    bot.send_message(
        ADMIN_ID,
        "📊 BOT STATS\n\n"
        "👥 Total Users: " + str(total) + "\n"
        "✅ Verified: " + str(verified) + "\n"
        "💎 Premium: " + str(premium) + "\n"
        "📜 Total Scripts: " + str(scripts)
    )


@bot.message_handler(commands=['allusers'])
def allusers(message):
    if message.chat.id != ADMIN_ID:
        return
    if not users:
        bot.send_message(ADMIN_ID, "❌ Koi user nahi hai.")
        return
    lines = []
    count = 0
    for uid, data in users.items():
        count += 1
        status = "💎" if data.get("premium") else "🆓"
        verified = "✅" if data.get("verified") else "❌"
        name = data.get("name", "Unknown")
        uname = "@" + data["username"] if data.get("username") else "N/A"
        lines.append(
            str(count) + ". " + status + verified + " " + name + " (" + uname + ")\n"
            "   🆔 " + uid + "\n"
            "   🪙 " + str(data.get("credits", 0)) + " | 📜 " + str(data.get("total_scripts", 0)) + " scripts"
        )
        if count % 15 == 0:
            bot.send_message(ADMIN_ID, "\n\n".join(lines))
            lines = []
    if lines:
        header = "👥 ALL USERS (" + str(len(users)) + " total)\n" + "="*25 + "\n\n"
        bot.send_message(ADMIN_ID, header + "\n\n".join(lines))


@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.chat.id != ADMIN_ID:
        return
    parts = message.text.split(None, 1)
    if len(parts) < 2:
        bot.send_message(ADMIN_ID, "Usage:\n/broadcast MESSAGE")
        return
    msg = parts[1]
    sent = failed = 0
    for uid in users:
        try:
            bot.send_message(uid, msg)
            sent += 1
        except:
            failed += 1
    bot.send_message(ADMIN_ID, "✅ Sent: " + str(sent) + "\n❌ Failed: " + str(failed))


@bot.message_handler(commands=['addcredits'])
def addcredits(message):
    if message.chat.id != ADMIN_ID:
        return
    try:
        parts = message.text.split()
        target_id = parts[1]
        amount = int(parts[2])
        user = get_user(target_id)
        user["credits"] += amount
        save_users()
        bot.send_message(ADMIN_ID, "✅ " + str(amount) + " Credits diye " + target_id + " ko")
        try:
            bot.send_message(int(target_id), "🎉 Tumhe " + str(amount) + " Credits Mila!")
        except:
            pass
    except (IndexError, ValueError):
        bot.send_message(ADMIN_ID, "Usage:\n/addcredits USER_ID AMOUNT")


@bot.message_handler(commands=['addpremium'])
def addpremium(message):
    if message.chat.id != ADMIN_ID:
        return
    try:
        target_id = message.text.split()[1]
        user = get_user(target_id)
        user["premium"] = True
        user["credits"] += 20000
        save_users()
        bot.send_message(ADMIN_ID, "✅ " + target_id + " ko Premium Diya")
        try:
            bot.send_message(int(target_id), "🎉 Premium Activate!\n\n💎 Unlimited Scripts Enjoy Karo!")
        except:
            pass
    except IndexError:
        bot.send_message(ADMIN_ID, "Usage:\n/addpremium USER_ID")


@bot.message_handler(commands=['removepremium'])
def removepremium(message):
    if message.chat.id != ADMIN_ID:
        return
    try:
        target_id = message.text.split()[1]
        user = get_user(target_id)
        user["premium"] = False
        save_users()
        bot.send_message(ADMIN_ID, "✅ " + target_id + " ka Premium Hata Diya")
    except IndexError:
        bot.send_message(ADMIN_ID, "Usage:\n/removepremium USER_ID")


@bot.message_handler(commands=['userinfo'])
def userinfo(message):
    if message.chat.id != ADMIN_ID:
        return
    try:
        target_id = message.text.split()[1]
        if target_id not in users:
            bot.send_message(ADMIN_ID, "❌ User Not Found")
            return
        u = users[target_id]
        status = "⭐ Premium" if u.get("premium") else "🆓 Free"
        uname = "@" + u["username"] if u.get("username") else "N/A"
        bot.send_message(
            ADMIN_ID,
            "👤 USER INFO\n\n"
            "🙍 Name: " + u.get("name", "Unknown") + "\n"
            "📛 Username: " + uname + "\n"
            "🆔 ID: " + target_id + "\n"
            "🪙 Credits: " + str(u.get("credits", 0)) + "\n"
            "🏷️ Status: " + status + "\n"
            "📜 Scripts: " + str(u.get("total_scripts", 0)) + "\n"
            "✅ Verified: " + str(u.get("verified", False)) + "\n"
            "👥 Referrals: " + str(len(u.get("referrals", [])))
        )
    except IndexError:
        bot.send_message(ADMIN_ID, "Usage:\n/userinfo USER_ID")


@bot.message_handler(commands=['cancel'])
def cancel_reply(message):
    if message.chat.id != ADMIN_ID:
        return
    admin_key = str(ADMIN_ID)
    if admin_key in pending_replies:
        del pending_replies[admin_key]
        bot.send_message(ADMIN_ID, "✅ Reply cancel ho gayi.")
    else:
        bot.send_message(ADMIN_ID, "❌ Koi pending reply nahi hai.")


# =========================
# CALLBACKS
# =========================

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    user_id = str(call.message.chat.id)

    if call.data.startswith("reply_") and call.message.chat.id == ADMIN_ID:
        target_id = int(call.data.replace("reply_", ""))
        pending_replies[str(ADMIN_ID)] = target_id
        bot.answer_callback_query(call.id, "✅ Ab audio/voice/text bhejo!")
        bot.send_message(
            ADMIN_ID,
            "🎙️ Ab voice, audio ya text bhejo — user ko jayega!\n"
            "❌ Cancel karna ho toh /cancel bhejo."
        )
        return

    user = get_user(user_id)

    if call.data == "verify":
        try:
            member = bot.get_chat_member(CHANNEL_USERNAME, call.from_user.id)
            if member.status in ["member", "administrator", "creator"]:
                user["verified"] = True
                save_users()
                bot.answer_callback_query(call.id, "✅ Verified!")
                bot.send_message(call.message.chat.id, "✅ Verification Successful!\n\nAb script bhejo.")
            else:
                bot.answer_callback_query(call.id, "❌ Join Karo Pehle!")
                bot.send_message(call.message.chat.id, "❌ Pehle Channel Join Karo!\n\nhttps://t.me/crazymithx")
        except Exception as e:
            bot.answer_callback_query(call.id, "❌ Error!")
            bot.send_message(call.message.chat.id, "❌ Error. Thodi der baad try karo.")

    elif call.data == "buy":
        caption = (
            "💎 " + BOT_NAME + " PREMIUM\n\n"
            "₹50 = 20,000 Credits\n\n"
            "✅ Unlimited Scripts\n"
            "✅ No Credit Deduction\n"
            "✅ Priority Support\n\n"
            "📸 Payment Screenshot bhejo:\n@" + SUPPORT_USERNAME
        )
        bot.answer_callback_query(call.id)
        bot.send_photo(call.message.chat.id, QR_IMAGE_URL, caption=caption)

    elif call.data == "profile_btn":
        status = "⭐ Premium" if user["premium"] else "🆓 Free"
        uname = "@" + user.get("username", "") if user.get("username") else "N/A"
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            "👤 PROFILE\n\n"
            "🙍 Name: " + user.get("name", "Unknown") + "\n"
            "📛 Username: " + uname + "\n"
            "🆔 ID: " + str(call.message.chat.id) + "\n"
            "🪙 Credits: " + str(user["credits"]) + "\n"
            "🏷️ Status: " + status + "\n"
            "📜 Scripts: " + str(user["total_scripts"]) + "\n"
            "✅ Verified: " + str(user["verified"]) + "\n"
            "👥 Referrals: " + str(len(user.get("referrals", [])))
        )

    elif call.data == "credits_btn":
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            "🪙 Credits: " + str(user["credits"]) + "\n\n"
            "💡 1 Word = 1 Credit\n"
            "🎁 Refer karo aur " + str(REFER_BONUS) + " credits pao!"
        )

    elif call.data == "history_btn":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "📜 Total Scripts: " + str(user["total_scripts"]))

    elif call.data == "refer_btn":
        bot_username = bot.get_me().username
        referrals = len(user.get("referrals", []))
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            "👥 Refer & Earn\n\n"
            "Apna link:\nhttps://t.me/" + bot_username + "?start=" + user_id + "\n\n"
            "🎁 Har referral: +" + str(REFER_BONUS) + " Credits\n"
            "👥 Tumhare Referrals: " + str(referrals)
        )


# =========================
# SCRIPT HANDLER - Sabse last mein
# =========================

@bot.message_handler(
    content_types=['text'],
    func=lambda msg: not msg.text.startswith('/') and msg.chat.id != ADMIN_ID
)
def handle_script(message):
    user_id = str(message.chat.id)
    user = update_user_info(message.from_user)

    if not user["verified"]:
        bot.send_message(
            message.chat.id,
            "❌ Pehle Channel Join Karke Verify Karo!\n\n/start pe jao aur ✅ Verify dabao."
        )
        return

    word_count = len(message.text.split())
    cost = 0 if user["premium"] else word_count

    if not user["premium"] and user["credits"] < cost:
        bot.send_message(
            message.chat.id,
            "❌ Credits Kam Hain!\n\n"
            "📝 Script Words: " + str(word_count) + "\n"
            "💰 Chahiye: " + str(cost) + " credits\n"
            "🪙 Tumhare pass: " + str(user["credits"]) + " credits\n\n"
            "💎 Premium lo ya refer karo!"
        )
        return

    if not user["premium"]:
        user["credits"] -= cost
    user["total_scripts"] += 1
    save_users()

    bot.send_message(
        message.chat.id,
        "✅ Script Admin Ko Bhej Diya!\n"
        "📝 Words: " + str(word_count) + " | 🪙 Use: " + str(cost) + "\n"
        "⏳ Thodi der mein audio milega..."
    )
    if not user["premium"]:
        bot.send_message(message.chat.id, "🪙 Baaki Credits: " + str(user["credits"]))

    uname_str = "@" + user["username"] if user.get("username") else "N/A"
    status = "⭐ Premium" if user["premium"] else "🆓 Free"

    reply_kb = InlineKeyboardMarkup()
    reply_kb.add(InlineKeyboardButton(
        "↩️ " + user["name"] + " ko Reply Karo",
        callback_data="reply_" + str(message.chat.id)
    ))

    bot.send_message(
        ADMIN_ID,
        "📩 NEW SCRIPT\n\n"
        "👤 Name: " + user["name"] + "\n"
        "🆔 ID: " + str(message.chat.id) + "\n"
        "📛 Username: " + uname_str + "\n"
        "🏷️ Status: " + status + "\n"
        "📝 Words: " + str(word_count) + "\n\n"
        "Script:\n" + message.text + "\n\n"
        "👇 Reply button dabao phir audio bhejo",
        reply_markup=reply_kb
    )


# =========================
# ADMIN REPLY HANDLER - Sabse last mein
# =========================

@bot.message_handler(
    content_types=['voice', 'audio', 'document'],
    func=lambda msg: msg.chat.id == ADMIN_ID
)
def admin_media_handler(message):
    admin_key = str(ADMIN_ID)
    if admin_key not in pending_replies:
        bot.send_message(ADMIN_ID, "❌ Pehle kisi ka Reply button dabao!")
        return

    target_user_id = pending_replies[admin_key]
    try:
        if message.content_type == 'voice':
            bot.send_voice(target_user_id, message.voice.file_id, caption="🎙️ Tumhari voice aa gayi!")
        elif message.content_type == 'audio':
            bot.send_audio(target_user_id, message.audio.file_id, caption="🎵 Tumhari audio aa gayi!")
        elif message.content_type == 'document':
            bot.send_document(target_user_id, message.document.file_id, caption="📁 Admin ki taraf se file")

        bot.send_message(ADMIN_ID, "✅ " + str(target_user_id) + " ko bhej diya!")
        del pending_replies[admin_key]
    except Exception as e:
        bot.send_message(ADMIN_ID, "❌ Error: " + str(e))


@bot.message_handler(
    content_types=['text'],
    func=lambda msg: msg.chat.id == ADMIN_ID and not msg.text.startswith('/')
)
def admin_text_reply_handler(message):
    admin_key = str(ADMIN_ID)
    if admin_key not in pending_replies:
        return
    target_user_id = pending_replies[admin_key]
    try:
        bot.send_message(target_user_id, "📩 Admin ka jawab:\n\n" + message.text)
        bot.send_message(ADMIN_ID, "✅ " + str(target_user_id) + " ko bhej diya!")
        del pending_replies[admin_key]
    except Exception as e:
        bot.send_message(ADMIN_ID, "❌ Error: " + str(e))


# =========================
# RUN BOT
# =========================

print(BOT_NAME + " Bot Chal Raha Hai...")
bot.infinity_polling()
