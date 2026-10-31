# Chach-Chu — O'zbekcha ovozli AI agent 🤖

**Chach-Chu** — bu siz bilan **o'zbek tilida** gaplashadigan, qurilmangizni **sizning ruxsatingiz bilan** boshqaradigan va topshiriqlarni bajaradigan shaxsiy AI yordamchi. Claude (Anthropic) modeli asosida ishlaydi.

## U nima qila oladi

- 🎙️ **Ovozli muloqot** — siz gapirasiz, u o'zbekcha eshitadi va o'zbekcha ovozda javob qaytaradi (ovoz moduli ixtiyoriy).
- 💬 **Matnli rejim** — mikrofon bo'lmasa, oddiy klaviatura orqali ham ishlaydi.
- 🖥️ **Qurilmani boshqarish** — dastur ochish, havola ochish, buyruq bajarish (har bir xavfli amal **ruxsat so'raydi**).
- 🌐 **Internetdan qidirish** — real vaqt ma'lumotlarini topadi.
- 📣 **Ijtimoiy tarmoqlar** — Telegram orqali xabar/post yuboradi (rasmiy Bot API orqali).
- 📱 **iPhone bilan bog'lanish** — Apple Shortcuts orqali telefoningizdan buyruq yuborish (ixtiyoriy "bridge" rejimi).

> **Muhim:** Chach-Chu hech qanday amalni yashirincha bajarmaydi. Dastur ochish, buyruq ishga tushirish yoki ijtimoiy tarmoqqa post qilishdan oldin har doim sizdan **tasdiq so'raydi**.

---

## ⚡ Tez boshlash (avtomatik)

**Kompyuter (Linux / macOS):**

```bash
bash setup.sh          # kutubxonalar + .env + config.json
# .env ni ochib ANTHROPIC_API_KEY ni qo'ying
./run.sh               # ishga tushadi
```

**Android (Termux):** pastdagi "Android" bo'limiga qarang.

---

## O'rnatish (qo'lda)

### 1. Python (3.9+) kerak

```bash
python3 --version
```

### 2. Loyihani yuklab oling va asosiy kutubxonalarni o'rnating

```bash
pip install -r requirements.txt
```

### 3. Anthropic API kalitini sozlang

[console.anthropic.com](https://console.anthropic.com) dan API kalit oling, so'ng:

```bash
cp .env.example .env
# .env faylini ochib ANTHROPIC_API_KEY ni qo'ying
```

### 4. Konfiguratsiyani sozlang

```bash
cp config.example.json config.json
# config.json ni o'zingizga moslang (Telegram tokeni, ruxsatlar va h.k.)
```

---

## Ishga tushirish

### Matnli rejim (eng oddiy, hamma joyda ishlaydi)

```bash
python -m chachchu
```

### Ovozli rejim

Avval ovoz kutubxonalarini o'rnating:

```bash
pip install -r requirements-voice.txt
```

Keyin `config.json` da `"voice": { "enabled": true }` qiling va:

```bash
python -m chachchu --voice
```

### iPhone / Shortcuts bilan bog'lash (bridge rejimi)

```bash
python -m chachchu --bridge
```

So'ng iPhone'da **Shortcuts** ilovasida yangi buyruq yaratib, kompyuteringiz IP manziliga
`POST http://<kompyuter-ip>:8787/ask` so'rov yuboring (tafsilotlar pastda).

---

## Ruxsatlar (xavfsizlik)

`config.json` dagi `permissions` bo'limi kim nimaga ruxsat berilganini belgilaydi:

- `auto_allow` — tasdiqsiz bajariladigan **xavfsiz** amallar (masalan, qidiruv, vaqtni bilish).
- `always_confirm` — har safar **sizdan so'raladigan** amallar (dastur ochish, buyruq, post yuborish).

Agar `--yes` bayrog'i bilan ishga tushirsangiz ham, `always_confirm` ro'yxatidagi amallar baribir so'raladi — bu ataylab shunday qilingan.

---

## Telegramni ulash

1. Telegram'da [@BotFather](https://t.me/BotFather) ga `/newbot` yuborib bot yarating.
2. Olingan tokenni `config.json` dagi `telegram.bot_token` ga qo'ying.
3. Botingizga bir marta xabar yozing, so'ng `telegram.default_chat_id` ni to'ldiring
   (chat id ni bilish uchun: `python -m chachchu.tools.social --whoami`).

Endi Chach-Chu ga "Telegramga 'Salom' deb yoz" desangiz, u yuboradi (tasdig'ingiz bilan).

> **Boshqa ijtimoiy tarmoqlar (Instagram, X, va h.k.):** ularni faqat **rasmiy API** orqali
> qo'shish tavsiya etiladi. Norasmiy avtomatlashtirish akkauntingiz bloklanishiga olib keladi.
> `chachchu/tools/social.py` da yangi platforma qo'shish uchun tayyor interfeys bor.

---

## 📱 Android'da ishlatish (Termux)

Chach-Chu Android telefonda **Termux** orqali to'g'ridan-to'g'ri ishlaydi — ovozli ham.

### 1. Ilovalarni o'rnating (F-Droid'dan)

- **Termux**: https://f-droid.org/packages/com.termux/
- **Termux:API**: https://f-droid.org/packages/com.termux.api/  ← ovoz uchun shart

> Play Store'dagi Termux eski — **F-Droid** versiyasini ishlating.

### 2. Loyihani oling va o'rnating

Termux ichida:

```bash
pkg install git -y
git clone <loyiha-havolasi> uy-ishlari
cd uy-ishlari
bash setup-termux.sh
```

### 3. API kalitni qo'ying

```bash
nano .env      # ANTHROPIC_API_KEY=sk-ant-... ni yozing
```

### 4. Ishga tushiring

```bash
python -m chachchu            # matnli rejim
python -m chachchu --voice    # ovozli (termux-api orqali o'zbekcha)
```

**Ovoz qanday ishlaydi (Android):**
- Eshitish — `termux-speech-to-text` (qurilmangiz Google nutq tanish tizimi; o'zbekcha
  til qurilma sozlamalarida yoqilgan bo'lsa yaxshi ishlaydi).
- Gapirish — `termux-tts-speak -l uz` (qurilmaning TTS dvigateli). Agar o'zbekcha ovoz
  bo'lmasa, dastur avtomatik gTTS'ga o'tadi.

> **Eslatma:** Android'da `open_app`/`run_shell` kabi tizim buyruqlari Termux doirasida
> ishlaydi (butun telefonni emas). Telefon funksiyalari uchun `termux-api` buyruqlarini
> (masalan `termux-sms-send`, `termux-battery-status`) `run_shell` orqali chaqirtirsangiz
> bo'ladi — lekin har biri ruxsat so'raydi.

### Telefonni doim yoqiq tutish (ixtiyoriy)

```bash
termux-wake-lock       # uyqu rejimida ham ishlab tursin
```

---

## iPhone (Apple Shortcuts) bilan integratsiya

iOS uchinchi tomon ilovalariga telefonni to'liq boshqarishga ruxsat bermaydi, lekin
**Shortcuts** orqali Chach-Chu bilan bemalol gaplashish mumkin:

1. Kompyuterda `python -m chachchu --bridge` ishga tushiring.
2. `config.json` da `bridge.token` ga maxfiy so'z qo'ying.
3. iPhone Shortcuts'da:
   - **Dictate Text** (ovozni matnga aylantirish)
   - **Get Contents of URL** → `POST http://<ip>:8787/ask`
     - Header: `X-Token: <sizning tokeningiz>`
     - Body (JSON): `{ "text": "<diktat qilingan matn>" }`
   - **Speak Text** → kelgan javobni (`reply` maydoni) ovozda o'qish.

Shunda telefon mikrofoniga gapirasiz — Chach-Chu javobni o'zbekcha aytib beradi.

---

## Loyiha tuzilishi

```
setup.sh               # avtomatik o'rnatish (Linux/macOS)
setup-termux.sh        # Android/Termux o'rnatish
run.sh                 # ishga tushirish
chachchu/
├── __main__.py        # kirish nuqtasi (CLI)
├── assistant.py       # asosiy muloqot sikli
├── brain.py           # Claude API + tool-use mantiq
├── speech.py          # ovoz: Termux (Android) va Desktop backendlari
├── permissions.py     # ruxsat so'rash mantig'i
├── bridge.py          # iPhone/Shortcuts uchun HTTP server
└── tools/
    ├── registry.py    # tool'larni ro'yxatga olish va chaqirish
    ├── system.py      # dastur/havola ochish, buyruq bajarish
    ├── web.py         # havola ochish, sana/vaqt
    ├── memory.py      # oddiy eslab qolish
    └── social.py      # Telegram va boshqa tarmoqlar
```

---

## Ogohlantirish

Chach-Chu sizning nomingizdan ish ko'radi. Unga faqat o'zingiz tushunadigan va ruxsat
bergan amallarni bajartiring. `run_shell` kabi buyruqlar kompyuteringizga ta'sir qiladi —
noma'lum buyruqlarni tasdiqlamang.
