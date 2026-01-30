import time
import random

class SkillChecker:
    def __init__(self, data_manager):
        self.dm = data_manager
        self.words = self.dm.load_lines(self.dm.get_file_path("word.list"))

    def run(self):
        selected = random.sample(self.words, min(20, len(self.words)))
        print("スキルチェックを開始します。Enterでスタート")
        input()
        start = time.time()

        for i, word in enumerate(selected, 1):
            while True:
                typed = input(f"{i}. {word}: ").strip()
                if typed == word:
                    break
                print("間違いです。もう一度。")

        elapsed = time.time() - start
        self.dm.save_speed_log(selected, elapsed)
        m, s = divmod(int(elapsed), 60)
        print(f"完了！かかった時間: {m}分{s}秒")