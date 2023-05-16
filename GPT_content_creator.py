import requests
import openai
import os
from dotenv import load_dotenv

load_dotenv()
Airtable_key = os.getenv("KEYSTORE_KEY_OD")
Airtable_app = os.getenv("KEYSTORE_APP")

# Set API keys for ChatGPT and webshop
openai.api_key = os.getenv("OPENAI_KEY")


airtable_table = "AppInstalls"
column1 = "{AppName}= "
column2 = "{shop_id}= "
filter1 = f"{column1} 'GPT_App'"
filter2 = f"{column2}'{shopID}'"


r = airtable_api.request(
    "GET",
    airtable_table,
    params={"filterByFormula": f"AND({filter1}, {filter2})"},
)
if not r.ok:
    with open("app/yotpo/webhooklog.log", "a") as f:
        f.write(
            f"{now} webhook zonder app geinstalleerd shop = {shopID}\n {filter1} {filter2}"
                )

# Vul hier je eigen API-sleutel, API-geheim en cluster in
api_key = "d8fd1b1b3c39848bf30bfe406e5f1768"
api_secret = "f65b972fbd59f64cf3d3bf0256b07220"
cluster = "webshopapp"


# Function to generate content based on user input
def generate_content_from_input(data):
    prompt = f"Schrijf een uitgebreide product tekst voor de webshop bedshop.nl en maakt hierin gebruik van alle gegevens uit deze json data {data}"
    generated_text = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.8,
    ).choices[0].text
    return generated_text

#get product
response = requests.get(f'https://{api_key}:{api_secret}@api.{cluster}.com/nl/catalog/142627199.json')

# Example usage of the functions
data = response.text

#keywords = ["Geschikt voor in/outdoor", "Eenvoudig in onderhoud" , "Gemaakt van duurzame materialen" , "Weersbestendig"]


# Generate content based on user input
generated_content = generate_content_from_input(data)

print(generated_content)
