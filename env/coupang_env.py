import sys 
import os,re 
import json
LUMINA_ROOT = os.environ.get('LUMINA_ROOT')
sys.path.append(LUMINA_ROOT)
from gpt_prompt.gpt4_completion import GPT4Query

from selenium import webdriver
from bs4 import BeautifulSoup
from colorama import Fore, Style
import urllib.parse

COUPANG_MAIN_URL = 'https://www.coupang.com/'

class CoupangEnv:
    
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-blink-features")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
        self.driver = webdriver.Chrome(options=options)
        self.gpt_conn = GPT4Query()

    def search_product(self, product_name):
        product_name_encoded = urllib.parse.quote(product_name)
        self.driver.get(f"{COUPANG_MAIN_URL}np/search?q={product_name_encoded}")
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        products = []
        for product in soup.find_all('li', {'class': 'search-product'}):

            product_link =COUPANG_MAIN_URL + soup.find('a', class_='search-product-link')['href'][1:] # HARD-CODED
            image = product.find('img', {'class': 'search-product-wrap-img'}).get('src')
            name = product.find('div', {'class': 'name'}).text
            price = product.find('strong', {'class': 'price-value'}).text
            rating = product.find('em', {'class': 'rating'})

            if rating:
                rating = rating.text
            else:
                rating = "No rating"

            products.append({
                'name': re.sub(r'\s+', ' ', name).strip(),
                'price': re.sub(r'\s+', ' ', price).strip(),
                'rating': re.sub(r'\s+', ' ', rating).strip(),
                'image': re.sub(r'\s+', ' ', image).strip(),
                'detail_link' : re.sub(r'\s+', ' ', product_link).strip(),
            })

        return products

    def goto_detail_page(self, link):
        self.driver.get(link)

    def get_product_details(self):
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        # Find the script tag
        script_tag = soup.find('script', text=lambda t: t and 'exports.sdp' in t)

        # Check if script_tag is None
        if script_tag is not None:
            # Extract the content of the script tag
            script_content = script_tag.string
            
            # Extract the value of exports.sdp
            start_index = script_content.find('exports.sdp')
            end_index = start_index + len('exports.sdp') + 3  # +3 to account for the '= {' characters
            brace_count = 0
            
            # Loop through the characters from the start index
            for i in range(end_index, len(script_content)):
                if script_content[i] == '{':
                    brace_count += 1
                elif script_content[i] == '}':
                    brace_count -= 1
                    
                    if brace_count == 0:
                        end_index = i + 1  # Set the end index when brace_count reaches 0
                        break
            
            exports_sdp = script_content[start_index:end_index]
            script_dict = json.loads(exports_sdp)
            # Print the value of exports.sdp
            print(exports_sdp)
        else:
            print("No script tag containing 'exports.sdp' found.")

        print(script_dict['name'])

        exit()

        product_details = {}

        # Save soup as a .txt file
        with open('/Users/seungyounshin/Desktop/lumina/detail_example.txt', 'w', encoding='utf-8') as file:
            file.write(self.driver.page_source)


        brand_name = soup.find('a', {'class': 'prod-brand-name'})
        product_details['brand_name'] = brand_name.text if brand_name else 'N/A'

        product_title = soup.find('span', {'class': 'prod-share__twitter'})
        product_details['product_title'] = product_title.get('data-title') if product_title else 'N/A'

        price = soup.find('span', {'class': 'total-price'}).find('strong')
        product_details['price'] = price.text if price else 'N/A'

        coupang_wow_price = soup.select_one('.prod-price .major-price-coupon')
        if coupang_wow_price:
            coupang_wow_price = coupang_wow_price.text.strip().split('\n')[0]
        else:
            coupang_wow_price = 'N/A'
        product_details['coupang_wow_price'] = coupang_wow_price

        when_to_arrive_div = soup.find('div', {'class': 'prod-pdd'})
        if when_to_arrive_div:
            when_to_arrive_em_tags = when_to_arrive_div.find_all('em', {'class': 'prod-txt-onyx'})
            when_to_arrive = ' '.join(em.text for em in when_to_arrive_em_tags)
        else:
            when_to_arrive = 'N/A'
        product_details['when_to_arrive'] = when_to_arrive

        detail_option_button = soup.find('div', {'class': 'prod-option__selected  multiple'})
        product_details['detail_option_button'] = dict()

        quantity = soup.find('input', {'class': 'prod-quantity__input'})
        
        # Extract product option keys
        product_option_keys = soup.find_all('div', {'class': 'prod-option__selected-container'})

        for key_container in product_option_keys:
            key = key_container.find('span', {'class': 'title'}).text.strip()
            product_details['detail_option_button'][key] = []

        # Extract product options
        product_option_lists = soup.find_all('ul', {'class': 'prod-option__list'})

        print(product_option_lists)
        for i, option_list in enumerate(product_option_lists):
            key = list(product_details['detail_option_button'].keys())[i]  # get the corresponding key
            option_items = option_list.find_all('li', {'class': 'prod-option-dropdown-item'})

            print(f'{key} :: {option_items}')

            for item in option_items:
                option = item.find('strong').text
                product_details['detail_option_button'][key].append(option)


        return product_details

    def detail_reply(self, link=None):
        self.goto_detail_page(link)
    
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        

if __name__ == "__main__":
    coupang = CoupangEnv()
    products = coupang.search_product('노트북')

    print(f' len of product : {len(products)}')
    for product in products:
        name = product['name']
        price = product['price']
        rating = product['rating']
        image = product['image']
        link = product['detail_link']
        
        output = f"{Fore.BLUE}Name: {name}{Style.RESET_ALL}\n"
        output += f"{Fore.GREEN}Price: {price}{Style.RESET_ALL}\n"
        output += f"{Fore.YELLOW}Rating: {rating}{Style.RESET_ALL}\n"
        output += f"{Fore.MAGENTA}Image: {image}{Style.RESET_ALL}\n"
        output += f"{Fore.GREEN}Detail link: {link}{Style.RESET_ALL}\n"
        
        print(output)
        print("======="*5)
    
    # goto detail first page
    print(f" goto product detail link : { products[-1]['detail_link'] }")
    coupang.goto_detail_page('https://www.coupang.com/vp/products/4692708274?itemId=13761893691&vendorItemId=81397125516&sourceType=srp_product_ads&clickEventId=9cc34095-1e0d-4369-913a-461f6a6e76ed&korePlacement=15&koreSubPlacement=1&clickEventId=9cc34095-1e0d-4369-913a-461f6a6e76ed&korePlacement=15&koreSubPlacement=1&q=%EB%85%B8%ED%8A%B8%EB%B6%81&itemsCount=36&searchId=efbbb1e41e2e464b8e70a3970eaa3213&rank=0')
    
    print(coupang.get_product_details())

    import time 
    time.sleep(3)