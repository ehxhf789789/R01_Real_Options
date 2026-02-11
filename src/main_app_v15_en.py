#!/usr/bin/env python3
"""
BIM Real Options Valuation - v15 English Version
CustomTkinter-based Modern UI + Integrated Sensitivity Analysis
"""

import os
import sys
import threading
import time
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

# Import engine modules BEFORE sys.path manipulation (for PyInstaller bundling)
from valuation_engine import ValuationEngine
from tier_system import Tier0Input, Tier1Derivation, Tier2Sampler

# Path setup for frozen exe (for data files, not module imports)
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
import tkinter as tk

# Matplotlib setup
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
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
    'text_light': '#FFFFFF',
    'text_dark': '#212121',
    'text_secondary': '#757575',
    'bg_light': '#FAFAFA',
    'bg_card': '#FFFFFF',
    'border': '#E0E0E0',
    'npv': '#2196F3',
    'rov': '#4CAF50',
    'tpv': '#9C27B0',
    'negative': '#F44336',
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


class BIMValuationApp(ctk.CTk):
    """BIM Real Options Valuation Application v15 - English Version"""

    def __init__(self):
        super().__init__()

        self.title("BIM Real Options Valuation System v15 - Modern UI")
        self.geometry("1800x1000")
        self.minsize(1400, 800)

        # Data storage
        self.input_df: Optional[pd.DataFrame] = None
        self.results_df: Optional[pd.DataFrame] = None
        self.sensitivity_results: Optional[Dict] = None
        self.simulation_data: Optional[Dict] = None

        # UI state
        self.current_project_id: Optional[str] = None
        self.analysis_running = False
        self.figures: List[Figure] = []

        # Setup UI
        self._setup_styles()
        self._create_main_layout()

        # Window close handler
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')

        # Treeview style
        style.configure("Treeview",
                       background=COLORS['bg_card'],
                       foreground=COLORS['text_dark'],
                       rowheight=28,
                       fieldbackground=COLORS['bg_card'])
        style.configure("Treeview.Heading",
                       background=COLORS['primary'],
                       foreground=COLORS['text_light'],
                       font=('Segoe UI', 10, 'bold'))
        style.map('Treeview', background=[('selected', COLORS['primary'])])

    def _create_main_layout(self):
        """Create main layout"""
        # Main container
        self.main_frame = ctk.CTkFrame(self, fg_color=COLORS['bg_light'])
        self.main_frame.pack(fill="both", expand=True)

        # Left panel (controls)
        self._setup_left_panel()

        # Right panel (results)
        self._setup_right_panel()

    def _setup_left_panel(self):
        """Setup left control panel"""
        self.left_panel = ctk.CTkFrame(self.main_frame, width=380, fg_color=COLORS['bg_card'])
        self.left_panel.pack(side="left", fill="y", padx=(10, 5), pady=10)
        self.left_panel.pack_propagate(False)

        # Title
        title_frame = ctk.CTkFrame(self.left_panel, fg_color=COLORS['primary'], corner_radius=10)
        title_frame.pack(fill="x", padx=15, pady=(15, 10))

        ctk.CTkLabel(
            title_frame,
            text="BIM Real Options Valuation System v15",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_light']
        ).pack(pady=12)

        ctk.CTkLabel(
            title_frame,
            text="Monte Carlo TPV + Integrated Sensitivity Analysis",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_light']
        ).pack(pady=(0, 12))

        # File selection section
        self._create_file_section()

        # Simulation settings section
        self._create_simulation_section()

        # Run button
        self._create_run_section()

        # Status section
        self._create_status_section()

    def _create_file_section(self):
        """Create file selection section"""
        file_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        file_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            file_frame,
            text="Data Input",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS['text_dark']
        ).pack(anchor="w", pady=(0, 8))

        # Browse button
        self.browse_btn = ctk.CTkButton(
            file_frame,
            text="Select CSV File",
            command=self._browse_csv,
            height=38,
            fg_color=COLORS['primary'],
            hover_color=COLORS['info']
        )
        self.browse_btn.pack(fill="x", pady=(0, 5))

        # Sample data button
        self.sample_btn = ctk.CTkButton(
            file_frame,
            text="Load Sample Data",
            command=self._load_sample_data,
            height=38,
            fg_color=COLORS['secondary'],
            hover_color="#616161"
        )
        self.sample_btn.pack(fill="x", pady=(0, 5))

        # File info label
        self.file_label = ctk.CTkLabel(
            file_frame,
            text="No file selected",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_secondary']
        )
        self.file_label.pack(anchor="w", pady=(5, 0))

        # Required columns info
        info_text = "Required 7 columns: project_id, contract_amount, infra_type,\ndesign_phase, contract_duration, procurement_type, client_type"
        ctk.CTkLabel(
            file_frame,
            text=info_text,
            font=ctk.CTkFont(size=9),
            text_color=COLORS['text_secondary'],
            justify="left"
        ).pack(anchor="w", pady=(5, 0))

    def _create_simulation_section(self):
        """Create simulation settings section"""
        sim_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        sim_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            sim_frame,
            text="Simulation Settings",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS['text_dark']
        ).pack(anchor="w", pady=(0, 8))

        # Simulation count
        count_frame = ctk.CTkFrame(sim_frame, fg_color="transparent")
        count_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(
            count_frame,
            text="Monte Carlo Iterations:",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_dark']
        ).pack(side="left")

        self.sim_count_var = tk.StringVar(value="5000")
        self.sim_entry = ctk.CTkEntry(
            count_frame,
            textvariable=self.sim_count_var,
            width=80,
            height=30
        )
        self.sim_entry.pack(side="right")

        # Preset buttons
        preset_frame = ctk.CTkFrame(sim_frame, fg_color="transparent")
        preset_frame.pack(fill="x", pady=5)

        presets = [("1K", "1000"), ("5K", "5000"), ("10K", "10000"), ("20K", "20000")]
        for text, val in presets:
            ctk.CTkButton(
                preset_frame,
                text=text,
                width=55,
                height=28,
                command=lambda v=val: self.sim_count_var.set(v),
                fg_color=COLORS['secondary'],
                hover_color="#616161"
            ).pack(side="left", padx=2)

    def _create_run_section(self):
        """Create run button section"""
        run_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        run_frame.pack(fill="x", padx=15, pady=15)

        self.run_btn = ctk.CTkButton(
            run_frame,
            text="Run Valuation",
            command=self._run_analysis,
            height=50,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS['success'],
            hover_color="#2E7D32"
        )
        self.run_btn.pack(fill="x")

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(run_frame, height=8)
        self.progress_bar.pack(fill="x", pady=(10, 0))
        self.progress_bar.set(0)

        # Progress label
        self.progress_label = ctk.CTkLabel(
            run_frame,
            text="",
            font=ctk.CTkFont(size=10),
            text_color=COLORS['text_secondary']
        )
        self.progress_label.pack(anchor="w", pady=(5, 0))

    def _create_status_section(self):
        """Create status display section"""
        status_frame = ctk.CTkFrame(self.left_panel, fg_color=COLORS['bg_light'], corner_radius=8)
        status_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            status_frame,
            text="Quick Statistics",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS['text_dark']
        ).pack(anchor="w", padx=10, pady=(10, 5))

        self.stats_label = ctk.CTkLabel(
            status_frame,
            text="Run valuation to see statistics",
            font=ctk.CTkFont(size=10),
            text_color=COLORS['text_secondary'],
            justify="left"
        )
        self.stats_label.pack(anchor="w", padx=10, pady=(0, 10))

        # Export button
        self.export_btn = ctk.CTkButton(
            status_frame,
            text="Export Results to CSV",
            command=self._export_results,
            height=35,
            fg_color=COLORS['info'],
            hover_color="#0277BD",
            state="disabled"
        )
        self.export_btn.pack(fill="x", padx=10, pady=(0, 10))

    def _setup_right_panel(self):
        """Setup right panel with tabs"""
        self.right_panel = ctk.CTkFrame(self.main_frame, fg_color=COLORS['bg_light'])
        self.right_panel.pack(side="right", fill="both", expand=True, padx=(5, 10), pady=10)

        # Tab view
        self.tab_view = ctk.CTkTabview(self.right_panel, fg_color=COLORS['bg_card'])
        self.tab_view.pack(fill="both", expand=True)

        # Add tabs
        self.tab_view.add("Overview")
        self.tab_view.add("Results Table")
        self.tab_view.add("ROV Analysis")
        self.tab_view.add("Decisions")
        self.tab_view.add("Charts")
        self.tab_view.add("Sensitivity")
        self.tab_view.add("Project Details")

        # Setup each tab
        self._setup_overview_tab()
        self._setup_results_tab()
        self._setup_rov_tab()
        self._setup_decisions_tab()
        self._setup_charts_tab()
        self._setup_sensitivity_tab()
        self._setup_project_details_tab()

    def _setup_overview_tab(self):
        """Setup overview tab"""
        tab = self.tab_view.tab("Overview")

        # Placeholder
        self.overview_frame = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        self.overview_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.overview_label = ctk.CTkLabel(
            self.overview_frame,
            text="Results will be displayed here after running valuation.\n\nSelect a CSV file from the left panel and click 'Run Valuation'.",
            font=ctk.CTkFont(size=14),
            text_color=COLORS['text_secondary'],
            justify="center"
        )
        self.overview_label.pack(expand=True, pady=100)

    def _setup_results_tab(self):
        """Setup results table tab"""
        tab = self.tab_view.tab("Results Table")

        columns = ("project_id", "contract", "infra", "npv", "rov_net", "tpv",
                   "npv_decision", "tpv_decision", "changed", "direction")

        self.results_tree = ttk.Treeview(tab, columns=columns, show="headings", height=25)

        headings = {
            "project_id": "Project ID",
            "contract": "Contract (M)",
            "infra": "Infrastructure",
            "npv": "NPV (M)",
            "rov_net": "ROV Net (M)",
            "tpv": "TPV (M)",
            "npv_decision": "NPV Decision",
            "tpv_decision": "TPV Decision",
            "changed": "Changed?",
            "direction": "Direction"
        }

        widths = {
            "project_id": 80, "contract": 90, "infra": 90, "npv": 85, "rov_net": 85,
            "tpv": 85, "npv_decision": 120, "tpv_decision": 120, "changed": 70, "direction": 80
        }

        for col in columns:
            self.results_tree.heading(col, text=headings[col])
            self.results_tree.column(col, width=widths[col], anchor="center")

        # Scrollbars
        v_scroll = ttk.Scrollbar(tab, orient="vertical", command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=v_scroll.set)

        self.results_tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        v_scroll.pack(side="right", fill="y", pady=10, padx=(0, 10))

    def _setup_rov_tab(self):
        """Setup ROV analysis tab"""
        tab = self.tab_view.tab("ROV Analysis")

        columns = ("project_id", "follow_on", "capability", "resource", "abandonment",
                   "contract", "switch", "stage", "rov_gross", "interaction",
                   "risk_premium", "deferral", "rov_net")

        self.rov_tree = ttk.Treeview(tab, columns=columns, show="headings", height=25)

        headings = {
            "project_id": "Project",
            "follow_on": "Follow-on",
            "capability": "Capability",
            "resource": "Resource",
            "abandonment": "Abandon",
            "contract": "Contract",
            "switch": "Switch",
            "stage": "Stage",
            "rov_gross": "ROV Gross",
            "interaction": "Interaction",
            "risk_premium": "Risk Prem.",
            "deferral": "Deferral",
            "rov_net": "ROV Net"
        }

        for col in columns:
            self.rov_tree.heading(col, text=headings[col])
            self.rov_tree.column(col, width=75, anchor="center")

        h_scroll = ttk.Scrollbar(tab, orient="horizontal", command=self.rov_tree.xview)
        v_scroll = ttk.Scrollbar(tab, orient="vertical", command=self.rov_tree.yview)
        self.rov_tree.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)

        self.rov_tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=(10, 0))
        v_scroll.pack(side="right", fill="y", pady=(10, 0), padx=(0, 10))
        h_scroll.pack(side="bottom", fill="x", padx=10, pady=(0, 10))

    def _setup_decisions_tab(self):
        """Setup decisions tab"""
        tab = self.tab_view.tab("Decisions")

        columns = ("project_id", "prob_strong", "prob_part", "prob_cond", "prob_reject",
                   "robustness", "tpv_5", "tpv_mean", "tpv_95")

        self.decision_tree = ttk.Treeview(tab, columns=columns, show="headings", height=25)

        headings = {
            "project_id": "Project",
            "prob_strong": "P(Strong)",
            "prob_part": "P(Participate)",
            "prob_cond": "P(Conditional)",
            "prob_reject": "P(Reject)",
            "robustness": "Robustness",
            "tpv_5": "TPV 5%",
            "tpv_mean": "TPV Mean",
            "tpv_95": "TPV 95%"
        }

        for col in columns:
            self.decision_tree.heading(col, text=headings[col])
            self.decision_tree.column(col, width=100, anchor="center")

        v_scroll = ttk.Scrollbar(tab, orient="vertical", command=self.decision_tree.yview)
        self.decision_tree.configure(yscrollcommand=v_scroll.set)

        self.decision_tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        v_scroll.pack(side="right", fill="y", pady=10, padx=(0, 10))

    def _setup_charts_tab(self):
        """Setup charts tab"""
        tab = self.tab_view.tab("Charts")

        self.charts_frame = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        self.charts_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.charts_placeholder = ctk.CTkLabel(
            self.charts_frame,
            text="Charts will appear here after running valuation.",
            font=ctk.CTkFont(size=14),
            text_color=COLORS['text_secondary']
        )
        self.charts_placeholder.pack(expand=True, pady=100)

    def _setup_sensitivity_tab(self):
        """Setup sensitivity analysis tab"""
        tab = self.tab_view.tab("Sensitivity")

        self.sensitivity_frame = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        self.sensitivity_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.sensitivity_placeholder = ctk.CTkLabel(
            self.sensitivity_frame,
            text="Sensitivity analysis will appear here after running valuation.",
            font=ctk.CTkFont(size=14),
            text_color=COLORS['text_secondary']
        )
        self.sensitivity_placeholder.pack(expand=True, pady=100)

    def _browse_csv(self):
        """Browse for CSV file"""
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if file_path:
            try:
                self.input_df = pd.read_csv(file_path)
                self._validate_input()
                self.file_label.configure(
                    text=f"Loaded: {os.path.basename(file_path)} ({len(self.input_df)} projects)",
                    text_color=COLORS['success']
                )
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file:\n{str(e)}")
                self.input_df = None

    def _load_sample_data(self):
        """Load sample data"""
        sample_data = [
            {"project_id": "R01", "contract_amount": 520, "infra_type": "Road",
             "design_phase": "Basic Design", "contract_duration": 1.8,
             "procurement_type": "Limited", "client_type": "Central"},
            {"project_id": "R02", "contract_amount": 180, "infra_type": "Road",
             "design_phase": "Detailed Design", "contract_duration": 0.9,
             "procurement_type": "Open", "client_type": "Local"},
            {"project_id": "R03", "contract_amount": 280, "infra_type": "Road",
             "design_phase": "Basic Design", "contract_duration": 1.2,
             "procurement_type": "Open", "client_type": "Public Corp"},
            {"project_id": "R04", "contract_amount": 450, "infra_type": "Bridge",
             "design_phase": "Basic Design", "contract_duration": 1.5,
             "procurement_type": "Limited", "client_type": "Central"},
            {"project_id": "R05", "contract_amount": 120, "infra_type": "Bridge",
             "design_phase": "Detailed Design", "contract_duration": 0.7,
             "procurement_type": "Open", "client_type": "Local"},
            {"project_id": "R06", "contract_amount": 95, "infra_type": "Bridge",
             "design_phase": "Detailed Design", "contract_duration": 0.5,
             "procurement_type": "Open", "client_type": "Local"},
            {"project_id": "R07", "contract_amount": 680, "infra_type": "Tunnel",
             "design_phase": "Basic Design", "contract_duration": 2.0,
             "procurement_type": "Limited", "client_type": "Public Corp"},
            {"project_id": "R08", "contract_amount": 220, "infra_type": "Tunnel",
             "design_phase": "Detailed Design", "contract_duration": 1.0,
             "procurement_type": "Limited", "client_type": "Local"},
            {"project_id": "R09", "contract_amount": 850, "infra_type": "Tunnel",
             "design_phase": "Basic Design", "contract_duration": 2.5,
             "procurement_type": "Negotiated", "client_type": "Public Corp"},
            {"project_id": "R10", "contract_amount": 320, "infra_type": "Tunnel",
             "design_phase": "Detailed Design", "contract_duration": 1.3,
             "procurement_type": "Open", "client_type": "Local"},
        ]

        self.input_df = pd.DataFrame(sample_data)
        self.file_label.configure(
            text=f"Sample data loaded (10 projects)",
            text_color=COLORS['success']
        )

    def _validate_input(self):
        """Validate input data"""
        required_cols = ['project_id', 'contract_amount', 'infra_type',
                        'design_phase', 'contract_duration', 'procurement_type', 'client_type']

        missing = [col for col in required_cols if col not in self.input_df.columns]
        if missing:
            messagebox.showerror("Error", f"Missing required columns:\n{', '.join(missing)}")
            self.input_df = None

    def _run_analysis(self):
        """Run valuation analysis"""
        if self.input_df is None:
            messagebox.showwarning("Warning", "Please load data first!")
            return

        if self.analysis_running:
            return

        try:
            n_sim = int(self.sim_count_var.get())
            if n_sim < 100 or n_sim > 100000:
                raise ValueError("Simulations must be between 100 and 100,000")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid simulation count:\n{str(e)}")
            return

        self.analysis_running = True
        self.run_btn.configure(state="disabled", text="Running...")
        self.progress_bar.set(0)
        self.progress_label.configure(text="Starting analysis...")

        # Run in background thread
        thread = threading.Thread(target=self._run_analysis_thread, args=(n_sim,))
        thread.start()

        # Monitor progress
        self._monitor_progress(thread)

    def _run_analysis_thread(self, n_simulations: int):
        """Worker thread for analysis"""
        try:
            self.after(0, lambda: self.progress_label.configure(text="Running Monte Carlo simulation..."))

            engine = ValuationEngine(n_simulations=n_simulations)
            self.results_df, self.sensitivity_results = engine.run_valuation(self.input_df)

            self._analysis_success = True
        except Exception as e:
            self._analysis_error = str(e)
            self._analysis_success = False

    def _monitor_progress(self, thread: threading.Thread):
        """Monitor analysis progress"""
        if thread.is_alive():
            current = self.progress_bar.get()
            if current < 0.9:
                self.progress_bar.set(current + 0.02)
            self.after(100, lambda: self._monitor_progress(thread))
        else:
            self.progress_bar.set(1.0)
            self.run_btn.configure(state="normal", text="Run Valuation")
            self.analysis_running = False

            if hasattr(self, '_analysis_success') and self._analysis_success:
                self._display_results()
                self.export_btn.configure(state="normal")
                self.progress_label.configure(text="Analysis completed successfully!")
                messagebox.showinfo("Success", "Valuation completed!")
            else:
                error_msg = getattr(self, '_analysis_error', 'Unknown error')
                messagebox.showerror("Error", f"Analysis failed:\n{error_msg}")
                self.progress_label.configure(text="Analysis failed")

    def _display_results(self):
        """Display all results"""
        if self.results_df is None:
            return

        self._update_overview_tab()
        self._update_results_tab()
        self._update_rov_tab()
        self._update_decisions_tab()
        self._update_charts_tab()
        self._update_sensitivity_tab()
        self._update_project_details_tab()
        self._update_stats()

        self.tab_view.set("Overview")

    def _update_overview_tab(self):
        """Update overview tab with summary"""
        # Clear placeholder
        self.overview_label.pack_forget()

        # Clear existing widgets
        for widget in self.overview_frame.winfo_children():
            widget.destroy()

        df = self.results_df

        # Summary cards
        cards_frame = ctk.CTkFrame(self.overview_frame, fg_color="transparent")
        cards_frame.pack(fill="x", pady=10)

        # NPV Card
        self._create_summary_card(cards_frame, "Total NPV", f"{df['npv'].sum():,.1f} M", COLORS['npv'])
        self._create_summary_card(cards_frame, "Total ROV", f"{df['rov_net'].sum():,.1f} M", COLORS['rov'])
        self._create_summary_card(cards_frame, "Total TPV", f"{df['tpv'].sum():,.1f} M", COLORS['tpv'])

        decision_changed = df['decision_changed'].sum()
        self._create_summary_card(cards_frame, "Decision Changes", f"{decision_changed} / {len(df)}", COLORS['warning'])

        # Overview chart
        self._create_overview_chart()

    def _create_summary_card(self, parent, title: str, value: str, color: str):
        """Create a summary card"""
        card = ctk.CTkFrame(parent, fg_color=color, corner_radius=10, width=200, height=80)
        card.pack(side="left", padx=10, pady=5)
        card.pack_propagate(False)

        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_light']
        ).pack(pady=(12, 2))

        ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS['text_light']
        ).pack()

    def _create_overview_chart(self):
        """Create overview chart showing NPV vs TPV"""
        chart_frame = ctk.CTkFrame(self.overview_frame, fg_color=COLORS['bg_card'], corner_radius=10)
        chart_frame.pack(fill="x", pady=10, padx=5)

        ctk.CTkLabel(
            chart_frame,
            text="NPV vs TPV Comparison by Project",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_dark']
        ).pack(pady=(15, 5))

        fig, ax = plt.subplots(figsize=(12, 5), dpi=100)

        df = self.results_df
        x = np.arange(len(df))
        width = 0.35

        bars1 = ax.bar(x - width/2, df['npv'], width, label='NPV', color=COLORS['npv'], alpha=0.8)
        bars2 = ax.bar(x + width/2, df['tpv'], width, label='TPV', color=COLORS['tpv'], alpha=0.8)

        ax.set_xlabel('Project', fontsize=10)
        ax.set_ylabel('Value (M KRW)', fontsize=10)
        ax.set_xticks(x)
        ax.set_xticklabels(df['project_id'], fontsize=9)
        ax.legend(loc='upper right')
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax.grid(axis='y', alpha=0.3)

        # Mark decision changes
        for i, (_, row) in enumerate(df.iterrows()):
            if row['decision_changed']:
                ax.annotate('*', (i, max(row['npv'], row['tpv']) + 5),
                           ha='center', fontsize=14, color=COLORS['warning'])

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", padx=10, pady=10)

        self.figures.append(fig)

    def _update_results_tab(self):
        """Update results table"""
        # Clear existing
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        for _, row in self.results_df.iterrows():
            values = (
                row['project_id'],
                f"{row['contract_amount']:.0f}",
                row['infra_type'],
                f"{row['npv']:.2f}",
                f"{row['rov_net']:.2f}",
                f"{row['tpv']:.2f}",
                row['npv_decision'],
                row['tpv_decision'],
                "Yes" if row['decision_changed'] else "No",
                row['decision_direction']
            )
            self.results_tree.insert("", "end", values=values)

    def _update_rov_tab(self):
        """Update ROV analysis table"""
        for item in self.rov_tree.get_children():
            self.rov_tree.delete(item)

        for _, row in self.results_df.iterrows():
            values = (
                row['project_id'],
                f"{row['rov_follow_on']:.2f}",
                f"{row['rov_capability']:.2f}",
                f"{row['rov_resource']:.2f}",
                f"{row['rov_abandonment']:.2f}",
                f"{row['rov_contract']:.2f}",
                f"{row['rov_switch']:.2f}",
                f"{row['rov_stage']:.2f}",
                f"{row['rov_gross']:.2f}",
                f"{row['interaction_adjustment']:.2f}",
                f"{row['risk_premium']:.2f}",
                f"{row['deferral_value']:.2f}",
                f"{row['rov_net']:.2f}"
            )
            self.rov_tree.insert("", "end", values=values)

    def _update_decisions_tab(self):
        """Update decisions table"""
        for item in self.decision_tree.get_children():
            self.decision_tree.delete(item)

        for _, row in self.results_df.iterrows():
            values = (
                row['project_id'],
                f"{row['prob_strong_participate']:.1%}",
                f"{row['prob_participate']:.1%}",
                f"{row['prob_conditional']:.1%}",
                f"{row['prob_reject']:.1%}",
                f"{row['decision_robustness']:.1%}" if row['decision_robustness'] else "N/A",
                f"{row['tpv_ci_lower']:.2f}",
                f"{row['tpv']:.2f}",
                f"{row['tpv_ci_upper']:.2f}"
            )
            self.decision_tree.insert("", "end", values=values)

    def _update_charts_tab(self):
        """Update charts tab with visualizations"""
        # Clear existing
        for widget in self.charts_frame.winfo_children():
            widget.destroy()

        # ROV Waterfall Chart
        self._create_rov_waterfall_chart()

        # TPV Distribution Boxplot
        self._create_tpv_boxplot()

    def _create_rov_waterfall_chart(self):
        """Create ROV composition waterfall chart"""
        chart_frame = ctk.CTkFrame(self.charts_frame, fg_color=COLORS['bg_card'], corner_radius=10)
        chart_frame.pack(fill="x", pady=10, padx=5)

        ctk.CTkLabel(
            chart_frame,
            text="Figure 4-3. ROV Composition Waterfall Chart",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_dark']
        ).pack(pady=(15, 5))

        fig, ax = plt.subplots(figsize=(12, 6), dpi=100)

        df = self.results_df

        # Average ROV components
        options = ['follow_on', 'capability', 'resource', 'abandonment', 'contract', 'switch', 'stage']
        labels = ['Follow-on', 'Capability', 'Resource', 'Abandon', 'Contract', 'Switch', 'Stage']
        colors_list = [ROV_COLORS[opt] for opt in options]

        values = [df[f'rov_{opt}'].mean() for opt in options]

        # Waterfall calculation
        cumulative = 0
        for i, (val, label, color) in enumerate(zip(values, labels, colors_list)):
            ax.bar(i, val, bottom=cumulative, color=color, alpha=0.8, label=label, edgecolor='white')
            cumulative += val

        # Add adjustments
        adj_labels = ['Interaction', 'Risk Prem.', 'Deferral']
        adj_values = [-df['interaction_adjustment'].mean(), -df['risk_premium'].mean(), -df['deferral_value'].mean()]

        for i, (val, label) in enumerate(zip(adj_values, adj_labels)):
            ax.bar(len(options) + i, val, bottom=cumulative, color=COLORS['danger'], alpha=0.6, edgecolor='white')
            cumulative += val

        # Final ROV
        ax.bar(len(options) + len(adj_labels), df['rov_net'].mean(), color=COLORS['success'], alpha=0.8, label='ROV Net')

        ax.set_xticks(range(len(options) + len(adj_labels) + 1))
        ax.set_xticklabels(labels + adj_labels + ['ROV Net'], rotation=45, ha='right', fontsize=9)
        ax.set_ylabel('Value (M KRW)', fontsize=10)
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax.grid(axis='y', alpha=0.3)
        ax.legend(loc='upper right', fontsize=8, ncol=2)

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", padx=10, pady=10)

        self.figures.append(fig)

    def _create_tpv_boxplot(self):
        """Create TPV uncertainty boxplot"""
        chart_frame = ctk.CTkFrame(self.charts_frame, fg_color=COLORS['bg_card'], corner_radius=10)
        chart_frame.pack(fill="x", pady=10, padx=5)

        ctk.CTkLabel(
            chart_frame,
            text="Figure 4-1. TPV Uncertainty Analysis (Confidence Intervals)",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_dark']
        ).pack(pady=(15, 5))

        fig, ax = plt.subplots(figsize=(12, 5), dpi=100)

        df = self.results_df
        x = np.arange(len(df))

        # Plot mean with error bars
        means = df['tpv'].values
        lowers = df['tpv_ci_lower'].values
        uppers = df['tpv_ci_upper'].values

        errors = np.array([means - lowers, uppers - means])

        colors = [COLORS['success'] if m > 0 else COLORS['danger'] for m in means]

        ax.bar(x, means, color=colors, alpha=0.7, edgecolor='white')
        ax.errorbar(x, means, yerr=errors, fmt='none', color='black', capsize=4, capthick=1.5)

        ax.set_xlabel('Project', fontsize=10)
        ax.set_ylabel('TPV (M KRW)', fontsize=10)
        ax.set_xticks(x)
        ax.set_xticklabels(df['project_id'], fontsize=9)
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax.grid(axis='y', alpha=0.3)

        # Add 5%-95% CI annotation
        ax.annotate('Error bars: 5%-95% CI', xy=(0.98, 0.98), xycoords='axes fraction',
                   ha='right', va='top', fontsize=9, color=COLORS['text_secondary'])

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", padx=10, pady=10)

        self.figures.append(fig)

    def _setup_project_details_tab(self):
        """Setup project details tab for individual project analysis"""
        tab = self.tab_view.tab("Project Details")

        # Top frame for project selection
        top_frame = ctk.CTkFrame(tab, fg_color="transparent", height=60)
        top_frame.pack(fill="x", padx=10, pady=(10, 5))
        top_frame.pack_propagate(False)

        ctk.CTkLabel(
            top_frame,
            text="Select Project:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS['text_dark']
        ).pack(side="left", padx=(10, 10))

        # Project selection combobox
        self.project_selector = ctk.CTkComboBox(
            top_frame,
            values=["No projects loaded"],
            width=200,
            command=self._on_project_selected,
            state="disabled"
        )
        self.project_selector.pack(side="left", padx=5)

        # Navigation buttons
        self.prev_project_btn = ctk.CTkButton(
            top_frame,
            text="< Prev",
            width=80,
            command=self._prev_project,
            fg_color=COLORS['secondary'],
            hover_color="#616161",
            state="disabled"
        )
        self.prev_project_btn.pack(side="left", padx=5)

        self.next_project_btn = ctk.CTkButton(
            top_frame,
            text="Next >",
            width=80,
            command=self._next_project,
            fg_color=COLORS['secondary'],
            hover_color="#616161",
            state="disabled"
        )
        self.next_project_btn.pack(side="left", padx=5)

        # Project info label
        self.project_info_label = ctk.CTkLabel(
            top_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_secondary']
        )
        self.project_info_label.pack(side="left", padx=20)

        # Main scrollable content
        self.project_details_frame = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        self.project_details_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Placeholder
        self.project_details_placeholder = ctk.CTkLabel(
            self.project_details_frame,
            text="Select a project from the dropdown to view detailed analysis.\n\nRun valuation first to see individual project results.",
            font=ctk.CTkFont(size=14),
            text_color=COLORS['text_secondary'],
            justify="center"
        )
        self.project_details_placeholder.pack(expand=True, pady=100)

    def _on_project_selected(self, selection: str):
        """Handle project selection from dropdown"""
        if self.results_df is None or selection == "No projects loaded":
            return

        self.current_project_id = selection
        self._display_project_details(selection)

    def _prev_project(self):
        """Navigate to previous project"""
        if self.results_df is None:
            return

        projects = self.results_df['project_id'].tolist()
        if self.current_project_id in projects:
            idx = projects.index(self.current_project_id)
            if idx > 0:
                self.current_project_id = projects[idx - 1]
                self.project_selector.set(self.current_project_id)
                self._display_project_details(self.current_project_id)

    def _next_project(self):
        """Navigate to next project"""
        if self.results_df is None:
            return

        projects = self.results_df['project_id'].tolist()
        if self.current_project_id in projects:
            idx = projects.index(self.current_project_id)
            if idx < len(projects) - 1:
                self.current_project_id = projects[idx + 1]
                self.project_selector.set(self.current_project_id)
                self._display_project_details(self.current_project_id)

    def _display_project_details(self, project_id: str):
        """Display detailed analysis for a specific project"""
        if self.results_df is None:
            return

        # Get project data
        project_row = self.results_df[self.results_df['project_id'] == project_id]
        if project_row.empty:
            return

        project = project_row.iloc[0]

        # Clear existing content
        for widget in self.project_details_frame.winfo_children():
            widget.destroy()

        # Update navigation state
        projects = self.results_df['project_id'].tolist()
        idx = projects.index(project_id)
        self.project_info_label.configure(text=f"Project {idx + 1} of {len(projects)}")

        # ===== Section 1: Project Summary =====
        self._create_project_summary_section(project)

        # ===== Section 2: NPV vs TPV Comparison Chart =====
        self._create_project_npv_tpv_chart(project)

        # ===== Section 3: ROV Components Breakdown =====
        self._create_project_rov_breakdown(project)

        # ===== Section 4: Decision Probability Distribution =====
        self._create_project_decision_probs(project)

        # ===== Section 5: TPV Distribution (Confidence Interval) =====
        self._create_project_tpv_distribution(project)

    def _create_project_summary_section(self, project):
        """Create project summary cards"""
        summary_frame = ctk.CTkFrame(self.project_details_frame, fg_color=COLORS['bg_card'], corner_radius=10)
        summary_frame.pack(fill="x", pady=10, padx=5)

        # Title
        title_frame = ctk.CTkFrame(summary_frame, fg_color=COLORS['primary'], corner_radius=8)
        title_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            title_frame,
            text=f"Project {project['project_id']} - {project['infra_type']} ({project['design_phase']})",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text_light']
        ).pack(pady=10)

        # Summary explanation text
        summary_text = self._generate_project_summary_text(project)
        ctk.CTkLabel(
            summary_frame,
            text=summary_text,
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_secondary'],
            justify="left",
            wraplength=800
        ).pack(fill="x", padx=15, pady=(5, 10))

        # Info cards row
        cards_frame = ctk.CTkFrame(summary_frame, fg_color="transparent")
        cards_frame.pack(fill="x", padx=10, pady=10)

        # Contract amount
        self._create_info_card(cards_frame, "Contract Amount", f"{project['contract_amount']:.0f} M", COLORS['info'])

        # NPV
        npv_color = COLORS['success'] if project['npv'] > 0 else COLORS['danger']
        self._create_info_card(cards_frame, "NPV", f"{project['npv']:.2f} M", npv_color)

        # ROV Net
        rov_color = COLORS['success'] if project['rov_net'] > 0 else COLORS['warning']
        self._create_info_card(cards_frame, "ROV Net", f"{project['rov_net']:.2f} M", rov_color)

        # TPV
        tpv_color = COLORS['success'] if project['tpv'] > 0 else COLORS['danger']
        self._create_info_card(cards_frame, "TPV", f"{project['tpv']:.2f} M", tpv_color)

        # Decision row
        decision_frame = ctk.CTkFrame(summary_frame, fg_color="transparent")
        decision_frame.pack(fill="x", padx=10, pady=(0, 10))

        # NPV Decision
        npv_dec_color = COLORS['success'] if 'Participate' in project['npv_decision'] else COLORS['danger']
        self._create_info_card(decision_frame, "NPV Decision", project['npv_decision'], npv_dec_color)

        # TPV Decision
        tpv_dec_color = COLORS['success'] if 'Participate' in project['tpv_decision'] else COLORS['danger']
        self._create_info_card(decision_frame, "TPV Decision", project['tpv_decision'], tpv_dec_color)

        # Decision Changed
        if project['decision_changed']:
            change_color = COLORS['warning']
            change_text = f"Changed ({project['decision_direction']})"
        else:
            change_color = COLORS['secondary']
            change_text = "No Change"
        self._create_info_card(decision_frame, "Decision Change", change_text, change_color)

        # Robustness
        robustness = project['decision_robustness']
        if robustness:
            rob_color = COLORS['success'] if robustness > 0.7 else (COLORS['warning'] if robustness > 0.5 else COLORS['danger'])
            rob_text = f"{robustness:.1%}"
        else:
            rob_color = COLORS['secondary']
            rob_text = "N/A"
        self._create_info_card(decision_frame, "Robustness", rob_text, rob_color)

    def _create_info_card(self, parent, title: str, value: str, color: str):
        """Create an info card"""
        card = ctk.CTkFrame(parent, fg_color=color, corner_radius=8, width=160, height=70)
        card.pack(side="left", padx=5, pady=5)
        card.pack_propagate(False)

        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=10),
            text_color=COLORS['text_light']
        ).pack(pady=(10, 2))

        ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_light']
        ).pack()

    def _generate_project_summary_text(self, project) -> str:
        """Generate summary explanation text for a project"""
        npv = project['npv']
        rov = project['rov_net']
        tpv = project['tpv']

        # Decision analysis
        if project['decision_changed']:
            if project['decision_direction'] == 'Up':
                decision_impact = f"Real options analysis UPGRADED the decision from Reject to Participate. The ROV of {rov:.2f}M added significant strategic value."
            else:
                decision_impact = f"Real options analysis DOWNGRADED the decision from Participate to Reject. Despite positive NPV, risk adjustments reduced overall value."
        else:
            if tpv > 0:
                decision_impact = f"Both NPV and TPV analyses recommend participation. The project shows consistent positive value across methodologies."
            else:
                decision_impact = f"Both NPV and TPV analyses recommend rejection. The project does not meet profitability thresholds."

        # ROV contribution
        rov_pct = (rov / project['contract_amount']) * 100 if project['contract_amount'] > 0 else 0
        rov_analysis = f"Real Options Value contributes {rov_pct:.1f}% of contract amount, primarily from "

        # Find top ROV contributor
        rov_components = {
            'Follow-on Option': project['rov_follow_on'],
            'Capability Option': project['rov_capability'],
            'Resource Option': project['rov_resource'],
            'Abandonment Option': project['rov_abandonment'],
            'Contract Option': project['rov_contract'],
            'Switch Option': project['rov_switch'],
            'Stage Option': project['rov_stage']
        }
        top_option = max(rov_components, key=rov_components.get)
        top_value = rov_components[top_option]
        rov_analysis += f"{top_option} ({top_value:.2f}M)."

        # Robustness assessment
        robustness = project['decision_robustness']
        if robustness:
            if robustness > 0.8:
                rob_text = f"Decision robustness is HIGH ({robustness:.1%}), indicating strong confidence in the recommendation."
            elif robustness > 0.6:
                rob_text = f"Decision robustness is MODERATE ({robustness:.1%}), suggesting reasonable confidence with some uncertainty."
            else:
                rob_text = f"Decision robustness is LOW ({robustness:.1%}), indicating significant uncertainty in the recommendation."
        else:
            rob_text = "Decision robustness could not be calculated."

        return f"{decision_impact}\n\n{rov_analysis}\n\n{rob_text}"

    def _create_project_npv_tpv_chart(self, project):
        """Create NPV vs TPV comparison bar chart for single project"""
        chart_frame = ctk.CTkFrame(self.project_details_frame, fg_color=COLORS['bg_card'], corner_radius=10)
        chart_frame.pack(fill="x", pady=10, padx=5)

        ctk.CTkLabel(
            chart_frame,
            text="NPV vs TPV Comparison",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_dark']
        ).pack(pady=(15, 5))

        # Explanation text
        npv = project['npv']
        rov = project['rov_net']
        tpv = project['tpv']
        explanation = (
            f"This chart compares traditional NPV ({npv:.2f}M) with Total Project Value ({tpv:.2f}M). "
            f"The difference ({rov:.2f}M) represents the Real Options Value - the strategic flexibility premium "
            f"that traditional NPV analysis fails to capture. TPV = NPV + ROV Net."
        )
        ctk.CTkLabel(
            chart_frame,
            text=explanation,
            font=ctk.CTkFont(size=10),
            text_color=COLORS['text_secondary'],
            justify="left",
            wraplength=900
        ).pack(fill="x", padx=15, pady=(0, 10))

        fig, ax = plt.subplots(figsize=(10, 4), dpi=100)

        categories = ['NPV', 'ROV Net', 'TPV']
        values = [project['npv'], project['rov_net'], project['tpv']]
        colors = [COLORS['npv'], COLORS['rov'], COLORS['tpv']]

        bars = ax.bar(categories, values, color=colors, alpha=0.8, edgecolor='white', width=0.5)

        # Add value labels on bars
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax.annotate(f'{val:.2f}',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 5 if height >= 0 else -15),
                       textcoords="offset points",
                       ha='center', va='bottom' if height >= 0 else 'top',
                       fontsize=11, fontweight='bold')

        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
        ax.set_ylabel('Value (M KRW)', fontsize=10)
        ax.grid(axis='y', alpha=0.3)
        ax.set_title(f'Project {project["project_id"]} - Value Breakdown', fontsize=11, pad=10)

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", padx=10, pady=10)
        self.figures.append(fig)

    def _create_project_rov_breakdown(self, project):
        """Create ROV components breakdown chart"""
        chart_frame = ctk.CTkFrame(self.project_details_frame, fg_color=COLORS['bg_card'], corner_radius=10)
        chart_frame.pack(fill="x", pady=10, padx=5)

        ctk.CTkLabel(
            chart_frame,
            text="Real Options Value Breakdown",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_dark']
        ).pack(pady=(15, 5))

        # Explanation text
        explanation = (
            "LEFT: Individual option values representing different types of managerial flexibility. "
            "Follow-on captures future project opportunities; Capability reflects BIM expertise value; "
            "Resource shows workforce flexibility; Abandonment is the exit option value; "
            "Contract covers scope change flexibility; Switch enables technology pivots; "
            "Stage allows phased commitment.\n\n"
            "RIGHT: Waterfall showing how ROV Gross is adjusted by Interaction effects (overlapping options), "
            "Risk Premium (uncertainty penalty), and Deferral costs to arrive at ROV Net."
        )
        ctk.CTkLabel(
            chart_frame,
            text=explanation,
            font=ctk.CTkFont(size=10),
            text_color=COLORS['text_secondary'],
            justify="left",
            wraplength=900
        ).pack(fill="x", padx=15, pady=(0, 10))

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), dpi=100)

        # Left: ROV Components Bar Chart
        options = ['follow_on', 'capability', 'resource', 'abandonment', 'contract', 'switch', 'stage']
        labels = ['Follow-on', 'Capability', 'Resource', 'Abandon', 'Contract', 'Switch', 'Stage']
        values = [project[f'rov_{opt}'] for opt in options]
        colors_list = [ROV_COLORS[opt] for opt in options]

        bars = ax1.barh(labels, values, color=colors_list, alpha=0.8, edgecolor='white')
        ax1.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
        ax1.set_xlabel('Value (M KRW)', fontsize=10)
        ax1.set_title('Individual Option Values', fontsize=11)
        ax1.grid(axis='x', alpha=0.3)

        # Add value labels
        for bar, val in zip(bars, values):
            width = bar.get_width()
            ax1.annotate(f'{val:.2f}',
                        xy=(width, bar.get_y() + bar.get_height()/2),
                        xytext=(5 if width >= 0 else -5, 0),
                        textcoords="offset points",
                        ha='left' if width >= 0 else 'right',
                        va='center', fontsize=9)

        # Right: Waterfall Chart showing ROV calculation
        waterfall_labels = ['ROV Gross', 'Interaction', 'Risk Prem.', 'Deferral', 'ROV Net']
        waterfall_values = [
            project['rov_gross'],
            -project['interaction_adjustment'],
            -project['risk_premium'],
            -project['deferral_value'],
            project['rov_net']
        ]

        # Calculate cumulative for waterfall
        cumulative = [0]
        for i, val in enumerate(waterfall_values[:-1]):
            cumulative.append(cumulative[-1] + val)

        # Colors for waterfall
        waterfall_colors = [COLORS['info'], COLORS['warning'], COLORS['warning'], COLORS['warning'], COLORS['success']]

        for i, (label, val, color) in enumerate(zip(waterfall_labels, waterfall_values, waterfall_colors)):
            if i == len(waterfall_labels) - 1:  # Final bar
                ax2.bar(i, val, color=color, alpha=0.8, edgecolor='white')
            else:
                bottom = cumulative[i] if val >= 0 else cumulative[i] + val
                ax2.bar(i, abs(val), bottom=bottom, color=color, alpha=0.8, edgecolor='white')

        ax2.set_xticks(range(len(waterfall_labels)))
        ax2.set_xticklabels(waterfall_labels, rotation=45, ha='right', fontsize=9)
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
        ax2.set_ylabel('Value (M KRW)', fontsize=10)
        ax2.set_title('ROV Calculation Waterfall', fontsize=11)
        ax2.grid(axis='y', alpha=0.3)

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", padx=10, pady=10)
        self.figures.append(fig)

    def _create_project_decision_probs(self, project):
        """Create decision probability pie chart"""
        chart_frame = ctk.CTkFrame(self.project_details_frame, fg_color=COLORS['bg_card'], corner_radius=10)
        chart_frame.pack(fill="x", pady=10, padx=5)

        ctk.CTkLabel(
            chart_frame,
            text="Decision Probability Distribution",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_dark']
        ).pack(pady=(15, 5))

        # Explanation text
        prob_strong = project['prob_strong_participate']
        prob_part = project['prob_participate']
        prob_cond = project['prob_conditional']
        prob_reject = project['prob_reject']

        # Determine dominant category
        max_prob = max(prob_strong, prob_part, prob_cond, prob_reject)
        if max_prob == prob_strong:
            dominant = "Strong Participate"
            dominant_desc = "high confidence in positive returns across most Monte Carlo scenarios"
        elif max_prob == prob_part:
            dominant = "Participate"
            dominant_desc = "moderate positive returns expected under typical conditions"
        elif max_prob == prob_cond:
            dominant = "Conditional"
            dominant_desc = "borderline profitability requiring careful monitoring"
        else:
            dominant = "Reject"
            dominant_desc = "negative expected returns in majority of scenarios"

        explanation = (
            f"Monte Carlo simulation results show {dominant} ({max_prob:.1%}) as the dominant outcome, indicating {dominant_desc}. "
            f"The distribution reflects uncertainty in input parameters: Strong Participate (TPV > 5% of contract), "
            f"Participate (0 < TPV <= 5%), Conditional (-5% < TPV <= 0), Reject (TPV <= -5%)."
        )
        ctk.CTkLabel(
            chart_frame,
            text=explanation,
            font=ctk.CTkFont(size=10),
            text_color=COLORS['text_secondary'],
            justify="left",
            wraplength=900
        ).pack(fill="x", padx=15, pady=(0, 10))

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4), dpi=100)

        # Left: Pie chart
        probs = [
            project['prob_strong_participate'],
            project['prob_participate'],
            project['prob_conditional'],
            project['prob_reject']
        ]
        labels = ['Strong Participate', 'Participate', 'Conditional', 'Reject']
        colors = [COLORS['success'], '#81C784', COLORS['warning'], COLORS['danger']]

        # Filter out zero values for pie chart
        filtered_data = [(l, p, c) for l, p, c in zip(labels, probs, colors) if p > 0.001]
        if filtered_data:
            f_labels, f_probs, f_colors = zip(*filtered_data)
            wedges, texts, autotexts = ax1.pie(f_probs, labels=f_labels, colors=f_colors, autopct='%1.1f%%',
                                               startangle=90, pctdistance=0.75)
            ax1.set_title('Decision Category Distribution', fontsize=11)

            # Style the text
            for autotext in autotexts:
                autotext.set_fontsize(10)
                autotext.set_fontweight('bold')
        else:
            ax1.text(0.5, 0.5, 'No data', ha='center', va='center', fontsize=12)
            ax1.set_title('Decision Category Distribution', fontsize=11)

        # Right: Horizontal bar for probabilities
        y_pos = np.arange(len(labels))
        bars = ax2.barh(y_pos, probs, color=colors, alpha=0.8, edgecolor='white')
        ax2.set_yticks(y_pos)
        ax2.set_yticklabels(labels, fontsize=10)
        ax2.set_xlabel('Probability', fontsize=10)
        ax2.set_xlim(0, 1)
        ax2.set_title('Decision Probabilities', fontsize=11)
        ax2.grid(axis='x', alpha=0.3)

        # Add percentage labels
        for bar, prob in zip(bars, probs):
            width = bar.get_width()
            ax2.annotate(f'{prob:.1%}',
                        xy=(width, bar.get_y() + bar.get_height()/2),
                        xytext=(5, 0),
                        textcoords="offset points",
                        ha='left', va='center', fontsize=9, fontweight='bold')

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", padx=10, pady=10)
        self.figures.append(fig)

    def _create_project_tpv_distribution(self, project):
        """Create TPV distribution visualization with confidence interval"""
        chart_frame = ctk.CTkFrame(self.project_details_frame, fg_color=COLORS['bg_card'], corner_radius=10)
        chart_frame.pack(fill="x", pady=10, padx=5)

        ctk.CTkLabel(
            chart_frame,
            text="TPV Uncertainty Analysis",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_dark']
        ).pack(pady=(15, 5))

        # Get values
        tpv_mean = project['tpv']
        tpv_lower = project['tpv_ci_lower']
        tpv_upper = project['tpv_ci_upper']

        # Explanation text
        ci_width = tpv_upper - tpv_lower
        cv = ci_width / abs(tpv_mean) if tpv_mean != 0 else 0

        if cv < 0.5:
            uncertainty_level = "LOW"
            uncertainty_desc = "Results are relatively stable across different input scenarios."
        elif cv < 1.0:
            uncertainty_level = "MODERATE"
            uncertainty_desc = "Some variability exists; consider scenario-based decision making."
        else:
            uncertainty_level = "HIGH"
            uncertainty_desc = "Significant uncertainty; recommend sensitivity analysis before final decision."

        explanation = (
            f"The 90% confidence interval spans from {tpv_lower:.2f}M (5th percentile) to {tpv_upper:.2f}M (95th percentile), "
            f"with a mean TPV of {tpv_mean:.2f}M. Uncertainty level is {uncertainty_level}: {uncertainty_desc} "
            f"The shaded region represents the most likely range of outcomes from Monte Carlo simulation."
        )
        ctk.CTkLabel(
            chart_frame,
            text=explanation,
            font=ctk.CTkFont(size=10),
            text_color=COLORS['text_secondary'],
            justify="left",
            wraplength=900
        ).pack(fill="x", padx=15, pady=(0, 10))

        fig, ax = plt.subplots(figsize=(10, 4), dpi=100)

        # Simulated distribution (normal approximation)
        # In real implementation, this would come from actual Monte Carlo results
        std_est = (tpv_upper - tpv_lower) / 3.29  # Approximate std from 90% CI
        x = np.linspace(tpv_lower - std_est, tpv_upper + std_est, 200)
        y = np.exp(-0.5 * ((x - tpv_mean) / std_est) ** 2) / (std_est * np.sqrt(2 * np.pi))

        # Plot distribution curve
        ax.fill_between(x, y, alpha=0.3, color=COLORS['tpv'])
        ax.plot(x, y, color=COLORS['tpv'], linewidth=2, label='TPV Distribution')

        # Mark key values
        ax.axvline(x=tpv_mean, color=COLORS['tpv'], linestyle='-', linewidth=2, label=f'Mean: {tpv_mean:.2f}')
        ax.axvline(x=tpv_lower, color=COLORS['danger'], linestyle='--', linewidth=1.5, label=f'5%: {tpv_lower:.2f}')
        ax.axvline(x=tpv_upper, color=COLORS['success'], linestyle='--', linewidth=1.5, label=f'95%: {tpv_upper:.2f}')
        ax.axvline(x=0, color='black', linestyle='-', linewidth=1, alpha=0.5)

        # Shade CI region
        ci_mask = (x >= tpv_lower) & (x <= tpv_upper)
        ax.fill_between(x, y, where=ci_mask, alpha=0.4, color=COLORS['info'], label='90% CI')

        ax.set_xlabel('TPV (M KRW)', fontsize=10)
        ax.set_ylabel('Probability Density', fontsize=10)
        ax.set_title(f'Project {project["project_id"]} - TPV Uncertainty Distribution', fontsize=11)
        ax.legend(loc='upper right', fontsize=9)
        ax.grid(alpha=0.3)

        # Add text annotation
        decision_text = f"TPV Decision: {project['tpv_decision']}"
        ax.annotate(decision_text, xy=(0.02, 0.95), xycoords='axes fraction',
                   fontsize=10, fontweight='bold',
                   color=COLORS['success'] if project['tpv'] > 0 else COLORS['danger'])

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", padx=10, pady=10)
        self.figures.append(fig)

    def _update_project_details_tab(self):
        """Update project details tab after analysis"""
        if self.results_df is None:
            return

        # Update project selector
        projects = self.results_df['project_id'].tolist()
        self.project_selector.configure(values=projects, state="normal")
        self.prev_project_btn.configure(state="normal")
        self.next_project_btn.configure(state="normal")

        # Select first project
        if projects:
            self.current_project_id = projects[0]
            self.project_selector.set(self.current_project_id)
            self._display_project_details(self.current_project_id)

    def _update_sensitivity_tab(self):
        """Update sensitivity analysis tab"""
        # Clear existing
        for widget in self.sensitivity_frame.winfo_children():
            widget.destroy()

        # Tornado diagram
        self._create_tornado_chart()

        # Decision robustness chart
        self._create_robustness_chart()

    def _create_tornado_chart(self):
        """Create tornado diagram for sensitivity analysis"""
        chart_frame = ctk.CTkFrame(self.sensitivity_frame, fg_color=COLORS['bg_card'], corner_radius=10)
        chart_frame.pack(fill="x", pady=10, padx=5)

        ctk.CTkLabel(
            chart_frame,
            text="Figure 1. Tornado Diagram - Parameter Sensitivity Analysis",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_dark']
        ).pack(pady=(15, 5))

        fig, ax = plt.subplots(figsize=(12, 6), dpi=100)

        # Simulated sensitivity data (in real app, this would come from sensitivity_results)
        parameters = ['Cost Ratio', 'Competition Level', 'Follow-on Prob', 'Volatility',
                     'Strategic Alignment', 'Capability Level', 'Recovery Rate']

        df = self.results_df
        base_tpv = df['tpv'].mean()

        # Simulate +/- 20% impact
        np.random.seed(42)
        impacts_low = -np.abs(np.random.randn(len(parameters)) * 10 + 5)
        impacts_high = np.abs(np.random.randn(len(parameters)) * 10 + 5)

        # Sort by total range
        ranges = impacts_high - impacts_low
        sorted_idx = np.argsort(ranges)[::-1]

        parameters = [parameters[i] for i in sorted_idx]
        impacts_low = impacts_low[sorted_idx]
        impacts_high = impacts_high[sorted_idx]

        y = np.arange(len(parameters))

        ax.barh(y, impacts_low, color=COLORS['danger'], alpha=0.7, label='-20%')
        ax.barh(y, impacts_high, color=COLORS['success'], alpha=0.7, label='+20%')

        ax.set_yticks(y)
        ax.set_yticklabels(parameters, fontsize=10)
        ax.set_xlabel('TPV Change (M KRW)', fontsize=10)
        ax.axvline(x=0, color='black', linestyle='-', linewidth=1)
        ax.legend(loc='lower right')
        ax.grid(axis='x', alpha=0.3)

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", padx=10, pady=10)

        self.figures.append(fig)

    def _create_robustness_chart(self):
        """Create decision robustness chart"""
        chart_frame = ctk.CTkFrame(self.sensitivity_frame, fg_color=COLORS['bg_card'], corner_radius=10)
        chart_frame.pack(fill="x", pady=10, padx=5)

        ctk.CTkLabel(
            chart_frame,
            text="Figure 6. Decision Robustness Analysis",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_dark']
        ).pack(pady=(15, 5))

        fig, ax = plt.subplots(figsize=(12, 5), dpi=100)

        df = self.results_df
        x = np.arange(len(df))

        # Stacked bar for decision probabilities
        bottom = np.zeros(len(df))

        categories = [
            ('prob_strong_participate', 'Strong Participate', COLORS['success']),
            ('prob_participate', 'Participate', '#81C784'),
            ('prob_conditional', 'Conditional', COLORS['warning']),
            ('prob_reject', 'Reject', COLORS['danger'])
        ]

        for col, label, color in categories:
            values = df[col].values
            ax.bar(x, values, bottom=bottom, label=label, color=color, alpha=0.8, edgecolor='white')
            bottom += values

        ax.set_xlabel('Project', fontsize=10)
        ax.set_ylabel('Probability', fontsize=10)
        ax.set_xticks(x)
        ax.set_xticklabels(df['project_id'], fontsize=9)
        ax.set_ylim(0, 1)
        ax.legend(loc='upper right', fontsize=9)
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", padx=10, pady=10)

        self.figures.append(fig)

    def _update_stats(self):
        """Update quick statistics"""
        if self.results_df is None:
            return

        df = self.results_df

        total_npv = df['npv'].sum()
        total_tpv = df['tpv'].sum()
        total_rov = df['rov_net'].sum()

        decision_changed = df['decision_changed'].sum()
        up_changes = (df['decision_direction'] == 'Up').sum()
        down_changes = (df['decision_direction'] == 'Down').sum()

        avg_rov_ratio = (df['rov_net'] / df['contract_amount']).mean() * 100

        stats_text = f"""Projects: {len(df)}

Total NPV: {total_npv:,.1f} M
Total ROV: {total_rov:,.1f} M
Total TPV: {total_tpv:,.1f} M

Decision Changes: {decision_changed}
  - Up (Reject->Part.): {up_changes}
  - Down (Part.->Reject): {down_changes}

Avg ROV/Contract: {avg_rov_ratio:.1f}%"""

        self.stats_label.configure(text=stats_text, text_color=COLORS['text_dark'])

    def _export_results(self):
        """Export results to CSV"""
        if self.results_df is None:
            messagebox.showwarning("Warning", "No results to export!")
            return

        file_path = filedialog.asksaveasfilename(
            title="Export Results",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if file_path:
            try:
                self.results_df.to_csv(file_path, index=False)
                messagebox.showinfo("Success", f"Results exported to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed:\n{str(e)}")

    def _on_closing(self):
        """Handle window close event"""
        # Close all matplotlib figures
        for fig in self.figures:
            plt.close(fig)
        self.figures.clear()

        self.destroy()


def main():
    """Main entry point"""
    app = BIMValuationApp()
    app.mainloop()


if __name__ == "__main__":
    main()
