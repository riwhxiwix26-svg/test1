import streamlit as st
import pandas as pd

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="서울-양평 도시 열섬현상 분석", layout="wide")
st.title("🏙️ 서울 vs 🌲 양평 기온 데이터 비교")
st.markdown("### 도시 열섬현상(Urban Heat Island) 분석 웹 애플리케이션")

# 2. 데이터 로드 함수 (캐싱을 적용하여 속도 향상)
@st.cache_data
def load_data():
    # 파일 읽기 (요구사항: cp949 인코딩 적용)
    seoul_df = pd.read_csv("서울_기온.csv", encoding="cp949")
    yangpyeong_df = pd.read_csv("양평_기온.csv", encoding="cp949")
    
    # 일시 컬럼을 datetime 형식으로 변환
    seoul_df['일시'] = pd.to_datetime(seoul_df['일시'])
    yangpyeong_df['일시'] = pd.to_datetime(yangpyeong_df['일시'])
    
    # 분석에 필요한 월, 시각 컬럼 추출
    for df in [seoul_df, yangpyeong_df]:
        df['월'] = df['일시'].dt.month
        df['시각'] = df['일시'].dt.hour
        
    return seoul_df, yangpyeong_df

try:
    # 데이터 불러오기
    seoul_data, yangpyeong_data = load_data()
    
    # 두 데이터셋을 '일시' 기준으로 병합
    merged_data = pd.merge(
        seoul_data[['일시', '월', '시각', '기온(°C)']], 
        yangpyeong_data[['일시', '기온(°C)']], 
        on='일시', 
        suffixes=('_서울', '_양평')
    )
    # 두 지역의 기온차 계산 (서울 - 양평)
    merged_data['기온차(서울-양평)'] = merged_data['기온(°C)_서울'] - merged_data['기온(°C)_양평']

    # 사이드바 데이터 요약 정보 제공
    st.sidebar.header("📊 데이터 요약 정보")
    st.sidebar.write("**데이터 기간:** 2025년 1년치 (시간별)")
    st.sidebar.write(f"**총 관측 데이터 수:** {len(merged_data):,}개")
    st.sidebar.write(f"**서울 평균 기온:** {seoul_data['기온(°C)'].mean():.2f}°C")
    st.sidebar.write(f"**양평 평균 기온:** {yangpyeong_data['기온(°C)'].mean():.2f}°C")
    st.sidebar.write(f"**평균 기온차(서울-양평):** {merged_data['기온차(서울-양평)'].mean():.2f}°C")

    # 메인 화면 그래프 시각화 영역
    st.write("---")
    
    # ① 1년간 두 지역의 기온 변화 (선그래프)
    st.subheader("① 1년간 두 지역의 기온 변화")
    line_chart_data = merged_data.set_index('일시')[['기온(°C)_서울', '기온(°C)_양평']]
    line_chart_data.columns = ['서울 기온 (°C)', '양평 기온 (°C)']
    st.line_chart(line_chart_data)
    
    # 하단 2열(Column) 레이아웃 구성
    col1, col2 = st.columns(2)
    
    with col1:
        # ② 시각(0~23시)별 평균 기온차 (막대그래프)
        st.subheader("② 시각별 평균 기온차 (서울 - 양평)")
        hour_diff = merged_data.groupby('시각')['기온차(서울-양평)'].mean().reset_index()
        hour_diff = hour_diff.set_index('시각')
        hour_diff.columns = ['평균 기온차 (°C)']
        st.bar_chart(hour_diff)
        st.caption("💡 도시의 인공열 및 콘크리트 축열 영향으로 주로 야간과 새벽 시간에 서울의 기온이 양평보다 현저히 높게 나타납니다.")

    with col2:
        # ③ 월(1~12월)별 평균 기온차 (막대그래프)
        st.subheader("③ 월별 평균 기온차 (서울 - 양평)")
        month_diff = merged_data.groupby('월')['기온차(서울-양평)'].mean().reset_index()
        month_diff = month_diff.set_index('월')
        month_diff.columns = ['평균 기온차 (°C)']
        st.bar_chart(month_diff)
        st.caption("💡 계절에 따른 일사량 차이와 대기 순환 상태에 따라 월별 기온 편차가 다르게 나타납니다.")

    # 4. 데이터프레임 확인 기능 (선택사항)
    st.write("---")
    if st.checkbox("전체 통합 데이터프레임 확인하기"):
        st.subheader("📋 데이터셋 샘플 (상위 100행)")
        st.dataframe(merged_data.head(100))

except FileNotFoundError:
    st.error("❌ 파일을 찾을 수 없습니다. `서울_기온.csv`와 `양평_기온.csv` 파일이 현재 실행하는 스크립트(`app.py`)와 **같은 폴더**에 있는지 확인해주세요.")
