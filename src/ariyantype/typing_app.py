import argparse
import sys

from pathlib import Path

from .data_manager import DataManager
from .data_extractor import DataExtractor
from .training_logger import Logger
from .skill_checker import SkillChecker
from .typing_session import TypingSession
from .plotter import Plotter


class TypingApp:
    def __init__(self):
        self.dm = DataManager()
        self.plotter = Plotter(
            out_dir=self.dm.base_dir / "plots"
        )  # 追加：保存先フォルダ（自動作成）

    def app(self, argv):
        parser = argparse.ArgumentParser(description="ariyan typing game")
        parser.add_argument("-d", "--data", help="データ展開 (ZIPまたはフォルダ)")
        parser.add_argument("-r", "--record", action="store_true", help="履歴表示")
        parser.add_argument("-c", "--check", action="store_true", help="スキルチェック")
        parser.add_argument(
            "-H", "--history", action="store_true", help="練習したSTEP一覧をtable表示"
        )  # argparseは-hで自動でhelpを作成するため-Hに変更
        parser.add_argument(
            "--plot-check",
            action="store_true",
            help="スキルチェックの所要時間をグラフ表示/保存",
        )
        parser.add_argument(
            "--plot-training",
            action="store_true",
            help="トレーニングの積算時間をグラフ表示/保存",
        )
        parser.add_argument(
            "--out", help="グラフ保存パス（省略時は plots/ に自動保存）"
        )
        parser.add_argument("step", nargs="?", help="ステップ番号")

        args = parser.parse_args(argv)

        if args.data:
            DataExtractor(self.dm).extract(Path(args.data))
        elif args.record:
            Logger(self.dm).print_Log()
        elif args.history:
            Logger(self.dm).print_history()
        elif args.check:
            SkillChecker(self.dm).skillcheck()
        elif args.plot_check:
            out = Path(args.out) if args.out else None
            try:
                self.plotter.plot_speed_log(self.dm.speed_log, out)
            except FileNotFoundError as e:
                print(f"エラー: {e}")
                print(
                    "正しいプロジェクトのルートディレクトリに移動してから再度実行してください。"
                )
                sys.exit(1)
        elif args.plot_training:
            out = Path(args.out) if args.out else None
            try:
                self.plotter.plot_training_scores(self.dm.training_log, out)
            except FileNotFoundError as e:
                print(f"エラー: {e}")
                print(
                    "正しいプロジェクトのルートディレクトリに移動してから再度実行してください。"
                )
                sys.exit(1)
        elif args.step and args.step.isdigit():
            file_name = f"STEP-{args.step}.txt"
            TypingSession(self.dm, file_name).run()
        else:
            parser.print_help()
