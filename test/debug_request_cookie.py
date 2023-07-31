import requests
from lxml import etree

url = "https://www.amazon.sg/Leather-Honey-Cleaner-Furniture-Accessories/dp/B00U7HEUEI/ref=zg_bs_automotive_sccl_1/356-8870810-4077739?psc=1"
cookie_value = 'session-id=358-3585930-8682529; i18n-prefs=USD; ubid-acbsg=356-8914296-9168616'
cookies = {k.split("=")[0]: k.split("=")[1] for k in cookie_value.split("; ")}
custom_headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'accept-language': 'en-GB,en;q=0.9',
}
response = requests.get(url, headers=custom_headers, cookies=cookies)
print(response.status_code)
xpath = '//*[@id="glow-ingress-block"]'
result = etree.HTML(response.text).xpath(xpath)
print(result[0].xpath(".//text()"))
