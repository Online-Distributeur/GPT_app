import requests
import time
import os
import openai
from utils import get_products_with_category, get_titles_with_depth, generate_content_from_input, get_products_with_diff, update_product
from pyairtable import Table
from pyairtable.formulas import match
from dotenv import load_dotenv
import sys
import json
import logging
import pandas as pd

load_dotenv()
airtable_key = os.getenv("KEYSTORE_KEY")
airtable_base = os.getenv("KEYSTORE_APP")

# Set API keys for ChatGPT
openai.api_key = os.getenv("OPENAI_KEY")

# The argument is accessible through the sys.argv list
client = sys.argv[1] if len(sys.argv) > 1 else None

with open(f'{client}/config.json', "r") as file:
    # Read the contents of the file
    file_contents = file.read()

    # Parse the file contents as JSON
    config_file = json.loads(file_contents)

#set up variables from config file
shopID = config_file['CLIENTS'][client]['PRIMARY']['ID']
languages = config_file['CLIENTS'][client]['PRIMARY']['LANGUAGE']
gpt_service = config_file['CLIENTS'][client]['services'][0]
use_shopsync = gpt_service['properties']['use_shopsync']
translate_to = gpt_service['properties']['translate_to']
shopsync_client = gpt_service['properties']['shopsync_client']

ToDo_category_id = gpt_service['properties']['ToDo_category_id']
done_cat_id = gpt_service['properties']['done_cat_id']

current_directory = os.getcwd() 

# Logging configuration
logging.basicConfig(
    filename=f'{current_directory}/{client}/gpt_script.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logging.info(f'started run')

# get api keys from airtable
airtable = Table(airtable_key, airtable_base, "AppInstalls")
formula = match({"AppName": 'GPT_Content', "shop_id": shopID})
shop_credentials = airtable.first(formula=formula)

if use_shopsync:
    shopsync_folder = gpt_service['properties']['shopsync_folder']
    # Define the file path
    shopsync_config_file = f'{shopsync_folder}/{shopsync_client}/config.json'
    with open(shopsync_config_file, "r") as file:
        # Read the contents of the file
        file_contents = file.read()

        # Parse the file contents as JSON
        shopsync_config_file = json.loads(file_contents)
    shop_id_primary = shopsync_config_file['CLIENTS'][shopsync_client]['PRIMARY']['ID']

    # Read the CSV data
    file_path = f'{shopsync_folder}/{shopsync_client}/{shopsync_client}_merged_no_duplicates.csv'

    matched_products_shopsync = pd.read_csv(file_path)

    # Get the primary shop credentials
    primary_shop_credentials = airtable.first(formula=match({"AppName": 'GPT_Content', "shop_id": shop_id_primary}))

    if not primary_shop_credentials:
        logging.error(f"No record found for shopID: {shop_id_primary}")
        exit()

    # store those here
    api_key_primary = primary_shop_credentials['fields'].get('api_key')
    api_secret_primary = primary_shop_credentials['fields'].get('api_secret')

if not shop_credentials:
    logging.error(f"No record found for shopID: {shopID}")
    exit()

# store those here
api_key = shop_credentials['fields'].get('api_key')
api_secret = shop_credentials['fields'].get('api_secret')

for language in languages:

    prompt_input = gpt_service['properties']['prompt'][language]

    logging.info(f"Processing language: {language}")

    if use_shopsync:
        # Get products
        response = get_products_with_diff(language, matched_products_shopsync, shop_credentials, primary_shop_credentials)

    else:
        # Get products
        response = get_products_with_category(language, api_key, api_secret, ToDo_category_id, done_cat_id)

    for product in response:

        product_name = product['title']
        product_id = product['id']
        product_content = product['content']
        if gpt_service['properties']['use_brand']:
            try:
                brand_id = product['brand']['id']
                brand = product['brand']['title']
                brand_url = f'https://{api_key}:{api_secret}@api.webshopapp.com/{language}/brands/{brand_id}.json'
                brand_response = requests.request("GET", brand_url)
                brand_data = brand_response.json()
                brand_content = brand_data['brand']['content']
            except TypeError:
                logging.info(f'No brand set for {product_id}')
                continue

        if use_shopsync:
            main_cat = ""
            logging.info(f"Processing product: {product_name} | Has duplicated content")
        else:
            main_cat = get_titles_with_depth(product['categories'], 1, ToDo_category_id)
            logging.info(f"Processing product: {product_name} | Main category: {main_cat}")
        

        if gpt_service['properties']['use_brand']:
            prompt = prompt_input.format(product_name=product_name, main_cat=main_cat, brand=brand, brand_content=brand_content)

        elif use_shopsync:
            prompt = prompt_input.format(product_content=product_content)
        
        else:
            prompt = prompt_input.format(product_name=product_name, main_cat=main_cat)
            
        generated_content = generate_content_from_input(prompt)

        response = update_product(api_key, api_secret, language, product_id, generated_content)

        if response.ok:
            logging.info(f"updated content for product: {product_id}") 

            if use_shopsync:
                continue

            if translate_to:

                for lang in translate_to:

                    if lang == "de":
                        taal = "Duits"

                    if lang == "fr":
                        taal = "Frans"

                    promt = f'Vertaal deze tekst naar {taal}: {generated_content}'
                    translated_content = generate_content_from_input(prompt)

                    response_trans = update_product(api_key, api_secret, lang, product_id, translated_content)

                    if response_trans.ok:
                        logging.info(f"translated content for product: {product_id}") 

                    else:
                        logging.info((f"translated content for product: {product_id} failed in language {lang}") )

            # add product to done category
            logging.info(f"adding product to done category: {product_id}")
            payload_cat = {
                "categoriesProduct": {
                    "category": done_cat_id,
                    "product": product_id
                }
                    }
                
            url_cat = f'https://{api_key}:{api_secret}@api.webshopapp.com/{language}/categories/products.json'
            
            # Throttle requests to one per second
            time.sleep(1)

            response = requests.request("POST", url_cat, json=payload_cat)

            if response.ok:

                logging.info(f"Processed product: {product_id} | Main category: {main_cat} and with prompt: {prompt}")
            else:
                logging.error(f"issue with cat_product: {product_id} | Main category: {main_cat}, {response.text}")
        else:
            logging.error(f"issue with put product: {product_id} | Main category: {main_cat}, {response.text}")

logging.info(f'finished run')

