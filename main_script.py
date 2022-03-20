import requests
import pandas as pd
import json
from translate import Translator
from unicodedata import lookup

URL = "https://api.covid19api.com/summary"
TOP_NUMBER_OF_COUTNRIES = 50
TRANSLATE_TO = "russian"
OUTPUT_FILE_NAME = "daily_covid_update.txt"
RECEIVER_NAME = "Инна"

response = requests.request("GET", URL)
data = json.loads(response.text)

df_global = pd.json_normalize(data)  # Global summary
df_countries = pd.json_normalize(data["Countries"])  # Summary per country
print(
    f'The data drawn from the API consists of {df_countries.shape[0]} countries and {df_global.shape[0]} row(s)'
    f' regarding a global summary')

# Sorting TOP countries
df_countries = df_countries.sort_values("NewDeaths", ascending=False).head(TOP_NUMBER_OF_COUTNRIES)

# Translate to Russian
translator = Translator(from_lang="english", to_lang=TRANSLATE_TO)
df_countries["RussianCountry"] = df_countries["Country"].apply(lambda x: translator.translate(x))


# Flags
def create_flag(country_code: str) -> str:
    return lookup(f'REGIONAL INDICATOR SYMBOL LETTER {country_code[0]}') + lookup(
        f'REGIONAL INDICATOR SYMBOL LETTER {country_code[1]}')


df_countries["Flag"] = df_countries["CountryCode"].apply(create_flag)

# Message construction
#     Global stats:
total_infections = format(df_global["Global.TotalConfirmed"][0], ",d")
total_deaths = format(df_global["Global.TotalDeaths"][0], ",d")
message = f"Привет {RECEIVER_NAME}. Во всем мире, Есть {total_infections} случаев COVID-19 " \
          f"и {total_deaths} человек умерли из-за этого.\n" \
          f"Сегодня количество смертей в каждой стране было:\n"

#     Individual countries:
filtered_df = df_countries[["Flag", "RussianCountry", "NewDeaths"]]
for index, row in filtered_df.iterrows():
    message += f'{row["Flag"]} {row["RussianCountry"]}: {format(row["NewDeaths"], ",d")}' + "\n"

# Writing to file
with open(OUTPUT_FILE_NAME, "wb") as f:
    f.write(message.encode('utf8'))
