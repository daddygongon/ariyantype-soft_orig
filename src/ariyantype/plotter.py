from __future__ import annotations
from collections import defaultdict

import datetime
import warnings
from pathlib import Path
from typing import Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import font_manager


# 日本語フォントの自動設定（ここは最小変更でそのまま）
def _setup_japanese_font():
    candidates = [
        "Noto Sans CJK JP",
        "Noto Sans JP",
        "IPAexGothic",
        "IPAPGothic",
        "TakaoPGothic",
        "TakaoGothic",
        "Yu Gothic",
        "Meiryo",
        "Hiragino Maru Gothic Pro",
        "Hiragino Kaku Gothic ProN",
        "Arial Unicode MS",
    ]

    available = {f.name for f in font_manager.fontManager.ttflist}
    for name in candidates:
        if name in available:
            matplotlib.rcParams["font.family"] = name
            matplotlib.rcParams["axes.unicode_minus"] = False
            return name

    for f in font_manager.fontManager.ttflist:
        n = f.name
        if any(k in n for k in ("IPA", "Noto", "Takao", "Meiryo", "Yu ", "Hiragino")):
            matplotlib.rcParams["font.family"] = n
            matplotlib.rcParams["axes.unicode_minus"] = False
            return n

    warnings.warn("日本語フォントが見つかりません。プロットの日本語ラベルが化ける可能性があります。")
    return None


_setup_japanese_font()  # モジュール読み込み時に一度だけ設定


class Plotter:
    """ログからグラフを生成して保存するクラス（WSL/CUI前提でshow()は使わない）。"""

    def __init__(self, out_dir: Path | str = "."):
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _parse_datetime(s: str) -> datetime.datetime:
        # format used: 2025-12-03 12:34:56 +0900
        try:
            dt_part = " ".join(s.split()[:2])  # strip timezone
            return datetime.datetime.strptime(dt_part, "%Y-%m-%d %H:%M:%S")
        except Exception:
            return datetime.datetime.now()

    @staticmethod
    def _group_by_day_average(times, values):
        """datetime配列を日付単位でまとめ、平均を返す"""
        bucket = defaultdict(list)
        for t, v in zip(times, values):
            bucket[t.date()].append(v)

        days = sorted(bucket.keys())
        avgs = [sum(vs) / len(vs) for vs in (bucket[d] for d in days)]
        return days, avgs

    @staticmethod
    def _group_by_day_sum(times, values):
        """datetime配列を日付単位でまとめ、合計を返す"""
        bucket = defaultdict(list)
        for t, v in zip(times, values):
            bucket[t.date()].append(v)

        days = sorted(bucket.keys())
        sums = [sum(vs) for vs in (bucket[d] for d in days)]
        return days, sums

    def _filter_last_n_days(self, days, values, n_days: int = 90):
        """直近 n_days 分のみ残す（days は datetime.date の配列想定）"""
        if not days:
            return days, values

        latest = max(days)
        threshold = latest - datetime.timedelta(days=n_days)

        new_days = []
        new_values = []
        for d, v in zip(days, values):
            if d >= threshold:
                new_days.append(d)
                new_values.append(v)

        return new_days, new_values

    def _set_daily_xaxis(self, interval: int = 1):
        """x軸を日単位表示に固定（ラベルはMM/DD）"""
        ax = plt.gca()
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=interval))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
        plt.xticks(rotation=45, ha="right")

    def _save_or_default(self, save_path: Optional[Path], default_name: str) -> Path:
        """save_pathが無いなら out_dir/default_name に保存して返す。"""
        return save_path if save_path is not None else (self.out_dir / default_name)

    def plot_speed_log(self, speed_log_path: Path, save_path: Optional[Path] = None) -> None:
        """speed_log を読み、日別平均WPMを（直近3か月・1日単位で）プロットする。"""
        if not speed_log_path.exists():
            raise FileNotFoundError(f"speed log not found: {speed_log_path}")

        times = []
        wpms = []
        with speed_log_path.open(encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) < 4:
                    continue
                dt = self._parse_datetime(parts[0])
                try:
                    total_time = float(parts[2])
                    total_chars = int(parts[3])
                except Exception:
                    continue
                if total_time <= 0:
                    continue
                wpm = (total_chars / 5.0) / (total_time / 60.0)
                times.append(dt)
                wpms.append(wpm)

        if not times:
            raise RuntimeError("no data in speed log")

        # 日別平均へ集約 → 直近90日へ絞り込み
        days, daily_wpms = self._group_by_day_average(times, wpms)
        days, daily_wpms = self._filter_last_n_days(days, daily_wpms, 90)

        plt.figure(figsize=(10, 4))
        plt.plot(days, daily_wpms, marker="o", linestyle="-", label="Daily WPM (avg)")
        self._set_daily_xaxis(interval=1)

        plt.xlabel("日付")
        plt.ylabel("WPM")
        plt.title("Skill Check: WPM (daily average, last 3 months)")
        plt.grid(True)
        plt.tight_layout()

        out = self._save_or_default(save_path, "wpm_over_time.png")
        plt.savefig(str(out))
        print(f"[saved] {out}")
        plt.close()

    def plot_training_scores(self, training_log_path: Path, save_path: Optional[Path] = None) -> None:
        """training_log を読み、日別合計スコア（total_words）を（直近3か月・1日単位で）プロットする。"""
        if not training_log_path.exists():
            raise FileNotFoundError(f"training log not found: {training_log_path}")

        times = []
        scores = []
        sessions = []
        with training_log_path.open(encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) < 4:
                    continue
                dt = self._parse_datetime(parts[0])
                file_name = parts[1]
                try:
                    total_words = int(parts[2])
                except Exception:
                    continue
                times.append(dt)
                scores.append(total_words)
                sessions.append(file_name)

        if not times:
            raise RuntimeError("no data in training log")

        # 日別合計へ集約 → 直近90日へ絞り込み
        days, daily_scores = self._group_by_day_sum(times, scores)
        days, daily_scores = self._filter_last_n_days(days, daily_scores, 90)

        plt.figure(figsize=(10, 4))
        plt.plot(days, daily_scores, marker="o", linestyle="-", label="Daily score (sum)")
        self._set_daily_xaxis(interval=1)

        plt.xlabel("日付")
        plt.ylabel("正答単語数（合計）")
        plt.title("Training scores (daily sum, last 3 months)")
        plt.grid(True)
        plt.tight_layout()

        out = self._save_or_default(save_path, "training_scores.png")
        plt.savefig(str(out))
        print(f"[saved] {out}")
        plt.close()

    def plot_practiced_steps(self, training_log_path: Path, save_path: Optional[Path] = None) -> None:
        """training_log から STEP-xx の出現回数を棒グラフで表示する。"""
        if not training_log_path.exists():
            raise FileNotFoundError(f"training log not found: {training_log_path}")

        counts = {}
        with training_log_path.open(encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) < 2:
                    continue
                file_name = parts[1]
                if file_name.startswith("STEP-") and file_name.endswith(".txt"):
                    num_part = file_name[5:-4]
                    if num_part.isdigit():
                        n = int(num_part)
                        counts[n] = counts.get(n, 0) + 1

        if not counts:
            raise RuntimeError("no STEP data in training log")

        xs = sorted(counts.keys())
        ys = [counts[x] for x in xs]

        plt.figure(figsize=(10, 4))
        plt.bar(xs, ys)
        plt.xlabel("STEP")
        plt.ylabel("練習回数")
        plt.title("Practiced STEP counts")
        plt.grid(axis="y")
        plt.tight_layout()

        out = self._save_or_default(save_path, "practiced_steps.png")
        plt.savefig(str(out))
        plt.close()
