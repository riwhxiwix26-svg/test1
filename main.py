#실험1
import streamlit as st
 
st.title("하이 웹앱")
st.write("반가워")

#실험2
지역 = st.selectbox("지역을 골라 보세요", ["서울", "양평", "부산"])
st.write("당신이 고른 지역:", 지역)

#실험3
숫자 = st.slider("좋아하는 숫자", 0, 100)
st.write("고른 숫자:", 숫자)
 
if st.button("풍선 날리기"):
	st.balloons()


