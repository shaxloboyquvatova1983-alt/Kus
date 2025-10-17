from flask import Flask, request
from threading import Thread
from telebot import TeleBot, types
import random
import requests
import os

API_TOKEN = '7907926145:AAHvHgm4z1CF4xHtCV6LAt04Wyy0LY2rNv8'
ADMIN_ID = 6852738257
KARTA = '9860356610242188'
CHANNEL_LINK = "https://t.me/Sardor_ludoman"
WEBHOOK_URL = 'https://kus-v3wz.onrender.com'  # ← /webhook qilib qo‘yildi

bot = TeleBot(API_TOKEN)
user_data = {}
app = Flask(__name__)

def main_menu(chat_id, text="💎 TezkorPay - Tez va ishonchli to'lov tizimi"):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("💰 Hisob to'ldirish", callback_data="hisob"),
        types.InlineKeyboardButton("💸 Pul yechish", callback_data="yechish")
    )
    markup.add(types.InlineKeyboardButton("📞 Qo'llab-quvvatlash", callback_data="aloqa"))
    
    # Admin panel tugmasini faqat admin uchun qo'shish
    if chat_id == ADMIN_ID:
        markup.add(types.InlineKeyboardButton("👨‍💼 Admin Panel", callback_data="admin_panel"))
    
    bot.send_message(chat_id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "aloqa")
def aloqa_handler(call):
    bot.answer_callback_query(call.id)
    
    text = (
        "🎧 QO'LLAB-QUVVATLASH XIZMATI\n\n"
        "💬 Sizda savol yoki muammo bormi?\n"
        "🚀 Bizning mutaxassislarimiz 24/7 xizmatda!\n\n"
        "📱 Quyidagi usullar orqali bog'laning:"
    )
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("💬 Telegram Admin", url="https://t.me/KASSA_SPED"),
        types.InlineKeyboardButton("🔙 Asosiy menyu", callback_data="back_main")
    )
    
    bot.edit_message_text(text, chat_id=call.message.chat.id, 
                         message_id=call.message.message_id, reply_markup=markup)

def check_subscription(user_id):
    """Obuna tekshirish funksiyasi"""
    try:
        member = bot.get_chat_member(chat_id="@Sardor_ludoman", user_id=user_id)
        return member.status not in ['left', 'kicked']
    except Exception:
        return False

def send_subscription_message(chat_id):
    """Obuna xabarini yuborish"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📢 Kanalga obuna bo'lish", url=CHANNEL_LINK),
        types.InlineKeyboardButton("✅ Obunani tekshirish", callback_data="check_sub")
    )
    bot.send_message(chat_id,
                     "🔒 Botdan foydalanish uchun avval kanalimizga obuna bo'ling!\n\n"
                     "Obuna bo'lgandan so'ng 'Obunani tekshirish' tugmasini bosing.",
                     reply_markup=markup)

@bot.message_handler(commands=['start'])
def start(message):
    cid = message.chat.id
    
    # Obuna tekshiruvi (admin uchun emas)
    if cid != ADMIN_ID and not check_subscription(cid):
        return send_subscription_message(cid)
    
    # Foydalanuvchi ma'lumotlarini boshlang'ich holatga o'rnatish
    user_data[cid] = {}
    
    welcome_text = "🎉 Assalomu aleykum!\n\n" \
                  "💎 TezkorPay ga xush kelibsiz!\n\n" \
                  "⚡ Tez, xavfsiz va ishonchli to'lov tizimi\n" \
                  "🔒 100% kafolatlangan tranzaksiyalar\n" \
                  "🎯 Minimal komissiya to'lovlari\n\n" \
                  "Kerakli bo'limni tanlang 👇"
    
    main_menu(cid, welcome_text)

@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    bot.answer_callback_query(call.id)
    cid = call.message.chat.id
    message_id = call.message.message_id
    
    # Foydalanuvchi ma'lumotlarini ta'minlash
    if cid not in user_data:
        user_data[cid] = {}
    data = user_data[cid]
    
    # Inline xabarni o'chirish funksiyasi
    def remove_message():
        try:
            bot.delete_message(cid, message_id)
        except Exception:
            pass
    
    if call.data == "check_sub":
        if check_subscription(call.from_user.id):
            remove_message()
            main_menu(cid, "🎉 Tabriklaymiz! Endi botdan to'liq foydalanishingiz mumkin.")
        else:
            bot.answer_callback_query(call.id, "❌ Siz hali kanalga obuna bo'lmagansiz!", show_alert=True)
    
    elif call.data == "admin_panel":
        if cid == ADMIN_ID:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("📊 Bot statistikasi", callback_data="statistika"))
            markup.add(types.InlineKeyboardButton("📢 Foydalanuvchilarga xabar yuborish", callback_data="xabar_yuborish"))
            markup.add(types.InlineKeyboardButton("🔙 Orqaga", callback_data="back_main"))
            bot.edit_message_text("👨‍💼 Boshqaruv", chat_id=cid, message_id=message_id, reply_markup=markup)
    
    elif call.data == "statistika":
        if cid == ADMIN_ID:
            user_count = len([uid for uid in user_data.keys() if uid != ADMIN_ID])
            text = f"📊 Statistika:\n\n👥 Foydalanuvchilar: {user_count} ta"
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Admin Panel", callback_data="admin_panel"))
            bot.edit_message_text(text, chat_id=cid, message_id=message_id, reply_markup=markup)
    
    elif call.data == "xabar_yuborish":
        if cid == ADMIN_ID:
            user_data[cid]['broadcast'] = True
            remove_message()
            bot.send_message(cid, "📝 Xabar matnini yozing:")
    
    elif call.data == "hisob":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.row(types.InlineKeyboardButton("1xBet UZS",
        callback_data="buk_1xBet"),
        types.InlineKeyboardButton("MelBet UZS",callback_data="buk_MelBet"))
        markup.row(types.InlineKeyboardButton("Betwiner UZS", callback_data="buk_Betwiner"),
        types.InlineKeyboardButton("WinWin UZS",callback_data="buk_WinWin"))
        markup.row(types.InlineKeyboardButton("MostBet UZS",callback_data="buk_MostBet"),
        types.InlineKeyboardButton("🔙 Asosiy menyu", callback_data="back_main"))
        
        user_data[cid] = {"type": "hisob"}
        bot.edit_message_text("🏢 Bukmeker kompaniyangizni tanlang:", 
                             chat_id=cid, message_id=message_id, reply_markup=markup)
    
    elif call.data == "yechish":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.row(types.InlineKeyboardButton("1xBet UZS",  callback_data="out_1xBet"),
         types.InlineKeyboardButton("MelBet UZS",callback_data="out_MelBet"))
        markup.row(types.InlineKeyboardButton("Betwiner UZS",callback_data="out_Betwiner"),
        types.InlineKeyboardButton("WinWin UZS",callback_data="out_WinWin"))
        markup.row(types.InlineKeyboardButton("MostBet UZS",callback_data="out_MostBet"),
        types.InlineKeyboardButton("🔙 Asosiy menyu", callback_data="back_main"))
        
        user_data[cid] = {"type": "yechish"}
        bot.edit_message_text("🏢 Bukmeker kompaniyangizni tanlang:", 
                             chat_id=cid, message_id=message_id, reply_markup=markup)
    
    elif call.data.startswith("buk_") or call.data.startswith("out_"):
        action = "to'ldirish" if call.data.startswith("buk_") else "yechish"
        user_data[cid]['bukmeker'] = call.data[4:]
        user_data[cid]['username'] = call.from_user.username
        
        bot.edit_message_text(f"🆔 {action.title()} uchun ID raqamingizni kiriting:\n\n"
                             "ID 9 yoki 11 raqamdan iborat bo'lishi kerak.",
                             chat_id=cid, message_id=message_id)
    
    elif call.data == "back_main":
        user_data[cid] = {}
        remove_message()
        main_menu(cid, "🏠 Asosiy menyuga qaytdingiz.")
    
    elif call.data == "tasdiq":
        if data.get("type") == "hisob":
            user_data[cid]['awaiting_chek'] = True
            bot.edit_message_text("📸 To'lov chekini rasm shaklida yuboring:Pdf va boshqa format qabul qilinmaydi..", 
                                 chat_id=cid, message_id=message_id)
        
        elif data.get("type") == "yechish":
            # Admin uchun so'rov yuborish
            admin_text = (
                f"📤 YANGI PUL YECHISH SO'ROVI\n\n"
                f"👤 Foydalanuvchi: @{data.get('username', 'Noaniq')}\n"
                f"🏢 Bukmeker: {data.get('bukmeker')}\n"
                f"🆔 ID: <code>{data.get('id')} </code>\n"
                f"💳 Karta: {data.get('card')}\n"
                f"💰 Summa: {data.get('summa'):,} so'm\n"
                f"🔐 Maxsus kod: <code>{data.get('kod')} </code>\n"
            )
            
            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(
                types.InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"admin_ok_{cid}"),
                types.InlineKeyboardButton("❌ Rad etish", callback_data=f"admin_no_{cid}")
            )
            
            bot.send_message(ADMIN_ID, admin_text, reply_markup=markup, parse_mode="HTML")
            
            # Foydalanuvchiga javob
            bot.edit_message_text("⏳ So'rovingiz qabul qilindi va ko'rib chiqilmoqda.\n"
                                 "Tez orada natija haqida xabar beramiz!", 
                                 chat_id=cid, message_id=message_id)
            user_data[cid] = {}
            
    # Admin javoblari
    elif call.data.startswith("admin_ok_") and cid == ADMIN_ID:
        uid = int(call.data.split("_")[2])
        info = user_data.get(uid, {})
        
        if info.get("type") == "hisob":
            success_text = f"✅ Hisob to'ldirish muvaffaqiyatli!\n\n" \
                          f"💰 {info.get('summa', 0):,} so'm ID: {info.get('id')} raqamingizga o'tkazildi."
        else:
            success_text = f"✅ Pul yechish muvaffaqiyatli!\n\n" \
                          f"💰 {info.get('summa', 0):,} so'm karta raqamingizga o'tkazildi."
        
        try:
            bot.send_message(uid, success_text)
            main_menu(uid)
        except Exception:
            pass
        
        bot.edit_message_reply_markup(cid, message_id, reply_markup=None)
        bot.send_message(cid, f"✅ So'rov tasdiqlandi va foydalanuvchiga xabar yuborildi!")
        
        if uid in user_data:
            user_data[uid] = {}
    
    elif call.data.startswith("admin_no_") and cid == ADMIN_ID:
        uid = int(call.data.split("_")[2])
        
        try:
            bot.send_message(uid, "❌ So'rovingiz ayrim sabablarga ko'ra rad etildi.\n\n"
                                 "Batafsil ma'lumot uchun admin bilan bog'laning.")
            main_menu(uid)
        except Exception:
            pass
        
        bot.edit_message_reply_markup(cid, message_id, reply_markup=None)
        bot.send_message(cid, f"❌ So'rov rad etildi va foydalanuvchiga xabar yuborildi!")
        
        if uid in user_data:
            user_data[uid] = {}

@bot.message_handler(content_types=['photo'])
def receive_photo(message):
    cid = message.chat.id
    data = user_data.get(cid, {})
    
    if data.get("type") == "hisob" and data.get("awaiting_chek"):
        photo_id = message.photo[-1].file_id
        
        # Admin uchun chek yuborish
        caption = (
            f"🧾 YANGI TO'LOV CHEKI\n\n"
            f"👤 @{message.from_user.username or 'Noaniq'}\n"
            f"🏢 Bukmeker: {data.get('bukmeker')}\n"
            f"🆔 ID: <code>{data.get('id')} </code>\n"
            f"💳 Karta: {data.get('card')}\n"
            f"💰 Summa: {data.get('toliq_sum', 0):,} so'm"
        )
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"admin_ok_{cid}"),
            types.InlineKeyboardButton("❌ Rad etish", callback_data=f"admin_no_{cid}")
        )
        
        bot.send_photo(ADMIN_ID, photo_id, caption=caption, reply_markup=markup, parse_mode="HTML")
        
        # Foydalanuvchiga javob
        bot.send_message(cid, "✅ Tolov qabul qilindi! Tez orada hisobingizga tushadi..")
        user_data[cid]['awaiting_chek'] = False
        main_menu(cid)

@bot.message_handler(func=lambda m: True)
def handle_messages(message):
    cid = message.chat.id
    text = message.text.strip()
    
    if cid not in user_data:
        user_data[cid] = {}
    data = user_data[cid]
    
    # Admin broadcast
    if cid == ADMIN_ID and data.get('broadcast'):
        sent_count = 0
        for user_id in user_data.keys():
            if user_id != ADMIN_ID:
                try:
                    bot.send_message(user_id, text)
                    sent_count += 1
                except Exception:
                    pass
        
        bot.send_message(ADMIN_ID, f"✅ Xabar {sent_count} ta foydalanuvchiga yuborildi.")
        user_data[cid].pop('broadcast', None)
        main_menu(cid)
        return
    
    # Agar foydalanuvchi jarayonda bo'lmasa
    if not data.get("type"):
        return main_menu(cid, "❗️Noma'llum buyruq iltimos, menyudan kerakli bo'limni tanlang.")
    
    # Hisob to'ldirish
    if data.get("type") == "hisob":
        if 'id' not in data:
            if not text.isdigit() or len(text) not in [9, 10]:
                return bot.send_message(cid, "❌ ID 9 yoki 10 raqamdan iborat bo'lishi kerak!")
            data['id'] = text
            return bot.send_message(cid, "💳 Karta raqamingizni kiriting (16 raqam):")
        
        elif 'card' not in data:
            if not text.isdigit() or len(text) != 16:
                return bot.send_message(cid, "❌ Karta raqami 16 raqamdan iborat bo'lishi kerak!")
            data['card'] = text
            return bot.send_message(cid, "💰 To'ldirish summasini kiriting:\n\n"
                                         "📋 Min: 3600 so'm\n📋 Max: 3,000,000 so'm")
        
        elif 'summa' not in data:
            try:
                summa = int(text)
                if not 3600 <= summa <= 3000000:
                    return bot.send_message(cid, "❌ Summa 3600 dan 3,000,000 so'm oralig'ida bo'lishi kerak!")
                
                # Random qo'shimcha
                random_add = random.randint(10, 99)
                toliq_sum = (summa // 100) * 100 + random_add
                
                data['summa'] = summa
                data['toliq_sum'] = toliq_sum
                
                markup = types.InlineKeyboardMarkup(row_width=2)
                markup.add(
                    types.InlineKeyboardButton("✅ Tasdiqlash", callback_data="tasdiq"),
                    types.InlineKeyboardButton("❌ Bekor qilish", callback_data="back_main")
                )
                
                payment_text = (
                    f"💳 TO'LOV MA'LUMOTLARI\n\n"
                    f"🏦 Karta: <code>{KARTA}</code>\n"
                    f"💰 To'lov summasi: <code>{toliq_sum:,} </code>so'm\n\n"
                    f"⚠️ DIQQAT: Aynan {toliq_sum:,} so'm o'tkazing!\n"
                    f"Buni emas: {summa:,} emas\n"
                    f"Buni o'tkazing:  <code>{toliq_sum:,}</code> so'm\n\n"
                    f"To'lov amalga oshirilgandan so'ng 'Tasdiqlash' tugmasini bosing."
                )
                
                bot.send_message(cid, payment_text, reply_markup=markup, parse_mode="HTML")
            except ValueError:
                bot.send_message(cid, "❌ Karta raqam faqat raqamlardan iborat!")
    
    # Pul yechish
    elif data.get("type") == "yechish":
        if 'id' not in data:
            if not text.isdigit() or len(text) not in [9, 10]:
                return bot.send_message(cid, "❌ ID raqam 9 yoki 10 raqamdan iborat bo'lishi kerak!")
            data['id'] = text
            return bot.send_message(cid, "💳 Pulni qabul qilish uchun karta raqamingizni kiriting:")
        
        elif 'card' not in data:
            if not text.isdigit() or len(text) != 16:
                return bot.send_message(cid, "❌ Karta raqami 16 raqamdan iborat bo'lishi kerak!")
            data['card'] = text
            return bot.send_message(cid, "💰 Yechish summasini kiriting:\n\n"
                                         "📋 Min: 11,500 so'm\n📋 Max: 10,000,000 so'm")
        
        elif 'summa' not in data:
            try:
                summa = int(text)
                if not 11500 <= summa <= 10000000:
                    return bot.send_message(cid, "❌ Summa 11,500 dan 10,000,000 so'm oralig'ida bo'lishi kerak!")
                data['summa'] = summa
                return bot.send_message(cid, "🔐 Maxsus kodni kiriting (4-8 ta belgi):")
            except ValueError:
                bot.send_message(cid, "❌ Faqat raqam kiriting!")
        
        elif 'kod' not in data:
            if not 4 <= len(text) <= 8:
                return bot.send_message(cid, "❌ Kod 4 dan 8 ta belgigacha bo'lishi kerak!")
            
            data['kod'] = text.upper()
            
            # Tasdiqlash
            confirmation_text = (
                f"📋 MA'LUMOTLARNI TEKSHIRING\n\n"
                f"🆔 ID: {data['id']}\n"
                f"💳 Karta: {data['card']}\n"
                f"💰 Summa: {data['summa']:,} so'm\n"
                f"🔐 Kod: {data['kod']}\n\n"
                f"⚠️ Barcha ma'lumotlar to'g'rimi?"
            )
            
            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(
                types.InlineKeyboardButton("✅ To'g'ri", callback_data="tasdiq"),
                types.InlineKeyboardButton("❌ Noto'g'ri", callback_data="back_main")
            )
            
            bot.send_message(cid, confirmation_text, reply_markup=markup)


# Webhookni qabul qilish
@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    else:
        return 'Invalid request', 400

# Webhookni o‘rnatish
@app.route('/set_webhook')
def set_webhook():
    url = f"{WEBHOOK_URL}/webhook"
    r = requests.get(f"https://api.telegram.org/bot{API_TOKEN}/setWebhook?url={url}")
    return r.json()

# 👇 Uptime uchun route
@app.route('/')
def home():
    return "✅ TezkorPay Bot ishlayapti!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
