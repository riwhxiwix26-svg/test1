<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>열섬현상과 전력수요의 관계 분석</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/PapaParse/5.4.1/papaparse.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --primary-blue: #1e3a8a;
            --light-blue: #3b82f6;
            --accent-orange: #f97316;
            --bg-gray: #f1f5f9;
            --card-bg: #ffffff;
            --text-dark: #0f172a;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: var(--bg-gray);
            color: var(--text-dark);
            margin: 0;
            padding: 20px;
            line-height: 1.6;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        /* 둥근 카드 형태 디자인 */
        .card {
            background: var(--card-bg);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        }

        header.card {
            background: linear-gradient(135deg, var(--primary-blue), var(--light-blue));
            color: white;
            text-align: center;
        }
        header h1 { margin: 0 0 8px 0; font-size: 2rem; font-weight: 800; }
        header p { margin: 0; font-size: 1.1rem; opacity: 0.9; }

        h2 {
            font-size: 1.4rem;
            color: var(--primary-blue);
            margin-top: 0;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 8px;
        }

        .filter-container {
            display: flex;
            gap: 16px;
            flex-wrap: wrap;
            margin-top: 12px;
        }
        .filter-group { display: flex; flex-direction: column; gap: 4px; }
        select {
            padding: 8px 16px;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            font-size: 1rem;
            background-color: white;
        }

        /* 대시보드 메트릭 구조 */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
            margin-top: 20px;
        }
        .stat-item {
            background: #f8fafc;
            border-left: 4px solid var(--light-blue);
            padding: 16px;
            border-radius: 8px;
        }
        .stat-item.orange { border-left-color: var(--accent-orange); }
        .stat-item .value { font-size: 1.6rem; font-weight: 700; color: var(--text-dark); }
        .stat-item .label { font-size: 0.85rem; color: #64748b; margin-top: 4px; }

        /* 반응형 차트 레이아웃 */
        .chart-box {
            position: relative;
            height: 400px;
            width: 100%;
            margin-top: 16px;
        }
        .grid-2 {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 24px;
        }

        /* 분석 해석 결과 창 */
        .analysis-box {
            background-color: #f0fdf4;
            border: 1px solid #bbf7d0;
            padding: 16px;
            border-radius: 8px;
            margin-top: 16px;
        }
        .warning-text {
            font-size: 0.85rem;
            color: #64748b;
            margin-top: 8px;
            font-style: italic;
        }

        /* 에러 메시지 안내 레이어 */
        #error-overlay {
            display: none;
            background: #fef2f2;
            border: 2px solid #fca5a5;
            color: #991b1b;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 24px;
        }
        #error-overlay h3 { margin-top: 0; }
        #error-overlay ul { margin-bottom: 0; padding-left: 20px; }

        #loading {
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(255,255,255,0.9);
            display: flex; justify-content: center; align-items: center;
            font-size: 1.3rem; font-weight: bold; z-index: 999;
        }

        @media (max-width: 768px) {
            body { padding: 10px; }
            header h1 { font-size: 1.6rem; }
            .chart-box { height: 300px; }
        }
    </style>
</head>
<body>

<div id="loading">⏳ 2025년 데이터셋 융합 및 상관관계 분석 중...</div>

<div class="container">
    <header class="card">
        <h1>열섬현상과 전력수요의 관계</h1>
        <p>❓ 탐구 질문: 도심 열섬 강도가 커질수록 전력수요도 증가할까?</p>
    </header>

    <div id="error-overlay">
        <h3>❌ 데이터 파일 로드 실패 안내</h3>
        <p>웹앱 폴더 내에서 필수 CSV 데이터를 읽어오지 못했습니다. 아래 원인과 해결 방법을 확인해 주세요.</p>
        <ul>
            <li><strong>원인 1 (CORS 보안 정책):</strong> GitHub Pages가 아닌 로컬 컴퓨터에서 `index.html` 파일을 더블 클릭해 실행하면 브라우저 보안 정책상 파일 읽기가 차단됩니다.</li>
            <li><strong>해결 방법 1:</strong> 본 코드를 GitHub 저장소에 업로드한 후 <strong>GitHub Pages</strong> 기능을 켜서 웹 링크로 접속하시면 정상 작동합니다. 또는 VS Code의 Live Server 플러그인을 사용하세요.</li>
            <li><strong>원인 2 (파일명 불일치):</strong> 동일 폴더 내에 <code>서울_기온.csv</code>, <code>양평_기온.csv</code>, <code>전력수요.csv</code> 파일이 존재하지 않거나 이름이 다를 수 있습니다.</li>
        </ul>
    </div>

    <section class="card">
        <h2>📊 2025년 관측 데이터 개요</h2>
        <p>기상청 및 전력거래소의 <strong>2025년 1년치 시간별 데이터(총 8,760개 행 모델)</strong>를 기준으로 합니다. 도심(서울)과 교외(양평)의 동시간대 기온 차이를 통해 '열섬 강도'를 산출하고 전력수요와의 연계성을 실증합니다.</p>
        
        <div class="filter-container">
            <div class="filter-group">
                <label for="month-filter">📅 기온 조건 필터</label>
                <select id="month-filter" onchange="updateDashboard()">
                    <option value="all">연간 전체 데이터</option>
                    <option value="hot">🔥 기온 높은 시기 (7월 ~ 8월 여름철)</option>
                    <option value="cold">❄️ 기온 낮은 시기 (12월 ~ 2월 겨울철)</option>
                </select>
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat-item"><div class="value" id="stat-seoul">- °C</div><div class="label">서울 평균 기온</div></div>
            <div class="stat-item"><div class="value" id="stat-yangpyeong">- °C</div><div class="label">양평 평균 기온</div></div>
            <div class="stat-item orange"><div class="value" id="stat-uh
