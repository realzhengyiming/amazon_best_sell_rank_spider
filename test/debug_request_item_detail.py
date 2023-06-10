import os
import time

import requests

custom_headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'accept-language': 'en-GB,en;q=0.9',
}

url = "https://www.amazon.sg/Marna-Shupatto-Compact-Renewal-Foldable/dp/B08NHZYZ4N/ref=zg-bs_office-products_sccl_3/356-8870810-4077739?pd_rd_w=m0KPL&content-id=amzn1.sym.4003cb08-7585-48be-9f3b-81dc7f7d11ae&pf_rd_p=4003cb08-7585-48be-9f3b-81dc7f7d11ae&pf_rd_r=FCVDGJSFHWA15RX9XPFC&pd_rd_wg=gq40V&pd_rd_r=a022768e-4653-431f-8f49-1cc828073b40&pd_rd_i=B08NHZYZ4N&psc=1"

url = "https://www.amazon.sg/Leather-Honey-Cleaner-Furniture-Accessories/dp/B00U7HEUEI/ref=zg_bs_automotive_sccl_1/356-8870810-4077739?psc=1"

# url = "https://www.amazon.com/Best-Sellers-Amazon-Devices-Accessories/zgbs/amazon-devices/ref=zg_bs_nav_0"

result = []
for i in range(1):
    os.makedirs("output", exist_ok=True)
    start = time.time()
    response = requests.get(url, headers=custom_headers)
    # 查看容量
    print(response.text[:100])
    a = time.time() - start
    result.append(a)
    print(a)
    print(len(response.content) / 1024 ** 2, "M")
    with open(f"item_detail_example_from_requests.html", "w") as file:
        file.write(response.text)
    ## 设置代理，依然会被检测出来，
    # for i in range(1000):
    #     import time
    #
    #     start = time.time()
    #     response = requests.get(url, headers=custom_headers)
    #     print(len(response.text))
    #     print(f"spend {time.time() - start}")
    #     with open(f"output/{i}.html", "w") as file:
    #         file.write(response.text)

    #
import numpy as np

print(np.mean(result))

# print(response.text)
