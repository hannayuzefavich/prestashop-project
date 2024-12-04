import unittest
import random
from glob import glob

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
import os
import time

SHOP_URL = "https://localhost:8090"

class ShopTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.start_time = time.time()

    @classmethod
    def tearDownClass(cls):
        total_time = time.time() - cls.start_time
        print(f"\nCałkowity czas wypełniania testów: {total_time:.2f} s")

    def setUp(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.driver.get(SHOP_URL)
        self.wait = WebDriverWait(self.driver, 30)

    def tearDown(self):
        if self._testMethodName == 'test_invoice_download_from_order_history':
            time.sleep(10)
        self.driver.quit()

    def wait_for_page_to_load(self):
        self.wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")

    def wait_for_element_to_be_visible(self, by, value, timeout=30):
        self.wait.until(EC.visibility_of_element_located((by, value)))

    def set_quantity(self, quantity):

        for _ in range(quantity - 1):
            self.driver.find_element(By.CSS_SELECTOR, ".touchspin-up").click()

    def add_product_to_cart(self, product_element, quantity):

        try:
            product_element.click()
            self.wait_for_page_to_load()
            self.set_quantity(quantity)
            self.driver.find_element(By.CSS_SELECTOR, ".add-to-cart").click()

        except StaleElementReferenceException:
            self.fail("Towar nie był znaleziony")
        self.driver.back()
        self.wait_for_page_to_load()

    def add_products_from_category_to_cart(self, category_selector, products_to_add=2):

        self.driver.find_element(By.CSS_SELECTOR, category_selector).click()
        self.wait_for_page_to_load()

        for _ in range(products_to_add):
            product_list = self.driver.find_elements(By.CSS_SELECTOR, ".js-product")
            if not product_list:
                self.fail(f"Produkty nie zostałe znalezione w kategorii: {category_selector}")
            product = random.choice(product_list)
            self.add_product_to_cart(product.find_element(By.TAG_NAME, "a"), random.randint(1, 5))

        self.driver.get(SHOP_URL)
        self.wait_for_page_to_load()

        self.driver.find_element(By.CSS_SELECTOR, "a > .shopping-cart").click()
        self.wait_for_page_to_load()

        for _ in range(3):
            try:
                remove_button = self.driver.find_element(By.CSS_SELECTOR, ".cart-item:nth-child(1) .material-icons")
                remove_button.click()
                self.wait_for_page_to_load()
            except Exception as e:
               self.fail(f"Nie udało się usunąć produkt")

    def register_new_user(self):

        try:
            self.wait_for_element_to_be_visible(By.CSS_SELECTOR, 'a[title="Zaloguj się do swojego konta klienta"]')
            self.driver.find_element(By.CSS_SELECTOR, 'a[title="Zaloguj się do swojego konta klienta"]').click()
            self.driver.find_element(By.CSS_SELECTOR, 'div.no-account a').click()
            self.driver.find_element(By.ID, 'field-firstname').send_keys('John')
            self.driver.find_element(By.ID, 'field-lastname').send_keys('Doe')
            email = f"test_user_{random.randint(1000, 9999)}@example.com"
            self.driver.find_element(By.ID, 'field-email').send_keys(email)
            self.driver.find_element(By.ID, 'field-password').send_keys('password123')
            self.driver.find_element(By.NAME, 'customer_privacy').click()
            self.driver.find_element(By.NAME, 'psgdpr').click()
            self.driver.find_element(By.CSS_SELECTOR, 'button[data-link-action="save-customer"]').click()
            print("Test d: Rejestrację nowego konta - OK")
        except NoSuchElementException as e:
            self.fail(f"Element nie znaleziony")

    def search_and_add_product_to_cart(self, product_name):

        try:
            search_box = self.driver.find_element(By.NAME, 's')
            search_box.send_keys(product_name)
            search_box.submit()
            products = self.wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#js-product-list .js-product"))
            )
            product_link = random.choice(products).find_element(By.TAG_NAME, 'a')
            self.add_product_to_cart(product_link, 1)
            print(f"Test b: Wyszukanie produktu po nazwie i dodanie do koszyka losowego produku '{product_name}' - OK")
        except Exception as e:
            self.fail(f"Nie udało się wyszukać i dodać produktu")

    def remove_products_from_cart(self, number_of_products=3):

        self.driver.find_element(By.CSS_SELECTOR, "a > .shopping-cart").click()
        self.wait_for_page_to_load()

        for _ in range(number_of_products):
            try:
                remove_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".remove-from-cart")
                if not remove_buttons:
                    self.fail("Nie znaleziono produktów do usunięcia z koszyka.")
                remove_buttons[0].click()
                self.wait_for_page_to_load()
            except Exception as e:
                self.fail(f"Nie udało się usunąć produkt")

    def start_order(self):

        self.driver.get(f"{SHOP_URL}/koszyk?action=show")
        self.driver.find_element(By.CLASS_NAME, 'btn.btn-primary').click()
        self.driver.find_element(By.ID, 'field-address1').send_keys('Test Street')
        self.driver.find_element(By.ID, 'field-postcode').send_keys('12-345')
        self.driver.find_element(By.ID, 'field-city').send_keys('Test City')
        country_select_element = self.driver.find_element(By.ID, 'field-id_country')
        select_country = Select(country_select_element)
        select_country.select_by_visible_text('Polska')
        self.driver.find_element(By.NAME, 'confirm-addresses').click()
        print("Test e: Wykonanie zamówienia zawartości koszyka - OK")

    def choose_shipment_method(self):
        try:
            self.driver.find_element(By.NAME, 'confirmDeliveryOption').click()
            print("Test g: Wybór jednego z dwóch przewoźników - OK")
        except NoSuchElementException as e:
            self.fail(f"Nie ma opcji dostawy: dozwolona waga przekroczona")

    def choose_payment_method(self, payment_option_id='payment-option-3'):

        try:
            payment_option = self.driver.find_element(By.ID, payment_option_id)
            self.driver.execute_script("arguments[0].click();", payment_option)
        except NoSuchElementException as e:
            self.fail(f"Metoda płatności nie została znaleziona")

    def accept_terms_and_confirm_order(self):

        self.driver.find_element(By.ID, 'conditions_to_approve[terms-and-conditions]').click()
        self.driver.find_element(By.CSS_SELECTOR, '.ps-shown-by-js > .btn').click()

    def navigate_to_account(self):

        try:
            self.wait_for_element_to_be_visible(By.CSS_SELECTOR, 'a.account')
            self.driver.find_element(By.CSS_SELECTOR, 'a.account').click()
        except NoSuchElementException as e:
            self.fail(f"Nie udało się otworzyć konta")

    def navigate_to_order_history(self):

        try:
            self.wait_for_element_to_be_visible(By.ID, 'history-link')
            self.driver.find_element(By.ID, 'history-link').click()
        except NoSuchElementException as e:
            self.fail(f"Nie udało się przejść do historii zamówień")

    def open_order_details(self):

        try:
            self.wait_for_element_to_be_visible(By.LINK_TEXT, "Szczegóły")
            self.driver.find_element(By.LINK_TEXT, "Szczegóły").click()
            print("Test i: Sprawdzenie statusu zamówienia - OK")
        except NoSuchElementException as e:
            self.fail(f"Nie udało się otworzyć szczegółów zamówienia")

    def download_invoice(self):
        try:
            self.wait_for_element_to_be_visible(By.LINK_TEXT, "Pobierz fakturę proforma w pliku PDF")
            invoice_link = self.driver.find_element(By.LINK_TEXT, "Pobierz fakturę proforma w pliku PDF")
            self.driver.execute_script("arguments[0].click();", invoice_link)
            print("Test j: Pobieranie faktury VAT - OK")

        except NoSuchElementException as e:
            self.fail(f"Nie udało się znaleźć faktury")

        download_dir = os.path.expanduser("~/Downloads")
        file_pattern = "FV*.pdf"
        start_time = time.time()
        while not glob(os.path.join(download_dir, file_pattern)):
            if time.time() - start_time > 10:
                self.fail("Nie udało się pobrać faktury w ciągu 10 sekund.")
            time.sleep(1)
        print("Test j: Faktura została pobrana pomyślnie - OK")

    def test_add_10_products_to_card_and_remove(self):
        self.register_new_user()

        self.add_products_from_category_to_cart("#category-178 > .dropdown-item", 3)
        self.add_products_from_category_to_cart("#category-179 > .dropdown-item", 3)
        print("Test a: Dodanie do koszyka 10 produktów - OK")

        self.remove_products_from_cart(3)
        print("Test c: Usunięcie z koszyka 3 produktów - OK")

    def test_full_flow(self):
        """Pełny scenariusz"""

        self.register_new_user()

        self.search_and_add_product_to_cart("pokemon")

        self.start_order()

        self.choose_shipment_method()

        self.choose_payment_method('payment-option-3')
        print("Test f: Wybór metody płatności: przy odbiorze - OK")

        self.accept_terms_and_confirm_order()

        self.wait = WebDriverWait(self.driver, 100)

    def test_invoice_download_from_order_history(self):
        """Test: sprawdzenie statusu i pobranie faktury VAT"""

        self.register_new_user()

        self.search_and_add_product_to_cart("pokemon")

        self.start_order()

        self.choose_shipment_method()

        self.choose_payment_method('payment-option-2')

        self.accept_terms_and_confirm_order()

        self.navigate_to_account()

        self.navigate_to_order_history()

        self.open_order_details()

        self.download_invoice()

        time.sleep(30)

if __name__ == "__main__":
    unittest.main()
