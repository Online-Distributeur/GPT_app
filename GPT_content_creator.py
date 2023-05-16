import requests
import openai
import os
from dotenv import load_dotenv

load_dotenv()
Airtable_key = os.getenv("KEYSTORE_KEY_OD")
Airtable_app = os.getenv("KEYSTORE_APP")

# Set API keys for ChatGPT and webshop
openai.api_key = os.getenv("OPENAI_KEY")

shopID = #default = 273092" else = UserInput


airtable_table = "AppInstalls"
column1 = "{AppName}= "
column2 = "{shop_id}= "
filter1 = f"{column1} 'GPT_App'"
filter2 = f"{column2}'{shopID}'"

#get the data from Airtable API
response = airtable_api.request(
    "GET",
    airtable_table,
    params={"filterByFormula": f"AND({filter1}, {filter2})"},
)

## in the response fields there should be a value "api_key" and a value "api_secret"


# store those here
api_key = respnse.api_key
api_secret = respnse.api_secret
cluster = "webshopapp"

prompt = " default text here and user input"

# Function to generate content based on user input
def generate_content_from_input(data):
    prompt = prompt
    generated_text = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.9,
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
