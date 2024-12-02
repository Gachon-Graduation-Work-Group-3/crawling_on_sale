import pandas as pd
import requests
import time
import re
from bs4 import BeautifulSoup


url = 'https://www.bobaedream.co.kr/mycar/mycar_list.php?gubun=K'

#전반적인 정보
info=["링크", "이름", "가격", "신차대비가격", "차량번호", "최초등록일", 
      "연식","주행거리","연료", "배기량","색상","보증정보", "설명글"]

#차량 제원
spec=["엔진형식", "연비", "최고출력", "최대토크", "차량중량"]


#옵션정보
#외관
appearances=["선루프", "파노라마선루프"]
#내장
interiors=["열선시트(앞좌석)", "열선시트(뒷좌석)"]
#안전
safeties=["동승석에어백", "후측방경보", "후방센서", "전방센서", "후방카메라", "전방카메라",
        "어라운드뷰"]
#편의
conveniences=["열선핸들", "오토라이트", "크루즈컨트롤", "자동주차"]
#멀티미디어
multimedia=["네비게이션(순정)", "네비게이션(비순정)"]


#보험처리이력
insurance=["보험처리수", "소유자변경", "전손", "침수전손", "침수분손", "도난", "내차피해_횟수", "내차피해_금액", "타차가해_횟수", "타차가해_금액"]

#성능정검
check=["판금", "교환", "부식", "사고침수유무", "불법구조변경"]

cols = info+spec+appearances+interiors+safeties+conveniences+multimedia+insurance+check
df_cars = []


#옵션이름 받아서 확인여부하는 함수
def option_check(soupobject,option_name):
    if soupobject.find("button", string=option_name) is None: return '무'
    check = soupobject.find("button", string=option_name).find_parent("label").find_parent("span")
    check = check.find("input", {"type": "checkbox"})
    # .find_parent().find_previous_sibling().get_attribute_list('checked')

    if check.has_attr("checked"):
        return '유'
    else:
        return '무'


for attempt in range(3):
        try:
            res_url = requests.get(url, timeout=10)
            if res_url.status_code == 200:
                break
        except requests.exceptions.RequestException as e:
            time.sleep(5)
soup_url = BeautifulSoup(res_url.text, "html.parser")


#마지막 페이지 찾기
try:
    last_page = soup_url.find("a", attrs={"class": "last"}).get("href")
except: 
    last_page = None

if last_page is not None:
    # 정규 표현식을 사용하여 숫자 추출
    match = re.search(r'pageClick\((\d+)\)', last_page)
    if match:
        last_page_num = int(match.group(1))
    else:
        last_page_num = 1
else:
   last_page_num = 1


# 1페이지부터 마지막 페이지까지
for curr_page in range(1, last_page_num):

    page_url = f'https://www.bobaedream.co.kr/mycar/mycar_list.php?gubun=K&page={curr_page}'
    # 요청 (최대 3번 재시도)
    for attempt in range(3):
        try:
            res_page = requests.get(page_url, timeout=10)
            if res_page.status_code == 200:
                break
        except requests.exceptions.RequestException as e:
            time.sleep(5)
    else:
        continue  # 요청 실패 시 무시
    # results_html = driver.page_source
    soup_page = BeautifulSoup(res_page.text, "html.parser")
    
    cars=soup_page.find_all("p",attrs={"class":"tit"})
    links= []

    print(page_url)

        
    #한 url마다 들어있는 모든 차들에 대해 실행
    for car in cars:
        link = "https://www.bobaedream.co.kr" + car.a["href"]
        links.append(link)

    for link in links:
        print(link)

            # 요청 (최대 3번 재시도)
        for attempt in range(3):
            try:
                res = requests.get(link, timeout=10)
                if res.status_code == 200:
                    break
            except requests.exceptions.RequestException as e:
                time.sleep(5)
        else:
            continue  # 요청 실패 시 무시

        
        # res=requests.get(link, timeout=10)
        res.raise_for_status()
        soup=BeautifulSoup(res.text, "html.parser")

        #info
        name = soup.find("h3", attrs={"class":"tit"}).get_text()
        price = soup.find("span", attrs={"class": "price"}).get_text()

        #신차대비 명시여부
        if soup.find("b", attrs={"class": "percent"}):
            percent = soup.find("b", attrs={"class": "percent"}).get_text()
        else:
            percent = None
            

        galdata = soup.find("div", attrs={"class": "gallery-data"})
        carnum = galdata.find("b").get_text().split()[1]
        regist=galdata.find_all("dd", attrs={"class":["txt-bar", "cg"]})[2].get_text()

        info_basic = soup.find("div", attrs={"class": "info-basic"})
        year=info_basic.find("th",string='연식').find_next_sibling("td").get_text()
        km=info_basic.find("th",string='주행거리').find_next_sibling("td").get_text()
        fuel=info_basic.find("th",string='연료').find_next_sibling("td").get_text()
        amount=info_basic.find("th",string='배기량').find_next_sibling("td").get_text()
        color=info_basic.find("th",string='색상').find_next_sibling("td").get_text()
        guarn=info_basic.find("b",string='보증정보').find_next("td").get_text()

        explain = soup.find("div", attrs={"class": "explanation-box"}).get_text()

        res_info = [link, name, price, percent, carnum, regist, year, km,
                    fuel, amount, color, guarn, explain]

        #spec
        engin = soup.find("span", string="엔진 형식").find_next_sibling("strong").get_text()
        effic = soup.find("span", string="연비").find_next_sibling("strong").get_text()
        max_pow = soup.find("span", string="최고출력").find_next_sibling("strong").get_text()
        max_tok = soup.find("span", string="최대토크").find_next_sibling("strong").get_text()
        weight = soup.find("span", string="차량중량").find_next_sibling("strong").get_text()

        res_spec = [engin, effic, max_pow, max_tok, weight]

        #옵션정보
        option_table=soup.find("div",attrs={"class":"tbl-option"})
        res_options= []
        #appearance
        for appearence in appearances:
            res_options.append(option_check(option_table, appearence))

        #interiors
        for interior in interiors:
            res_options.append(option_check(option_table, interior))

        #safeties
        for safety in safeties:
            res_options.append(option_check(option_table, safety))

        #conveniences
        for convenience in conveniences:
            res_options.append(option_check(option_table, convenience))

        # multimedia
        for media in multimedia:
            res_options.append(option_check(option_table, media))


        #보험이력이 있는지 여부
        isvalid_insur = soup.find("span", attrs={"class": ["round-in", "insurance"]}).find_next("i").find_next("em") != None
        #수리이력이 있는지 여부1
        isvalid_check1 = soup.find("span", attrs={"class": ["round-in", "repair"]}) != None
        isvalid_check2 = False

        if isvalid_check1: #수리이력 아이콘은 있지만 수리이력이 없는 경우
            #수리이력이 있는지 여부2
            isvalid_check2 = soup.find("span", attrs={"class": ["round-in", "repair"]}).find_next("span").find("em") != None


        if isvalid_insur and isvalid_check2:
            #보험처리이력
            info_insur = soup.find("div", attrs={"class": "info-insurance"})
            insur_cnt = info_insur.find("b", attrs={"class": "cr"}).get_text()
            insur_change = info_insur.find("th", string="차량번호/소유자변경").find_next_sibling("td").get_text().split("/")[1]

            acc = info_insur.find("th", string="자동차보험 특수사고").find_next_sibling("td").get_text().split("/")
            acc1 = acc[0].split(":")[1] #전손
            acc2 = acc[1].split(":")[1] #침수전손
            acc3 = acc[2].split(":")[1] #침수분손
            acc4 = acc[3].split(":")[1] if len(acc)>3 else None #도난

            #보험사고(내차피해)
            insur_mycar = info_insur.find("th", string="보험사고(내차피해)").find_next_sibling("td").get_text().split()
            insur_mycar_cnt = insur_mycar[0]
            insur_mycar_price = insur_mycar[1]

            #보험사고(타차가해)
            insur_othercar = info_insur.find("th", string="보험사고(타차가해)").find_next_sibling("td").get_text().split()
            insur_othercar_cnt = insur_mycar[0]
            insur_othercar_price = insur_mycar[1]

            res_insur = [insur_cnt, insur_change,  acc1, acc2, acc3, acc4, insur_mycar_cnt, insur_mycar_price,
                            insur_othercar_cnt, insur_othercar_price]
            

            #성능점검
            info_check = soup.find("div", attrs={"class": "info-check"}) 
            sheet = info_check.find_all("b", attrs={"class":"cr"})[0].get_text() #판금
            change = info_check.find_all("b", attrs={"class":"cr"})[1].get_text() #교환
            corrosion = info_check.find_all("b", attrs={"class":"cr"})[2].get_text() #부식

            flooding = info_check.find("th", string="사고/침수유무").find_next_sibling("td").get_text() #사고침수
            illegal = info_check.find("th", string="불법구조변경").find_next_sibling("td").get_text() #불법구조변경

            res_check = [sheet, change, corrosion, flooding, illegal]

        #보험이력이 있고, 수리아이콘도 있으나 수리 이력이 없는 경우
        elif isvalid_insur and isvalid_check1 and not isvalid_check2:
            #보험처리이력
            info_insur = soup.find("div", attrs={"class": "info-insurance"})
            insur_cnt = info_insur.find("b", attrs={"class": "cr"}).get_text()

            # th 태그로 받아와야 하는 경우
            if info_insur.find("th", string="차량번호/소유자변경"):
                insur_change = info_insur.find("th", string="차량번호/소유자변경").find_next_sibling("td").get_text().split("/")[1]

                acc = info_insur.find("th", string="자동차보험 특수사고").find_next_sibling("td").get_text().split("/")
                acc1 = acc[0].split(":")[1] #전손
                acc2 = acc[1].split(":")[1] #침수전손
                acc3 = acc[2].split(":")[1] #침수분손
                acc4 = acc[3].split(":")[1] if len(acc)>3 else None #도난

                #보험사고(내차피해)
                insur_mycar = info_insur.find("th", string="보험사고(내차피해)").find_next_sibling("td").get_text().split()
                insur_mycar_cnt = insur_mycar[0]
                insur_mycar_price = insur_mycar[1]

                #보험사고(타차가해)
                insur_othercar = info_insur.find("th", string="보험사고(타차가해)").find_next_sibling("td").get_text().split()
                insur_othercar_cnt = insur_mycar[0]
                insur_othercar_price = insur_mycar[1]

               

            #dt태그로 받아와야 하는 경우
            else: 
                insur_change = info_insur.find("dt", string="차량번호/소유자변경").find_next_sibling("dd").get_text().split("/")[1]

                acc = info_insur.find("dt", string="자동차보험 특수사고").find_next_sibling("dd").get_text().split("/")
                acc1 = acc[0].split(":")[1] #전손
                acc2 = acc[1].split(":")[1] #침수전손
                acc3 = acc[2].split(":")[1] #침수분손
                acc4 = acc[3].split(":")[1] if len(acc)>3 else None #도난

                #보험사고(내차피해)
                insur_mycar = info_insur.find("dt", string="보험사고(내차피헤)").find_next_sibling("dd").get_text().split()
                insur_mycar_cnt = insur_mycar[0]
                insur_mycar_price = insur_mycar[1]

                #보험사고(타차가해)
                insur_othercar = info_insur.find("dt", string="보험사고(타차가해)").find_next_sibling("dd").get_text().split()
                insur_othercar_cnt = insur_mycar[0]
                insur_othercar_price = insur_mycar[1]


            res_insur = [insur_cnt, insur_change,  acc1, acc2, acc3, acc4, insur_mycar_cnt, insur_mycar_price,
                                        insur_othercar_cnt, insur_othercar_price]
            res_check = [None] * len(check)

        #보험이력은 있으나 수리이력이 없는 경우
        elif isvalid_insur and not isvalid_check2:
            #보험처리이력
            info_insur = soup.find("div", attrs={"class": "info-insurance"})
            insur_cnt = info_insur.find("b", attrs={"class": "cr"}).get_text()
            insur_change = info_insur.find("dt", string="차량번호/소유자변경").find_next_sibling("dd").get_text().split("/")[1]

            acc = info_insur.find("dt", string="자동차보험 특수사고").find_next_sibling("dd").get_text().split("/")
            acc1 = acc[0].split(":")[1] #전손
            acc2 = acc[1].split(":")[1] #침수전손
            acc3 = acc[2].split(":")[1] #침수분손
            acc4 = acc[3].split(":")[1] if len(acc)>3 else None #도난

            #보험사고(내차피해)
            insur_mycar = info_insur.find("dt", string="보험사고(내차피헤)").find_next_sibling("dd").get_text().split()
            insur_mycar_cnt = insur_mycar[0]
            insur_mycar_price = insur_mycar[1]

            #보험사고(타차가해)
            insur_othercar = info_insur.find("dt", string="보험사고(타차가해)").find_next_sibling("dd").get_text().split()
            insur_othercar_cnt = insur_mycar[0]
            insur_othercar_price = insur_mycar[1]

            res_insur = [insur_cnt, insur_change,  acc1, acc2, acc3, acc4, insur_mycar_cnt, insur_mycar_price,
                            insur_othercar_cnt, insur_othercar_price]
            
            res_check = [None] * len(check)


        else: #보험이력이 없는 경우
            res_insur = [None] * len(insurance)
            res_check = [None] * len(check)


        temp = res_info + res_spec + res_options + res_insur + res_check

        df_cars.append(temp)



df = pd.DataFrame(data=df_cars, columns=cols)
df.to_csv('./results/on_sale_cars_test.csv')