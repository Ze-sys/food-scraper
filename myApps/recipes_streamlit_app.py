import streamlit as st
import pandas as pd
from pymongo import MongoClient
st.set_page_config(layout="wide")


client = MongoClient('localhost',27017)
database = client.allrecipes
# print('List of collections in the database allrecipes: ', database.list_collection_names())

collection = database['recipes']
# x = collection.find()
# print(f'...in the collection, {collection}:\n')

recipe_name = [doc['title']  if 'title' in doc.keys() else 'NA' for doc in collection.find() ] 
prep_times = [doc['prep']  if 'prep' in doc.keys() else 'NA' for doc in collection.find()] 
author = [doc['Author']  if 'Author' in doc.keys() else 'NA' for doc in collection.find() ] 
servings = [doc['Servings']  if 'Servings' in doc.keys() else 'NA' for doc in collection.find() ]
additional = [doc['additional']  if 'additional' in doc.keys() else 'NA' for doc in collection.find()]
cooking_time = [doc['cook']  if 'cook' in doc.keys() else 'NA' for doc in collection.find()]
direction = [doc['direction']  if 'direction' in doc.keys() else 'NA' for doc in collection.find() ]
ingredient = [doc['ingredient']  if 'ingredient' in doc.keys() else 'NA' for doc in collection.find() ]
nutrition_per_serving = [doc['nutrition_per_serving']  if 'nutrition_per_serving' in doc.keys() else 'NA' for doc in collection.find() ] 
ratings = [doc['ratings']  if 'ratings' in doc.keys() else 'NA' for doc in collection.find() ] 
ratings_1 = [int(dic["1"]) for dic in ratings if dic]
ratings_2 = [int(dic["2"]) for dic in ratings if dic]
ratings_3 = [int(dic["3"]) for dic in ratings if dic]
ratings_4 = [int(dic["4"]) for dic in ratings if dic]
ratings_5 = [int(dic["5"]) for dic in ratings if dic]
total     = [doc['total']  if 'total' in doc.keys() else 'NA' for doc in collection.find() ]
total_ratings = [doc['total_ratings'] if 'total_ratings' in doc.keys() else 'NA' for doc in collection.find()]



colnames = ["recipe_name","prep_time","author","servings","cooking_time",
"1star_rating_count","2star_rating_count","3star_rating_count","4star_rating_count","5star_rating_count",
"total_cooking_time","total_ratings_count","ingredients","nutrition_per_serving","additional_info"]

data = [recipe_name,prep_times,author,servings,cooking_time,ratings_1,ratings_2,ratings_3,
    ratings_4,ratings_5,total,total_ratings,
    ingredient,nutrition_per_serving,additional]

 
# data = map(lambda *xx: list(xx), *data)
# data = np.array(data)
# data = data.T
# data = data.tolist()
df = pd.DataFrame(data).T

df.columns = colnames
st.write(df)