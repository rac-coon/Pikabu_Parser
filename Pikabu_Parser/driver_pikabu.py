import time
import undetected_chromedriver as uc
from proxy_checking import ProxyChecker
import requests
import random
import re

def driver_start():
    options = uc.ChromeOptions()
    options.headless = True
    options.browser_version = "101.0.4951.67"
    driver = uc.Chrome(options=options)
    return driver


def driver_end(driver):
    driver.quit()


def driver_with_proxy():
    proxy_list = proxy_pars()
    proxy = proxy_choose(proxy_list)
    options = uc.ChromeOptions()
    options.headless = True
    options.add_argument(f'--proxy-server={proxy[0]}://{proxy[1]}')
    driver = uc.Chrome(options=options)
    return driver


def proxy_choose(proxy_list):
    checker = ProxyChecker()
    progress = len(proxy_list)
    iterations_count = 0
    timeout = 2.0
    for proxy in proxy_list:
        iterations_count += 1
        print(f"[DEBUG] proxy: {iterations_count}/{progress}, {proxy}")
        proxy = str(proxy)
        try:
            result = checker.check_proxy(proxy)
        except:
            continue
        if result['status'] and (result['type'][0] != 'http'):
            print(f"{proxy} {result['type']} {result['time_response']}")
            if float(result['time_response']) < timeout:
                timeout = float(result['time_response'])
                if timeout < 0.7:
                    return [proxy, result['type']]
        else:
            pass
    print("PROXY NOT FOUND")
    return None

def proxy_pars():
    # дополнить список
    #
    # "https://www.proxyscan.io/download?type=https"
    # "http://rootjazz.com/proxies/proxies.txt"
    # "https://api.openproxy.space/lists/http"


    # links = [
    #     "https://api.openproxy.space/lists/socks4",
    #     "https://api.openproxy.space/lists/socks5"
    #     "https://proxy-daily.com/"
    #     "https://free-proxy-list.net/"
    # ]

    links = ["https://proxy-daily.com/"]

    proxy_list = []
    url = random.choice(links)
    print(url)
    req = requests.get(url).text
    print(req)
    temp_list = re.findall(r"(\d+\.\d+\.\d+\.\d+:\d+)", req)
    for proxy in temp_list:
        if proxy != "":
            proxy_list.append(proxy)
    return (proxy_list)


if __name__ == '__main__':
    print("[DEBUG] driver_pikabu.py")
    # driver = driver_with_proxy()
    # driver.get("https://2ip.ru")
    # print("successful")
    # time.sleep(5)
    # driver.save_screenshot("test.png")
    # driver.save_screenshot('/Screenshots/proxy_test.png')
    # time.sleep(20)
    # driver_end(driver)
