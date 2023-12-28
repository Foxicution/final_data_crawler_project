from .crawler_objects import PlotEstateCrawler, ApartmentEstateCrawler, HouseEstateCrawler
from typing import Any, Callable, Literal

def crawl_real_estate( search_text, time_limit):
    crawler = PlotEstateCrawler(search_text, time_limit)
    crawled_data=crawler.get_search_results()
    crawler.close_driver()
    return crawled_data

if __name__ == "__main__":
    data_found = crawl_real_estate(search_text="kaune", time_limit=15)
    print(data_found)