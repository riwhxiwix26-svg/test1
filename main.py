import streamlit as st
import pandas as pd

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="기온 비교 및 전력수요 분석", layout="wide")
st.title("🏙️ 서울-양평 기온 분석 및 전력수요 연계 대시보드")

# 2. 데이터 로드 함수 (캐싱 및 전처리 적용)
@st.cache_data
def load_all_data():
    try:
        # 파일 읽기 (요구사항: cp949 인코딩 적용)
        seoul_df = pd.read_csv("서울_기온.csv", encoding="cp949")
        yangpyeong_df = pd.read_csv("양평_기온.csv", encoding="cp949")
        power_df = pd.read_csv("전력수요.csv", encoding="cp949")
        
        # 열 이름 공백 제거 (KeyError 방지)
        seoul_df.columns = seoul_df.columns.str.strip()
        yangpyeong_df.columns = yangpyeong_df.columns.str.strip()
        power_df.columns = power_df.columns.str.strip()
        
        # 일시 컬럼을 datetime 형식으로 변환 (포맷 불일치 방지)
        seoul_df['일시'] = pd.to_datetime(seoul_df['일시'].astype(str).str.strip(), errors='coerce')
        yangpyeong_df['일시'] = pd.to_datetime(yangpyeong_df['일시'].astype(str).str.strip(), errors='coerce')
        power_df['일시'] = pd.to_datetime(power_df['일시'].astype(str).str.strip(), errors='coerce')
        
        # 데이터 누락(결측치) 행 제거
        seoul_df = seoul_df.dropna(subset=['일시', '기온(°C)'])
        yangpyeong_df = yangpyeong_df.dropna(subset=['일시', '기온(°C)'])
        power_df = power_df.dropna(subset=['일시', '전력수요(MWh)'])
        
        # 분석에 필요한 월, 시각 컬럼 미리 추출
        seoul_df['월'] = seoul_df['일시'].dt.month
        seoul_df['시각'] = seoul_df['일시'].dt.hour
        yangpyeong_df['월'] = yangpyeong_df['일시'].dt.month
        yangpyeong_df['시각'] = yangpyeong_df['일시'].dt.hour
        power_df['월'] = power_df['일시'].dt.month
        
        return seoul_df, yangpyeong_df, power_df, None
    except Exception as e:
        return None, None, None, str(e)

# 데이터 불러오기 실행
seoul_data, yangpyeong_data, power_data, error_msg = load_all_data()

# 데이터 로드 에러 예외 처리
if error_msg:
    st.error(f"❌ 데이터를 로드하는 중 오류가 발생했습니다: {error_msg}")
    st.info("💡 '서울_기온.csv', '양평_기온.csv', '전력수요.csv' 파일이 스크립트 파일과 같은 폴더에 있는지 확인해 주세요.")
else:
    # 3. 탭 구성 (요구사항: st.tabs 사용)
    tab1, tab2 = st.tabs(["🏙️ 탭1: 열섬 분석", "⚡ 탭2: 전력 연결"])
    
    # -------------------------------------------------------------
    # [탭1: 열섬 분석]
    # -------------------------------------------------------------
    with tab1:
        st.header("도시 열섬현상(Urban Heat Island) 분석")
        
        # 서울과 양평 기온 데이터 병합 (같은 일시 기준)
        merged_weather = pd.merge(
            seoul_data[['일시', '월', '시각', '기온(°C)']], 
            yangpyeong_data
