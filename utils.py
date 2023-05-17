import requests
import time
import openai


def get_products_with_category(api_key, api_secret, ToDo_category_id, done_cat_id, limit=250):
    # Initialize the page
    page = 1
    all_products = []
    
    while True:
        # Get products
        response = requests.get(
            f'https://{api_key}:{api_secret}@api.webshopapp.com/nl/catalog.json',
            params={'limit': limit, 'page': page}
        )
        
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
            print(f"Failed to fetch products. Status code: {response.status_code}")
            break

    return all_products


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