#!/usr/bin/env python3
"""
BIM Real Options Valuation System - Model Explanation Dashboard
Comprehensive visualization of system architecture, model logic, and analytical flow
"""

import os
import sys
import numpy as np
import pandas as pd

# Path setup
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import customtkinter as ctk
from tkinter import ttk
import tkinter as tk

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle
from matplotlib.patches import ConnectionPatch
import matplotlib.patches as mpatches

# Set appearance
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Color palette
COLORS = {
    'primary': '#1976D2',
    'secondary': '#424242',
    'success': '#388E3C',
    'warning': '#F57C00',
    'danger': '#D32F2F',
    'info': '#0288D1',
    'purple': '#7B1FA2',
    'teal': '#00838F',
    'text_light': '#FFFFFF',
    'text_dark': '#212121',
    'text_secondary': '#757575',
    'bg_light': '#FAFAFA',
    'bg_card': '#FFFFFF',
    'tier0': '#2196F3',
    'tier1': '#4CAF50',
    'tier2': '#FF9800',
    'npv': '#2196F3',
    'rov': '#4CAF50',
    'tpv': '#9C27B0',
}

# ROV Option colors
ROV_COLORS = {
    'follow_on': '#1976D2',
    'capability': '#388E3C',
    'resource': '#7B1FA2',
    'abandonment': '#C62828',
    'contract': '#F57C00',
    'switch': '#00838F',
    'stage': '#5D4037',
}


class ModelDashboard(ctk.CTk):
    """Model Explanation Dashboard"""

    def __init__(self):
        super().__init__()

        self.title("BIM Real Options Valuation - Model Architecture Dashboard")
        self.geometry("1900x1000")
        self.minsize(1600, 900)

        self.figures = []

        self._create_main_layout()
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _create_main_layout(self):
        """Create main layout with tabs"""
        # Title header
        header = ctk.CTkFrame(self, fg_color=COLORS['primary'], height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="BIM Real Options Valuation System - Model Architecture Dashboard",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS['text_light']
        ).pack(pady=15)

        # Tab view
        self.tab_view = ctk.CTkTabview(self, fg_color=COLORS['bg_card'])
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=10)

        # Add tabs
        self.tab_view.add("1. System Overview")
        self.tab_view.add("2. Input Variables")
        self.tab_view.add("3. Tier System")
        self.tab_view.add("4. Valuation Model")
        self.tab_view.add("5. Real Options")
        self.tab_view.add("6. Output & Decisions")
        self.tab_view.add("7. Example Analysis")

        # Setup each tab
        self._setup_overview_tab()
        self._setup_input_tab()
        self._setup_tier_tab()
        self._setup_valuation_tab()
        self._setup_options_tab()
        self._setup_output_tab()
        self._setup_example_tab()

    # ==================== TAB 1: System Overview ====================
    def _setup_overview_tab(self):
        """System architecture overview"""
        tab = self.tab_view.tab("1. System Overview")
        frame = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Title
        ctk.CTkLabel(
            frame,
            text="System Architecture Overview",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS['text_dark']
        ).pack(pady=(10, 5))

        ctk.CTkLabel(
            frame,
            text="This dashboard explains the complete architecture of the BIM Real Options Valuation System,\n"
                 "from input processing through Monte Carlo simulation to final bid decision recommendations.",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary'],
            justify="center"
        ).pack(pady=(0, 20))

        # Architecture diagram
        self._create_architecture_diagram(frame)

        # Key features
        features_frame = ctk.CTkFrame(frame, fg_color=COLORS['bg_card'], corner_radius=10)
        features_frame.pack(fill="x", pady=20, padx=20)

        ctk.CTkLabel(
            features_frame,
            text="Key System Features",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_dark']
        ).pack(pady=(15, 10))

        features = [
            ("3-Tier Input System", "Transforms 7 basic inputs into probabilistic parameters through deterministic derivation"),
            ("Monte Carlo Simulation", "5,000 iterations to capture uncertainty in cost ratios, competition, and strategic factors"),
            ("7 Real Options Valuation", "Comprehensive assessment of managerial flexibility: Follow-on, Capability, Resource, Abandonment, Contract, Switch, Stage"),
            ("3 Adjustment Factors", "Interaction effects, Risk premium, and Deferral costs for realistic ROV estimation"),
            ("Decision Support", "Probability-based recommendations with robustness metrics for informed bid decisions"),
        ]

        for title, desc in features:
            feat_frame = ctk.CTkFrame(features_frame, fg_color="transparent")
            feat_frame.pack(fill="x", padx=20, pady=5)

            ctk.CTkLabel(
                feat_frame,
                text=f"• {title}:",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=COLORS['primary']
            ).pack(side="left")

            ctk.CTkLabel(
                feat_frame,
                text=f" {desc}",
                font=ctk.CTkFont(size=11),
                text_color=COLORS['text_secondary']
            ).pack(side="left")

        ctk.CTkLabel(features_frame, text="").pack(pady=5)  # Spacer

    def _create_architecture_diagram(self, parent):
        """Create system architecture flow diagram"""
        fig, ax = plt.subplots(figsize=(16, 8), dpi=100)
        ax.set_xlim(0, 16)
        ax.set_ylim(0, 8)
        ax.axis('off')

        # Title
        ax.text(8, 7.5, 'BIM Real Options Valuation System Architecture',
                fontsize=14, fontweight='bold', ha='center', va='center')

        # === INPUT LAYER ===
        input_box = FancyBboxPatch((0.5, 4.5), 2.5, 2.5, boxstyle="round,pad=0.1",
                                    facecolor=COLORS['tier0'], alpha=0.3, edgecolor=COLORS['tier0'], linewidth=2)
        ax.add_patch(input_box)
        ax.text(1.75, 6.5, 'INPUT', fontsize=10, fontweight='bold', ha='center', color=COLORS['tier0'])
        ax.text(1.75, 6.0, 'Tier 0', fontsize=9, ha='center', color=COLORS['tier0'])

        inputs = ['Project ID', 'Contract Amount', 'Infra Type', 'Design Phase',
                  'Duration', 'Procurement', 'Client Type']
        for i, inp in enumerate(inputs):
            ax.text(1.75, 5.5 - i*0.2, f'• {inp}', fontsize=7, ha='center')

        # === TIER SYSTEM ===
        tier1_box = FancyBboxPatch((4, 5), 2.5, 2, boxstyle="round,pad=0.1",
                                    facecolor=COLORS['tier1'], alpha=0.3, edgecolor=COLORS['tier1'], linewidth=2)
        ax.add_patch(tier1_box)
        ax.text(5.25, 6.5, 'DERIVATION', fontsize=10, fontweight='bold', ha='center', color=COLORS['tier1'])
        ax.text(5.25, 6.1, 'Tier 1', fontsize=9, ha='center', color=COLORS['tier1'])
        ax.text(5.25, 5.6, 'Deterministic\nTransformation', fontsize=8, ha='center')
        ax.text(5.25, 5.0, '• Follow-on flag\n• Complexity\n• Competition params', fontsize=7, ha='center')

        tier2_box = FancyBboxPatch((4, 2.5), 2.5, 2, boxstyle="round,pad=0.1",
                                    facecolor=COLORS['tier2'], alpha=0.3, edgecolor=COLORS['tier2'], linewidth=2)
        ax.add_patch(tier2_box)
        ax.text(5.25, 4.0, 'SAMPLING', fontsize=10, fontweight='bold', ha='center', color=COLORS['tier2'])
        ax.text(5.25, 3.6, 'Tier 2', fontsize=9, ha='center', color=COLORS['tier2'])
        ax.text(5.25, 3.1, 'Probabilistic\nDistributions', fontsize=8, ha='center')
        ax.text(5.25, 2.5, '• Beta, Triangular\n• Normal, Uniform', fontsize=7, ha='center')

        # === MONTE CARLO ENGINE ===
        mc_box = FancyBboxPatch((7.5, 3), 2.5, 3.5, boxstyle="round,pad=0.1",
                                 facecolor=COLORS['purple'], alpha=0.2, edgecolor=COLORS['purple'], linewidth=2)
        ax.add_patch(mc_box)
        ax.text(8.75, 6.0, 'MONTE CARLO', fontsize=10, fontweight='bold', ha='center', color=COLORS['purple'])
        ax.text(8.75, 5.5, 'Simulation Engine', fontsize=9, ha='center', color=COLORS['purple'])
        ax.text(8.75, 4.8, '5,000 Iterations', fontsize=9, ha='center', fontweight='bold')
        ax.text(8.75, 4.3, 'For each iteration:', fontsize=8, ha='center')
        ax.text(8.75, 3.8, '1. Sample Tier 2\n2. Calculate NPV\n3. Calculate 7 ROVs\n4. Apply adjustments\n5. Compute TPV',
                fontsize=7, ha='center')

        # === OPTIONS VALUATION ===
        rov_box = FancyBboxPatch((11, 4.5), 2.5, 3, boxstyle="round,pad=0.1",
                                  facecolor=COLORS['rov'], alpha=0.2, edgecolor=COLORS['rov'], linewidth=2)
        ax.add_patch(rov_box)
        ax.text(12.25, 7.0, 'REAL OPTIONS', fontsize=10, fontweight='bold', ha='center', color=COLORS['rov'])
        ax.text(12.25, 6.5, '7 Options', fontsize=9, ha='center', color=COLORS['rov'])

        options = ['Follow-on', 'Capability', 'Resource', 'Abandonment', 'Contract', 'Switch', 'Stage']
        for i, opt in enumerate(options):
            ax.text(12.25, 6.0 - i*0.3, f'• {opt}', fontsize=7, ha='center')

        # Adjustments box
        adj_box = FancyBboxPatch((11, 2), 2.5, 2, boxstyle="round,pad=0.1",
                                  facecolor=COLORS['warning'], alpha=0.2, edgecolor=COLORS['warning'], linewidth=2)
        ax.add_patch(adj_box)
        ax.text(12.25, 3.5, 'ADJUSTMENTS', fontsize=10, fontweight='bold', ha='center', color=COLORS['warning'])
        ax.text(12.25, 3.0, '• Interaction (-12%)\n• Risk Premium (-15%)\n• Deferral Cost', fontsize=8, ha='center')

        # === OUTPUT ===
        output_box = FancyBboxPatch((14, 3.5), 1.5, 3, boxstyle="round,pad=0.1",
                                     facecolor=COLORS['tpv'], alpha=0.3, edgecolor=COLORS['tpv'], linewidth=2)
        ax.add_patch(output_box)
        ax.text(14.75, 6.0, 'OUTPUT', fontsize=10, fontweight='bold', ha='center', color=COLORS['tpv'])
        ax.text(14.75, 5.4, 'TPV = NPV + ROV', fontsize=8, ha='center', fontweight='bold')
        ax.text(14.75, 4.8, 'Decision\nProbabilities', fontsize=8, ha='center')
        ax.text(14.75, 4.0, 'Bid\nRecommendation', fontsize=8, ha='center')

        # === ARROWS ===
        arrow_style = dict(arrowstyle='->', color='#666666', lw=1.5)

        # Input -> Tier 1
        ax.annotate('', xy=(4, 5.75), xytext=(3, 5.75), arrowprops=arrow_style)

        # Tier 1 -> Tier 2
        ax.annotate('', xy=(5.25, 4.5), xytext=(5.25, 5), arrowprops=arrow_style)

        # Tier 2 -> MC
        ax.annotate('', xy=(7.5, 4), xytext=(6.5, 3.5), arrowprops=arrow_style)

        # Tier 1 -> MC
        ax.annotate('', xy=(7.5, 5.5), xytext=(6.5, 5.75), arrowprops=arrow_style)

        # MC -> ROV
        ax.annotate('', xy=(11, 5.5), xytext=(10, 5), arrowprops=arrow_style)

        # MC -> Adj
        ax.annotate('', xy=(11, 3), xytext=(10, 3.5), arrowprops=arrow_style)

        # ROV -> Output
        ax.annotate('', xy=(14, 5), xytext=(13.5, 5.5), arrowprops=arrow_style)

        # Adj -> Output
        ax.annotate('', xy=(14, 4.5), xytext=(13.5, 3.5), arrowprops=arrow_style)

        # Formula at bottom
        ax.text(8, 1.2, 'Core Formula:', fontsize=10, fontweight='bold', ha='center')
        ax.text(8, 0.7, 'TPV = NPV + ROV_net', fontsize=11, ha='center',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        ax.text(8, 0.2, 'ROV_net = Σ(7 Options) - Interaction - Risk Premium - Deferral',
                fontsize=9, ha='center')

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", padx=20, pady=10)
        self.figures.append(fig)

    # ==================== TAB 2: Input Variables ====================
    def _setup_input_tab(self):
        """Input variables explanation"""
        tab = self.tab_view.tab("2. Input Variables")
        frame = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            frame,
            text="Tier 0: Input Variables (7 Required Fields)",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS['text_dark']
        ).pack(pady=(10, 5))

        ctk.CTkLabel(
            frame,
            text="These 7 variables can be directly extracted from project bid announcements.\n"
                 "They form the foundation for all subsequent derivations and valuations.",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary'],
            justify="center"
        ).pack(pady=(0, 20))

        # Input variables table
        self._create_input_table(frame)

        # Example data section
        self._create_example_input(frame)

    def _create_input_table(self, parent):
        """Create input variables table"""
        table_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_card'], corner_radius=10)
        table_frame.pack(fill="x", pady=10, padx=20)

        ctk.CTkLabel(
            table_frame,
            text="Input Variable Specifications",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['primary']
        ).pack(pady=(15, 10))

        # Table data
        columns = ("Variable", "Data Type", "Format/Range", "Example", "Description")
        data = [
            ("project_id", "String", "Alphanumeric", "R01", "Unique project identifier"),
            ("contract_amount", "Float", "Million KRW", "520", "Total contract value in millions"),
            ("infra_type", "Categorical", "Road/Bridge/Tunnel", "Road", "Infrastructure category"),
            ("design_phase", "Categorical", "Basic Design/Detailed Design", "Basic Design", "Current design stage"),
            ("contract_duration", "Float", "Years (0.5-3.0)", "1.8", "Project duration in years"),
            ("procurement_type", "Categorical", "Open/Limited/Negotiated", "Limited", "Bidding competition type"),
            ("client_type", "Categorical", "Central/Public Corp/Local", "Central", "Client organization type"),
        ]

        # Create treeview
        style = ttk.Style()
        style.configure("Input.Treeview", rowheight=30)
        style.configure("Input.Treeview.Heading", font=('Segoe UI', 10, 'bold'))

        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=7, style="Input.Treeview")

        widths = [120, 100, 180, 100, 300]
        for col, width in zip(columns, widths):
            tree.heading(col, text=col)
            tree.column(col, width=width, anchor="center" if col != "Description" else "w")

        for row in data:
            tree.insert("", "end", values=row)

        tree.pack(fill="x", padx=20, pady=(0, 15))

    def _create_example_input(self, parent):
        """Create example input visualization"""
        example_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_card'], corner_radius=10)
        example_frame.pack(fill="x", pady=10, padx=20)

        ctk.CTkLabel(
            example_frame,
            text="Sample Input Data (10 Projects)",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['primary']
        ).pack(pady=(15, 10))

        fig, ax = plt.subplots(figsize=(14, 4), dpi=100)

        # Sample data
        projects = ['R01', 'R02', 'R03', 'R04', 'R05', 'R06', 'R07', 'R08', 'R09', 'R10']
        amounts = [520, 180, 280, 450, 120, 95, 680, 220, 850, 320]
        infra = ['Road', 'Road', 'Road', 'Bridge', 'Bridge', 'Bridge', 'Tunnel', 'Tunnel', 'Tunnel', 'Tunnel']
        colors_map = {'Road': COLORS['tier0'], 'Bridge': COLORS['tier1'], 'Tunnel': COLORS['tier2']}
        bar_colors = [colors_map[i] for i in infra]

        bars = ax.bar(projects, amounts, color=bar_colors, alpha=0.8, edgecolor='white')

        ax.set_xlabel('Project ID', fontsize=10)
        ax.set_ylabel('Contract Amount (M KRW)', fontsize=10)
        ax.set_title('Sample Input: Contract Amounts by Infrastructure Type', fontsize=12)
        ax.grid(axis='y', alpha=0.3)

        # Legend
        legend_elements = [mpatches.Patch(facecolor=colors_map['Road'], label='Road'),
                          mpatches.Patch(facecolor=colors_map['Bridge'], label='Bridge'),
                          mpatches.Patch(facecolor=colors_map['Tunnel'], label='Tunnel')]
        ax.legend(handles=legend_elements, loc='upper right')

        # Add value labels
        for bar, val in zip(bars, amounts):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
                   f'{val}', ha='center', va='bottom', fontsize=9)

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=example_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", padx=20, pady=(0, 15))
        self.figures.append(fig)

    # ==================== TAB 3: Tier System ====================
    def _setup_tier_tab(self):
        """Tier system explanation"""
        tab = self.tab_view.tab("3. Tier System")
        frame = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            frame,
            text="3-Tier Input Transformation System",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS['text_dark']
        ).pack(pady=(10, 5))

        ctk.CTkLabel(
            frame,
            text="The system transforms simple bid announcement data into rich probabilistic parameters\n"
                 "through a 3-tier hierarchy: Deterministic → Derived → Probabilistic",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary'],
            justify="center"
        ).pack(pady=(0, 20))

        # Tier transformation diagram
        self._create_tier_diagram(frame)

        # Tier 1 derivation rules
        self._create_tier1_rules(frame)

        # Tier 2 distributions
        self._create_tier2_distributions(frame)

    def _create_tier_diagram(self, parent):
        """Create tier transformation diagram"""
        fig, ax = plt.subplots(figsize=(14, 5), dpi=100)
        ax.set_xlim(0, 14)
        ax.set_ylim(0, 5)
        ax.axis('off')

        # Tier 0
        tier0_box = FancyBboxPatch((0.5, 1), 3.5, 3, boxstyle="round,pad=0.1",
                                    facecolor=COLORS['tier0'], alpha=0.3, edgecolor=COLORS['tier0'], linewidth=2)
        ax.add_patch(tier0_box)
        ax.text(2.25, 3.7, 'TIER 0', fontsize=12, fontweight='bold', ha='center', color=COLORS['tier0'])
        ax.text(2.25, 3.2, 'Raw Input (Deterministic)', fontsize=9, ha='center')
        tier0_vars = ['project_id', 'contract_amount', 'infra_type', 'design_phase',
                      'contract_duration', 'procurement_type', 'client_type']
        for i, var in enumerate(tier0_vars):
            ax.text(2.25, 2.7 - i*0.25, f'• {var}', fontsize=8, ha='center')

        # Arrow 1
        ax.annotate('', xy=(5, 2.5), xytext=(4, 2.5),
                   arrowprops=dict(arrowstyle='->', color='#666666', lw=2))
        ax.text(4.5, 2.9, 'Derivation\nRules', fontsize=8, ha='center')

        # Tier 1
        tier1_box = FancyBboxPatch((5, 1), 3.5, 3, boxstyle="round,pad=0.1",
                                    facecolor=COLORS['tier1'], alpha=0.3, edgecolor=COLORS['tier1'], linewidth=2)
        ax.add_patch(tier1_box)
        ax.text(6.75, 3.7, 'TIER 1', fontsize=12, fontweight='bold', ha='center', color=COLORS['tier1'])
        ax.text(6.75, 3.2, 'Derived (Deterministic)', fontsize=9, ha='center')
        tier1_vars = ['has_follow_on', 'complexity', 'competition_params',
                      'n_milestones', 'follow_on_beta_params', 'client_reliability']
        for i, var in enumerate(tier1_vars):
            ax.text(6.75, 2.7 - i*0.25, f'• {var}', fontsize=8, ha='center')

        # Arrow 2
        ax.annotate('', xy=(9.5, 2.5), xytext=(8.5, 2.5),
                   arrowprops=dict(arrowstyle='->', color='#666666', lw=2))
        ax.text(9, 2.9, 'Probability\nDistributions', fontsize=8, ha='center')

        # Tier 2
        tier2_box = FancyBboxPatch((9.5, 1), 4, 3, boxstyle="round,pad=0.1",
                                    facecolor=COLORS['tier2'], alpha=0.3, edgecolor=COLORS['tier2'], linewidth=2)
        ax.add_patch(tier2_box)
        ax.text(11.5, 3.7, 'TIER 2', fontsize=12, fontweight='bold', ha='center', color=COLORS['tier2'])
        ax.text(11.5, 3.2, 'Sampled (Probabilistic)', fontsize=9, ha='center')
        tier2_vars = ['cost_ratio ~ Triangular', 'follow_on_prob ~ Beta',
                      'volatility ~ Normal', 'competition_level ~ Normal',
                      'strategic_alignment ~ Uniform', 'capability_level ~ Triangular']
        for i, var in enumerate(tier2_vars):
            ax.text(11.5, 2.7 - i*0.25, f'• {var}', fontsize=8, ha='center')

        ax.text(7, 0.5, 'Each Monte Carlo iteration samples new Tier 2 values based on Tier 1 parameters',
               fontsize=10, ha='center', style='italic')

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", padx=20, pady=10)
        self.figures.append(fig)

    def _create_tier1_rules(self, parent):
        """Create Tier 1 derivation rules table"""
        rules_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_card'], corner_radius=10)
        rules_frame.pack(fill="x", pady=10, padx=20)

        ctk.CTkLabel(
            rules_frame,
            text="Tier 1 Derivation Rules",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['tier1']
        ).pack(pady=(15, 10))

        rules_text = """
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  Tier 0 Input           │  Tier 1 Output          │  Derivation Logic                       │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│  design_phase           │  has_follow_on          │  True if "Basic Design", else False     │
│  infra_type + amount    │  complexity             │  Tunnel=high, Bridge=medium, Road=low   │
│                         │                         │  (+1 level if amount >= 300M)           │
│  procurement_type       │  competition_params     │  Open: μ=0.6, σ=0.15                    │
│                         │                         │  Limited: μ=0.4, σ=0.10                 │
│                         │                         │  Negotiated: μ=0.2, σ=0.05              │
│  infra_type             │  n_milestones           │  Road=3, Bridge=3, Tunnel=4             │
│  design_phase           │  follow_on_beta_params  │  Basic: Beta(4,2), Detailed: Beta(1.5,4)│
│  client_type            │  client_reliability     │  Central=0.9, Public Corp=0.8, Local=0.6│
└─────────────────────────────────────────────────────────────────────────────────────────────┘
        """

        ctk.CTkLabel(
            rules_frame,
            text=rules_text,
            font=ctk.CTkFont(family="Consolas", size=10),
            text_color=COLORS['text_dark'],
            justify="left"
        ).pack(padx=20, pady=(0, 15))

    def _create_tier2_distributions(self, parent):
        """Create Tier 2 distribution visualizations"""
        dist_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_card'], corner_radius=10)
        dist_frame.pack(fill="x", pady=10, padx=20)

        ctk.CTkLabel(
            dist_frame,
            text="Tier 2 Probability Distributions",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['tier2']
        ).pack(pady=(15, 10))

        fig, axes = plt.subplots(2, 3, figsize=(14, 6), dpi=100)

        # Cost ratio - Triangular
        x = np.linspace(0.7, 1.1, 100)
        from scipy import stats
        y = stats.triang.pdf(x, c=0.33, loc=0.75, scale=0.30)
        axes[0, 0].fill_between(x, y, alpha=0.3, color=COLORS['tier2'])
        axes[0, 0].plot(x, y, color=COLORS['tier2'], lw=2)
        axes[0, 0].set_title('Cost Ratio\nTriangular(0.75, 0.85, 1.05)', fontsize=10)
        axes[0, 0].axvline(x=0.85, color='red', linestyle='--', label='mode')
        axes[0, 0].legend(fontsize=8)

        # Follow-on probability - Beta
        x = np.linspace(0, 1, 100)
        y1 = stats.beta.pdf(x, 4, 2)
        y2 = stats.beta.pdf(x, 1.5, 4)
        axes[0, 1].fill_between(x, y1, alpha=0.3, color=COLORS['tier1'], label='Basic: Beta(4,2)')
        axes[0, 1].fill_between(x, y2, alpha=0.3, color=COLORS['danger'], label='Detailed: Beta(1.5,4)')
        axes[0, 1].plot(x, y1, color=COLORS['tier1'], lw=2)
        axes[0, 1].plot(x, y2, color=COLORS['danger'], lw=2)
        axes[0, 1].set_title('Follow-on Probability\nBeta Distribution', fontsize=10)
        axes[0, 1].legend(fontsize=8)

        # Volatility - Normal
        x = np.linspace(0.1, 0.4, 100)
        y = stats.norm.pdf(x, 0.25, 0.05)
        axes[0, 2].fill_between(x, y, alpha=0.3, color=COLORS['purple'])
        axes[0, 2].plot(x, y, color=COLORS['purple'], lw=2)
        axes[0, 2].set_title('Volatility\nNormal(0.25, 0.05)', fontsize=10)
        axes[0, 2].axvline(x=0.25, color='red', linestyle='--', label='mean')
        axes[0, 2].legend(fontsize=8)

        # Competition level - Normal (varies by procurement)
        x = np.linspace(0, 1, 100)
        y1 = stats.norm.pdf(x, 0.6, 0.15)
        y2 = stats.norm.pdf(x, 0.4, 0.10)
        y3 = stats.norm.pdf(x, 0.2, 0.05)
        axes[1, 0].plot(x, y1, color=COLORS['danger'], lw=2, label='Open')
        axes[1, 0].plot(x, y2, color=COLORS['warning'], lw=2, label='Limited')
        axes[1, 0].plot(x, y3, color=COLORS['success'], lw=2, label='Negotiated')
        axes[1, 0].set_title('Competition Level\nNormal (by procurement)', fontsize=10)
        axes[1, 0].legend(fontsize=8)

        # Strategic alignment - Uniform
        x = np.linspace(0, 1, 100)
        y = np.where((x >= 0.3) & (x <= 0.9), 1/(0.9-0.3), 0)
        axes[1, 1].fill_between(x, y, alpha=0.3, color=COLORS['info'])
        axes[1, 1].plot(x, y, color=COLORS['info'], lw=2)
        axes[1, 1].set_title('Strategic Alignment\nUniform(0.3, 0.9)', fontsize=10)

        # Capability level - Triangular
        x = np.linspace(0, 1, 100)
        y = stats.triang.pdf(x, c=0.5, loc=0.3, scale=0.5)
        axes[1, 2].fill_between(x, y, alpha=0.3, color=COLORS['teal'])
        axes[1, 2].plot(x, y, color=COLORS['teal'], lw=2)
        axes[1, 2].set_title('Capability Level\nTriangular(0.3, 0.55, 0.8)', fontsize=10)

        for ax in axes.flat:
            ax.grid(alpha=0.3)

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=dist_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", padx=20, pady=(0, 15))
        self.figures.append(fig)

    # ==================== TAB 4: Valuation Model ====================
    def _setup_valuation_tab(self):
        """Valuation model explanation"""
        tab = self.tab_view.tab("4. Valuation Model")
        frame = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            frame,
            text="Monte Carlo Valuation Engine",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS['text_dark']
        ).pack(pady=(10, 5))

        # NPV calculation
        self._create_npv_section(frame)

        # TPV formula
        self._create_tpv_formula(frame)

        # Monte Carlo process
        self._create_mc_process(frame)

    def _create_npv_section(self, parent):
        """Create NPV calculation section"""
        npv_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_card'], corner_radius=10)
        npv_frame.pack(fill="x", pady=10, padx=20)

        ctk.CTkLabel(
            npv_frame,
            text="NPV Calculation",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['npv']
        ).pack(pady=(15, 10))

        formula_text = """
NPV = Contract Amount × (1 - Cost Ratio) × Discount Factor

Where:
  • Contract Amount: From Tier 0 input (Million KRW)
  • Cost Ratio: Sampled from Triangular(0.75, 0.85, 1.05) - represents cost/revenue ratio
  • Discount Factor: exp(-r × T) where r = 9% (discount rate), T = contract duration

Example:
  Contract = 520M, Cost Ratio = 0.82, Duration = 1.8 years
  NPV = 520 × (1 - 0.82) × exp(-0.09 × 1.8) = 520 × 0.18 × 0.85 = 79.56M
        """

        ctk.CTkLabel(
            npv_frame,
            text=formula_text,
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color=COLORS['text_dark'],
            justify="left"
        ).pack(padx=20, pady=(0, 15))

    def _create_tpv_formula(self, parent):
        """Create TPV formula section"""
        tpv_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_card'], corner_radius=10)
        tpv_frame.pack(fill="x", pady=10, padx=20)

        ctk.CTkLabel(
            tpv_frame,
            text="Total Project Value (TPV) Formula",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['tpv']
        ).pack(pady=(15, 10))

        fig, ax = plt.subplots(figsize=(12, 4), dpi=100)
        ax.axis('off')

        # Main formula box
        main_box = FancyBboxPatch((1, 2), 10, 1.5, boxstyle="round,pad=0.1",
                                   facecolor=COLORS['tpv'], alpha=0.2, edgecolor=COLORS['tpv'], linewidth=2)
        ax.add_patch(main_box)
        ax.text(6, 2.75, 'TPV = NPV + ROV_net', fontsize=16, fontweight='bold', ha='center', va='center')

        # ROV breakdown
        ax.text(6, 1.5, 'ROV_net = ROV_gross - Interaction - Risk Premium - Deferral',
               fontsize=12, ha='center')

        ax.text(6, 0.8, 'ROV_gross = Follow-on + Capability + Resource + Abandonment + Contract + Switch + Stage',
               fontsize=10, ha='center')

        # Parameters
        ax.text(6, 0.2, 'Interaction = 12% × ROV_gross  |  Risk Premium = 15% × ROV_gross  |  Deferral = 5% × ROV_gross × T',
               fontsize=9, ha='center', color=COLORS['text_secondary'])

        ax.set_xlim(0, 12)
        ax.set_ylim(0, 4)

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=tpv_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", padx=20, pady=(0, 15))
        self.figures.append(fig)

    def _create_mc_process(self, parent):
        """Create Monte Carlo process diagram"""
        mc_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_card'], corner_radius=10)
        mc_frame.pack(fill="x", pady=10, padx=20)

        ctk.CTkLabel(
            mc_frame,
            text="Monte Carlo Simulation Process (5,000 iterations)",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['purple']
        ).pack(pady=(15, 10))

        process_text = """
┌────────────────────────────────────────────────────────────────────────────────────┐
│  FOR each iteration i = 1 to 5,000:                                                │
│                                                                                    │
│    1. SAMPLE Tier 2 parameters from probability distributions                      │
│       • cost_ratio[i] ~ Triangular(0.75, 0.85, 1.05)                              │
│       • follow_on_prob[i] ~ Beta(α, β)  # from Tier 1                             │
│       • volatility[i] ~ Normal(0.25, 0.05)                                        │
│       • strategic_alignment[i] ~ Uniform(0.3, 0.9)                                │
│       • ... other parameters                                                       │
│                                                                                    │
│    2. CALCULATE NPV[i]                                                             │
│       NPV[i] = Contract × (1 - cost_ratio[i]) × exp(-r × T)                       │
│                                                                                    │
│    3. CALCULATE each Real Option value                                             │
│       ROV_follow_on[i], ROV_capability[i], ... ROV_stage[i]                       │
│                                                                                    │
│    4. APPLY adjustments                                                            │
│       ROV_net[i] = Σ(options) × (1 - 0.12) × (1 - 0.15) - deferral                │
│                                                                                    │
│    5. COMPUTE TPV[i] = NPV[i] + ROV_net[i]                                        │
│                                                                                    │
│  END FOR                                                                           │
│                                                                                    │
│  OUTPUT: Distribution of 5,000 TPV values → Decision probabilities                 │
└────────────────────────────────────────────────────────────────────────────────────┘
        """

        ctk.CTkLabel(
            mc_frame,
            text=process_text,
            font=ctk.CTkFont(family="Consolas", size=10),
            text_color=COLORS['text_dark'],
            justify="left"
        ).pack(padx=20, pady=(0, 15))

    # ==================== TAB 5: Real Options ====================
    def _setup_options_tab(self):
        """Real options explanation"""
        tab = self.tab_view.tab("5. Real Options")
        frame = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            frame,
            text="7 Real Options Valuation",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS['text_dark']
        ).pack(pady=(10, 5))

        ctk.CTkLabel(
            frame,
            text="Each option represents a different type of managerial flexibility that adds strategic value beyond NPV.",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary']
        ).pack(pady=(0, 20))

        # Options overview chart
        self._create_options_overview(frame)

        # Detailed formulas
        self._create_options_formulas(frame)

    def _create_options_overview(self, parent):
        """Create options overview visualization"""
        overview_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_card'], corner_radius=10)
        overview_frame.pack(fill="x", pady=10, padx=20)

        fig, ax = plt.subplots(figsize=(14, 5), dpi=100)

        options = ['Follow-on', 'Capability', 'Resource', 'Abandonment', 'Contract', 'Switch', 'Stage']
        descriptions = [
            'Future project\nopportunities',
            'BIM expertise\nvalue growth',
            'Workforce\nflexibility',
            'Exit option\nvalue',
            'Scope change\nflexibility',
            'Technology\npivot option',
            'Phased\ncommitment'
        ]

        colors_list = list(ROV_COLORS.values())

        # Example values (proportional to typical contribution)
        values = [35, 25, 15, 8, 10, 5, 7]

        bars = ax.bar(options, values, color=colors_list, alpha=0.8, edgecolor='white')

        # Add descriptions below bars
        for i, (bar, desc) in enumerate(zip(bars, descriptions)):
            ax.text(bar.get_x() + bar.get_width()/2, -8, desc,
                   ha='center', va='top', fontsize=8, color=COLORS['text_secondary'])
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                   f'{values[i]}%', ha='center', va='bottom', fontsize=10, fontweight='bold')

        ax.set_ylabel('Typical Contribution to ROV (%)', fontsize=10)
        ax.set_title('Real Options Composition (Typical Distribution)', fontsize=12)
        ax.set_ylim(-15, 45)
        ax.axhline(y=0, color='black', linewidth=0.5)
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=overview_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", padx=20, pady=15)
        self.figures.append(fig)

    def _create_options_formulas(self, parent):
        """Create detailed options formulas"""
        formulas_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_card'], corner_radius=10)
        formulas_frame.pack(fill="x", pady=10, padx=20)

        ctk.CTkLabel(
            formulas_frame,
            text="Real Options Valuation Formulas",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['rov']
        ).pack(pady=(15, 10))

        formulas = [
            ("1. Follow-on Option", "Contract × Follow_on_Prob × Multiplier(1.5~2.5) × Exercise_Rate(0.50)",
             "Captures value of potential follow-on design projects (e.g., detailed design after basic design)"),
            ("2. Capability Option", "Contract × Strategic_Alignment × Capability_Level × Growth_Rate(0.10)",
             "Value of building BIM expertise that can be leveraged in future projects"),
            ("3. Resource Option", "Contract × Resource_Utilization × Premium(0.06)",
             "Flexibility value from workforce allocation and utilization efficiency"),
            ("4. Abandonment Option", "max(0, Loss) × Recovery_Rate",
             "Right to exit unprofitable projects and recover partial investment"),
            ("5. Contract Option", "Contract × Flexibility × Flex_Rate(0.05)",
             "Option to modify scope, terms, or deliverables during project execution"),
            ("6. Switch Option", "Contract × Mobility × Switch_Rate(0.04)",
             "Ability to pivot between technologies or methodologies (e.g., BIM levels)"),
            ("7. Stage Option", "Contract × (1/N_Milestones) × Checkpoint_Value(0.03)",
             "Value of phased investment with go/no-go decisions at each milestone"),
        ]

        for name, formula, desc in formulas:
            opt_frame = ctk.CTkFrame(formulas_frame, fg_color="transparent")
            opt_frame.pack(fill="x", padx=20, pady=5)

            ctk.CTkLabel(
                opt_frame,
                text=name,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=COLORS['primary']
            ).pack(anchor="w")

            ctk.CTkLabel(
                opt_frame,
                text=f"Formula: {formula}",
                font=ctk.CTkFont(family="Consolas", size=10),
                text_color=COLORS['text_dark']
            ).pack(anchor="w", padx=20)

            ctk.CTkLabel(
                opt_frame,
                text=desc,
                font=ctk.CTkFont(size=10),
                text_color=COLORS['text_secondary']
            ).pack(anchor="w", padx=20)

        ctk.CTkLabel(formulas_frame, text="").pack(pady=5)

    # ==================== TAB 6: Output & Decisions ====================
    def _setup_output_tab(self):
        """Output and decisions explanation"""
        tab = self.tab_view.tab("6. Output & Decisions")
        frame = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            frame,
            text="Output Metrics & Decision Framework",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS['text_dark']
        ).pack(pady=(10, 5))

        # Decision categories
        self._create_decision_categories(frame)

        # Output metrics
        self._create_output_metrics(frame)

        # Decision flow
        self._create_decision_flow(frame)

    def _create_decision_categories(self, parent):
        """Create decision categories visualization"""
        cat_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_card'], corner_radius=10)
        cat_frame.pack(fill="x", pady=10, padx=20)

        ctk.CTkLabel(
            cat_frame,
            text="Decision Categories (Based on Monte Carlo Distribution)",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['primary']
        ).pack(pady=(15, 10))

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 4), dpi=100)

        # Left: Category definitions
        categories = ['Strong Participate', 'Participate', 'Conditional', 'Reject']
        thresholds = ['TPV > NPV×1.5 AND TPV > 30M', 'NPV×1.05 < TPV ≤ NPV×1.5',
                      'NPV×0.80 < TPV ≤ NPV×1.05', 'TPV ≤ NPV×0.80 OR TPV ≤ 0']
        colors = [COLORS['success'], '#81C784', COLORS['warning'], COLORS['danger']]

        y_pos = np.arange(len(categories))
        bars = ax1.barh(y_pos, [1, 1, 1, 1], color=colors, alpha=0.8)
        ax1.set_yticks(y_pos)
        ax1.set_yticklabels(categories, fontsize=10)
        ax1.set_xlim(0, 1.5)
        ax1.set_title('Decision Categories', fontsize=12)

        for i, (bar, thresh) in enumerate(zip(bars, thresholds)):
            ax1.text(0.1, bar.get_y() + bar.get_height()/2, thresh,
                    va='center', fontsize=9, color='white', fontweight='bold')

        ax1.set_xticks([])

        # Right: Example distribution
        np.random.seed(42)
        tpv_samples = np.random.normal(50, 30, 1000)

        ax2.hist(tpv_samples, bins=50, color=COLORS['tpv'], alpha=0.7, edgecolor='white')
        ax2.axvline(x=0, color='black', linestyle='-', linewidth=2, label='Break-even')
        ax2.axvline(x=30, color=COLORS['success'], linestyle='--', linewidth=2, label='Strong threshold')

        ax2.set_xlabel('TPV (M KRW)', fontsize=10)
        ax2.set_ylabel('Frequency', fontsize=10)
        ax2.set_title('Example: TPV Distribution from Monte Carlo', fontsize=12)
        ax2.legend(fontsize=9)
        ax2.grid(alpha=0.3)

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=cat_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", padx=20, pady=(0, 15))
        self.figures.append(fig)

    def _create_output_metrics(self, parent):
        """Create output metrics table"""
        metrics_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_card'], corner_radius=10)
        metrics_frame.pack(fill="x", pady=10, padx=20)

        ctk.CTkLabel(
            metrics_frame,
            text="Output Metrics",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['primary']
        ).pack(pady=(15, 10))

        metrics_text = """
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  Metric                    │  Description                                                   │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│  NPV                       │  Traditional Net Present Value (deterministic)                 │
│  ROV_gross                 │  Sum of 7 real option values before adjustments               │
│  ROV_net                   │  ROV after interaction, risk premium, deferral adjustments    │
│  TPV                       │  Total Project Value = NPV + ROV_net                          │
│  TPV_CI_lower (5%)         │  5th percentile of Monte Carlo TPV distribution               │
│  TPV_CI_upper (95%)        │  95th percentile of Monte Carlo TPV distribution              │
│  prob_strong_participate   │  P(Strong Participate) from Monte Carlo                       │
│  prob_participate          │  P(Participate) from Monte Carlo                              │
│  prob_conditional          │  P(Conditional) from Monte Carlo                              │
│  prob_reject               │  P(Reject) from Monte Carlo                                   │
│  decision_robustness       │  Probability of the most likely decision category             │
│  npv_decision              │  Decision based on NPV alone (Participate if NPV > 0)         │
│  tpv_decision              │  Decision based on TPV distribution (highest probability)     │
│  decision_changed          │  Whether NPV and TPV decisions differ                         │
│  decision_direction        │  Up (Reject→Participate) or Down (Participate→Reject)         │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
        """

        ctk.CTkLabel(
            metrics_frame,
            text=metrics_text,
            font=ctk.CTkFont(family="Consolas", size=10),
            text_color=COLORS['text_dark'],
            justify="left"
        ).pack(padx=20, pady=(0, 15))

    def _create_decision_flow(self, parent):
        """Create decision flow diagram"""
        flow_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_card'], corner_radius=10)
        flow_frame.pack(fill="x", pady=10, padx=20)

        ctk.CTkLabel(
            flow_frame,
            text="Decision Flow Logic",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['primary']
        ).pack(pady=(15, 10))

        fig, ax = plt.subplots(figsize=(14, 5), dpi=100)
        ax.axis('off')
        ax.set_xlim(0, 14)
        ax.set_ylim(0, 5)

        # NPV Decision
        npv_box = FancyBboxPatch((0.5, 3), 3, 1.5, boxstyle="round,pad=0.1",
                                  facecolor=COLORS['npv'], alpha=0.3, edgecolor=COLORS['npv'], linewidth=2)
        ax.add_patch(npv_box)
        ax.text(2, 4.0, 'NPV Decision', fontsize=11, fontweight='bold', ha='center')
        ax.text(2, 3.5, 'NPV > 0 → Participate\nNPV ≤ 0 → Reject', fontsize=9, ha='center')

        # TPV Decision
        tpv_box = FancyBboxPatch((5, 3), 3, 1.5, boxstyle="round,pad=0.1",
                                  facecolor=COLORS['tpv'], alpha=0.3, edgecolor=COLORS['tpv'], linewidth=2)
        ax.add_patch(tpv_box)
        ax.text(6.5, 4.0, 'TPV Decision', fontsize=11, fontweight='bold', ha='center')
        ax.text(6.5, 3.5, 'Most likely category\nfrom MC distribution', fontsize=9, ha='center')

        # Comparison
        comp_box = FancyBboxPatch((9.5, 3), 4, 1.5, boxstyle="round,pad=0.1",
                                   facecolor=COLORS['warning'], alpha=0.3, edgecolor=COLORS['warning'], linewidth=2)
        ax.add_patch(comp_box)
        ax.text(11.5, 4.0, 'Decision Comparison', fontsize=11, fontweight='bold', ha='center')
        ax.text(11.5, 3.5, 'Changed? Direction?\nUp/Down/No Change', fontsize=9, ha='center')

        # Arrows
        ax.annotate('', xy=(5, 3.75), xytext=(3.5, 3.75), arrowprops=dict(arrowstyle='->', color='#666', lw=1.5))
        ax.annotate('', xy=(9.5, 3.75), xytext=(8, 3.75), arrowprops=dict(arrowstyle='->', color='#666', lw=1.5))

        # Decision outcomes
        outcomes = [
            (1, 1.5, 'Strong Participate', COLORS['success'], 'Highly recommended'),
            (4, 1.5, 'Participate', '#81C784', 'Recommended'),
            (7, 1.5, 'Conditional', COLORS['warning'], 'Caution advised'),
            (10, 1.5, 'Reject', COLORS['danger'], 'Not recommended'),
        ]

        for x, y, label, color, desc in outcomes:
            box = FancyBboxPatch((x-0.8, y-0.4), 2.5, 0.8, boxstyle="round,pad=0.05",
                                  facecolor=color, alpha=0.5, edgecolor=color, linewidth=1)
            ax.add_patch(box)
            ax.text(x+0.45, y+0.1, label, fontsize=9, fontweight='bold', ha='center', color='white')
            ax.text(x+0.45, y-0.2, desc, fontsize=7, ha='center', color='white')

        ax.text(7, 0.5, 'Final Recommendation = TPV Decision + Robustness Assessment',
               fontsize=11, ha='center', fontweight='bold')

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=flow_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", padx=20, pady=(0, 15))
        self.figures.append(fig)

    # ==================== TAB 7: Example Analysis ====================
    def _setup_example_tab(self):
        """Example analysis walkthrough"""
        tab = self.tab_view.tab("7. Example Analysis")
        frame = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            frame,
            text="Complete Example: Project R01 Analysis",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS['text_dark']
        ).pack(pady=(10, 5))

        # Step 1: Input
        self._create_example_input_section(frame)

        # Step 2: Tier transformation
        self._create_example_tier_section(frame)

        # Step 3: Valuation results
        self._create_example_results_section(frame)

        # Step 4: Decision
        self._create_example_decision_section(frame)

    def _create_example_input_section(self, parent):
        """Example input section"""
        input_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_card'], corner_radius=10)
        input_frame.pack(fill="x", pady=10, padx=20)

        ctk.CTkLabel(
            input_frame,
            text="Step 1: Input Data (Tier 0)",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['tier0']
        ).pack(pady=(15, 10))

        input_text = """
┌─────────────────────────────────────────────────────────────────┐
│  Variable           │  Value                                    │
├─────────────────────────────────────────────────────────────────┤
│  project_id         │  R01                                      │
│  contract_amount    │  520 Million KRW                          │
│  infra_type         │  Road                                     │
│  design_phase       │  Basic Design                             │
│  contract_duration  │  1.8 years                                │
│  procurement_type   │  Limited                                  │
│  client_type        │  Central                                  │
└─────────────────────────────────────────────────────────────────┘
        """

        ctk.CTkLabel(
            input_frame,
            text=input_text,
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color=COLORS['text_dark'],
            justify="left"
        ).pack(padx=20, pady=(0, 15))

    def _create_example_tier_section(self, parent):
        """Example tier transformation section"""
        tier_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_card'], corner_radius=10)
        tier_frame.pack(fill="x", pady=10, padx=20)

        ctk.CTkLabel(
            tier_frame,
            text="Step 2: Tier Transformation",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['tier1']
        ).pack(pady=(15, 10))

        tier_text = """
Tier 1 Derivation:
  • has_follow_on = True (Basic Design → follow-on possible)
  • complexity = "medium" (Road + amount >= 300M → upgrade from low)
  • competition_params = {mean: 0.4, std: 0.10} (Limited competition)
  • n_milestones = 3 (Road infrastructure)
  • follow_on_beta_params = (4, 2) (Basic Design → high follow-on probability)
  • client_reliability = 0.9 (Central government client)

Tier 2 Sample (one iteration):
  • cost_ratio = 0.82 (sampled from Triangular)
  • follow_on_prob = 0.68 (sampled from Beta(4,2))
  • volatility = 0.27 (sampled from Normal)
  • strategic_alignment = 0.72 (sampled from Uniform)
  • capability_level = 0.58 (sampled from Triangular)
  • competition_level = 0.38 (sampled from Normal)
        """

        ctk.CTkLabel(
            tier_frame,
            text=tier_text,
            font=ctk.CTkFont(family="Consolas", size=10),
            text_color=COLORS['text_dark'],
            justify="left"
        ).pack(padx=20, pady=(0, 15))

    def _create_example_results_section(self, parent):
        """Example valuation results section"""
        results_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_card'], corner_radius=10)
        results_frame.pack(fill="x", pady=10, padx=20)

        ctk.CTkLabel(
            results_frame,
            text="Step 3: Valuation Results (Monte Carlo Mean)",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['rov']
        ).pack(pady=(15, 10))

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 4), dpi=100)

        # Left: Value breakdown
        categories = ['NPV', 'ROV_gross', 'Adjustments', 'ROV_net', 'TPV']
        values = [79.56, 45.20, -12.35, 32.85, 112.41]
        colors = [COLORS['npv'], COLORS['rov'], COLORS['warning'], COLORS['rov'], COLORS['tpv']]

        bars = ax1.bar(categories, values, color=colors, alpha=0.8, edgecolor='white')
        ax1.axhline(y=0, color='black', linewidth=0.5)
        ax1.set_ylabel('Value (M KRW)', fontsize=10)
        ax1.set_title('Project R01: Value Breakdown', fontsize=12)
        ax1.grid(axis='y', alpha=0.3)

        for bar, val in zip(bars, values):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                    f'{val:.2f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

        # Right: ROV components
        options = ['Follow-on', 'Capability', 'Resource', 'Abandon', 'Contract', 'Switch', 'Stage']
        rov_values = [17.68, 10.90, 6.24, 3.12, 4.16, 1.87, 1.23]
        rov_colors = list(ROV_COLORS.values())

        bars2 = ax2.barh(options, rov_values, color=rov_colors, alpha=0.8, edgecolor='white')
        ax2.set_xlabel('Value (M KRW)', fontsize=10)
        ax2.set_title('ROV Components Breakdown', fontsize=12)
        ax2.grid(axis='x', alpha=0.3)

        for bar, val in zip(bars2, rov_values):
            ax2.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                    f'{val:.2f}', va='center', fontsize=9)

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=results_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", padx=20, pady=(0, 15))
        self.figures.append(fig)

    def _create_example_decision_section(self, parent):
        """Example decision section"""
        decision_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_card'], corner_radius=10)
        decision_frame.pack(fill="x", pady=10, padx=20)

        ctk.CTkLabel(
            decision_frame,
            text="Step 4: Decision Recommendation",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['tpv']
        ).pack(pady=(15, 10))

        decision_text = """
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│  Decision Analysis for Project R01                                                       │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│  NPV Decision:      Participate (NPV = 79.56M > 0)                                      │
│  TPV Decision:      Strong Participate (highest probability)                             │
│  Decision Changed:  No (both recommend participation)                                    │
│                                                                                          │
│  Decision Probabilities:                                                                 │
│    • Strong Participate: 68.4%                                                           │
│    • Participate:        24.2%                                                           │
│    • Conditional:         5.8%                                                           │
│    • Reject:              1.6%                                                           │
│                                                                                          │
│  Robustness: 68.4% (HIGH confidence)                                                     │
│  90% CI: [85.32M, 139.50M]                                                               │
│                                                                                          │
│  RECOMMENDATION: STRONG PARTICIPATE                                                      │
│  Real options analysis confirms NPV decision with high confidence.                       │
│  The ROV of 32.85M (6.3% of contract) adds significant strategic value                  │
│  primarily from Follow-on Option (17.68M) due to Basic Design phase.                    │
└─────────────────────────────────────────────────────────────────────────────────────────┘
        """

        ctk.CTkLabel(
            decision_frame,
            text=decision_text,
            font=ctk.CTkFont(family="Consolas", size=10),
            text_color=COLORS['text_dark'],
            justify="left"
        ).pack(padx=20, pady=(0, 15))

    def _on_closing(self):
        """Handle window close"""
        for fig in self.figures:
            plt.close(fig)
        self.figures.clear()
        self.destroy()


def main():
    """Main entry point"""
    app = ModelDashboard()
    app.mainloop()


if __name__ == "__main__":
    main()
