from dotenv import load_dotenv
import os
import logging
from tqdm import tqdm
from datetime import datetime
from ebaysdk.exception import ConnectionError
from ebaysdk.finding import Connection
import pandas as pd
from util import load_config, get_config_value, make_folder, setup_logging

class Ebay:
    def __init__(self, api_key, searched_word, data):
        self.api_key = api_key
        self.artist_name = searched_word.replace(" ", "_").rsplit("_", 1)[0]
        self.main_folder = 'data'
        self.artist_folder = os.path.join(self.main_folder, f'data_{self.artist_name}')
        self.data = data

    def fetch(self):
        try:
            api = Connection(appid=self.api_key, config_file=None)
            response = api.execute('findItemsAdvanced', self.data)
            return response

        except ConnectionError as e:
            print(e)
            print(e.response.dict())

    @staticmethod
    def parse(response):
        items_list = []
        for item in response.reply.searchResult.item:
            if hasattr(item, '__dict__'):
                # change it into dict and append in list
                items_list.append(item.__dict__)
        return items_list

    def make_n_save_dataframe(self, data):
        sort_method = self.data['sortOrder']
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y%m%d_%H%M%S")
        file_name = f'ebay_data_{self.artist_name}_{sort_method}_{formatted_time}.xlsx'

        make_folder(self.main_folder)
        make_folder(self.artist_folder)

        file_path = os.path.join(self.artist_folder, file_name)
        df = pd.DataFrame(data)
        df["title"] = df["title"].apply(lambda x: f"'{x}" if x.startswith("=") else x)
        df.to_excel(file_path, index=False)

if __name__ == "__main__":

    # log setup
    setup_logging()

    # load .env
    load_dotenv()
    API_KEY = os.getenv("API_KEY")  # get API_KEY

    # load config.json
    config = load_config("config.json")
    keywords = get_config_value(config, "keywords")
    entry_per_page = get_config_value(config, "entry_per_page") # how many item to get per page
    max_pages = get_config_value(config, "max_pages") # the max is 100

    e = Ebay(API_KEY, keywords, {})

    sort_order = ["BestMatch", "StartTimeNewest"]
    total_api_calls = 0
    for method in sort_order:
        print(f'==========Searching for {keywords}, {method}==========')

        bar_format = "{l_bar}{bar}| {n_fmt}/{total_fmt} {percentage:3.0f}% | " \
                     "剩餘時間: {remaining} | 處理速度: {rate_fmt}"

        PAGE_NUMBER = 1
        final_data = []
        with tqdm(total=max_pages, desc="Processing", unit="Page", ncols=100,
                  bar_format=bar_format) as pbar:
            while PAGE_NUMBER <= max_pages:

                search_filter = {
                    "keywords": str(keywords),
                    "paginationInput": {"pageNumber": str(PAGE_NUMBER), "entriesPerPage": str(entry_per_page)},
                    "sortOrder": str(method)
                }
                e.data = search_filter

                try:
                    to_parse = e.fetch()
                    if to_parse:
                        data_batch = e.parse(to_parse)
                        final_data.extend(data_batch)

                        total_api_calls += 1
                    else:
                        print(f"Empty response on page {PAGE_NUMBER}, skipping...")
                        logging.warning(f"Empty response on page {PAGE_NUMBER}, skipping...")
                except Exception as e:
                    print(f"Error processing page {PAGE_NUMBER}: {e}")
                    logging.error(f"Error processing page {PAGE_NUMBER}: {e}")

                PAGE_NUMBER += 1

                pbar.update(1)

        e.make_n_save_dataframe(final_data)

    logging.info(f"Total API calls made: {total_api_calls}")