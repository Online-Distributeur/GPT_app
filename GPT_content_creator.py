import os
import openai
from utils import get_products_with_category, get_titles_with_depth, generate_content_from_input
from pyairtable import Table
from pyairtable.formulas import match
from dotenv import load_dotenv

load_dotenv()
airtable_key = os.getenv("KEYSTORE_KEY")
airtable_base = os.getenv("KEYSTORE_APP")

# Set API keys for ChatGPT
openai.api_key = os.getenv("OPENAI_KEY")

shopID = 273092
category_id = 11977379
AppName ='GPT_Content'

airtable = Table(airtable_key, airtable_base, "AppInstalls")
formula = match({"AppName": AppName, "shop_id": shopID})
record = airtable.first(formula=formula)


if record:
    # store those here
    api_key = record['fields'].get('api_key')
    api_secret = record['fields'].get('api_secret')

    #get products
    response = get_products_with_category(api_key, api_secret, category_id)

    for product in response:

        product_name = product['title']

        main_cat = get_titles_with_depth(product['categories'], 1, category_id)
        print(main_cat, product_name)

        prompt = f"Je bent de copywriter voor de webshop Vloerkledenopvinyl en je wil de beste beschrijving van een product maken. Het doel van de beschrijving is goed scoren bij Google, maar het is ook belangrijk dat de klanten die dit lezen enthousiast worden van het product. Webshop Vloerkledenopvinyl maakt unieke vloerkleden, placemats, keukenlopers en inductiebeschermers gemaakt van vinyl. De producten worden allemaal in een eigen werkplaats in Nederland gemaakt van gerecycled polyester. Unieke eigenschappen van vinyl zijn een lange levensduur, slijtvast en makkelijk schoon te maken. Schrijf een unieke productbeschrijving van min. 600 en max. 800 tekens voor webshop Vloerkledenopvinyl in HTML-formaat en verwerk daarin het volgende: 1. Artikel is: {product_name} 2. Productcategorie: {main_cat} 3. Toon: informerend en overtuigend 4. Voeg na de unieke productbeschrijving van max. 800 karakters de volgende lijst in bulletpoints toe in HTML-formaat: Specificaties: - Slijtvast - Onverwoestbaar - Geschikt voor binnen en buiten - Hygiënisch - Makkelijk te reinigen - Vochtbestendig - Kleurvast - Brandveilig - Makkelijk oprolbaar"

        # Generate content based on user input
        generated_content = generate_content_from_input(prompt)

        print(generated_content)
else:
    print(f"No record found for shopID: {shopID}")
