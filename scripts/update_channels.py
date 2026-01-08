import requests
import json
import os

# --------------------- قوائم M3U (يمكنك إضافة المزيد هنا) ---------------------
# المسار إلى ملف تكوين المصادر الخارجي
CONFIG_SOURCES_PATH = "config/m3u_sources.json"

# مصادر افتراضية تُستخدم إذا لم يوجد ملف التكوين
DEFAULT_M3U_SOURCES = [
    "https://iptv-org.github.io/iptv/countries/sa.m3u",
    "https://iptv-org.github.io/iptv/countries/eg.m3u",
]

# دالة لقراءة المصادر من ملف التكوين أو إنشاء الملف بالمصادر الافتراضية
def load_m3u_sources():
    try:
        with open(CONFIG_SOURCES_PATH, "r", encoding="utf-8") as cf:
            data = json.load(cf)
            if isinstance(data, list):
                return data
    except FileNotFoundError:
        # أنشئ دليل config والملف الافتراضي
        cfg_dir = os.path.dirname(CONFIG_SOURCES_PATH)
        if cfg_dir:
            os.makedirs(cfg_dir, exist_ok=True)
        with open(CONFIG_SOURCES_PATH, "w", encoding="utf-8") as cf:
            json.dump(DEFAULT_M3U_SOURCES, cf, ensure_ascii=False, indent=2)
        return DEFAULT_M3U_SOURCES
    except Exception as e:
        print(f"خطأ في قراءة {CONFIG_SOURCES_PATH}: {e}")
    return DEFAULT_M3U_SOURCES

# اقرأ المصادر عند التشغيل
M3U_SOURCES = load_m3u_sources()

# --------------------- مسار JSON للتطبيق ---------------------
CHANNELS_JSON_PATH = "remote/channels.json"  # نسخة محلية للتطبيق

# --------------------- دوال المساعدة ---------------------
def fetch_m3u(url):
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return r.text, None
    except Exception as e:
        err = str(e)
        print(f"فشل تحميل M3U من {url} : {err}")
        return "", err

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
    failed_sources = []

    # تأكد من وجود مجلد الإخراج مبكراً لكتابة ملفات المساعدة
    dirpath = os.path.dirname(CHANNELS_JSON_PATH)
    if dirpath:
        os.makedirs(dirpath, exist_ok=True)

    print(f"قراءة مصادر M3U من: {CONFIG_SOURCES_PATH} (المجموع: {len(M3U_SOURCES)})")
    for s in M3U_SOURCES:
        print(f" - {s}")

    for source in M3U_SOURCES:
        m3u_text, err = fetch_m3u(source)
        if err:
            failed_sources.append({"source": source, "error": err})
            continue
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

    # إحصاءات
    total_sources = len(M3U_SOURCES)
    failed_count = len(failed_sources)
    success_count = total_sources - failed_count
    print("\nملخص التحديث:")
    print(f" - المصادر المدخلة: {total_sources}")
    print(f" - تم التحميل بنجاح من: {success_count}")
    print(f" - فشلت من: {failed_count}")
    print(f" - ملف القنوات: {CHANNELS_JSON_PATH} (القنوات: {len(all_channels)})")

    # سجل المصادر الفاشلة إن وُجدت
    if failed_sources:
        failed_path = os.path.join(dirpath or ".", "failed_sources.json")
        with open(failed_path, "w", encoding="utf-8") as fs:
            json.dump(failed_sources, fs, ensure_ascii=False, indent=2)
        print(f" - ملف المصادر الفاشلة: {failed_path}")

if __name__ == "__main__":
    main()
