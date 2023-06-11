# ShopGPT 

## COUPANG Env

This repository provides a Python interface for interacting with the Coupang e-commerce platform. It utilizes web scraping techniques to extract details of various products and simulates actions such as searching for a product, clicking on product details and getting detailed product information. The extracted information includes product details like name, price, rating, image, link to product, brand, item ID, product ID, title, rating count, average rating percentage, and product options.

## Features
* Searching for products: This module allows you to search for any product on the Coupang platform and returns a list of products along with their basic details such as name, price, rating, image and link to product page.

* Product Detail Extraction: It allows you to get detailed information about a specific product by clicking on the product. The detailed information includes brand, item ID, product ID, title, rating count, average rating percentage, and product options.

* Integration with GPT-4: This project also integrates the powerful GPT-4 language model to generate actions based on natural language instructions.

## Requirements
```
Python 3.6+
selenium
BeautifulSoup
colorama
urllib
```

## How to use
```python
from CoupangEnv import CoupangEnv

# Initialize the Coupang environment
coupang = CoupangEnv()

# To search a product
products = coupang.search_product("노트북")

# To get detailed information about a product
product_details = coupang.click_product_num(1) # clicking on first product
```

## Example
An example of the system in action with the GPT-4 language model:

```python
# Initialize the GPT-4 model
gpt4_agent = GPT4Query(role_msg=GPT4_PROMPT)

# Give the model an instruction
obs = coupang.instruct('맥북에어 m2 들어간거 골라줘 200만원 이하로')

for i in range(MAX_STEPS):
    # Query GPT-4
    gpt4_agent.query(obs)

    # Get action from GPT-4
    action_str = gpt4_agent.get_response_content()
    print('GPT4 action : ',action_str)

    # Perform the action in the Coupang environment
    obs = coupang.step(action_str)
```

You will get results of 

```plaintext
GPT4 action :  [search]맥북 에어 m2
Observation : 

Product Number : [1]
Name: Apple MacBook Air with 2021 M2 Chip, Retina Display, 512GB SSD, Space Gray
Price: 2,050,000
Rating: 4.7
---------
Product Number : [2]
Name: Apple MacBook Air with 2021 M2 Chip, Retina Display, 256GB SSD, Gold
Price: 1,850,000
Rating: 4.6
....

GPT4 action :  [click]1
Title: Apple 2022 맥북 에어, 미드나이트, M2 8코어, GPU 8코어, 256GB, 8GB, 30W, 한글, MLY33KH/A
Rating Count: 10
Rating : 100
Options: 
        색상 × 용량 × 메모리: 미드나이트 × 256GB × 8GB
<back_to_search>

GPT4 action :  I found the perfect match for you:
Title: Apple 2022 맥북 에어, 미드나이트, M2 8코어, GPU 8코어, 256GB, 8GB, 30W, 한글, MLY33KH/A
```