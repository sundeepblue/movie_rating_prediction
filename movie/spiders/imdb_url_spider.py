# -*- coding: utf-8 -*-
import scrapy
import json
import urllib2
from scrapy.selector import Selector
from movie.items import ImdbUrlItem

# shell command to run:
# $ scrapy crawl fetch_imdb_url -o fetch_imdb_url.json

class ImdbSearchUrlProvider():
    def __init__(self):
        pass

    def prepare_imdb_title_search_urls(self):
        with open("movie_budget.json", "r") as f:
            movies = json.load(f)

        urls = []
        for m in movies:
            title = m['movie_name']
            title_for_url = urllib2.quote(title.encode('utf-8'))
            imdb_search_link = "http://www.imdb.com/find?ref_=nv_sr_fn&q={}&s=tt".format(title_for_url)
            urls.append(imdb_search_link)

        return urls


class ImdbUrlSpider(scrapy.Spider):
    name = "fetch_imdb_url"
    allowed_domains = ["imdb.com"]
    start_urls = ImdbSearchUrlProvider().prepare_imdb_title_search_urls()

    def parse(self, response):
        item = ImdbUrlItem()

        # get the href and title of the first returned movie from the search result page
        first_returned_movie_href = response.xpath("//table[@class='findList']/tr/td[@class='result_text']/a/@href").extract()[0]
        full_imdb_url = "http://www.imdb.com" + first_returned_movie_href

        item['movie_name'] = response.xpath("//table[@class='findList']/tr/td[@class='result_text']/a/text()").extract()[0]
        item['movie_imdb_link'] = full_imdb_url

        yield item
