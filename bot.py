import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import os

TOKEN = "8681324108:AAEnbCDZd3WfHmlyY-Zb-QH_1BvIAqC2wA0"
bot = telebot.TeleBot(TOKEN)

ADMIN_USERNAME = "@Ergashboyeva077" 
CHANNEL_LINK = "https://t.me/korea_kosmetika010"

# Botning profil ma'lumotlarini (Description va About) o'zgartirish
try:
    bot.set_my_description(
        description=f"✨ Go'zallik va Koreya kosmetikasi olamiga xush kelibsiz!\n\n"
                    f"🛍 Bizning rasmiy kanal: {CHANNEL_LINK}\n"
                    f"👩‍💻 Admin: {ADMIN_USERNAME}"
    )
    bot.set_my_short_description(
        short_description=f"Koreya kosmetikasi buyurtma berish boti 🌸\nKanal: {CHANNEL_LINK}"
    )
except Exception as e:
    print("Profilni yangilashda xatolik (bu muhim emas):", e)

# Mahsulotlar bazasi (Lokal rasmlar bilan)
products = {
    "face": [
        {
            "name": "🌟 VELIUM COLLAGEN NOURISHING CREAM", 
            "desc": "💧 <b>Oziqlantiruvchi krem</b>\n• Terini namlantiradi va yumshatadi\n• Teri elastikligi va parvarishiga yordam beradi\n• Quruq va namlikka muhtoj terilar uchun", 
            "price": "80 000 so'm",
            "image": "images/face_1.jpg"
        },
        {
            "name": "🌟 MEDIPEEL MELANON X Cream", 
            "desc": "✨ <b>Muammoli teri uchun yechim</b>\n• Dog'lar, husnbuzar izlari va qora nuqtalarga qarshi kurashuvchi\n• Terini oqartiradi va pigmentatsiyani yo'q qiladi", 
            "price": "160 000 so'm",
            "image": "images/face_2.jpg"
        },
        {
            "name": "🌟 ALII OK LOVEFIT CUSHION", 
            "desc": "🎀 <b>Mukammal Makiyaj</b>\n• Teri yuzdek silliq va tiniq ko'rinadi\n• Yuzdagi mayda nuqson va notekisliklarni chiroyli yopadi\n• Kundalik makiyaj uchun juda qulay", 
            "price": "100 000 so'm",
            "image": "images/face_3.jpg"
        },
        {
            "name": "🌟 Ricocell Glow Drop tonviy spf",
            "desc": "☀️ <b>Quyoshdan himoya va chiroy</b>\n• Yuzga yengil yotadi\n• Oqartiradi va quyoshdan kuchli himoya qiladi",
            "price": "140 000 so'm",
            "image": "images/face_4.jpg"
        }
    ],
    "eyes": [
        {
            "name": "🌟 Ricocell Premium Ko'z Kremi (Lacto Collagen)", 
            "desc": "👁 <b>Ko'z atrofi parvarishi</b>\n• Ajinlarni yoyadi, oqartiradi va chuqur namlaydi\n• 📦 <i>Hajmi:</i> 50ml + 50ml (2ta bo'ladi)", 
            "price": "140 000 so'm",
            "image": "images/eyes_1.jpg"
        }
    ],
    "hair": [
        {
            "name": "🌟 Fino soch maskalari", 
            "desc": "💆‍♀️ <b>Sog'lom sochlar siri</b>\n• Sochlar uchun maxsus va kuchli ta'sir etuvchi mukammal maska.", 
            "price": "160 000 so'm",
            "image": "images/hair_1.jpg"
        }
    ],
    "health": [
        {
            "name": "🌟 Healthy Place Liposomal Glutathione", 
            "desc": "💊 <b>Go'zallik va Quvvat</b>\n• Terini ichidan oqartirish va dog'larni ketkazish\n• Limon ta'mli kunlik quvvat va tetiklik beruvchi yoqimli stil-paketlar.", 
            "price": "190 000 so'm",
            "image": "images/health_1.jpg"
        },
        {
            "name": "🌟 Arencia trenddagi boosterlar", 
            "desc": "✨ <b>Terini tiklash va porlash</b>\n• Eng so'nggi trenddagi Arencia brendining yuz va tana uchun boosterlari.", 
            "price": "190 000 so'm",
            "image": "images/health_2.jpg"
        }
    ]
}

def main_menu():
    """Asosiy kategoriyalar menyusi"""
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("👩 Yuz parvarishi", callback_data="cat_face"),
        InlineKeyboardButton("👁 Ko'z atrofini parvarishlash", callback_data="cat_eyes"),
        InlineKeyboardButton("💆‍♀️ Soch parvarishi", callback_data="cat_hair"),
        InlineKeyboardButton("💊 Vitamin va Boosterlar", callback_data="cat_health")
    )
    # Kanalga o'tish tugmasi
    markup.add(InlineKeyboardButton("📢 Bizning rasmiy kanal", url=CHANNEL_LINK))
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    reply_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    reply_markup.add(
        KeyboardButton("🛍 Katalog (Menyu)"), 
        KeyboardButton("📢 Bizning kanal")
    )
    reply_markup.add(KeyboardButton("📞 Biz bilan aloqa"))
    
    welcome_text = (
        f"🌸 <b>Assalomu alaykum, {message.from_user.first_name}!</b>\n\n"
        "🎀 <i>Koreyaning eng sara, original va sifatli kosmetika olamiga xush kelibsiz!</i>\n\n"
        "╭━━━━━━━━━━━━━━━━━━━╮\n"
        "   Siz izlagan mukammallik \n"
        "   aynan shu yerda! ✨\n"
        "╰━━━━━━━━━━━━━━━━━━━╯\n\n"
        "👇 <b>Katalogni ko'rish uchun quyidagi bo'limlardan birini tanlang:</b>"
    )
    
    bot.send_message(message.chat.id, welcome_text, reply_markup=reply_markup, parse_mode='HTML')
    bot.send_message(message.chat.id, "🗂 <b>MAHSULOTLAR KATALOGI:</b>", reply_markup=main_menu(), parse_mode='HTML')

@bot.message_handler(func=lambda message: message.text in ["🛍 Katalog (Menyu)", "🛍 Asosiy menyu"])
def menu_btn(message):
    bot.send_message(message.chat.id, "🗂 <b>MAHSULOTLAR KATALOGI:</b>", reply_markup=main_menu(), parse_mode='HTML')

@bot.message_handler(func=lambda message: message.text == "📢 Bizning kanal")
def channel_btn(message):
    text = (
        "✨ <b>Bizning asosiy telegram kanalimiz!</b>\n\n"
        "U yerda yangi kelgan mahsulotlar, aksiyalar va mijozlarimizning fikrlari bilan tanishishingiz mumkin.\n\n"
        f"👉 <b>Kanalga o'tish:</b> {CHANNEL_LINK}"
    )
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Kanalga a'zo bo'lish ↗️", url=CHANNEL_LINK))
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode='HTML')

@bot.message_handler(func=lambda message: message.text == "📞 Biz bilan aloqa")
def contact_btn(message):
    text = (
        "📞 <b>Biz bilan aloqa markazi</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "Savollaringiz bormi yoki buyurtma bermoqchimisiz?\n"
        f"Buning uchun adminga murojaat qiling!\n\n"
        f"👩‍💻 <b>Admin profil:</b> {ADMIN_USERNAME}\n"
        f"📢 <b>Kanalimiz:</b> {CHANNEL_LINK}\n\n"
        "<i>Sizga xizmat ko'rsatishdan mamnunmiz! 💖</i>"
    )
    bot.send_message(message.chat.id, text, parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: call.data.startswith('cat_'))
def show_products(call):
    category = call.data.split('_')[1]
    
    if category not in products or not products[category]:
        bot.answer_callback_query(call.id, "Hozircha bu bo'limda mahsulotlar yo'q 😔", show_alert=True)
        return
    
    bot.answer_callback_query(call.id)
    
    cat_names = {
        "face": "👩 YUZ UCHUN KOSMETIKA",
        "eyes": "👁 KO'Z UCHUN KREMLAR",
        "hair": "💆‍♀️ SOCH PARVARISHI",
        "health": "💊 VITAMIN VA BOOSTERLAR"
    }
    
    bot.send_message(
        call.message.chat.id, 
        f"✨ <b>{cat_names[category]}</b> bo'limidagi mahsulotlar:\n━━━━━━━━━━━━━━━━━━", 
        parse_mode='HTML'
    )
    
    # Har bir mahsulotni haqiqiy lokal rasm bilan yuboramiz
    for prod in products[category]:
        text = (
            f"<b>{prod['name']}</b>\n\n"
            f"{prod['desc']}\n\n"
            f"🏷 <b>Narxi:</b> <u>{prod['price']}</u>"
        )
        
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("🛒 Buyurtma berish (Adminga yozish)", url=f"https://t.me/{ADMIN_USERNAME.replace('@', '')}"),
            InlineKeyboardButton("📢 Kanalda ko'rish", url=CHANNEL_LINK)
        )
        
        try:
            # Lokal rasmni ochib yuborish
            with open(prod['image'], 'rb') as photo:
                bot.send_photo(call.message.chat.id, photo, caption=text, reply_markup=markup, parse_mode='HTML')
        except Exception as e:
            # Rasm topilmasa yoki muammo bo'lsa
            bot.send_message(call.message.chat.id, text, reply_markup=markup, parse_mode='HTML')

import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import os

class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8000))
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, DummyHandler)
    httpd.serve_forever()

if __name__ == '__main__':
    print("Bot ishga tushdi... (To'xtatish uchun Ctrl+C bosing)")
    
    # Render platformasi uchun soxta veb-serverni alohida oqimda (thread) ishga tushirish
    threading.Thread(target=run_dummy_server, daemon=True).start()
    
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print("Xatolik yuz berdi:", e)
