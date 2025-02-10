import subprocess
import os
from util import update_config, load_config, get_config_value

def main():
    # 設定虛擬環境中的 Python 路徑
    python_exe = r".\.venv\Scripts\python.exe"  # 虛擬環境 Python 解釋器路徑
    config_file = "config.json"
    py1 = "Ebay.py"
    py2 = "DataCleaning.py"
    py3 = "CreateTableau.py"
    key = "keywords"

    # 檢查路徑是否正確
    if not os.path.exists(python_exe):
        print("錯誤：找不到指定的虛擬環境 Python 解釋器。")
        return

    # 方法1: 輸入關鍵字 (單次搜索)
    #jazz_giant = [input("請輸入關鍵字 (例如: Chet Baker vinyl, Bill Evans vinyl): ")]

    # 方法2: 讀json檔
    # config = load_config("config.json")
    # jazz_giant = get_config_value(config, "jazz_giant")

    # 方法3: for開發用，直接在裡面的list中修改就好
    '''jazz_giant = ['Bill Evans', 'Chet Baker', 'Miles Davis',
                      'John Coltrane', 'Keith Jarrett', 'Stan Getz',
                      'Louis Armstrong', 'Duke Ellington', 'Dave Brubeck',
                      'Wes Montgomery', 'Ella Fitzgerald', 'Charlie Parker',
                      'Herbie Hancock', 'Cannonball Adderley', 'Erroll Garner',
                      'Frank Sinatra', 'Chick Corea', 'Gerry Mulligan',
                      'Charles Mingus', 'Oscar Peterson', 'Joe Pass',
                      'Ornette Coleman', 'Sonny Rollins', 'Thelonious Monk',
                      'Pat Metheny', 'Antonio Carlos Jobim', 'Lee Morgan',
                      'Billie Holiday', 'Jim Hall', 'Sarah Vaughan',
                      ]'''

    jazz_giant =['Bill Evans']

    for name in jazz_giant:
        update_config(config_path=config_file, key=key, value=name + ' ' + 'vinyl')

        print("執行 Ebay.py 取得data...")
        subprocess.run([python_exe, py1])

        print("執行 DataCleaning.py 來整理數據並生成 Excel...")
        subprocess.run([python_exe, py2])

        print("執行 CreateTableau.py 來基於Tableau模板進行複製...")
        subprocess.run([python_exe, py3])

if __name__ == "__main__":

    main()
