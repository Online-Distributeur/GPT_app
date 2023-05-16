import os
import openai
import requests
from airtable import Airtable
from dotenv import load_dotenv

load_dotenv()
Airtable_key = os.getenv("KEYSTORE_KEY_OD")
Airtable_base = os.getenv("KEYSTORE_APP")

# Set API keys for ChatGPT
openai.api_key = os.getenv("OPENAI_KEY")

shopID = # default = 273092" else = UserInput

airtable = Airtable(Airtable_base, 'AppInstalls', api_key=Airtable_key)

# Filter records
records = airtable.search('AppName', 'GPT_App')

# Find record that matches shopID
record = next((record for record in records if record['fields'].get('shop_id') == shopID), None)

if record:
    # store those here
    api_key = record['fields'].get('api_key')
    api_secret = record['fields'].get('api_secret')
    cluster = "webshopapp"

    prompt = " default text here and user input"

    # Function to generate content based on user input
    def generate_content_from_input(data):
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

    # Generate content based on user input
    generated_content = generate_content_from_input(data)

    print(generated_content)
else:
    print(f"No record found for shopID: {shopID}")
