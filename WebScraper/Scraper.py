from bs4 import BeautifulSoup
import requests
import csv
import os
import re

BASE_URL = "https://www.nin-nin-game.com/en/"
MAX_PRODUCTS_PER_SUBCATEGORY = 125

categories = []
figures_goodies_subcategories = []
video_games_subcategories = []
trading_cards_subcategories = []
plush_toys_subcategories = []


def replace_restricted_characters(name):
    safe = re.sub(r'[\\/:*?"<>|]', '-', name)
    safe = safe.strip().rstrip('.')
    return safe


def download_image(image_url, file_name):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(image_url, headers=headers, stream=True)
        response.raise_for_status()
        os.makedirs("images", exist_ok=True)
        file_path = os.path.join("images", f"{file_name}.jpg")
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print(f"Image saved as {file_path}")
    except Exception as e:
        print(f"Failed to download image {file_name}: {e}")


def fetch_html(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text


def extract_subcategories(soup, selector, start_idx, end_idx):
    subcategories = []
    subcategory_elements = soup.select(selector)
    for subcategory in subcategory_elements[start_idx:end_idx]:
        name = subcategory.get_text(strip=True)
        link = subcategory.find_parent('a')['href']
        if not link.startswith("http"):
            link = BASE_URL + link.lstrip("/")
        subcategories.append({"name": name, "link": link})
    return subcategories


def extract_products(subcategory_url, max_products):
    products = []
    current_page = 1

    while len(products) < max_products:
        if current_page == 1:
            paginated_url = subcategory_url
        else:
            paginated_url = f"{subcategory_url}?p={current_page}"

        print(f"Fetching page {current_page}: {paginated_url}")
        try:
            subcategory_html = fetch_html(paginated_url)
            subcategory_soup = BeautifulSoup(subcategory_html, 'html.parser')
            product_elements = subcategory_soup.select('li.general_block_card.ajax_block_product.item')

            if not product_elements:
                print("No more products found on this page.")
                break

            for product_element in product_elements:
                try:
                    product_link = product_element.select_one('a')['href']
                    if not product_link.startswith("http"):
                        product_link = BASE_URL + product_link.lstrip("/")
                    name = product_element.select_one('a.product-name')['title']
                    safe_file_name = replace_restricted_characters(name)
                    miniature_image_url = product_element.select_one('img')['src']
                    miniature_file_name = f"{safe_file_name}"
                    download_image(miniature_image_url, miniature_file_name)
                    product_details = extract_product_details(product_link)
                    if product_details:
                        product_details["miniature"] = f"{miniature_file_name}.jpg"
                        products.append(product_details)


                    if len(products) >= max_products:
                        break
                except Exception as e:
                    print(f"Error processing product: {e}")

            current_page += 1
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page {current_page}: {e}")
            break

    return products


def extract_product_details(product_url):
    try:
        product_html = fetch_html(product_url)
        product_soup = BeautifulSoup(product_html, 'html.parser')
        description = product_soup.find('div', class_='rte product-page-tab', id='idTab1')
        name = product_soup.select_one('h1.product-short-desc-title').get_text(strip=True)
        price = product_soup.select_one('.our_price_display span').get_text(strip=True)
        big_image_tag = product_soup.find('img', {'width': '569', 'height': '569'})
        srcset = big_image_tag['srcset']
        big_image_url = srcset.split(',')[0].strip().split(' ')[0]
        big_image_file_name = f"{replace_restricted_characters(name)}_BIG"
        download_image(big_image_url, big_image_file_name)

        return {
            "name": name,
            "description": description,
            "price": price,
            "big_image": f"{big_image_file_name}.jpg"
        }
    except Exception as e:
        print(f"Error extracting product details from {product_url}: {e}")
        return None


def write_to_csv(filename, fieldnames, data):
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for item in data:
            writer.writerow(item)

main_html = fetch_html(BASE_URL)
main_soup = BeautifulSoup(main_html, 'html.parser')
category_elements = main_soup.select('.parentMenu a span')
categories_to_write = []
for category in category_elements[:4]:
    name = category.get_text(strip=True)
    link = category.find_parent('a')['href']
    if not link.startswith("http"):
        link = BASE_URL + link.lstrip("/")
    categories.append({"name": name, "link": link})
    categories_to_write.append({"name": name, "description": "", "parent_id": 0})
write_to_csv("categories.csv", ["name", "description", "parent_id"], categories_to_write)

figures_goodies_subcategories = extract_subcategories(main_soup, '.itemMenu.level4 a span', 25, 27)
video_games_subcategories = extract_subcategories(main_soup, '.itemMenu.level4 a span', 68, 70)
trading_cards_subcategories = extract_subcategories(main_soup, '.itemMenu.level1 a.itemMenuName.level3.nochild span', 0, 2)
plush_toys_subcategories = extract_subcategories(main_soup, '.itemMenu.level1 a.itemMenuName.level3.nochild span', 23, 25)

all_subcategories = [
    {"name": sub["name"], "link": sub["link"], "parent_category": "Figures / Goodies"}
    for sub in figures_goodies_subcategories
] + [
    {"name": sub["name"], "link": sub["link"], "parent_category": "Video games"}
    for sub in video_games_subcategories
] + [
    {"name": sub["name"], "link": sub["link"], "parent_category": "Trading Cards"}
    for sub in trading_cards_subcategories
] + [
    {"name": sub["name"], "link": sub["link"], "parent_category": "Plush toys"}
    for sub in plush_toys_subcategories
]

subcategories_to_write = [
    {"name": sub["name"], "description": "", "parent_category": sub["parent_category"]}
    for sub in all_subcategories
]
write_to_csv(
    "subcategories.csv",
    ["name", "description", "parent_category"],
    subcategories_to_write
)

products_to_write = []

for subcategory in all_subcategories:
    subcategory_name = subcategory["name"]
    subcategory_link = subcategory["link"]

    print(f"Fetching products for subcategory: {subcategory_name}")
    products = extract_products(subcategory_link, max_products=MAX_PRODUCTS_PER_SUBCATEGORY)

    for product in products:
        product["subcategory"] = subcategory_name
        products_to_write.append(product)

write_to_csv(
    "products.csv",
    ["name", "price", "miniature", "big_image", "description", "details", "subcategory"],
    products_to_write
)
print("Products have been written to products.csv.")


