import time
import os
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

CONFIG_PATH = "config/m3u_sources.json"
UPDATE_SCRIPT = "scripts/update_channels.py"
DEBOUNCE_SECONDS = 2


class SourcesHandler(FileSystemEventHandler):
    def __init__(self):
        self._last_run = 0

    def _is_target(self, path):
        try:
            return os.path.abspath(path) == os.path.abspath(CONFIG_PATH)
        except Exception:
            return False

    def _run_update(self):
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] تغيير مُكتشف — تشغيل {UPDATE_SCRIPT}")
        try:
            subprocess.run(["python3", UPDATE_SCRIPT])
            # بعد التشغيل، حاول قراءة عدد القنوات من ملف الناتج
            try:
                import json
                out_path = os.path.join("remote", "channels.json")
                if os.path.exists(out_path):
                    with open(out_path, "r", encoding="utf-8") as fh:
                        data = json.load(fh)
                        total = 0
                        for c in data.get("categories", []):
                            total += len(c.get("channels", []))
                    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] تحديث مكتمل — إجمالي القنوات: {total}")
                else:
                    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] لم يتم إيجاد {out_path} بعد التحديث")
            except Exception as e:
                print(f"فشل قراءة ملف القنوات بعد التحديث: {e}")
        except Exception as e:
            print(f"فشل تشغيل {UPDATE_SCRIPT}: {e}")

    def on_modified(self, event):
        if not self._is_target(event.src_path):
            return
        now = time.time()
        if now - self._last_run < DEBOUNCE_SECONDS:
            return
        self._last_run = now
        self._run_update()

    def on_created(self, event):
        if self._is_target(event.src_path):
            self.on_modified(event)


def main():
    watch_dir = os.path.dirname(CONFIG_PATH) or "."
    handler = SourcesHandler()
    observer = Observer()
    observer.schedule(handler, path=watch_dir, recursive=False)
    observer.start()
    print(f"مراقب يعمل على {CONFIG_PATH} — سيشغّل {UPDATE_SCRIPT} عند التغيير")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
