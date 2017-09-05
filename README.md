.===================================================================================
# Predict IMDB movie rating

    by Chuan Sun (sundeepblue at gmail dot com)
    
    https://twitter.com/sundeepblue
    
    Scrapy project @ NYC Data Science Academy
    
    8/14/2016


===================================================================================
# STEP 1: 

Fetch a list of 5000 movie titles and budgets from www.the-numbers.com

This step will generate a JSON file 'movie_budget.json'

$ scrapy crawl movie_budget -o movie_budget.json


===================================================================================
# STEP 2: 

Load 5000+ movie titles from the JSON file 'movie_budget.json'

Then search those titles from IMDB website to get the real IMDB movie links

It will generate a JSON file 'fetch_imdb_url.json' containing movie-link pairs

$ scrapy crawl fetch_imdb_url -o fetch_imdb_url.json


===================================================================================
# STEP 3: 

Scrape 5000+ IMDB movie information

This step will load the JSON file 'fetch_imdb_url.json', go into each movie page, and grab data

This step will generate a JSON file 'imdb_output.json' (20M) containing detailed info of 5000+ movies

It will also download all available posters for all movies.

A total of 4907 posters can be downloaded (998MB). Note that I am not sure if I can upload all those posters into github,
so I only uploaded a few. You can see from my code how to use scrapy to grab them all. 

$ scrapy crawl imdb -o imdb_output.json


===================================================================================
# STEP 4: 

Perform face recognition to count face numbers from all posters

This step will save result into JSON file 'image_and_facenumber_pair_list.json'

$ python detect_faces_from_posters.py

===================================================================================
# STEP 5: 

Load two JSON files 'imdb_output.json' and 'image_and_facenumber_pair_list.json'

Parse all variables into valid format.

Generate a final CSV table containing 28 variables that can be loaded in R or Pandas

The output will be a CSV file 'movie_metadata.csv' (1.5MB)

"movie_title"   
"color"                     
"num_critic_for_reviews"   
"movie_facebook_likes" 
"duration"                  
"director_name"  
"director_facebook_likes"  
"actor_3_name" 
"actor_3_facebook_likes"    
"actor_2_name"           
"actor_2_facebook_likes"   
"actor_1_name" 
"actor_1_facebook_likes"    
"gross"                     
"genres"                   
"num_voted_users"           
"cast_total_facebook_likes" 
"facenumber_in_poster"      
"plot_keywords"             
"movie_imdb_link"           
"num_user_for_reviews"      
"language"                 
"country"                   
"content_rating"            
"budget"                    
"title_year"                   
"imdb_score"                
"aspect_ratio"              

$ python parse_scraped_data.py


===================================================================================
# STEP 6:

Load the 'movie_metadata.csv' file in RStudio, and perform EDA and LASSO regression

$ > run the RStudio

$ > load the file 'movie_rating_prediction.R'
