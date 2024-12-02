import pandas as pd
import requests
import time
import re
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

# 병렬처리로 속도 높임.

def crawl_bobaedream():
    # 전역 설정
    url = 'https://www.bobaedream.co.kr/mycar/mycar_list.php?gubun=K'
    info = ["링크", "이름", "가격", "신차대비가격", "차량번호", "최초등록일", 
            "연식", "주행거리", "연료", "배기량", "색상", "보증정보", "설명글"]
    spec = ["엔진형식", "연비", "최고출력", "최대토크", "차량중량"]
    appearances = ["선루프", "파노라마선루프"]
    interiors = ["열선시트(앞좌석)", "열선시트(뒷좌석)"]
    safeties = ["동승석에어백", "후측방경보", "후방센서", "전방센서", "후방카메라", "전방카메라", "어라운드뷰"]
    conveniences = ["열선핸들", "오토라이트", "크루즈컨트롤", "자동주차"]
    multimedia = ["네비게이션(순정)", "네비게이션(비순정)"]
    insurance = ["보험처리수", "소유자변경", "전손", "침수전손", "침수분손", "도난", 
                 "내차피해_횟수", "내차피해_금액", "타차가해_횟수", "타차가해_금액"]
    check = ["판금", "교환", "부식", "사고침수유무", "불법구조변경"]
    cols = info + spec + appearances + interiors + safeties + conveniences + multimedia + insurance + check
    df_cars = []

    # 옵션 확인 함수
    def option_check(soupobject, option_name):
        if soupobject.find("button", string=option_name) is None:
            return '무'
        check = soupobject.find("button", string=option_name).find_parent("label").find_parent("span")
        check = check.find("input", {"type": "checkbox"})
        return '유' if check.has_attr("checked") else '무'

    # 차량 상세 정보 수집
    def fetch_car_details(link):
        try:
            res = requests.get(link, timeout=10)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, "html.parser")

            print(link)

            # info
            name = soup.find("h3", attrs={"class": "tit"}).get_text()
            price = soup.find("span", attrs={"class": "price"}).get_text()
            percent = soup.find("b", attrs={"class": "percent"}).get_text() if soup.find("b", attrs={"class": "percent"}) else None
            galdata = soup.find("div", attrs={"class": "gallery-data"})
            carnum = galdata.find("b").get_text().split()[1]
            regist = galdata.find_all("dd", attrs={"class": ["txt-bar", "cg"]})[2].get_text()
            info_basic = soup.find("div", attrs={"class": "info-basic"})
            year = info_basic.find("th", string='연식').find_next_sibling("td").get_text()
            km = info_basic.find("th", string='주행거리').find_next_sibling("td").get_text()
            fuel = info_basic.find("th", string='연료').find_next_sibling("td").get_text()
            amount = info_basic.find("th", string='배기량').find_next_sibling("td").get_text()
            color = info_basic.find("th", string='색상').find_next_sibling("td").get_text()
            guarn = info_basic.find("b", string='보증정보').find_next("td").get_text()
            explain = soup.find("div", attrs={"class": "explanation-box"}).get_text()

            res_info = [link, name, price, percent, carnum, regist, year, km, fuel, amount, color, guarn, explain]

            # spec
            engin = soup.find("span", string="엔진 형식").find_next_sibling("strong").get_text()
            effic = soup.find("span", string="연비").find_next_sibling("strong").get_text()
            max_pow = soup.find("span", string="최고출력").find_next_sibling("strong").get_text()
            max_tok = soup.find("span", string="최대토크").find_next_sibling("strong").get_text()
            weight = soup.find("span", string="차량중량").find_next_sibling("strong").get_text()

            res_spec = [engin, effic, max_pow, max_tok, weight]

            # Combine all results
            return res_info + res_spec
        except Exception as e:
            print(f"Error fetching details for {link}: {e}")
            return [link] + [None] * (len(cols) - 1)

    # Fetch all links from pages
    res = requests.get(url, timeout=10)
    soup_url = BeautifulSoup(res.text, "html.parser")

    # Last page
    try:
        last_page = soup_url.find("a", attrs={"class": "last"}).get("href")
        match = re.search(r'pageClick\((\d+)\)', last_page)
        last_page_num = int(match.group(1)) if match else 1
    except:
        last_page_num = 1

    # Fetch all links
    all_links = []
    for curr_page in range(1, last_page_num + 1):
        page_url = f'{url}&page={curr_page}'
        try:
            res_page = requests.get(page_url, timeout=10)
            soup_page = BeautifulSoup(res_page.text, "html.parser")
            cars = soup_page.find_all("p", attrs={"class": "tit"})
            all_links.extend(["https://www.bobaedream.co.kr" + car.a["href"] for car in cars])
        except Exception as e:
            print(f"Error fetching page {curr_page}: {e}")
            continue

    # Parallel processing of links
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(fetch_car_details, all_links))

    # Save to CSV
    df = pd.DataFrame(results, columns=cols)
    df.to_csv('./results/on_sale_cars_test.csv', index=False)
    print("Crawling completed!")


if __name__ == "__main__":
    crawl_bobaedream()
