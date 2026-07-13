import streamlit as st
import pandas as pd

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="기온 비교 및 전력수요 분석", layout="wide")
st.title("🏙️ 서울-양평 기온 분석 및 전력수요 연계 대시보드 (오류 보완판)")

# 2. 데이터 로드 함수 (캐싱 적용 및 오류 방지 로직 추가)
@st.cache_data
def load_all_data():
    try:
        # 파일 읽기 (요구사항: cp949 인코딩 적용)
        seoul_df = pd.read_csv("서울_기온.csv", encoding="cp949")
        yangpyeong_df = pd.read_csv("양평_기온.csv", encoding="cp949")
        power_df = pd.read_csv("전력수요.csv", encoding="cp949")
        
        # [오류 방지] 열 이름의 앞뒤 공백 제거
        seoul_df.columns = seoul_df.columns.str.strip()
        yangpyeong_df.columns = yangpyeong_df.columns.str.strip()
        power_df.columns = power_df.columns.str.strip()
        
        # [오류 방지] 일시 컬럼의 문자열 공백 제거 후 datetime 형식으로 변환
        seoul_df['일시'] = pd.to_datetime(seoul_df['일시'].astype(str).str.strip(), errors='coerce')
        yangpyeong_df['일시'] = pd.to_datetime(yangpyeong_df['일시'].astype(str).str.strip(), errors='coerce')
        power_df['일시'] = pd.to_datetime(power_df['일시'].astype(str).str.strip(), errors='coerce')
        
        # [오류 방지] 날짜 변환 실패(NaT) 데이터 제거 및 기온/전력 결측치 제거
        seoul_df = seoul_df.dropna(subset=['일시', '기온(°C)'])
        yangpyeong_df = yangpyeong_df.dropna(subset=['일시', '기온(°C)'])
        power_df = power_df.dropna(subset=['일시', '전력수요(MWh)'])
        
        # 분석에 필요한 월, 시각 컬럼 추출
        seoul_df['월'] = seoul_df['일시'].dt.month
        seoul_df['시각'] = seoul_df['일시'].dt.hour
        yangpyeong_df['월'] = yangpyeong_df['일시'].dt.month
        yangpyeong_df['시각'] = yangpyeong_df['일시'].dt.hour
        power_df['월'] = power_df['일시'].dt.month
        
        return seoul_df, yangpyeong_df, power_df
    except FileNotFoundError as e:
        # 파일이 없을 때 캐시 함수 내부가 아닌 메인 로직에서 처리하도록 None 반환
        return None, None, None
    except KeyError as e:
        st.error(f"❌ CSV 파일의 열(Column) 이름을 확인해주세요. 에러 위치: {e}")
        return None, None, None

# 데이터 불러오기 실행
seoul_data, yangpyeong_data, power_data = load_all_data()

if seoul_data is None:
    st.error("❌ 데이터를 로드하지 못했습니다. `서울_기온.csv`, `양평_기온.csv`, `전력수요.csv` 세 파일이 이 스크립트와 **같은 폴더**에 있는지 꼭 확인해주세요.")
else:
    # 3. 탭 구성 (st.tabs)
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
            
        with col2:
            # ③ 월(1~12월)별 평균 기온차 (막대그래프)
            st.subheader("③ 월별 평균 기온차 (서울 - 양평)")
            month_diff = merged_weather.groupby('월')['기온차(서울-양평)'].mean().reset_index()
            month_diff = month_diff.set_index('월')
            month_diff.columns = ['평균 기온차 (°C)']
            st.bar_chart(month_diff)

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
        
        if len(merged_power) == 0:
            st.warning("⚠️ 서울 기온 데이터와 전력수요 데이터의 '일시' 형식이 일치하지 않아 병합된 데이터가 없습니다. 두 파일의 날짜 형식을 확인해주세요.")
        else:
            # ① 기온(가로)과 전력수요(세로)의 산점도
            st.subheader("① 기온 vs 전력수요 산점도")
            scatter_df = merged_power[['기온(°C)', '전력수요(MWh)']]
            st.scatter_chart(scatter_df, x='기온(°C)', y='전력수요(MWh)')
            
            # 2열 좌우 배치
            col3, col4 = st.columns(2)
            
            with col3:
                # ② 기온 구간별 평균 전력수요 (막대그래프)
                st.subheader("② 기온 구간별 평균 전력수요")
                temp_grouped = (merged_power['기온(°C)'] // 5 * 5).astype(int)
                temp_bins = merged_power.groupby(temp_grouped)['전력수요(MWh)'].mean().reset_index()
                
                # 정렬 및 출력용 문자열 생성
                temp_bins['기온구간'] = temp_bins['기온(°C)'].astype(str) + " ~ " + (temp_bins['기온(°C)'] + 5).astype(str) + "°C"
                temp_bins = temp_bins.sort_values(by='기온(°C)').set_index('기온구간')[['전력수요(MWh)']]
                st.bar_chart(temp_bins)
                
            with col4:
                # ③ 월(1~12월)별 평균 전력수요 (막대그래프)
                st.subheader("③ 월별 평균 전력수요")
                monthly_power = merged_power.groupby('월')['전력수요(MWh)'].mean().reset_index()
                monthly_power = monthly_power.set_index('월')
                st.bar_chart(monthly_power)
