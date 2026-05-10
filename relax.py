import telebot # type: ignore
from datetime import datetime
import json
import urllib.parse
import requests # type: ignore
from time import sleep
from io import BytesIO
import base64
import re
import os

TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)
user_start_counts = {}
total_start_count = 0

print("Bot Hizmete Hazır.")

USER_DATA_FILE = ''

def load_user_ids():
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            print("JSON okuma hatası:", e)
            with open(USER_DATA_FILE, 'w') as file:
                json.dump([], file)
            return []
    return []

def save_user_ids(user_ids):
    try:
        with open(USER_DATA_FILE, 'w') as file:
            json.dump(user_ids, file)
    except Exception as e:
        print(f"Hata oluştu: {e}")

def save_user_data(user_id):
    user_ids = load_user_ids()
    if user_id not in user_ids:
        user_ids.append(user_id)
        save_user_ids(user_ids)

def is_user_member(user_id, chat_id):
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print(str(e))
        return False

def api_veri_cek(api_url):
    try:
        yanıt = requests.get(api_url)
        if yanıt.status_code == 200:
            return yanıt.json()
        else:
            return None
    except Exception as hata:
        print("API'den veri çekerken bir hata oluştu:", hata)
        return None

def send_message_to_all_users(message_text):
    users = load_user_ids()
    for user_id in users:
        try:
            bot.send_message(user_id, message_text)
        except Exception as e:
            print(f"Mesaj gönderilemedi {user_id}: {e}")    

ADMIN_ID = 8447839505

@bot.message_handler(commands=['sendall'])
def send_all_users(message):
    if message.from_user.id == ADMIN_ID:
        send_message_to_all_users("Ücretsiz Bot Aktiftir. \n\nPremium Bot Satın Almak İçin: @tahqxdrr")     

@bot.message_handler(commands=['iletisim'])
def iletisim(message):
    if message.chat.type != "private":
        return
    
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    bot.send_message(message.chat.id, f"👋 Merhaba {user_name}, ({user_id})!\n\n🌱 Gördüğüm Kadarıyla Bizle İletişime Geçmeye Çalışıyorsun.\n\n💭 Kodlayıcıma Ulaşmanın Tek Yolu Olan Telegram Adresini Senin İçin Bıraktım: @tahqxdrr")

@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.type != "private":
        return
    
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    save_user_data(user_id)   

    channel_id = -1003920046572
    group_id = -1003913878935

    if not is_user_member(user_id, channel_id) or not is_user_member(user_id, group_id):
        response = f"👋 Merhaba {user_name}, ({user_id})! \n\n〽️ Sorgular Ücretsiz Olduğu İçin Kanala Ve Gruba Katılmanız Zorunludur! Kanal Ve Gruba Katılıp Tekrar /start Yazınız."
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(
            telebot.types.InlineKeyboardButton("📢 Duyuru", url="https://t.me/relaxvipduyuru"),
        )    
        markup.add(
            telebot.types.InlineKeyboardButton("💭 Chat", url="https://t.me/relaxvipchat"),
        ) 
        bot.send_message(message.chat.id, response, reply_markup=markup)
        return

    if user_id not in user_start_counts:
        user_start_counts[user_id] = 0

    user_start_counts[user_id] += 1
    total_users = len(user_start_counts)

    response = f"🍀 Merhaba {user_name}, ({user_id})!\n\n📚 Sorgu Botuna Hoş Geldin. Bu Bot, Sistemlerde Bulunan Verileri Analiz Etmene Yardımcı Olur Ve Tamamen Ücretsizdir!\n\n📮 Bu Sorguların Genel Olarak Sizlere Hitap Etmek Amacıyla Hazırlandığını Rica Ediyoruzki Unutmayınız!\n\n📢 Geri Bildirimlerinizi Bekleriz: /iletisim"
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("📝 Komutlar", callback_data="commands"),
        telebot.types.InlineKeyboardButton("👤 Hakkımda", callback_data="hakkimda")
    )    
    markup.add(
        telebot.types.InlineKeyboardButton("📞 İletişim", callback_data="iletisim"),
        telebot.types.InlineKeyboardButton("🌐 Premium Üyelik", callback_data="satinal")
    )
    markup.add(
        telebot.types.InlineKeyboardButton("⚙ APİ Servisi", callback_data="api")
    )
    bot.send_message(message.chat.id, response, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "commands")
def commands(call):
    response = "👨🏼‍💻 Komutlar Menüsü:"
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("🔍 Ad Soyad Sorgu", callback_data="adsoyad"),
        telebot.types.InlineKeyboardButton("🔍 Ad Soyad Pro Sorgu", callback_data="adsoyad")
    )    
    markup.add(
        telebot.types.InlineKeyboardButton("👤 T.C Sorgu", callback_data="tc"),
        telebot.types.InlineKeyboardButton("👤 T.C Pro Sorgu", callback_data="tcpro")
    )
    markup.add(
        telebot.types.InlineKeyboardButton("👤 T.C Plus Sorgu", callback_data="tcplus"),
        telebot.types.InlineKeyboardButton("🆔 Seri No Sorgu", callback_data="serino")
    )
    markup.add(
        telebot.types.InlineKeyboardButton("📞 T.C-GSM Sorgu", callback_data="tcgsm"),
        telebot.types.InlineKeyboardButton("📞 GSM-T.C Sorgu", callback_data="gsmtc")
    )
    markup.add(
        telebot.types.InlineKeyboardButton("👪 Aile Sorgu", callback_data="aile"),
        telebot.types.InlineKeyboardButton("👨‍👨‍👧‍👧 Sülale Sorgu", callback_data="sulale")
    )
    markup.add(
        telebot.types.InlineKeyboardButton("➕👪 Aile Pro Sorgu", callback_data="ailepro"),
        telebot.types.InlineKeyboardButton("➕👨‍👨‍👧‍👧 Sülale Pro Sorgu", callback_data="sulalepro")
    )
    markup.add(
        telebot.types.InlineKeyboardButton("💼 Meslek Sorgu", callback_data="meslek"),
        telebot.types.InlineKeyboardButton("🏫 Üniversite Sorgu", callback_data="universite")
    )
    markup.add(
        telebot.types.InlineKeyboardButton("🏫 Okul No Sorgu", callback_data="okulno"),
        telebot.types.InlineKeyboardButton("🏫 Okul Geçmişi Sorgu", callback_data="okulgecmisi")
    )
    markup.add(
        telebot.types.InlineKeyboardButton("📷 E-Okul Vesika Sorgu", callback_data="vesika"),
        telebot.types.InlineKeyboardButton("📷 Ehliyet Vesika Sorgu", callback_data="ehliyet")
    )
    markup.add(
        telebot.types.InlineKeyboardButton("📊 Rapor Sorgu", callback_data="rapor"),
        telebot.types.InlineKeyboardButton("💊 İlaç Sorgu", callback_data="ilac")
    )
    markup.add(
        telebot.types.InlineKeyboardButton("💉 Aşı Sorgu", callback_data="asi"),
        telebot.types.InlineKeyboardButton("📅 Randevu Sorgu", callback_data="randevu")
    )
    markup.add(
        telebot.types.InlineKeyboardButton("🏥 Muayene Sorgu", callback_data="muayene"),
        telebot.types.InlineKeyboardButton("🏥 Röntgen Sorgu", callback_data="rontgen")
    )
    markup.add(
        telebot.types.InlineKeyboardButton("🏠 Adres Sorgu", callback_data="adres"),
        telebot.types.InlineKeyboardButton("🏡 Apartman Sorgu", callback_data="apartman")
    )
    markup.add(
        telebot.types.InlineKeyboardButton("🏠 Tapu Sorgu", callback_data="tapu"),
        telebot.types.InlineKeyboardButton("🏞 Ada Parsel Sorgu", callback_data="adaparsel")
    )
    markup.add(
        telebot.types.InlineKeyboardButton("🛣 Sokak Sorgu", callback_data="sokak"),
        telebot.types.InlineKeyboardButton("🏛 Vergi Dairesi Sorgu", callback_data="vergi")
    )
    markup.add(
        telebot.types.InlineKeyboardButton("🏠 Hane Sorgu", callback_data="hane"),
        telebot.types.InlineKeyboardButton("🏡 Sigorta Sorgu", callback_data="sigorta")
    )
    markup.add(
        telebot.types.InlineKeyboardButton("🚘 Plaka Sorgu", callback_data="plaka"),
        telebot.types.InlineKeyboardButton("🚘 Plaka Borç Sorgu", callback_data="plakaborc")
    )
    markup.add(
        telebot.types.InlineKeyboardButton("💼 İşyeri Sorgu", callback_data="isyeri"),
        telebot.types.InlineKeyboardButton("💼 İşyeri Arkadaşı Sorgu", callback_data="isyeriarkadasi")
    )
    markup.add(
        telebot.types.InlineKeyboardButton("🏢 Firma Sorgu", callback_data="firma"),
        telebot.types.InlineKeyboardButton("📔 Sicil Sorgu", callback_data="sicil")
    )
    markup.add(
        telebot.types.InlineKeyboardButton("🏦 İban Sorgu", callback_data="iban"),
        telebot.types.InlineKeyboardButton("👩🏻‍🦳 Kızlık Soyadı Sorgu", callback_data="kizlik")
    )
    markup.add(
        telebot.types.InlineKeyboardButton("📆 SKT Sorgu (Son Kullanım Tarihi)", callback_data="skt"),
        telebot.types.InlineKeyboardButton("🔒 Mahkum Sorgu", callback_data="mahkum")
    )
    markup.add(
        telebot.types.InlineKeyboardButton("💣 SMS Bomber", callback_data="smsbomber"),
        telebot.types.InlineKeyboardButton("📱 Arama Gönderme", callback_data="call")
    )
    markup.add(
        telebot.types.InlineKeyboardButton("♨ Satın Al", url="https://t.me/tanrican")
    )
    markup.add(
        telebot.types.InlineKeyboardButton("🔙 Geri", callback_data="back")
    )

    bot.edit_message_text(response, call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "back")
def back(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception as e:
        print(f"Mesaj silinirken hata oluştu: {e}")
    start(call.message)

@bot.callback_query_handler(func=lambda call: call.data == "satinal")
def satinal(call):
    response = f"❌ Premium Üyeliğiniz Bulunmamaktadır.\n\n💠 Üyelik Satın Almak İçin, Satın Al Butonuna Tıklayınız."
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("♨ Satın Al", url="https://t.me/tahqxdrr"),
        telebot.types.InlineKeyboardButton("🔙 Geri", callback_data="back")
    )
    bot.send_message(call.message.chat.id, response, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "iletisim")
def iletisim(call):
    user_id = call.from_user.id
    user_name = call.from_user.first_name

    response = f"🔻 Merhaba {user_name}, ({user_id})! Bu Botun Sahibine Ulaşmak, İçin Aşağıdaki Butondan İletişime Geçebilirsin!"

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("🔶 Kodlayıcım", url="https://t.me/tahqxdrr"),
        telebot.types.InlineKeyboardButton("🔙 Geri", callback_data="back")
    )
    bot.send_message(call.message.chat.id, response, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "api")
def satinal(call):
    response = f"✨ Çok Yakında Sizlerle..."
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("🔙 Geri", callback_data="back")
    )
    bot.send_message(call.message.chat.id, response, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "hakkimda")
def hakkimda(call):
    user_id = call.from_user.id
    user_name = call.from_user.first_name

    response = f"✨ Hakkımda Kısmına Hoşgeldin {user_name}, ({user_id})! \n\n❄ Amacım Beni Kullananlar İçin En İyi Sorguyu En Hızlı Şekilde Çıkarmaktır Ve Tamamen Ücretsizim. \n\n❤ Beni Kullandığın İçin Teşekkürler!"
    
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("📢 Duyuru Kanalım", url="https://t.me/relaxvipduyuru"),
        telebot.types.InlineKeyboardButton("🔙 Geri", callback_data="back")
    )
    bot.send_message(call.message.chat.id, response, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["adsoyad", "hane", "skt", "mahkum", "kizlik", "sokak", "asi", "serino", "sicil", "firma", "randevu", "isyeri", "isyeriarkadasi", "muayene", "okulno", "okulgecmisi", "meslek", "universite", "ehliyet", "tcpro", "tapu", "adres", "rontgen", "adaparsel", "evesika", "plaka", "call", "apartman", "vergi", "sulale", "plaka", "rapor", "tcpro", "sigorta", "ilac", "vesika", "sulalepro", "adres", "ailepro", "tc", "gsmtc", "tcgsm", "aile", "tcplus", "smsbomber", "iban", "plakaborc", "ip"])
def other_commands(call):
    if call.data == "adsoyad":
        response = "/sorgu • Ad Soyad'dan Kişinin Bilgilerini Verir."
    elif call.data == "tc":
        response = "/tckn • T.C.'den Kişinin Bilgilerini Verir."
    elif call.data == "tcpro":
        response = "/tcpro • T.C.'den Kişinin Detaylı Kimlik Bilgilerini Verir."
    elif call.data == "tcplus":
        response = "/tcplus • T.C.'den Kişinin En Detaylı Kimlik Bilgilerini Verir."     
    elif call.data == "hane":
        response = "/hane • T.C.'den Kişinin Aile Adres Bilgilerini Verir."
    elif call.data == "gsmtc":
        response = "/gsmtc • GSM'den T.C Verir."
    elif call.data == "skt":
        response = "/skt • T.C.'den Son Kullanım Tarihini Verir."
    elif call.data == "mahkum":
        response = "/mahkum • T.C.'den Mahkum Bilgisi Verir."
    elif call.data == "tcgsm":
        response = "/tcgsm • T.C.'den GSM Verir."
    elif call.data == "asi":
        response = "/asi • T.C.'den Kişinin Aşı Bilgilerini Verir."
    elif call.data == "kizlik":
        response = "/kizlik • T.C.'den Kişinin Kızlık Soyadını Verir."
    elif call.data == "okulno":
        response = "/okulno • T.C.'den Kişinin Okul NO'sunu Verir."
    elif call.data == "randevu":
        response = "/randevu • T.C.'den Kişinin Hastane Randevu Bilgilerini Verir."
    elif call.data == "okulgecmisi":
        response = "/okulgecmisi • T.C.'den Kişinin Okul Geçmişi Bilgilerini Verir."
    elif call.data == "meslek":
        response = "/meslek • T.C.'den Kişinin Meslek Bilgisini Verir."
    elif call.data == "muayene":
        response = "/muayene • T.C.'den Kişinin Muayene Bilgilerini Verir."
    elif call.data == "universite":
        response = "/universite • T.C.'den Kişinin Okuduğu Üniversiteyi Ve Mezun Bilgisini Verir."
    elif call.data == "tapu":
        response = "/tapu • T.C.'den Kişinin Tapu Bilgilerini Verir."
    elif call.data == "adaparsel":
        response = "/adaparsel • Ada Parselden Kişinin Kimlik Bilgisini Verir."
    elif call.data == "sokak":
        response = "/sokak • T.C.'den Kişinin Sokak Bilgisini Verir."
    elif call.data == "aile":   
        response = "/aile • T.C.'den Kişinin Aile Bilgilerini Verir"
    elif call.data == "iban":
        response = "/iban • Kişinin İbanından Kimlik Bilgilerini Verir."
    elif call.data == "ehliyet":
        response = "/evesika • T.C.'den Kişinin Ehliyet Vesikasını Verir."
    elif call.data == "rontgen":
        response = "/rontgen • Kişinin Röntgen Bilgilerini Verir."
    elif call.data == "firma":
        response = "/firma • T.C.'den Kişinin Firma Bilgisini Verir."
    elif call.data == "sicil":
        response = "/sicil • T.C.'den Kişinin Sicil Kaydını Verir."
    elif call.data == "plakaborc":
        response = "/plakaborc • Plakadan Kişinin Sahip Olduğu Borçları Verir."
    elif call.data == "plaka":
        response = "/plaka • Plakadan Kişinin Kimlik Bilgilerini Verir."
    elif call.data == "isyeri":
        response = "/isyeri • T.C.'den Kişinin İşyeri Bilgisini Verir."
    elif call.data == "isyeriarkadasi":
        response = "/isyeriarkadasi • T.C.'den Kişinin İşyeri Arkadaşları Bilgisini Verir."
    elif call.data == "smsbomber":
        response = "/smsbomber • GSM'den Kişiye SMS Saldırısı Gönderir."
    elif call.data == "call":
        response = "/call • GSM'den Kişiye Arama Saldırısı Gönderir."
    elif call.data == "apartman":
        response = "/apartman • T.C.'den Kişinin Apartman Bilgilerini Verir."
    elif call.data == "vergi":
        response = "/vergi • T.C.'den Kişinin Vergi NO'sunu Verir."
    elif call.data == "ailepro":
        response = "/ailepro • T.C.'den Kişinin Ailesinin Detaylı Bilgilerini Verir. "
    elif call.data == "sulale":
        response = "/sulale • T.C.'den Kişinin Sülalesinin Bilgilerini Verir."
    elif call.data == "adres":
        response = "/adres • T.C.'den Kişinin Adres Bilgilerini Verir."
    elif call.data == "sulalepro":
        response = "/sulalepro • T.C.'den Kişinin Sülalesinin Detaylı Bilgilerini Verir."
    elif call.data == "serino":
        response = "/serino • T.C.'den Kişinin Seri No'sunu Verir."
    elif call.data == "ilac":
        response = "/ilac • T.C.'den Kişinin İlaç Bilgilerini Verir."
    elif call.data == "vesika":
        response = "/vesika • T.C.'den Kişinin E-Okul Vesika Bilgilerini Verir."
    elif call.data == "rapor":
        response = "/rapor • T.C.'den Kişinin Rapor Bilgilerini Verir."
    elif call.data == "sigorta":
        response = "/sigorta • T.C.'den Kişinin Sigorta Bilgilerini Verir."

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("🔙 Geri", callback_data="commands")
    )
    bot.edit_message_text(response, call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.message_handler(commands=['vesika'])
def vesika_mesajı(message):
    response = f"❌ Premium Üyeliğiniz Bulunmamaktadır.\n\n💠 Üyelik Satın Almak İçin, Satın Al Butonuna Tıklayınız."
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("♨ Satın Al", url="https://t.me/tahqxdrr"),
    )
    markup.add(
        telebot.types.InlineKeyboardButton("🔙 Geri", callback_data="commands")
    )
    bot.send_message(message.chat.id, response, reply_markup=markup)

@bot.message_handler(commands=['mahkum'])
def vesika_mesajı(message):
    response = f"❌ Premium Üyeliğiniz Bulunmamaktadır.\n\n💠 Üyelik Satın Almak İçin, Satın Al Butonuna Tıklayınız."
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("♨ Satın Al", url="https://t.me/tahqxdrr"),
    )
    markup.add(
        telebot.types.InlineKeyboardButton("🔙 Geri", callback_data="commands")
    )
    bot.send_message(message.chat.id, response, reply_markup=markup)

@bot.message_handler(commands=['skt'])
def vesika_mesajı(message):
    response = f"❌ Premium Üyeliğiniz Bulunmamaktadır.\n\n💠 Üyelik Satın Almak İçin, Satın Al Butonuna Tıklayınız."
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("♨ Satın Al", url="https://t.me/tahqxdrr"),
    )
    markup.add(
        telebot.types.InlineKeyboardButton("🔙 Geri", callback_data="commands")
    )
    bot.send_message(message.chat.id, response, reply_markup=markup)

@bot.message_handler(commands=['plakaborc'])
def pborc(message):
    response = f"❌ Premium Üyeliğiniz Bulunmamaktadır.\n\n💠 Üyelik Satın Almak İçin, Satın Al Butonuna Tıklayınız."
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("♨ Satın Al", url="https://t.me/tahqxdrr"),
    )
    markup.add(
        telebot.types.InlineKeyboardButton("🔙 Geri", callback_data="commands")
    )
    bot.send_message(message.chat.id, response, reply_markup=markup)

@bot.message_handler(commands=["tckn"])
def tc_sorgula(message):
    if message.chat.type != "private":
        return

    user_id = message.from_user.id
    user_name = message.from_user.first_name
    username = message.from_user.username

    channel_id = -1003920046572
    group_id = -1003913878935

    if not is_user_member(user_id, channel_id) or not is_user_member(user_id, group_id):
        response = f"👋 Merhaba {user_name}, ({user_id})! \n\n〽️ Sorgular Ücretsiz Olduğu İçin Kanala Ve Gruba Katılmanız Zorunludur! Kanal Ve Gruba Katılıp Tekrar /start Yazınız."
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("📢 Duyuru", url="https://t.me/relaxvipduyuru"))
        markup.add(telebot.types.InlineKeyboardButton("💭 Chat", url="https://t.me/relaxvipchat"))
        bot.send_message(message.chat.id, response, reply_markup=markup)
        return 

    mesaj = message.text
    tc = mesaj.replace("/tckn", "").strip()

    if tc.isdigit() and len(tc) == 11:
        # Yeni API URL Yapısı
        api_url = f"https://ilah.cc/apiler/tc.php?tc={tc}"
        
        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                json_data = response.json()

                # Yeni API bir liste döndürüyor, listenin boş olup olmadığını kontrol ediyoruz
                if isinstance(json_data, list) and len(json_data) > 0:
                    user_data = json_data[0] # Listenin ilk elemanını al

                    # Yeni JSON anahtarlarına göre veri çekme
                    tc_no = user_data.get("TC", "")
                    adi = user_data.get("ADI", "")
                    soyadi = user_data.get("SOYADI", "")
                    dogum_tarihi_str = user_data.get("DOGUMTARIHI", "")
                    nufus_il = user_data.get("NUFUSIL", "")
                    nufus_ilce = user_data.get("NUFUSILCE", "")
                    anne_adi = user_data.get("ANNEADI", "")
                    anne_tc = user_data.get("ANNETC", "")
                    baba_adi = user_data.get("BABAADI", "")
                    baba_tc = user_data.get("BABATC", "")
                    uyruk = user_data.get("UYRUK") or "TR"

                    # Yaş Hesaplama
                    try:
                        # API'den gelen tarih formatı 16.3.1998 gibi (tek haneli gün/ay gelebilir)
                        dogum_tarihi = datetime.strptime(dogum_tarihi_str, "%d.%m.%Y")
                        simdiki_tarih = datetime.now()
                        yas = simdiki_tarih.year - dogum_tarihi.year - ((simdiki_tarih.month, simdiki_tarih.day) < (dogum_tarihi.month, dogum_tarihi.day))
                    except:
                        yas = "Bilinmiyor"

                    cevap = f"""
╭━━━━━━━━━━━━━━━╮
┃➥ + Sorgu Başarılı
╰━━━━━━━━━━━━━━━╯
╭━━━━━━━━━━━━━━━╮
┃➥ TC: {tc_no}
┃➥ ADI: {adi}
┃➥ SOYADI: {soyadi}
┃➥ DOĞUM TARİHİ: {dogum_tarihi_str}
┃➥ NUFUS IL: {nufus_il}
┃➥ NUFUS ILCE: {nufus_ilce}
┃➥ ANNE ADI: {anne_adi}
┃➥ ANNE TC: {anne_tc}
┃➥ BABA ADI: {baba_adi}
┃➥ BABA TC: {baba_tc}
┃➥ UYRUK: {uyruk}
┃➥ YAŞ: {yas}
╰━━━━━━━━━━━━━━━╯
"""
                else:
                    cevap = "Aranan TC'ye ait bilgi bulunamadı."
            else:
                cevap = f"API Hatası: {response.status_code}"
        except Exception as e:
            cevap = f"Bir hata oluştu: {str(e)}"
    else:
        cevap = "Lütfen geçerli bir 11 haneli T.C. Kimlik Numarası girin!\nÖrnek: /tckn 11111111110"

    bot.send_message(message.chat.id, f"```{cevap}```", parse_mode='Markdown')

    log_message = f"Yeni TC Sorgu Atıldı!\n\n" \
                  f"Sorgulanan TC: {tc}\n" \
                  f"Sorgulayan ID: {user_id}\n" \
                  f"Sorgulayan Adı: {user_name}\n" \
                  f"Sorgulayan K. Adı: @{username}"
    bot.send_message(-1003997096434, log_message)

@bot.message_handler(commands=["tcpro"])
def tc_sorgula(message):
    if message.chat.type != "private":
        return

    user_id = message.from_user.id
    user_name = message.from_user.first_name
    username = message.from_user.username

    channel_id = -1003920046572
    group_id = -1003913878935

    if not is_user_member(user_id, channel_id) or not is_user_member(user_id, group_id):
        response = f"👋 Merhaba {user_name}, ({user_id})! \n\n〽️ Sorgular Ücretsiz Olduğu İçin Kanala Ve Gruba Katılmanız Zorunludur! Kanal Ve Gruba Katılıp Tekrar /start Yazınız."
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(
            telebot.types.InlineKeyboardButton("📢 Duyuru", url="https://t.me/relaxvipduyuru"),
        )    
        markup.add(
            telebot.types.InlineKeyboardButton("💭 Chat", url="https://t.me/relaxvipchat"),
        ) 
        bot.send_message(message.chat.id, response, reply_markup=markup)
        return
    
    mesaj = message.text or ""

    if mesaj.startswith("/tcpro"):
        tc = mesaj.replace("/tcpro", "").strip()

        if tc.isdigit() and len(tc) == 11:
            api_url = f"https://nexusapiservice.xyz/servis/tckn/apiv2?hash=nNzPDg3s943Nba23h&auth=connell&tc={tc}"
            response = requests.get(api_url)

            if response.status_code == 200:           
                try:
                    json_data = response.json()

                    if json_data.get("Veri"):
                        user_data = json_data["Veri"]

                        tc = user_data.get("TCKN", "")
                        adi = user_data.get("Adi", "")
                        soyadi = user_data.get("Soyadi", "")
                        cinsiyet = user_data.get("Cinsiyet", "")
                        dogum_tarihi_str = user_data.get("DogumTarihi", "")
                        olumtarihi = user_data.get("OlumTarihi", "") or "YOK"
                        dogum_yeri = user_data.get("DogumYeri", "")
                        medeni_hal = user_data.get("MedeniHal", "")
                        anne_adi = user_data.get("AnneAdi", "")
                        anne_tc = user_data.get("AnneTCKN", "")
                        baba_tc = user_data.get("BabaTCKN", "")
                        baba_adi = user_data.get("BabaAdi", "")
                        il = user_data.get("AdresIl", "")
                        mahalle = user_data.get("AdresIlce", "")
                        memleket_il = user_data.get("MemleketIl", "")
                        memleket_ilce = user_data.get("MemleketIlce", "")
                        memleket_koy = user_data.get("MemleketKoy", "")
                        ailesirano = user_data.get("AileSiraNo", "")
                        sirano = user_data.get("BireySiraNo", "")
                        vergino = user_data.get("VergiNumarasi", "")
                        adres_2023 = user_data.get("2023Adres", "")
                        adres_2015 = user_data.get("2015Adres", "")
                        gsm = user_data.get("GSM", [])
                        gsm_no = gsm[0][0] if gsm else "YOK"

                        try:
                            dogum_tarihi = datetime.strptime(dogum_tarihi_str, "%d.%m.%Y")
                            simdiki_tarih = datetime.now()
                            yas = simdiki_tarih.year - dogum_tarihi.year - ((simdiki_tarih.month, simdiki_tarih.day) < (dogum_tarihi.month, dogum_tarihi.day))
                        except ValueError:
                            yas = "Bilinmiyor"

                        cevap = f"""
╭━━━━━━━━━━━━━━━╮
┃➥ + Sorgu Başarılı
╰━━━━━━━━━━━━━━━╯
╭━━━━━━━━━━━━━━━╮
┃➥ TC: {tc}
┃➥ ADI: {adi}
┃➥ SOYADI: {soyadi}
┃➥ CİNSİYET: {cinsiyet}
┃➥ DOĞUM TARİHİ: {dogum_tarihi_str}
┃➥ ÖLÜM TARİHİ: {olumtarihi}
┃➥ DOĞUM YERİ: {dogum_yeri}
┃➥ MEDENİ HAL: {medeni_hal}
┃➥ ANNE ADI: {anne_adi}
┃➥ ANNE TC: {anne_tc}
┃➥ BABA ADI: {baba_adi}
┃➥ BABA TC: {baba_tc}
┃➥ İL: {il}
┃➥ İLÇE: {mahalle}
┃➥ MEMLEKET İL: {memleket_il}
┃➥ MEMLEKET İLÇE: {memleket_ilce}
┃➥ MEMLEKET KÖY: {memleket_koy}
┃➥ AİLE SIRA NO: {ailesirano}
┃➥ BİREY SIRA NO: {sirano}
┃➥ 2023 ADRESİ: {adres_2023}
┃➥ 2015 ADRESİ: {adres_2015}
┃➥ Vergi NO: {vergino}
┃➥ GSM NO: {gsm_no}
┃➥ YAŞ: {yas}
╰━━━━━━━━━━━━━━━╯
"""
                    else:
                        cevap = "Aranan TC'ye ait bilgi bulunamadı."
                except ValueError:
                    cevap = "API'den alınan yanıt çözümlenemedi."
            else:
                cevap = f"API Hata Kodu ({response.status_code}): {response.text}"
        else:
            cevap = "\nLütfen geçerli bir T.C. Kimlik Numarası girin!\nÖrnek: /tcpro 11111111110"
    else:
        cevap = "\nLütfen geçerli bir T.C. Kimlik Numarası girin!\nÖrnek: /tcpro 11111111110"

    bot.send_message(message.chat.id, f"```{cevap}```", parse_mode='Markdown')

    log_message = f"Yeni TC Pro Sorgu Atıldı!\n\n" \
                  f"Sorgulanan TC: {tc}\n" \
                  f"Sorgulayan ID: {user_id}\n" \
                  f"Sorgulayan Adı: {user_name}\n" \
                  f"Sorgulayan K. Adı: @{username}"
    bot.send_message(-4781401242, log_message)

@bot.message_handler(commands=["adres"])
def adres(message):
    if message.chat.type != "private":
        return

    user_id = message.from_user.id
    user_name = message.from_user.first_name
    username = message.from_user.username

    channel_id = -1003920046572
    group_id = -1003913878935

    if not is_user_member(user_id, channel_id) or not is_user_member(user_id, group_id):
        response = f"👋 Merhaba {user_name}, ({user_id})! \n\n〽️ Sorgular Ücretsiz Olduğu İçin Kanala Ve Gruba Katılmanız Zorunludur! Kanal Ve Gruba Katılıp Tekrar /start Yazınız."
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(
            telebot.types.InlineKeyboardButton("📢 Duyuru", url="https://t.me/relaxvipduyuru"),
        )    
        markup.add(
            telebot.types.InlineKeyboardButton("💭 Chat", url="https://t.me/relaxvipchat"),
        ) 
        bot.send_message(message.chat.id, response, reply_markup=markup)
        return

    mesaj = message.text
    if mesaj.startswith("/adres"):
        tc = mesaj.replace("/adres", "").strip()
        if tc.isdigit() and len(tc) == 11:
            api_url = f"https://nexusapiservice.xyz/servis/adres/apiv3?hash=ZXG4LxPpSf0aHXXZY&auth=connel&tc={tc}"
            response = requests.get(api_url)

            if response.status_code == 200:
                try:
                    json_data = response.json()
                except json.decoder.JSONDecodeError as e:
                    print(f"JSON Decode Hatası: {e}")
                    print(f"API Yanıtı: {response.text}")
                    cevap = "API Yanıtı Beklenen Formatta Değil."
                    bot.send_message(message.chat.id, cevap)
                    return

                if "Veri" in json_data and json_data["Veri"]:
                    person = json_data["Veri"]
                    adi = person["Adres"]
               
                    ad = person["AdiSoyadi"]
                    vergino = person["VKN"]

                    cevap = f"""
╭━━━━━━━━━━━━━━━╮
┃➥ + Sorgu Başarılı
╰━━━━━━━━━━━━━━━╯
╭━━━━━━━━━━━━━━━╮
┃➥ TC: {tc}
┃➥ Ad Soyad: {ad}
┃➥ Vergi No: {vergino}
┃➥ Adres: {adi}
╰━━━━━━━━━━━━━━━╯
"""
                else:
                    cevap = "Aranan TC'ye ait bilgi bulunamadı."
            else:
                cevap = f"Api Hata Kodu ({response.status_code}): {response.text}"
        else:
            cevap = "\nLütfen geçerli bir T.C. Kimlik Numarası girin!\nÖrnek: /adres 11111111110"
    else:
        cevap = "\nLütfen geçerli bir T.C. Kimlik Numarası girin!\nÖrnek: /adres 11111111110"

    bot.send_message(message.chat.id, f"```{cevap}```", parse_mode='Markdown')

    log_message = f"Yeni Adres Sorgu Atıldı!\n\n" \
                  f"Sorgulanan Kişi: {tc}\n" \
                  f"Sorgulayan ID: {user_id}\n" \
                  f"Sorgulayan Adı: {user_name}\n" \
                  f"Sorgulayan K. Adı: @{username}"
    bot.send_message(-4781401242, log_message)

@bot.message_handler(commands=["hane"])
def hane(message):
    if message.chat.type != "private":
        return

    user_id = message.from_user.id
    user_name = message.from_user.first_name
    username = message.from_user.username

    channel_id = -1003920046572
    group_id = -1003913878935

    if not is_user_member(user_id, channel_id) or not is_user_member(user_id, group_id):
        response = f"👋 Merhaba {user_name}, ({user_id})! \n\n〽️ Sorgular Ücretsiz Olduğu İçin Kanala Ve Gruba Katılmanız Zorunludur! Kanal Ve Gruba Katılıp Tekrar /start Yazınız."
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(
            telebot.types.InlineKeyboardButton("📢 Duyuru", url="https://t.me/relaxvipduyuru"),
        )    
        markup.add(
            telebot.types.InlineKeyboardButton("💭 Chat", url="https://t.me/relaxvipchat"),
        ) 
        bot.send_message(message.chat.id, response, reply_markup=markup)
        return

    mesaj = message.text
    if mesaj.startswith("/hane"):
        tc = mesaj.replace("/hane", "").strip()
        if tc.isdigit() and len(tc) == 11:
            api_url = f"https://nexusapiservice.xyz/servis/hane/api?hash=EMByPtwRmX16XzxXz&auth=connel&tc={tc}"
            response = requests.get(api_url)

            if response.status_code == 200:
                try:
                    json_data = response.json()
                except json.decoder.JSONDecodeError as e:
                    print(f"JSON Decode Hatası: {e}")
                    print(f"API Yanıtı: {response.text}")
                    cevap = "API Yanıtı Beklenen Formatta Değil."
                    bot.send_message(message.chat.id, cevap)
                    return

                if "Veri" in json_data and json_data["Veri"]:
                    person_list = json_data["Veri"]

                    cevap = "\n\n╭━━━━━━━━━━━━━╮\n"
                    for person in person_list:
                        tcc = person["KimlikNumarasi"]
                        adi = person["Ikametgah"]
                        ad = person["AdiSoyadi"]
                        vergino = person["VergiNumarasi"]

                        cevap += f"┃➥ TC: {tcc}\n"
                        cevap += f"┃➥ Ad: {ad}\n"
                        cevap += f"┃➥ Vergi No: {vergino}\n"
                        cevap += f"┃➥ Adres: {adi}\n"
                        cevap += "╰━━━━━━━━━━━━━━╯\n"

                    cevap = cevap.rstrip("\n")
                else:
                    cevap = "Aranan TC'ye ait bilgi bulunamadı."
            else:
                cevap = f"Api Hata Kodu ({response.status_code}): {response.text}"
        else:
            cevap = "\nLütfen geçerli bir T.C. Kimlik Numarası girin!\nÖrnek: /hane 11111111110"
    else:
        cevap = "\nLütfen geçerli bir T.C. Kimlik Numarası girin!\nÖrnek: /hane 11111111110"

    bot.send_message(message.chat.id, f"```{cevap}```", parse_mode='Markdown')

    log_message = f"Yeni Hane Sorgu Atıldı!\n\n" \
                  f"Sorgulanan Kişi: {tc}\n" \
                  f"Sorgulayan ID: {user_id}\n" \
                  f"Sorgulayan Adı: {user_name}\n" \
                  f"Sorgulayan K. Adı: @{username}"
    bot.send_message(-4781401242, log_message)

@bot.message_handler(commands=["sigorta"])
def sigorta(message):
    response = f"❌ Premium Üyeliğiniz Bulunmamaktadır.\n\n💠 Üyelik Satın Almak İçin, Satın Al Butonuna Tıklayınız."
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("♨ Satın Al", url="https://t.me/tahqxdrr"),
    )
    markup.add(
        telebot.types.InlineKeyboardButton("🔙 Geri", callback_data="commands")
    )
    bot.send_message(message.chat.id, response, reply_markup=markup)

@bot.message_handler(commands=["sorgu"])
def handle_sorgu_command(message):
    if message.chat.type != "private":
        return

    user_id = message.from_user.id
    user_name = message.from_user.first_name
    username = message.from_user.username

    channel_id = -1003920046572
    group_id = -1003913878935

    if not is_user_member(user_id, channel_id) or not is_user_member(user_id, group_id):
        response = f"👋 Merhaba {user_name}, ({user_id})! \n\n〽️ Sorgular Ücretsiz Olduğu İçin Kanala Ve Gruba Katılmanız Zorunludur! Kanal Ve Gruba Katılıp Tekrar /start Yazınız."
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("📢 Duyuru", url="https://t.me/relaxvipduyuru"))
        markup.add(telebot.types.InlineKeyboardButton("💭 Chat", url="https://t.me/relaxvipchat"))
        bot.send_message(message.chat.id, response, reply_markup=markup)
        return

    isim = None
    isim2 = None
    soyisim = None
    il = None
    ilce = None

    words = message.text.split()

    for i in range(len(words)):
        if words[i] == "-isim" and i < len(words) - 1:
            isim = words[i + 1]
        elif words[i] == "-isim2" and i < len(words) - 1:
            isim2 = words[i + 1]
        elif words[i] == "-soyisim" and i < len(words) - 1:
            soyisim = words[i + 1]
        elif words[i] == "-il" and i < len(words) - 1:
            il = words[i + 1]
        elif words[i] == "-ilce" and i < len(words) - 1:
            ilce = words[i + 1]

    if not isim or not soyisim:
        bot.reply_to(message, "```\nYanlış Kullanım!\n\nÖrnek: /sorgu -isim Mert -isim2 Can -soyisim Ak -il İstanbul -ilce Güngören```", parse_mode="Markdown")
        return

    tam_ad = f"{isim} {isim2}" if isim2 else isim
    api_url = f"https://ilah.cc/apiler/adsoyad.php?ad={urllib.parse.quote(tam_ad)}&soyad={urllib.parse.quote(soyisim)}"

    if il:
        api_url += f"&il={urllib.parse.quote(il)}"
    if ilce:
        api_url += f"&ilce={urllib.parse.quote(ilce)}"

    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            
            if data.get("success") == "true" and data.get("data"):
                mesajlar = []
                for person in data["data"]:
                    tc = person.get("TC", "Bulunamadı")
                    adi = person.get("ADI", "Bulunamadı")
                    soyadi = person.get("SOYADI", "Bulunamadı")
                    dogumtarihi = person.get("DOGUMTARIHI", "Bulunamadı")
                    nufusil = person.get("NUFUSIL", "Bulunamadı")
                    nufusilce = person.get("NUFUSILCE", "Bulunamadı")
                    anneadi = person.get("ANNEADI", "Bulunamadı")
                    annetc = person.get("ANNETC", "Bulunamadı")
                    babaadi = person.get("BABAADI", "Bulunamadı")
                    babatc = person.get("BABATC", "Bulunamadı")
                    uyruk = person.get("UYRUK", "TR")

                    info = f"""
╭━━━━━━━━━━━━━━━╮
┃➥ TC: {tc}
┃➥ ADI: {adi}
┃➥ SOY ADI: {soyadi}
┃➥ DOĞUM TARİHİ: {dogumtarihi}
┃➥ İL: {nufusil}
┃➥ İLÇE: {nufusilce}
┃➥ ANNE ADI: {anneadi}
┃➥ ANNE TC: {annetc}
┃➥ BABA ADI: {babaadi}
┃➥ BABA TC: {babatc}
┃➥ UYRUK: {uyruk}
╰━━━━━━━━━━━━━━━╯
"""
                    mesajlar.append(info)

                # Dosya işlemleri
                with open("sorgu_mesajlari.txt", "w", encoding="utf-8") as file:
                    for mesaj in mesajlar:
                        file.write(mesaj + "\n\n")

                with open("sorgu_mesajlari.txt", "rb") as file:
                    bot.send_document(message.chat.id, file)

                # Log
                log_message = (f"Yeni Ad Soyad Sorgu!\n"
                               f"Ad: {tam_ad}\nSoyad: {soyisim}\n"
                               f"Sorgulayan: {user_name} ({user_id})")
                bot.send_message(-1003997096434, log_message)
            else:
                bot.reply_to(message, "❌ Sonuç Bulunamadı.")
        else:
            bot.reply_to(message, f"❌ API Hatası: {response.status_code}")

    except json.JSONDecodeError as e:
        bot.reply_to(message, f"⚠️ JSON Hatası: {e}")

@bot.message_handler(commands=["aile"])
def aile_sorgula(message):
    if message.chat.type != "private":
        return

    user_id = message.from_user.id
    user_name = message.from_user.first_name
    username = message.from_user.username

    channel_id = -1003920046572
    group_id = -1003913878935

    if not is_user_member(user_id, channel_id) or not is_user_member(user_id, group_id):
        response = f"👋 Merhaba {user_name}, ({user_id})! \n\n〽️ Sorgular Ücretsiz Olduğu İçin Kanala Ve Gruba Katılmanız Zorunludur! Kanal Ve Gruba Katılıp Tekrar /start Yazınız."
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(
            telebot.types.InlineKeyboardButton("📢 Duyuru", url="https://t.me/relaxvipduyuru"),
        )    
        markup.add(
            telebot.types.InlineKeyboardButton("💭 Chat", url="https://t.me/relaxvipchat"),
        ) 
        bot.send_message(message.chat.id, response, reply_markup=markup)
        return

    mesaj = message.text

    if mesaj.startswith("/aile"):
        tc = mesaj.replace("/aile", "").strip()

        if tc.isdigit() and len(tc) == 11:
            api_url = f"https://nexusapiservice.xyz/servis/aile/api?hash=4SxndsECSsruv5E7b&auth=connel&tc={tc}"
            response = requests.get(api_url)

            if response.status_code == 200:
                json_data = response.json()

                if json_data and json_data.get("Info").get("Status") == "OK" and json_data.get("Veri"):
                    mesajlar = []
                    for person in json_data["Veri"]:
                        tc = person.get("TCKN", "")
                        adi = person.get("Adi", "")
                        soyadi = person.get("Soyadi", "")
                        dogumtarihi = person.get("DogumTarihi", "")
                        nufusil = person.get("NufusIl", "")
                        nufusilce = person.get("NufusIlce", "")
                        anneadi = person.get("AnneAdi", "")
                        annetc = person.get("AnneTCKN", "")
                        babaadi = person.get("BabaAdi", "")
                        babatc = person.get("BabaTCKN", "")
                        uyruk = person.get("Uyruk", "")
                        yakınlık = person.get("Yakinlik", "-")
                      

                        info = f"""
╭━━━━━━━━━━━━━━━╮
┃➥ TC: {tc}
┃➥ ADI: {adi}
┃➥ SOYADI: {soyadi}
┃➥ DOĞUM TARİHİ: {dogumtarihi}
┃➥ İL: {nufusil}
┃➥ İLÇE: {nufusilce}
┃➥ ANNE ADI: {anneadi}
┃➥ ANNE TC: {annetc}
┃➥ BABA ADI: {babaadi}
┃➥ BABA TC: {babatc}
┃➥ UYRUK: {uyruk}
┃➥ YAKINLIK: {yakınlık}
╰━━━━━━━━━━━━━━━╯
"""
                        mesajlar.append(info)

                    with open("aile_sorgu_mesajlari.txt", "w", encoding="utf-8") as file:
                        for mesaj in mesajlar:
                            file.write(mesaj + "\n\n")

                    with open("aile_sorgu_mesajlari.txt", "rb") as file:
                        bot.send_document(message.chat.id, file)

                    log_message = f"Yeni Aile Sorgu Atıldı!\n\n" \
                                  f"Sorgulanan TC: {tc}\n" \
                                  f"Sorgulayan ID: {user_id}\n" \
                                  f"Sorgulayan Adı: {user_name}\n" \
                                  f"Sorgulayan K. Adı: @{username}"
                    bot.send_message(-4781401242, log_message)

                else:
                    bot.reply_to(message, "Veri Bulunamadı.")
            else:
                bot.reply_to(message, f"Api Hata Kodu ({response.status_code}): {response.text}")
        else:
            bot.reply_to(message, '```\nLütfen geçerli bir T.C. Kimlik Numarası girin!\nÖrnek: /aile 11111111110```', parse_mode="Markdown")
    else:
        bot.reply_to(message, '```\nLütfen geçerli bir T.C. Kimlik Numarası girin!\nÖrnek: /aile 11111111110```', parse_mode="Markdown")

@bot.message_handler(commands=["muayene"])
def muayene(message):
    response = f"❌ Premium Üyeliğiniz Bulunmamaktadır.\n\n💠 Üyelik Satın Almak İçin, Satın Al Butonuna Tıklayınız."
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("♨ Satın Al", url="https://t.me/tahqxdrr"),
    )
    markup.add(
        telebot.types.InlineKeyboardButton("🔙 Geri", callback_data="commands")
    )
    bot.send_message(message.chat.id, response, reply_markup=markup)

@bot.message_handler(commands=["sulalepro"])
def sulalegsm(message):
    if message.chat.type != "private":
        return

    user_id = message.from_user.id
    user_name = message.from_user.first_name
    username = message.from_user.username

    channel_id = -1003920046572
    group_id = -1003913878935

    if not is_user_member(user_id, channel_id) or not is_user_member(user_id, group_id):
        response = f"👋 Merhaba {user_name}, ({user_id})! \n\n〽️ Sorgular Ücretsiz Olduğu İçin Kanala Ve Gruba Katılmanız Zorunludur! Kanal Ve Gruba Katılıp Tekrar /start Yazınız."
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(
            telebot.types.InlineKeyboardButton("📢 Duyuru", url="https://t.me/relaxvipduyuru"),
        )    
        markup.add(
            telebot.types.InlineKeyboardButton("💭 Chat", url="https://t.me/relaxvipchat"),
        ) 
        bot.send_message(message.chat.id, response, reply_markup=markup)
        return

    mesaj = message.text

    if mesaj.startswith("/sulalepro"):
        tc = mesaj.replace("/sulalepro", "").strip()

        if tc.isdigit() and len(tc) == 11:
            api_url = f"http://localhost:5000/sulalepro?tc={tc}"
            response = requests.get(api_url)
            print(response.text)

            if response.status_code == 200:
                json_data = response.json()

                if json_data["Veri"]:
                    mesajlar = []
                    for person in json_data["Veri"]:

                        tc = person.get("TCKN", "")
                        adi = person.get("Adi", "")
                        soyadi = person.get("Soyadi", "")
                        dogum_tarihi = person.get("DogumTarihi", "")
                        anne_adi = person.get("AnneAdi", "")
                        anne_tc = person.get("AnneTCKN", "")
                        baba_adi = person.get("BabaAdi", "")
                        baba_tc = person.get("BabaTCKN", "")
                        nufusil = person.get("NufusIl", "")
                        nufusilce = person.get("NufusIlce", "")
                        adres_2023 = person.get("2023Adres", "")
                        uyruk = person.get("Uyruk", "") or "Bilinmiyor"
                        yakinlik = person.get("Yakinlik", "-")
                        gsm = person.get("GSM", [])
                        gsm_no = gsm[0][0] if gsm else "YOK"

                        info = f"""
╭━━━━━━━━━━━━━━━╮
┃➥ TC: {tc}
┃➥ ADI: {adi}
┃➥ SOYADI: {soyadi}
┃➥ DOĞUM TARİHİ: {dogum_tarihi}
┃➥ İL: {nufusil}
┃➥ İLÇE: {nufusilce}
┃➥ ANNE ADI: {anne_adi}
┃➥ ANNE TC: {anne_tc}
┃➥ BABA ADI: {baba_adi}
┃➥ BABA TC: {baba_tc}
┃➥ ADRES: {adres_2023}
┃➥ GSM: {gsm_no}
┃➥ UYRUK: {uyruk}
┃➥ YAKINLIK: {yakinlik}
╰━━━━━━━━━━━━━━━╯
"""
                        mesajlar.append(info)

                    with open("sulalepro_sorgu_mesajlari.txt", "w", encoding="utf-8") as file:
                        for mesaj in mesajlar:
                            file.write(mesaj + "\n\n")

                    with open("sulalepro_sorgu_mesajlari.txt", "rb") as file:
                        bot.send_document(message.chat.id, file)

                    log_message = f"Yeni Sülale Pro Sorgu Atıldı!\n\n" \
                                  f"Sorgulanan TC: {tc}\n" \
                                  f"Sorgulayan ID: {user_id}\n" \
                                  f"Sorgulayan Adı: {user_name}\n" \
                                  f"Sorgulayan K. Adı: @{username}"
                    bot.send_message(-4781401242, log_message)
                else:
                    bot.reply_to(message, "Veri Bulunamadı.")
            else:
                bot.reply_to(message, f"Api Hata Kodu ({response.status_code}): {response.text}")
        else:
            bot.reply_to(message, '```\nLütfen geçerli bir T.C. Kimlik Numarası girin!\nÖrnek: /sulalepro 11111111110```', parse_mode="Markdown")
    else:
        bot.reply_to(message, '```\nLütfen geçerli bir T.C. Kimlik Numarası girin!\nÖrnek: /sulalepro 11111111110```', parse_mode="Markdown")

@bot.message_handler(commands=["tcplus"])
def sulalegsm(message):
    response = f"❌ Premium Üyeliğiniz Bulunmamaktadır.\n\n💠 Üyelik Satın Almak İçin, Satın Al Butonuna Tıklayınız."
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("♨ Satın Al", url="https://t.me/tahqxdrr"),
    )
    markup.add(
        telebot.types.InlineKeyboardButton("🔙 Geri", callback_data="commands")
    )
    bot.send_message(message.chat.id, response, reply_markup=markup)

@bot.message_handler(commands=["ailepro"])
def sulalegsm(message):
    if message.chat.type != "private":
        return

    user_id = message.from_user.id
    user_name = message.from_user.first_name
    username = message.from_user.username

    channel_id = -1003920046572
    group_id = -1003913878935

    if not is_user_member(user_id, channel_id) or not is_user_member(user_id, group_id):
        response = f"👋 Merhaba {user_name}, ({user_id})! \n\n〽️ Sorgular Ücretsiz Olduğu İçin Kanala Ve Gruba Katılmanız Zorunludur! Kanal Ve Gruba Katılıp Tekrar /start Yazınız."
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(
            telebot.types.InlineKeyboardButton("📢 Duyuru", url="https://t.me/relaxvipduyuru"),
        )    
        markup.add(
            telebot.types.InlineKeyboardButton("💭 Chat", url="https://t.me/relaxvipchat"),
        ) 
        bot.send_message(message.chat.id, response, reply_markup=markup)
        return

    mesaj = message.text

    if mesaj.startswith("/ailepro"):
        tc = mesaj.replace("/ailepro", "").strip()

        if tc.isdigit() and len(tc) == 11:
            api_url = f"http://localhost:7000/apro?tc={tc}"
            response = requests.get(api_url)
            print(response.text)

            if response.status_code == 200:
                json_data = response.json()

                if json_data["Veri"]:
                    mesajlar = []
                    for person in json_data["Veri"]:

                        tc = person.get("TCKN", "")
                        adi = person.get("Adi", "")
                        soyadi = person.get("Soyadi", "")
                        dogum_tarihi = person.get("DogumTarihi", "")
                        anne_adi = person.get("AnneAdi", "")
                        anne_tc = person.get("AnneTCKN", "")
                        baba_adi = person.get("BabaAdi", "")
                        baba_tc = person.get("BabaTCKN", "")
                        nufusil = person.get("NufusIl", "")
                        nufusilce = person.get("NufusIlce", "")
                        adres_2023 = person.get("2023Adres", "")
                        uyruk = person.get("Uyruk", "") or "Bilinmiyor"
                        yakinlik = person.get("Yakinlik", "-")
                        gsm = person.get("GSM", [])
                        gsm_no = gsm[0][0] if gsm else "YOK"

                        info = f"""
╭━━━━━━━━━━━━━━━╮
┃➥ TC: {tc}
┃➥ ADI: {adi}
┃➥ SOYADI: {soyadi}
┃➥ DOĞUM TARİHİ: {dogum_tarihi}
┃➥ İL: {nufusil}
┃➥ İLÇE: {nufusilce}
┃➥ ANNE ADI: {anne_adi}
┃➥ ANNE TC: {anne_tc}
┃➥ BABA ADI: {baba_adi}
┃➥ BABA TC: {baba_tc}
┃➥ ADRES: {adres_2023}
┃➥ GSM: {gsm_no}
┃➥ UYRUK: {uyruk}
┃➥ YAKINLIK: {yakinlik}
╰━━━━━━━━━━━━━━╯
"""
                        mesajlar.append(info)

                    with open("ailepro_sorgu_mesajlari.txt", "w", encoding="utf-8") as file:
                        for mesaj in mesajlar:
                            file.write(mesaj + "\n\n")

                    with open("ailepro_sorgu_mesajlari.txt", "rb") as file:
                        bot.send_document(message.chat.id, file)

                    log_message = f"Yeni Aile Pro Sorgu Atıldı!\n\n" \
                                  f"Sorgulanan TC: {tc}\n" \
                                  f"Sorgulayan ID: {user_id}\n" \
                                  f"Sorgulayan Adı: {user_name}\n" \
                                  f"Sorgulayan K. Adı: @{username}"
                    bot.send_message(-4781401242, log_message)
                else:
                    bot.reply_to(message, "Veri Bulunamadı.")
            else:
                bot.reply_to(message, f"Api Hata Kodu ({response.status_code}): {response.text}")
        else:
            bot.reply_to(message, '```\nLütfen geçerli bir T.C. Kimlik Numarası girin!\nÖrnek: /ailepro 11111111110```', parse_mode="Markdown")
    else:
        bot.reply_to(message, '```\nLütfen geçerli bir T.C. Kimlik Numarası girin!\nÖrnek: /ailepro 11111111110```', parse_mode="Markdown")

@bot.message_handler(commands=["meslek"])
def ailegsm_sorgula(message):
    response = f"❌ Premium Üyeliğiniz Bulunmamaktadır.\n\n💠 Üyelik Satın Almak İçin, Satın Al Butonuna Tıklayınız."
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("♨ Satın Al", url="https://t.me/tahqxdrr"),
    )
    markup.add(
        telebot.types.InlineKeyboardButton("🔙 Geri", callback_data="commands")
    )
    bot.send_message(message.chat.id, response, reply_markup=markup)

@bot.message_handler(commands=["plaka"])
def ailegsm_sorgula(message):
    response = f"❌ Premium Üyeliğiniz Bulunmamaktadır.\n\n💠 Üyelik Satın Almak İçin, Satın Al Butonuna Tıklayınız."
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("♨ Satın Al", url="https://t.me/tahqxdrr"),
    )
    markup.add(
        telebot.types.InlineKeyboardButton("🔙 Geri", callback_data="commands")
    )
    bot.send_message(message.chat.id, response, reply_markup=markup)

@bot.message_handler(commands=["sokak"])
def ailegsm_sorgula(message):
    response = f"❌ Premium Üyeliğiniz Bulunmamaktadır.\n\n💠 Üyelik Satın Almak İçin, Satın Al Butonuna Tıklayınız."
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("♨ Satın Al", url="https://t.me/tahqxdrr"),
    )
    markup.add(
        telebot.types.InlineKeyboardButton("🔙 Geri", callback_data="commands")
    )
    bot.send_message(message.chat.id, response, reply_markup=markup)
    
@bot.message_handler(commands=["tapu"])
def ailegsm_sorgula(message):
    response = f"❌ Premium Üyeliğiniz Bulunmamaktadır.\n\n💠 Üyelik Satın Almak İçin, Satın Al Butonuna Tıklayınız."
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("♨ Satın Al", url="https://t.me/tahqxdrr"),
    )
    markup.add(
        telebot.types.InlineKeyboardButton("🔙 Geri", callback_data="commands")
    )
    bot.send_message(message.chat.id, response, reply_markup=markup)

@bot.message_handler(commands=["adaparsel"])
def ailegsm_sorgula(message):
    response = f"❌ Premium Üyeliğiniz Bulunmamaktadır.\n\n💠 Üyelik Satın Almak İçin, Satın Al Butonuna Tıklayınız."
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("♨ Satın Al", url="https://t.me/tahqxdrr"),
    )
    markup.add(
        telebot.types.InlineKeyboardButton("🔙 Geri", callback_data="commands")
    )
    bot.send_message(message.chat.id, response, reply_markup=markup)

@bot.message_handler(commands=["universite"])
def ailegsm_sorgula(message):
    response = f"❌ Premium Üyeliğiniz Bulunmamaktadır.\n\n💠 Üyelik Satın Almak İçin, Satın Al Butonuna Tıklayınız."
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("♨ Satın Al", url="https://t.me/tahqxdrr"),
    )
    markup.add(
        telebot.types.InlineKeyboardButton("🔙 Geri", callback_data="commands")
    )
    bot.send_message(message.chat.id, response, reply_markup=markup)

@bot.message_handler(commands=["rontgen"])
def ailegsm_sorgula(message):
    response = f"❌ Premium Üyeliğiniz Bulunmamaktadır.\n\n💠 Üyelik Satın Almak İçin, Satın Al Butonuna Tıklayınız."
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("♨ Satın Al", url="https://t.me/tahqxdrr"),
    )
    markup.add(
        telebot.types.InlineKeyboardButton("🔙 Geri", callback_data="commands")
    )
    bot.send_message(message.chat.id, response, reply_markup=markup)

@bot.message_handler(commands=["apartman"])
def ailegsm_sorgula(message):
    response = f"❌ Premium Üyeliğiniz Bulunmamaktadır.\n\n💠 Üyelik Satın Almak İçin, Satın Al Butonuna Tıklayınız."
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("♨ Satın Al", url="https://t.me/tahqxdrr"),
    )
    markup.add(
        telebot.types.InlineKeyboardButton("🔙 Geri", callback_data="commands")
    )
    bot.send_message(message.chat.id, response, reply_markup=markup)

@bot.message_handler(commands=["asi"])
def ailegsm_sorgula(message):
    response = f"❌ Premium Üyeliğiniz Bulunmamaktadır.\n\n💠 Üyelik Satın Almak İçin, Satın Al Butonuna Tıklayınız."
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("♨ Satın Al", url="https://t.me/tahqxdrr"),
    )
    markup.add(
        telebot.types.InlineKeyboardButton("🔙 Geri", callback_data="commands")
    )
    bot.send_message(message.chat.id, response, reply_markup=markup)

@bot.message_handler(commands=["randevu"])
def ailegsm_sorgula(message):
    response = f"❌ Premium Üyeliğiniz Bulunmamaktadır.\n\n💠 Üyelik Satın Almak İçin, Satın Al Butonuna Tıklayınız."
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("♨ Satın Al", url="https://t.me/tahqxdrr"),
    )
    markup.add(
        telebot.types.InlineKeyboardButton("🔙 Geri", callback_data="commands")
    )
    bot.send_message(message.chat.id, response, reply_markup=markup)

@bot.message_handler(commands=["okulno"])
def ailegsm_sorgula(message):
    response = f"❌ Premium Üyeliğiniz Bulunmamaktadır.\n\n💠 Üyelik Satın Almak İçin, Satın Al Butonuna Tıklayınız."
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("♨ Satın Al", url="https://t.me/tahqxdrr"),
    )
    markup.add(
        telebot.types.InlineKeyboardButton("🔙 Geri", callback_data="commands")
    )
    bot.send_message(message.chat.id, response, reply_markup=markup)

@bot.message_handler(commands=["okulgecmisi"])
def ailegsm_sorgula(message):
    response = f"❌ Premium Üyeliğiniz Bulunmamaktadır.\n\n💠 Üyelik Satın Almak İçin, Satın Al Butonuna Tıklayınız."
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("♨ Satın Al", url="https://t.me/tahqxdrr"),
    )
    markup.add(
        telebot.types.InlineKeyboardButton("🔙 Geri", callback_data="commands")
    )
    bot.send_message(message.chat.id, response, reply_markup=markup)

@bot.message_handler(commands=["evesika"])
def ailegsm_sorgula(message):
    response = f"❌ Premium Üyeliğiniz Bulunmamaktadır.\n\n💠 Üyelik Satın Almak İçin, Satın Al Butonuna Tıklayınız."
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("♨ Satın Al", url="https://t.me/tahqxdrr"),
    )
    markup.add(
        telebot.types.InlineKeyboardButton("🔙 Geri", callback_data="commands")
    )
    bot.send_message(message.chat.id, response, reply_markup=markup)

@bot.message_handler(commands=["sicil"])
def ailegsm_sorgula(message):
    response = f"❌ Premium Üyeliğiniz Bulunmamaktadır.\n\n💠 Üyelik Satın Almak İçin, Satın Al Butonuna Tıklayınız."
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("♨ Satın Al", url="https://t.me/tahqxdrr")
    )
    markup.add(
        telebot.types.InlineKeyboardButton("🔙 Geri", callback_data="commands")
    )
    bot.send_message(message.chat.id, response, reply_markup=markup)

@bot.message_handler(commands=["smsbomber"])
def ailegsm_sorgula(message):
    response = f"❌ Premium Üyeliğiniz Bulunmamaktadır.\n\n💠 Üyelik Satın Almak İçin, Satın Al Butonuna Tıklayınız."
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("♨ Satın Al", url="https://t.me/tahqxdrr")
    )
    markup.add(
        telebot.types.InlineKeyboardButton("🔙 Geri", callback_data="commands")
    )
    bot.send_message(message.chat.id, response, reply_markup=markup)

@bot.message_handler(commands=["call"])
def ailegsm_sorgula(message):
    response = f"❌ Premium Üyeliğiniz Bulunmamaktadır.\n\n💠 Üyelik Satın Almak İçin, Satın Al Butonuna Tıklayınız."
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("♨ Satın Al", url="https://t.me/tahqxdrr")
    )
    markup.add(
        telebot.types.InlineKeyboardButton("🔙 Geri", callback_data="commands")
    )
    bot.send_message(message.chat.id, response, reply_markup=markup)

@bot.message_handler(commands=["firma"])
def ailegsm_sorgula(message):
    response = f"❌ Premium Üyeliğiniz Bulunmamaktadır.\n\n💠 Üyelik Satın Almak İçin, Satın Al Butonuna Tıklayınız."
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("♨ Satın Al", url="https://t.me/tahqxdrr"),
    )
    markup.add(
        telebot.types.InlineKeyboardButton("🔙 Geri", callback_data="commands")
    )
    bot.send_message(message.chat.id, response, reply_markup=markup)

@bot.message_handler(commands=["isyeri"])
def ailegsm_sorgula(message):
    response = f"❌ Premium Üyeliğiniz Bulunmamaktadır.\n\n💠 Üyelik Satın Almak İçin, Satın Al Butonuna Tıklayınız."
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("♨ Satın Al", url="https://t.me/tahqxdrr"),
    )
    markup.add(
        telebot.types.InlineKeyboardButton("🔙 Geri", callback_data="commands")
    )
    bot.send_message(message.chat.id, response, reply_markup=markup)

@bot.message_handler(commands=["isyeriarkadasi"])
def ailegsm_sorgula(message):
    response = f"❌ Premium Üyeliğiniz Bulunmamaktadır.\n\n💠 Üyelik Satın Almak İçin, Satın Al Butonuna Tıklayınız."
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("♨ Satın Al", url="https://t.me/tahqxdrr"),
    )
    markup.add(
        telebot.types.InlineKeyboardButton("🔙 Geri", callback_data="commands")
    )
    bot.send_message(message.chat.id, response, reply_markup=markup)

@bot.message_handler(commands=["evsesika"])
def ailegsm_sorgula(message):
    response = f"❌ Premium Üyeliğiniz Bulunmamaktadır.\n\n💠 Üyelik Satın Almak İçin, Satın Al Butonuna Tıklayınız."
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("♨ Satın Al", url="https://t.me/tahqxdrr"),
    )
    markup.add(
        telebot.types.InlineKeyboardButton("🔙 Geri", callback_data="commands")
    )
    bot.send_message(message.chat.id, response, reply_markup=markup)

@bot.message_handler(commands=["sulale"])
def sulale_sorgula(message):
    if message.chat.type != "private":
        return

    user_id = message.from_user.id
    user_name = message.from_user.first_name
    username = message.from_user.username

    channel_id = -1003920046572
    group_id = -1003913878935

    # Üyelik Kontrolü
    if not is_user_member(user_id, channel_id) or not is_user_member(user_id, group_id):
        response = f"👋 Merhaba {user_name}, ({user_id})! \n\n〽️ Sorgular Ücretsiz Olduğu İçin Kanala Ve Gruba Katılmanız Zorunludur! Kanal Ve Gruba Katılıp Tekrar /start Yazınız."
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("📢 Duyuru", url="https://t.me/relaxvipduyuru"))
        markup.add(telebot.types.InlineKeyboardButton("💭 Chat", url="https://t.me/relaxvipchat"))
        bot.send_message(message.chat.id, response, reply_markup=markup)
        return

    mesaj = message.text

    if mesaj.startswith("/sulale"):
        tc = mesaj.replace("/sulale", "").strip()

        if tc.isdigit() and len(tc) == 11:
            # API URL
            api_url = f"https://arastir.vip/api/sulale.php?tc={tc}"
            
            try:
                response = requests.get(api_url)
                
                if response.status_code == 200:
                    json_data = response.json()

                    if json_data and json_data.get("success") == "true" and json_data.get("data"):
                        mesajlar = []
                        for person in json_data["data"]:
                            tc_no = person.get("TC", "")
                            adi = person.get("ADI", "")
                            soyadi = person.get("SOYADI", "")
                            dogumtarihi = person.get("DOGUMTARIHI", "")
                            nufusil = person.get("NUFUSIL", "")
                            nufusilce = person.get("NUFUSILCE", "")
                            anneadi = person.get("ANNEADI", "")
                            annetc = person.get("ANNETC", "")
                            babaadi = person.get("BABAADI", "")
                            babatc = person.get("BABATC", "")
                            uyruk = person.get("UYRUK", "Belirtilmemiş")
                            yakinlik = person.get("YAKINLIK", "-")

                            info = f"""
╭━━━━━━━━━━━━━━━╮
┃➥ TC: {tc_no}
┃➥ ADI: {adi}
┃➥ SOYADI: {soyadi}
┃➥ DOĞUM TARİHİ: {dogumtarihi}
┃➥ İL: {nufusil}
┃➥ İLÇE: {nufusilce}
┃➥ ANNE ADI: {anneadi}
┃➥ ANNE TC: {annetc}
┃➥ BABA ADI: {babaadi}
┃➥ BABA TC: {babatc}
┃➥ UYRUK: {uyruk}
┃➥ YAKINLIK: {yakinlik}
╰━━━━━━━━━━━━━━━╯
"""
                            mesajlar.append(info)

                        filename = f"sulale_{tc}.txt"
                        with open(filename, "w", encoding="utf-8") as file:
                            for m in mesajlar:
                                file.write(m + "\n\n")

                        with open(filename, "rb") as file:
                            bot.send_document(message.chat.id, file, caption=f"✅ {tc} Sülale Bilgileri Çıkarıldı.")

                        # Loglama
                        log_channel = -1003997096434
                        log_message = f"Yeni Sülale Sorgu Atıldı!\n\nSorgulanan TC: {tc}\nSorgulayan ID: {user_id}\nSorgulayan Adı: {user_name}"
                        bot.send_message(log_channel, log_message)
                    else:
                        bot.reply_to(message, "⚠️ Aranan T.C. numarasına ait sülale verisi bulunamadı.")
                else:
                    bot.reply_to(message, f"❌ Api Hatası ({response.status_code})")
            
            except Exception as e:
                bot.reply_to(message, "⚠️ Sorgulama sırasında teknik bir sorun oluştu.")
        else:
            # Hatalı olan kısım burasıydı, düzeltildi:
            bot.reply_to(message, '```\nLütfen geçerli bir T.C. Kimlik Numarası girin!\nÖrnek: /sulale 11111111110\n```', parse_mode="Markdown")

@bot.message_handler(commands=["rapor"])
def raporsalolaylar(message):
    response = f"❌ Premium Üyeliğiniz Bulunmamaktadır.\n\n💠 Üyelik Satın Almak İçin, Satın Al Butonuna Tıklayınız."
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("♨ Satın Al", url="https://t.me/tahqxdrr"),
    )
    markup.add(
        telebot.types.InlineKeyboardButton("🔙 Geri", callback_data="commands")
    )
    bot.send_message(message.chat.id, response, reply_markup=markup)

@bot.message_handler(commands=["ilac"])
def ilac(message):
    response = f"❌ Premium Üyeliğiniz Bulunmamaktadır.\n\n💠 Üyelik Satın Almak İçin, Satın Al Butonuna Tıklayınız."
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("♨ Satın Al", url="https://t.me/tahqxdrr"),
    )
    markup.add(
        telebot.types.InlineKeyboardButton("🔙 Geri", callback_data="commands")
    )
    bot.send_message(message.chat.id, response, reply_markup=markup)
        
@bot.message_handler(commands=['gsmtc'])
def gsm(message):
    if message.chat.type != "private":
        return

    user_id = message.from_user.id
    user_name = message.from_user.first_name
    username = message.from_user.username

    channel_id = -1003920046572
    group_id = -1003913878935

    if not is_user_member(user_id, channel_id) or not is_user_member(user_id, group_id):
        response = f"👋 Merhaba {user_name}, ({user_id})! \n\n〽️ Sorgular Ücretsiz Olduğu İçin Kanala Ve Gruba Katılmanız Zorunludur!"
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("📢 Duyuru", url="https://t.me/relaxvipduyuru"))
        markup.add(telebot.types.InlineKeyboardButton("💭 Chat", url="https://t.me/relaxvipchat"))
        bot.send_message(message.chat.id, response, reply_markup=markup)
        return

    args = message.text.split()
    gsm_num = args[1] if len(args) > 1 else None

    if not gsm_num or not re.match(r'^\d{10}$', gsm_num) or not gsm_num.startswith('5'):
        bot.reply_to(message, '```\nLütfen geçerli bir GSM numarası girin!\nÖrnek: /gsmtc 5553723339\n```', parse_mode="Markdown")
        return

    try:
        api_url = f"https://arastir.vip/api/gsmtc.php?gsm={gsm_num}"
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if isinstance(data.get("data"), list) and len(data["data"]) > 0:
            entry = data["data"][0]
            tc_no = entry.get('TC', 'Bulunamadı')
            gsm_no = entry.get('GSM', 'Bulunamadı')

            # Hata veren kısım burasıydı. Üç tırnak kullanarak hatayı imkansız hale getirdik:
            result_text = f"""```
╭━━━━━━━━━━━━━━╮
┃➥ +  Sorgu Başarılı
╰━━━━━━━━━━━━━━╯
╭─━━━━━━━━━━━━─╮
┃➥ T.C: {tc_no}
┃➥ GSM: {gsm_no}
╰─━━━━━━━━━━━━━─╯
```"""

            bot.reply_to(message, result_text, parse_mode="Markdown")

            log_message = f"Yeni GSMTC Sorgu!\n\nNumara: {gsm_num}\nID: {user_id}\nAd: {user_name}"
            bot.send_message(-1003997096434, log_message)
            
        else:
            bot.reply_to(message, '⚠️ *Girdiğiniz Bilgiler ile Eşleşen Biri Bulunamadı!*', parse_mode="Markdown")

    except Exception as e:
        bot.reply_to(message, f'⚠️ Hata oluştu: {str(e)}')

@bot.message_handler(commands=['tcgsm'])
def tcgsm(message):
    if message.chat.type != "private":
        return

    user_id = message.from_user.id
    user_name = message.from_user.first_name
    username = message.from_user.username

    channel_id = -1003920046572
    group_id = -1003913878935

    # Kanal Kontrol
    if not is_user_member(user_id, channel_id) or not is_user_member(user_id, group_id):
        response = f"Merhaba {user_name}! Sorgu icin kanala katilmalisiniz."
        bot.send_message(message.chat.id, response)
        return

    # Veri Alma
    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit() or len(args[1]) != 11:
        bot.reply_to(message, "Lutfen 11 haneli TC girin. Ornek: /tcgsm 11111111110")
        return

    tc = args[1]

    try:
        api_url = f"https://arastir.vip/api/tcgsm.php?tc={tc}"
        response = requests.get(api_url, timeout=10)
        data = response.json()
        
        if data and "data" in data and len(data["data"]) > 0:
            # Hata ihtimalini sifira indirmek icin duz metin yapisi
            sonuc = f"TCGSM Sorgu Basarili\n\nTC: {tc}\n"
            
            for index, item in enumerate(data["data"], 1):
                gsm_no = item.get('GSM', 'Bulunamadi')
                sonuc += f"GSM {index}: {gsm_no}\n"
            
            bot.reply_to(message, f"```\n{sonuc}\n
```", parse_mode="Markdown")

            # Log
            log_msg = f"TCGSM Sorgu: {tc} | ID: {user_id}"
            bot.send_message(-1003997096434, log_msg)
            
        else:
            bot.reply_to(message, "Veri bulunamadi.")
            
    except Exception as e:
        bot.reply_to(message, "Sistem hatasi.")

@bot.message_handler(commands=["ilac"])
def ilac(message):
    response = f"❌ Premium Üyeliğiniz Bulunmamaktadır.\n\n💠 Üyelik Satın Almak İçin, Satın Al Butonuna Tıklayınız."
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("♨ Satın Al", url="https://t.me/tahqxdrr"),
    )
    markup.add(
        telebot.types.InlineKeyboardButton("🔙 Geri", callback_data="commands")
    )
    bot.send_message(message.chat.id, response, reply_markup=markup)

@bot.message_handler(commands=["serino"])
def ilac(message):
    response = f"❌ Premium Üyeliğiniz Bulunmamaktadır.\n\n💠 Üyelik Satın Almak İçin, Satın Al Butonuna Tıklayınız."
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("♨ Satın Al", url="https://t.me/tahqxdrr"),
    )
    markup.add(
        telebot.types.InlineKeyboardButton("🔙 Geri", callback_data="commands")
    )
    bot.send_message(message.chat.id, response, reply_markup=markup)

@bot.message_handler(commands=["iban"])
def ilac(message):
    response = f"❌ Premium Üyeliğiniz Bulunmamaktadır.\n\n💠 Üyelik Satın Almak İçin, Satın Al Butonuna Tıklayınız."
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("♨ Satın Al", url="https://t.me/tahqxdrr"),
    )
    markup.add(
        telebot.types.InlineKeyboardButton("🔙 Geri", callback_data="commands")
    )
    bot.send_message(message.chat.id, response, reply_markup=markup)

bot.infinity_polling(allowed_updates=["message", "callback_query"])
