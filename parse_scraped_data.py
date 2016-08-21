import os
import re
import csv
import json
import locale
import collections

base_dir = "/Users/sundeepblue/movie"
locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' ) 


def parse_facebook_likes_number(num_likes_string):
    # eg: "8.5K" --> "85000"
    if not num_likes_string:
        return 0
    size = len(num_likes_string)
    if num_likes_string[-1] == 'K' and num_likes_string[ : size-1].isdigit():
        return int(float(num_likes_string[ : size - 1]) * 1000)
    elif num_likes_string.isdigit():
        return int(num_likes_string)
    else: 
        return 0

def parse_price(price):
    # eg: u'$237,000,000' --> 237000000
    if not price:
        return 0
    return locale.atoi(re.sub('[^0-9,]', "", price))

def parse_duration(duration_string):
    if not duration_string:
        return 0

    #n = re.findall('[0-9,]+', duration_string)
    if "min" in duration_string:
        if "h" in duration_string: # eg: "2h 49min"
            s = duration_string.split("h")
            hours = int(s[0])
            if len(s) > 1: # has minute number
                if "min" in s[1]:
                    minutes = int(s[1].strip().split("min")[0])
                else:
                    minutes = 0
            else:
                minutes = 0
            return 60 * hours + minutes
        else: # eg: "169 min"
            return int(duration_string.split('min')[0])
    else:
        if "h" in duration_string: # eg: "2h"
            return int(duration_string.split('h')[0].strip()) * 60
        else:
            return None

def remove_non_ascii_chars_in_string(s):
    # eg: u'Avatar\xa0' ---> u'Avatar'
    return re.sub(r'[^\x00-\x7F]+','', s) 

def load_unparsed_movie_metadata():
    try:
        with open(os.path.join(base_dir, "imdb_output.json"), "r") as f:
            movies = json.load(f)
            return movies
    except:
        print "Cannot load the unparsed movie metadata file!"
        return None

def load_poster_and_facenumber_pair():
    try:
        with open(os.path.join(base_dir, "image_and_facenumber_pair_list.json"), "r") as f:
            poster_facenumber_pairs = json.load(f)
            return poster_facenumber_pairs
    except:
        print "Cannot load the image vs facenumber pair json file!"
        return None

def generate_posterid_facenumber_dict():
    posterid_facenumber_pairs = load_poster_and_facenumber_pair()
    if not posterid_facenumber_pairs:
        return None
    posterid_facenumber_dict = {}
    for p in posterid_facenumber_pairs:
        poster_id = p['image_id']
        facenumber = p['num_faces']
        posterid_facenumber_dict[poster_id] = facenumber
    return posterid_facenumber_dict

def parse_genres(genres):
    if not genres:
        return None
    return "|".join([g.strip() for g in sorted(genres)])

def parse_plot_keywords(words):
    if not words:
        return None
    return "|".join([w.strip() for w in sorted(words)])   

def parse_aspect_ratio(ratio_string):
    if not ratio_string:
        return None
    if ":" in ratio_string:
        return float(ratio_string.split(":")[0].strip())
    else:
        return float(re.search('[0-9,.]+', ratio_string).group())

def parse_one_movie_metadata(movie, posterid_facenumber_dict):
    if not movie:
        return None

    parsed_movie = {}

    parsed_movie['movie_imdb_link'] = movie['movie_imdb_link']
    parsed_movie['movie_title'] = movie['movie_title'].encode('utf-8')
    parsed_movie['num_voted_users'] = movie['num_voted_users']
    parsed_movie['plot_keywords'] = parse_plot_keywords(movie['plot_keywords'])
    parsed_movie['num_user_for_reviews'] = movie['num_user_for_reviews']
    parsed_movie['language'] = None if movie['language'] is None or len(movie['language']) == 0 else movie['language'][0] # choose the first language
    parsed_movie['country'] = None if movie['country'] is None or len(movie['country']) == 0 else movie['country'][0] # choose 1st country
    parsed_movie['genres'] = parse_genres(movie['genres'])
    parsed_movie['color'] = None if movie['color'] is None or len(movie['color']) == 0 else movie['color'][0]
    parsed_movie['gross'] = None if movie['gross'] is None or len(movie['gross']) == 0 else parse_price(movie['gross'][0].strip())
    parsed_movie['content_rating'] = None if movie['content_rating'] is None or len(movie['content_rating']) == 0 else movie['content_rating'][0].strip()
    parsed_movie['budget'] = None if movie['budget'] is None or len(movie['budget']) == 0 else parse_price(movie['budget'][0].strip())
    parsed_movie['title_year'] = None if movie['title_year'] is None else int(movie['title_year'])
    parsed_movie['movie_facebook_likes'] = parse_facebook_likes_number(movie['num_facebook_like'])
    #parsed_movie['storyline'] = movie['storyline'].strip().encode('utf-8')
    parsed_movie['imdb_score'] = float(movie['imdb_score'][0].strip())
    parsed_movie['aspect_ratio'] = parse_aspect_ratio(movie['aspect_ratio'])
    # get number of human faces in movie poster
    if not posterid_facenumber_dict:
        arsed_movie['facenumber_in_poster'] = None
    else:
        if not movie['images']:
            parsed_movie['facenumber_in_poster'] = None
        else:
            poster_id = movie['images'][0]['path'].split('/')[1].split('.')[0]
            facenumber_in_poster = posterid_facenumber_dict[poster_id]
            parsed_movie['facenumber_in_poster'] = facenumber_in_poster

    num_critic_for_reviews = movie['num_critic_for_reviews']
    parsed_movie['num_critic_for_reviews'] = None if num_critic_for_reviews is None else num_critic_for_reviews

    # parse movie duration
    duration = movie['duration']
    if not duration:
        parsed_movie['duration'] = None
    else:
        if len(duration) == 1:
            parsed_movie['duration'] = parse_duration(duration[0].strip())
        else:
            parsed_movie['duration'] = parse_duration(duration[-1].strip())

    # get cast's total facebook likes (all actors and actress listed in movie's main page)
    cast_info = movie['cast_info']
    cast_total_facebook_likes = 0
    for actor in cast_info:
        _num = actor['actor_facebook_likes']
        if not _num:
            continue
        num = parse_facebook_likes_number(_num)
        cast_total_facebook_likes += num
    parsed_movie['cast_total_facebook_likes'] = cast_total_facebook_likes

    # get top k actors/actress based on their facebook likes
    sorted_casts_by_popularity = sorted(cast_info, key=lambda k: parse_facebook_likes_number(k['actor_facebook_likes']), reverse=True)
    top_k = 3
    # let's extract top k actors
    for k in range(top_k):
        _key_of_actor_name = "actor_{}_name".format(k+1)
        _key_of_facebook_likes = "actor_{}_facebook_likes".format(k+1)
        if k < len(sorted_casts_by_popularity):
            parsed_movie[_key_of_actor_name] = sorted_casts_by_popularity[k]['actor_name'].encode('utf-8')
            parsed_movie[_key_of_facebook_likes] = parse_facebook_likes_number(sorted_casts_by_popularity[k]['actor_facebook_likes'])
        else:
            parsed_movie[_key_of_actor_name] = None
            parsed_movie[_key_of_facebook_likes] = None
    
    # parse director info
    director_info = movie['director_info']
    if not director_info:
        parsed_movie['director_name'] = None
        parsed_movie['director_facebook_likes'] = None
    else:
        parsed_movie['director_name'] = director_info['director_name'].encode('utf-8')
        parsed_movie['director_facebook_likes'] = parse_facebook_likes_number(director_info['director_facebook_likes'])

    return parsed_movie

def parse_all_movies():
    movies = load_unparsed_movie_metadata()
    total_count = len(movies)
    print "{} movie metadata were loaded!".format(total_count)
    posterid_facenumber_dict = generate_posterid_facenumber_dict()

    with open("movie_metadata.csv", "w") as f:
        header_was_written = False
        for i, movie in enumerate(movies):
            print "Processing {} of {}: {}".format(i+1, total_count, movie['movie_imdb_link'])
            parsed_movie = parse_one_movie_metadata(movie, posterid_facenumber_dict)
            w = csv.DictWriter(f, parsed_movie.keys()) 
            if not header_was_written:
                w.writeheader()
                header_was_written = True

            w.writerow(parsed_movie)
    
parse_all_movies()

