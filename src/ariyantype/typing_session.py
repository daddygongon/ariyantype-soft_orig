import sys
import time
import threading

class TypingSession:
    def __init__(self, data_manager, file_name):
        self.dm = data_manager
        self.file_name = file_name
        self.lines = self.dm.load_lines(self.dm.get_file_path(file_name))
        self.time_limit = 60

    def counter(self, expected, typed):
        return sum(1 for e, t in zip(expected.split(), typed.split()) if e == t)

    def run(self):
        print("タイピングゲームを開始します！Enterでスタート")
        input()
        start_time = time.time()
        total_words = 0
        index = 0

        while time.time() - start_time < self.time_limit:
            line = self.lines[index % len(self.lines)]
            print(line)

            typed = []
            done = threading.Event()

            def read_input():
                typed.append(sys.stdin.readline().strip())
                done.set()

            t = threading.Thread(target=read_input)
            t.start()
            timeout = self.time_limit - (time.time() - start_time)
            t.join(timeout)

            if not done.is_set():
                print("時間切れ！")
                break

            total_words += self.counter(line, typed[0])
            index += 1

        print(f"{self.time_limit}秒で合計{total_words}個の単語を正しくタイプしました。")
        self.dm.save_training_log(self.file_name, total_words, self.time_limit)