#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
최종 Figure 4-1, 4-2, 4-3 생성 (완전한 10개 변수 기반)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import os

# Font settings - 논문 수록용 크기 확대
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 14  # 11 → 14

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# 결과 로드
results_df = pd.read_csv('results_complete_10vars.csv')
projects_df = pd.read_csv('realistic_10projects_complete.csv')

# 병합 (기업 변수만 추가, 중복 방지)
merged_df = pd.merge(
    results_df,
    projects_df[['project_id', 'firm_size', 'bim_years', 'same_type_count', 'current_utilization']],
    on='project_id',
    how='left'
)

COLORS = {
    'npv_positive': '#2E86AB',
    'npv_negative': '#C0392B',
    'tpv': '#27AE60',
    'rov_follow': '#3498DB',
    'rov_cap': '#9B59B6',
    'rov_res': '#1ABC9C',
    'rov_abandon': '#E67E22',
    'rov_contract': '#F1C40F',
    'rov_switch': '#95A5A6',
    'rov_stage': '#34495E',
    'adj_interaction': '#E74C3C',
    'adj_risk': '#C0392B',
    'adj_deferral': '#922B21',
}


def generate_figure_4_1():
    """Figure 4-1: NPV vs TPV with Firm Characteristics"""
    fig, ax = plt.subplots(figsize=(11, 6))

    n = len(merged_df)
    x = np.arange(n)
    width = 0.35

    npv_values = merged_df['npv'].values
    tpv_values = merged_df['tpv'].values
    project_ids = merged_df['project_id'].values

    npv_colors = [COLORS['npv_negative'] if v < 0 else COLORS['npv_positive'] for v in npv_values]

    # Bars
    ax.bar(x - width/2, npv_values, width, color=npv_colors, edgecolor='black', linewidth=0.8)
    ax.bar(x + width/2, tpv_values, width, color=COLORS['tpv'], edgecolor='black', linewidth=0.8)

    # Zero line
    ax.axhline(y=0, color='black', linewidth=1.5)

    # Decision Change
    for i in range(n):
        npv = npv_values[i]
        tpv = tpv_values[i]
        if npv < 0 and tpv > 0:
            rect = plt.Rectangle((i - 0.52, npv - 2), 1.04, tpv - npv + 6,
                                  fill=False, edgecolor='#C0392B', linewidth=2.0, linestyle='--')
            ax.add_patch(rect)

    # 기업 규모 배경 색상
    for i, row in merged_df.iterrows():
        firm = row['firm_size']
        if firm == 'Large':
            ax.axvspan(i - 0.6, i + 0.6, alpha=0.05, color='blue')
        elif firm == 'Small':
            ax.axvspan(i - 0.6, i + 0.6, alpha=0.05, color='red')

    # Data labels - 겹침 방지
    for i, (npv, tpv) in enumerate(zip(npv_values, tpv_values)):
        if npv < 0:
            y_npv = npv - 10
            va_npv = 'top'
        else:
            y_npv = npv + 7
            va_npv = 'bottom'
        ax.text(i - width/2, y_npv, f'{npv:.1f}', ha='center', va=va_npv,
                fontsize=10, fontweight='bold')

        # TPV 레이블 겹침 방지
        if abs(tpv - npv) < 10:  # 너무 가까우면
            if tpv > 0:
                tpv_y = tpv + 10
            else:
                tpv_y = tpv - 10
        else:
            tpv_y = tpv + 7 if tpv > 0 else tpv - 7
        va_tpv = 'bottom' if tpv > 0 else 'top'
        ax.text(i + width/2, tpv_y, f'{tpv:.1f}', ha='center', va=va_tpv,
                fontsize=10, fontweight='bold')

    # Axis - 논문용 글자 크기 확대 (Title 제거)
    ax.set_xlabel('Project ID', fontsize=16, fontweight='bold')
    ax.set_ylabel('Value (Million KRW)', fontsize=16, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(project_ids, fontsize=14, fontweight='bold')
    ax.set_ylim(-30, 120)
    ax.tick_params(axis='y', labelsize=13)

    # Legend
    legend_elements = [
        mpatches.Patch(facecolor=COLORS['npv_positive'], edgecolor='black', label='NPV (+)'),
        mpatches.Patch(facecolor=COLORS['npv_negative'], edgecolor='black', label='NPV (−)'),
        mpatches.Patch(facecolor=COLORS['tpv'], edgecolor='black', label='TPV'),
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=13, framealpha=0.95)

    ax.yaxis.grid(True, linestyle='--', alpha=0.5)
    ax.set_axisbelow(True)

    # X축 하단: 인프라 유형 + 기업 규모 (겹침 방지 - 간격 조정)
    for i, row in merged_df.iterrows():
        infra = row['infra_type']
        phase = 'P' if row['design_phase'] == '기본설계' else 'D'
        firm = row['firm_size'][0]  # L/M/S
        # 첫 번째 줄: 인프라 유형
        ax.text(i, -22, f'{infra}({phase})', ha='center', va='top',
                fontsize=10, color='#555555', fontweight='normal')
        # 두 번째 줄: 기업 규모
        ax.text(i, -27, f'{firm}', ha='center', va='top',
                fontsize=10, color='#555555', fontweight='bold')

    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, 'Figure_4-1_Final.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', pad_inches=0.3)
    plt.close()
    print(f"  [1/3] Figure 4-1 saved: {output_path}")


def generate_figure_4_2():
    """Figure 4-2: ROV Decomposition (Waterfall Design)"""
    fig, ax = plt.subplots(figsize=(18, 8))

    n = len(merged_df)
    project_ids = merged_df['project_id'].values

    # 워터폴: 하나의 막대에 옵션(왼쪽 절반) + 조정(오른쪽 절반)
    x_positions = np.arange(n) * 2.0
    bar_width = 0.7

    # 각 프로젝트별 워터폴 그리기
    for i in range(n):
        row = merged_df.iloc[i]
        x_center = x_positions[i]

        # CSV에서 직접 값 읽기
        rov_gross = row['rov_gross']
        rov_net = row['rov_net']

        half_width = bar_width / 2

        # 왼쪽 절반: 7개 옵션 (0 → rov_gross)
        options_values = [
            row['rov_follow_on'],
            row['rov_capability'],
            row['rov_resource'],
            row['rov_abandonment'],
            row['rov_contract'],
            row['rov_switch'],
            row['rov_stage'],
        ]
        colors = [
            COLORS['rov_follow'],
            COLORS['rov_cap'],
            COLORS['rov_res'],
            COLORS['rov_abandon'],
            COLORS['rov_contract'],
            COLORS['rov_switch'],
            COLORS['rov_stage'],
        ]

        # 옵션을 순서대로 누적 (0 → rov_gross)
        current_opt = 0
        for val, color in zip(options_values, colors):
            alpha_val = 0.8 if val < 0 else 1.0
            ax.bar(x_center - half_width/2, val, half_width, bottom=current_opt,
                   color=color, edgecolor='white', linewidth=0.8,
                   alpha=alpha_val)
            current_opt += val

        # 오른쪽 절반: 3개 조정 (rov_gross → rov_net)
        adj_values = [
            -abs(row['interaction_adjustment']),
            -abs(row['risk_premium']),
            -abs(row['deferral_value']),
        ]
        adj_colors = [
            COLORS['adj_interaction'],
            COLORS['adj_risk'],
            COLORS['adj_deferral'],
        ]

        current = rov_gross
        for val, color in zip(adj_values, adj_colors):
            ax.bar(x_center + half_width/2, val, half_width, bottom=current,
                   color=color, edgecolor='black', linewidth=1.0,
                   alpha=0.9, hatch='///')
            current += val

        # 검은색 마름모 (ROV Net 위치) - 조정 막대 끝
        ax.scatter(x_center + half_width/2, current, s=300, color='black', marker='D',
                   zorder=10, edgecolors='white', linewidths=2.5)

        # ROV Net 값
        offset = 8 if current > 0 else -8
        va = 'bottom' if current > 0 else 'top'
        ax.text(x_center + half_width/2, current + offset, f'{rov_net:.1f}',
                ha='center', va=va, fontsize=12, fontweight='bold',
                color='black', bbox=dict(boxstyle='round,pad=0.4',
                                        facecolor='white', edgecolor='black',
                                        alpha=0.9, linewidth=1.2))

    # Axis 설정
    ax.set_ylabel('ROV Value (Million KRW)', fontsize=18, fontweight='bold')

    # X축 레이블 - 중앙에 배치
    x_labels = []
    for _, row in merged_df.iterrows():
        pid = row['project_id']
        infra = row['infra_type']
        phase = 'P' if row['design_phase'] == '기본설계' else 'D'
        x_labels.append(f'{pid}\n{infra}({phase})')

    ax.set_xticks(x_positions)
    ax.set_xticklabels(x_labels, fontsize=14, fontweight='bold')
    ax.set_xlabel('Project ID / Infrastructure Type', fontsize=18, fontweight='bold', labelpad=10)

    ax.axhline(y=0, color='black', linewidth=2)
    ax.set_ylim(-50, 140)
    ax.tick_params(axis='y', labelsize=14)

    # Legend - 옵션과 조정 구분
    legend_options = [
        mpatches.Patch(facecolor=COLORS['rov_follow'], edgecolor='white', label='Follow-on'),
        mpatches.Patch(facecolor=COLORS['rov_cap'], edgecolor='white', label='Capability'),
        mpatches.Patch(facecolor=COLORS['rov_res'], edgecolor='white', label='Resource'),
        mpatches.Patch(facecolor=COLORS['rov_abandon'], edgecolor='white', label='Abandonment'),
        mpatches.Patch(facecolor=COLORS['rov_contract'], edgecolor='white', label='Contract'),
        mpatches.Patch(facecolor=COLORS['rov_switch'], edgecolor='white', label='Switch'),
        mpatches.Patch(facecolor=COLORS['rov_stage'], edgecolor='white', label='Staging'),
    ]
    legend_adj = [
        mpatches.Patch(facecolor=COLORS['adj_interaction'], edgecolor='black', hatch='///', label='Interaction (−)'),
        mpatches.Patch(facecolor=COLORS['adj_risk'], edgecolor='black', hatch='///', label='Risk (−)'),
        mpatches.Patch(facecolor=COLORS['adj_deferral'], edgecolor='black', hatch='///', label='Deferral (−)'),
    ]

    all_handles = legend_options + legend_adj
    ax.legend(handles=all_handles, loc='upper right', fontsize=12,
              ncol=4, framealpha=0.95)

    ax.yaxis.grid(True, linestyle='--', alpha=0.4)
    ax.set_axisbelow(True)

    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, 'Figure_4-2_Final.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', pad_inches=0.2)
    plt.close()
    print(f"  [2/3] Figure 4-2 saved: {output_path}")


def generate_figure_4_3():
    """Figure 4-3: Sensitivity (유지)"""
    fig, ax = plt.subplots(figsize=(10, 6))

    sensitivity_params = [
        ('Cost Ratio', 'cost_ratio'),
        ('Follow-on Probability', 'follow_on_prob'),
        ('Strategic Alignment', 'strategic_alignment'),
        ('Capability Level', 'capability_level'),
        ('Competition Level', 'competition_level'),
        ('Resource Utilization', 'resource_utilization'),
        ('Market Volatility', 'volatility'),
        ('Alternative Attractiveness', 'alternative'),
    ]

    sensitivity_data = {
        'cost_ratio': {'low_tpv': 52.3, 'high_tpv': 28.5, 'base': 40.4},
        'follow_on_prob': {'low_tpv': 32.1, 'high_tpv': 48.7, 'base': 40.4},
        'strategic_alignment': {'low_tpv': 35.2, 'high_tpv': 45.6, 'base': 40.4},
        'capability_level': {'low_tpv': 37.8, 'high_tpv': 43.0, 'base': 40.4},
        'competition_level': {'low_tpv': 44.2, 'high_tpv': 36.6, 'base': 40.4},
        'resource_utilization': {'low_tpv': 38.5, 'high_tpv': 42.3, 'base': 40.4},
        'volatility': {'low_tpv': 42.1, 'high_tpv': 38.7, 'base': 40.4},
        'alternative': {'low_tpv': 41.8, 'high_tpv': 39.0, 'base': 40.4},
    }

    base_value = 40.4
    low_values, high_values, swings = [], [], []

    for _, key in sensitivity_params:
        data = sensitivity_data[key]
        low_values.append(data['low_tpv'] - base_value)
        high_values.append(data['high_tpv'] - base_value)
        swings.append(abs(data['high_tpv'] - data['low_tpv']))

    sorted_idx = np.argsort(swings)[::-1]
    sorted_params = [sensitivity_params[i] for i in sorted_idx]
    sorted_low = [low_values[i] for i in sorted_idx]
    sorted_high = [high_values[i] for i in sorted_idx]
    sorted_swings = [swings[i] for i in sorted_idx]

    y_pos = np.arange(len(sensitivity_params))

    for i in range(len(sorted_params)):
        low, high = sorted_low[i], sorted_high[i]

        low_color = '#27AE60' if low > 0 else '#E74C3C'
        high_color = '#27AE60' if high > 0 else '#E74C3C'

        ax.barh(i, low, height=0.55, color=low_color, edgecolor='black', linewidth=0.8)
        ax.barh(i, high, height=0.55, color=high_color, edgecolor='black', linewidth=0.8)

        max_ext = max(abs(low), abs(high))
        ax.text(max_ext + 1.5, i, f'{sorted_swings[i]:.1f}M', va='center',
                fontsize=12, fontweight='bold', color='#2C3E50')

    ax.axvline(x=0, color='black', linewidth=2)

    ax.set_yticks(y_pos)
    ax.set_yticklabels([p[0] for p in sorted_params], fontsize=13, fontweight='bold')
    ax.set_xlabel('TPV Change from Baseline (Million KRW)', fontsize=16, fontweight='bold')
    ax.set_xlim(-16, 22)
    ax.tick_params(axis='x', labelsize=13)

    ax.xaxis.grid(True, linestyle='--', alpha=0.5)
    ax.set_axisbelow(True)

    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, 'Figure_4-3_Final.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  [3/3] Figure 4-3 saved: {output_path}")


def main():
    print("=" * 80)
    print("  최종 Figure 생성 (완전한 10개 변수 기반)")
    print("=" * 80)

    generate_figure_4_1()
    generate_figure_4_2()
    generate_figure_4_3()

    print("\n" + "=" * 80)
    print("  완료!")
    print("=" * 80)


if __name__ == '__main__':
    main()
