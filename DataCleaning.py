import os
import glob
import re
from datetime import datetime
import json
from json.decoder import JSONDecodeError
import pandas as pd
from util import load_config, get_config_value

class DataCleaning:
    def __init__(self, searched_word):
        self.artist_name = searched_word.replace(" ", "_").rsplit("_", 1)[0]
        self.given_name = self.artist_name.split('_')[0]
        self.last_name = self.artist_name.split('_')[-1]
        self.main_folder = 'data'
        self.discography_file_loc = os.path.join('Discography', f'{self.artist_name}_discography.xlsx')
        self.artist_folder = os.path.join(self.main_folder, f'data_{self.artist_name}')
        self.to_excel_name = f'{self.artist_name}_data.xlsx'
        self.df = None # will build it later

    # group all xlsx into one and roughly clean it
    def merge_xlsx_from_folder(self):
        # get all file's name from folder_path
        file_paths = glob.glob(os.path.join(self.artist_folder, f"ebay_data_{self.artist_name}*.xlsx"))

        if not file_paths:
            print(f"No .xlsx files found in {self.artist_folder}")
            return pd.DataFrame()

        # make all dataframe into one
        dataframes = []
        file_amount = len(file_paths)
        for q, file in enumerate(file_paths):
            print(f"Reading {file} , {q + 1} / {file_amount}")
            df = pd.read_excel(file)
            dataframes.append(df)

        # concatenate all df, then drop duplicate, then make df
        merged_df = pd.concat(dataframes, ignore_index=True)
        data_cleaned = merged_df.drop_duplicates(subset=["itemId", "title"], keep="first")
        data_cleaned = data_cleaned.reset_index(drop=True)
        self.df = data_cleaned

    # can't access json type directly if we don't turn it into py type
    def make_json_to_str(self, columns_to_fix:list):
        # this func is going to be applied for making json type -> py type
        def process_json_cell(cell):
            try:
                # in most of the cases
                return json.loads(cell.replace("'", '"'))
            except JSONDecodeError:
                # handling datetime format
                cell = re.sub(
                    r"datetime\.datetime\((.*?)\)",
                    lambda match: f'"{datetime(*map(int, match.group(1).split(", ")))}"',
                    cell
                )
                return json.loads(cell.replace("'", '"'))
            except (TypeError, AttributeError):
                # handling null
                return None if pd.isna(cell) else json.loads(cell.replace("'", '"'))

        for col in columns_to_fix:
            try:
                # one apply method to fix all of them
                self.df[col] = self.df[col].apply(process_json_cell)
            except Exception as e:
                print(f"處理欄位 {col} 時發生錯誤: {e}")

    # use json_normalize to flat col into different cols
    def split_json_cols(self, columns_to_split:list):

        list_to_concat = []
        for col in columns_to_split:
            temp_df = pd.json_normalize(self.df[col]).copy()

            if col == "productId":
                temp_df.rename(columns={'value': 'ReferenceID'}, inplace=True)
                temp_df = temp_df['ReferenceID']

            list_to_concat.append(temp_df)

        self.df = pd.concat([self.df] + list_to_concat, axis=1)

    def add_item_year_col(self):
        # match a number between 1900 and 2030
        self.df['item_year'] = self.df['title'].str.extract(r'\b(19[0-9]{2}|20[0-2][0-9]|2030)\b')


    def add_year_difference_col(self):
        self.df['year_difference'] = abs(self.df['Album_year'] - self.df['item_year'])

    def dtype_handling(self):
        self.df['convertedCurrentPrice.value'] = pd.to_numeric(self.df['convertedCurrentPrice.value'], errors="coerce").astype('float64')
        self.df['item_year'] = pd.to_numeric(self.df['item_year'], errors='coerce').astype('Int64')
        self.df['Album_year'] = pd.to_numeric(self.df['Album_year'], errors='coerce').astype('Int64')
        self.df['watchCount'] = pd.to_numeric(self.df['item_year'], errors='coerce').astype('Int64')
        self.df['startTime'] = pd.to_datetime(self.df['startTime'])
        self.df['endTime'] = pd.to_datetime(self.df['endTime'])

    def cols_drop(self, cols_to_drop:list):
        self._validate_columns(cols_to_drop)
        self.df.drop(columns=cols_to_drop, inplace=True)

    def cols_rename(self, rename_dict):
        self._validate_columns(rename_dict.keys())
        self.df.rename(columns=rename_dict, inplace=True)

    def cols_rearrange(self, columns_to_rearrange):
        self._validate_columns(columns_to_rearrange)
        self.df = self.df[columns_to_rearrange]

    def convert_new_n_used(self):
        # only have '1000' and '3000'
        self.df.loc[self.df['conditionId'] != '1000', 'conditionId'] = '3000'

    def filter_categories(self, filter_dict):
        query = False
        for col, values in filter_dict.items():
            query |= self.df[col].isin(values)

        self.df = self.df[query].reset_index(drop=True)

    def read_discography(self):
        dtype_mapping = {
            "Year_of_pressing": "Int64",
            "title": str,
            "title_for_match": str,
            "label": str
        }
        disco_df = pd.read_excel(self.discography_file_loc, dtype=dtype_mapping, engine="openpyxl")

        # make sure no blank space
        columns_to_strip = ['title', 'title_for_match', 'label']
        for column in columns_to_strip:
            disco_df[column] = disco_df[column].str.strip()

        artist_albums = disco_df[['year_of_pressing', 'title', 'title_for_match', 'label']].values.tolist()
        self.df['title'] = self.df['title'].astype('string') # make sure ['title'] is a string format

        def extract_album_info(title, full_name, given_name, last_name):
            # make sure everything for matching is lower case
            full_name = full_name.replace("_", " ")
            title, full_name, given_name, last_name = [item.lower() for item in (title, full_name, given_name, last_name)]
            name_set = {full_name, given_name, last_name}
            counts = {name: title.count(name) for name in name_set}

            for album in artist_albums:
                artist_year, artist_title, match_title, album_label = album
                match_title = match_title.lower()
                cols_to_return = (artist_title, artist_year, album_label)

                if match_title not in title:  # Skip if no match
                    continue
                if match_title not in name_set:  # matched but no in name set
                    return cols_to_return

                # matched, in name set
                if match_title == full_name and counts[full_name] >= 2:
                    return cols_to_return
                if match_title == given_name and counts[given_name] >= 2 and counts[last_name] >= 1:
                    return cols_to_return
                if match_title == last_name and counts[given_name] >= 1 and counts[last_name] >= 2:
                    return cols_to_return

            # otherwise, no match can be found
            return None, None, None

        self.df[['Album_name', 'Album_year', 'album_label']] = self.df['title'].apply(
            lambda x: extract_album_info(x, self.artist_name, self.given_name, self.last_name)).apply(pd.Series)
        # remove ['Album_name'] == Nan data
        self.df = self.df[~self.df['Album_name'].isnull()]

    def to_excel(self):
        save_path = os.path.join(self.artist_folder, self.to_excel_name)
        self.df.to_excel(save_path, index=False)
        print(f'檔案: {self.to_excel_name} ，已匯出至 {self.artist_folder}')

    def _validate_columns(self, columns: list):
        invalid_cols = [col for col in columns if col not in set(self.df.columns)]
        if invalid_cols:
            raise ValueError(f"欄位 {invalid_cols} 不存在於 DataFrame 中，請檢查輸入列表。")

if __name__ == "__main__":

    # 確保放入格式正確的discography的excel檔
    # 檔名需為: "{given_name}_{last_name}_discography.xlsx"
    # a欄為'Year of pressing', 首版年份，標題為，格式為4位數字，如1996
    # b欄是'Title', 專輯名稱，格式為字串，如 Chet Baker in Milan
    # c欄是'title_for_match', 手動調整專輯名稱後的字串，以盡可能多去匹配到為目的，愈簡短的Title需放到愈下面，如 Chet Baker in Milan -> in Milan

    # read json
    config = load_config("config.json")
    keywords = get_config_value(config, "keywords")
    cols_to_fix = get_config_value(config, "cols_to_fix")
    cols_to_del = get_config_value(config, "cols_to_del")
    filter_condition = get_config_value(config, "filter_condition")
    cols_to_rearrange = get_config_value(config, "cols_to_rearrange")
    cols_to_rename = get_config_value(config, "cols_to_rename")

    dc = DataCleaning(searched_word=keywords) # init it

    dc.merge_xlsx_from_folder() # 多份EXCEL合一
    dc.make_json_to_str(columns_to_fix=cols_to_fix) # 處理JSON型態
    dc.split_json_cols(columns_to_split=cols_to_fix) # 拆解cols
    dc.cols_drop(cols_to_drop=cols_to_fix + cols_to_del) # 去掉不需要的cols

    dc.filter_categories(filter_dict=filter_condition) # 篩選資料
    dc.convert_new_n_used() # 將1000全新以外的condition id統統改為3000二手
    dc.read_discography() # 取得唱片專輯相對應的出版年份
    dc.add_item_year_col() # 新增額外欄位
    dc.dtype_handling() # 將data轉換成正確的dtype
    dc.add_year_difference_col()  # 新增額外欄位
    dc.cols_rearrange(columns_to_rearrange=cols_to_rearrange) # 調整欄位順序
    dc.cols_rename(rename_dict=cols_to_rename)  # 改名

    dc.to_excel() # 匯出EXCEL