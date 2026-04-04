from __future__ import annotations
from collections import defaultdict

import datetime
import warnings
from pathlib import Path
from typing import Optional
import platform
import subprocess

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates



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

    def _open_image(self, file_path: Path) -> None:
        """OSに応じてデフォルトの画像ビューアーで開く"""
        system = platform.system()
        try:
            if system == "Darwin":  # macOS
                subprocess.call(["open", str(file_path)])
            elif system == "Windows":  # Windows
                subprocess.call(["cmd", "/c", "start", "", str(file_path)])
            else:  # Linux (Ubuntu, WSL etc.)
                subprocess.call([str(Path.home() / "bin/open"), str(file_path)])
        except Exception as e:
            print(f"画像を開けませんでした: {e}")

    def plot_speed_log(
        self, speed_log_path: Path, save_path: Optional[Path] = None
    ) -> None:

        if not speed_log_path.exists():
            raise FileNotFoundError(f"speed log not found: {speed_log_path}")

        times = []
        durations = []
        with speed_log_path.open(encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) < 4:
                    continue
                dt = self._parse_datetime(parts[0])
                try:
                    total_time = float(parts[2])
                except Exception:
                    continue
                if total_time <= 0:
                    continue
                times.append(dt)
                durations.append(total_time)

        if not times:
            raise RuntimeError("no data in speed log")

        # 直近90日に絞り込む（日別の集約は行わない）
        latest = max(times)
        threshold = latest - datetime.timedelta(days=90)

        filtered_times = []
        filtered_durations = []
        for t, d in zip(times, durations):
            if t >= threshold:
                filtered_times.append(t)
                filtered_durations.append(d)

        if not filtered_times:
            print("No skill check data in the last 3 months.")
            return

        plt.figure(figsize=(10, 4))
        plt.plot(
            filtered_times,
            filtered_durations,
            marker="o",
            linestyle="-",
            label="Time [s]",
        )

        # X-axis: MM/DD HH:MM format
        ax = plt.gca()
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d %H:%M"))
        plt.xticks(rotation=45, ha="right")

        plt.xlabel("DateTime")
        plt.ylabel("Duration (s)")
        plt.title("Skill Check: Time Taken (Per Session, last 3 months)")
        plt.grid(True)
        plt.tight_layout()

        out = self._save_or_default(save_path, "check_time_over_time.png")
        plt.savefig(str(out))
        print(f"[saved] {out}")
        plt.close()

        self._open_image(out)

    def plot_training_scores(
        self, training_log_path: Path, save_path: Optional[Path] = None
    ) -> None:
        """training_log を読み、トレーニング毎の積算時間（所要時間）を細かくプロットする。"""
        if not training_log_path.exists():
            raise FileNotFoundError(f"training log not found: {training_log_path}")

        times = []
        durations = []
        with training_log_path.open(encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) < 4:
                    continue
                dt = self._parse_datetime(parts[0])
                try:
                    total_time = float(parts[3])
                except Exception:
                    continue
                times.append(dt)
                durations.append(total_time)

        if not times:
            raise RuntimeError("no data in training log")

        # 直近90日に絞り込む（日別の集約は行わない）
        latest = max(times)
        threshold = latest - datetime.timedelta(days=90)

        filtered_times = []
        filtered_durations = []
        for t, d in zip(times, durations):
            if t >= threshold:
                filtered_times.append(t)
                filtered_durations.append(d)

        if not filtered_times:
            print("No training data in the last 3 months.")
            return

        # 所要時間を足し合わせて「積算時間」にする
        cumulative_durations = []
        current_sum = 0
        for d in filtered_durations:
            current_sum += d
            cumulative_durations.append(current_sum)
        filtered_durations = cumulative_durations

        # 最大値に合わせて時間を「分」または「時間」に変換
        max_duration = max(filtered_durations)
        if max_duration >= 3600:
            filtered_durations = [d / 3600 for d in filtered_durations]
            y_label = "Cumulative Time (hours)"
            legend_label = "Cumulative Time [h]"
        else:
            filtered_durations = [d / 60 for d in filtered_durations]
            y_label = "Cumulative Time (minutes)"
            legend_label = "Cumulative Time [m]"

        plt.figure(figsize=(10, 4))
        plt.plot(
            filtered_times,
            filtered_durations,
            marker="o",
            linestyle="-",
            label=legend_label,
        )

        # X軸を「月/日 時:分」の形式で細かく表示
        ax = plt.gca()
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d %H:%M"))
        plt.xticks(rotation=45, ha="right")

        plt.xlabel("date and time")
        plt.ylabel(y_label)
        plt.title("Training Time (Per Session, last 3 months)")
        plt.grid(True)
        plt.tight_layout()

        out = self._save_or_default(save_path, "training_time.png")
        plt.savefig(str(out))
        print(f"[saved] {out}")
        plt.close()

        self._open_image(out)
