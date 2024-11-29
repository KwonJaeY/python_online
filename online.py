# 240429 권재영 온라인 강의 자동화
'''
pip install webdriver_manager
pip install selenium
pip install instagrapi
pip install Pillow
'''
# 셀레니움 모듈
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# 인스타그램 모듈
# from instagrapi import Client
# from instagrapi.types import StoryMention, StoryMedia, StoryLink, StoryHashtag

# 시간체크 모듈
import time
from datetime import datetime
import math
import threading

# 이외 사용 모듈
import random
import traceback
import re

global newdriver  # 멀티 스레딩을 위한 드라이버 전역변수 선언
global main_window  # 메인 윈도우(기존창) 전역변수 선언
global now_window  # 현재 윈도우(새창) 전역변수 선언
global timerEnd  # 경고창 자동 확인 전역변수 선언 True / False
global loginRenewalEnd  # 로그인 갱신 전역변수 선언

timerEnd = True
loginRenewalEnd = True


def login(id, pw, driver):
    # 검색 입력창 찾기 (검색창의 이름이 'q')
    id_box = driver.find_element(By.NAME, 'user_id')
    pw_box = driver.find_element(By.NAME, 'user_pass')
    submit_bt = driver.find_element(By.CSS_SELECTOR, "#login_1 > span")
    # 검색어 입력
    id_box.send_keys(id)
    pw_box.send_keys(pw)
    # 검색 실행
    submit_bt.click()


def login_renewal():
    global newdriver  # 전역변수 사용
    global now_window  # 전역변수 사용
    global main_window  # 전역변수 사용

    try:
        newdriver.switch_to.window(main_window)  # 메인 윈도우로 이동
        newdriver.find_element(
            # 로그인 시간 연장
            By.CSS_SELECTOR, "#header > h1 > font > span:nth-child(3) > a").click()
        time.sleep(1)
        result = newdriver.switch_to.alert  # alert 창 접근
        result.accept()  # 확인
        # newdriver.execute_script("goSessionAdd();") ## 로그인 갱신 자바스크립트 호출 방식 위,아래 둘다 상관
        newdriver.switch_to.window(now_window)  # 동영상 재생창으로 복귀
    except:
        print("login_renewal : fail")
        pass


# 경고창 자동 확인 함수


def alert_check():
    global newdriver  # 전역변수 사용
    global now_window  # 전역변수 사용

    try:
        result = newdriver.switch_to.alert  # alert 창 접근
        result.accept()  # 확인
        newdriver.switch_to.window(now_window)  # 동영상 재생창으로 복귀
    except:
        # print("alert_check : fail")
        pass


# 로그인 갱신 타이머


def myTimer(t, start_time, logical, func):
    now = time.strftime('%H:%M:%S')  # 현재 시간
    time_laps = math.floor(time.time() - start_time)  # 경과 시간 계산(소수점버림)
    # if time_laps % 600 == 0 :
    print(f'로그인 후 {now} : {(time_laps / 60)}분 경과')
    timer = threading.Timer(t, myTimer, args=(
        t, start_time, logical, func))  # 2700초(45분) 마다 반복
    if globals()["{}".format(logical)]:
        timer.start()
        func()
    else:
        print("타이머 종료.")
        timer.cancel()
    pass


def return_sArr(driver):
    newListEl = driver.find_element(By.CSS_SELECTOR, ".login .login_list")
    sList = newListEl.text.split('\n')
    cList = list()
    newCheck = datetime.today().weekday()
    if str(newCheck) != "0":  # 나중에 0으로 바꿔줘야함
        for s in sList:
            subject = re.match(r"new .*", s)
            if subject:
                cList.append(subject.group())
            else:
                cList.append("")
    else:  # 월요일에는 new 강의가 아닌 전체 강의를 체크한다
        cList = sList

    sArr = []
    iter = 0
    for i in range(len(cList)):
        if cList[i]:
            newEl = driver.find_element(
                By.CSS_SELECTOR, "article.login > div.login_list > ul > li:nth-child(" + str(i + 1) + ") > a")
            sArr.append([])
            sArr[iter].append(cList[i])
            sArr[iter].append(newEl.get_attribute("href"))
            iter += 1
            # print(newEl.get_attribute("href"))
    return sArr


def make_wateTime(tArr):
    wArr = list()
    for t in tArr:
        subject = re.match(r".*[분].*[초].*", t)
        if subject:
            waitTime = subject.group().split("/")
            waitTime = re.findall(r"\d*", waitTime[-1])
            waitTime = [v for v in waitTime if v]
            waitSecond = ((int(waitTime[0]) + 1) * 60) + int(waitTime[1])
            wArr.append(waitSecond)
    del wArr[-1]
    return wArr


def each_subject(fn_openEnter, newdriver, cl, subj):
    global timerEnd
    insta_ids = [
        'kwon.jaeyeong'  # 계정 리스트 넣기
    ]

    login("202407003", "rkawk123!", newdriver)  # 로그인 함수 호출
    loginStartTime = time.time()
    myTimer(10, loginStartTime, "loginRenewalEnd", login_renewal)
    newdriver.execute_script(fn_openEnter)
    newdriver.maximize_window()
    # 원격 강의 클릭
    time.sleep(1)
    tEl = newdriver.find_element(
        By.CSS_SELECTOR, "body > div.left_menu.wrap > div > div.bgn.bgn1 > span:nth-child(2) > a")
    tEl.click()
    time.sleep(3)
    newIter = 1
    stElArr = newdriver.find_elements(
        By.CSS_SELECTOR, "div.product_list.wow.fadeInDown.animated > ul > li")
    for stEl in stElArr:
        temp = list()
        # 강의 목록 추출 ** 작업 끝난 후
        temp = stEl.text.split("\n")
        main_window = newdriver.current_window_handle  # 메인 윈도우 저장
        # 학습하기 && 100%가 아닐 경우에만 시작
        if (temp[-1] == "학습하기") and temp[-2] != "100%":
            '''newdriver.find_element(
                By.CSS_SELECTOR, "div.product_list.wow.fadeInDown.animated > ul > li:nth-child(" + str(
                    newIter) + ") > dl > dd > article > a").click()'''
            #fnUserAuth();
            temptext = newdriver.find_element(
                By.CSS_SELECTOR, "div.product_list.wow.fadeInDown.animated > ul > li:nth-child(" + str(
                    newIter) + ") > dl > dd > article > a").get_attribute("onclick")
            newdriver.execute_script(temptext)
            round_tcd_tmp = newdriver.find_element(
                By.ID, "round_tcd_tmp").get_attribute("value")
            newdriver.execute_script(
                "fnViewMovie('" + round_tcd_tmp + "');fnLoginAuthDisplay();")
            time.sleep(3)  # 새창 로드 대기
            # 창전환 새창 관리 시작
            now_window = newdriver.window_handles[1]  # 새창 변수에 담기

            wateArr = make_wateTime(temp)  # 시간 계산 함수 but 스킵하는걸로 수정

            start_time = time.time()  # 시작 시간 저장
            timerEnd = True
            myTimer(2, start_time, "timerEnd", alert_check)  # 경고창 타이머 시작
            newdriver.switch_to.window(now_window)
            newdriver.set_window_position(150, 150)  # 윈도우 배치 수정

            tempEle = newdriver.find_elements(
                # 리스트 가져오고
                By.CSS_SELECTOR, "#naviViewer > div.navi-tables-container > ul:nth-child(2) > li a")
            elArr = [a.get_attribute("onclick") for a in tempEle]
            # print(elArr)
            for e in elArr:
                reArr = re.findall(r"(?<=\')([\d\.]*?)(?=\')", e)
                # print(reArr)
                newdriver.execute_script(
                    e.replace("'" + reArr[1] + "'", "'" + reArr[0] + "'"))  # 화면 켜 주고
                print(temp[0])
                print(temp[-1])
                time.sleep(5)
                newdriver.switch_to.frame(newdriver.find_element(
                    By.ID, "contentViewer"))  # iframe 처리
                newdriver.find_element(
                    # 동영상 재생
                    By.CSS_SELECTOR, ".vc-front-screen-play-btn").click()
                newdriver.switch_to.default_content()  # 기존 html 구조로 전환
                # newdriver.execute_script("document.getElementsByClassName('vc-front-screen-play-btn')[0].click()"); ## 안잡힘.
                time.sleep(25)  # 30초 대기 초기 광고 동영상 16초 포함 여유롭게 작업
            ''' ## 스킵 기능 추가로 인해 사용 안함 
            print("대기시간 : "+str(waitSecond)) ## 강의 시간 + 1분 
            time.sleep(waitSecond)
            newdriver.find_element(By.CSS_SELECTOR, "#close_btn > div > a").click() ## 학습완료 버튼 클릭
            time.sleep(5)
            '''
            newdriver.close()
            timerEnd = False  # 경고창 타이머 종료
            newdriver.switch_to.window(main_window)

        newIter += 1

    time.sleep(1)  # 페이지가 로드되기를 기다리기 위해 1초 동안 대기.
    # total_height = newdriver.execute_script("return document.body.parentNode.scrollHeight") # 자바스크립트를 실행하여 웹페이지의 총 높이를 가져오기.
    newdriver.execute_script("location.reload(true);")  # 브라우저 축소
    newdriver.execute_script("document.body.style.zoom = '50%';")  # 브라우저 축소
    # 브라우저 창을 페이지 하단으로 스크롤 하기.
    newdriver.execute_script("window.scrollTo(0, 500);")
    time.sleep(1)  # 1초 동안 대기.
    # 아래 코드는 --headless 옵션을 넣어줘야 작동 하지만 해당 옵션을 사용시 스크립트 에러 브라우저 축소하는걸로 대체
    # newdriver.set_window_size("1920", total_height) # 창의 크기를 설정하여 전체 웹페이지를 캡처 (너비: 1920 픽셀, 높이: total_height 픽셀)
    scrName = "./screenshot" + str(random.randrange(1, 300)) + ".png"
    # while문 끝나면 각 과목별로 스크린샷 한장씩 찍어서 인스타 dm 보내기
    newdriver.save_screenshot(scrName)
    newdriver.close()
    '''
    for id in insta_ids :
        try:
            user_id = cl.user_id_from_username(id)

            # user_info_pk['pk']  #pk 정보 가져오기 #3949757665
            # user_info_pk['username'] #계정명

            cl.direct_send(subj, user_ids=[user_id]) #보내기
            cl.direct_send_photo(scrName,user_ids=[user_id])
            print(str(id) + " 계정에게 인스타 DM 발송이 완료되었습니다.")
        except :
            print(str(id) + " 계정에게 인스타 DM 발송이 전송하지 못했습니다.")
    '''


chrome_options = Options()
chrome_options.add_experimental_option("detach", True)  # 브라우저 꺼짐 방지 옵션

driver = webdriver.Chrome(service=ChromeService("chromedriver.exe"))  # 크롬 드라이버 생성
main_url = "https://lms.tsu.ac.kr/contents/main.do"
driver.get(main_url)  # 학교 도메인으로 이동
# 로그인
login("202407003", "rkawk123!", driver)
sArr = return_sArr(driver)  # 강의 목록에 new가 있는 데이터 및 href 추출
driver.quit()

# cl = Client()
# cl.login('wpdntm9418@naver.com', 'Qjejqmf12!!')
cl = ""
subj = ""
for i in sArr:
    for j in i:
        test = re.match(r"(new|[가-힣]).*", j)
        if test:
            subj = j
        else:
            # 하나씩 처리
            newdriver = webdriver.Chrome(service=ChromeService("chromedriver.exe"), options=chrome_options)
            newdriver.get(main_url)  # 메인 url로 이동
            try:
                subj = str(datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S")) + "\n" + subj
                each_subject(j, newdriver, cl, subj)
            except Exception as e:
                print(traceback.format_exc())
                newdriver.quit()
                loginRenewalEnd = False  # 로그인 갱신 타이머 종료
                timerEnd = False  # 경고창 타이머 종료
loginRenewalEnd = False  # 로그인 갱신 타이머 종료

'''
미사용 함수 

## 경고창 자동 확인 타이머 
def alert_timer():
    global timerEnd ## 전역변수 사용

    now = time.strftime('%H:%M:%S')                     ## 현재 시간
    time_laps = math.floor(time.time() - start_time)    ## 경과 시간 계산(소수점버림)
    print(f'{now} : {time_laps}초 경과')
    timer = threading.Timer(int(term),alert_timer)             ## x초 마다 반복
    if timerEnd :
        timer.start()
        alert_check()
    else :
        print("타이머 종료.")
        timer.cancel()
    pass 

 ## 로그인 갱신 타이머 
def login_timer() :
    global loginFalse ## 전역변수 사용

    now = time.strftime('%H:%M:%S')                     ## 현재 시간
    time_laps = math.floor(time.time() - loginStartTime)    ## 경과 시간 계산(소수점버림)
    print(f'로그인 후 {now} : {time_laps}초 경과')
    loginTimer = threading.Timer(2700,login_timer)             ## 2700초(45분) 마다 반복
    if loginRenewalEnd :
        loginTimer.start()
        login_renewal()
    else :
        print("타이머 종료.")
        loginTimer.cancel()
    pass  
'''
