#!/usr/bin/env python3
"""
개선된 ROV 로직 테스트
- 복합옵션 정교화
- ROV 상한 제약
- 음(-)의 ROV 허용
"""

import pandas as pd
from valuation_engine_v14 import ValuationEngine

# 10개 프로젝트 데이터 (실제 사용 데이터)
projects_data = [
    {'project_id': 'R01', 'contract_amount': 520, 'infra_type': 'Road', 'design_phase': '기본설계',
     'contract_duration': 2.5, 'procurement_type': '일반경쟁', 'client_type': '중앙'},

    {'project_id': 'R02', 'contract_amount': 180, 'infra_type': 'Road', 'design_phase': '실시설계',
     'contract_duration': 1.0, 'procurement_type': '제한경쟁', 'client_type': '지방'},

    {'project_id': 'R03', 'contract_amount': 280, 'infra_type': 'Road', 'design_phase': '기본설계',
     'contract_duration': 2.0, 'procurement_type': '제한경쟁', 'client_type': '공기업'},

    {'project_id': 'R04', 'contract_amount': 450, 'infra_type': 'Bridge', 'design_phase': '기본설계',
     'contract_duration': 2.5, 'procurement_type': '일반경쟁', 'client_type': '중앙'},

    {'project_id': 'R05', 'contract_amount': 120, 'infra_type': 'Bridge', 'design_phase': '실시설계',
     'contract_duration': 1.5, 'procurement_type': '지명경쟁', 'client_type': '지방'},

    {'project_id': 'R06', 'contract_amount': 95, 'infra_type': 'Bridge', 'design_phase': '실시설계',
     'contract_duration': 1.0, 'procurement_type': '지명경쟁', 'client_type': '지방'},

    {'project_id': 'R07', 'contract_amount': 680, 'infra_type': 'Tunnel', 'design_phase': '기본설계',
     'contract_duration': 3.0, 'procurement_type': '일반경쟁', 'client_type': '중앙'},

    {'project_id': 'R08', 'contract_amount': 220, 'infra_type': 'Tunnel', 'design_phase': '실시설계',
     'contract_duration': 2.0, 'procurement_type': '제한경쟁', 'client_type': '공기업'},

    {'project_id': 'R09', 'contract_amount': 850, 'infra_type': 'Tunnel', 'design_phase': '기본설계',
     'contract_duration': 3.5, 'procurement_type': '일반경쟁', 'client_type': '중앙'},

    {'project_id': 'R10', 'contract_amount': 320, 'infra_type': 'Tunnel', 'design_phase': '실시설계',
     'contract_duration': 2.5, 'procurement_type': '제한경쟁', 'client_type': '공기업'},
]

df = pd.DataFrame(projects_data)

# 엔진 실행 (5000회 시뮬레이션)
print("=" * 80)
print("개선된 ROV 로직 테스트 (복합옵션 + 상한 제약 + 음의 ROV 허용)")
print("=" * 80)

engine = ValuationEngine(n_simulations=5000)
results_df, sensitivity = engine.run_valuation(df)

print("\n[개선 후 결과 요약]")
print("=" * 80)
print(f"{'PID':<8} {'NPV':>10} {'ROV_Net':>10} {'TPV':>10} {'TPV/NPV':>10} {'Decision':<20}")
print("-" * 80)

for _, row in results_df.iterrows():
    pid = row['project_id']
    npv = row['npv']
    rov_net = row['rov_net']
    tpv = row['tpv']

    if npv != 0:
        ratio = tpv / npv
    else:
        ratio = 0

    decision = row['tpv_decision']

    print(f"{pid:<8} {npv:>10.1f} {rov_net:>10.1f} {tpv:>10.1f} {ratio:>10.2f}x {decision:<20}")

print("=" * 80)

# 음(-)의 ROV 케이스 확인
negative_rov = results_df[results_df['rov_net'] < 0]
if len(negative_rov) > 0:
    print(f"\n[음(-)의 ROV 발생: {len(negative_rov)}건]")
    for _, row in negative_rov.iterrows():
        print(f"  - {row['project_id']}: ROV_Net = {row['rov_net']:.2f}")
else:
    print("\n[음(-)의 ROV 발생: 0건]")

# TPV/NPV 비율 통계
positive_npv = results_df[results_df['npv'] > 0]
if len(positive_npv) > 0:
    ratios = (positive_npv['tpv'] / positive_npv['npv']).tolist()
    print(f"\n[TPV/NPV 비율 통계 (NPV > 0인 케이스)]")
    print(f"  - 평균: {sum(ratios) / len(ratios):.2f}x")
    print(f"  - 최소: {min(ratios):.2f}x")
    print(f"  - 최대: {max(ratios):.2f}x")

print("\n" + "=" * 80)
print("테스트 완료!")
print("=" * 80)

# CSV 저장
output_path = 'results_improved_rov.csv'
results_df.to_csv(output_path, index=False, encoding='utf-8-sig')
print(f"\n결과 저장: {output_path}")
