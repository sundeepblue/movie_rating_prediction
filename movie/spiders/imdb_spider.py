import re
import time
import scrapy
import random
import json
import locale
import urllib2
from bs4 import BeautifulSoup

from movie.items import MovieItem

# shell command to run:
# $ scrapy crawl imdb -o imdb_output.json


class ImdbMovieUrlsProvider():
    def __init__(self):
        pass

    def prepare_movie_urls(self):
        with open("fetch_imdb_url.json", "r") as f:
            movies = json.load(f)
        urls = [m['movie_imdb_link'] for m in movies]
        return urls


class ImdbSpider(scrapy.Spider):
    name = "imdb"
    allowed_domains = ["imdb.com"]
    start_urls = ImdbMovieUrlsProvider().prepare_movie_urls() # there are 5000+ movies

    locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' ) 

    def extract_text(self, xpath, response):
        path = "{}/text()".format(xpath)
        return response.xpath(path).extract()

    def get_facebook_likes(self, entity_type, entity_id):
        # the 'entity_id' could be imdb movie id, or imdb people id
        if entity_type == "person_name_id":
            url = "https://www.facebook.com/widgets/like.php?width=280&show_faces=1&layout=standard&href=http%3A%2F%2Fwww.imdb.com%2Fname%2F{}%2F&colorscheme=light".format(entity_id)
        elif entity_type == "movie_title_id":
            url = "https://www.facebook.com/widgets/like.php?width=280&show_faces=1&layout=standard&href=http%3A%2F%2Fwww.imdb.com%2Ftitle%2F{}%2F&colorscheme=light".format(entity_id)
        else:
            url = None
        time.sleep(random.uniform(0, 0.25)) # randomly snooze a time within [0, 0.4] second
        try:
            content = urllib2.urlopen(url).read()
            soup = BeautifulSoup(content, "lxml")
            sentence = soup.find_all(id="u_0_2")[0].span.string # get sentence like: "43K people like this"
            num_likes = sentence.split(" ")[0]
        except Exception as e:
            num_likes = None
        return num_likes

    def get_movie_id_from_url(self, url):
        # sample imdb movie url: http://www.imdb.com/title/tt0068646/?ref_=nv_sr_1
        # we need to return "tt0068646"
        if url is None:
            return None
        return re.search("(tt[0-9]{7})", url).group()

    def get_person_name_id_from_url(self, url):
        # sample imdb person url: http://www.imdb.com/name/nm0000338/?ref_=tt_ov_dr
        # we need to return "nm0000338"
        if url is None:
            return None
        return re.search("(nm[0-9]{7})", url).group()


    def parse(self, response):
        pass

    def parse(self, response):
        print "*"*100
        item = MovieItem()
        item['movie_imdb_link'] = response.url

        # ---------------------------------------------------------------------------------------------------
        try:
            movie_title = response.xpath('//div[@class="title_wrapper"]/h1/text()').extract()[0]
        except:
            movie_title = None
        item['movie_title'] = movie_title

        # ---------------------------------------------------------------------------------------------------
        try:
            title_year = response.xpath('//*[@id="titleYear"]/a/text()').extract()[0]
        except:
            title_year = None
        item['title_year'] = title_year

        # ---------------------------------------------------------------------------------------------------
        try:
            genres = response.xpath('//div[@itemprop="genre"]//a/text()').extract()
        except:
            genres = None
        item['genres'] = genres

        # ---------------------------------------------------------------------------------------------------
        try:
            country = response.xpath('//div[@id="titleDetails"]/div/a[contains(@href, "country")]/text()').extract()
        except:
            country = None
        item['country'] = country

        # ---------------------------------------------------------------------------------------------------
        try:
            language = response.xpath('//div[@id="titleDetails"]/div/a[contains(@href, "language")]/text()').extract()
        except:
            language = None
        item['language'] = language

        # ---------------------------------------------------------------------------------------------------
        try:
            plot_keywords = response.xpath('//a/span[@itemprop="keywords"]/text()').extract()
        except:
            plot_keywords = None
        item['plot_keywords'] = plot_keywords

        # ---------------------------------------------------------------------------------------------------
        try:
            storyline = response.xpath('//div[@id="titleStoryLine"]/div[@itemprop="description"]/p/text()').extract()[0]
        except:
            storyline = None
        item['storyline'] = storyline

        # ---------------------------------------------------------------------------------------------------
        try:
            color = response.xpath('//a[contains(@href, "colors=")]/text()').extract()
        except:
            color = None
        item['color'] = color

        # ---------------------------------------------------------------------------------------------------
        try:
            budget = response.xpath('//h4[contains(text(), "Budget:")]/following-sibling::node()/descendant-or-self::text()').extract()
        except:
            budget = None
        item['budget'] = budget

        # ---------------------------------------------------------------------------------------------------
        try:
            gross = response.xpath('//h4[contains(text(), "Gross:")]/following-sibling::node()/descendant-or-self::text()').extract()
        except:
            gross = None
        item['gross'] = gross

        # ---------------------------------------------------------------------------------------------------
        try:
            imdb_score = response.xpath("//span[@itemprop='ratingValue']/text()").extract()
        except:
            imdb_score = None
        item['imdb_score'] = imdb_score

        # ---------------------------------------------------------------------------------------------------
        try:
            num_voted_users = response.xpath('//span[@itemprop="ratingCount"]/text()').extract()[0]
        except:
            num_voted_users = None
        item['num_voted_users'] = locale.atoi(num_voted_users)

        # ---------------------------------------------------------------------------------------------------
        try:
            duration = response.xpath('//time[@itemprop="duration"]/text()').extract()
        except:
            duration = None
        item['duration'] = duration

        # ---------------------------------------------------------------------------------------------------
        try:
            aspect_ratio = response.xpath('//h4[contains(text(), "Aspect Ratio:")]/following-sibling::node()/descendant-or-self::text()').extract()
            # preprocess movie aspect ratio.
            ratio = ""
            for s in aspect_ratio:
                s = s.strip()
                if len(s) != 0:
                    ratio = s
                    break
            aspect_ratio = ratio
        except:
            aspect_ratio = None
        
        item['aspect_ratio'] = aspect_ratio

        # ---------------------------------------------------------------------------------------------------
        try:
            content_rating = response.xpath('//meta[@itemprop="contentRating"]/following-sibling::node()/descendant-or-self::text()').extract()
        except:
            content_rating = None
        item['content_rating'] = content_rating

        # ---------------------------------------------------------------------------------------------------
        try:
            num_user_for_reviews = response.xpath('//span/a[contains(@href, "reviews")]/text()').extract()[0]
            # preprocess "num_user_for_reviews". Convert "2,238 user" to number 2238
            num_user_for_reviews = locale.atoi(num_user_for_reviews.split(" ")[0])
        except:
            num_user_for_reviews = None
        item['num_user_for_reviews'] = num_user_for_reviews

        # ---------------------------------------------------------------------------------------------------
        try:
            num_critic_for_reviews = response.xpath('//span/a[contains(@href, "externalreviews")]/text()').extract()[0]
            # preprocess "num_critic_for_reviews". Convert "234 critics" to number 234
            num_critic_for_reviews = locale.atoi(num_critic_for_reviews.split(" ")[0])
        except:
            num_critic_for_reviews = None
        item['num_critic_for_reviews'] = num_critic_for_reviews

        # ---------------------------------------------------------------------------------------------------
        # (1) get names and links of all cast members

        base_url = "http://www.imdb.com"

        try:
            # extract all ODD table rows from the cast list
            cast_name_list_from_odd_rows = response.xpath('//table[@class="cast_list"]/tr[@class="odd"]/td[@class="itemprop"]/a/span[@class="itemprop"]/text()').extract()
            cast_name_href_list_from_odd_rows = response.xpath('//table[@class="cast_list"]/tr[@class="odd"]/td[@class="itemprop"]/a/@href').extract()
            links_from_odd_rows = [base_url + e for e in cast_name_href_list_from_odd_rows]
            pairs_for_odd_rows = zip(cast_name_list_from_odd_rows, links_from_odd_rows)

            # extract all EVEN table rows from the cast list
            cast_name_list_from_even_rows = response.xpath('//table[@class="cast_list"]/tr[@class="even"]/td[@class="itemprop"]/a/span[@class="itemprop"]/text()').extract()
            cast_name_href_list_from_even_rows = response.xpath('//table[@class="cast_list"]/tr[@class="even"]/td[@class="itemprop"]/a/@href').extract()
            links_from_even_rows = [base_url + e for e in cast_name_href_list_from_even_rows]
            pairs_for_even_rows = zip(cast_name_list_from_even_rows, links_from_even_rows)

            # combine the two lists
            cast_name_link_pairs = pairs_for_odd_rows + pairs_for_even_rows

            # convert list of pairs to dictionary
            cast_info = []
            for p in cast_name_link_pairs:
                name, link = p[0], p[1]
                actor = {}
                actor["actor_name"] = name
                actor["actor_link"] = link

                name_id = self.get_person_name_id_from_url(link)
                actor["actor_facebook_likes"] = self.get_facebook_likes(entity_type="person_name_id", entity_id=name_id)

                cast_info.append(actor)
        except:
            cast_info = None
        item['cast_info'] = cast_info

        # ---------------------------------------------------------------------------------------------------
        # (2) get names and links of directors
        try:
            director_name = response.xpath('//span[@itemprop="director"]/a/span/text()').extract()[0]

            director_partial_link = response.xpath('//span[@itemprop="director"]/a/@href').extract()[0]
            director_full_link = base_url + director_partial_link


            director_info = {}
            director_info["director_name"] = director_name
            director_info["director_link"] = director_full_link

            name_id = self.get_person_name_id_from_url(director_full_link)
            director_info["director_facebook_likes"] = self.get_facebook_likes(entity_type="person_name_id", entity_id=name_id)
        except:
            director_info = None
        item['director_info'] = director_info

        # ---------------------------------------------------------------------------------------------------
        movie_id = self.get_movie_id_from_url(response.url)
        num_facebook_like = self.get_facebook_likes(entity_type="movie_title_id", entity_id=movie_id)
        item['num_facebook_like'] = num_facebook_like

        # ---------------------------------------------------------------------------------------------------
        try:
            poster_image_url = response.xpath('//div[@class="poster"]/a/img/@src').extract()[0]

            # a sample image url looks like this:
            #   http://ia.media-imdb.com/images/M/MV5BMTY5NzY5NTY2NF5BMl5BanBnXkFtZTcwNTg3NzIxNA@@._V1_UX182_CR0,0,182,268_AL_.jpg
            # we need to remove trailing characters "UX182_CR0,0,182,268_AL_" to get larger poster with this like:
            #   http://ia.media-imdb.com/images/M/MV5BMTY5NzY5NTY2NF5BMl5BanBnXkFtZTcwNTg3NzIxNA@@._V1_.jpg
            poster_image_url = [ poster_image_url.split("_V1_")[0] + "_V1_.jpg" ]

        except:
            poster_image_url = None
        item['image_urls'] = poster_image_url

        # ---------------------------------------------------------------------------------------------------
        yield item

