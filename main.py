import streamlit as st
import pandas as pd

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="기온 비교 및 전력수요 분석", layout="wide")
st.title("🏙️ 서울-양평 기온 분석 및 전력수요 연계 대시보드")

# 2. 데이터 로드 함수 (오류 방지 로직 보완)
@st.cache_data
def load_all_data():
    try:
        # 파일 읽기 (encoding="cp949")
        seoul_df = pd.read_csv("서울_기온.csv", encoding="cp949")
        yangpyeong_df = pd.read_csv("양평_기온.csv", encoding="cp949")
        power_df = pd.read_csv("전력수요.csv", encoding="cp949")
        
        # 열 이름 공백 제거 (KeyError 방지)
        seoul_df.columns = seoul_df.columns.str.strip()
        yangpyeong_df.columns = yangpyeong_df.columns.str.strip()
        power_df.columns = power_df.columns.str.strip()
        
        # 일시 컬럼을 datetime 형식으로 변환 (오류 데이터는 NaT 처리)
        seoul_df['일시'] = pd.to_datetime(seoul_df['일시'].astype(str).str.strip(), errors='coerce')
        yangpyeong_df['일시'] = pd.to_datetime(yangpyeong_df['일시'].astype(str).str.strip(), errors='coerce')
        power_df['일시'] = pd.to_datetime(power_df['일시'].astype(str).str.strip(), errors='coerce')
        
        # 날짜 누락 및 주요 데이터 결측치 행 제거
        seoul_df = seoul_df.dropna(subset=['일시', '기온(°C)'])
        yangpyeong_df = yangpyeong_df.dropna(subset=['일시', '기온(°C)'])
        power_df = power_df.dropna(subset=['일시', '전력수요(MWh)'])
        
        # 월, 시각 추출
        seoul_df['월'] = seoul_df['일시'].dt.month
        seoul_df['시각'] = seoul_df['일시'].dt.hour
        yangpyeong_df['월'] = yangpyeong_df['일시'].dt.month
        yangpyeong_df['시각'] = yangpyeong_df['일시'].dt.hour
        power_df['월'] = power_df['일시'].dt.month
        
        return seoul_df, yangpyeong_df, power_df
    except Exception as e:
        return None, None, str(e)

# 데이터 불러오기 실행
seoul_data, yangpyeong_data, power_data = load_all_data()

# 에러 예외 처리
if seoul_data is None:
    st.error("❌ 데이터를 로드하는 중 에러가 발생했습니다.")
    if power_data: # 세번째 인자에 에러 메시지가 담겨온 경우
        st.code(power_data)
    st.info("💡 '서울_기온.csv', '양평_기온.csv', '전력수요.csv' 파일이 스크립트와 '같은 폴더'에 있는지 확인해 주세요.")
else:
    # 3. 탭 구성 (st.tabs)
    tab1, tab2 = st.tabs(["🏙️ 탭1: 열섬 분석", "⚡ 탭2: 전력 연결"])
    
    # -------------------------------------------------------------
    # [탭1: 열섬 분석]
    # -------------------------------------------------------------
    with tab1:
        st.header("도시 열섬현상(Urban Heat Island) 분석")
        
        # 기온 데이터 병합
        merged_weather = pd.merge(
            seoul_data[['일시', '월', '시각', '기온(°C)']], 
            yangpyeong_data[['일시', '기온(°C)']], 
            on='일시', 
            suffixes=('_서울', '_양평')
        )
        merged_weather['기온차(서울-양평)'] = merged_weather['기온(°C)_서울'] - merged_weather['기온(°C)_양평']
        
        # ① 1년간 두 지역 기온 변화 (선그래프)
        st.subheader("① 1년간 두 지역 기온 변화")
        line_chart_data = merged_weather.copy()
        line_chart_data.columns = ['일시', '월', '시각', '서울 기온 (°C)', '양평 기온 (°C)', '기온차']
        # 차트 에러 방지를 위해 x축을 컬럼명으로 명시
        st.line_chart(line_chart_data, x='일시', y=['서울 기온 (°C)', '양평 기온 (°C)'])
        
        # 2열 좌우 배치
        col1, col2 = st.columns(2)
        
        with col1:
            # ② 시각(0~23시)별 평균 기온차 (막대그래프)
            st.subheader("② 시각별 평균 기온차 (서울 - 양평)")
            hour_diff = merged_weather.groupby('시각')['기온차(서울-양평)'].mean().reset_index()
            hour_diff.columns = ['시각', '평균 기온차 (°C)']
            # 인덱스 대신 x, y 축 이름을 명확히 지정하여 Vega-Lite 차트 오류 방지
            st.bar_chart(hour_diff, x='시각', y='평균 기온차 (°C)')
            
        with col2:
            # ③ 월(1~12월)별 평균 기온차 (막대그래프)
            st.subheader("③ 월별 평균 기온차 (서울 - 양평)")
            month_diff = merged_weather.groupby('월')['기온차(서울-양평)'].mean().reset_index()
            month_diff.columns = ['월', '평균 기온차 (°C)']
            st.bar_chart(month_diff, x='월', y='평균 기온차 (°C)')

    # -------------------------------------------------------------
    # [탭2: 전력 연결]
    # -------------------------------------------------------------
    with tab2:
        st.header("서울 기온과 전력수요의 관계 분석")
        
        # 서울 기온과 전력수요 병합
        merged_power = pd.merge(
            seoul_data[['일시', '월', '기온(°C)']], 
            power_data[['일시', '전력수요(MWh)']], 
            on='일시'
        )
        
        if len(merged_power) == 0:
            st.warning("⚠️ 서울 기온 데이터와 전력수요 데이터의 '일시' 형식이 일치하지 않아 데이터가 비어있습니다.")
        else:
            # ① 기온(가로)과 전력수요(세로)의 산점도
            st.subheader("① 기온 vs 전력수요 산점도")
            scatter_df = merged_power[['기온(°C)', '전력수요(MWh)']].reset_index(drop=True)
            st.scatter_chart(scatter_df, x='기온(°C)', y='전력수요(MWh)')
            
            # 2열 좌우 배치
            col3, col4 = st.columns(2)
            
            with col3:
                # ② 기온 구간별 평균 전력수요 (막대그래프)
                st.subheader("② 기온 구간별 평균 전력수요")
                # 안전한 정렬과 표기를 위해 기온을 5도 단위 숫자로 그룹화
                merged_power['구간숫자'] = (merged_power['기온(°C)'] // 5 * 5).astype(int)
                temp_bins = merged_power.groupby
