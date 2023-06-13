import requests
import time
import openai
import logging
import json

def get_products_with_category(language, api_key, api_secret, ToDo_category_id, done_cat_id, limit=250):
    # Initialize the page
    page = 1
    all_products = []
    
    while True:
        # Get products
        response = requests.get(
            f'https://{api_key}:{api_secret}@api.webshopapp.com/{language}/catalog.json',
            params={'limit': limit, 'page': page}
        )
        logging.info(f'Getting catalog page {page}')
        # Check if request was successful
        if response.status_code == 200:
            data = response.json()
            
            # Filter products by category
            products = [
                product for product in data['products']
                if str(ToDo_category_id) in product['categories']
                if str(done_cat_id) not in product['categories']
            ]
            
            all_products.extend(products)
            
            # Check if there are more pages
            if len(data['products']) < limit:
                break
            
            # Increment the page
            page += 1
            
            # Sleep to avoid hitting rate limit
            time.sleep(1)
            
        else:
            logging.info(f"Failed to fetch products. Status code: {response.status_code}")
            break

    return all_products


def get_products_with_diff(language, matched_products_shopsync, shop_credentials, primary_shop_credentials, limit=250):
    api_key = shop_credentials['fields'].get('api_key')
    api_secret = shop_credentials['fields'].get('api_secret')

    api_key_primary = primary_shop_credentials['fields'].get('api_key')
    api_secret_primary = primary_shop_credentials['fields'].get('api_secret')

    # Define the dict to store products with differences
    duplicate_content = []

    for index, product in matched_products_shopsync.iterrows():
        product_id_primary = product['product_id_primary']
        product_id_secondary = product['product_id_secondary']

        # Request product details from primary
        response_primary = requests.get(f'https://{api_key_primary}:{api_secret_primary}@api.webshopapp.com/{language}/catalog/{product_id_primary}.json')
        if response_primary.status_code == 200:
            product_primary = response_primary.json()['product']
        else:
            continue  # Skip to the next product if the request was not successful

        # Request product details from secondary
        response_secondary = requests.get(f'https://{api_key}:{api_secret}@api.webshopapp.com/{language}/catalog/{product_id_secondary}.json')
        if response_secondary.status_code == 200:
            product_secondary = response_secondary.json()['product']
        else:
            continue  # Skip to the next product if the request was not successful

        content_primary = product_primary.get('content')
        content_secondary = product_secondary.get('content')

        # Check conditions: ignore if content is empty in both or identical in both
        if not content_primary and not content_secondary:
            continue
        elif content_primary != content_secondary:
            continue

        # If the content is duplicate, store the response from the catalog
        if content_primary == content_secondary:
            duplicate_content.append(product_secondary)

    return duplicate_content


# Function to get titles from a dictionary with a certain depth
def get_titles_with_depth(data, depth,category_id):
    titles = set()
    
    def traverse_dict(dict_data, current_depth):
        if isinstance(dict_data, dict):
            for key, value in dict_data.items():
                if current_depth == depth:
                    if 'title' in value and 'id' in value and value['id'] != category_id:
                        title = value['title']
                        titles.add(title)
                else:
                    traverse_dict(value, current_depth + 1)
    
    traverse_dict(data, 1)
    return list(titles)

# Function to generate content based on user input
def generate_content_from_input(prompt):
    generated_text = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1024,
        n=1,
            stop=None,
            temperature=0.9,
        ).choices[0].text
    return generated_text


def update_product(api_key,api_secret, language, product_id, content):
    #create payload

    payload = {
        "product": {
            "content": content
        }
    }
    # Update the product

    url = f'https://{api_key}:{api_secret}@api.webshopapp.com/{language}/products/{product_id}.json'

    # Throttle requests to one per second
    time.sleep(1)

    response = requests.request("PUT", url, json=payload)

    return response