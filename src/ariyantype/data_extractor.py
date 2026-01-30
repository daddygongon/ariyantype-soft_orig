import sys
import zipfile
import shutil
from pathlib import Path

class DataExtractor:
    def __init__(self, data_manager):
        self.dm = data_manager

    def extract(self, path: Path):
        if path.is_file() and path.suffix == ".zip":
            with zipfile.ZipFile(path, "r") as zf:
                for member in zf.namelist():
                    rel_path = member.replace("aoyamatypedata/", "")
                    target_path = self.dm.text_data_dir / rel_path
                    if not target_path.exists():
                        zf.extract(member, self.dm.text_data_dir)
            print("ZIPを展開しました。")
        elif path.is_dir():
            for item in path.iterdir():
                dst = self.dm.text_data_dir / item.name
                if dst.exists():
                    shutil.rmtree(dst) if item.is_dir() else dst.unlink()
                shutil.copytree(item, dst) if item.is_dir() else shutil.copy(item, dst)
            print("フォルダをコピーしました。")
        else:
            print("無効なパスです。")
            sys.exit(1)