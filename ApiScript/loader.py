from dotenv import load_dotenv
import os
import csv
import requests
import random
import xml.etree.ElementTree as ET
from http import HTTPStatus
from requests.auth import HTTPBasicAuth
from html import escape
import re
import xml.sax.saxutils as saxutils

load_dotenv()

PRESTASHOP_URL = os.getenv("PRESTASHOP_URL")
API_KEY = os.getenv("API_KEY")

CATEGORIES_URL = PRESTASHOP_URL + '/categories'
PRODUCTS_URL = PRESTASHOP_URL + '/products'
PRODUCTS_IMAGES_URL = PRESTASHOP_URL + '/images/products'
STOCK_AVAILABLE_URL = PRESTASHOP_URL + '/stock_availables'
IMAGES_FOLDER = 'images'
POST_HEADERS = {'Content-Type': 'application/xml; charset=UTF-8'}

HOME_CATEGORY_ID = 2
DEFAULT_QUANTITY = 9


def clean_category_name(name):
    return name.replace('\xa0', ' ').strip()


def load_category(category_name, parent_id):
    category_xml = f"""
    <prestashop xmlns:xlink="http://www.w3.org/1999/xlink">
        <category>
            <id_parent><![CDATA[{parent_id}]]></id_parent>
            <active><![CDATA[1]]></active>
            <name>
                <language id="2"><![CDATA[{category_name}]]></language>
            </name>
            <link_rewrite>
                <language id="2"><![CDATA[{category_name.lower().replace(' ', '-')}]]></language>
            </link_rewrite>
        </category>
    </prestashop>
    """

    response = requests.post(CATEGORIES_URL, auth=(API_KEY, ''), headers=POST_HEADERS,
                             data=category_xml.encode('utf-8'), verify=False)

    if response.status_code == HTTPStatus.CREATED:
        tree = ET.ElementTree(ET.fromstring(response.text))
        root = tree.getroot()
        category_id_element = root.find(".//id")

        category_id = category_id_element.text.strip()
        return int(category_id)
    else:
        print(response.status_code)
        return None


def load_categories(csv_file):
    with open(csv_file, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        categories_ids = []
        for row in csv_reader:
            category_name = row['name']
            category_name = clean_category_name(category_name)
            category_id = load_category(category_name, HOME_CATEGORY_ID)
            if category_id is not None:
                categories_ids.append({'name': category_name, 'id': category_id})
    return categories_ids


def load_subcategories(csv_file, categories_data):
    with open(csv_file, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        subcategories_id_list = []
        for row in csv_reader:
            subcategory_name = row['name']
            subcategory_name = clean_category_name(subcategory_name)
            parent_category_name = row['parent_category']
            parent_category_name = clean_category_name(parent_category_name)
            parent_category_id = HOME_CATEGORY_ID
            for category in categories_data:
                if category['name'] == parent_category_name:
                    parent_category_id = category['id']
                    break
            subcategory_id = load_category(subcategory_name, parent_category_id)
            if subcategory_id is not None:
                subcategories_id_list.append({'name': row['name'], 'id': subcategory_id, 'parent_category_id': parent_category_id})
    return subcategories_id_list


def generate_product_weight():
    return round(random.uniform(0.1, 60), 2)


def get_stock(product_id):
    response = requests.get(f"{STOCK_AVAILABLE_URL}?filter[id_product]={product_id}", auth=(API_KEY, ''), verify=False)
    if response.status_code == 200:
        root = ET.fromstring(response.content)
        stock_ids = [node.attrib['id'] for node in root.findall(".//stock_available")]
        return stock_ids[0] if stock_ids else None
    else:
        raise Exception(f"Error fetching stock ID: {response.content}")


def set_stock(stock_id, quantity):
    response = requests.get(f"{STOCK_AVAILABLE_URL}/{stock_id}", auth=(API_KEY, ''), verify=False)
    if response.status_code == HTTPStatus.OK:
        stock_data = ET.fromstring(response.content)
        for node in stock_data.findall(".//quantity"):
            node.text = str(quantity)

        update_response = requests.put(f"{STOCK_AVAILABLE_URL}/{stock_id}", auth=(API_KEY, ''), data=ET.tostring(stock_data),
            headers=POST_HEADERS, verify=False
        )

        if update_response.status_code in [200, 204]:
            print(f"Stock updated, ID = {stock_id}")
        else:
            raise Exception(f"Error updating stock: {update_response.content}")
    else:
        raise Exception(f"Error fetching stock data: {response.content}")


def fix_price(price_string):
    # Remove the currency symbols and commas
    price_string = price_string.replace("€", "").replace("¥", "").replace("US$", "").replace("£", "").strip()
    # Replace commas with dots for decimal handling
    price_string = price_string.replace(' ', '').replace(",", ".")
    # Convert to float and calculate the netto price by dividing by 1.23
    netto_price = round(float(price_string) / 1.23, 6)
    return netto_price


def upload_product_images(product_id, product_name, miniature_image, big_image):

    def upload_image(image_file_name, is_cover=False):

        image_path = os.path.join(IMAGES_FOLDER, image_file_name)
        if not os.path.exists(image_path):
            print(f"Error: Image file '{image_file_name}' for product '{miniature_image}' image '{image_file_name}' not found.")
            return False

        with open(image_path, 'rb') as image_file:
            files = {
                'image': (image_file_name, image_file, 'image/jpeg'),
            }
            params = {'id_product': product_id}
            if is_cover:
                params['is_cover'] = '1'

            response = requests.post(
                f"{PRODUCTS_IMAGES_URL}/{product_id}", files=files, params=params, auth=HTTPBasicAuth(API_KEY, ''), verify=False
            )

            if response.status_code == HTTPStatus.CREATED:
                print(f"Image '{image_file_name}' uploaded successfully for product '{product_name}'.")
                return True
            else:
                print(f"Failed to upload image '{image_file_name}' for product '{product_name}'. "
                      f"Status code: {response.status_code}, Response: {response.text}")
                return False

    # Upload the miniature image as the cover
    if not upload_image(miniature_image, is_cover=True):
        print(f"Failed to upload the miniature image '{miniature_image}' for product '{product_name}'.")

    # Upload the big image
    if not upload_image(big_image):
        print(f"Failed to upload the big image '{big_image}' for product '{product_name}'.")


def clean_invalid_xml_chars(data):
    invalid_xml_chars = re.compile(r'[\x00-\x08\x0B\x0C\x0E-\x1F]')
    return re.sub(invalid_xml_chars, '', data)


def escape_xml(data):
    return saxutils.escape(data)


def load_products(csv_file, subcategories_id_list):
    subcategories_mapping = {item['name']: item for item in subcategories_id_list}
    with open(csv_file, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            product_name = row['name']
            product_price = fix_price(row['price'])
            product_weight = generate_product_weight()
            product_description = row['description'] if row['description'] is not None else "Default description"
            product_description_cleaned = escape(product_description)
            sanitized_description = escape_xml(clean_invalid_xml_chars(product_description))
            product_subcategory_name = row['subcategory']
            miniature = row['miniature']
            big_image = row['big_image']
            subcategory_data = subcategories_mapping.get(product_subcategory_name)
            if not subcategory_data:
                print(f"Warning: Subcategory '{product_subcategory_name}' not found. Skipping product.")
                continue

            subcategory_id = subcategory_data['id']
            parent_category_id = subcategory_data['parent_category_id']
            product_xml = f"""
                <prestashop xmlns:xlink="http://www.w3.org/1999/xlink">
                    <product>
                        <id_category_default>{subcategory_id}</id_category_default>
                        <id_tax_rules_group>1</id_tax_rules_group>
                        <price><![CDATA[{product_price}]]></price>
                        <new>0</new>
                        <id_shop_default>1</id_shop_default>
                        <weight><![CDATA[{product_weight}]]></weight>
                        <available_for_order>1</available_for_order>
                        <minimal_quantity>1</minimal_quantity>
                        <active>1</active>
                        <show_price>1</show_price>            
                        <state>1</state>
                        <name>
                           <language id="2"><![CDATA[{product_name}]]></language>
                        </name>
                        <description>
                           <language id="2">{sanitized_description}</language>
                        </description>
                        <associations>
                            <categories>
                                <category>
                                    <id>2</id> <!-- Home category -->
                                </category>
                                <category>
                                    <id>{parent_category_id}</id> <!-- Parent category -->
                                </category>
                                <category>
                                    <id>{subcategory_id}</id> <!-- Subcategory -->
                                </category>
                            </categories>
                        </associations>
                    </product>                             
                </prestashop>
            """
            response = requests.post(PRODUCTS_URL, auth=(API_KEY, ''), headers=POST_HEADERS,
                                     data=product_xml.encode('utf-8'), verify=False)

            if response.status_code == HTTPStatus.CREATED:
                print("Product added")
            else:
                print(f"Product load error: {response.status_code}, Response: {response.text}")
                return

            tree = ET.ElementTree(ET.fromstring(response.text))
            root = tree.getroot()
            product_id_element = root.find(".//id")
            product_id = product_id_element.text.strip()

            set_stock(get_stock(product_id), DEFAULT_QUANTITY)
            upload_product_images(product_id, product_name, miniature, big_image)
                        

if __name__ == "__main__":
    csv_categories = "categories.csv"
    csv_subcategories = "subcategories.csv"
    csv_products = "products.csv"
    categories_ids = load_categories(csv_categories)
    subcategories_ids = load_subcategories(csv_subcategories, categories_ids)
    load_products(csv_products, subcategories_ids)
    print(categories_ids)
    print(subcategories_ids)
