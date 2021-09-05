
import streamlit as st
st.set_page_config(layout="wide")

import pandas as pd
import sys
import copy
import re
import numpy as np
import glob
import itertools
site_package_path = glob.glob("/home/*/my_repos/mygithubrepos/vacation-projects/recipes/recipes/lib/python3.8/site-packages")[0]
sys.path.append(site_package_path)
from pymongo import MongoClient, collation
from pymongo.errors import ConnectionFailure

with open(glob.glob('/home/*/*/*/mymongo')[0]) as f:
    pass_key = f.read()
pass_key=pass_key.strip('\n')


# connect to the database as a user name with read-only privilege. Protecting myself from myself here.
user_name = 'ze_readOnly'
client = MongoClient()
try:
    client = MongoClient(username=user_name, password=pass_key)
    st.write('Server available, you are authenticated as user %s.'%(user_name))

except ConnectionFailure:
    st.write("Server not available")

db = client.allrecipes    
collection = db.recipes
     

# for parsing the collection data
def append_value(dict_obj, key, value):
    return [dict_obj[k].append(v) for k,v in zip(key,value)]


# append all dicts of recipes 
reciped = {'_id': [], 'title': [], 'Author': [], 'ingredient': [], 'direction': [], 
           'nutrition_per_serving': [], 'total_ratings': [], 
           'ratings': [], 'prep': [], 'cook': [], 'additional': [], 
           'total': [], 'Servings': [], 'Yield': []
          }

keys = list(reciped.keys())
for recipe in collection.find({"Author": 'MakeItHealthy'}):
    if recipe.get('nutrition_per_serving'):  # <<--- this is because there are recipes (43 currently) that have no nutirtion info 
       values = [recipe.get(k) for k in keys]
       append_value(reciped,keys,values)

# create a pandas data frame
allkeys = list(reciped.keys())
df = pd.DataFrame([reciped[k] for k in keys]).T
df.columns = allkeys
# working on a copy is always safer with mutable data sturcutres  like pandas data frames
dff = copy.deepcopy(df)

def fun_int(nut):
    # takes a list, nut
    # extracts the numeric parts of nut units
    # returns  nut values and units
    nut_names = [name for name in nut[::2]]
    values = []
    units = []
    for n in nut:
        try:
            value = '.'.join(re.findall(r'\d+',n))
            values.append(float(value))

            if isinstance (float(value), float):
                unit = n.strip(value)
                unit = unit.strip('.')
                units.append(unit)
        except ValueError:
            pass
        
    return nut_names, values, units 

# As noted above some columns are made of lists. Need the  nutrition_per_serving in particular and going to flesh the data out from inside the lists
nut_list = list(itertools.chain(*dff['nutrition_per_serving'])) # gets a list out of data frame
# creating dictionaries 
Nut_names = []
Values = []
Units = []
ObjId = []
nunml=[]    
for nuts,objid in zip(nut_list,df['_id']):

    nut = nuts.replace(';','')
    nut = nut.split(' ')
    nut[0], nut[1] = nut[1], nut[0]
    nut_names,values, units = fun_int(nut)
    Nut_names.append(nut_names)
    Values.append(values)
    Units.append(units)
    # if len(nut_names) < 5:
    #     nunml.append(len(nut_names))
    ObjId.append([str(objid)]*len(nut_names))

# creating a dataframe of just nutirents ( call it dnut)
# The goal is to create a multiindex data frame with food id as top level, and nutrient names under it.
# Obviously there are more nutiernts in each recipe than I scraped, but it is ok for now to work with what we have 
arrays = [ np.array(list(itertools.chain(*ObjId))),
          np.array(list(itertools.chain(*Nut_names)))]
dnut = pd.DataFrame({
                     'nut_value':list(itertools.chain(*Values)), 
                     'nut_unit': list(itertools.chain(*Units)),
                    },index = arrays)
dnut = dnut.astype({'nut_value': 'float64'}).T

# parameters collected from various sources including USDA, https://www.healthline.com/health/high-cholesterol/rda, and https://www.acefitness.org/education-and-resources/professional/expert-articles/5904/how-to-determine-the-best-macronutrient-ratio-for-your-goals/
CARB = np.array([.45, .65])  # calorie fraction from carbohydrate 
PRO = np.array([.1,.35])    # calorie fraction from protien
FAT = np.array([.2, .35])   # calorie fraction from fat
CHOL = np.array([5.5, 6.5]) # This corresponds to min and max of cholesterol ([11000/2000, 13000/2000])  mg/cal min and max of cholesterol 
SOD = np.array([1, 2])    # min and max of Sodium

# Pretend we are food experts... and rate food. Ignore food that does not have fat, protien,carbs and sodium for simpilfying task
# This might be what they call feature engineering.
# need to cache this function as it is the slowest
# @st.cache 
def food_rater(dff):
    df = copy.deepcopy(dff)

    LIST1 = list(np.sort(['sodium', 'carbohydrates', 'protein', 'fat']))
    LIST2 = list(np.sort(list(set(['fat', 'protein', 'sodium', 'carbohydrates']).intersection(set(df.columns))))) 

    if LIST1 == LIST2:
                                                          
        if 'cholesterol' not in df:
            tot_cal = 4.0*df['carbohydrates'].get('nut_value') +4.0*df['protein'].get('nut_value') + 9.0*df['fat'].get('nut_value') 
            Xcarb = 4.0*df['carbohydrates'].get('nut_value')/tot_cal
            Xpro = 4.0*df['protein'].get('nut_value')/tot_cal
            Xfat = 9.0*df['fat'].get('nut_value')/tot_cal
            Xsod = df['sodium'].get('nut_value')/tot_cal
            Xchol = 'NA'
        else:
            tot_cal = 4.0*df['carbohydrates'].get('nut_value') +4.0*df['protein'].get('nut_value') + 9.0*df['fat'].get('nut_value') +0.009*df['cholesterol'].get('nut_value') 
                    # assuming unit is mg and cholestrol is still fat with 9 cal/gram cal source
            Xcarb = 4.0*df['carbohydrates'].get('nut_value')/tot_cal
            Xpro = 4.0*df['protein'].get('nut_value')/tot_cal
            Xfat = 9.0*df['fat'].get('nut_value')/tot_cal
            Xsod = df['sodium'].get('nut_value')/tot_cal
            Xchol = df['cholesterol'].get('nut_value')/tot_cal

            if Xchol <= CHOL[0]:
                df.loc['nut_value','cholesterol_level'] = 'low'
            elif Xchol >= CHOL[1]:
                df.loc['nut_value','cholesterol_level'] = 'high'
            else:
                df.loc['nut_value','cholesterol_level'] = 'normal'  
    else:
        tot_cal = np.nan 
        Xcarb = 'NA'
        Xpro = 'NA'
        Xfat = 'NA'
        Xsod = 'NA'
        Xchol = 'NA'

        
        
    if Xcarb != 'NA':  

        if Xcarb  <= CARB[0]:
            df.loc['nut_value','carbohydrates_level'] = 'low'
            df.loc['nut_value','carbohydrates_score'] = 1
        elif Xcarb >= CARB[1]:
            df.loc['nut_value','carbohydrates_level'] = 'high'
            df.loc['nut_value','carbohydrates_score'] = 0
        else:
            df.loc['nut_value','carbohydrates_level'] = 'normal' 
            df.loc['nut_value','carbohydrates_score'] = 2
    else:
            df.loc['nut_value','carbohydrates_level'] = np.nan 
            df.loc['nut_value','carbohydrates_score'] = np.nan
    
    if Xpro != 'NA':  

        if Xpro  <= PRO[0]:
            df.loc['nut_value','protien_level'] = 'low'
            df.loc['nut_value','protien_score'] = 1
        elif Xpro >= PRO[1]:
            df.loc['nut_value','protien_level'] = 'high'
            df.loc['nut_value','protien_score'] = 0
        else:
            df.loc['nut_value','protien_level'] = 'normal' 
            df.loc['nut_value','protien_score'] = 2
    else:
            df.loc['nut_value','protien_level'] = np.nan 
            df.loc['nut_value','protien_score'] = np.nan


    if Xfat != 'NA':    
        
        if Xfat  <= FAT[0]:
            df.loc['nut_value','fat_level'] = 'low'
            df.loc['nut_value','fat_score'] = 1
        elif Xfat >= FAT[1]:
            df.loc['nut_value','fat_level'] = 'high'
            df.loc['nut_value','fat_score'] = 0
        else:
            df.loc['nut_value','fat_level'] = 'normal'
            df.loc['nut_value','fat_score'] = 2
    else:
            df.loc['nut_value','fat_level'] = np.nan
            df.loc['nut_value','fat_score'] = np.nan
        
    if Xsod != 'NA':
        if Xsod <= 1: 
            df.loc['nut_value','sodium_level'] = 'good' 
            df.loc['nut_value','sodium_score'] = 2
        elif Xsod >= SOD[0] and Xsod <=SOD[1]:
            df.loc['nut_value','sodium_level'] = 'normal' 
            df.loc['nut_value','sodium_score'] = 1
        else:  
            df.loc['nut_value','sodium_level'] = 'bad' 
            df.loc['nut_value','sodium_score'] = 0
    else:
        df.loc['nut_value','sodium_level'] = np.nan 
        df.loc['nut_value','sodium_score'] = np.nan

    tot_score = df.fillna(0).loc['nut_value',['_score' in col for col in  df.columns]].sum()
    if tot_score in [0,2]:
        df['overall_food_quality'] = 'bad'
    elif tot_score in [3,4]:
        df['overall_food_quality'] = 'good'
    else:
        df['overall_food_quality'] = 'excellent'
    return df


# Now rate food based on nutrient composition. Note that the food id is appended to each food so we can trace back to it later on
# from functools import lru_cache
# @lru_cache(maxsize=32)
def rate_(dff):
    food=pd.DataFrame()
    for ids in dff['_id'].values:
        try:
            tot_cal = food_rater(dnut.get(str(ids)))
            tot_cal['food_id'] = ids
            food = food.append(tot_cal)
        except AttributeError:
            pass
    return food

food = rate_(dff)



# recipe_name = [doc['title']  if 'title' in doc.keys() else 'NA' for doc in collection.find() ] 
# prep_times = [doc['prep']  if 'prep' in doc.keys() else 'NA' for doc in collection.find()] 
# author = [doc['Author']  if 'Author' in doc.keys() else 'NA' for doc in collection.find() ] 
# servings = [doc['Servings']  if 'Servings' in doc.keys() else 'NA' for doc in collection.find() ]
# additional = [doc['additional']  if 'additional' in doc.keys() else 'NA' for doc in collection.find()]
# cooking_time = [doc['cook']  if 'cook' in doc.keys() else 'NA' for doc in collection.find()]
# direction = [doc['direction']  if 'direction' in doc.keys() else 'NA' for doc in collection.find() ]
# ingredient = [doc['ingredient']  if 'ingredient' in doc.keys() else 'NA' for doc in collection.find() ]
# nutrition_per_serving = [doc['nutrition_per_serving']  if 'nutrition_per_serving' in doc.keys() else 'NA' for doc in collection.find() ] 
# ratings = [doc['ratings']  if 'ratings' in doc.keys() else 'NA' for doc in collection.find() ] 
# ratings_1 = [int(dic["1"]) for dic in ratings if dic]
# ratings_2 = [int(dic["2"]) for dic in ratings if dic]
# ratings_3 = [int(dic["3"]) for dic in ratings if dic]
# ratings_4 = [int(dic["4"]) for dic in ratings if dic]
# ratings_5 = [int(dic["5"]) for dic in ratings if dic]
# total     = [doc['total']  if 'total' in doc.keys() else 'NA' for doc in collection.find() ]
# total_ratings = [doc['total_ratings'] if 'total_ratings' in doc.keys() else 'NA' for doc in collection.find()]



# colnames = ["recipe_name","prep_time","author","servings","cooking_time",
# "1star_rating_count","2star_rating_count","3star_rating_count","4star_rating_count","5star_rating_count",
# "total_cooking_time","total_ratings_count","ingredients","nutrition_per_serving","additional_info"]

# data = [recipe_name,prep_times,author,servings,cooking_time,ratings_1,ratings_2,ratings_3,
#     ratings_4,ratings_5,total,total_ratings,
#     ingredient,nutrition_per_serving,additional]

 
# # data = map(lambda *xx: list(xx), *data)
# # data = np.array(data)
# # data = data.T
# # data = data.tolist()
# df = pd.DataFrame(data).T

# df.columns = colnames
food.food_id = food.food_id.astype('str')
st.write(food.loc['nut_value'].head())