import requests
import json

# --------------------- قوائم M3U (يمكنك إضافة المزيد هنا) ---------------------
M3U_SOURCES = [
    # قنوات دينية
    "https://iptv-org.github.io/iptv/genres/religion.m3u",
    "https://iptv-org.github.io/iptv/countries/sa.m3u",
    "https://iptv-org.github.io/iptv/countries/eg.m3u",

    # قنوات إخبارية
    "https://iptv-org.github.io/iptv/streams/news.m3u",
    "https://iptv-org.github.io/iptv/streams/world.m3u",

    # قنوات رياضية
    "https://iptv-org.github.io/iptv/streams/sports.m3u",

    # قنوات متنوعة
    "https://iptv-org.github.io/iptv/streams/entertainment.m3u",
    "https://iptv-org.github.io/iptv/streams/music.m3u"
]

# --------------------- مسار JSON للتطبيق ---------------------
CHANNELS_JSON_PATH = "remote/channels.json"  # نسخة محلية للتطبيق

# --------------------- دوال المساعدة ---------------------
def fetch_m3u(url):
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"فشل تحميل M3U من {url} : {e}")
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
                "logo": "",        # يمكن إضافة شعارات لاحقًا
                "category": "Other" # سنحدد الفئة لاحقًا
            })
    return channels

def categorize_channel(channel):
    name = channel["name"].lower()
    url = channel["url"].lower()
    # تصنيف القنوات حسب الاسم أو الرابط
    if "quran" in name or "islam" in name:
        channel["category"] = "Quran"
    elif "news" in name or "aljazeera" in name or "cnn" in name:
        channel["category"] = "News"
    elif "sport" in name or "football" in name:
        channel["category"] = "Sports"
    elif "music" in name or "entertainment" in name:
        channel["category"] = "Entertainment"
    else:
        channel["category"] = "Other"
    return channel

# --------------------- البرنامج الرئيسي ---------------------
def main():
    all_channels = []
    for source in M3U_SOURCES:
        m3u_text = fetch_m3u(source)
        channels = parse_m3u(m3u_text)
        channels = [categorize_channel(ch) for ch in channels]
        all_channels.extend(channels)

    # تنظيم القنوات حسب الفئة
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
