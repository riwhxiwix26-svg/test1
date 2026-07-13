<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>열섬현상과 전력수요의 관계 분석 대시보드</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/PapaParse/5.4.1/papaparse.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --primary-blue: #1e3a8a;
            --light-blue: #3b82f6;
            --accent-orange: #f97316;
            --bg-gray: #f8fafc;
            --card-bg: #ffffff;
            --text-dark: #0f172a;
            --text-muted: #64748b;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
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

        /* 세련된 둥근 카드 스타일 UI */
        .card {
            background: var(--card-bg);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -2px rgba(0,0,0,0.05);
            border: 1px solid #e2e8f0;
        }

        header.card {
            background: linear-gradient(135deg, var(--primary-blue), var(--light-blue));
            color: white;
            text-align: center;
            border: none;
        }
        header h1 { margin: 0 0 10px 0; font-size: 2.2rem; font-weight: 800; letter-spacing: -0.05em; }
        header p { margin: 0; font-size: 1.1rem; opacity: 0.95; font-weight: 500; }

        h2 {
            font-size: 1.35rem;
            color: var(--primary-blue);
            margin-top: 0;
            border-bottom: 2px solid #f1f5f9;
            padding-bottom: 10px;
            font-weight: 700;
        }

        /* 필터 섹션 */
        .filter-container {
            display: flex;
            gap: 16px;
            flex-wrap: wrap;
            margin-top: 12px;
        }
        .filter-group { display: flex; flex-direction: column; gap: 6px; }
        .filter-group label { font-size: 0.9rem; font-weight: 600; color: var(--text-muted); }
        select {
            padding: 10px 16px;
            border: 1px solid #cbd5e1;
            border-radius: 10px;
            font-size: 1rem;
            background-color: white;
            color: var(--text-dark);
            font-weight: 500;
            outline: none;
            cursor: pointer;
        }

        /* 통계 메트릭 레이아웃 */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
            margin-top: 20px;
        }
        .stat-item {
            background: #f8fafc;
            border-left: 4px solid var(--light-blue);
            padding: 18px;
            border-radius: 10px;
        }
        .stat-item.orange { border-left-color: var(--accent-orange); }
        .stat-item .value { font-size: 1.7rem; font-weight: 700; color: var(--text-dark); }
        .stat-item .label { font-size: 0.85rem; color: var(--text-muted); margin-top: 4px; font-weight: 600; }

        /* 반응형 캔버스 박스 */
        .chart-box {
            position: relative;
            height: 420px;
            width: 100%;
            margin-top: 16px;
        }
        .grid-2 {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 24px;
        }

        /* 분석 결과 창 */
        .analysis-box {
            background-color: #f0fdf4;
            border: 1px solid #bbf7d0;
            padding: 18px;
            border-radius: 10px;
            margin-top: 16px;
        }
        .warning-text {
            font-size: 0.85rem;
            color: var(--text-muted);
            margin-top: 12px;
            font-style: italic;
            background: #f1f5f9;
            padding: 10px;
            border-radius: 8px;
        }

        /* 에러 오버레이 안내창 */
        #error-overlay {
            display: none;
            background: #fef2f2;
            border: 2px solid #fca5a5;
            color: #991b1b;
            padding: 24px;
            border-radius: 16px;
            margin-bottom: 24px;
        }
        #error-overlay h3 { margin-top: 0; font-size: 1.2rem; }
        #error-overlay ul { margin-bottom: 0; padding-left: 20px; }

        #loading {
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(255,255,255,0.95);
            display: flex; justify-content: center; align-items: center;
            font-size: 1.2rem; font-weight: 700; color: var(--primary-blue); z-index: 9999;
        }

        @media (max-width: 768px) {
            body { padding: 10px; }
            header.card { padding: 20px 15px; }
            header h1 { font-size: 1.6rem; }
            .chart-box { height: 320px; }
            .grid-2 { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>

<div id="loading">📊 2025년 시간별 기상·전력 데이터 융합 및 분석 진행 중...</div>

<div class="container">
    <header class="card">
        <h1>열섬현상과 전력수요의 관계</h1>
        <p>❓ 탐구 질문: 도심 열섬 강도가 커질수록 전력수요도 증가할까?</p>
    </header>

    <div id="error-overlay">
        <h3>❌ 데이터 세트 불러오기 실패</h3>
        <p>동일 경로의 CSV 파일데이터를 웹 브라우저가 정상적으로 수신하지 못했습니다. 아래 원인을 확인해 주세요.</p>
        <ul>
            <li><strong>원인 1 (로컬 브라우저 CORS 제한):</strong> 파일을 다운로드한 뒤 단순히 브라우저 창으로 직접 더블클릭하여 열었을 경우(`file://` 주소 체계) 브라우저 자체 보안 정책에 의해 로컬 CSV 호출이 완벽히 차단됩니다.</li>
            <li><strong>해결 방법 1 (강력 추천):</strong> 본 <code>index.html</code> 파일과 데이터 파일들을 본인의 <strong>GitHub 저장소(Repository)</strong> 메인 경로에 함께 올린 뒤, <strong>GitHub Pages</strong> 기능을 활성화하여 웹 배포 링크로 접속하시면 아무런 에러 없이 즉시 정상 작동합니다!</li>
            <li><strong>원인 2 (파일명 불일치):</strong> 폴더 내에 <code>서울_기온.csv</code>, <code>양평_기온.csv</code>, <code>전력수요.csv</code> 파일의 이름이나 확장자가 달라 매칭이 안 될 수 있습니다.</li>
        </ul>
    </div>

    <section class="card">
        <h2>📊 2. 데이터 개요 및 조건 필터</h2>
        <p>본 대시보드는 2025년 1년 동안 수집된 실시간 시간별 데이터(8,760건)를 융합하여 분석합니다. 서울(도심)과 양평(교외)의 기온차를 기반으로 열섬 지표를 산출하여 매칭합니다.</p>
        
        <div class="filter-container">
            <div class="filter-group">
                <label for="month-filter">📅 분석 대상 시기 선택</label>
                <select id="month-filter" onchange="updateDashboard()">
                    <option value="all">연간 전체 데이터 범위</option>
                    <option value="hot">🔥 기온이 높은 시기 비교 (7월 ~ 8월 여름철)</option>
                    <option value="cold">❄️ 기온이 낮은 시기 비교 (12월 ~ 2월 겨울철)</option>
                </select>
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat-item"><div class="value" id="stat-seoul">- °C</div><div class="label">서울 평균 기온</div></div>
            <div class="stat-item"><div class="value" id="stat-yangpyeong">- °C</div><div class="label">양평 평균 기온</div></div>
            <div class="stat-item orange"><div class="value" id="stat-uhi">- °C</div><div class="label">평균 열섬 강도 (도심-교외)</div></div>
            <div class="stat-item"><div class="value" id="stat-power">- MWh</div><div class="label">평균 전력수요</div></div>
        </div>
    </section>

    <section class="card">
        <h2>🏙️ 3. 열섬현상 분석 (도심 및 교외 기온 비교)</h2>
        <p>동일한 일시 조건 하의 <strong>‘열섬 강도 = 도심 기온(서울) - 교외 기온(양평)’</strong> 공식을 정밀 적용한 시계열 변동 그래프입니다.</p>
        <div class="chart-box">
            <canvas id="weatherLineChart"></canvas>
        </div>
    </section>

    <section class="card">
        <h2>⚡ 4. 전력수요 분석 (시간 흐름 및 추세 변화)</h2>
        <p>선택된 시기 내의 시간 및 날짜 변동성에 따른 전력수요(MWh)의 등락 패턴을 나타냅니다.</p>
        <div class="chart-box">
            <canvas id="powerLineChart"></canvas>
        </div>
    </section>

    <section class="card">
        <h2>📈 5. 상관관계 분석 및 통계 모델링</h2>
        <p>열섬 강도를 독립변수(X축), 전력수요를 종속변수(Y축)로 결합하여 도출한 데이터 플롯 분포와 최소자승법 기반 일차 선형 추세선입니다.</p>
        <div class="grid-2">
            <div class="chart-box">
                <canvas id="correlationScatterChart"></canvas>
            </div>
            <div>
                <h3>🔗 피어슨 상관계수 진단 연계</h3>
                <div class="stat-item orange" style="margin-bottom: 16px;">
                    <div class="value" id="pearson-r">r = -.--</div>
                    <div class="label">피어슨 상관계수 (Pearson Coefficient)</div>
                </div>
                <div class="analysis-box">
                    <strong>데이터 자동 연산 해석:</strong>
                    <div id="interpretation-text" style="margin-top: 8px; font-weight: bold; color: var(--primary-blue);">로딩 중...</div>
                </div>
                <p class="warning-text">💡 상관관계 분석 주의사항: 통계학적 상관관계가 발견되더라도 이것이 반드시 두 지표 간의 직접적인 원인과 결과를 유도하는 인과관계(Causality)를 증명하는 것은 아닙니다. 전력 소비에는 폭염/한파 시의 냉난방 외에도 산업용 소비, 요일별 조업 강도 등 복합적인 환경 요인이 작용함을 인지해야 합니다.</p>
            </div>
        </div>
    </section>

    <section class="card" style="background-color: #f8fafc; border: 1px solid #cbd5e1;">
        <h2>📝 6. 실측 데이터 기반 탐구 결과 요약</h2>
        <div id="summary-content" style="white-space: pre-line; font-weight: 500;">분석 연산 처리 후 실제 수치 기반 요약문이 표시됩니다.</div>
    </section>
</div>

<script>
    let masterDataset = [];
    let activeCharts = {};

    // 1. CSV 데이터 호출 및 동일 일시 조인 처리
    async function initializeApp() {
        try {
            const [seoulTxt, yangpyeongTxt, powerTxt] = await Promise.all([
                fetch('서울_기온.csv').then(res => { if(!res.ok) throw new Error(); return res.text(); }),
                fetch('양평_기온.csv').then(res => { if(!res.ok) throw new Error(); return res.text(); }),
                fetch('전력수요.csv').then(res => { if(!res.ok) throw new Error(); return res.text(); })
            ]);

            // cp949 인코딩 파일 한글 호환 파싱 기본 처리
            const seoulData = Papa.parse(seoulTxt, { header: true, skipEmptyLines: true }).data;
            const yangpyeongData = Papa.parse(yangpyeongTxt, { header: true, skipEmptyLines: true }).data;
            const powerData = Papa.parse(powerTxt, { header: true, skipEmptyLines: true }).data;

            // 해시 맵 구조 변환으로 데이터 조회 성능 최적화
            const yangpyeongMap = new Map(yangpyeongData.map(d => [d['일시']?.trim(), parseFloat(d['기온(°C)'])]));
            const powerMap = new Map(powerData.map(d => [d['일시']?.trim(), parseFloat(d['전력수요(MWh)'])]));

            masterDataset = seoulData.map(s => {
                const dateKey = s['일시']?.trim();
                const seoulTemp = parseFloat(s['기온(°C)']);
                const yangpyeongTemp = yangpyeongMap.get(dateKey);
                const electricityDemand = powerMap.get(dateKey);

                if (!dateKey || isNaN(seoulTemp) || isNaN(yangpyeongTemp) || isNaN(electricityDemand)) return null;

                return {
                    time: dateKey,
                    month: parseInt(dateKey.substring(5, 7)),
                    seoul: seoulTemp,
                    yangpyeong: yangpyeongTemp,
                    uhi: seoulTemp - yangpyeongTemp, // 열섬 강도 산출식 명시 적용
                    power: electricityDemand
                };
            }).filter(d => d !== null);

            document.getElementById('loading').style.display = 'none';
            updateDashboard();

        } catch (e) {
            document.getElementById('loading').style.display = 'none';
            document.getElementById('error-overlay').style.display = 'block';
        }
    }

    // 2. 대시보드 상태 필터 처리 로직
    function updateDashboard() {
        const selectedMode = document.getElementById('month-filter').value;
        let filtered = [];

        if (selectedMode === 'all') {
            filtered = masterDataset;
        } else if (selectedMode === 'hot') {
            filtered = masterDataset.filter(d => d.month === 7 || d.month === 8);
        } else if (selectedMode === 'cold') {
            filtered = masterDataset.filter(d => d.month === 12 || d.month === 1 || d.month === 2);
        }

        if (filtered.length === 0) return;

        // 평균값 통계 가공
        const avgSeoul = filtered.reduce((sum, d) => sum + d.seoul, 0) / filtered.length;
        const avgYang = filtered.reduce((sum, d) => sum + d.yangpyeong, 0) / filtered.length;
        const avgUhi = filtered.reduce((sum, d) => sum + d.uhi, 0) / filtered.length;
        const avgPower = filtered.reduce((sum, d) => sum + d.power, 0) / filtered.length;

        document.getElementById('stat-seoul').innerText = avgSeoul.toFixed(2) + ' °C';
        document.getElementById('stat-yangpyeong').innerText = avgYang.toFixed(2) + ' °C';
        document.getElementById('stat-uhi').innerText = avgUhi.toFixed(2) + ' °C';
        document.getElementById('stat-power').innerText = Math.round(avgPower).toLocaleString() + ' MWh';

        // 상관계수 계산
        const rCoeff = calcPearsonCorrelation(filtered);
        document.getElementById('pearson-r').innerText = `r = ${rCoeff.toFixed(3)}`;
        
        let interpretation = "";
        let interpretTag = "";
        const absR = Math.abs(rCoeff);

        if (absR < 0.1) {
            interpretation = "상관관계가 거의 없거나 분석 수준에서 경미하게 약함";
            interpretTag = "상관관계가 약함";
        } else if (absR < 0.3) {
            interpretation = `약한 ${rCoeff > 0 ? '양의 상관관계' : '음의 상관관계'}`;
            interpretTag = `${
