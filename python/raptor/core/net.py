import os
import sys
import time
from pathlib import Path

import requests


def download_file(url: str, target_path: Path):
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    with open(target_path, "wb") as f:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/83.0.4103.97 Safari/537.36"
        }
        response = requests.get(url, headers=headers, stream=True)
        total = response.headers.get("content-length")

        if total is None:
            f.write(response.content)
        else:
            downloaded = 0
            total = int(total)
            start_time = time.time()

            for data in response.iter_content(chunk_size=max(int(total / 1000), 1024 * 1024)):
                downloaded += len(data)
                f.write(data)

                try:
                    done = int(50 * downloaded / total) if (downloaded < total) else 50
                    percentage = (downloaded / total) * 100 if (downloaded < total) else 100
                except ZeroDivisionError:
                    done = 50
                    percentage = 100

                elapsed_time = time.time() - start_time
                try:
                    avg_kb_p_s = (downloaded / 1024) / elapsed_time
                except ZeroDivisionError:
                    avg_kb_p_s = 0.0

                avg_speed_str = "{:.2f} KB/s".format(avg_kb_p_s)
                if avg_kb_p_s > 1024:
                    avg_mb_p_s = avg_kb_p_s / 1024
                    avg_speed_str = "{:.2f} MB/s".format(avg_mb_p_s)

                sys.stdout.write("\r[{}{}] {:.2f}% ({})     ".format("█" * done, "." * (50 - done), percentage, avg_speed_str))
                sys.stdout.flush()

    sys.stdout.write("\n")
