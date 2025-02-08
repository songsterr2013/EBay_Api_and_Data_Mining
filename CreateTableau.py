import os
import shutil

from util import load_config, get_config_value

class CreateTableau:
    def __init__(self, searched_word):
        self.searched_word = searched_word
        self.artist_name = self.searched_word.replace(" ", "_").rsplit("_", 1)[0]
        self.artist_name_no_dash = self.artist_name.replace("_", " ")
        self.main_folder = 'data'
        self.artist_folder = os.path.join(self.main_folder, f'data_{self.artist_name}')
        self.target_file = "eBay電商平台上的唱片商品分析(模板).twb"
        self.target_file_rename = f"eBay電商平台上的{self.artist_name_no_dash}唱片商品分析.twb"

    def find_the_temple(self):
        file_path = os.path.join(self.main_folder, self.target_file)

        if os.path.exists(file_path):
            return file_path
        else:
            print(f"未找到檔案 '{self.target_file}' 在資料夾 '{self.main_folder}' 中。")
            return None

    def copy_file_to_artist_folders(self, path):

        if not os.path.exists(self.artist_folder):
            print(f"資料夾 '{self.artist_folder}' 不存在於資料夾 '{self.main_folder}' 中。")
            return

        destination_path = os.path.join(self.artist_folder, self.target_file_rename)
        shutil.copy(path, destination_path)
        print(f"已將檔案 '{self.target_file}' 複製到資料夾 '{self.artist_folder}' 中。")

if __name__ == "__main__":

    config = load_config("config.json")
    keywords = get_config_value(config, "keywords")

    ct = CreateTableau(searched_word=keywords) # init it
    file_loc = ct.find_the_temple()
    ct.copy_file_to_artist_folders(file_loc)