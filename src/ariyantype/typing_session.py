import sys
import time
import threading


class TypingSession:
    def __init__(self, data_manager, file_name):
        self.dm = data_manager
        self.file_name = file_name
        self.lines = self.dm.read_text_lines(self.file_name)

        self.time_limit = 60

    def counter(self, expected, typed):
        return sum(1 for e, t in zip(expected.split(), typed.split()) if e == t)

    def run(self):
        # --- ここから追加 ---
        groups = [
            ("frdejuki", range(1, 5)),
            ("tgyh", range(5, 10)),
            ("vbc", range(10, 15)),
            ("mn,", range(15, 20)),
            ("consol", range(20, 25)),
            ("swx", range(25, 30)),
            ("lo.", range(30, 35)),
            ("aqz", range(35, 40)),
            (";p", range(40, 46)),
            ("consol", range(46, 51)),
        ]

        target_chars = ""
        try:
            step_num = int("".join(filter(str.isdigit, self.file_name)))
            for label, step_range in groups:
                if step_num in step_range:
                    target_chars = label
                    break
        except ValueError:
            pass
        # --- ここまで追加 ---

        # キーボードの配色処理
        kb_lines = [
            " q \\ w \\ e \\ r t \\ y u \\ i \\ o \\ p",
            "  a \\ s \\ d \\ f g \\ h j \\ k \\ l \\ ; enter",
            "sh z \\ x \\ c \\ v b \\ n m \\ , \\ . \\  shift",
        ]

        red = "\033[31m"
        reset = "\033[0m"
        colored_kb = ""

        is_consol = target_chars.startswith("consol") or target_chars.startswith("ex")

        for line in kb_lines:
            i = 0
            while i < len(line):
                if line[i : i + 5] == "enter":
                    colored_kb += "enter"
                    i += 5
                elif line[i : i + 5] == "shift":
                    colored_kb += "shift"
                    i += 5
                elif line[i : i + 2] == "sh" and line[i : i + 5] != "shift":
                    colored_kb += "sh"
                    i += 2
                else:
                    c = line[i]
                    # consolやexではなく、ターゲット文字列に含まれる文字なら赤くする
                    if not is_consol and c in target_chars and c not in " \\":
                        colored_kb += f"{red}{c}{reset}"
                    else:
                        colored_kb += c
                    i += 1
            colored_kb += "\n"

        print(colored_kb)

        if target_chars:
            print(f"【 今回の練習キー: {target_chars} 】")

        print(f"STEP {self.file_name} を開始します。")
        for line in self.lines:
            print(line)
        print("-" * 30)

        input("Enterでスタート")

        print("3...")
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
