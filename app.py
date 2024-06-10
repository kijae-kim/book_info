import streamlit as st
import requests

st.title('광고 문구 서비스앱')
generate_ad_url = 'http://127.0.0.1:8000/create_ad'

product_name = st.text_input('도서 이름')
details = st.text_input('도서 정보')
options = st.multiselect('광고 문구의 느낌', options=['기본', '재밌게', '차분하게', '과장스럽게', '참신하게', '고급스럽게'], default=['기본'])

if st.button("광고 문구 생성하기"):
    try:
        response = requests.post(
            generate_ad_url,
            json={"product_name": product_name,
                "details": details,
                "tone_and_manner": ", ".join(options)})
        ad = response.json()['ad']
        st.success(ad)
    except:
        st.error("연결 실패!")