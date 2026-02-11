#!/usr/bin/env python3
"""
완전한 10개 변수 입력 테스트
- 입찰 공고 변수 (6개)
- 기업 특성 변수 (4개)
"""

import pandas as pd
from valuation_engine_v14 import ValuationEngine

# CSV 로드 (10개 변수 완전 입력)
df = pd.read_csv('realistic_10projects_complete.csv')

print("=" * 80)
print("완전한 10개 변수 입력 테스트")
print("=" * 80)
print("\n[입력 데이터 확인]")
print(df.head(3))
print(f"\n총 {len(df)}개 프로젝트, {len(df.columns)}개 변수")

# 엔진 실행
print("\n[평가 실행 중...]")
engine = ValuationEngine(n_simulations=5000)
results_df, sensitivity = engine.run_valuation(df)

print("\n[결과 요약]")
print("=" * 100)
print(f"{'PID':<6} {'Contract':>8} {'Firm':>8} {'BIM_Y':>6} {'Exp':>5} {'Util':>6} | "
      f"{'NPV':>8} {'ROV':>8} {'TPV':>8} {'Ratio':>7} | {'Decision':<15}")
print("-" * 100)

for _, row in results_df.iterrows():
    # 입력 정보
    pid = row['project_id']
    contract = row['contract_amount']

    # 원본 데이터에서 기업 정보 가져오기
    orig = df[df['project_id'] == pid].iloc[0]
    firm = orig['firm_size']
    bim_y = orig['bim_years']
    exp = orig['same_type_count']
    util = orig['current_utilization']

    # 결과
    npv = row['npv']
    rov = row['rov_net']
    tpv = row['tpv']
    ratio = tpv / npv if npv != 0 else 0
    decision = row['tpv_decision']

    print(f"{pid:<6} {contract:>8.0f} {firm:>8} {bim_y:>6} {exp:>5} {util:>6.2f} | "
          f"{npv:>8.1f} {rov:>8.1f} {tpv:>8.1f} {ratio:>7.2f}x | {decision:<15}")

print("=" * 100)

# 기업 규모별 통계
print("\n[기업 규모별 통계]")
for firm_size in ['Large', 'Medium', 'Small']:
    firm_projects = df[df['firm_size'] == firm_size]
    firm_results = results_df[results_df['project_id'].isin(firm_projects['project_id'])]

    if len(firm_results) > 0:
        avg_npv = firm_results['npv'].mean()
        avg_rov = firm_results['rov_net'].mean()
        avg_tpv = firm_results['tpv'].mean()
        print(f"  {firm_size:<8}: NPV={avg_npv:>7.1f}  ROV={avg_rov:>7.1f}  TPV={avg_tpv:>7.1f}")

# BIM 경험별 통계
print("\n[BIM 경험별 평균 ROV]")
for bim_range, projects in [
    ('초기(2-3년)', df[df['bim_years'] <= 3]),
    ('중급(4-6년)', df[(df['bim_years'] >= 4) & (df['bim_years'] <= 6)]),
    ('고급(7년+)', df[df['bim_years'] >= 7]),
]:
    if len(projects) > 0:
        pids = projects['project_id'].tolist()
        rov_values = results_df[results_df['project_id'].isin(pids)]['rov_net'].mean()
        print(f"  {bim_range:<15}: ROV={rov_values:>7.1f}")

# 가동률별 통계
print("\n[가동률별 의사결정]")
for util_range, projects in [
    ('낮음(<0.65)', df[df['current_utilization'] < 0.65]),
    ('중간(0.65-0.80)', df[(df['current_utilization'] >= 0.65) & (df['current_utilization'] <= 0.80)]),
    ('높음(>0.80)', df[df['current_utilization'] > 0.80]),
]:
    if len(projects) > 0:
        pids = projects['project_id'].tolist()
        project_results = results_df[results_df['project_id'].isin(pids)]
        participate = len(project_results[project_results['tpv_decision'].isin(['Strong Participate', 'Participate'])])
        total = len(project_results)
        print(f"  {util_range:<20}: 참여 {participate}/{total} ({participate/total*100:.0f}%)")

print("\n" + "=" * 80)
print("테스트 완료!")
print("=" * 80)

# 저장
output_path = 'results_complete_10vars.csv'
results_df.to_csv(output_path, index=False, encoding='utf-8-sig')
print(f"\n결과 저장: {output_path}")
