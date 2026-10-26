VD intensity 변수 구축 설명

대상: csdid_ultimately_granted_full7316_controls.dta (기업 단위, 7,316행)
원자료: C:/Users/user/iCloudDrive/5학기/연구미팅/20240108-2010 to 2015 firms/2010 2015 Crunchbase deals merged_v4.xlsx
금액: Money Raised Currency (in USD), 명목 USD. vd_backed 및 first_vd_year는 변경하지 않음.

Table 대응
3-1 vd_initial_usd: 원자료 First VD=1인 딜 금액.
3-2 ln_vd_initial: ln(양수 최초 VD 금액). ln1p_vd_initial도 별도로 제공.
3-3 vd_to_pre_equity: 최초 VD 금액 / 최초 VD 날짜보다 엄격히 이전인 equity 라운드 합계.
3-4 vd_to_prev_equity: 최초 VD 금액 / 직전 equity 라운드 금액. 직전 날짜에 여러 라운드가 있으면 임의 선택하지 않고 결측 처리.
3-5 vd_share_total_capital: 최초 VD / (최초 VD + 이전 누적 equity). 현금잔고나 순자본의 비율이 아니라 누적 조달금액 기준. 같은 날짜 equity는 이전 equity에서 제외하고 별도 열에 제공.
3-6 vd_subseq_rounds: 최초 VD 이후 원자료에 수록된 Debt Financing 라운드 수. 최초 VD와 같은 날짜의 별도 debt 딜도 포함.
3-7 ln1p_vd_subseq: ln(1 + 후속 VD 합계). 후속 라운드가 없는 기업은 0. 양수에만 정의되는 ln_vd_subseq도 별도 제공.
피드백의 누적 노출 및 문서 Table 3-8: vd_cumulative_usd, ln_vd_cumulative, ln1p_vd_cumulative.

정의 및 한계
문서는 결과표이며 로그에 +1을 사용하는지, 후속 관측기간, 분모의 상세 funding-type 규칙을 제시하지 않는다. 따라서 이 파일은 명시한 정의에 따라 새로 구축한 변수이며, 원 회귀 코드의 완전 복제라고 볼 수 없다.
후속 및 누적 변수는 자료에 수록된 전체 후속 기간의 기업별 합계이다. 연도별 누적 노출 변수가 아니며, 패널 회귀에서 과거 연도에 그대로 붙이면 미래 정보를 사용하게 된다. 관측기간 길이도 기업별로 다르다.
원본은 연도 및 혁신 종속변수가 없는 기업 단위 파일이므로 Post, 상호작용 및 회귀계수는 생성하지 않았다.
Equity 분류: Seed, Pre-Seed, Angel, Venture - Series Unknown, Private Equity, Corporate Round, Equity Crowdfunding, Post-IPO Equity, Series A~I(숫자 suffix 포함). Convertible Note, Grant, Secondary Market 등은 제외.
분모의 일부 equity 금액이 미공개이면 누적 분모 전체를 결측으로 처리. 분모 0인 비율은 결측. 같은 날짜는 선후를 판별할 수 없어 이전 equity에서 제외.
후속 VD가 없으면 후속 수/금액은 0. 후속 VD가 있으나 금액이 하나라도 누락되면 합계와 로그는 결측. *_known_usd는 공개분만 더한 하한값이며 완전 합계와 구별해야 한다.
비VD 기업의 신규 intensity 열은 결측으로 유지. VD dummy를 덮어쓰거나 미공개 VD 금액을 0으로 대체하지 않았다.
Galvanize와 Gooten은 원자료 First VD 표시보다 이른 Debt Financing 기록이 있다. 기존 treatment timing을 유지하여 표시된 최초 VD부터 노출을 집계하고 vd_earlier_debt_rounds로 표시. 실제 최초 debt를 기준으로 재정의하려면 처리시점과 intensity를 함께 수정해야 한다.
원자료 Helix에는 동일 이름/딜 번호의 다른 조직 기록이 있으나 비VD 기업이므로 intensity를 계산하지 않는다. VD 기업 내 딜 번호 중복은 검증한다.

검증과 보조 산출물
기존 14개 열의 값과 행 순서를 유지하고, 저장한 Stata 파일을 다시 읽어 비교했다. 원본의 변경 전 사본은 original_before_intensity_*.dta로 보존했다.
variable_dictionary.csv: 모든 신규 변수 정의.
vd_intensity_summary.csv: VD 기업의 요약통계.
observed_vs_missing_comparison.csv: 최초 VD 금액 관측/결측 기업의 기존 특성 비교. 연속/이진 변수는 평균 및 표준화 차이, 산업/지역은 비결측 관측치 내 비율. 기존 funding 변수는 엄격한 사전 equity와 다른 정의일 수 있다.
vd_intensity_deal_audit.csv: VD 기업의 딜별 금액과 최초/후속 VD 및 이전 equity 포함 여부.
vd_intensity_firm_values.csv: 기업별 신규 열.
재현 코드: scripts/add_vd_intensity.py.

실제 구축 결과: 신규 28열. 최초 VD 관측 1,235 / 결측 205. 누적 사전 equity 비율 755, 직전 equity 비율 982, 후속 합계 완전 관측 1,389, 누적 VD 완전 관측 1,198. 엄격한 누락 처리 및 날짜/분류 규칙으로 첨부 표의 비율 표본 1,088과 일치하지 않음. 원 회귀 생성 코드 없이 동일 표본의 복제를 주장하지 않음.
