import sys 
import os,re 
import json
LUMINA_ROOT = os.environ.get('LUMINA_ROOT')
sys.path.append(LUMINA_ROOT)
from gpt_prompt.gpt4_completion import GPT4Query
from const import *

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

        self.NOW_PAGE = 'HOME'
        self.productNum_to_url = dict()
        self.last_search_result = None

    def search_product(self, product_name):
        product_name_encoded = urllib.parse.quote(product_name)
        self.driver.get(f"{COUPANG_MAIN_URL}np/search?q={product_name_encoded}&sorter=scoreDesc")
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

        for idx, product in enumerate(products):
            self.productNum_to_url[idx+1] = product

        self.NOW_PAGE = 'SEARCH_RESULTS'
        obs = self.print_product_list(products, head=5)
        self.last_search_result = obs
        #return products
        return obs

    def goto_detail_page(self, link):
        self.driver.get(link)
        self.NOW_PAGE = 'DETAIL'

    def get_product_details(self):
        if self.NOW_PAGE is not 'DETAIL':
            return None

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
    

        scripts = soup.find_all('script')

        # pattern to match "exports.sdp = { ... };"
        pattern = re.compile(r"exports\.sdp = (.*?);", re.DOTALL)

        data = None
        for script in scripts:
            match = re.search(pattern, script.text)
            if match:
                json_str = match.group(1)  # extract the JSON string
                data = json.loads(json_str)  # parse the JSON string
            #break # HARD-CODED
        
        brand = data['brand']
        itemId = data['itemId']
        productId = data['productId']
        product_name = data['itemName']
        title = data['title']
        option_raw = data['options']
        ratingCount = data['ratingCount']
        ratingAveragePercentage = data['ratingAveragePercentage']
        
        options_dict = {}
        for option in option_raw['optionRows']:
            option_name = option['name']
            attributes = [attribute['name'] for attribute in option['attributes']]
            options_dict[option_name] = attributes

        detail_dict = {
            'brand' : brand,
            'itemId' : itemId,
            'productId' : productId,
            'title' : product_name,
            'ratingCount' : ratingCount,
            'ratingAveragePercentage' : ratingAveragePercentage,
            'option' : options_dict
        }

        return self.pretty_product_details(detail_dict)
    
    def print_product_list(self,products, head=None):
        
        if head is not None and isinstance(head, int):
            products_to_print = products[:head]
        else:
            products_to_print = products

        obs_str = ''
        for idx,product in enumerate(products_to_print):
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
            #print(output)

            obs_str += f'Product Number : [{idx+1}]\n'
            obs_str += f"Name: {name}\n"
            obs_str += f"Price: {price}\n"
            obs_str += f"Rating: {rating}\n"
            obs_str += (f'-')*8
            obs_str += '\n'
        
        return obs_str

    def click_product_num(self, num):
        if len(self.productNum_to_url.keys()) < 1 :
            return "Invalid action"
    
        product_info = self.productNum_to_url[num]
        url = product_info['detail_link']

        self.goto_detail_page(url) # DETAIL

        detail_dict = self.get_product_details()

        return detail_dict

    def pretty_product_details(self, details):
        options = "\n".join([f"\t{k}: {', '.join(v)}" for k, v in details["option"].items()])
        pretty_string = f"""
Title: {details["title"]}
Rating Count: {details["ratingCount"]}
Rating : {details["ratingAveragePercentage"]}
Options: 
{options}
<back_to_search>
        """
        return pretty_string

    def step(self,action):
        
        action = action.strip()
        obs = ''
        if action.startswith('[search]'):
            match = re.search(r'\[search\](\w+)', action)

            if match:
                result = match.group(1)
                obs = coupang.search_product(result)
            else:
                obs = 'Not a valid query'

        elif action.startswith('[think]'):
            obs= 'Ok.'
        
        elif action.startswith('[done]'):
            obs= 'Done.'

        elif action.startswith('[click]'):
            if self.NOW_PAGE == 'SEARCH_RESULTS':
                match = re.search(r'\[click\](\w+)', action)
                if match:
                    result = match.group(1)
                    try:
                        obs = self.click_product_num(int(result))
                        self.NOW_PAGE = 'DETAIL'
                    except:
                        obs = "Not a valid click button"

            elif self.NOW_PAGE == 'DETAIL':
                match = re.search(r'\[click\](\w+)', action)
                if match:
                    result = match.group(1)
                    if 'back_to_search' in result.lower():
                        # back to search 
                        obs = self.last_search_result
                        self.NOW_PAGE = 'SEARCH_RESULTS'

        return obs
    

    def instruct(self,instruct):
        return f"\'{instruct}\'"


if __name__ == "__main__":
    coupang = CoupangEnv()
    MAX_STEPS = 10
    
    '''obs = coupang.step('[search]노트북')
    print(obs)
    print('----')

    obs = coupang.step('[click]2')
    print(obs)
    print('----')

    obs = coupang.step('[click]Back_to_search')
    print(obs)
    print('----')'''

    # test GPT4 to select macbook m2 version with lowest price 
    gpt4_agent = GPT4Query(role_msg=GPT4_PROMPT)
    obs = coupang.instruct('맥북에어 m2 들어간거 골라줘')
    for i in range(MAX_STEPS):

        # Query GPT-4
        gpt4_agent.query(obs)
        action_str = gpt4_agent.get_response_content()
        
        print('GPT4 action : ',action_str)

        obs = coupang.step(action_str)

        print(f'Observation :\n{obs}')
        print("-------")
        if obs=='Done.':
            break


