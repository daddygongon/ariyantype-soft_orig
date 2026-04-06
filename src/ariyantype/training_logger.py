class Logger:
    def __init__(self, data_manager):
        self.dm = data_manager

    def print_Log(self):
        print("\nトレーニング履歴:")
        if self.dm.training_log.exists():
            with self.dm.training_log.open(encoding="utf-8") as f:
                print(f.read())
        else:
            print("データなし")

        print("\nスキルチェック履歴:")
        if self.dm.speed_log.exists():
            with self.dm.speed_log.open(encoding="utf-8") as f:
                print(f.read())
        else:
            print("データなし")

    def print_history(self):
        """Shunkuntype風：STEP練習履歴を整形して表示"""

        practiced = self.dm.get_practiced_steps()

        groups = [
            ("frdejuki", range(1, 5)),
            ("tgyh", range(5, 10)),
            ("vbc", range(10, 15)),
            ("mn,", range(15, 20)),
            ("mid-check", range(20, 25)),
            ("swx", range(25, 30)),
            ("lo.", range(30, 35)),
            ("aqz", range(35, 40)),
            (";p", range(40, 46)),
            ("whole-check", range(46, 51)),
            ("ex01", range(51, 56)),
            ("ex02", range(56, 61)),
            ("ex03", range(61, 66)),
            ("ex04", range(66, 71)),
            ("ex05", range(71, 76)),
            ("ex06", range(76, 81)),
            ("ex07", range(81, 86)),
            ("ex08", range(86, 91)),
            ("ex09", range(91, 96)),
            ("ex10", range(96, 98)),
        ]

        # ヘッダーを17文字幅に合わせてフォーマットで出力
        print(f"{'hour':>4} | {'contents':<11} | {'steps':<17} | practiced")
        for hour, (label, step_range) in enumerate(groups):
            steps_str = ",".join(str(s) for s in step_range)
            practiced_str = ",".join(str(s) for s in step_range if s in practiced)
            # steps_strの幅指定を :<15 から :<17 に変更
            print(f"{hour:4d} | {label:<11} | {steps_str:<17} | {practiced_str}")
