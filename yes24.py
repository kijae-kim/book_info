import time
import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from pymongo import MongoClient
import certifi

#Yes24크롤링 클래스 함수
class Yes24Scraper:
    #크롤링시 화면이 표시되지 않게 하기 위해
    def __init__(self, headless=True):
        self.options = webdriver.ChromeOptions()
        if headless:
            self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.driver = webdriver.Chrome(options=self.options)

    #스크롤을 자동으로 맨 밑까지 내릴 수 있게
    def scroll_down(self, times=20):
        for i in range(times):
            self.driver.execute_script(f'window.scrollTo(0, document.body.scrollHeight / {times} * {i})')
            time.sleep(0.1)

    #word를 넣으면 yes24 url에 검색하여 도서정보를 추출하여 book_list에 dic형식으로 저장.
    def search(self, word):
        book_list = []

        url = f'https://www.yes24.com/Product/Search?domain=ALL&query={word}'
        self.driver.get(url)
        self.driver.implicitly_wait(2)

        self.scroll_down(20)

        xpath = '/html/body/div[1]/div[4]/div/div[2]/section[2]/div[3]/ul'
        title_list = self.driver.find_element(By.XPATH, xpath)
        book_tags = title_list.find_elements(By.CLASS_NAME, 'itemUnit')

        for book in book_tags:
            book_img = book.find_element(By.TAG_NAME, 'img')
            url = book_img.get_attribute('src')
            title = book_img.get_attribute('alt')
            price = book.find_element(By.CLASS_NAME, 'yes_b').text
            author = book.find_element(By.CLASS_NAME, 'info_auth').text
            publisher = book.find_element(By.CLASS_NAME, 'info_pub').text

            book_list.append({
                'url': url,
                'title': title,
                'price': price,
                'author': author,
                'publisher': publisher
            })

        return book_list

    def close(self):
        self.driver.quit()

#mongoDB에 저장
def save_to_mongodb(data, db_name='aiproject', collection_name='yes24'):
    ca = certifi.where()
    client = MongoClient(
        'mongodb+srv://99hakssun:OTSCipcH7d2F2Ney@99hakssun.frdhloo.mongodb.net/?retryWrites=true&w=majority&appName=99hakssun',
        tlsCAFile=ca)
    db = client[db_name]
    collection = db[collection_name]
    collection.insert_many(data)

#mongoDB에서 저장된 도서정보를 가져올 수 있게 해주는 함수.
def load_from_mongodb(db_name='aiproject', collection_name='yes24'):
    ca = certifi.where()
    client = MongoClient(
        'mongodb+srv://99hakssun:OTSCipcH7d2F2Ney@99hakssun.frdhloo.mongodb.net/?retryWrites=true&w=majority&appName=99hakssun',
        tlsCAFile=ca)
    db = client[db_name]
    collection = db[collection_name]
    return list(collection.find())


# Streamlit 앱 시작
st.title("Yes24 도서 검색 및 저장")

# 사용자 입력 받기
search_word = st.text_input("검색할 도서명을 입력하세요:")

# 검색 버튼
if st.button("검색"):
    if search_word:
        with st.spinner("검색 중..."):
            scraper = Yes24Scraper()
            book_results = scraper.search(search_word)
            scraper.close()

            if book_results:
                save_to_mongodb(book_results)
                st.success(f"{len(book_results)}개의 책 정보를 MongoDB에 저장했습니다.")
            else:
                st.write("검색 결과가 없습니다.")
    else:
        st.write("검색어를 입력하세요.")

# 저장된 데이터 불러오기 버튼
if st.button("저장된 데이터 불러오기"):
    with st.spinner("불러오는 중..."):
        saved_books = load_from_mongodb()
        if saved_books:
            for book in saved_books:
                st.image(book['url'], width=100)
                st.write(f"**제목:** {book['title']}")
                st.write(f"**가격:** {book['price']}")
                st.write(f"**저자:** {book['author']}")
                st.write(f"**출판사:** {book['publisher']}")
                st.write("---")
        else:
            st.write("저장된 데이터가 없습니다.")
