import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from pymongo import MongoClient
import requests
import certifi


# MongoDB 클라이언트 설정
ca = certifi.where()
client = MongoClient(
    'mongodb+srv://99hakssun:OTSCipcH7d2F2Ney@99hakssun.frdhloo.mongodb.net/?retryWrites=true&w=majority&appName=99hakssun',
    tlsCAFile=ca)
db = client['aiproject']  # 데이터베이스 이름
collection = db['coffeemap']

# 지오코더 객체 생성
geolocator = Nominatim(user_agent="geoapiExercises")

def store_append(driver, dic_list):
    store_list_xpath = '/html/body/div[3]/div[3]/div[1]/div[2]/div[4]/div[1]'
    store_list = driver.find_element(By.XPATH, store_list_xpath)
    store_names = store_list.find_elements(By.CSS_SELECTOR, '.name > span')
    store_addresses = store_list.find_elements(By.CSS_SELECTOR, '.address > span')

    for store_name, store_address in zip(store_names, store_addresses):
        strong_tag = store_name.find_element(By.CSS_SELECTOR, 'strong.distance')
        if strong_tag:
            driver.execute_script("arguments[0].remove();", strong_tag)
        dic = {'shops': store_name.text, 'address': store_address.text}
        dic_list.append(dic)



# Kakao API를 사용하여 주소를 위도/경도로 변환하는 함수
def get_lat_lng(address):
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": "KakaoAK 9dd63d2676419808359e662dcb1c81fa"}
    params = {"query": address}
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        result = response.json()
        if result['documents']:
            address_info = result['documents'][0]['address']
            return [float(address_info['y']), float(address_info['x'])]
    return [None, None]

# MongoDB에서 데이터 가져오기
address = collection.find({}, {'shop': 1, 'address': 1, '_id': 0})
df_store = pd.DataFrame(address)

# 데이터프레임 구조 확인
st.write("DataFrame Structure:")
st.write(df_store.head())

# 주소를 위도/경도로 변환하여 DataFrame에 추가
df_store[['latitude', 'longitude']] = df_store['address'].apply(lambda x: pd.Series(get_lat_lng(x)))

# 유효한 좌표만 필터링
df_store = df_store.dropna(subset=['latitude', 'longitude'])
df_store['latitude'] = df_store['latitude'].astype(float)
df_store['longitude'] = df_store['longitude'].astype(float)

# 지도 생성
coffee_map = folium.Map(location=[df_store['latitude'].mean(), df_store['longitude'].mean()], zoom_start=12)
for i in df_store.index:
    shop_name = df_store.loc[i, 'shop'] + '-' + df_store.loc[i, 'address']
    popup = folium.Popup(shop_name, max_width=500)
    folium.Marker([df_store.loc[i, 'latitude'], df_store.loc[i, 'longitude']], popup=popup).add_to(coffee_map)

# Streamlit 페이지 설정
st.title('Coffee Bean Stores Map')
st.write('This map shows the locations of Coffee Bean stores.')

# 지도 표시
folium_static(coffee_map)
