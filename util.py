import json
import os
import logging
import pandas as pd

def setup_logging(log_filename='api_calls.log'):
    logging.basicConfig(
        filename=log_filename,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'  # 設置日誌格式
    )
    #logging.info("Logging is set up.")


def load_config(config_path:str):
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"檔案 {config_path} 不存在。")
        raise
    except json.JSONDecodeError as e:
        print(f"解析 JSON 檔案時發生錯誤: {e}")
        raise

def write_config(config_path: str, data: dict):
    try:
        with open(config_path, 'w', encoding='utf-8') as file:  # 這裡不會再有警告
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"config is written {config_path}")
    except Exception as e:
        print(f"{config_path} error: {e}")
        raise

def update_config(config_path: str, key: str, value: str):
    try:
        # read
        data = load_config(config_path=config_path)

        # update
        if key in data:
            data[key] = value
        else:
            print(f"key name: '{key}' doesn't exist, create new key name")
            data[key] = value

        # write
        write_config(config_path=config_path, data=data)
        print(f"config '{config_path}' updated，'{key}' has changed to '{value}'。")

    except Exception as e:
        print(f"{config_path} error: {e}")
        raise

def get_config_value(config, key):
    return config.get(key)

def make_folder(dir_name):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

# make all excel in one, for tableau using
def combine_excel_files(base_path, output_file):
    # make an empty df
    combined_df = pd.DataFrame()

    # traversal base_path
    for folder_name in os.listdir(base_path):
        folder_path = os.path.join(base_path, folder_name)

        # check if file start with 'data_n'
        if os.path.isdir(folder_path) and folder_name.startswith('data_'):
            folder_id = folder_name.split('_', 1)[1] if '_' in folder_name else folder_name

            for file_name in os.listdir(folder_path):
                if file_name.startswith(folder_id) and file_name.endswith('.xlsx'):
                    file_path = os.path.join(folder_path, file_name)

                    df = pd.read_excel(file_path)
                    artist_name = folder_id.replace("_", " ")
                    df['藝人名稱'] = artist_name
                    combined_df = pd.concat([combined_df, df], ignore_index=True)
                    print(f'{artist_name}相關DATA已加入')

    if '藝人名稱' in combined_df.columns:
        cols = ['藝人名稱'] + [col for col in combined_df.columns if col != '藝人名稱']
        combined_df = combined_df[cols]

    combined_df.to_excel(output_file, index=False)

    return combined_df

'''if __name__ == '__main__':
    base_path = './data'
    output_file = './all_artist_data.xlsx'

    # 呼叫工具函式
    combine_excel_files(base_path, output_file)'''