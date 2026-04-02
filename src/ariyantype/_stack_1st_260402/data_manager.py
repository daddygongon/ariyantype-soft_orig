import sys
import datetime
from pathlib import Path
from platformdirs import user_data_dir
from importlib import resources

class DataManager:
    def __init__(self, app_name: str = "ariyantype"):
        # 書き込み先（ログや、ユーザーが展開したtext_data）
        self.app_name = app_name
        self.base_dir = Path(user_data_dir(self.app_name))
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.text_data_dir = self.base_dir / "text_data"
        self.training_log = self.base_dir / "training_data.txt"
        self.speed_log = self.base_dir / "speed_data.txt"
        self.text_data_dir.mkdir(parents=True, exist_ok=True)

    # --- ここが肝：入力データの探索順をDataManagerが決める ---
    def read_text_lines(self, filename: str) -> list[str]:
        # 1) まずユーザー展開済みを優先（既存運用を維持）
        user_path = self.text_data_dir / filename
        if user_path.exists():
            return self._read_lines_from_path(user_path)

        # 2) なければパッケージ同梱データを読む（pip化向き）
        try:
            text = (
                resources.files(self.app_name)
                .joinpath(f"data/{filename}")
                .read_text(encoding="utf-8")
            )
            return [line.strip() for line in text.splitlines() if line.strip()]
        except FileNotFoundError:
            print(f"ファイルが存在しません: {user_path} か、パッケージ内 data/{filename}")
            sys.exit(1)

    def _read_lines_from_path(self, filepath: Path) -> list[str]:
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

