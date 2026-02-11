#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
개선된 Figure 4-1, 4-2, 4-3 생성
복합옵션 + ROV 상한 제약 반영
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import os

# Font settings
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 11
plt.rcParams['axes.linewidth'] = 1.2

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# Project Data
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

# 개선된 평가 결과 (개선 후 실제 결과 반영)
VALUATION_RESULTS = {
    'R01': {'npv': 65.6, 'rov_follow': 1.39, 'rov_cap': 10.87, 'rov_res': 5.17,
            'rov_abandon': 33.76, 'rov_contract': 1.24, 'rov_switch': 12.13, 'rov_stage': 46.80,
            'interaction': -22.75, 'risk_prem': -18.01, 'deferral': -55.02, 'tpv': 76.9},

    'R02': {'npv': -4.5, 'rov_follow': 0.00, 'rov_cap': 1.98, 'rov_res': 0.95,
            'rov_abandon': 17.20, 'rov_contract': 2.21, 'rov_switch': 5.08, 'rov_stage': 8.10,
            'interaction': -7.81, 'risk_prem': -4.96, 'deferral': -11.93, 'tpv': 0.3},

    'R03': {'npv': 7.3, 'rov_follow': 0.06, 'rov_cap': 3.11, 'rov_res': 1.49,
            'rov_abandon': 26.73, 'rov_contract': 2.43, 'rov_switch': 7.91, 'rov_stage': 25.20,
            'interaction': -14.72, 'risk_prem': -9.36, 'deferral': -26.41, 'tpv': 13.5},

    'R04': {'npv': 34.1, 'rov_follow': 0.72, 'rov_cap': 13.94, 'rov_res': 6.61,
            'rov_abandon': 40.10, 'rov_contract': 1.70, 'rov_switch': 8.35, 'rov_stage': 40.50,
            'interaction': -24.26, 'risk_prem': -19.84, 'deferral': -47.70, 'tpv': 45.1},

    'R05': {'npv': -7.2, 'rov_follow': 0.00, 'rov_cap': 2.81, 'rov_res': 1.34,
            'rov_abandon': 11.44, 'rov_contract': 1.26, 'rov_switch': 2.81, 'rov_stage': 8.10,
            'interaction': -6.11, 'risk_prem': -4.40, 'deferral': -9.90, 'tpv': -3.1},

    'R06': {'npv': -5.7, 'rov_follow': 0.00, 'rov_cap': 2.21, 'rov_res': 1.05,
            'rov_abandon': 9.08, 'rov_contract': 1.00, 'rov_switch': 2.22, 'rov_stage': 4.27,
            'interaction': -4.36, 'risk_prem': -3.14, 'deferral': -6.37, 'tpv': -2.2},

    'R07': {'npv': 85.5, 'rov_follow': 3.26, 'rov_cap': 21.10, 'rov_res': 10.15,
            'rov_abandon': 43.55, 'rov_contract': 0.71, 'rov_switch': 12.52, 'rov_stage': 81.60,
            'interaction': -35.03, 'risk_prem': -31.23, 'deferral': -78.24, 'tpv': 106.5},

    'R08': {'npv': -5.6, 'rov_follow': 0.00, 'rov_cap': 7.22, 'rov_res': 3.46,
            'rov_abandon': 21.00, 'rov_contract': 1.16, 'rov_switch': 4.06, 'rov_stage': 26.40,
            'interaction': -13.92, 'risk_prem': -11.19, 'deferral': -20.60, 'tpv': 0.7},

    'R09': {'npv': 106.8, 'rov_follow': 4.51, 'rov_cap': 26.14, 'rov_res': 12.53,
            'rov_abandon': 54.83, 'rov_contract': 0.89, 'rov_switch': 15.73, 'rov_stage': 102.00,
            'interaction': -43.86, 'risk_prem': -39.11, 'deferral': -106.97, 'tpv': 125.0},

    'R10': {'npv': 7.8, 'rov_follow': 0.00, 'rov_cap': 10.46, 'rov_res': 5.01,
            'rov_abandon': 30.63, 'rov_contract': 1.21, 'rov_switch': 5.89, 'rov_stage': 38.40,
            'interaction': -20.15, 'risk_prem': -16.19, 'deferral': -33.82, 'tpv': 15.3},
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
    """Figure 4-1: NPV vs TPV Comparison"""
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

    # Decision Change 하이라이트 (NPV < 0 & TPV > 0)
    decision_change_projects = []
    for i, pid in enumerate(project_ids):
        npv = npv_values[i]
        tpv = tpv_values[i]
        if npv < 0 and tpv > 0:
            decision_change_projects.append((i, pid, tpv))
            rect = plt.Rectangle((i - 0.52, npv - 2), 1.04, tpv - npv + 6,
                                  fill=False, edgecolor='#C0392B', linewidth=2.0, linestyle='--')
            ax.add_patch(rect)

    # Decision Change 라벨
    if decision_change_projects:
        first_dc = decision_change_projects[0]
        ax.annotate('Decision\nChange', xy=(first_dc[0], first_dc[2] + 4), fontsize=6, ha='center',
                    color='#C0392B', fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='#C0392B', linewidth=1.0))

    # 최대 TPV/NPV 비율 프로젝트
    max_ratio_idx = None
    max_ratio = 0
    for i, (npv, tpv) in enumerate(zip(npv_values, tpv_values)):
        if npv > 0:
            ratio = tpv / npv
            if ratio > max_ratio:
                max_ratio = ratio
                max_ratio_idx = i

    if max_ratio_idx is not None:
        ax.annotate(f'×{max_ratio:.2f}', xy=(max_ratio_idx + width/2 + 0.08, tpv_values[max_ratio_idx]),
                    fontsize=6, ha='left', va='center', color='#8E44AD', fontweight='bold')

    # Data labels
    for i, (npv, tpv) in enumerate(zip(npv_values, tpv_values)):
        if npv < 0:
            y_npv = npv - 6
            va_npv = 'top'
        else:
            y_npv = npv + 4
            va_npv = 'bottom'
        ax.text(i - width/2, y_npv, f'{npv:.1f}', ha='center', va=va_npv,
                fontsize=6, fontweight='bold')

        tpv_y = tpv + 4 if tpv > 0 else tpv - 4
        va_tpv = 'bottom' if tpv > 0 else 'top'
        ax.text(i + width/2, tpv_y, f'{tpv:.1f}', ha='center', va=va_tpv,
                fontsize=6, fontweight='bold')

    # Axis
    ax.set_xlabel('Project ID', fontsize=7, fontweight='bold')
    ax.set_ylabel('Value (Million KRW)', fontsize=7, fontweight='bold')
    ax.set_title('Figure 4-1. NPV vs TPV Comparison (Improved Model with ROV Cap)', fontsize=7, fontweight='bold', pad=10)
    ax.set_xticks(x)
    ax.set_xticklabels(project_ids, fontsize=6, fontweight='bold')
    ax.set_ylim(-25, 150)
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

    # Infrastructure type
    for i, pid in enumerate(project_ids):
        infra = PROJECTS[pid]['type']
        phase = 'P' if PROJECTS[pid]['phase'] == 'Preliminary' else 'D'
        ax.text(i, -22, f'{infra}({phase})', ha='center', va='top', fontsize=5.5, color='#555555')

    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, 'Figure_4-1_Improved.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  [1/3] Figure 4-1 saved: {output_path}")
    return output_path


def generate_figure_4_2():
    """Figure 4-2: ROV Decomposition Waterfall (Improved)"""
    fig, ax = plt.subplots(figsize=(12, 6.5))

    project_ids = list(VALUATION_RESULTS.keys())
    n = len(project_ids)

    options = [
        ('rov_follow', 'Follow-on', COLORS['rov_follow']),
        ('rov_cap', 'Capability', COLORS['rov_cap']),
        ('rov_res', 'Resource', COLORS['rov_res']),
        ('rov_abandon', 'Abandonment', COLORS['rov_abandon']),
        ('rov_contract', 'Contract', COLORS['rov_contract']),
        ('rov_switch', 'Switch', COLORS['rov_switch']),
        ('rov_stage', 'Staging', COLORS['rov_stage']),
    ]

    adjustments = [
        ('interaction', 'Interaction', COLORS['adj_interaction']),
        ('risk_prem', 'Risk Premium', COLORS['adj_risk']),
        ('deferral', 'Deferral Cost', COLORS['adj_deferral']),
    ]

    option_x = [i * 2.2 for i in range(n)]
    waterfall_x = [i * 2.2 + 0.8 for i in range(n)]
    bar_width = 0.7
    wf_width = 0.5

    # Option bars
    bottom = np.zeros(n)
    option_positions = []

    for key, label, color in options:
        values = np.array([VALUATION_RESULTS[p][key] for p in project_ids])
        option_positions.append((key, label, bottom.copy(), values))
        ax.bar(option_x, values, bar_width, bottom=bottom,
               color=color, edgecolor='white', linewidth=0.5)
        bottom += values

    rov_gross = bottom.copy()

    # Waterfall
    for i, pid in enumerate(project_ids):
        r = VALUATION_RESULTS[pid]
        gross = rov_gross[i]

        inter_val = abs(r['interaction'])
        ax.bar(waterfall_x[i], -inter_val, wf_width, bottom=gross,
               color=COLORS['adj_interaction'], edgecolor='black', linewidth=0.5)

        after_inter = gross - inter_val
        risk_val = abs(r['risk_prem'])
        ax.bar(waterfall_x[i], -risk_val, wf_width, bottom=after_inter,
               color=COLORS['adj_risk'], edgecolor='black', linewidth=0.5)

        after_risk = after_inter - risk_val
        defer_val = abs(r['deferral'])
        ax.bar(waterfall_x[i], -defer_val, wf_width, bottom=after_risk,
               color=COLORS['adj_deferral'], edgecolor='black', linewidth=0.5)

    # ROV Net
    rov_net = []
    for pid in project_ids:
        r = VALUATION_RESULTS[pid]
        gross = sum([r['rov_follow'], r['rov_cap'], r['rov_res'], r['rov_abandon'],
                     r['rov_contract'], r['rov_switch'], r['rov_stage']])
        net = gross + r['interaction'] + r['risk_prem'] + r['deferral']
        rov_net.append(net)

    for i in range(n):
        ax.scatter(waterfall_x[i], rov_net[i], s=120, color='black', marker='D',
                   zorder=5, edgecolors='white', linewidths=1.5)

    # 구성비중 라벨
    for i in range(n):
        pid = project_ids[i]
        r = VALUATION_RESULTS[pid]
        gross = rov_gross[i]

        for key, label, bottom_arr, values_arr in option_positions:
            val = values_arr[i]
            bot = bottom_arr[i]
            pct = (val / gross) * 100 if gross > 0 else 0

            if pct >= 5:
                mid_y = bot + val / 2
                ax.text(option_x[i], mid_y, f'{pct:.0f}%',
                        ha='center', va='center', fontsize=5.5, fontweight='bold', color='white')

        ax.text(option_x[i], gross + 3, f'{gross:.0f}M',
                ha='center', va='bottom', fontsize=6, fontweight='bold', color='#2C3E50')

        inter_pct = (abs(r['interaction']) / gross) * 100 if gross > 0 else 0
        risk_pct = (abs(r['risk_prem']) / gross) * 100 if gross > 0 else 0
        defer_pct = (abs(r['deferral']) / gross) * 100 if gross > 0 else 0

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

        ax.text(waterfall_x[i] + 0.35, rov_net[i], f'{rov_net[i]:.1f}M',
                ha='left', va='center', fontsize=6, fontweight='bold', color='black')

    # Connect lines
    for i in range(n):
        ax.plot([option_x[i] + bar_width/2, waterfall_x[i] - wf_width/2],
                [rov_gross[i], rov_gross[i]], color='gray', linewidth=0.8, linestyle=':')

    # Axis
    ax.set_ylabel('ROV Value (Million KRW)', fontsize=7, fontweight='bold')
    ax.set_title('Figure 4-2. ROV Decomposition with Cap Constraint (Trigeorgis 1996)',
                 fontsize=7, fontweight='bold', pad=10)

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
    ax.set_ylim(-5, 230)
    ax.tick_params(axis='y', labelsize=6)
    ax.tick_params(axis='x', pad=3)

    # Legend
    legend_fontsize = 6
    title_fontsize = 6.5

    legend_options = [mpatches.Patch(facecolor=c, edgecolor='white', label=l)
                      for _, l, c in options]
    legend1 = ax.legend(handles=legend_options, loc='upper right', fontsize=legend_fontsize,
                        ncol=4, framealpha=0.95, edgecolor='#2E86AB', fancybox=True,
                        title='Real Options (+)', title_fontsize=title_fontsize,
                        bbox_to_anchor=(1.0, 1.0), handlelength=1.2, handleheight=0.8)
    legend1.get_title().set_fontweight('bold')
    ax.add_artist(legend1)

    legend_adj = [mpatches.Patch(facecolor=c, edgecolor='black', label=l)
                  for _, l, c in adjustments]
    legend2 = ax.legend(handles=legend_adj, loc='upper right', fontsize=legend_fontsize,
                        ncol=3, framealpha=0.95, edgecolor='#C0392B', fancybox=True,
                        title='Adjustments (−)', title_fontsize=title_fontsize,
                        bbox_to_anchor=(1.0, 0.93), handlelength=1.2, handleheight=0.8)
    legend2.get_title().set_fontweight('bold')
    ax.add_artist(legend2)

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
    output_path = os.path.join(OUTPUT_DIR, 'Figure_4-2_Improved.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  [2/3] Figure 4-2 saved: {output_path}")
    return output_path


def generate_figure_4_3():
    """Figure 4-3: Sensitivity Tornado"""
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
                fontsize=6, fontweight='bold', color='#2C3E50')

        if abs(low) > 2:
            ax.text(low/2, i, '-20%', va='center', ha='center', fontsize=5.5,
                    color='white', fontweight='bold')
        if abs(high) > 2:
            ax.text(high/2, i, '+20%', va='center', ha='center', fontsize=5.5,
                    color='white', fontweight='bold')

    ax.axvline(x=0, color='black', linewidth=2)

    rect = plt.Rectangle((-14, -0.4), 28, 1.9, fill=False, edgecolor='#C0392B',
                          linewidth=2.0, linestyle='--')
    ax.add_patch(rect)
    ax.annotate('Key Drivers', xy=(15, 0.5), fontsize=6, color='#C0392B',
                fontweight='bold', va='center',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='#C0392B'))

    ax.set_yticks(y_pos)
    ax.set_yticklabels([p[0] for p in sorted_params], fontsize=6, fontweight='bold')
    ax.set_xlabel('TPV Change from Baseline (Million KRW)', fontsize=7, fontweight='bold')
    ax.set_title('Figure 4-3. Sensitivity Analysis: Parameter Impact on TPV (±20% Variation)',
                 fontsize=7, fontweight='bold', pad=10)
    ax.set_xlim(-16, 22)
    ax.tick_params(axis='x', labelsize=6)

    legend_elements = [
        mpatches.Patch(facecolor='#27AE60', edgecolor='black', label='TPV Increase'),
        mpatches.Patch(facecolor='#E74C3C', edgecolor='black', label='TPV Decrease'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=6, framealpha=0.95)

    ax.xaxis.grid(True, linestyle='--', alpha=0.5)
    ax.set_axisbelow(True)

    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, 'Figure_4-3_Improved.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  [3/3] Figure 4-3 saved: {output_path}")
    return output_path


def main():
    print("=" * 80)
    print("  개선된 Figure 4-1, 4-2, 4-3 생성 (복합옵션 + ROV Cap)")
    print("=" * 80)
    print(f"\n  Output: {OUTPUT_DIR}\n")

    generate_figure_4_1()
    generate_figure_4_2()
    generate_figure_4_3()

    print("\n" + "=" * 80)
    print("  모든 Figure 생성 완료!")
    print("=" * 80)


if __name__ == '__main__':
    main()
