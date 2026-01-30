import sys
import datetime
from pathlib import Path

class DataManager:
    def __init__(self):
        self.base_dir = Path.home() / ".aoyamatype"
        self.text_data_dir = self.base_dir / "text_data"
        self.training_log = self.base_dir / "training_data.txt"
        self.speed_log = self.base_dir / "speed_data.txt"
        self.text_data_dir.mkdir(parents=True, exist_ok=True)

    def get_file_path(self, filename: str) -> Path:
        return self.text_data_dir / filename

    def load_lines(self, filepath: Path):
        if not filepath.exists():
            print(f"ファイルが存在しません: {filepath}")
            sys.exit(1)
        with filepath.open(encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]

    def save_training_log(self, file_name, total_words, total_time):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S +0900")
        with self.training_log.open("a", encoding="utf-8") as f:
            f.write(f"{now},{file_name},{total_words},{total_time}\n")

    def save_speed_log(self, words, total_time):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S +0900")
        total_characters = sum(len(w) for w in words)
        with self.speed_log.open("a", encoding="utf-8") as f:
            f.write(f"{now},{len(words)},{total_time:.2f},{total_characters}\n")
            
    def get_practiced_steps(self):
        """training_log から、練習した STEP 番号の集合を返す"""
        steps = set()
        if not self.training_log.exists():
            return steps

        with self.training_log.open(encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) < 2:
                    continue
                file_name = parts[1]  # "STEP-12.txt" などを想定

                # "STEP-xx.txt" 形式から数字部分を取り出す
                if file_name.startswith("STEP-") and file_name.endswith(".txt"):
                    num_part = file_name[5:-4]  # "STEP-" と ".txt" を除いた部分
                    if num_part.isdigit():
                        steps.add(int(num_part))

        return steps

