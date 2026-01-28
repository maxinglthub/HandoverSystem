import pandas as pand
import os
import datetime
from dataclasses import dataclass
from typing import List

class CoreClass:
    def __init__(self, path: str):
        self.path = path
        self.df = ReadTaskFile(path)
        #self.colmap = b

def ReadTaskFile(path: str) -> pand.DataFrame:
    RTF = os.path.splitext(path)[1].lower()

    if RTF in [".xlsx", ".xls"]:
        return pand.read_excel(path, dtype=str).fillna("")
    elif RTF == ".csv":
        # 嘗試常見編碼
        for enc in ["utf-8-sig", "cp950", "utf-8"]:
            try:
                return pand.read_csv(path, encoding=enc, dtype=str).fillna("")
            except Exception:
                pass
        raise ValueError("ErrorCode:001")
    else:
        raise ValueError("ErrorCode:002")