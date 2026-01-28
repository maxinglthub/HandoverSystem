import pandas as pand
import os
import datetime
from dataclasses import dataclass
from typing import List, Optional

class CoreClass:

    #初始化
    def __init__(self, path: str):
        self.path = path
        self.df = ReadTaskFile(path)

        self.display_list = List[str] = []
        for tasks in ["Name", "Yes", "No"]:
            if tasks in self.display_list:
                self.display_list.append(self.display_list[tasks])
            if not self.display_list:
                self.display_list = list(self.df.columns)

    #新增task
    def AddTask(self, data):
        new_task = pand.Series({c: data.get(c, '') for c in self.df.columns}, index=self.df.columns)
        self.df.loc[len(self.df)] = new_task
        self.df = self.df.reset_index(drop=True)

    #刪除task
    def DelTask(self, index):
        old_data_amount = len(self.df)
        self.df = self.df.drop(index=index, errors='ignore').reset_index(drop=True)
        return old_data_amount - len(self.df)

    #複寫到檔案
    def SaveTaskToFile(self, path: Optional[str] = None) -> str:
        path = path or self.path
        ext = os.path.splitext(path)[1].lower()
        if ext == ".xlsx" or ext == ".xls":
            self.df.to_excel(path, index=False)
        else:
            self.df.to_csv(path, index=False, encoding="utf-8-sig")
        return path

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