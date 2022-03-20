import requests
import pandas as pd
import json

url = "https://api.covid19api.com/summary"
response = requests.request("GET", url)
data = json.loads(response.text)
df_global = pd.json_normalize(data)
df_countries = pd.json_normalize(data["Countries"])
print(df_global.head())
print(df_countries.head())