import requests
from pathlib import Path
import time
import json

class Parse5ka:

    headers = {
        'Accept': 'application/json',
        'User-Agent': 'Mozzila/5.0 (Macintosh; Intel Mac OS 10.16; rv:85.0) Gecko/2010101 Firefox/85.0'
    }

    def __init__(self, start_url:str, products_path:Path):
        self.start_url = start_url
        self.products_path = products_path

    def _get_response(self, url):
        while True:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response
            time.sleep(0.5)

    def run(self):
        for product in self._parse(self.start_url):
            product_path = self.products_path.joinpath(f"{product['id']}.json")
            self._save(product, product_path)

    def _parse(self, url):
        while url:
            response = self._get_response(url)
            data = response.json()
            url = data['next']
            for product in data['results']:
                yield  product

    @staticmethod
    def _save(data: dict, file_path):
        file_path.write_text(json.dumps(data, ensure_ascii=False), encoding='UTF-8')

class CatPars (Parse5ka):

    def __init__(self, cat_url, *args, **kwargs):
        self.cat_url = cat_url
        super().__init__(*args, **kwargs)

    def _get_cat(self) -> list:
        response = self._get_response(self.cat_url)
        data = response.json()
        return data

    def run(self):
        for category in self._get_cat():
            category['products'] = []
            url = f"{self.start_url}?categories={category['parent_group_code']}"
            file_path = self.products_path.joinpath(f"{category['parent_group_code']}.json")
            category['products'].extend(list(self._parse(url)))
            self._save(category, file_path)

def get_dir_path(dirname) -> Path:
    dir_path = Path(__file__).parent.joinpath(dirname)
    if not dir_path.exists():
        dir_path.mkdir()
    return  dir_path


if __name__ == '__main__':
    url = "https://5ka.ru/api/v2/special_offers/"
    product_path = get_dir_path('products')
    cat_path = get_dir_path('categories')
    cat_url = 'https://5ka.ru/api/v2/categories/'
    parser = Parse5ka(url, product_path)
    cat_parser = CatPars(cat_url, url, cat_path)
    cat_parser.run()










