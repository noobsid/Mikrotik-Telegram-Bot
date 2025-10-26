import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
from librouteros import connect

# =======================
# Konfigurasi
# =======================
BOT_TOKEN = "YOUR_BOT_TOKEN"

# Ubah sesuai permintaan: host dan port terpisah default port : 8729
MIKROTIK_IP = "IP"
MIKROTIK_PORT = PORT

MIKROTIK_USER = "USER"
MIKROTIK_PASS = "PASSWORD"

ALLOWED_CHAT_IDS = [ADMIN_ID]   # chat_id admin

profiles = {
    "2r": {"prefix": "2R", "profile": "2Rb-10Jam", "harga": "Rp2.000"},
    "3r": {"prefix": "3R", "profile": "3Rb-17Jam", "harga": "Rp3.000"},
    "4r": {"prefix": "4R", "profile": "4Rb-24Jam", "harga": "Rp4.000"},
    "8r": {"prefix": "8R", "profile": "8Rb-2Hari5Jam", "harga": "Rp8.000"},
    "7h": {"prefix": "7D", "profile": "7Hari-25Rb", "harga": "Rp25.000"},
    "1b": {"prefix": "30D", "profile": "1-BULAN", "harga": "Rp50.000"},
    "2b": {"prefix": "30D", "profile": "1Bulan-2Hp", "harga": "Rp80.000"},
    "3b": {"prefix": "30D", "profile": "1Bulan-3Hp", "harga": "Rp120.000"},
    "4b": {"prefix": "30D", "profile": "1Bulan-4HP-150", "harga": "Rp150.000"},
    "t1": {"prefix": "TE", "profile": "TEST", "harga": "Rp0"},
}

# =======================
# Utilitas
# =======================
SAFE_CHARS = "234679ACDEFGHJKMNPQTUVWXYZ"

def random_string(length=6):
    return ''.join(random.choice(SAFE_CHARS) for _ in range(length))

def is_authorized(chat_id):
    return chat_id in ALLOWED_CHAT_IDS

def make_voucher(code, jumlah):
    """Buat voucher di Mikrotik dan kembalikan teks hasilnya"""
    if code not in profiles:
        return ["❌ Kode tidak dikenal!"]

    prefix = profiles[code]["prefix"]
    profile = profiles[code]["profile"]

    # koneksi sekarang pakai host dan port terpisah
    try:
        api = connect(username=MIKROTIK_USER, password=MIKROTIK_PASS,
                      host=MIKROTIK_IP, port=MIKROTIK_PORT)
    except Exception as e:
        return [f"⚠️ Gagal koneksi ke Mikrotik {MIKROTIK_IP}:{MIKROTIK_PORT} — {e}"]

    users = api.path("ip", "hotspot", "user")

    vouchers = []
    for _ in range(int(jumlah)):
        uname = f"{prefix}{random_string(6)}"
        pwd = uname
        try:
            users.add(name=uname, password=pwd, profile=profile, comment="vc-Telegram")
            vouchers.append(
                f"✅ Kode Vocer:\n"
                f"🔐 {uname}\n"
                f"📦 {profile}\n"
                f"💰 {profiles[code]['harga']}\n"
            )
        except Exception as e:
            vouchers.append(f"⚠️ Gagal buat {uname}: {e}")

    # tutup koneksi kalau tersedia
    try:
        api.close()
    except Exception:
        pass

    return ["Berhasil ✅\n"] + vouchers


# =======================
# Menu Builder
# =======================
def main_menu():
    keyboard = [
        [InlineKeyboardButton("🎫 Generate", callback_data="menu_generate")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="menu_help")],
        [InlineKeyboardButton("📋 Profiles", callback_data="menu_profiles")]
    ]
    return InlineKeyboardMarkup(keyboard)


# =======================
# Handler Telegram
# =======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        await update.message.reply_text("❌ Anda tidak diizinkan.")
        return
    await update.message.reply_text("✅ Bot aktif!\n\nPilih menu:", reply_markup=main_menu())


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id

    if not is_authorized(chat_id):
        await query.edit_message_text("❌ Anda tidak diizinkan.")
        return

    data = query.data

    # Menu utama
    if data == "menu_generate":
        keyboard = [[InlineKeyboardButton(f"{d['profile']} ({k})", callback_data=f"profile_{k}")]
                    for k, d in profiles.items()]
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="back_main")])
        await query.edit_message_text("📋 Pilih Profile:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "menu_help":
        keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="back_main")]]
        await query.edit_message_text(
            "📌 Format manual:\n<kode> <jumlah>\n\nContoh:\n4r 2 → 2 voucher profile 4R",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "menu_profiles":
        text = "📋 Daftar Profile:\n"
        for kode, d in profiles.items():
            text += f"{kode} → {d['prefix']} / {d['profile']} ({d['harga']})\n"
        keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="back_main")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    # Submenu profile
    elif data.startswith("profile_"):
        kode = data.split("_")[1]
        keyboard = [[InlineKeyboardButton(str(i), callback_data=f"generate_{kode}_{i}")] for i in range(1, 5)]
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="menu_generate")])
        await query.edit_message_text(
            f"Berapa jumlah voucher untuk {profiles[kode]['profile']}?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # Generate voucher
    elif data.startswith("generate_"):
        _, kode, jumlah = data.split("_")
        vouchers = make_voucher(kode, jumlah)
        keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="menu_generate")]]
        await query.edit_message_text("\n".join(vouchers), reply_markup=InlineKeyboardMarkup(keyboard))

    # Back button
    elif data == "back_main":
        await query.edit_message_text("✅ Bot aktif!\n\nPilih menu:", reply_markup=main_menu())


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle input manual <kode> <jumlah>"""
    chat_id = update.effective_chat.id
    if not is_authorized(chat_id):
        await update.message.reply_text("❌ Anda tidak diizinkan.")
        return

    try:
        args = update.message.text.split()
        if len(args) != 2:
            await update.message.reply_text("Format: <kode> <jumlah>\nContoh: 4r 2")
            return

        code, jumlah = args
        vouchers = make_voucher(code, jumlah)
        await update.message.reply_text("\n".join(vouchers))

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {e}")


# =======================
# Main
# =======================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
