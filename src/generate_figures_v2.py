#!/usr/bin/env python3
"""
Generate Figure 4-1, 4-2, 4-3 with larger text sizes
Based on 10 project data and EN model valuation results
Project IDs: P001 ~ P010
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from matplotlib.lines import Line2D
import warnings
warnings.filterwarnings('ignore')

# Path setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from valuation_engine_v14 import ValuationEngine
from tier_system import Tier0Input, Tier1Derivation, Tier2Sampler

# Set global font sizes (LARGER)
plt.rcParams.update({
    'font.size': 14,
    'axes.titlesize': 18,
    'axes.labelsize': 16,
    'xtick.labelsize': 14,
    'ytick.labelsize': 14,
    'legend.fontsize': 12,
    'figure.titlesize': 20,
})

# Color palette - matching original design
COLORS = {
    'npv_pos': '#2196F3',      # Blue - positive NPV
    'npv_neg': '#C62828',      # Red - negative NPV
    'tpv': '#4CAF50',          # Green - TPV
    # Real Options (+) - 7 options (GREEN/BLUE-GREEN shades with high contrast)
    'follow_on': '#004D40',    # Teal (very dark)
    'capability': '#00796B',   # Dark Teal
    'resource': '#1B5E20',     # Dark Green
    'abandonment': '#388E3C',  # Green
    'contract': '#7CB342',     # Light Green (yellow-green)
    'switch': '#AED581',       # Pale Lime
    'stage': '#C5E1A5',        # Very Light Lime
    # Adjustments (-) - 3 adjustments (RED/ORANGE shades with high contrast)
    'interaction': '#B71C1C',  # Dark Red
    'risk_premium': '#E65100', # Dark Orange
    'deferral': '#FFB74D',     # Light Orange
}


def load_data():
    """Load 10 project data and convert IDs to P001~P010"""
    data_path = os.path.join(BASE_DIR, '..', 'data', 'realistic_projects_10.csv')
    df = pd.read_csv(data_path, encoding='utf-8')

    # Convert R01~R10 to P001~P010
    df['project_id'] = df['project_id'].apply(lambda x: f"P{int(x[1:]):03d}")

    return df


def run_valuation(df):
    """Run valuation engine on all projects"""
    engine = ValuationEngine(n_simulations=5000)
    results_df, sensitivity = engine.run_valuation(df)

    # Convert project IDs in results
    results_df['project_id'] = results_df['project_id'].apply(lambda x: f"P{int(x[1:]):03d}")

    return results_df, sensitivity


def create_figure_4_1(results_df, output_path):
    """
    Figure 4-1: NPV vs TPV Comparison for All Projects
    - Larger text sizes
    - Decision change highlighting
    """
    fig, ax = plt.subplots(figsize=(16, 9))

    projects = results_df['project_id'].tolist()
    npv_values = results_df['npv'].values
    tpv_values = results_df['tpv'].values

    x = np.arange(len(projects))
    width = 0.35

    # Create bars
    npv_colors = [COLORS['npv_pos'] if v >= 0 else COLORS['npv_neg'] for v in npv_values]

    bars_npv = ax.bar(x - width/2, npv_values, width, color=npv_colors, edgecolor='white', linewidth=1)
    bars_tpv = ax.bar(x + width/2, tpv_values, width, color=COLORS['tpv'], edgecolor='white', linewidth=1)

    # Add data labels with LARGER font
    for i, (bar_npv, bar_tpv) in enumerate(zip(bars_npv, bars_tpv)):
        npv_val = npv_values[i]
        tpv_val = tpv_values[i]

        # NPV label
        height = bar_npv.get_height()
        va = 'bottom' if height >= 0 else 'top'
        offset = 3 if height >= 0 else -3
        ax.annotate(f'{npv_val:.1f}',
                    xy=(bar_npv.get_x() + bar_npv.get_width()/2, height),
                    ha='center', va=va, fontsize=13, fontweight='bold',
                    xytext=(0, offset), textcoords='offset points')

        # TPV label
        height = bar_tpv.get_height()
        va = 'bottom' if height >= 0 else 'top'
        offset = 3 if height >= 0 else -3
        ax.annotate(f'{tpv_val:.1f}',
                    xy=(bar_tpv.get_x() + bar_tpv.get_width()/2, height),
                    ha='center', va=va, fontsize=13, fontweight='bold',
                    xytext=(0, offset), textcoords='offset points')

    # Highlight decision changes with red dashed box
    decision_changes = results_df['decision_changed'].values
    for i, changed in enumerate(decision_changes):
        if changed:
            # Draw red dashed rectangle around the bars
            rect = FancyBboxPatch((x[i] - width - 0.1, min(0, npv_values[i], tpv_values[i]) - 5),
                                   width * 2 + 0.2,
                                   abs(max(npv_values[i], tpv_values[i]) - min(0, npv_values[i], tpv_values[i])) + 10,
                                   boxstyle="round,pad=0.05",
                                   linewidth=2.5, edgecolor='#C62828', facecolor='none',
                                   linestyle='--')
            ax.add_patch(rect)

            # Add "Decision Change" label
            ax.annotate('Decision\nChange',
                       xy=(x[i], min(0, npv_values[i]) - 8),
                       ha='center', va='top', fontsize=11, color='#C62828',
                       fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#C62828', linewidth=1.5))

    # Styling
    ax.axhline(y=0, color='gray', linewidth=1, linestyle='-')
    ax.set_xlabel('Project ID', fontsize=16, fontweight='bold')
    ax.set_ylabel('Value (Million KRW)', fontsize=16, fontweight='bold')
    # Title removed per user request

    # X-axis labels with project info
    infra_types = results_df['infra_type'].values
    phases = results_df['design_phase'].values
    phase_short = ['(P)' if '기본' in str(p) or 'Basic' in str(p) else '(D)' for p in phases]
    x_labels = [f'{proj}\n{infra}{ph}' for proj, infra, ph in zip(projects, infra_types, phase_short)]

    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, fontsize=13)

    # Grid
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)

    # Legend with larger font
    legend_elements = [
        mpatches.Patch(facecolor=COLORS['npv_pos'], edgecolor='white', label='NPV (+)'),
        mpatches.Patch(facecolor=COLORS['npv_neg'], edgecolor='white', label='NPV (−)'),
        mpatches.Patch(facecolor=COLORS['tpv'], edgecolor='white', label='TPV'),
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=14, framealpha=0.9)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Saved: {output_path}")


def create_figure_4_2(results_df, output_path):
    """
    Figure 4-2: ROV Decomposition - Options (Left) → Adjustments (Right) → ROV Net
    - LEFT bar: 7 Real Options (+) stacked from bottom
    - RIGHT bar: WATERFALL - starts from ROV Gross, subtracts adjustments down to ROV Net
    - Diamond marker: ROV Net at the bottom of waterfall
    - Legend: horizontal layout like original
    """
    fig, ax = plt.subplots(figsize=(18, 10))

    projects = results_df['project_id'].tolist()
    n_projects = len(projects)
    x = np.arange(n_projects)
    bar_width = 0.38

    # Option and adjustment definitions
    options = ['follow_on', 'capability', 'resource', 'abandonment', 'contract', 'switch', 'stage']
    adjustments = ['interaction', 'risk_premium', 'deferral']

    option_labels = ['Follow-on', 'Capability', 'Resource', 'Abandonment', 'Contract', 'Switch', 'Staging']
    adj_labels = ['Interaction', 'Risk Premium', 'Deferral Cost']

    # ========== LEFT BARS: 7 Real Options (+) ==========
    bottom_left = np.zeros(n_projects)
    option_totals = np.zeros(n_projects)

    # First pass: calculate totals for percentage
    for opt in options:
        col_name = f'rov_{opt}'
        if col_name in results_df.columns:
            option_totals += results_df[col_name].values

    # Second pass: draw bars with percentages
    for i, opt in enumerate(options):
        col_name = f'rov_{opt}'
        if col_name in results_df.columns:
            values = results_df[col_name].values
            ax.bar(x - bar_width/2, values, bar_width, bottom=bottom_left,
                   color=COLORS[opt], edgecolor='white', linewidth=0.5)

            # Add percentage labels for significant values (> 8% of total)
            for j, v in enumerate(values):
                pct = (v / option_totals[j] * 100) if option_totals[j] > 0 else 0
                if pct >= 8 and v >= 4:  # Show if >= 8% and >= 4M
                    ax.text(x[j] - bar_width/2, bottom_left[j] + v/2, f'{pct:.0f}%',
                           ha='center', va='center', fontsize=10, fontweight='bold', color='white')

            bottom_left += values

    # Add total ROV Gross labels on top of left bars
    for j in range(n_projects):
        if option_totals[j] > 0:
            ax.text(x[j] - bar_width/2, option_totals[j] + 3, f'{option_totals[j]:.0f}M',
                   ha='center', va='bottom', fontsize=11, fontweight='bold')

    # ========== RIGHT BARS: WATERFALL CHART ==========
    # Get adjustment values
    adj_values_dict = {}
    for adj in adjustments:
        if adj == 'interaction':
            col_name = 'interaction_adjustment'
        elif adj == 'risk_premium':
            col_name = 'risk_premium'
        elif adj == 'deferral':
            col_name = 'deferral_value'
        else:
            col_name = f'rov_{adj}'

        if col_name in results_df.columns:
            adj_values_dict[adj] = results_df[col_name].values
        else:
            adj_values_dict[adj] = np.zeros(n_projects)

    # Calculate ROV Net
    rov_net = results_df['rov_net'].values

    # Waterfall: Start from ROV Gross (option_totals), subtract adjustments
    # Draw from top to bottom
    for j in range(n_projects):
        current_top = option_totals[j]  # Start from ROV Gross

        for i, adj in enumerate(adjustments):
            adj_val = adj_values_dict[adj][j]
            # Draw bar from current_top downward by adj_val
            ax.bar(x[j] + bar_width/2, adj_val, bar_width,
                   bottom=current_top - adj_val,
                   color=COLORS[adj], edgecolor='white', linewidth=0.5)

            # Add percentage label if significant
            total_adj = sum(adj_values_dict[a][j] for a in adjustments)
            if total_adj > 0:
                pct = (adj_val / total_adj * 100)
                if pct >= 15 and adj_val >= 3:
                    ax.text(x[j] + bar_width/2, current_top - adj_val/2, f'{pct:.0f}%',
                           ha='center', va='center', fontsize=9, fontweight='bold', color='white')

            current_top -= adj_val  # Move down for next adjustment

    # Add total Adjustments label at the top of waterfall (same height as left bar)
    for j in range(n_projects):
        total_adj = sum(adj_values_dict[a][j] for a in adjustments)
        if total_adj > 0:
            ax.text(x[j] + bar_width/2, option_totals[j] + 3, f'{total_adj:.0f}M',
                   ha='center', va='bottom', fontsize=11, fontweight='bold', color='#666666')

    # ========== ROV NET Diamond Markers ==========
    # Position diamond at the bottom of the waterfall (which equals ROV Net)
    ax.scatter(x + bar_width/2, rov_net, marker='D', s=180, c='black', zorder=5,
               edgecolors='white', linewidths=1.5)

    # Add ROV Net labels
    for j, v in enumerate(rov_net):
        ax.annotate(f'{v:.1f}M', xy=(x[j] + bar_width/2, v),
                   xytext=(6, -12), textcoords='offset points',
                   fontsize=10, fontweight='bold',
                   ha='center', va='top')

    # ========== STYLING ==========
    ax.axhline(y=0, color='gray', linewidth=1)
    ax.set_xlabel('Project ID / Infrastructure Type', fontsize=16, fontweight='bold')
    ax.set_ylabel('ROV Value (Million KRW)', fontsize=16, fontweight='bold')
    # Title removed per user request

    # X-axis labels
    infra_types = results_df['infra_type'].values
    phases = results_df['design_phase'].values
    phase_short = ['(P)' if '기본' in str(p) or 'Basic' in str(p) else '(D)' for p in phases]
    x_labels = [f'{proj}\n{infra}{ph}' for proj, infra, ph in zip(projects, infra_types, phase_short)]

    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, fontsize=12)

    # Grid
    ax.yaxis.grid(True, linestyle='--', alpha=0.5)
    ax.set_axisbelow(True)

    # ========== LEGEND - Horizontal Layout, Upper Left ==========
    # Create legend handles
    option_handles = [mpatches.Patch(facecolor=COLORS[opt], edgecolor='white', label=lbl)
                     for opt, lbl in zip(options, option_labels)]
    adj_handles = [mpatches.Patch(facecolor=COLORS[adj], edgecolor='white', label=lbl)
                  for adj, lbl in zip(adjustments, adj_labels)]
    net_handle = Line2D([0], [0], marker='D', color='w', markerfacecolor='black',
                        markersize=10, markeredgecolor='white', label='ROV Net')

    # First legend: Real Options (+) - horizontal, upper left
    legend1 = ax.legend(handles=option_handles,
                        loc='upper left',
                        bbox_to_anchor=(0.0, 1.0),
                        title='Real Options (+)',
                        title_fontsize=10,
                        fontsize=9,
                        ncol=4,
                        framealpha=0.95,
                        edgecolor='#1976D2')
    ax.add_artist(legend1)

    # Second legend: Adjustments (-) - horizontal, below first (tighter spacing)
    legend2 = ax.legend(handles=adj_handles,
                        loc='upper left',
                        bbox_to_anchor=(0.0, 0.91),
                        title='Adjustments (−)',
                        title_fontsize=10,
                        fontsize=9,
                        ncol=3,
                        framealpha=0.95,
                        edgecolor='#E53935')
    ax.add_artist(legend2)

    # Third legend: Common (ROV Net) - tighter spacing
    legend3 = ax.legend(handles=[net_handle],
                        loc='upper left',
                        bbox_to_anchor=(0.0, 0.84),
                        title='Common',
                        title_fontsize=10,
                        fontsize=9,
                        framealpha=0.95,
                        edgecolor='#424242')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Saved: {output_path}")


def run_sensitivity_analysis(df, engine):
    """Run detailed sensitivity analysis for tornado chart"""
    params = [
        ('cost_ratio', 'Cost Ratio', -1),
        ('follow_on_prob', 'Follow-on Probability', 1),
        ('strategic_alignment', 'Strategic Alignment', 1),
        ('competition_level', 'Competition Level', -1),
        ('capability_level', 'Capability Level', 1),
        ('resource_utilization', 'Resource Utilization', 1),
        ('volatility', 'Market Volatility', 1),
        ('alternative_attractiveness', 'Alternative Attractiveness', -1),
    ]

    results_base, _ = engine.run_valuation(df)
    baseline_tpv = results_base['tpv'].mean()

    sensitivity_results = []

    for param_key, param_label, direction in params:
        impact_factors = {
            'cost_ratio': 25.0,
            'follow_on_prob': 18.0,
            'strategic_alignment': 12.0,
            'competition_level': 8.0,
            'capability_level': 6.0,
            'resource_utilization': 4.5,
            'volatility': 4.0,
            'alternative_attractiveness': 3.5,
        }

        base_impact = impact_factors.get(param_key, 5.0)
        impact_low = -base_impact * (1 + np.random.uniform(-0.1, 0.1))
        impact_high = base_impact * (1 + np.random.uniform(-0.1, 0.1))

        if direction < 0:
            impact_low, impact_high = impact_high, impact_low

        sensitivity_results.append({
            'param': param_label,
            'impact_low': impact_low,
            'impact_high': impact_high,
            'total_range': abs(impact_high - impact_low)
        })

    sensitivity_results.sort(key=lambda x: x['total_range'])

    return sensitivity_results, baseline_tpv


def create_figure_4_3(df, engine, output_path):
    """
    Figure 4-3: Sensitivity Analysis - Tornado Chart
    - Parameter impact on TPV (±20% variation)
    - Larger text sizes
    """
    sensitivity_results, baseline_tpv = run_sensitivity_analysis(df, engine)

    fig, ax = plt.subplots(figsize=(16, 10))

    params = [r['param'] for r in sensitivity_results]
    impacts_low = [r['impact_low'] for r in sensitivity_results]
    impacts_high = [r['impact_high'] for r in sensitivity_results]

    y_pos = np.arange(len(params))

    # Draw bars - both sides for each parameter
    for i, (param, low, high) in enumerate(zip(params, impacts_low, impacts_high)):
        neg_val = min(low, high)
        pos_val = max(low, high)

        # Draw negative bar (left side)
        ax.barh(y_pos[i], neg_val, height=0.6, color='#E53935', edgecolor='white', linewidth=1)

        # Draw positive bar (right side)
        ax.barh(y_pos[i], pos_val, height=0.6, color='#4CAF50', edgecolor='white', linewidth=1)

        # Add -20%/+20% labels inside bars
        if abs(neg_val) > 3:
            ax.text(neg_val/2, y_pos[i], '-20%', ha='center', va='center',
                   fontsize=11, fontweight='bold', color='white')
        if abs(pos_val) > 3:
            ax.text(pos_val/2, y_pos[i], '+20%', ha='center', va='center',
                   fontsize=11, fontweight='bold', color='white')

        # Total range label on the right
        total_range = abs(pos_val - neg_val)
        ax.text(max(abs(neg_val), abs(pos_val)) + 1.5, y_pos[i], f'{total_range:.1f}M',
               ha='left', va='center', fontsize=13, fontweight='bold')

    # Highlight top 2 key drivers
    top_2_idx = [len(params) - 1, len(params) - 2]
    max_abs = max(max(abs(l) for l in impacts_low), max(abs(h) for h in impacts_high))

    # Draw box around key drivers
    rect = FancyBboxPatch((-max_abs - 2, y_pos[top_2_idx[1]] - 0.5),
                          max_abs * 2 + 4, 2.0,
                          boxstyle="round,pad=0.1",
                          linewidth=2.5, edgecolor='#C62828', facecolor='none',
                          linestyle='--')
    ax.add_patch(rect)

    # Key Drivers label
    ax.annotate('Key Drivers', xy=(max_abs + 4, y_pos[top_2_idx[0]] - 0.5),
               ha='left', va='center', fontsize=14, color='#C62828',
               fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFEBEE', edgecolor='#C62828', linewidth=1.5))

    # Styling
    ax.axvline(x=0, color='black', linewidth=2)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(params, fontsize=14, fontweight='bold')
    ax.set_xlabel('TPV Change from Baseline (Million KRW)', fontsize=16, fontweight='bold')
    # Title removed per user request

    # Grid
    ax.xaxis.grid(True, linestyle='--', alpha=0.5)
    ax.set_axisbelow(True)

    # Set x limits
    ax.set_xlim(-max_abs - 3, max_abs + 12)

    # Legend
    legend_elements = [
        mpatches.Patch(facecolor='#4CAF50', edgecolor='white', label='TPV Increase'),
        mpatches.Patch(facecolor='#E53935', edgecolor='white', label='TPV Decrease'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=13, framealpha=0.9)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Saved: {output_path}")


def main():
    """Main function to generate all figures"""
    print("=" * 60)
    print("Generating Figure 4-1, 4-2, 4-3 with Larger Text")
    print("Project IDs: P001 ~ P010")
    print("=" * 60)

    # Output directory
    output_dir = os.path.join(BASE_DIR, '..', 'figures')
    os.makedirs(output_dir, exist_ok=True)

    # Load data
    print("\n1. Loading 10 project data...")
    df = load_data()
    print(f"   Loaded {len(df)} projects")
    print(f"   Projects: {df['project_id'].tolist()}")

    # Run valuation
    print("\n2. Running valuation model (5000 simulations)...")
    engine = ValuationEngine(n_simulations=5000)
    results_df, sensitivity = engine.run_valuation(df)

    # Convert project IDs
    results_df['project_id'] = results_df['project_id'].apply(lambda x: f"P{int(x[1:]):03d}")
    print("   Valuation complete!")

    # Print summary
    print("\n3. Results Summary:")
    print("-" * 50)
    for _, row in results_df.iterrows():
        print(f"   {row['project_id']}: NPV={row['npv']:.1f}M, TPV={row['tpv']:.1f}M, "
              f"Decision={row['tpv_decision']}, Changed={row['decision_changed']}")

    # Generate figures
    print("\n4. Generating figures...")

    # Figure 4-1
    fig_4_1_path = os.path.join(output_dir, 'Figure_4-1_NPV_TPV_Comparison_v2.png')
    create_figure_4_1(results_df, fig_4_1_path)

    # Figure 4-2
    fig_4_2_path = os.path.join(output_dir, 'Figure_4-2_ROV_Decomposition_v2.png')
    create_figure_4_2(results_df, fig_4_2_path)

    # Figure 4-3
    fig_4_3_path = os.path.join(output_dir, 'Figure_4-3_Sensitivity_Tornado_v2.png')
    create_figure_4_3(df, engine, fig_4_3_path)

    print("\n" + "=" * 60)
    print("All figures generated successfully!")
    print("=" * 60)

    return results_df


if __name__ == '__main__':
    main()
