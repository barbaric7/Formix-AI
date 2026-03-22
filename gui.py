import customtkinter as ctk
import json
import os
import sys
import threading
from app import run_automation, setup_browser_login


# ─────────────────────────────────────────────
#  DESIGN TOKENS  (single source of truth)
# ─────────────────────────────────────────────
COLORS = {
    # Backgrounds
    "bg_root":        "#0F1117",   # deepest base
    "bg_card":        "#16181F",   # card surfaces
    "bg_input":       "#1C1F2A",   # input fields
    "bg_tab_active":  "#1C1F2A",
    "bg_tab_idle":    "#0F1117",

    # Accent — electric indigo
    "accent":         "#5B6CF8",
    "accent_hover":   "#4A5AE8",
    "accent_dim":     "#1E2340",

    # Semantic colours
    "success":        "#22C55E",
    "success_hover":  "#16A34A",
    "warning":        "#F59E0B",
    "warning_hover":  "#D97706",
    "danger":         "#EF4444",

    # Text
    "text_primary":   "#F0F2FF",
    "text_secondary": "#8B8FA8",
    "text_muted":     "#50546A",

    # Borders
    "border":         "#252836",
    "border_focus":   "#5B6CF8",
}

FONT = {
    "family_ui":   "Segoe UI",
    "family_mono": "Cascadia Code",
    "size_h1":     20,
    "size_h2":     14,
    "size_body":   12,
    "size_small":  11,
}

RADIUS  = 10
PAD_X   = 18
PAD_Y   = 10


# ─────────────────────────────────────────────
#  LOG REDIRECTOR
# ─────────────────────────────────────────────
class TextRedirector:
    def __init__(self, textbox, root):
        self.textbox = textbox
        self.root = root

    def write(self, string):
        self.root.after(0, self._insert_text, string)

    def flush(self):
        pass

    def _insert_text(self, string):
        self.textbox.configure(state="normal")
        self.textbox.insert("end", string)
        self.textbox.see("end")
        self.textbox.configure(state="disabled")


# ─────────────────────────────────────────────
#  HELPER: SECTION CARD
# ─────────────────────────────────────────────
def make_card(parent, title=None, icon=None):
    """A rounded, bordered card frame with an optional header row."""
    card = ctk.CTkFrame(
        parent,
        fg_color=COLORS["bg_card"],
        corner_radius=RADIUS,
        border_width=1,
        border_color=COLORS["border"],
    )
    card.pack(fill="x", pady=(0, 12), padx=2)

    if title:
        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=PAD_X, pady=(14, 0))
        label_text = f"{icon}  {title}" if icon else title
        ctk.CTkLabel(
            hdr,
            text=label_text,
            font=ctk.CTkFont(family=FONT["family_ui"], size=FONT["size_h2"], weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(side="left")

    inner = ctk.CTkFrame(card, fg_color="transparent")
    inner.pack(fill="x", padx=PAD_X, pady=(8, 16))
    return inner


# ─────────────────────────────────────────────
#  HELPER: FIELD BUILDERS
# ─────────────────────────────────────────────
def make_label(parent, text):
    return ctk.CTkLabel(
        parent,
        text=text,
        font=ctk.CTkFont(family=FONT["family_ui"], size=FONT["size_small"], weight="bold"),
        text_color=COLORS["text_secondary"],
    )


def make_entry(parent, placeholder="", show="", default="", height=38):
    e = ctk.CTkEntry(
        parent,
        placeholder_text=placeholder,
        show=show,
        height=height,
        fg_color=COLORS["bg_input"],
        border_color=COLORS["border"],
        border_width=1,
        corner_radius=7,
        text_color=COLORS["text_primary"],
        placeholder_text_color=COLORS["text_muted"],
        font=ctk.CTkFont(family=FONT["family_ui"], size=FONT["size_body"]),
    )
    if default:
        e.insert(0, default)
    return e


def make_combo(parent, values, default="", height=38):
    c = ctk.CTkComboBox(
        parent,
        values=values,
        height=height,
        fg_color=COLORS["bg_input"],
        border_color=COLORS["border"],
        border_width=1,
        corner_radius=7,
        button_color=COLORS["border"],
        button_hover_color=COLORS["accent"],
        dropdown_fg_color=COLORS["bg_card"],
        dropdown_hover_color=COLORS["accent_dim"],
        text_color=COLORS["text_primary"],
        font=ctk.CTkFont(family=FONT["family_ui"], size=FONT["size_body"]),
    )
    c.set(default)
    return c


def labeled_field(parent, label, widget_factory, pady_top=10, pady_bottom=0):
    """Stacks a label above a widget and returns the widget."""
    make_label(parent, label).pack(anchor="w", pady=(pady_top, 3))
    w = widget_factory(parent)
    w.pack(fill="x", pady=(0, pady_bottom))
    return w


def make_divider(parent):
    ctk.CTkFrame(
        parent, height=1,
        fg_color=COLORS["border"],
        corner_radius=0,
    ).pack(fill="x", pady=8)


# ─────────────────────────────────────────────
#  MAIN APPLICATION
# ─────────────────────────────────────────────
class FormAutomationApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("AutoForm AI")
        self.geometry("700x820")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg_root"])

        self.settings_file = "user_settings.json"
        self.user_data = self.load_settings()

        self._build_titlebar()
        self._build_tabs()

        if not self.user_data:
            self.tabview.set("Profile")
        else:
            self.tabview.set("Dashboard")

    # ── TITLE BAR ──────────────────────────────
    def _build_titlebar(self):
        bar = ctk.CTkFrame(self, fg_color="transparent", height=56)
        bar.pack(fill="x", padx=24, pady=(18, 4))
        bar.pack_propagate(False)

        # Logo mark
        logo_dot = ctk.CTkFrame(bar, width=8, height=28, fg_color=COLORS["accent"], corner_radius=4)
        logo_dot.pack(side="left", pady=14)

        ctk.CTkLabel(
            bar,
            text="  AutoForm AI",
            font=ctk.CTkFont(family=FONT["family_ui"], size=FONT["size_h1"], weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(side="left", pady=14)

        ctk.CTkLabel(
            bar,
            text="v2.0",
            font=ctk.CTkFont(family=FONT["family_ui"], size=10),
            text_color=COLORS["text_muted"],
        ).pack(side="left", padx=(6, 0), pady=20)

        # Status pill
        self.status_pill = ctk.CTkLabel(
            bar,
            text="● Ready",
            font=ctk.CTkFont(family=FONT["family_ui"], size=11, weight="bold"),
            text_color=COLORS["success"],
            fg_color=COLORS["bg_card"],
            corner_radius=20,
            padx=12,
            pady=4,
        )
        self.status_pill.pack(side="right", pady=14)

    # ── TABS ───────────────────────────────────
    def _build_tabs(self):
        self.tabview = ctk.CTkTabview(
            self,
            fg_color=COLORS["bg_root"],
            segmented_button_fg_color=COLORS["bg_card"],
            segmented_button_selected_color=COLORS["accent"],
            segmented_button_selected_hover_color=COLORS["accent_hover"],
            segmented_button_unselected_color=COLORS["bg_card"],
            segmented_button_unselected_hover_color=COLORS["bg_input"],
            text_color=COLORS["text_secondary"],
            text_color_disabled=COLORS["text_muted"],
            corner_radius=RADIUS,
        )
        self.tabview.pack(padx=18, pady=(4, 18), fill="both", expand=True)

        self.tabview.add("Dashboard")
        self.tabview.add("Profile")

        # Style the tab container
        self.tabview._segmented_button.configure(
            font=ctk.CTkFont(family=FONT["family_ui"], size=12, weight="bold")
        )

        self._build_dashboard(self.tabview.tab("Dashboard"))
        self._build_profile(self.tabview.tab("Profile"))

    # ══════════════════════════════════════════
    #  DASHBOARD TAB
    # ══════════════════════════════════════════
    def _build_dashboard(self, tab):
        tab.configure(fg_color="transparent")

        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent", scrollbar_button_color=COLORS["border"])
        scroll.pack(fill="both", expand=True)

        # ── URL Input Card ─────────────────────
        url_inner = make_card(scroll, title="Target Form", icon="⬡")
        make_label(url_inner, "GOOGLE FORM URL").pack(anchor="w")
        self.form_link_input = make_entry(url_inner, placeholder="https://docs.google.com/forms/d/...", height=42)
        self.form_link_input.pack(fill="x", pady=(4, 0))

        # ── Action Buttons ─────────────────────
        btn_inner = make_card(scroll, title="Actions", icon="◈")

        setup_desc = ctk.CTkLabel(
            btn_inner,
            text="First time? Log in via the browser setup step before running automation.",
            font=ctk.CTkFont(family=FONT["family_ui"], size=11),
            text_color=COLORS["text_secondary"],
            wraplength=580,
            justify="left",
        )
        setup_desc.pack(anchor="w", pady=(0, 10))

        btn_row = ctk.CTkFrame(btn_inner, fg_color="transparent")
        btn_row.pack(fill="x")
        btn_row.columnconfigure(0, weight=1)
        btn_row.columnconfigure(1, weight=1)

        self.setup_btn = ctk.CTkButton(
            btn_row,
            text="⚙   Browser Setup",
            command=self.start_setup_thread,
            height=44,
            fg_color=COLORS["bg_input"],
            hover_color=COLORS["warning_hover"],
            border_width=1,
            border_color=COLORS["warning"],
            text_color=COLORS["warning"],
            corner_radius=8,
            font=ctk.CTkFont(family=FONT["family_ui"], size=12, weight="bold"),
        )
        self.setup_btn.grid(row=0, column=0, padx=(0, 6), sticky="ew")

        self.start_btn = ctk.CTkButton(
            btn_row,
            text="▶   Run Automation",
            command=self.start_automation_thread,
            height=44,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            corner_radius=8,
            font=ctk.CTkFont(family=FONT["family_ui"], size=12, weight="bold"),
        )
        self.start_btn.grid(row=0, column=1, padx=(6, 0), sticky="ew")

        # ── Terminal Log Card ──────────────────
        log_card = ctk.CTkFrame(
            scroll,
            fg_color=COLORS["bg_card"],
            corner_radius=RADIUS,
            border_width=1,
            border_color=COLORS["border"],
        )
        log_card.pack(fill="both", expand=True, pady=(0, 2), padx=2)

        log_header = ctk.CTkFrame(log_card, fg_color="transparent")
        log_header.pack(fill="x", padx=PAD_X, pady=(12, 6))

        ctk.CTkLabel(
            log_header,
            text="⬛  Live Output",
            font=ctk.CTkFont(family=FONT["family_ui"], size=FONT["size_h2"], weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(side="left")

        ctk.CTkButton(
            log_header,
            text="Clear",
            width=60,
            height=26,
            fg_color=COLORS["bg_input"],
            hover_color=COLORS["border"],
            text_color=COLORS["text_secondary"],
            corner_radius=6,
            font=ctk.CTkFont(family=FONT["family_ui"], size=11),
            command=lambda: (
                self.log_textbox.configure(state="normal"),
                self.log_textbox.delete("1.0", "end"),
                self.log_textbox.configure(state="disabled"),
            ),
        ).pack(side="right")

        # Separator
        ctk.CTkFrame(log_card, height=1, fg_color=COLORS["border"], corner_radius=0).pack(fill="x")

        self.log_textbox = ctk.CTkTextbox(
            log_card,
            state="disabled",
            fg_color="#0B0D14",
            text_color="#6EE7B7",
            font=ctk.CTkFont(family=FONT["family_mono"], size=12),
            corner_radius=0,
            height=260,
            scrollbar_button_color=COLORS["border"],
        )
        self.log_textbox.pack(fill="both", expand=True, padx=1, pady=(0, 1))

        sys.stdout = TextRedirector(self.log_textbox, self)

    # ══════════════════════════════════════════
    #  PROFILE TAB
    # ══════════════════════════════════════════
    def _build_profile(self, tab):
        tab.configure(fg_color="transparent")

        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent", scrollbar_button_color=COLORS["border"])
        scroll.pack(fill="both", expand=True)

        # ── App Setup ─────────────────────────
        ai_inner = make_card(scroll, title="App Setup", icon="◈")

        self.browser_input = labeled_field(
            ai_inner, "PREFERRED BROWSER",
            lambda p: make_combo(p, ["Chrome", "Edge"], default=self.user_data.get("browser", "Chrome")),
        )
        self.primary_api_input = labeled_field(
            ai_inner, "PRIMARY API KEY  (OpenRouter / GPT)",
            lambda p: make_entry(p, placeholder="sk-or-v1-...", show="*", default=self.user_data.get("primary_api_key", "")),
            pady_top=14,
        )
        self.secondary_api_input = labeled_field(
            ai_inner, "SECONDARY API KEY  (Llama / Claude)",
            lambda p: make_entry(p, placeholder="sk-or-v1-...", show="*", default=self.user_data.get("secondary_api_key", "")),
            pady_top=14,
        )

        # ── Personal Details ───────────────────
        per_inner = make_card(scroll, title="Personal Details", icon="⬡")

        self.email_input = labeled_field(
            per_inner, "EMAIL ADDRESS",
            lambda p: make_entry(p, placeholder="student@college.edu", default=self.user_data.get("email", "")),
        )
        self.name_input = labeled_field(
            per_inner, "FULL NAME",
            lambda p: make_entry(p, default=self.user_data.get("full_name", "")),
            pady_top=14,
        )

        make_divider(per_inner)

        # Two-column row: Roll + PRN
        row_a = ctk.CTkFrame(per_inner, fg_color="transparent")
        row_a.pack(fill="x")
        row_a.columnconfigure(0, weight=1)
        row_a.columnconfigure(1, weight=1)

        lf_roll = ctk.CTkFrame(row_a, fg_color="transparent")
        lf_roll.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        make_label(lf_roll, "ROLL NUMBER").pack(anchor="w", pady=(0, 3))
        self.roll_input = make_entry(lf_roll, default=self.user_data.get("roll_number", ""))
        self.roll_input.pack(fill="x")

        lf_prn = ctk.CTkFrame(row_a, fg_color="transparent")
        lf_prn.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        make_label(lf_prn, "PRN").pack(anchor="w", pady=(0, 3))
        self.prn_input = make_entry(lf_prn, default=self.user_data.get("prn", ""))
        self.prn_input.pack(fill="x")

        self.college_input = labeled_field(
            per_inner, "COLLEGE NAME",
            lambda p: make_entry(p, default=self.user_data.get("college", "Vishwakarma Institute of Technology")),
            pady_top=14,
        )

        make_divider(per_inner)

        # Two-column row: Year + Branch
        row_b = ctk.CTkFrame(per_inner, fg_color="transparent")
        row_b.pack(fill="x")
        row_b.columnconfigure(0, weight=1)
        row_b.columnconfigure(1, weight=1)

        lf_yr = ctk.CTkFrame(row_b, fg_color="transparent")
        lf_yr.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        make_label(lf_yr, "YEAR").pack(anchor="w", pady=(0, 3))
        self.year_input = make_combo(lf_yr, ["Year I", "Year II", "Year III", "Year IV"], default=self.user_data.get("year", "Year II"))
        self.year_input.pack(fill="x")

        lf_branch = ctk.CTkFrame(row_b, fg_color="transparent")
        lf_branch.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        make_label(lf_branch, "BRANCH & DIVISION").pack(anchor="w", pady=(0, 3))
        branch_options = [
            "CS-A","CS-B","CS-C","CS-D","CS-E","CS-F","CS-G","CS-H","CS-I",
            "CSAI-A","CSAI-B","CSAI-C","CSAI-D","CSAI-E","CSAI-F","CSAI-G","CSAI-H",
            "CSAIML-A","CSAIML-B","CSAIML-C","CSAIML-D","CSAIML-E","CSAIML-F",
            "CSSE-A","CSSE-B","CSSE-C","CSSE-D","CSDS-A","CSDS-B","CSDS-C",
            "CSIOT-A","CSIOT-B","CSIS-A",
            "IT-A","IT-B","IT-C","IT-D","IT-E","IT-F","IT-G",
        ]
        self.branch_input = make_combo(lf_branch, branch_options, default=self.user_data.get("branch_division", "CSSE-B"))
        self.branch_input.pack(fill="x")

        # ── Save Button ────────────────────────
        save_wrap = ctk.CTkFrame(scroll, fg_color="transparent")
        save_wrap.pack(fill="x", pady=(4, 6), padx=2)

        self.save_btn = ctk.CTkButton(
            save_wrap,
            text="Save Profile",
            command=self.save_settings,
            height=46,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            corner_radius=9,
            font=ctk.CTkFont(family=FONT["family_ui"], size=13, weight="bold"),
        )
        self.save_btn.pack(fill="x")

    # ══════════════════════════════════════════
    #  DATA LAYER
    # ══════════════════════════════════════════
    def load_settings(self):
        if os.path.exists(self.settings_file):
            with open(self.settings_file, "r") as f:
                return json.load(f)
        return {}

    def save_settings(self):
        data = {
            "primary_api_key":  self.primary_api_input.get(),
            "secondary_api_key": self.secondary_api_input.get(),
            "email":            self.email_input.get(),
            "full_name":        self.name_input.get(),
            "roll_number":      self.roll_input.get(),
            "prn":              self.prn_input.get(),
            "college":          self.college_input.get(),
            "year":             self.year_input.get(),
            "branch_division":  self.branch_input.get(),
            "browser":          self.browser_input.get(),
        }
        with open(self.settings_file, "w") as f:
            json.dump(data, f, indent=2)
        self.user_data = data
        self.tabview.set("Dashboard")
        self._set_status("● Profile saved", COLORS["success"])
        print("✅  Profile saved successfully.\n")

    # ══════════════════════════════════════════
    #  STATUS HELPER
    # ══════════════════════════════════════════
    def _set_status(self, text, color):
        self.after(0, lambda: self.status_pill.configure(text=text, text_color=color))

    # ══════════════════════════════════════════
    #  THREADING & AUTOMATION
    # ══════════════════════════════════════════
    def start_setup_thread(self):
        if not self.user_data:
            print("❌  Please save your profile first.\n")
            return
        self.setup_btn.configure(state="disabled", text="Setting up…")
        self._set_status("● Setting up", COLORS["warning"])
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.configure(state="disabled")
        threading.Thread(target=self._run_setup, daemon=True).start()

    def _run_setup(self):
        try:
            setup_browser_login(self.user_data)
            self._set_status("● Ready", COLORS["success"])
        except Exception as e:
            print(f"\n❌  CRITICAL ERROR: {e}\n")
            self._set_status("● Error", COLORS["danger"])
        finally:
            self.after(0, lambda: self.setup_btn.configure(state="normal", text="⚙   Browser Setup"))

    def start_automation_thread(self):
        form_url = self.form_link_input.get().strip()
        if not form_url:
            print("❌  Please paste a Google Form URL first.\n")
            return
        if not self.user_data:
            print("❌  Please save your profile first.\n")
            return
        self.user_data["form_url"] = form_url
        self.start_btn.configure(state="disabled", text="Running…")
        self._set_status("● Running", COLORS["accent"])
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.configure(state="disabled")
        print("▶  Automation engine started…\n")
        threading.Thread(target=self._run_automation, daemon=True).start()

    def _run_automation(self):
        try:
            run_automation(self.user_data)
            self._set_status("● Done", COLORS["success"])
        except Exception as e:
            print(f"\n❌  CRITICAL ERROR: {e}\n")
            self._set_status("● Error", COLORS["danger"])
        finally:
            self.after(0, lambda: self.start_btn.configure(state="normal", text="▶   Run Automation"))


# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = FormAutomationApp()
    app.mainloop()