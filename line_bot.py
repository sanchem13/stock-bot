# LINE Stock Bot - ดึงข้อมูลจาก Google Sheets แบบ Real-time
# ติดตั้ง: pip install flask gunicorn requests
# รัน: gunicorn line_bot:app

import os
import re
import csv
import time
import json
import hmac
import hashlib
import base64
import requests
import io
from flask import Flask, request, abort

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN", "YOUR_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET", "YOUR_CHANNEL_SECRET")

def verify_signature(body: bytes, signature: str) -> bool:
    hash_ = hmac.new(LINE_CHANNEL_SECRET.encode("utf-8"), body, hashlib.sha256).digest()
    expected = base64.b64encode(hash_).decode("utf-8")
    return hmac.compare_digest(expected, signature)

def send_reply(reply_token: str, text: str):
    """ส่ง reply ไป LINE โดยตรง (bypass SDK เพื่อแก้ UnicodeEncodeError)"""
    payload = json.dumps(
        {"replyToken": reply_token, "messages": [{"type": "text", "text": text}]},
        ensure_ascii=False
    ).encode("utf-8")
    requests.post(
        "https://api.line.me/v2/bot/message/reply",
        data=payload,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
        },
        timeout=10,
    )

# ===================== Google Sheets Config =====================
SHEET_ID = "17vP4_JV4TfAu_8V_POc0k9pt4OkIIToRwW74Pp6FjZM"
SHEET_GIDS = [0, 1984549136, 703469311, 798179661, 1606336018]
CACHE_TTL = 300

_cache = {"data": [], "ts": 0}

def extract_qty(val) -> int:
    if val is None or str(val).strip() == "":
        return 0
    nums = re.findall(r'\d+', str(val))
    return int(nums[0]) if nums else 0

def fetch_sheet_csv(gid: int) -> list:
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        r.encoding = "utf-8"
        reader = csv.reader(io.StringIO(r.text))
        return list(reader)
    except Exception as e:
        print(f"Error fetching gid={gid}: {e}")
        return []

def parse_sheet(rows: list) -> list:
    items = []
    if not rows:
        return items
    first_vals = " ".join(str(c) for row in rows[:5] for c in row).lower()
    is_battery = "แบต" in first_vals and "จอ" not in first_vals[:50]
    cat = "แบตเตอรี่" if is_battery else "จอ"
    current_brand = ""
    for row in rows:
        if not any(str(c).strip() for c in row):
            continue
        col0 = str(row[0]).strip() if row[0] else ""
        if col0 in ["จอ IPHONE", "แบต", "IPHONE"] and not row[1]:
            if col0 not in ["จอ IPHONE", "แบต"]:
                current_brand = col0
            continue
        if col0 and col0 not in ["", "จอ IPHONE", "แบต"]:
            current_brand = col0
        model = str(row[1]).strip() if len(row) > 1 and row[1] else ""
        if not model or model in ["รุ่น", "N", ""]:
            continue
        model = model.replace("\n", " / ")
        if is_battery:
            detail = str(row[2]).strip() if len(row) > 2 and row[2] else ""
            price  = str(row[3]).strip() if len(row) > 3 and row[3] else "-"
            qty    = extract_qty(row[4] if len(row) > 4 else 0)
        else:
            detail = ""
            price  = str(row[2]).strip() if len(row) > 2 and row[2] else "-"
            qty    = extract_qty(row[3] if len(row) > 3 else 0)
        item = {"cat": cat, "brand": current_brand, "model": model, "price": price, "qty": qty}
        if detail:
            item["detail"] = detail
        items.append(item)
    return items

def get_stock() -> list:
    now = time.time()
    if now - _cache["ts"] < CACHE_TTL and _cache["data"]:
        return _cache["data"]
    print("Fetching fresh data from Google Sheets...")
    all_items = []
    for gid in SHEET_GIDS:
        rows = fetch_sheet_csv(gid)
        if rows:
            items = parse_sheet(rows)
            all_items.extend(items)
            print(f"  gid={gid}: {len(items)} items")
    if all_items:
        _cache["data"] = all_items
        _cache["ts"] = now
        print(f"Total: {len(all_items)} items cached")
    elif _cache["data"]:
        print("Fetch failed, using stale cache")
    return _cache["data"]

def search_stock(query: str) -> list:
    stock = get_stock()
    q = query.lower().replace(" ", "").replace("-", "").replace("_", "")
    return [item for item in stock
            if q in item["model"].lower().replace(" ", "").replace("-", "").replace("_", "")]

def format_results(results: list, query: str) -> str:
    if not results:
        return (f"❌ ไม่พบสินค้า \"{query}\"\n\n"
                "💡 ลองพิมพ์ชื่อรุ่น เช่น:\n"
                "  iphone13\n  samsung a54\n  vivo y21\n  redmi note11")
    screens   = [x for x in results if x["cat"] == "จอ"]
    batteries = [x for x in results if x["cat"] == "แบตเตอรี่"]
    lines = [f"🔍 ผลค้นหา: \"{query}\" (พบ {len(results)} รายการ)\n"]
    if screens:
        lines.append("📱 จอ:")
        for item in screens[:10]:
            icon = "✅" if item["qty"] > 0 else "❌"
            lines.append(f"  {icon} {item['brand']} {item['model']}\n     💰 {item['price']} บ. | 📦 {item['qty']} ชิ้น")
    if batteries:
        lines.append("\n🔋 แบตเตอรี่:")
        for item in batteries[:10]:
            icon = "✅" if item["qty"] > 0 else "❌"
            detail = f" ({item['detail']})" if item.get("detail") else ""
            lines.append(f"  {icon} {item['brand']} {item['model']}{detail}\n     💰 {item['price']} บ. | 📦 {item['qty']} ชิ้น")
    if len(results) > 20:
        lines.append(f"\n⚠️ แสดง 20 รายการแรก จากทั้งหมด {len(results)} รายการ")
    return "\n".join(lines)

def format_help() -> str:
    return ("📋 วิธีใช้งาน Stock Bot\n\n"
            "🔍 ค้นหาสินค้า: พิมพ์ชื่อรุ่น\n"
            "ตัวอย่าง:\n  iphone13\n  samsung a54\n  vivo y21\n  redmi note11\n\n"
            "📊 คำสั่งพิเศษ:\n"
            "  จอ -> สรุปสต็อกจอทั้งหมด\n"
            "  แบต -> สรุปสต็อกแบตทั้งหมด\n"
            "  รีเฟรช -> อัปเดตข้อมูลล่าสุด\n"
            "  ช่วย -> วิธีใช้\n\n"
            "✅ = มีสินค้า | ❌ = สินค้าหมด")

def format_category_summary(cat: str) -> str:
    stock = get_stock()
    items    = [x for x in stock if x["cat"] == cat]
    in_stock = [x for x in items if x["qty"] > 0]
    icon = "📱" if cat == "จอ" else "🔋"
    lines = [f"{icon} สรุปสต็อก{cat} ({len(items)} รายการ)\n"]
    lines.append(f"✅ มีสินค้า: {len(in_stock)} | ❌ หมดสต็อก: {len(items)-len(in_stock)}\n")
    lines.append("📦 สินค้ามีสต็อก (10 อันดับแรก):")
    for item in in_stock[:10]:
        lines.append(f"  {item['brand']} {item['model']} | {item['price']} บ. | {item['qty']} ชิ้น")
    if len(in_stock) > 10:
        lines.append(f"\n  ... อีก {len(in_stock)-10} รายการ — ค้นหาด้วยชื่อรุ่น")
    return "\n".join(lines)

# ===================== Webhook =====================
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body_bytes = request.get_data()
    if not verify_signature(body_bytes, signature):
        abort(400)
    body = json.loads(body_bytes.decode("utf-8"))
    for ev in body.get("events", []):
        if ev.get("type") == "message" and ev["message"].get("type") == "text":
            handle_message(ev)
    return "OK"

def handle_message(event):
    text = event["message"]["text"].strip()
    text_lower = text.lower()
    reply_token = event["replyToken"]
    if text_lower in ["help", "ช่วย", "วิธีใช้", "menu", "เมนู"]:
        reply = format_help()
    elif text_lower in ["จอ", "screen", "หน้าจอ"]:
        reply = format_category_summary("จอ")
    elif text_lower in ["แบต", "battery", "แบตเตอรี่"]:
        reply = format_category_summary("แบตเตอรี่")
    elif text_lower in ["รีเฟรช", "refresh", "อัปเดต", "update"]:
        _cache["ts"] = 0
        get_stock()
        total = len(_cache["data"])
        reply = f"✅ อัปเดตข้อมูลจาก Google Sheets แล้ว\n📦 พบสินค้าทั้งหมด {total} รายการ"
    else:
        results = search_stock(text)
        reply = format_results(results, text)
    send_reply(reply_token, reply)

@app.route("/", methods=["GET"])
def health():
    stock = get_stock()
    return f"LINE Stock Bot 🚀 | สินค้า {len(stock)} รายการ | Cache: {int(time.time()-_cache['ts'])}s ago"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
