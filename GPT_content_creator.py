import requests
import time
import os
import openai
from utils import get_products_with_category, get_titles_with_depth, generate_content_from_input
from pyairtable import Table
from pyairtable.formulas import match
from dotenv import load_dotenv
import sys
import json
import logging

load_dotenv()
airtable_key = os.getenv("KEYSTORE_KEY")
airtable_base = os.getenv("KEYSTORE_APP")

# Set API keys for ChatGPT
openai.api_key = os.getenv("OPENAI_KEY")

# The argument is accessible through the sys.argv list
client = sys.argv[1] if len(sys.argv) > 1 else None

with open(f'/home/matser/Dev/GPT_app/{client}/config.json', "r") as file:
    # Read the contents of the file
    file_contents = file.read()

    # Parse the file contents as JSON
    config_file = json.loads(file_contents)

#set up variables from config file
shopID = config_file['CLIENTS'][client]['PRIMARY']['ID']
language = config_file['CLIENTS'][client]['PRIMARY']['LANGUAGE'][0]
gpt_service = config_file['CLIENTS'][client]['services'][0]
prompt = gpt_service['properties']['prompt']
ToDo_category_id = gpt_service['properties']['ToDo_category_id']
done_cat_id = gpt_service['properties']['done_cat_id']

# Logging configuration
logging.basicConfig(
    filename=f'/home/matser/Dev/GPT_app/{client}/gpt_script.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logging.info(f'started run')

# get api keys from airtable
airtable = Table(airtable_key, airtable_base, "AppInstalls")
formula = match({"AppName": 'GPT_Content', "shop_id": shopID})
record = airtable.first(formula=formula)

if record:
    # store those here
    api_key = record['fields'].get('api_key')
    api_secret = record['fields'].get('api_secret')

    # Get products
    response = get_products_with_category(client, api_key, api_secret, ToDo_category_id, done_cat_id)

    for product in response:

        product_name = product['title']
        product_id = product['id']
        if gpt_service['properties']['use_brand']:
            try:
                brand_id = product['brand']['id']
                brand = product['brand']['title']
                brand_url = f'https://{api_key}:{api_secret}@api.webshopapp.com/nl/brands/{brand_id}.json'
                brand_response = requests.request("GET", brand_url)
                brand_data = brand_response.json()
                brand_content = brand_data['brand']['content']
            except TypeError:
                logging.info(f'No brand set for {product_id}')
                gpt_service['properties']['use_brand'] = False

        main_cat = get_titles_with_depth(product['categories'], 1, ToDo_category_id)

        logging.info(f"Processing product: {product_name} | Main category: {main_cat}")

        if gpt_service['properties']['use_brand']:
            prompt = prompt.format(product_name=product_name, main_cat=main_cat, brand=brand, brand_content=brand_content)
        else:
            prompt = prompt.format(product_name=product_name, main_cat=main_cat, brand="skip the brand part in this case")

        # Generate content based on user input
        generated_content = generate_content_from_input(prompt)

        payload = {
            "product": {
                "content": generated_content
            }
        }

        payload_cat = {
            "categoriesProduct": {
                "category": done_cat_id,
                "product": product_id
            }
        }

        url = f'https://{api_key}:{api_secret}@api.webshopapp.com/nl/products/{product_id}.json'

        # Throttle requests to one per second
        time.sleep(1)

        response = requests.request("PUT", url, json=payload)

        if response.ok:
            logging.info(f"updated content for product: {product_id}") 

            url_cat = f'https://{api_key}:{api_secret}@api.webshopapp.com/nl/categories/products.json'
            
            # Throttle requests to one per second
            time.sleep(1)

            response = requests.request("POST", url_cat, json=payload_cat)

            if response.ok:

                logging.info(f"Processed product: {product_id} | Main category: {main_cat}")
            else:
                logging.error(f"issue with cat_product: {product_id} | Main category: {main_cat}, {response.text}")
        else:
            logging.error(f"issue with put product: {product_id} | Main category: {main_cat}, {response.text}")

else:
    logging.warning(f"No record found for shopID: {shopID}")
