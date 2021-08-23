import scrapy
import itertools
from scrapy.selector import Selector

import pandas as pd

import glob

# files = ["appetizers-and-snacks-file-0_urls.csv","appetizers-and-snacks-file-1_urls.csv" ,
# "appetizers-and-snacks-file-2_urls.csv","appetizers-and-snacks-file-3_urls.csv" ,
# "appetizers-and-snacks-file-4_urls.csv","appetizers-and-snacks-file-5_urls.csv",
# "appetizers-and-snacks-file-6_urls.csv","appetizers-and-snacks-file-7_urls.csv" ,
# "breakfast-and-brunch-file-0_urls.csv","smoothies-file-0_urls.csv" ,
# "smoothies-file-1_urls.csv","smoothies-file-2_urls.csv","smoothies-file-3_urls.csv" ,
# "smoothies-file-4_urls.csv","smoothies-file-5_urls.csv","smoothies-file-6_urls.csv",
# "smoothies-file-7_urls.csv","smoothies-file-8_urls.csv",
# "smoothies-file-9_urls.csv","smoothies-file-10_urls.csv","smoothies-file-11_urls.csv",
# "smoothies-file-12_urls.csv","smoothies-file-13_urls.csv", "dessert_urls.csv"]

# for file in files:
#     # read urls scrapped using Selenium
#     filename = glob.glob(f'/home/*/*/*/*/recipes/data/{file}')
#     df = pd.read_csv(filename[0] , sep=",", engine='python', skiprows= 0, error_bad_lines=False)
#     urls = [list(df[name]) for name in df] # make lists out of the df
#     urls = list(itertools.chain(*urls)) # merge lists
#     urls = list(filter(None, urls)) # remove NoneType values from list

# df = pd.read_csv('/home/zelalem/my_repos/mygithubrepos/vacation-projects/recipes/dessert_urls.csv', sep=",", engine='python', skiprows= 0, error_bad_lines=False) 
# urls = [list(df[name]) for name in df] # make lists out of the df
# urls = list(itertools.chain(*urls)) # merge lists
# urls = list(filter(None, urls)) # remove NoneType values from list
filename = glob.glob(f'/home/*/*/*/*/recipes/data/all_recipe_urls.csv')
durl = pd.read_csv(filename[0] , sep=",", engine='python', skiprows= 0, error_bad_lines=False)
urls_from_df = [list(durl[name]) for name in durl]
urls = list(itertools.chain(*urls_from_df))


class AllrecipesSpider(scrapy.Spider):
    name = 'allrecipes'
    allowed_domains = ['www.allrecipes.com']
    start_urls = urls  

    def parse(self, response):
        
        headers = response.css("div.recipe-meta-item-header::text").getall()
        bodies = response.css("div.recipe-meta-item-body::text").getall()
        metadict = {f'{head}'.strip(":"): body for head, body in zip(headers,bodies)}


        steps = response.xpath("//span[@class='checkbox-list-text']/text()").extract()
        directions= response.xpath("//div[@class='paragraph']/p/text()").extract()
        cooking_instruction = list(itertools.zip_longest(steps,directions))
        nutrition_info = response.xpath("//div[@class='partial recipe-nutrition-section']/div[@class='section-body']/text()").extract()
        nutrition_info  = [x.strip() for x in nutrition_info if x.strip()]
        tot_ratings = response.xpath("//div[@class='recipe-ratings-list']/span[@class='ratings-count']/text()").extract()
        tot_ratings = list(set(tot_ratings))
        stars = ['5', '4', '3', '2','1']

        star_counts = response.xpath("//div[@class='recipe-ratings-list']//span[@class='rating-count']/text()").extract()
        star_counts = star_counts[0:5]
        star_breakdown = {f'{s}': int(sc) for s, sc in zip(stars,star_counts)}
        # nutrient_name = response.xpath("//div[@class='nutrition-row']//span[@class='nutrient-name']/text()").extract()
        # nutrient_name = [x.strip() for x in nutrient_name if x.strip()]
        # nutrient_value = response.xpath("//div[@class='nutrition-row']//span[@class='nutrient-value']/text()").extract()
        # daily_value = response.xpath("//div[@class='nutrition-row']//span[@class='daily-value']/text()").extract()
        # daily_values = {name [nutrient_value, daily_value] for name, n_value,d_value in itertools.zip_longest(nutrient_name, nutrient_value, daily_value)}

        maindict = {
                    'title': response.css("h1.headline::text").get(),
                    'Author': response.css("span.author-name::text").get(),
                    'ingredient': response.css("span.ingredients-item-name::text").getall(),
                    'direction': cooking_instruction,
                    'nutrition_per_serving': nutrition_info, 
                    'total_ratings': tot_ratings,
                    'ratings': star_breakdown,
                    }
        maindict.update(metadict)

        yield maindict

        
    
