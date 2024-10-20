from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import re
import time
import cx_Oracle
from datetime import datetime

def execute_query(query, params=None, sequence_name=None):
    connection = cx_Oracle.connect("steamsale", "1234", "localhost:1521/XE")
    cursor = connection.cursor()

    try:
        if query.strip().upper().startswith("INSERT"):
            cursor.execute(query, params)
            connection.commit()

            if sequence_name:
                # 지정된 시퀀스의 CURRVAL을 가져오는 SELECT 쿼리
                cursor.execute(f"SELECT {sequence_name}.CURRVAL FROM dual")
                return cursor.fetchone()[0]  # CURRVAL 값을 반환
        else:
            cursor.execute(query, params)

            if query.strip().upper().startswith("SELECT"):
                return cursor.fetchall()
            else:
                connection.commit()
                return cursor.rowcount
    finally:
        cursor.close()
        connection.close()


def cost_split(text):
    costs = re.findall(r'￦([\d,]+)', text)  # ￦로 시작하는 숫자 패턴 찾기
    cost_list = [cost.replace(',', '') for cost in costs]  # 쉼표 제거
    return cost_list[0], cost_list[1]

def date_split(text):
    text = text.replace(".","-")
    tmp_date = text.split("~")
    start = tmp_date[0].strip()
    end = ""
    if len(tmp_date) > 1:
        end = tmp_date[1].strip()

    return start, end

def more_click(cnt):
    for i in range(cnt):
        try:
            # 더보기 버튼 클릭
            more_button = driver.find_element(By.CSS_SELECTOR, ".btn.btn-secondary.d-block.rounded-0.w-100.font-ko")
            more_button.click()
            time.sleep(1)
        except Exception as e:
            print("버튼끝")
            break
        # 페이지 스크롤
        ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()
        time.sleep(1)



cx_Oracle.init_oracle_client(lib_dir=r"D:\groot\DB\Oracle\instantclient_23_5")
list = ['Current', 'Top', 'History']
driver = webdriver.Chrome()
cnt = 1 # 더보기 몇번 클릭할지 선택

print("======== list start")
for target in list:
    print("======== target => " , target)
    insert_query = "INSERT INTO tb_category (id, type) VALUES (SEQ_tb_category.nextval, :1)"
    print("tb_category : ", insert_query)
    params = (target,)  # name과 cost는 전달할 파라미터
    tb_category_id = execute_query(insert_query, params, "SEQ_tb_category")

    driver.get("https://steamsale.windbell.co.kr/"+target)
    more_click(cnt)

    elements = driver.find_elements(By.CLASS_NAME, "clear-a")


    for element in elements:
        print("start-1sec")
        time.sleep(1)
        print("click-1sec")
        element.click()
        time.sleep(1)

        ul_elements = driver.find_elements(By.CLASS_NAME, "card-body")
        tmptext = ul_elements[0].text.split("\n")

        name = tmptext[0]
        cost, sale = cost_split(tmptext[1])

        # tb_game
        insert_query = "INSERT INTO tb_game (id, name, cost, create_date) VALUES (seq_tb_game.nextval, :1, :2, :3)"
        print("tb_game : ", insert_query)
        params = (name, cost, datetime.now())  # name과 cost는 전달할 파라미터
        tb_game_id = execute_query(insert_query, params,"seq_tb_game")

        # tb_gametocategory
        insert_query = "INSERT INTO tb_gametocategory (game_id, category_id) VALUES (:1, :2)"
        print("tb_gametocategory : ", insert_query)
        params = (tb_game_id, tb_category_id)  # name과 cost는 전달할 파라미터
        execute_query(insert_query, params)


        ul_elements = driver.find_elements(By.CLASS_NAME, "list-group-item.border-left-0.border-right-0.rounded-0")
        for ul in ul_elements:
            tmptext = ul.text.split("\n")
            date_start, date_end = date_split(tmptext[0])
            discount = tmptext[1].strip()

            # tb_discount
            insert_query = """INSERT INTO tb_discount (id, game_id, sale, start_date, end_date, create_date) VALUES (SEQ_tb_discount.nextval, :1, :2, TO_DATE(:3, 'YYYY-MM-DD'), TO_DATE(:4, 'YYYY-MM-DD'), :5)"""
            print("tb_discount : ", insert_query)
            params = (tb_game_id, sale, date_start, date_end, datetime.now())
            execute_query(insert_query, params)

        try:
            modal = driver.find_element(By.CLASS_NAME, "ss-modal")  # 모달 찾기
            driver.execute_script("arguments[0].click();", modal)  # 모달 클릭
        except Exception as e:
            print("모달을 찾거나 클릭하는 중 오류 발생:", e)

print("======== end")


