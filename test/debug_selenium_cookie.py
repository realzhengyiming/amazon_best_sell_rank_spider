from amazon_scrapy_spider.selenium_utils import create_wire_proxy_chrome, pickle_cookie, set_en_language_cookie

if __name__ == '__main__':

    driver = create_wire_proxy_chrome(headless=False, image_mode=True)
    # driver.get('https://dev.kdlapi.com/testproxy')
    # driver.get("https://www.amazon.com")

    # pickle_cookie(driver)
    # load_pickled_cookie(driver)
    # driver.add_cookie({'name': 'lc-main', 'value': 'en_US'})

    driver.add_cookie({'domain': '.amazon.com', 'expiry': 1716907356, 'httpOnly': False, 'name': 'lc-main', 'path': '/', 'secure': False, 'value': 'en_US'})
    driver.get("https://www.amazon.com")

    print()