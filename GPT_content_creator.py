import requests
import time
import os
import openai
from utils import get_products_with_category, get_titles_with_depth, generate_content_from_input
from pyairtable import Table
from pyairtable.formulas import match
from dotenv import load_dotenv
import logging

load_dotenv()
airtable_key = os.getenv("KEYSTORE_KEY")
airtable_base = os.getenv("KEYSTORE_APP")

# Set API keys for ChatGPT
openai.api_key = os.getenv("OPENAI_KEY")

# Set variables
shopID = 273092
write_to = "Lightspeed_API"

# Logging configuration
logging.basicConfig(filename='script.log', level=logging.INFO)

if write_to == "Lightspeed_API":
    ToDo_category_id = 11977379
    done_cat_id = 11962437

airtable = Table(airtable_key, airtable_base, "AppInstalls")
formula = match({"AppName": 'GPT_Content', "shop_id": shopID})
record = airtable.first(formula=formula)

if record:
    # store those here
    api_key = record['fields'].get('api_key')
    api_secret = record['fields'].get('api_secret')

    # Get products
    response = get_products_with_category(api_key, api_secret, ToDo_category_id, done_cat_id)

    for product in response:

        product_name = product['title']
        product_id = product['id']

        main_cat = get_titles_with_depth(product['categories'], 1, ToDo_category_id)

        logging.info(f"Processing product: {product_name} | Main category: {main_cat}")

        prompt = f"Je bent de copywriter voor de webshop Vloerkledenopvinyl en je wil de beste beschrijving van een product maken. Het doel van de beschrijving is goed scoren bij Google, maar het is ook belangrijk dat de klanten die dit lezen enthousiast worden van het product. Webshop Vloerkledenopvinyl maakt unieke vloerkleden, placemats, keukenlopers en inductiebeschermers gemaakt van vinyl. De producten worden allemaal in een eigen werkplaats in Nederland gemaakt van gerecycled polyester. Unieke eigenschappen van vinyl zijn een lange levensduur, slijtvast en makkelijk schoon te maken. Schrijf een unieke productbeschrijving van min. 600 en max. 800 tekens voor webshop Vloerkledenopvinyl in HTML-formaat en verwerk daarin het volgende: 1. Artikel is: {product_name} 2. Productcategorie: {main_cat} 3. Toon: informerend en overtuigend 4. Voeg na de unieke productbeschrijving van max. 800 karakters de volgende lijst in bulletpoints toe in HTML-formaat: Specificaties: - Slijtvast - Onverwoestbaar - Geschikt voor binnen en buiten - Hygiënisch - Makkelijk te reinigen - Vochtbestendig - Kleurvast - Brandveilig - Makkelijk oprolbaar"

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

        url_cat = f'https://{api_key}:{api_secret}@api.webshopapp.com/nl/categories/products.json'

        # Throttle requests to one per second
        time.sleep(1)

        response = requests.request("POST", url_cat, json=payload_cat)

        logging.info(f"Processed product: {product_id} | Main category: {main_cat}")

else:
    logging.warning(f"No record found for shopID: {shopID}")
