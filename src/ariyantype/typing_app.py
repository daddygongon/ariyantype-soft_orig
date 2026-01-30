import argparse

from pathlib import Path

from data_manager import DataManager
from data_extractor import DataExtractor
from training_logger import Logger
from skill_checker import SkillChecker
from typing_session import TypingSession
from plotter import Plotter


class TypingApp:
    def __init__(self):
        self.dm = DataManager()
        self.plotter = Plotter(out_dir="plots")  # 追加：保存先フォルダ（自動作成）

    def run(self, argv):
        parser = argparse.ArgumentParser(description="Aoyama Typing Game")
        parser.add_argument("-d", "--data", help="データ展開 (ZIPまたはフォルダ)")
        parser.add_argument("-r", "--record", action="store_true", help="履歴表示")
        parser.add_argument("-c", "--check", action="store_true", help="スキルチェック")
        parser.add_argument("-H", "--history", action="store_true", help="練習したSTEP一覧ho表示") #argparseは-hで自動でhelpを作成するため-Hに変更
        parser.add_argument("--plot-speed", action="store_true", help="スピードログをグラフ表示/保存")
        parser.add_argument("--plot-score", action="store_true", help="トレーニングスコアをグラフ表示/保存")
        parser.add_argument("--out", help="グラフ保存パス（省略時は plots/ に自動保存）") #リモートやヘッドレス環境で実行する場合はエラーになるか、表示できません。 → 保存オプションを追加
        parser.add_argument("step", nargs="?", help="ステップ番号")

        args = parser.parse_args(argv)

        if args.data:
            DataExtractor(self.dm).extract(Path(args.data))
        elif args.record:
            Logger(self.dm).print_Log()
        elif args.history:
            Logger(self.dm).print_history()   # Shunkuntype風の練習履歴表
        elif args.check:
            SkillChecker(self.dm).run()
        elif args.plot_speed:
            out = Path(args.out) if args.out else None
            self.plotter.plot_speed_log(self.dm.speed_log, out)
        elif args.plot_score:
            out = Path(args.out) if args.out else None
            self.plotter.plot_training_scores(self.dm.training_log, out)
        elif args.step and args.step.isdigit():
            file_name = f"STEP-{args.step}.txt"
            TypingSession(self.dm, file_name).run()
        else:
            parser.print_help()
