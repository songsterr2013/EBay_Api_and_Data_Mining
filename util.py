import json
import os
import logging

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