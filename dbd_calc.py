import customtkinter as ctk
from tkinter import font as tkfont

# these two lines are the first thing you set up in any CTk app
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# define colors as constants at the top so if I ever want to change a color they're all in once place
BG_DARK = "#0e0c0a" # main window background
BG_CARD = "#1a1512" # input/card surface
BG_RESULT = "#141210" # result panel background
ACCENT = "#c0392b" # primary accent
ACCENT_HOV = "#a93226" # hover states
TEXT_MAIN = "#d4c9b8" # body text
TEXT_DIM = "#6b6356" # labels
TEXT_VALUE = "#e8d5c0" # result numbers
BORDER = "#3a2e25" # border

# ------- game data -------
SHARD_PER_LEVEL = [50, 65, 85, 150, 195, 235, 270, 300]
XP_PER_LEVEL = [720, 900, 1200, 2100, 2700, 3300, 3750, 4200]
AVG_XP_PER_GAME = 550

def get_tier(level: int) -> int:
    # helper function to return the reward tier for a given level
    if level <= 2: return 0
    if level <= 3: return 1
    if level <= 6: return 2
    if level <= 14: return 3
    if level <= 24: return 4
    if level <= 34: return 5
    if level <= 49: return 6
    return 7

class DBDCalculator(ctk.CTk):

    # initialize ctk window setup
    def __init__(self):
        super().__init__()

        # ------- window configuration -------
        self.title("Dead by Daylight - Shard Calculator")
        self.geometry("480x600")
        self.resizable(False, False)
        self.configure(fg_color=BG_DARK)

        # build all widgets
        self._build_header()
        self._build_inputs()
        self._build_button()
        self._build_results()

        # bind Enter key to calculate when pressed
        self.bind("<Return>", lambda event: self.calculate())

    # split the UI into sections, each by its own method. underscore prefix is a Python convention to represent an internal method, not be called from outside

    def _build_header(self):
        title = ctk.CTkLabel(self, text="DEAD BY DAYLIGHT", font=ctk.CTkFont(family="Georgia", size=20, weight="bold"), text_color=ACCENT)

        # pack() actually places the widget in the window. pady adds vertical padding
        title.pack(pady=(28, 0))

        subtitle = ctk.CTkLabel(self, text="Iridescent Shard Calculator", font=ctk.CTkFont(family="Georgia", size=12), text_color=TEXT_DIM,)
        subtitle.pack(pady=(2, 20))

        # CTk doesnt have a separator widget, so a common trick is to use this 1px tall frame as a visual divider
        sep = ctk.CTkFrame(self, height=1, fg_color=BORDER)

        # fill="x" makes it stretch the full width. padx adds side margins
        sep.pack(fill="x", padx=24, pady=(0, 20))

    def _build_inputs(self):
        """
        layout guide:
            pack() - stacks widgets top to bottom
            grid() - places widgets in rows and columns
            place() - absolute pixel positioning. excessive and usually not necessary
        """

        # frames are invisible containers just used to group things together
        grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        grid_frame.pack(padx=28, fill="x")

        # columnconfigure makes the two columns share space equally (weight=1). otherwise columns automatically shrink to fit their content!
        grid_frame.columnconfigure(0, weight=1)
        grid_frame.columnconfigure(1, weight=1)

        # store entry references as instance variables so calculate() can read them later
        self.entry_level = self._make_field(grid_frame, "Current Level", 0, 0)
        self.entry_xp = self._make_field(grid_frame, "Current XP", 0, 1)
        self.entry_shards = self._make_field(grid_frame, "Shards Owned", 1, 0)
        self.entry_needed = self._make_field(grid_frame, "Shards Needed", 1, 1)

    def _make_field(self, parent, label_text: str, row: int, col: int):
        """
        helper that creates one labeled input field and returns the entry widget
            parent - the frame this field lives inside
            label_text - the text shown above the input
            row, col - obviously grid position
        """
        cell = ctk.CTkFrame(parent, fg_color="transparent")
        cell.grid(row=row, column=col, padx=6, pady=6, sticky="ew")

        label = ctk.CTkLabel(cell, text=label_text.upper(), font=ctk.CTkFont(family="Georgia", size=10), text_color=TEXT_DIM, anchor="w")
        label.pack(fill="x", pady=(0, 3))

        entry = ctk.CTkEntry(
            cell, 
            height=38, 
            fg_color=BG_CARD, 
            border_color=BORDER, 
            border_width=1, 
            text_color=TEXT_MAIN, 
            font=ctk.CTkFont(family="Georgia", size=15), 
            placeholder_text="0", 
            placeholder_text_color=TEXT_DIM,
            )
        entry.pack(fill="x")

        return entry


    def _build_button(self):
        # the calculate button
         btn = ctk.CTkButton(
             self,
             text="CALCULATE",
             height=42,
             fg_color=ACCENT,
             hover_color=ACCENT_HOV,
             text_color=TEXT_MAIN,
             font=ctk.CTkFont(family="Georgia", size=13, weight="bold"),
             corner_radius=4,
             command=self.calculate, # no () since im passing self.calculate itself, not calling it yet. obvious but good to note for my brain
         )
         btn.pack(padx=28, pady=16, fill="x")

    def _build_results(self):
        # the results panel. 2x2 grid that starts empty and is filled in when calculate() is called
        sep = ctk.CTkFrame(self, height=1, fg_color=BORDER)
        sep.pack(fill="x", padx=24, pady=(0, 16))

        result_frame = ctk.CTkFrame(self, fg_color="transparent")
        result_frame.pack(padx=28, fill="x")
        result_frame.columnconfigure(0, weight=1)
        result_frame.columnconfigure(1, weight=1)

        # each stat card is a frame containing a label as the title and a label as the value. 
        # the value labels are instance variables so calculate() can update them later
        self.lbl_levels = self._make_stat_card(result_frame, "Levels Needed", 0, 0, accent=True)
        self.lbl_shards = self._make_stat_card(result_frame, "Shards to Earn", 0, 1)
        self.lbl_xp = self._make_stat_card(result_frame, "XP Required", 1, 0)
        self.lbl_games = self._make_stat_card(result_frame, "Average Games", 1, 1)

        # error label. hidden by default, shown on wrong input
        self.lbl_error = ctk.CTkLabel(
            self,
            text="",
            text_color=ACCENT,
            font=ctk.CTkFont(family="Georgia", size=13)
        )
        self.lbl_error.pack(pady=(10, 0))

    
    def _make_stat_card(self, parent, title: str, row: int, col: int, accent=False):
        """
        creates a stat card containing a title and a number
        returns the value label so calculate can update it.
        accent=True colors the number red
        """
        card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=4, border_width=1, border_color=BORDER)
        card.grid(row=row, column=col, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(
            card,
            text=title.upper(),
            font=ctk.CTkFont(family="Georgia", size=10),
            text_color=TEXT_DIM,
        ).pack(padx=14, pady=(13, 2), anchor="w")

        value_color = ACCENT if accent else TEXT_VALUE
        val_label = ctk.CTkLabel(
            card,
            text="-",
            font=ctk.CTkFont(family="Georgia", size=24),
            text_color=value_color
        )
        val_label.pack(padx=14, pady=(0, 14), anchor="w")

        return val_label
    

    # ------- logic -------

    def calculate(self):
        # reads the four inputs and calculates the results

        # clear any errors
        self.lbl_error.configure(text="")

        # read and validate input
        try:
            level = int(self.entry_level.get())
            cur_xp = int(self.entry_xp.get())
            cur_sh = int(self.entry_shards.get())
            need_sh = int(self.entry_needed.get())
        except ValueError:
            self.lbl_error.configure(text="Enter valid numbers in all fields.")
            self._clear_stats()
            return
        
        if cur_sh >= need_sh:
            self.lbl_error.configure(text="You already have enough shards.")
            self._clear_stats()
            return
        
        # simulate leveling
        xp_needed = -cur_xp
        levels_needed = 0
        shards = cur_sh

        while shards < need_sh:
            if level == 100:
                level = 1

            tier = get_tier(level)
            xp_needed += XP_PER_LEVEL[tier]
            shards += SHARD_PER_LEVEL[tier]
            level += 1
            levels_needed += 1

        xp_needed = max(0, xp_needed)
        games = xp_needed / AVG_XP_PER_GAME
        shard_diff = need_sh - cur_sh

        # update stat cards
        self.lbl_levels.configure(text=f"{levels_needed:,}")
        self.lbl_shards.configure(text=f"{shard_diff:,}")
        self.lbl_xp.configure(text=f"{xp_needed:,}")
        self.lbl_games.configure(text=f"{int(games + 0.9999):,}") # this forces the int conversion to round up if theres ever a decimal for full number of games


    def _clear_stats(self):
        # reset all stat cards to their empty state
        for lbl in (self.lbl_levels, self.lbl_shards, self.lbl_xp, self.lbl_games):
            lbl.configure(text="-")


if __name__ == "__main__":
    # create instance of class
    app = DBDCalculator()

    # start even loop. the window stays open until the user closes it
    app.mainloop()