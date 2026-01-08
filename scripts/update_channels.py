import requests
import json

# رابط JSON الحالي في GitHub (الذي سيتم تحديثه لاحقًا)
CHANNELS_JSON_PATH = "remote/channels.json"

# مثال: قائمة مصادر جاهزة من GitHub (يمكنك إضافة أكثر من مصدر)
M3U_SOURCES = [
    # ----------------- قنوات دينية -----------------
    "https://iptv-org.github.io/iptv/countries/sa.m3u",      # السعودية
    "https://iptv-org.github.io/iptv/countries/eg.m3u",      # مصر
    "https://iptv-org.github.io/iptv/countries/ae.m3u",      # الإمارات
    "https://iptv-org.github.io/iptv/genres/religion.m3u",   # قنوات دينية عامة

    # ----------------- قنوات إخبارية -----------------
    "https://iptv-org.github.io/iptv/streams/news.m3u",      # أخبار عالمية
    "https://iptv-org.github.io/iptv/streams/world.m3u",     # قنوات متنوعة عالمية

    # ----------------- قنوات رياضية -----------------
    "https://iptv-org.github.io/iptv/streams/sports.m3u",    # رياضية عامة
    "https://iptv-org.github.io/iptv/countries/gb.m3u",      # بريطانيا (تشمل رياضية وأخبارية)
    
    # ----------------- قنوات متنوعة -----------------
    "https://iptv-org.github.io/iptv/streams/entertainment.m3u",
    "https://iptv-org.github.io/iptv/streams/music.m3u"

    # قنوات دينية
    "https://iptv-org.github.io/iptv/countries/sa.m3u",  # السعودية - تشمل قنوات دينية وإخبارية
    "https://iptv-org.github.io/iptv/countries/eg.m3u",  # مصر - قناة دينية + عامة
    "https://iptv-org.github.io/iptv/blob/master/streams/ae.m3u", # قنوات عربية مني
    # قنوات إخبارية عالمية
    "https://iptv-org.github.io/iptv/streams/news.m3u",  # قنوات أخبار متعددة
]

def fetch_m3u(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.text
    except:
        return ""

def parse_m3u(m3u_text):
    channels = []
    lines = m3u_text.splitlines()
    for i in range(len(lines)):
        if lines[i].startswith("#EXTINF"):
            name = lines[i].split(",")[-1].strip()
            url = lines[i+1].strip() if i+1 < len(lines) else ""
            channels.append({
                "name": name,
                "url": url,
                "logo": "",
                "category": "Auto"
            })
    return channels

def categorize_channel(channel):
    name = channel["name"].lower()
    if "quran" in name:
        channel["category"] = "Quran"
    elif "news" in name:
        channel["category"] = "News"
    else:
        channel["category"] = "Other"
    return channel

def main():
    all_channels = []
    for source in M3U_SOURCES:
        m3u_text = fetch_m3u(source)
        channels = parse_m3u(m3u_text)
        channels = [categorize_channel(ch) for ch in channels]
        all_channels.extend(channels)

    # تنظيم القنوات حسب الفئات
    final_json = {"updated_at": "2026-01-08", "categories": []}
    categories = {}
    for ch in all_channels:
        cat = ch["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(ch)

    for cat_name, ch_list in categories.items():
        final_json["categories"].append({
            "name": cat_name,
            "channels": ch_list
        })

    # حفظ JSON النهائي
    with open(CHANNELS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(final_json, f, ensure_ascii=False, indent=2)

    print(f"تم تحديث القنوات بنجاح، عدد القنوات: {len(all_channels)}")

if __name__ == "__main__":
    main()

