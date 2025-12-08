#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chapter 4 - Research Visualization Figures (Publication Quality)
논문 4장용 시각화 자료 - 학술 논문 수록 수준
실제 v14 엔진 평가 결과 기반 (R01~R10)

Figure 4-1: NPV vs TPV Comparison (All 10 Projects)
Figure 4-2: ROV Value Decomposition Waterfall (All 10 Projects)
Figure 4-3: Sensitivity Analysis Tornado (All 10 Projects)
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import os

# Font settings (English, Publication quality)
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 11
plt.rcParams['axes.linewidth'] = 1.2
plt.rcParams['xtick.major.width'] = 1.0
plt.rcParams['ytick.major.width'] = 1.0

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# =============================================================================
# Project Data - 실제 v14 엔진 평가 결과 (realistic_projects_10.csv 기반)
# =============================================================================

PROJECTS = {
    'R01': {'name': '세종-대전 고속도로', 'type': 'Road', 'contract': 520, 'phase': 'Preliminary'},
    'R02': {'name': '○○시 우회도로', 'type': 'Road', 'contract': 180, 'phase': 'Detailed'},
    'R03': {'name': '△△IC 연결로', 'type': 'Road', 'contract': 280, 'phase': 'Preliminary'},
    'R04': {'name': '□□대교', 'type': 'Bridge', 'contract': 450, 'phase': 'Preliminary'},
    'R05': {'name': '◇◇교', 'type': 'Bridge', 'contract': 120, 'phase': 'Detailed'},
    'R06': {'name': '▽▽육교 보강', 'type': 'Bridge', 'contract': 95, 'phase': 'Detailed'},
    'R07': {'name': '○○터널', 'type': 'Tunnel', 'contract': 680, 'phase': 'Preliminary'},
    'R08': {'name': '△△지하차도', 'type': 'Tunnel', 'contract': 220, 'phase': 'Detailed'},
    'R09': {'name': '□□해저터널', 'type': 'Tunnel', 'contract': 850, 'phase': 'Preliminary'},
    'R10': {'name': '◎◎산악터널', 'type': 'Tunnel', 'contract': 320, 'phase': 'Detailed'},
}

# 실제 v14 엔진 평가 결과 (5000회 Monte Carlo 시뮬레이션)
VALUATION_RESULTS = {
    'R01': {'npv': 65.09, 'rov_follow': 2.05, 'rov_cap': 11.39, 'rov_res': 5.42,
            'rov_abandon': 34.48, 'rov_contract': 1.27, 'rov_switch': 12.15, 'rov_stage': 42.12,
            'interaction': -22.30, 'risk_prem': -17.58, 'deferral': -47.01, 'tpv': 87.09},

    'R02': {'npv': -4.31, 'rov_follow': 0.00, 'rov_cap': 1.87, 'rov_res': 0.89,
            'rov_abandon': 17.15, 'rov_contract': 2.19, 'rov_switch': 5.10, 'rov_stage': 7.29,
            'interaction': -7.59, 'risk_prem': -4.82, 'deferral': -11.42, 'tpv': 6.36},

    'R03': {'npv': 6.80, 'rov_follow': 0.09, 'rov_cap': 2.91, 'rov_res': 1.39,
            'rov_abandon': 26.75, 'rov_contract': 2.46, 'rov_switch': 7.92, 'rov_stage': 15.12,
            'interaction': -12.46, 'risk_prem': -7.92, 'deferral': -20.62, 'tpv': 22.44},

    'R04': {'npv': 33.46, 'rov_follow': 0.98, 'rov_cap': 14.69, 'rov_res': 7.07,
            'rov_abandon': 40.05, 'rov_contract': 1.72, 'rov_switch': 8.29, 'rov_stage': 30.38,
            'interaction': -22.40, 'risk_prem': -18.29, 'deferral': -37.00, 'tpv': 58.95},

    'R05': {'npv': -7.23, 'rov_follow': 0.00, 'rov_cap': 2.49, 'rov_res': 1.19,
            'rov_abandon': 11.54, 'rov_contract': 1.26, 'rov_switch': 2.80, 'rov_stage': 3.78,
            'interaction': -5.07, 'risk_prem': -3.66, 'deferral': -6.71, 'tpv': 0.39},

    'R06': {'npv': -5.71, 'rov_follow': 0.00, 'rov_cap': 1.96, 'rov_res': 0.95,
            'rov_abandon': 9.06, 'rov_contract': 1.00, 'rov_switch': 2.21, 'rov_stage': 2.14,
            'interaction': -3.81, 'risk_prem': -2.75, 'deferral': -4.51, 'tpv': 0.54},

    'R07': {'npv': 85.21, 'rov_follow': 5.30, 'rov_cap': 22.17, 'rov_res': 10.52,
            'rov_abandon': 45.67, 'rov_contract': 0.70, 'rov_switch': 12.61, 'rov_stage': 81.60,
            'interaction': -36.32, 'risk_prem': -32.23, 'deferral': -65.04, 'tpv': 130.20},

    'R08': {'npv': -5.66, 'rov_follow': 0.00, 'rov_cap': 7.24, 'rov_res': 3.44,
            'rov_abandon': 21.02, 'rov_contract': 1.16, 'rov_switch': 4.07, 'rov_stage': 13.20,
            'interaction': -11.03, 'risk_prem': -8.86, 'deferral': -14.74, 'tpv': 9.85},

    'R09': {'npv': 105.82, 'rov_follow': 6.85, 'rov_cap': 27.60, 'rov_res': 13.34,
            'rov_abandon': 55.83, 'rov_contract': 0.91, 'rov_switch': 15.69, 'rov_stage': 102.00,
            'interaction': -45.08, 'risk_prem': -40.14, 'deferral': -90.39, 'tpv': 152.42},

    'R10': {'npv': 7.76, 'rov_follow': 0.00, 'rov_cap': 9.88, 'rov_res': 4.77,
            'rov_abandon': 30.41, 'rov_contract': 1.21, 'rov_switch': 5.90, 'rov_stage': 24.96,
            'interaction': -16.97, 'risk_prem': -13.63, 'deferral': -24.56, 'tpv': 29.73},
}

# Colors
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
    """
    Figure 4-1: NPV vs TPV Comparison (Publication Quality)
    실제 v14 엔진 결과 기반 (R01~R10)
    폰트 크기: 5.5~7pt 범위
    """
    fig, ax = plt.subplots(figsize=(10, 5.5))

    project_ids = list(VALUATION_RESULTS.keys())
    n = len(project_ids)
    x = np.arange(n)
    width = 0.35

    npv_values = [VALUATION_RESULTS[p]['npv'] for p in project_ids]
    tpv_values = [VALUATION_RESULTS[p]['tpv'] for p in project_ids]

    npv_colors = [COLORS['npv_negative'] if v < 0 else COLORS['npv_positive'] for v in npv_values]

    # Bars
    ax.bar(x - width/2, npv_values, width, color=npv_colors, edgecolor='black', linewidth=0.8)
    ax.bar(x + width/2, tpv_values, width, color=COLORS['tpv'], edgecolor='black', linewidth=0.8)

    # Zero line
    ax.axhline(y=0, color='black', linewidth=1.5)

    # Decision Change 하이라이트 (NPV < 0 & TPV > 0인 프로젝트)
    decision_change_projects = []
    for i, pid in enumerate(project_ids):
        npv = npv_values[i]
        tpv = tpv_values[i]
        if npv < 0 and tpv > 0:
            decision_change_projects.append((i, pid, tpv))
            rect = plt.Rectangle((i - 0.52, npv - 2), 1.04, tpv - npv + 6,
                                  fill=False, edgecolor='#C0392B', linewidth=2.0, linestyle='--')
            ax.add_patch(rect)

    # 첫 번째 Decision Change 프로젝트에 라벨
    if decision_change_projects:
        first_dc = decision_change_projects[0]
        ax.annotate('Decision\nChange', xy=(first_dc[0], first_dc[2] + 8), fontsize=6, ha='center',
                    color='#C0392B', fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='#C0392B', linewidth=1.0))

    # 최대 TPV/NPV 비율 프로젝트 하이라이트
    max_ratio_idx = None
    max_ratio = 0
    for i, (npv, tpv) in enumerate(zip(npv_values, tpv_values)):
        if npv > 0:
            ratio = tpv / npv
            if ratio > max_ratio:
                max_ratio = ratio
                max_ratio_idx = i

    if max_ratio_idx is not None:
        ax.annotate(f'×{max_ratio:.1f}', xy=(max_ratio_idx + width/2 + 0.08, tpv_values[max_ratio_idx]),
                    fontsize=6, ha='left', va='center', color='#8E44AD', fontweight='bold')

    # Data labels - NPV와 TPV 값 (겹침 방지)
    for i, (npv, tpv) in enumerate(zip(npv_values, tpv_values)):
        # NPV 라벨
        if npv < 0:
            y_npv = npv - 6
            va_npv = 'top'
        else:
            y_npv = npv + 4
            va_npv = 'bottom'
        ax.text(i - width/2, y_npv, f'{npv:.1f}', ha='center', va=va_npv,
                fontsize=6, fontweight='bold')

        # TPV 라벨 - NPV와 겹치지 않도록 위치 조정
        tpv_y = tpv + 4
        ax.text(i + width/2, tpv_y, f'{tpv:.1f}', ha='center', va='bottom',
                fontsize=6, fontweight='bold')

    # Axis
    ax.set_xlabel('Project ID', fontsize=7, fontweight='bold')
    ax.set_ylabel('Value (Million KRW)', fontsize=7, fontweight='bold')
    ax.set_title('Figure 4-1. NPV vs TPV Comparison for All Projects', fontsize=7, fontweight='bold', pad=10)
    ax.set_xticks(x)
    ax.set_xticklabels(project_ids, fontsize=6, fontweight='bold')
    ax.set_ylim(-25, 175)
    ax.tick_params(axis='y', labelsize=6)

    # Legend
    legend_elements = [
        mpatches.Patch(facecolor=COLORS['npv_positive'], edgecolor='black', label='NPV (+)'),
        mpatches.Patch(facecolor=COLORS['npv_negative'], edgecolor='black', label='NPV (−)'),
        mpatches.Patch(facecolor=COLORS['tpv'], edgecolor='black', label='TPV'),
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=6, framealpha=0.95)

    ax.yaxis.grid(True, linestyle='--', alpha=0.5)
    ax.set_axisbelow(True)

    # Infrastructure type (x축 아래)
    for i, pid in enumerate(project_ids):
        infra = PROJECTS[pid]['type']
        phase = 'P' if PROJECTS[pid]['phase'] == 'Preliminary' else 'D'
        ax.text(i, -22, f'{infra}({phase})', ha='center', va='top', fontsize=5.5, color='#555555')

    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, 'Figure_4-1_NPV_TPV_Comparison.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  [1/3] Figure 4-1 saved")
    return output_path


def generate_figure_4_2():
    """
    Figure 4-2: ROV Decomposition Waterfall (Publication Quality)
    - 실제 v14 엔진 결과 기반 (R01~R10)
    - 범례 3그룹 분리: Real Options (+) / Adjustments (-) / Common
    - 각 옵션별 구성비중(%) 라벨 추가
    - 범례 크기 통일
    - 폰트 크기: 5.5~7pt 범위
    """
    fig, ax = plt.subplots(figsize=(12, 6.5))

    project_ids = list(VALUATION_RESULTS.keys())
    n = len(project_ids)

    # Option components
    options = [
        ('rov_follow', 'Follow-on', COLORS['rov_follow']),
        ('rov_cap', 'Capability', COLORS['rov_cap']),
        ('rov_res', 'Resource', COLORS['rov_res']),
        ('rov_abandon', 'Abandonment', COLORS['rov_abandon']),
        ('rov_contract', 'Contract', COLORS['rov_contract']),
        ('rov_switch', 'Switch', COLORS['rov_switch']),
        ('rov_stage', 'Staging', COLORS['rov_stage']),
    ]

    # Adjustment components
    adjustments = [
        ('interaction', 'Interaction', COLORS['adj_interaction']),
        ('risk_prem', 'Risk Premium', COLORS['adj_risk']),
        ('deferral', 'Deferral Cost', COLORS['adj_deferral']),
    ]

    # 간격 설정
    option_x = [i * 2.2 for i in range(n)]
    waterfall_x = [i * 2.2 + 0.8 for i in range(n)]
    bar_width = 0.7
    wf_width = 0.5

    # Draw stacked bars for 7 options & store positions for labels
    bottom = np.zeros(n)
    option_positions = []  # [(key, bottom_arr, values_arr), ...]

    for key, label, color in options:
        values = np.array([VALUATION_RESULTS[p][key] for p in project_ids])
        option_positions.append((key, label, bottom.copy(), values))
        ax.bar(option_x, values, bar_width, bottom=bottom,
               color=color, edgecolor='white', linewidth=0.5)
        bottom += values

    # ROV Gross values
    rov_gross = bottom.copy()

    # Draw waterfall for adjustments
    for i, pid in enumerate(project_ids):
        r = VALUATION_RESULTS[pid]
        gross = rov_gross[i]

        # Interaction
        inter_val = abs(r['interaction'])
        ax.bar(waterfall_x[i], -inter_val, wf_width, bottom=gross,
               color=COLORS['adj_interaction'], edgecolor='black', linewidth=0.5)

        # Risk premium
        after_inter = gross - inter_val
        risk_val = abs(r['risk_prem'])
        ax.bar(waterfall_x[i], -risk_val, wf_width, bottom=after_inter,
               color=COLORS['adj_risk'], edgecolor='black', linewidth=0.5)

        # Deferral
        after_risk = after_inter - risk_val
        defer_val = abs(r['deferral'])
        ax.bar(waterfall_x[i], -defer_val, wf_width, bottom=after_risk,
               color=COLORS['adj_deferral'], edgecolor='black', linewidth=0.5)

    # Calculate ROV Net
    rov_net = []
    for pid in project_ids:
        r = VALUATION_RESULTS[pid]
        gross = sum([r['rov_follow'], r['rov_cap'], r['rov_res'], r['rov_abandon'],
                     r['rov_contract'], r['rov_switch'], r['rov_stage']])
        net = gross + r['interaction'] + r['risk_prem'] + r['deferral']
        rov_net.append(net)

    # ROV Net markers
    for i in range(n):
        ax.scatter(waterfall_x[i], rov_net[i], s=120, color='black', marker='D',
                   zorder=5, edgecolors='white', linewidths=1.5)

    # 각 옵션별 구성비중(%) 라벨 - 모든 7개 옵션 막대 내부에 표시
    for i in range(n):
        pid = project_ids[i]
        r = VALUATION_RESULTS[pid]
        gross = rov_gross[i]

        # 각 옵션 막대 내부에 비중(%) 라벨 표시
        for key, label, bottom_arr, values_arr in option_positions:
            val = values_arr[i]
            bot = bottom_arr[i]
            pct = (val / gross) * 100 if gross > 0 else 0

            # 막대 높이가 충분할 때만 라벨 표시 (최소 5% 이상)
            if pct >= 5:
                mid_y = bot + val / 2
                ax.text(option_x[i], mid_y, f'{pct:.0f}%',
                        ha='center', va='center', fontsize=5.5, fontweight='bold', color='white')

        # Gross 라벨 (옵션 막대 상단)
        ax.text(option_x[i], gross + 3, f'{gross:.0f}M',
                ha='center', va='bottom', fontsize=6, fontweight='bold', color='#2C3E50')

        # 조정요소 각각의 비중 라벨 표시
        adj_total = abs(r['interaction']) + abs(r['risk_prem']) + abs(r['deferral'])

        # Interaction 비중
        inter_pct = (abs(r['interaction']) / gross) * 100 if gross > 0 else 0
        risk_pct = (abs(r['risk_prem']) / gross) * 100 if gross > 0 else 0
        defer_pct = (abs(r['deferral']) / gross) * 100 if gross > 0 else 0

        # 워터폴 막대 옆에 각 조정요소 비중 표시
        inter_mid = gross - abs(r['interaction']) / 2
        risk_mid = gross - abs(r['interaction']) - abs(r['risk_prem']) / 2
        defer_mid = gross - abs(r['interaction']) - abs(r['risk_prem']) - abs(r['deferral']) / 2

        if inter_pct >= 5:
            ax.text(waterfall_x[i], inter_mid, f'{inter_pct:.0f}%',
                    ha='center', va='center', fontsize=5.5, fontweight='bold', color='white')
        if risk_pct >= 5:
            ax.text(waterfall_x[i], risk_mid, f'{risk_pct:.0f}%',
                    ha='center', va='center', fontsize=5.5, fontweight='bold', color='white')
        if defer_pct >= 5:
            ax.text(waterfall_x[i], defer_mid, f'{defer_pct:.0f}%',
                    ha='center', va='center', fontsize=5.5, fontweight='bold', color='white')

        # Net 라벨 (다이아몬드 옆)
        ax.text(waterfall_x[i] + 0.35, rov_net[i], f'{rov_net[i]:.1f}M',
                ha='left', va='center', fontsize=6, fontweight='bold', color='black')

    # Connect gross to waterfall
    for i in range(n):
        ax.plot([option_x[i] + bar_width/2, waterfall_x[i] - wf_width/2],
                [rov_gross[i], rov_gross[i]], color='gray', linewidth=0.8, linestyle=':')

    # 최대 ROV 프로젝트 하이라이트 (R09)
    max_rov_idx = np.argmax(rov_gross)
    ax.annotate('Highest ROV\nValue', xy=(option_x[max_rov_idx], rov_gross[max_rov_idx] + 15),
                fontsize=6, ha='center', color='#8E44AD', fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='#8E44AD', alpha=0.9))

    # Axis settings
    ax.set_ylabel('ROV Value (Million KRW)', fontsize=7, fontweight='bold')
    ax.set_title('Figure 4-2. ROV Decomposition: Options (Left) → Adjustments (Right) → ROV Net',
                 fontsize=7, fontweight='bold', pad=10)

    # X-axis labels
    label_x = [(option_x[i] + waterfall_x[i]) / 2 for i in range(n)]
    x_labels = []
    for pid in project_ids:
        infra = PROJECTS[pid]['type']
        phase = 'P' if PROJECTS[pid]['phase'] == 'Preliminary' else 'D'
        x_labels.append(f'{pid}\n{infra}({phase})')

    ax.set_xticks(label_x)
    ax.set_xticklabels(x_labels, fontsize=6, fontweight='bold')
    ax.set_xlabel('Project ID / Infrastructure Type', fontsize=7, fontweight='bold', labelpad=8)

    ax.axhline(y=0, color='black', linewidth=1)
    ax.set_ylim(-5, 250)  # R09 gross≈222 수용
    ax.tick_params(axis='y', labelsize=6)
    ax.tick_params(axis='x', pad=3)

    # ============ 범례 3그룹 분리 (크기 통일) ============
    legend_fontsize = 6
    title_fontsize = 6.5

    # 1. Real Options (+) 범례 - 상단
    legend_options = [mpatches.Patch(facecolor=c, edgecolor='white', label=l)
                      for _, l, c in options]
    legend1 = ax.legend(handles=legend_options, loc='upper right', fontsize=legend_fontsize,
                        ncol=4, framealpha=0.95, edgecolor='#2E86AB', fancybox=True,
                        title='Real Options (+)', title_fontsize=title_fontsize,
                        bbox_to_anchor=(1.0, 1.0), handlelength=1.2, handleheight=0.8)
    legend1.get_title().set_fontweight('bold')
    ax.add_artist(legend1)

    # 2. Adjustments (-) 범례 - 중간
    legend_adj = [mpatches.Patch(facecolor=c, edgecolor='black', label=l)
                  for _, l, c in adjustments]
    legend2 = ax.legend(handles=legend_adj, loc='upper right', fontsize=legend_fontsize,
                        ncol=3, framealpha=0.95, edgecolor='#C0392B', fancybox=True,
                        title='Adjustments (−)', title_fontsize=title_fontsize,
                        bbox_to_anchor=(1.0, 0.93), handlelength=1.2, handleheight=0.8)
    legend2.get_title().set_fontweight('bold')
    ax.add_artist(legend2)

    # 3. Common 범례 - 하단 (ROV Net 마커)
    legend_common = [Line2D([0], [0], marker='D', color='w', markerfacecolor='black',
                            markersize=7, label='ROV Net', markeredgecolor='white', markeredgewidth=1.0)]
    legend3 = ax.legend(handles=legend_common, loc='upper right', fontsize=legend_fontsize,
                        ncol=1, framealpha=0.95, edgecolor='#555555', fancybox=True,
                        title='Common', title_fontsize=title_fontsize,
                        bbox_to_anchor=(1.0, 0.87), handlelength=1.2, handleheight=0.8)
    legend3.get_title().set_fontweight('bold')

    ax.yaxis.grid(True, linestyle='--', alpha=0.5)
    ax.set_axisbelow(True)

    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, 'Figure_4-2_ROV_Decomposition.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  [2/3] Figure 4-2 saved")
    return output_path


def generate_figure_4_3():
    """
    Figure 4-3: Sensitivity Tornado (Publication Quality)
    폰트 크기: 5.5~7pt 범위
    """
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

    # Sort by swing
    sorted_idx = np.argsort(swings)[::-1]
    sorted_params = [sensitivity_params[i] for i in sorted_idx]
    sorted_low = [low_values[i] for i in sorted_idx]
    sorted_high = [high_values[i] for i in sorted_idx]
    sorted_swings = [swings[i] for i in sorted_idx]

    y_pos = np.arange(len(sensitivity_params))

    # Draw bars
    for i in range(len(sorted_params)):
        low, high = sorted_low[i], sorted_high[i]

        low_color = '#27AE60' if low > 0 else '#E74C3C'
        high_color = '#27AE60' if high > 0 else '#E74C3C'

        ax.barh(i, low, height=0.55, color=low_color, edgecolor='black', linewidth=0.8)
        ax.barh(i, high, height=0.55, color=high_color, edgecolor='black', linewidth=0.8)

        # Swing label
        max_ext = max(abs(low), abs(high))
        ax.text(max_ext + 1.5, i, f'{sorted_swings[i]:.1f}M', va='center',
                fontsize=6, fontweight='bold', color='#2C3E50')

        # Direction labels
        if abs(low) > 2:
            ax.text(low/2, i, '-20%', va='center', ha='center', fontsize=5.5,
                    color='white', fontweight='bold')
        if abs(high) > 2:
            ax.text(high/2, i, '+20%', va='center', ha='center', fontsize=5.5,
                    color='white', fontweight='bold')

    # Baseline
    ax.axvline(x=0, color='black', linewidth=2)

    # Highlight top 2
    rect = plt.Rectangle((-14, -0.4), 28, 1.9, fill=False, edgecolor='#C0392B',
                          linewidth=2.0, linestyle='--')
    ax.add_patch(rect)
    ax.annotate('Key Drivers', xy=(15, 0.5), fontsize=6, color='#C0392B',
                fontweight='bold', va='center',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='#C0392B'))

    # Axis
    ax.set_yticks(y_pos)
    ax.set_yticklabels([p[0] for p in sorted_params], fontsize=6, fontweight='bold')
    ax.set_xlabel('TPV Change from Baseline (Million KRW)', fontsize=7, fontweight='bold')
    ax.set_title('Figure 4-3. Sensitivity Analysis: Parameter Impact on TPV (±20% Variation)',
                 fontsize=7, fontweight='bold', pad=10)
    ax.set_xlim(-16, 22)
    ax.tick_params(axis='x', labelsize=6)

    # Legend
    legend_elements = [
        mpatches.Patch(facecolor='#27AE60', edgecolor='black', label='TPV Increase'),
        mpatches.Patch(facecolor='#E74C3C', edgecolor='black', label='TPV Decrease'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=6, framealpha=0.95)

    ax.xaxis.grid(True, linestyle='--', alpha=0.5)
    ax.set_axisbelow(True)

    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, 'Figure_4-3_Sensitivity_Tornado.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  [3/3] Figure 4-3 saved")
    return output_path


def main():
    print("=" * 60)
    print("  Chapter 4 Figures - Publication Quality")
    print("=" * 60)
    print(f"\n  Output: {OUTPUT_DIR}\n")

    generate_figure_4_1()
    generate_figure_4_2()
    generate_figure_4_3()

    print("\n" + "=" * 60)
    print("  All figures generated successfully!")
    print("=" * 60)


if __name__ == '__main__':
    main()
