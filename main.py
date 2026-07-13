import streamlit as st
import pandas as pd

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="기온 비교 및 전력수요 분석", layout="wide")
st.title("🏙️ 서울-양평 기온 분석 및 전력수요 연계 대시보드")

# 2. 데이터 로드 함수 (캐싱 적용으로 로딩 속도 최적화)
@st.cache_data
def load_all_data():
    # 파일 읽기 (요구사항: cp949 인코딩 적용)
    seoul_df = pd.read_csv("서울_기온.csv", encoding="cp949")
    yangpyeong_df = pd.read_csv("양평_기온.csv", encoding="cp949")
    power_df = pd.read_csv("전력수요.csv", encoding="cp949")
    
    # 일시 컬럼을 datetime 형식으로 변환
    seoul_df['일시'] = pd.to_datetime(seoul_df['일시'])
    yangpyeong_df['일시'] = pd.to_datetime(yangpyeong_df['일시'])
    power_df['일시'] = pd.to_datetime(power_df['일시'])
    
    # 분석에 필요한 월, 시각 컬럼 추출
    for df in [seoul_df, yangpyeong_df]:
        df['월'] = df['일시'].dt.month
        df['시각'] = df['일시'].dt.hour
        
    power_df['월'] = power_df['일시'].dt.month
    
    return seoul_df, yangpyeong_df, power_df

try:
    # 데이터 불러오기
    seoul_data, yangpyeong_data, power_data = load_all_data()
    
    # 3. 탭 구성 (요구사항: st.tabs 사용)
    tab1, tab2 = st.tabs(["🏙️ 탭1: 열섬 분석", "⚡ 탭2: 전력 연결"])
    
    # -------------------------------------------------------------
    # [탭1: 열섬 분석]
    # -------------------------------------------------------------
    with tab1:
        st.header("도시 열섬현상(Urban Heat Island) 분석")
        
        # 데이터 병합 (서울과 양평 기온 일시 기준 맞춤)
        merged_weather = pd.merge(
            seoul_data[['일시', '월', '시각', '기온(°C)']], 
            yangpyeong_data[['일시', '기온(°C)']], 
            on='일시', 
            suffixes=('_서울', '_양평')
        )
        merged_weather['기온차(서울-양평)'] = merged_weather['기온(°C)_서울'] - merged_weather['기온(°C)_양평']
        
        # ① 1년간 두 지역 기온 변화 (선그래프)
        st.subheader("① 1년간 두 지역 기온 변화")
        line_chart_data = merged_weather.set_index('일시')[['기온(°C)_서울', '기온(°C)_양평']]
        line_chart_data.columns = ['서울 기온 (°C)', '양평 기온 (°C)']
        st.line_chart(line_chart_data)
        
        # 2열 좌우 배치
        col1, col2 = st.columns(2)
        
        with col1:
            # ② 시각(0~23시)별 평균 기온차 (막대그래프)
            st.subheader("② 시각별 평균 기온차 (서울 - 양평)")
            hour_diff = merged_weather.groupby('시각')['기온차(서울-양평)'].mean().reset_index()
            hour_diff = hour_diff.set_index('시각')
            hour_diff.columns = ['평균 기온차 (°C)']
            st.bar_chart(hour_diff)
            st.caption("💡 주로 인공열 방출이 축적되는 야간 시간대에 서울 기온이 크게 올라갑니다.")
            
        with col2:
            # ③ 월(1~12월)별 평균 기온차 (막대그래프)
            st.subheader("③ 월별 평균 기온차 (서울 - 양평)")
            month_diff = merged_weather.groupby('월')['기온차(서울-양평)'].mean().reset_index()
            month_diff = month_diff.set_index('월')
            month_diff.columns = ['평균 기온차 (°C)']
            st.bar_chart(month_diff)
            st.caption("💡 계절적 기후 특징 및 복사 냉각 조건에 따라 월별 편차가 다르게 관측됩니다.")

    # -------------------------------------------------------------
    # [탭2: 전력 연결]
    # -------------------------------------------------------------
    with tab2:
        st.header("서울 기온과 전력수요의 관계 분석")
        
        # 데이터 병합 (서울 기온과 전력수요 일시 기준 맞춤)
        merged_power = pd.merge(
            seoul_data[['일시', '월', '기온(°C)']], 
            power_data[['일시', '전력수요(MWh)']], 
            on='일시'
        )
        
        # ① 기온(가로)과 전력수요(세로)의 산점도
        st.subheader("① 기온 vs 전력수요 산점도")
        scatter_df = merged_power[['기온(°C)', '전력수요(MWh)']]
        # 외부 라이브러리 없이 st.scatter_chart를 활용한 산점도 구현
        st.scatter_chart(scatter_df, x='기온(°C)', y='전력수요(MWh)')
        st.caption("💡 기온이 매우 낮을 때(동절기 난방)와 기온이 매우 높을 때(하절기 냉방) 전력수요가 양쪽으로 올라가는 U자형(혹은 V자형) 분포를 보입니다.")
        
        # 2열 좌우 배치
        col3, col4 = st.columns(2)
        
        with col3:
            # ② 기온 구간별 평균 전력수요 (막대그래프)
            st.subheader("② 기온 구간별 평균 전력수요")
            # 5도 단위 기온 구간화 및 보기 좋은 라벨 정렬
            temp_grouped = (merged_power['기온(°C)'] // 5 * 5).astype(int)
            temp_bins = merged_power.groupby(temp_grouped)['전력수요(MWh)'].mean().reset_index()
            temp_bins['기온구간'] = temp_bins['기온(°C)'].astype(str) + " ~ " + (temp_bins['기온(°C)'] + 5).astype(str) + "°C"
            temp_bins = temp_bins.set_index('기온구간')[['전력수요(MWh)']]
            st.bar_chart(temp_bins)
            st.caption("💡 극한 기온대(폭염 및 한파) 구간에서 평균 전력수요가 두드러지게 증가합니다.")
            
        with col4:
            # ③ 월(1~12월)별 평균 전력수요 (막대그래프)
            st.subheader("③ 월별 평균 전력수요")
            monthly_power = merged_power.groupby('월')['전력수요(MWh)'].mean().reset_index()
            monthly_power = monthly_power.set_index('월')
            st.bar_chart(monthly_power)
            st.caption("💡 주로 냉·난방기 가동이 집중되는 한여름(7~8월)과 한겨울(12~1월)에 전력이 높게 소비됩니다.")

except FileNotFoundError:
    st.error("❌ 필수 데이터를 찾을 수 없습니다. `서울_기온.csv`, `양평_기온.csv`, `전력수요.csv` 세 파일이 스크립트 파일과 **같은 폴더**에 있는지 확인해주세요.")
