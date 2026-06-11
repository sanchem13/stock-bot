# LINE Stock Bot - ค้นหาสต็อกจอและแบตเตอรี่
# ติดตั้ง: pip install flask line-bot-sdk gunicorn
# รัน: gunicorn line_bot:app

import os
import json
import re
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# ตั้งค่า LINE credentials (ใส่ใน environment variable หรือแก้ตรงนี้)
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN", "YOUR_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET", "YOUR_CHANNEL_SECRET")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# ===================== ข้อมูลสต็อก =====================
STOCK_DATA = [
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iphone6",
    "price": "1500",
    "qty": 3
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iphone6plus",
    "price": "1500",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iphone6s",
    "price": "1500",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iphone6s",
    "price": "1500",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iphone7plus",
    "price": "1500",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "IPhone se2 /se3 / iphone8g /black",
    "price": "1500",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iphone8plus",
    "price": "1500",
    "qty": 0
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iPhone X จอ full hd ดีกว่า incell จอถูก สู้แสง",
    "price": "1700",
    "qty": 3
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iPhone X จอ เกรด hard OLED สวย คมสุด",
    "price": "2300",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iphone xs gx",
    "price": "2000",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iPhone XS",
    "price": "1800",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iPhone XS full HD",
    "price": "2000",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iPhone XS เกรด hard oled",
    "price": "2400",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iPhone XS เกรดจอ HD Plus",
    "price": "2500",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iphone Xs MAX fhd",
    "price": "2200",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iphone xR FHD เกรด A",
    "price": "2000-ลดได้1800",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iphone xr เกรด A",
    "price": "2000-ลดได้1800",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iphone XR เกรด B",
    "price": "1800-ลดได้1600",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iphone xr เกรด B",
    "price": "1800-ลดได้1600",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iPhone 11 เกรดจอ FHD",
    "price": "2000",
    "qty": 3
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "i11 จอแท้",
    "price": "2500",
    "qty": 0
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iPhone 11 pro เกรดจอ FHD",
    "price": "2200",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "i11 pro oled",
    "price": "2700",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "i11 pro งาน GX",
    "price": "1700",
    "qty": 0
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "i11 promax incell",
    "price": "2000",
    "qty": 0
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "i11 promax FHD",
    "price": "2500",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "i11 promax oled",
    "price": "3000",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iPhone 11pro max เกรดจอ SOFT OLED",
    "price": "3300",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "i12 hard oled",
    "price": "3500",
    "qty": 0
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iPhone 12 และ 12pro fhd gx",
    "price": "2700",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "i12 i12pro oled",
    "price": "3000",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iPhone 12 และ 12pro เกรดจอ SOFT OLED",
    "price": "3500",
    "qty": 0
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iPhone 12pro max FHD",
    "price": "3000",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iPhone 12pro max soft oled",
    "price": "-",
    "qty": 0
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iPhone 13 เกรดจอ incell JK",
    "price": "2000",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iPhone 13 เกรดจอ FHD",
    "price": "2700",
    "qty": 0
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iPhone 13 เกรดจอ OLED",
    "price": "3000",
    "qty": 0
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iPhone 13 เกรดจอ HARD OLED",
    "price": "3700",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iPhone 13 PROเกรดจอ incell JK",
    "price": "2500",
    "qty": 0
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iPhone 13 Pro เกรดจอ FHD",
    "price": "3000",
    "qty": 3
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iPhone 13 Pro เกรดจอ JCID ไม่แจ้งเตือน",
    "price": "3500",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iphone13 Pro MAX fhd ic",
    "price": "2800",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iPhone 13Pro max เกรดจอ incell JK",
    "price": "2800",
    "qty": 0
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iPhone 13 Pro MAX เกรดจอ ไม่แจ้งเตือน",
    "price": "3800",
    "qty": 5
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iphone13promax hard oled ic",
    "price": "-",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iphone14 fhd",
    "price": "3000-3500",
    "qty": 0
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iphone14pro fhd ic",
    "price": "-",
    "qty": 3
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iphone14pro in cell",
    "price": "-",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iphone14pro diagnosable",
    "price": "-",
    "qty": 3
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iphone14promax",
    "price": "4000",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iphone15 oled",
    "price": "4000",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iphone15 fhd ic",
    "price": "4000",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iphone15 soft oled ic",
    "price": "6500",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iphone15pro",
    "price": "-",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iphone15promax",
    "price": "4500",
    "qty": 0
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iphone15promax full hd",
    "price": "6000",
    "qty": 0
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "จอทัช ipad mini1/mini2",
    "price": "1700",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "จอทัชสกรีน ipad gen9 แท้ ใช้ปากหาได้",
    "price": "2500",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "จอใน Ipad gen9",
    "price": "2700",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "gen11",
    "price": "3000-2500",
    "qty": 0
  },
  {
    "cat": "จอ",
    "brand": "iPhone",
    "model": "iPad Pro 11 นิ้ว รุ่น A1980",
    "price": "9500",
    "qty": 0
  },
  {
    "cat": "จอ",
    "brand": "VIVO",
    "model": "Y91 y93 y95 y1s",
    "price": "1300",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "VIVO",
    "model": "Y11 Y12 Y15 Y17 Y3 U10 U3X Y3S",
    "price": "1500",
    "qty": 4
  },
  {
    "cat": "จอ",
    "brand": "VIVO",
    "model": "y02/y02t / 11-2023",
    "price": "1700",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "VIVO",
    "model": "y03 Y18 Y18e Y28s Y03T",
    "price": "1700",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "VIVO",
    "model": "Y19s / y19spro / y28-4g/5g / y38-4g/5g / y37 pro  / y29-4g/5g / y39-5g / y300i",
    "price": "1700",
    "qty": 3
  },
  {
    "cat": "จอ",
    "brand": "VIVO",
    "model": "Y04 Y19E Y29E Y29s",
    "price": "1700",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "VIVO",
    "model": "Y20/Y15S/Y12S/Y12A/Y20S/Y01a/Y3S/Y30 5G/Y10  / y21/y16/y15a/y15s/y21a/y21e/y21g/y21s/y21t/y33e/y31s / y32/y01/y02s",
    "price": "1600",
    "qty": 5
  },
  {
    "cat": "จอ",
    "brand": "VIVO",
    "model": "Vivo Y17S/Y22/Y22S",
    "price": "1700",
    "qty": 3
  },
  {
    "cat": "จอ",
    "brand": "VIVO",
    "model": "Y35-5G/Y35-2020/Y33T/Y33S/Y76-5G/Y72-5G / Y51-2020/Y52/Y53S/Y52SY31-2020/Y31S / /Y72-5G/Y55S/Y75-5G/Y55-5G/Y56-5G/Y77S / Y77-5G/Y72T/Y51T/Z6LITE-5G/Y76SVivo / Y31 2021/TIX/Y51 2020/Y51A/Y528 5G/ / Y72 5G/IQOO Z3/Z3Pro/Z5X/U3X",
    "price": "1700",
    "qty": 5
  },
  {
    "cat": "จอ",
    "brand": "VIVO",
    "model": "y35 4g/",
    "price": "1700",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "VIVO",
    "model": "Y74s Y76s T1x",
    "price": "-",
    "qty": 0
  },
  {
    "cat": "จอ",
    "brand": "VIVO",
    "model": "Y27 5G Y27s Y35+",
    "price": "1700",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "VIVO",
    "model": "V19 TFT สแกนนิ้วไม่ได้ งานดี",
    "price": "1800",
    "qty": 0
  },
  {
    "cat": "จอ",
    "brand": "VIVO",
    "model": "V11 V11Pro x23 oled",
    "price": "2000",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "VIVO",
    "model": "V11 V11Pro x23 TFT",
    "price": "1500",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "VIVO",
    "model": "v20 pro oled",
    "price": "2000",
    "qty": 0
  },
  {
    "cat": "จอ",
    "brand": "VIVO",
    "model": "v20 v20se v23e oled/ y75/v21e/y70",
    "price": "oled/1800 สแกนนิ้วได้",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "VIVO",
    "model": "v21/v25/t1-5g TFT",
    "price": "1700 สแกนนิ้วไม่ได้",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "VIVO",
    "model": "v21 oled",
    "price": "2000 (สแกนนิ้วได้)",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "VIVO",
    "model": "v23 oled",
    "price": "3500ลดได้ถึง2700",
    "qty": 3
  },
  {
    "cat": "จอ",
    "brand": "VIVO",
    "model": "v23 TFT",
    "price": "1500",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "VIVO",
    "model": "v17pro/v19pro",
    "price": "1700",
    "qty": 0
  },
  {
    "cat": "จอ",
    "brand": "VIVO",
    "model": "S1 Y7S Y9s Z5 V17 neo OLED",
    "price": "2000",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "VIVO",
    "model": "y36-4g/ Y100T / Y 100i / Y78T / IQOO Z7 / 27X",
    "price": "1700",
    "qty": 4
  },
  {
    "cat": "จอ",
    "brand": "VIVO",
    "model": "Y200 Y100 5G V29E V30 LITE V40SE TFT",
    "price": "1500",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "VIVO",
    "model": "Y200 Y100 5G V29E V30 LITE V40SE (OLED)",
    "price": "2500(สแกนนิ้วได้)",
    "qty": 3
  },
  {
    "cat": "จอ",
    "brand": "VIVO",
    "model": "Y19 Y5S",
    "price": "1700",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "VIVO",
    "model": "Y50",
    "price": "1700",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "VIVO",
    "model": "Y71 ขาว",
    "price": "1200",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "VIVO",
    "model": "y81",
    "price": "1600",
    "qty": 0
  },
  {
    "cat": "จอ",
    "brand": "VIVO",
    "model": "V9",
    "price": "1200",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "VIVO",
    "model": "v7 ดำ",
    "price": "1500",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "VIVO",
    "model": "v7 ขาว",
    "price": "1500",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "VIVO",
    "model": "v7plus ขาว",
    "price": "1200",
    "qty": 5
  },
  {
    "cat": "จอ",
    "brand": "VIVO",
    "model": "v7plus ดำ",
    "price": "1200",
    "qty": 0
  },
  {
    "cat": "จอ",
    "brand": "VIVO",
    "model": "v11i",
    "price": "1500",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "VIVO",
    "model": "V15",
    "price": "1600",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "A1K/ C2",
    "price": "1200",
    "qty": 0
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "Realme c83-5g / oppo a6c / c100-5g",
    "price": "1700",
    "qty": 6
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "Realmev23-5g / Narzo50-5g / a97-5g / Q5i",
    "price": "1700",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "Realme15x-5g / c85 oppo a6x-5g/4g/ a6/a6t-5g /narzo90x-5g",
    "price": "1700",
    "qty": 3
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "a5pro",
    "price": "1700",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "A15/A15S/A16K/a16e/Narzo20/Narzo30A/narzo50a / C11 2020/C12/C15/c25c25s/7i/A56-5G/A53S-5G/A55-5GA35",
    "price": "1600",
    "qty": 10
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "A57 2022 4G/5G/A17/A17K/A77S/a57s/ / a18/a38/a58/a78-5g/A77 5G/a57e",
    "price": "1700",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "C35 realme 2020 narzo 50A prime",
    "price": "1700",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "c21/c20/nazro50i",
    "price": "1600",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "realme c61/c63/note60",
    "price": "1700",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "a76-5g/a35-5g",
    "price": "1700",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "OPPO A53-4g 2020/Realme 7i /C17/ONE Plus N100/",
    "price": "1700",
    "qty": 3
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "A54-4G/A53S 4G/A55 4G/A32 4G/A33 4G",
    "price": "-",
    "qty": 0
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "A54-5G/A74-5G/A93-5G/A94-5G/OnePlus N200",
    "price": "1700",
    "qty": 4
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "A16/A16S/A54S/RealmeC25/C25S/Narzo50A",
    "price": "1600",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "A55 5G A56 A53s 5G",
    "price": "1700",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "realme C51 C51s C53 c36 c60/nazro n53 / realme note50",
    "price": "1700",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "Reno5 4G 5G/ reno6 4g/ Reno7 5G",
    "price": "2000(สแกนนิ้วได้)",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "Reno12/realme13pro/realme13proplus",
    "price": "2200",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "Reno3 A91 OLED",
    "price": "2200",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "REALME8i realme9i / A96-4G realme nazo 50 4g",
    "price": "1500",
    "qty": 3
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "F19/ F19PRO/ A95-4G-5G/ A94-4G-5G/ A96-5G/ RENO4 SF-5G/ A74-4g / Rno6z / Rno7z / Rno8z / Real8-4g / Real8pro",
    "price": "1700",
    "qty": 3
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "reno4se oled/a74-4g/a95-4g/a96-5g/reno6lite / reno 6z / reno8z /realme8 /f19/v15/f21pro-5g/-oled",
    "price": "2500 (สแกนนิ้วได้)",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "reno7se / reno7-4g / reno8-4g / reno8t / f21pro4g/ / findx5lite / realme9-4g / realme10 / a78-4g",
    "price": "2000 oled (สแกนนิ้วได้)",
    "qty": 0
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "Reno4 A93-2022",
    "price": "1800",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "oppo f7",
    "price": "1200",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "oppo F9 realme2 U1",
    "price": "1500",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "oppo F11Pro",
    "price": "1700",
    "qty": 6
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "oppo F11",
    "price": "1500",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "C21Y / C25Y",
    "price": "1700",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "C30S/c30/c33/narzo50prime",
    "price": "1700",
    "qty": 5
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "reno2",
    "price": "1700",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "reno2f",
    "price": "1700",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "RENO2F oled",
    "price": "2000",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "Reno8t / reno10 / reno11 / realme10pro plus / realme11pro plus / realme11pro / realme12pro / realme12pro plus / reno10pro / reno11pro / reno9 / a1pro / a3pro / f27proplus / realme p1pro / narzo60pro",
    "price": "1700",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "A83",
    "price": "1500",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "A3s",
    "price": "1400",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "Realme12plus/Realmep1/RealmeNazro70-5g/Narzo70pro-5g",
    "price": "1700",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "C55/c67/a1-5g/realme11-5G /realme11X-5G / narzo 60x-5G / /A58-4G /A79-5G /A98-5G/f23-5g",
    "price": "1700",
    "qty": 4
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "realme C75/c67-4g/realme 13-5g",
    "price": "1700",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "a3pro / c65-4g / a3x / a5x / a60 / c55 /  / a40 / a98-5g / a79-5g / c67 / c75 / c75x / A5-4g / a80/realme12x/Realme12-4g-5g",
    "price": "1600",
    "qty": 6
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "a3x / a5x / a60 / c55 /  / a40 / a98-5g / a79-5g / c67 / c75 / c75x / a80 / realme12x / Realme12-4g-5g",
    "price": "1600",
    "qty": 4
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "realme 3pro/5pro",
    "price": "1500",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "oppo a31 a5-2020/a9-2020 realme C3 5s 5i 6i realme5 /A8/A11x",
    "price": "1500",
    "qty": 4
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "oppo a52-4g/72-4g/92-4g",
    "price": "1800",
    "qty": 3
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "realme6/narzo20pro",
    "price": "1600",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "REALME7 5G",
    "price": "1700",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "REALME X50 x3",
    "price": "1700",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "REALME 9pro",
    "price": "1700",
    "qty": 0
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "REALME 10pro -5g",
    "price": "1700",
    "qty": 5
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "REALME 6pro /a92s/reno4z",
    "price": "1700",
    "qty": 5
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "Oppo a6pro / reno14f / f31 / f31pro / reno15f / reno13 / reno14",
    "price": "1800",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "OPPO-realme",
    "model": "Oppo a6pro / reno14f / f31 / f31pro / reno15f / reno13 / reno14",
    "price": "3500",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "HUAWEI",
    "model": "Y9-2019",
    "price": "1700",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "HUAWEI",
    "model": "Y9-prime y9s",
    "price": "1700",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "HUAWEI",
    "model": "Y5-2019",
    "price": "1200",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "HUAWEI",
    "model": "Y6P-2020",
    "price": "1500",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "HUAWEI",
    "model": "Y7-2019",
    "price": "1300",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "HUAWEI",
    "model": "Y7pro-2018 -ขาว",
    "price": "1300",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "HUAWEI",
    "model": "Y6-2018",
    "price": "1300",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "HUAWEI",
    "model": "NOVA3",
    "price": "1500",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "HUAWEI",
    "model": "NOVA4",
    "price": "1500",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "HUAWEI",
    "model": "p20",
    "price": "1500",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "HUAWEI",
    "model": "p20 lite",
    "price": "1700",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "HUAWEI",
    "model": "p30 lite",
    "price": "1700",
    "qty": 0
  },
  {
    "cat": "จอ",
    "brand": "HUAWEI",
    "model": "Hornor X5",
    "price": "1700",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A06 4G /a045",
    "price": "1700",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A06 5G",
    "price": "1700",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "J4+ j6+",
    "price": "1500",
    "qty": 0
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "J7prime ดำ",
    "price": "-",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "J7prime ขาว",
    "price": "-",
    "qty": 0
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A7 A750",
    "price": "1200",
    "qty": 0
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A13 5G",
    "price": "1700",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A13 4g / A23 4G",
    "price": "1700",
    "qty": 3
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "M336 M33 5G A23-5g m336b A13 5G, A23 4G",
    "price": "1700",
    "qty": 0
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A135 A235 A23 4G M236 M23",
    "price": "1700",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A14-4G/A145 HD",
    "price": "1700",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A14 5G/A146P socket เล็ก",
    "price": "1600",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A14 5G /A146B socket ใหญ่",
    "price": "1600",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A15WF/A15-4G/A15-5G/A156/A155",
    "price": "1700",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A15 5G oled",
    "price": "2000สแกนลายนิ้วมืออยู่ที่ ปุ่มเปิด-ปิดเครื่อง",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A35-5G/A55/A356/fs01",
    "price": "1700",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A55/A35-5G INCELL",
    "price": "1700",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A35/A55 LEEPLUS PREMIUM",
    "price": "1700",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A35 OLED",
    "price": "2000",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A01",
    "price": "1200",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A02s a03 03s",
    "price": "1500",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A04 A045 งานแท้",
    "price": "1500",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A04S/ A13 5G / A136u",
    "price": "1500",
    "qty": 3
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A20",
    "price": "1600",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A05 / A055",
    "price": "1600",
    "qty": 3
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A05S /a057 /a057f",
    "price": "1600",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A21S",
    "price": "1700",
    "qty": 3
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A22 4g incell",
    "price": "1600",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A22 5g",
    "price": "1600",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A11 M11",
    "price": "1700",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "M20",
    "price": "1700",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "M21 M30 M31 M30s",
    "price": "1700",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A20s",
    "price": "1700",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A23 5G A236",
    "price": "1700",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "a25-5g oled",
    "price": "1800",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A24 A25 M34 F34 OLED",
    "price": "1800",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A50S",
    "price": "1800",
    "qty": 0
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A30S oLed",
    "price": "1800",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A30/A50/A50S",
    "price": "2000",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A31 oLed",
    "price": "2000",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A32 oLed",
    "price": "2200",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A32-5G/A326/A125/A127/A022/A326/M127/M236B",
    "price": "1700",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A12/A02 /M02/M125 / M127F / A125 A127 A022/A32-5g",
    "price": "1500",
    "qty": 5
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A02 A12 A125F M02",
    "price": "1500",
    "qty": 0
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A34-5G/A346",
    "price": "1700",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "a34-5g oled",
    "price": "2500",
    "qty": 4
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A36/A366B",
    "price": "-",
    "qty": 0
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "a36/a56/s24fe incel",
    "price": "1800 สแกนนิ้วไม่ได้",
    "qty": 3
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A36 oLed พร้อมเฟรมขอบจอ สี_ดำ",
    "price": "4400สแกนนิ้วได้",
    "qty": 4
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A56 oLed พร้อมเฟรมขอบจอ สี_เงิน",
    "price": "5000สแกนนิ้วได้",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A51 oLed",
    "price": "2000",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A52-4G-5G WF OLED",
    "price": "2500",
    "qty": 3
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "a53 incell",
    "price": "1800",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A53 OLED",
    "price": "2000",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A54-5g / s23fe",
    "price": "1800 สแกนนิ้วไม่ได้",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "a55-5g oled",
    "price": "2500",
    "qty": 3
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A55 oLed /A556 พร้อมเฟรมขอบจอ สี_ดำ",
    "price": "3500",
    "qty": 3
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A16/A26/A165/A17----INCEL HD TFT",
    "price": "1700",
    "qty": 3
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "a16/a17/a26",
    "price": "oled/2000",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A10S",
    "price": "1300",
    "qty": 0
  },
  {
    "cat": "จอ",
    "brand": "SAMSUNG",
    "model": "A71-4G",
    "price": "3500",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "ZTE",
    "model": "ZTE A34 A54",
    "price": "1700",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "ZTE",
    "model": "ZTE A35 A55",
    "price": "1700",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "ZTE",
    "model": "ZTE A35E",
    "price": "1700",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "REDMI",
    "model": "REDMi 8 / 8A",
    "price": "1500",
    "qty": 0
  },
  {
    "cat": "จอ",
    "brand": "REDMI",
    "model": "Redmi a5 / poco c71",
    "price": "1600",
    "qty": 3
  },
  {
    "cat": "จอ",
    "brand": "REDMI",
    "model": "REDMi A1 A1+ a2 a2+. poco c50",
    "price": "1500",
    "qty": 4
  },
  {
    "cat": "จอ",
    "brand": "REDMI",
    "model": "Redmi a3 / poco c61",
    "price": "1500",
    "qty": 4
  },
  {
    "cat": "จอ",
    "brand": "REDMI",
    "model": "REDMi 9A / 9C /10A / poco c3",
    "price": "1600",
    "qty": 0
  },
  {
    "cat": "จอ",
    "brand": "REDMI",
    "model": "REDMi 9T poco m3 redmi9power",
    "price": "1600",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "REDMI",
    "model": "REDMI13c poco c65",
    "price": "1600",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "REDMI",
    "model": "REDMi 10",
    "price": "1600",
    "qty": 0
  },
  {
    "cat": "จอ",
    "brand": "REDMI",
    "model": "REDMi 10C poco c40",
    "price": "1600",
    "qty": 0
  },
  {
    "cat": "จอ",
    "brand": "REDMI",
    "model": "REDmi 14c. poco c67",
    "price": "1600",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "REDMI",
    "model": "Redmi15c/codeCSOT-15/HKC-15A",
    "price": "1700",
    "qty": 4
  },
  {
    "cat": "จอ",
    "brand": "REDMI",
    "model": "Redmi15c/codeXL-15",
    "price": "1700",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "REDMI",
    "model": "Xiaomi 10T Lite, Poco X3 NFC",
    "price": "1700",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "REDMI",
    "model": "X3 Pro",
    "price": "-",
    "qty": 0
  },
  {
    "cat": "จอ",
    "brand": "REDMI",
    "model": "Mi NOTE7/NOTE7 pro",
    "price": "1600",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "REDMI",
    "model": "NOTE9s /9 pro /9se/9promax",
    "price": "1700",
    "qty": 3
  },
  {
    "cat": "จอ",
    "brand": "REDMI",
    "model": "Redmi note9/10x",
    "price": "1700",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "REDMI",
    "model": "NOTE8 pro",
    "price": "1700",
    "qty": 3
  },
  {
    "cat": "จอ",
    "brand": "REDMI",
    "model": "NOTE8",
    "price": "1600",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "REDMI",
    "model": "NOTE10 /NOTE10s 4G",
    "price": "1800",
    "qty": 5
  },
  {
    "cat": "จอ",
    "brand": "REDMI",
    "model": "NOTE10 10 5G/ poco m3 pro 5g",
    "price": "1700",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "REDMI",
    "model": "NOte11 4G 11S 12s poco m4 pro",
    "price": "1700 TFT",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "REDMI",
    "model": "NOte11 5G M4pro 5G",
    "price": "1700",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "REDMI",
    "model": "Note13-4g /Note14-4/5g",
    "price": "2200 (สแกนนิ้วได้)",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "REDMI",
    "model": "Note13-4g /Note14-4/5g",
    "price": "1800 (สแกนนิ้วไม่ได้)",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "REDMI",
    "model": "mi11tpro/11t",
    "price": "1800",
    "qty": 4
  },
  {
    "cat": "จอ",
    "brand": "REDMI",
    "model": "mi11lite-5g",
    "price": "1800",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "REDMI",
    "model": "MI10lite TFT งานถูกเเสกนนิ้วไม่ได้",
    "price": "1800",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "REDMI",
    "model": "MI10lite oled งานแท้",
    "price": "2500",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "infinix",
    "model": "Hot 9 play",
    "price": "1600",
    "qty": 2
  },
  {
    "cat": "จอ",
    "brand": "infinix",
    "model": "HOT50i",
    "price": "1600",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "infinix",
    "model": "note30-5g hot30 spark10pro pova5 pova5pro 5g/Hot40/Hot40pro",
    "price": "1700",
    "qty": 5
  },
  {
    "cat": "จอ",
    "brand": "infinix",
    "model": "smart6Hd",
    "price": "1500",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "infinix",
    "model": "infinix note11 12 12pro x663 670671 676 677",
    "price": "1600",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "infinix",
    "model": "Hot40 pro",
    "price": "1600",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "infinix",
    "model": "smart5",
    "price": "1600",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "infinix",
    "model": "smart7/7hd/7plus /spark10-5g/ hot30i",
    "price": "1600",
    "qty": 7
  },
  {
    "cat": "จอ",
    "brand": "infinix",
    "model": "smart9",
    "price": "1600",
    "qty": 6
  },
  {
    "cat": "จอ",
    "brand": "infinix",
    "model": "smart10",
    "price": "1600",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "infinix",
    "model": "HOT12/HOT20/HOT12i/ HOT20S/CAMON19",
    "price": "1700",
    "qty": 0
  },
  {
    "cat": "จอ",
    "brand": "infinix",
    "model": "smart8/hot40i/spark20c/Tecno spark go2024",
    "price": "1600",
    "qty": 1
  },
  {
    "cat": "จอ",
    "brand": "Nokia",
    "model": "G10 / G20",
    "price": "-",
    "qty": 1
  },
  {
    "cat": "แบตเตอรี่",
    "brand": "IPHONE",
    "model": "iphone 6s",
    "detail": "",
    "price": "800",
    "qty": 1
  },
  {
    "cat": "แบตเตอรี่",
    "brand": "IPHONE",
    "model": "i6s plus",
    "detail": "2750mah",
    "price": "800",
    "qty": 1
  },
  {
    "cat": "แบตเตอรี่",
    "brand": "IPHONE",
    "model": "i7",
    "detail": "1960amh",
    "price": "950",
    "qty": 1
  },
  {
    "cat": "แบตเตอรี่",
    "brand": "IPHONE",
    "model": "i7plus",
    "detail": "แบตเพิ่มความจุ 3600mAh",
    "price": "1100",
    "qty": 1
  },
  {
    "cat": "แบตเตอรี่",
    "brand": "IPHONE",
    "model": "i8",
    "detail": "แบตเพิ่มความจุ 2200mAh",
    "price": "1100",
    "qty": 1
  },
  {
    "cat": "แบตเตอรี่",
    "brand": "IPHONE",
    "model": "i8+",
    "detail": "งาน ดี PISEN Battery มอก",
    "price": "1100",
    "qty": 1
  },
  {
    "cat": "แบตเตอรี่",
    "brand": "IPHONE",
    "model": "iphone SE3/ SE-2022",
    "detail": "",
    "price": "1200",
    "qty": 1
  },
  {
    "cat": "แบตเตอรี่",
    "brand": "IPHONE",
    "model": "5se",
    "detail": "",
    "price": "990",
    "qty": 1
  },
  {
    "cat": "แบตเตอรี่",
    "brand": "IPHONE",
    "model": "xs max",
    "detail": "แบตเพิ่มความจุ3710mAh",
    "price": "1500",
    "qty": 1
  },
  {
    "cat": "แบตเตอรี่",
    "brand": "IPHONE",
    "model": "iphone x",
    "detail": "แบตเพิ่มความจุ2716mah",
    "price": "1300-1400",
    "qty": 1
  },
  {
    "cat": "แบตเตอรี่",
    "brand": "IPHONE",
    "model": "iphone x",
    "detail": "แบตเพิ่มความจุ2950mah",
    "price": "1300-1400",
    "qty": 1
  },
  {
    "cat": "แบตเตอรี่",
    "brand": "IPHONE",
    "model": "iphone x",
    "detail": "แบตเพิ่มความจุmah",
    "price": "1300-1400",
    "qty": 1
  },
  {
    "cat": "แบตเตอรี่",
    "brand": "IPHONE",
    "model": "xr leeplus",
    "detail": "แบตเพิ่มความจุ3500mah",
    "price": "1700",
    "qty": 1
  },
  {
    "cat": "แบตเตอรี่",
    "brand": "IPHONE",
    "model": "i11",
    "detail": "แบตเพิ่มความจุ 3110mAh",
    "price": "1800",
    "qty": 1
  },
  {
    "cat": "แบตเตอรี่",
    "brand": "IPHONE",
    "model": "i11 pro",
    "detail": "แบตเพิ่มความจุ 3450mAh",
    "price": "2200",
    "qty": 1
  },
  {
    "cat": "แบตเตอรี่",
    "brand": "IPHONE",
    "model": "i_Phone11 pro",
    "detail": "งาน ดี PISEN Battery มอก 3046amh",
    "price": "2000",
    "qty": 1
  },
  {
    "cat": "แบตเตอรี่",
    "brand": "IPHONE",
    "model": "i11 promax",
    "detail": "แบตเพิ่มความจุ 3969mAh",
    "price": "1800",
    "qty": 1
  },
  {
    "cat": "แบตเตอรี่",
    "brand": "IPHONE",
    "model": "i_Phone12",
    "detail": "งาน ดี PISEN Battery มอก",
    "price": "1800",
    "qty": 1
  },
  {
    "cat": "แบตเตอรี่",
    "brand": "IPHONE",
    "model": "i12 i12pro",
    "detail": "แบตเพิ่มความจุ 2815mAh",
    "price": "1800",
    "qty": 1
  },
  {
    "cat": "แบตเตอรี่",
    "brand": "IPHONE",
    "model": "i12 i12pro",
    "detail": "แบตเพิ่มความจุ 3200mAh",
    "price": "2100",
    "qty": 1
  },
  {
    "cat": "แบตเตอรี่",
    "brand": "IPHONE",
    "model": "12pro",
    "detail": "3100mah",
    "price": "2000",
    "qty": 1
  },
  {
    "cat": "แบตเตอรี่",
    "brand": "IPHONE",
    "model": "i12pro max",
    "detail": "ผ่านการซ่อมแซม4200mah",
    "price": "2100",
    "qty": 1
  },
  {
    "cat": "แบตเตอรี่",
    "brand": "IPHONE",
    "model": "i_Phone13",
    "detail": "แบต100% รอบชาร์จ 0 💥 ซ่อมแซมได้ ขึ้นแท้3500mah",
    "price": "1800",
    "qty": 1
  },
  {
    "cat": "แบตเตอรี่",
    "brand": "IPHONE",
    "model": "i_Phone13",
    "detail": "งาน ดี PISEN Battery มอก 3227Mah",
    "price": "1800",
    "qty": 1
  },
  {
    "cat": "แบตเตอรี่",
    "brand": "IPHONE",
    "model": "i_Phone13 Pro",
    "detail": "งาน ดี PISEN Battery มอก",
    "price": "2300",
    "qty": 1
  },
  {
    "cat": "แบตเตอรี่",
    "brand": "IPHONE",
    "model": "i_Phone13 Pro",
    "detail": "แบต100% รอบชาร์จ 0 💥 ซ่อมแซมได้ ขึ้นแท้",
    "price": "2300",
    "qty": 1
  },
  {
    "cat": "แบตเตอรี่",
    "brand": "IPHONE",
    "model": "iphone 13promax",
    "detail": "แบต100% รอบชาร์จ 0 💥 ซ่อมแซมได้ ขึ้นแท้",
    "price": "2300",
    "qty": 1
  },
  {
    "cat": "แบตเตอรี่",
    "brand": "IPHONE",
    "model": "i13pro max",
    "detail": "ผ่านการซ่อมแซม4450mah",
    "price": "2300",
    "qty": 1
  },
  {
    "cat": "แบตเตอรี่",
    "brand": "IPHONE",
    "model": "i13pro max",
    "detail": "วินิจฉัย ชิ้นส่วนแท้จาก Apple",
    "price": "2300",
    "qty": 1
  },
  {
    "cat": "แบตเตอรี่",
    "brand": "IPHONE",
    "model": "i14",
    "detail": "งาน ดี PISEN Battery มอก",
    "price": "2600",
    "qty": 1
  },
  {
    "cat": "แบตเตอรี่",
    "brand": "IPHONE",
    "model": "i14 Plus",
    "detail": "งาน ดี PISEN Battery มอก",
    "price": "2700",
    "qty": 1
  },
  {
    "cat": "แบตเตอรี่",
    "brand": "IPHONE",
    "model": "i14pro",
    "detail": "แบต100% รอบชาร์จ 0 💥 ซ่อมแซมได้ ขึ้นแท้3500mah",
    "price": "-",
    "qty": 1
  },
  {
    "cat": "แบตเตอรี่",
    "brand": "IPHONE",
    "model": "i14pro",
    "detail": "วินิจฉัย ชิ้นส่วนแท้จาก Apple",
    "price": "2000",
    "qty": 1
  },
  {
    "cat": "แบตเตอรี่",
    "brand": "IPHONE",
    "model": "i14pro max",
    "detail": "มอก 4222mah",
    "price": "2500",
    "qty": 1
  }
]

# ===================== ฟังก์ชันค้นหา =====================
def search_stock(query: str) -> list:
    query_clean = query.lower().replace(" ", "").replace("-", "").replace("_", "")
    results = []
    for item in STOCK_DATA:
        model_clean = item["model"].lower().replace(" ", "").replace("-", "").replace("_", "")
        if query_clean in model_clean:
            results.append(item)
    return results

def format_results(results: list, query: str) -> str:
    if not results:
        return (
            f"❌ ไม่พบสินค้า \"{query}\"\n\n"
            "💡 ลองพิมพ์ชื่อรุ่นอีกครั้ง เช่น:\n"
            "  • iphone13\n  • samsung a54\n  • vivo y21\n  • redmi note11"
        )

    # แยกจอ vs แบตต
    screens = [x for x in results if x["cat"] == "จอ"]
    batteries = [x for x in results if x["cat"] == "แบตเตอรี่"]

    lines = [f"🔍 ผลค้นหา: \"{query}\" (พบ {len(results)} รายการ)\n"]

    if screens:
        lines.append("📱 จอ:")
        for item in screens[:10]:
            qty = item["qty"]
            qty_icon = "✅" if qty > 0 else "❌"
            lines.append(
                f"  {qty_icon} {item['brand']} {item['model']}\n"
                f"     💰 ราคา: {item['price']} บาท | 📦 คงเหลือ: {qty} ชิ้น"
            )

    if batteries:
        lines.append("\n🔋 แบตเตอรี่:")
        for item in batteries[:10]:
            qty = item["qty"]
            qty_icon = "✅" if qty > 0 else "❌"
            detail = f" ({item['detail']})" if item.get("detail") else ""
            lines.append(
                f"  {qty_icon} {item['brand']} {item['model']}{detail}\n"
                f"     💰 ราคา: {item['price']} บาท | 📦 คงเหลือ: {qty} ชิ้น"
            )

    if len(results) > 20:
        lines.append(f"\n⚠️ แสดง 20 รายการแรก จากทั้งหมด {len(results)} รายการ\nลองค้นหาให้เจาะจงขึ้น")

    return "\n".join(lines)

def format_help() -> str:
    return (
        "📋 วิธีใช้งาน Stock Bot\n\n"
        "🔍 ค้นหาสินค้า: พิมพ์ชื่อรุ่น\n"
        "ตัวอย่าง:\n"
        "  • iphone13\n"
        "  • samsung a54\n"
        "  • vivo y21\n"
        "  • redmi note11\n"
        "  • oppo reno5\n\n"
        "📊 คำสั่งพิเศษ:\n"
        "  • พิมพ์ \"จอ\" → ดูสต็อกจอทั้งหมด\n"
        "  • พิมพ์ \"แบต\" → ดูสต็อกแบตทั้งหมด\n"
        "  • พิมพ์ \"ช่วย\" หรือ \"help\" → แสดงวิธีใช้\n\n"
        "✅ = มีสินค้า | ❌ = สินค้าหมด"
    )

def format_category_summary(cat: str) -> str:
    items = [x for x in STOCK_DATA if x["cat"] == cat]
    in_stock = [x for x in items if x["qty"] > 0]
    out_of_stock = [x for x in items if x["qty"] == 0]

    icon = "📱" if cat == "จอ" else "🔋"
    lines = [f"{icon} สรุปสต็อก{cat} ({len(items)} รายการ)\n"]
    lines.append(f"✅ มีสินค้า: {len(in_stock)} รายการ")
    lines.append(f"❌ หมดสต็อก: {len(out_of_stock)} รายการ\n")
    lines.append("📦 สินค้ามีสต็อก (10 อันดับแรก):")
    for item in in_stock[:10]:
        lines.append(f"  • {item['brand']} {item['model']} | {item['price']} บ. | {item['qty']} ชิ้น")

    if len(in_stock) > 10:
        lines.append(f"\n  ... และอีก {len(in_stock)-10} รายการ")
        lines.append("  ค้นหาด้วยชื่อรุ่นเพื่อดูรายละเอียด")

    return "\n".join(lines)

# ===================== Webhook =====================
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.strip()
    text_lower = text.lower()

    # คำสั่งพิเศษ
    if text_lower in ["help", "ช่วย", "วิธีใช้", "menu", "เมนู"]:
        reply = format_help()
    elif text_lower in ["จอ", "screen", "หน้าจอ"]:
        reply = format_category_summary("จอ")
    elif text_lower in ["แบต", "battery", "แบตเตอรี่"]:
        reply = format_category_summary("แบตเตอรี่")
    else:
        # ค้นหาตามชื่อรุ่น
        results = search_stock(text)
        reply = format_results(results, text)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

@app.route("/", methods=["GET"])
def health():
    return "LINE Stock Bot is running! 🚀"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
