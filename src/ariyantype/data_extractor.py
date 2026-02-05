import sys
import zipfile
import shutil
from pathlib import Path

import shutil
import zipfile
from pathlib import Path


class DataExtractor:
    def __init__(self, data_manager):
        self.dm = data_manager

    def extract(self, path: Path) -> None:
        if path.is_file() and path.suffix.lower() == ".zip":
            self._extract_zip(path)
            print("ZIPを展開しました。")
            return

        if path.is_dir():
            self._copy_folder(path)
            print("フォルダをコピーしました。")
            return

        raise ValueError(f"無効なパスです: {path}")

    def _extract_zip(self, zip_path: Path) -> None:
        base = self.dm.text_data_dir.resolve()

        with zipfile.ZipFile(zip_path, "r") as zf:
            for member in zf.namelist():
                
                if member.endswith("/"):
                    continue

                rel = member.replace("aoyamatypedata/", "", 1)
                target = (self.dm.text_data_dir / rel)

                # Zip Slip対策：展開先が base 配下であることを保証
                target_resolved = target.resolve()
                if base not in target_resolved.parents and target_resolved != base:
                    raise ValueError(f"不正なZIPパスです: {member}")

                # 既存ファイルを上書きしない（必要なら仕様で変更）
                if target.exists():
                    continue

                target.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(member) as src, target.open("wb") as dst:
                    shutil.copyfileobj(src, dst)

    def _copy_folder(self, folder_path: Path) -> None:
        for item in folder_path.iterdir():
            dst = self.dm.text_data_dir / item.name
            if dst.exists():
                shutil.rmtree(dst) if dst.is_dir() else dst.unlink()
            shutil.copytree(item, dst) if item.is_dir() else shutil.copy(item, dst)
