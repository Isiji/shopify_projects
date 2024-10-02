import requests
import pandas as pd

API_URL = "https://blazemu.myshopify.com/admin/api/2024-01"
ACCESS_TOKEN = "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"  # Use the access token you acquired

file_path = "sku_prices.csv"  # Path to the CSV file with SKU and New Price columns

# Loads the CSV file with SKU and New Price columns
def load_csv(file_path):
    data = pd.read_csv(file_path)
    return data


def get_product_by_sku(sku):
    # Find product variant by SKU
    headers = {
        "X-Shopify-Access-Token": ACCESS_TOKEN
    }

    # Use the search parameter to filter by SKU
    print(f"Searching for SKU: {sku}")
    response = requests.get(f"{API_URL}/products.json?fields=id,title,variants&limit=250", headers=headers)

    if response.status_code != 200:
        print(f"Error fetching products: {response.status_code}")
        print(f"Response: {response.text}")
        return None

    products = response.json().get('products', [])

    print(f"Found {len(products)} products")

    for product in products:
        for variant in product.get('variants', []):
            print(f"Checking variant with SKU: {variant['sku']}")
            if variant['sku'] == sku:
                print(f"Found matching variant: {variant['id']}")
                return variant
    print(f"SKU {sku} not found.")
    return None

def update_variant_price(variant_id, current_price, new_price):
    # Skip if the current price is the same as the new price
    if float(current_price) == float(new_price):
        print(f"Price for variant {variant_id} is already {current_price}. Skipping update.")
        return True  # Consider this a successful skip

    # Update the price of the variant
    headers = {
        "X-Shopify-Access-Token": ACCESS_TOKEN,
        "Content-Type": "application/json"
    }
    data = {
        "variant": {
            "id": variant_id,
            "price": str(new_price)
        }
    }
    response = requests.put(f"{API_URL}/variants/{variant_id}.json", json=data, headers=headers)

    if response.status_code == 200:
        print(f"Successfully updated variant {variant_id} to {new_price}")
        return True
    else:
        print(f"Failed to update variant {variant_id}. Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def update_prices_from_csv(file_path):
    data = load_csv(file_path)
    for _, row in data.iterrows():
        sku = row['SKU']
        new_price = row['New Price']

        # Find product variant by SKU
        variant = get_product_by_sku(sku)
        if variant:
            current_price = variant.get('price')
            variant_id = variant.get('id')
            success = update_variant_price(variant_id, current_price, new_price)
            if success:
                print(f"Processed {sku} - Price: {current_price} -> {new_price}")
            else:
                print(f"Failed to update price for {sku}")
        else:
            print(f"SKU {sku} not found.")

# Example usage: update_prices_from_csv("sku_prices.csv")
update_prices_from_csv(file_path)
