#!/usr/bin/env python3
"""
BIM Real Options Valuation System - English GUI v15
Portable GUI Application using CustomTkinter
"""

import os
import sys
import threading
import numpy as np
import pandas as pd

# Add src directory to path for imports
if getattr(sys, 'frozen', False):
    # Running as compiled exe
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, BASE_DIR)

import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
import tkinter as tk

from valuation_engine_v14 import ValuationEngine
from tier_system import Tier0Input, Tier1Derivation, Tier2Sampler


# Set appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class BIMROVApp(ctk.CTk):
    """Main Application Window"""

    def __init__(self):
        super().__init__()

        self.title("BIM Real Options Valuation System v15")
        self.geometry("1400x900")
        self.minsize(1200, 700)

        # Data storage
        self.input_df = None
        self.results_df = None
        self.sensitivity_results = None

        # Create UI
        self._create_menu()
        self._create_main_layout()
        self._create_status_bar()

    def _create_menu(self):
        """Create menu bar"""
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)

        # File menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load CSV...", command=self._load_csv, accelerator="Ctrl+O")
        file_menu.add_command(label="Load Sample Data", command=self._load_sample_data)
        file_menu.add_separator()
        file_menu.add_command(label="Export Results...", command=self._export_results, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit, accelerator="Alt+F4")

        # View menu
        view_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Dark Mode", command=lambda: ctk.set_appearance_mode("dark"))
        view_menu.add_command(label="Light Mode", command=lambda: ctk.set_appearance_mode("light"))

        # Help menu
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
        help_menu.add_command(label="Model Documentation", command=self._show_model_info)

        # Keyboard shortcuts
        self.bind("<Control-o>", lambda e: self._load_csv())
        self.bind("<Control-s>", lambda e: self._export_results())

    def _create_main_layout(self):
        """Create main layout with tabs"""
        # Main container
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Left panel - Controls
        self.left_panel = ctk.CTkFrame(self.main_container, width=350)
        self.left_panel.pack(side="left", fill="y", padx=(0, 10))
        self.left_panel.pack_propagate(False)

        # Right panel - Results
        self.right_panel = ctk.CTkFrame(self.main_container)
        self.right_panel.pack(side="right", fill="both", expand=True)

        self._create_left_panel()
        self._create_right_panel()

    def _create_left_panel(self):
        """Create left control panel"""
        # Title
        title_label = ctk.CTkLabel(
            self.left_panel,
            text="Control Panel",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(15, 20))

        # Data Section
        data_frame = ctk.CTkFrame(self.left_panel)
        data_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(
            data_frame,
            text="Data Input",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))

        self.load_btn = ctk.CTkButton(
            data_frame,
            text="Load CSV File",
            command=self._load_csv,
            height=35
        )
        self.load_btn.pack(fill="x", padx=10, pady=5)

        self.sample_btn = ctk.CTkButton(
            data_frame,
            text="Load Sample Data",
            command=self._load_sample_data,
            height=35,
            fg_color="gray40"
        )
        self.sample_btn.pack(fill="x", padx=10, pady=(5, 10))

        self.data_info_label = ctk.CTkLabel(
            data_frame,
            text="No data loaded",
            text_color="gray"
        )
        self.data_info_label.pack(pady=(0, 10))

        # Simulation Settings
        sim_frame = ctk.CTkFrame(self.left_panel)
        sim_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            sim_frame,
            text="Simulation Settings",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))

        # Number of simulations
        sim_sub_frame = ctk.CTkFrame(sim_frame, fg_color="transparent")
        sim_sub_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(sim_sub_frame, text="Monte Carlo Iterations:").pack(side="left")

        self.sim_count_var = tk.StringVar(value="5000")
        self.sim_count_entry = ctk.CTkEntry(
            sim_sub_frame,
            textvariable=self.sim_count_var,
            width=80
        )
        self.sim_count_entry.pack(side="right")

        # Simulation presets
        preset_frame = ctk.CTkFrame(sim_frame, fg_color="transparent")
        preset_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(
            preset_frame, text="1K", width=50,
            command=lambda: self.sim_count_var.set("1000"),
            fg_color="gray40"
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            preset_frame, text="5K", width=50,
            command=lambda: self.sim_count_var.set("5000"),
            fg_color="gray40"
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            preset_frame, text="10K", width=50,
            command=lambda: self.sim_count_var.set("10000"),
            fg_color="gray40"
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            preset_frame, text="20K", width=50,
            command=lambda: self.sim_count_var.set("20000"),
            fg_color="gray40"
        ).pack(side="left", padx=2)

        # Run button
        self.run_btn = ctk.CTkButton(
            sim_frame,
            text="Run Valuation",
            command=self._run_valuation,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="green",
            hover_color="darkgreen"
        )
        self.run_btn.pack(fill="x", padx=10, pady=15)

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(sim_frame)
        self.progress_bar.pack(fill="x", padx=10, pady=(0, 10))
        self.progress_bar.set(0)

        # Export Section
        export_frame = ctk.CTkFrame(self.left_panel)
        export_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            export_frame,
            text="Export Results",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))

        self.export_btn = ctk.CTkButton(
            export_frame,
            text="Export to CSV",
            command=self._export_results,
            height=35,
            state="disabled"
        )
        self.export_btn.pack(fill="x", padx=10, pady=(5, 10))

        # Quick Stats
        self.stats_frame = ctk.CTkFrame(self.left_panel)
        self.stats_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            self.stats_frame,
            text="Quick Statistics",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))

        self.stats_label = ctk.CTkLabel(
            self.stats_frame,
            text="Run valuation to see statistics",
            text_color="gray",
            justify="left"
        )
        self.stats_label.pack(padx=10, pady=(0, 10))

    def _create_right_panel(self):
        """Create right panel with tabs"""
        # Tab view
        self.tab_view = ctk.CTkTabview(self.right_panel)
        self.tab_view.pack(fill="both", expand=True, padx=5, pady=5)

        # Add tabs
        self.tab_view.add("Input Data")
        self.tab_view.add("Results Summary")
        self.tab_view.add("ROV Breakdown")
        self.tab_view.add("Decision Analysis")

        # Input Data Tab
        self._create_input_tab()

        # Results Summary Tab
        self._create_results_tab()

        # ROV Breakdown Tab
        self._create_rov_tab()

        # Decision Analysis Tab
        self._create_decision_tab()

    def _create_input_tab(self):
        """Create input data tab"""
        tab = self.tab_view.tab("Input Data")

        # Treeview for input data
        columns = ("project_id", "contract_amount", "infra_type", "design_phase",
                   "contract_duration", "procurement_type", "client_type")

        self.input_tree = ttk.Treeview(tab, columns=columns, show="headings", height=20)

        # Define headings
        headings = {
            "project_id": "Project ID",
            "contract_amount": "Contract (M)",
            "infra_type": "Infrastructure",
            "design_phase": "Design Phase",
            "contract_duration": "Duration (yr)",
            "procurement_type": "Procurement",
            "client_type": "Client Type"
        }

        for col in columns:
            self.input_tree.heading(col, text=headings[col])
            self.input_tree.column(col, width=120, anchor="center")

        # Scrollbars
        v_scroll = ttk.Scrollbar(tab, orient="vertical", command=self.input_tree.yview)
        h_scroll = ttk.Scrollbar(tab, orient="horizontal", command=self.input_tree.xview)
        self.input_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        # Pack
        self.input_tree.pack(side="left", fill="both", expand=True)
        v_scroll.pack(side="right", fill="y")

    def _create_results_tab(self):
        """Create results summary tab"""
        tab = self.tab_view.tab("Results Summary")

        columns = ("project_id", "npv", "rov_net", "tpv", "npv_decision",
                   "tpv_decision", "decision_changed", "decision_direction")

        self.results_tree = ttk.Treeview(tab, columns=columns, show="headings", height=20)

        headings = {
            "project_id": "Project ID",
            "npv": "NPV (M)",
            "rov_net": "ROV Net (M)",
            "tpv": "TPV (M)",
            "npv_decision": "NPV Decision",
            "tpv_decision": "TPV Decision",
            "decision_changed": "Changed?",
            "decision_direction": "Direction"
        }

        for col in columns:
            self.results_tree.heading(col, text=headings[col])
            self.results_tree.column(col, width=110, anchor="center")

        v_scroll = ttk.Scrollbar(tab, orient="vertical", command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=v_scroll.set)

        self.results_tree.pack(side="left", fill="both", expand=True)
        v_scroll.pack(side="right", fill="y")

    def _create_rov_tab(self):
        """Create ROV breakdown tab"""
        tab = self.tab_view.tab("ROV Breakdown")

        columns = ("project_id", "follow_on", "capability", "resource",
                   "abandonment", "contract", "switch", "stage",
                   "rov_gross", "interaction", "risk_premium", "deferral", "rov_net")

        self.rov_tree = ttk.Treeview(tab, columns=columns, show="headings", height=20)

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
            "interaction": "Interact.",
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

        self.rov_tree.pack(side="left", fill="both", expand=True)
        v_scroll.pack(side="right", fill="y")

    def _create_decision_tab(self):
        """Create decision analysis tab"""
        tab = self.tab_view.tab("Decision Analysis")

        columns = ("project_id", "prob_strong", "prob_participate",
                   "prob_conditional", "prob_reject", "robustness",
                   "tpv_ci_lower", "tpv", "tpv_ci_upper")

        self.decision_tree = ttk.Treeview(tab, columns=columns, show="headings", height=20)

        headings = {
            "project_id": "Project",
            "prob_strong": "P(Strong)",
            "prob_participate": "P(Participate)",
            "prob_conditional": "P(Conditional)",
            "prob_reject": "P(Reject)",
            "robustness": "Robustness",
            "tpv_ci_lower": "TPV 5%",
            "tpv": "TPV Mean",
            "tpv_ci_upper": "TPV 95%"
        }

        for col in columns:
            self.decision_tree.heading(col, text=headings[col])
            self.decision_tree.column(col, width=100, anchor="center")

        v_scroll = ttk.Scrollbar(tab, orient="vertical", command=self.decision_tree.yview)
        self.decision_tree.configure(yscrollcommand=v_scroll.set)

        self.decision_tree.pack(side="left", fill="both", expand=True)
        v_scroll.pack(side="right", fill="y")

    def _create_status_bar(self):
        """Create status bar"""
        self.status_bar = ctk.CTkFrame(self, height=30)
        self.status_bar.pack(side="bottom", fill="x")

        self.status_label = ctk.CTkLabel(
            self.status_bar,
            text="Ready",
            font=ctk.CTkFont(size=11)
        )
        self.status_label.pack(side="left", padx=10)

        self.version_label = ctk.CTkLabel(
            self.status_bar,
            text="BIM ROV System v15 | Engine v14",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.version_label.pack(side="right", padx=10)

    def _load_csv(self):
        """Load CSV file"""
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if file_path:
            try:
                self.input_df = pd.read_csv(file_path)
                self._validate_and_display_input()
                self.status_label.configure(text=f"Loaded: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file:\n{str(e)}")

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
        self._validate_and_display_input()
        self.status_label.configure(text="Sample data loaded (10 projects)")

    def _validate_and_display_input(self):
        """Validate input data and display in tree"""
        required_cols = ['project_id', 'contract_amount', 'infra_type',
                        'design_phase', 'contract_duration', 'procurement_type', 'client_type']

        missing = [col for col in required_cols if col not in self.input_df.columns]
        if missing:
            messagebox.showerror("Error", f"Missing required columns:\n{', '.join(missing)}")
            self.input_df = None
            return

        # Clear existing data
        for item in self.input_tree.get_children():
            self.input_tree.delete(item)

        # Insert new data
        for _, row in self.input_df.iterrows():
            values = (
                row['project_id'],
                f"{row['contract_amount']:.0f}",
                row['infra_type'],
                row['design_phase'],
                f"{row['contract_duration']:.1f}",
                row['procurement_type'],
                row['client_type']
            )
            self.input_tree.insert("", "end", values=values)

        # Update info label
        self.data_info_label.configure(
            text=f"{len(self.input_df)} projects loaded",
            text_color="lightgreen"
        )

    def _run_valuation(self):
        """Run valuation in background thread"""
        if self.input_df is None:
            messagebox.showwarning("Warning", "Please load data first!")
            return

        try:
            n_sim = int(self.sim_count_var.get())
            if n_sim < 100 or n_sim > 100000:
                raise ValueError("Simulations must be between 100 and 100,000")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid simulation count:\n{str(e)}")
            return

        # Disable controls during valuation
        self.run_btn.configure(state="disabled", text="Running...")
        self.progress_bar.set(0)
        self.status_label.configure(text="Running Monte Carlo simulation...")

        # Run in background thread
        thread = threading.Thread(target=self._valuation_worker, args=(n_sim,))
        thread.start()

        # Monitor progress
        self._monitor_progress(thread)

    def _valuation_worker(self, n_simulations):
        """Worker function for valuation"""
        try:
            engine = ValuationEngine(n_simulations=n_simulations)
            self.results_df, self.sensitivity_results = engine.run_valuation(self.input_df)
            self._valuation_complete = True
        except Exception as e:
            self._valuation_error = str(e)
            self._valuation_complete = False

    def _monitor_progress(self, thread):
        """Monitor valuation progress"""
        if thread.is_alive():
            # Animate progress bar
            current = self.progress_bar.get()
            if current < 0.9:
                self.progress_bar.set(current + 0.02)
            self.after(100, lambda: self._monitor_progress(thread))
        else:
            # Valuation complete
            self.progress_bar.set(1.0)
            self.run_btn.configure(state="normal", text="Run Valuation")

            if hasattr(self, '_valuation_complete') and self._valuation_complete:
                self._display_results()
                self.export_btn.configure(state="normal")
                self.status_label.configure(text="Valuation completed successfully!")
                messagebox.showinfo("Success", "Valuation completed!")
            else:
                error_msg = getattr(self, '_valuation_error', 'Unknown error')
                messagebox.showerror("Error", f"Valuation failed:\n{error_msg}")
                self.status_label.configure(text="Valuation failed")

    def _display_results(self):
        """Display results in all tabs"""
        if self.results_df is None:
            return

        # Clear existing data
        for tree in [self.results_tree, self.rov_tree, self.decision_tree]:
            for item in tree.get_children():
                tree.delete(item)

        # Results Summary Tab
        for _, row in self.results_df.iterrows():
            values = (
                row['project_id'],
                f"{row['npv']:.2f}",
                f"{row['rov_net']:.2f}",
                f"{row['tpv']:.2f}",
                row['npv_decision'],
                row['tpv_decision'],
                "Yes" if row['decision_changed'] else "No",
                row['decision_direction']
            )
            self.results_tree.insert("", "end", values=values)

        # ROV Breakdown Tab
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

        # Decision Analysis Tab
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

        # Update Quick Statistics
        self._update_quick_stats()

        # Switch to Results tab
        self.tab_view.set("Results Summary")

    def _update_quick_stats(self):
        """Update quick statistics panel"""
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

Total NPV: {total_npv:,.1f}M
Total ROV: {total_rov:,.1f}M
Total TPV: {total_tpv:,.1f}M

Decision Changes: {decision_changed}
  - Up (Reject→Part.): {up_changes}
  - Down (Part.→Reject): {down_changes}

Avg ROV/Contract: {avg_rov_ratio:.1f}%"""

        self.stats_label.configure(text=stats_text, text_color="white")

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
                self.status_label.configure(text=f"Exported: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed:\n{str(e)}")

    def _show_about(self):
        """Show about dialog"""
        about_text = """BIM Real Options Valuation System

Version: v15 (GUI) / v14 (Engine)

A real options-based valuation model for
BIM design service bidding decisions.

Core Concept: TPV = NPV + ROV

Features:
• 3-Tier Input System
• 7 Real Options
• 3 Adjustment Factors
• Monte Carlo Simulation

Author: Hanbin Lee
Purpose: Academic Research"""

        messagebox.showinfo("About", about_text)

    def _show_model_info(self):
        """Show model documentation"""
        info_text = """Real Options Model Documentation

=== 7 Options (+) ===
1. Follow-on: Subsequent design participation
2. Capability: BIM capability accumulation
3. Resource: Idle resource utilization
4. Abandonment: Early termination flexibility
5. Contract: Scope reduction flexibility
6. Switch: Resource reallocation
7. Staging: Staged investment

=== 3 Adjustments (-) ===
1. Interaction: Option overlap discount
2. Risk Premium: Volatility/complexity premium
3. Deferral Cost: Opportunity cost

=== Decision Criteria ===
• Strong Participate: TPV > NPV×1.5 & TPV > 30M
• Participate: NPV×1.05 < TPV ≤ NPV×1.5
• Conditional: NPV×0.80 < TPV ≤ NPV×1.05
• Reject: TPV ≤ NPV×0.80 or TPV ≤ 0"""

        messagebox.showinfo("Model Documentation", info_text)


def main():
    """Main entry point"""
    app = BIMROVApp()
    app.mainloop()


if __name__ == "__main__":
    main()
