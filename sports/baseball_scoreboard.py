from shared.shared import *
class BaseballSoftballScoreboard(QWidget, ScoreboardToolkit):
    def __init__(self, state: ScoreState, mode="transparent", parent=None):
        super().__init__(parent)
        self.state = state
        self.mode = mode
        self.flash_on = False
        self.state.bspossession = "top"
        self.show_baseballsoftball_intro = False
        self.show_baseballsoftball_breakboard = False
        self.show_baseballsoftball_scorebug = True 
        self.show_baseballsoftball_final = False
        screen = QApplication.primaryScreen()
        dpi_scale = screen.devicePixelRatio()
        self.setFixedSize(int(1920*dpi_scale), int(1080*dpi_scale))
        if self.mode == "transparent":
            self.setAttribute(Qt.WA_TranslucentBackground)
        else:
            self.bg_color = QColor(255, 0, 255)  # green chroma key for vMix
        self.setAutoFillBackground(False)

        # fonts
        self.sets_font = QFont("College", 22, QFont.Bold)
        self.title_font = QFont("BigNoodleTitling", 20, QFont.Bold)
        self.timer_font = QFont("College", 30, QFont.Bold)
        self.setNumber_font = QFont("College", 18, QFont.Bold)
        self.set_font = QFont("College", 18, QFont.Bold)
        self.score_font = QFont("BigNoodleTitling", 30, QFont.Bold)
        self.record_font = QFont("College", 25, QFont.Bold)
        self.introupper_font = QFont("BigNoodleTitling", 25, QFont.Bold)
        self.introtitle_font = QFont("College", 30, QFont.Bold)
        self.introupper1_font = QFont("BigNoodleTitling", 25) 
        self.introlower_font = QFont("BigNoodleTitling", 20)   
        self.introrank_font = QFont("BigNoodleTitling", 30)
        self.introschool_font = QFont("BigNoodleTitling", 30, QFont.Bold)
        self.introcity_font = QFont("BigNoodleTitling", 25)
        self.bbtimer_font = QFont("Legacy", 15)
        self.bbperiod_font = QFont("Legacy", 15)
        self.final_font = QFont("BigNoodleTitling", 30, QFont.Bold)
        self.bbscore_font = QFont("Octin Sports", 55, QFont.Bold)
        self.event_font = QFont("Legacy", 12, QFont.Bold)
        self.introrecord_font = QFont("College", 24, QFont.Bold)
        self.inning_font = QFont("BigNoodleTitling", 30, QFont.Bold)
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing)
        w = self.width()
        h = self.height()
        if self.mode == "keyable":
            p.fillRect(self.rect(), self.bg_color)
        if self.show_baseballsoftball_intro:
            self.draw_baseballsoftball_intro(p)
        if self.show_baseballsoftball_scorebug:
            self.draw_baseballsoftball_scorebug(p)
        if self.show_baseballsoftball_breakboard:
            self.draw_baseballsoftball_breakboard(p)
        if self.show_baseballsoftball_final:
            self.draw_baseballsoftball_final(p)
            return
    def draw_baseballsoftball_intro(self, p):
        pass
    def draw_baseballsoftball_breakboard(self, p):
        pass
    def draw_baseballsoftball_scorebug(self, p):
        left_x = 1415
        left_w = 400
        y_base = 890
        h_main = 120
        x = left_x + 190 - 15  # half of text box width
        y = y_base + 60
        top_color = QColor("#ff0000") if getattr(self.state, "bspossession", "top") == "top" else QColor("#1c1c1c")
        bottom_color = QColor("#ff0000") if getattr(self.state, "bspossession", "bottom") == "bottom" else QColor("#1c1c1c")       
        self.draw_fully_rounded_rect(p, left_x, y_base, left_w, h_main, QColor("#1c1c1c"), radius=10)
        self.draw_tlteam_gradient_rect(p, left_x + 8, y_base + 8, left_w - 301, 52, self.state.away_color)
        self.draw_blteam_gradient_rect(p, left_x + 8, y_base + 60, left_w - 301, 52, self.state.home_color)
        self.draw_line(p, left_x + 8, y_base + 60, left_x + 8 + (left_w - 301), y_base + 60, QColor("#ffffff"), 3)        
        self.draw_normal_rect(p, left_x + 105, y_base + 8, 60, 52, QColor("#ffffff"))
        self.draw_normal_rect(p, left_x + 105, y_base + 60, 60, 52, QColor("#ffffff"))  
        self.draw_line(p, left_x + 105, y_base + 60, left_x + 165, y_base + 60, QColor("#000000"), 3)
        self.draw_up_triangle(p, left_x + 190, y_base + 28, 18, 18, top_color)
        p.setPen(QColor("#ffffff"))
        p.setPen(QColor("#ffffff"))
        p.setFont(self.inning_font)
        p.drawText(x, y-20, 30, 45, Qt.AlignCenter, str(self.state.inning))
        self.draw_down_triangle(p, left_x + 190, y_base + 95, 18, 18, bottom_color)
        self.draw_line(p, left_x + 212, y_base + 8, left_x + 212, y_base + 112, QColor("#ffffff"), 3)
        p.setPen(QColor("#000000"))
        p.setFont(self.score_font)
        p.drawText(QRect(left_x + 130, y_base + 14, 60, 52), str(self.state.bsaway_score))
        p.drawText(QRect(left_x + 130, y_base + 66, 60, 52), str(self.state.bshome_score))
        out1 = QColor("#ff0000") if self.state.outs >= 1 else QColor("#1c1c1c")
        out2 = QColor("#ff0000") if self.state.outs >= 2 else QColor("#1c1c1c")
        x2 = left_x + 225
        p.setPen(QPen(QColor("#ffffff"), 2))
        p.setBrush(out1)
        p.drawEllipse(x2, y_base + 80, 16, 16)
        p.setBrush(out2)
        p.drawEllipse(x2 + 35, y_base + 80, 16, 16)
        x = left_x + 225
        p.setPen(QColor("#ffffff"))
        p.setFont(self.record_font)
        p.drawText(x, y_base + 25, 100, 55, Qt.AlignLeft, f"{self.state.balls}-{self.state.strikes}")
        
        logo_x, logo_y, logo_w, logo_h = left_x + 29, y_base + 3, 60, 65
        p.save()
        self.draw_logo_in_top_rounded_window(p, logo_x, logo_y, logo_w, logo_h, self.state.away_logo)
        p.restore()

        logo_x2, logo_y2, logo_w2, logo_h2 = left_x + 29, y_base + 55, 60, 65
        p.save()
        self.draw_logo_in_top_rounded_window(p, logo_x2, logo_y2, logo_w2, logo_h2, self.state.home_logo)
        p.restore()
        base_x = left_x + 345
        base_y = y_base + 57
        gap = 22
        self.draw_diamond(p, base_x, base_y - gap, 14, QColor("#ff0000") if self.state.second_base else QColor("#1c1c1c"))
        self.draw_diamond(p, base_x - gap, base_y, 14, QColor("#ff0000") if self.state.third_base else QColor("#1c1c1c"))
        self.draw_diamond(p, base_x + gap, base_y, 14, QColor("#ff0000") if self.state.first_base else QColor("#1c1c1c"))
    def draw_baseballsoftball_final(self, p):
        pass
        p.end()
class BaseballSoftballControl(QMainWindow):
    def __init__(self, state: ScoreState, scoreboard: BaseballSoftballScoreboard):
        super().__init__()
        self.state = state
        version = beta_version if beta_mode else current_version

        self.setWindowTitle(
            f"Baseball/Softball Scoreboard Control (Version: {version}"
            f"{' - BETA' if beta_mode else ''})"
        )
        self.setStyleSheet("""
        QWidget{background:#121212;color:white;font-size:12px;}
        QGroupBox{border:1px solid #2a2a2a;margin-top:10px;padding:8px;font-weight:bold;}
        QGroupBox::title{subcontrol-origin:margin;left:10px;padding:0 5px;}
        QPushButton{background:white;color:black;border:none;padding:6px;border-radius:6px;}
        QPushButton:hover{background:#e6e6e6;}
        QPushButton:pressed{background:#cfcfcf;}
        QLabel{color:white;}
        QLCDNumber{background:#0a0a0a;color:white;border:1px solid #333;border-radius:6px;}
        QTabWidget::pane{background:white;}
        QTabBar::tab{background:white;color:black;padding:6px;}
        QTabBar::tab:selected{background:white;color:black;}
        """)
        self.scoreboard = scoreboard
        self.state.first_base = False
        self.state.second_base = False
        self.state.third_base = False
        self.state.outs = False
        self.setWindowTitle("Baseball/Softball Scoreboard Control")
        self.setMinimumSize(720, 520)
        tabs = QTabWidget()
        self.setCentralWidget(tabs)
        page1 = QWidget()
        tabs.addTab(page1, "Game Info Setup")
        grid_info = QGridLayout()
        page1.setLayout(grid_info)
        page2 = QWidget()
        tabs.addTab(page2, "Main Controls")
        grid = QGridLayout()
        page2.setLayout(grid)
        score_group = QGroupBox("Score Control")
        count_group = QGroupBox("Count Control")
        inning_group = QGroupBox("Inning Control")
        bases_group = QGroupBox("Bases Control")
        score_layout = QGridLayout()
        count_layout = QGridLayout()
        inning_layout = QGridLayout()
        bases_layout = QGridLayout()
        score_group.setLayout(score_layout)
        count_group.setLayout(count_layout)
        inning_group.setLayout(inning_layout)
        bases_group.setLayout(bases_layout)
        grid.addWidget(score_group, 0, 0, 1, 2)
        grid.addWidget(count_group, 1, 0)
        grid.addWidget(inning_group, 1, 1)
        grid.addWidget(bases_group, 2, 0, 1, 2)
        page3 = QWidget()
        tabs.addTab(page3, "Away Setup")
        grid_away = QGridLayout()
        page3.setLayout(grid_away)
        page4 = QWidget()
        tabs.addTab(page4, "Home Setup")
        grid_home = QGridLayout()
        page4.setLayout(grid_home)
        self.away_lcd = QLCDNumber()
        self.home_lcd = QLCDNumber()
        self.away_lcd.setDigitCount(3)
        self.home_lcd.setDigitCount(3)
        self.away_lcd.display(self.state.bsaway_score)
        self.home_lcd.display(self.state.bshome_score)
        btn_away = QPushButton("Away +1")
        btn_home = QPushButton("Home +1")
        btn_away.clicked.connect(lambda: self.add_runs("away", 1))
        btn_home.clicked.connect(lambda: self.add_runs("home", 1))
        score_layout.addWidget(QLabel(self.state.away_name), 0, 0)
        score_layout.addWidget(QLabel(self.state.home_name), 0, 1)
        score_layout.addWidget(self.away_lcd, 1, 0)
        score_layout.addWidget(self.home_lcd, 1, 1)
        score_layout.addWidget(btn_away, 2, 0)
        score_layout.addWidget(btn_home, 2, 1)
        self.balls_lcd = QLCDNumber()
        self.strikes_lcd = QLCDNumber()
        self.outs_lcd = QLCDNumber()
        for lcd in (self.balls_lcd, self.strikes_lcd, self.outs_lcd):
            lcd.setDigitCount(1)
        self.update_count()
        btn_ball = QPushButton("+ Ball")
        btn_strike = QPushButton("+ Strike")
        btn_out = QPushButton("+ Out")
        btn_ball.clicked.connect(lambda: self.change_ball(1))
        btn_strike.clicked.connect(lambda: self.change_strike(1))
        btn_out.clicked.connect(lambda: self.change_out(1))
        count_layout.addWidget(QLabel("Balls"), 0, 0)
        count_layout.addWidget(QLabel("Strikes"), 0, 1)
        count_layout.addWidget(QLabel("Outs"), 0, 2)
        count_layout.addWidget(self.balls_lcd, 1, 0)
        count_layout.addWidget(self.strikes_lcd, 1, 1)
        count_layout.addWidget(self.outs_lcd, 1, 2)
        count_layout.addWidget(btn_ball, 2, 0)
        count_layout.addWidget(btn_strike, 2, 1)
        count_layout.addWidget(btn_out, 2, 2)
        btn_reset = QPushButton("Reset Count")
        btn_reset.clicked.connect(self.reset_count)
        count_layout.addWidget(btn_reset, 3, 0, 1, 3)
        self.inning_lcd = QLCDNumber()
        self.inning_lcd.setDigitCount(2)
        self.inning_lcd.display(self.state.inning)
        btn_top = QPushButton("Top")
        btn_bottom = QPushButton("Bottom")
        btn_next = QPushButton("Next Inning")
        btn_top.clicked.connect(lambda: self.set_possession("top"))
        btn_bottom.clicked.connect(lambda: self.set_possession("bottom"))
        btn_top.clicked.connect(lambda: self.set_half(True))
        btn_bottom.clicked.connect(lambda: self.set_half(False))
        btn_next.clicked.connect(self.next_inning)
        btn_hr = QPushButton("Home Run")
        btn_hr.clicked.connect(self.hit_home_run)
        score_layout.addWidget(btn_hr, 3, 0, 1, 2)
        inning_layout.addWidget(QLabel("Inning"), 0, 0)
        inning_layout.addWidget(self.inning_lcd, 1, 0)
        inning_layout.addWidget(btn_top, 2, 0)
        inning_layout.addWidget(btn_bottom, 2, 1)
        inning_layout.addWidget(btn_next, 2, 2)
        grid_away.addWidget(QLabel("<b>Away Team Setup</b>"), -1, 0)
        grid_away.addWidget(QLabel("Enter Away Name:"), 1, 0)
        self.away_setup_name = QLineEdit(self.state.away_name)
        grid_away.addWidget(self.away_setup_name, 1, 1)
        btn_away_name_submit = QPushButton("Submit")
        btn_away_name_submit.clicked.connect(self.submit_away_setup)
        grid_away.addWidget(btn_away_name_submit, 1, 2)
        grid_away.addWidget(QLabel("Away Team Color:"), 2, 0)
        btn_away_pick_color = QPushButton("🎨")
        btn_away_pick_color.clicked.connect(self.pick_away_color_from_setup)
        grid_away.addWidget(btn_away_pick_color, 2, 1)
        grid_away.addWidget(QLabel("Away Team Logo:"), 3, 0)
        btn_away_load_logo = QPushButton("🖼")
        btn_away_load_logo.clicked.connect(self.load_away_logo_from_setup)
        grid_away.addWidget(btn_away_load_logo, 3, 1)
        #grid_away.addWidget(QLabel("Away Team Record:"), 4, 0)
        #self.away_record_wins_edit = QLineEdit(str(self.state.away_record_wins))
        #self.away_record_losses_edit = QLineEdit(str(self.state.away_record_losses))
        #grid_away.addWidget(self.away_record_wins_edit, 4, 1)
        #grid_away.addWidget(self.away_record_losses_edit, 4, 2)
        #btn_away_record_submit = QPushButton("Submit")
        #btn_away_record_submit.clicked.connect(self.submit_away_setup)
        #grid_away.addWidget(btn_away_record_submit, 4, 3)
        #grid_away.addWidget(QLabel("Away District Record:"), 5, 0)
        #self.away_district_wins_edit = QLineEdit(str(self.state.away_district_wins))
        #self.away_district_losses_edit = QLineEdit(str(self.state.away_district_losses))
        #grid_away.addWidget(self.away_district_wins_edit, 5, 1)
        #grid_away.addWidget(self.away_district_losses_edit, 5, 2)
        #btn_away_district_submit = QPushButton("Submit")
        #btn_away_district_submit.clicked.connect(self.submit_away_setup)
        #grid_away.addWidget(btn_away_district_submit, 5, 3)
        grid_home.addWidget(QLabel("<b>Home Team Setup</b>"), -4, 0)
        grid_home.addWidget(QLabel("Enter Home Name:"), 0, 0)
        self.home_setup_name = QLineEdit(self.state.home_name)
        grid_home.addWidget(self.home_setup_name, 0, 1)
        btn_home_name_submit = QPushButton("Submit")
        btn_home_name_submit.clicked.connect(self.submit_home_setup)
        grid_home.addWidget(btn_home_name_submit, 0, 2)
        grid_home.addWidget(QLabel("Home Team Color:"), 1, 0)
        btn_home_pick_color = QPushButton("🎨")
        btn_home_pick_color.clicked.connect(self.pick_home_color_from_setup)
        grid_home.addWidget(btn_home_pick_color, 1, 1)
        grid_home.addWidget(QLabel("Home Team Logo:"), 2, 0)
        btn_home_load_logo = QPushButton("🖼")
        btn_home_load_logo.clicked.connect(self.load_home_logo_from_setup)
        grid_home.addWidget(btn_home_load_logo, 2, 1)
        #grid_home.addWidget(QLabel("Home Team Record:"), 3, 0)
        #self.home_record_wins_edit = QLineEdit(str(self.state.home_record_wins))
        #self.home_record_losses_edit = QLineEdit(str(self.state.home_record_losses))
        #grid_home.addWidget(self.home_record_wins_edit, 3, 1)
        #grid_home.addWidget(self.home_record_losses_edit, 3, 2)
        #btn_home_record_submit = QPushButton("Submit")
        #btn_home_record_submit.clicked.connect(self.submit_home_setup)
        #grid_home.addWidget(btn_home_record_submit, 3, 3)
        #grid_home.addWidget(QLabel("Home District Record:"), 4, 0)
        #grid_home.addWidget(self.home_district_wins_edit, 4, 1)
        #grid_home.addWidget(self.home_district_losses_edit, 4, 2)
        #btn_home_district_submit = QPushButton("Submit")
        #btn_home_district_submit.clicked.connect(self.submit_home_setup)
        #grid_home.addWidget(btn_home_district_submit, 4, 3)
        btn_first = QPushButton("1st Base")
        btn_second = QPushButton("2nd Base")
        btn_third = QPushButton("3rd Base")
        btn_clear_bases = QPushButton("Clear Bases")

        btn_first.clicked.connect(lambda: self.set_base(1))
        btn_second.clicked.connect(lambda: self.set_base(2))
        btn_third.clicked.connect(lambda: self.set_base(3))
        btn_clear_bases.clicked.connect(self.clear_bases)

        bases_layout.addWidget(btn_first, 0, 0)
        bases_layout.addWidget(btn_second, 0, 1)
        bases_layout.addWidget(btn_third, 0, 2)
        bases_layout.addWidget(btn_clear_bases, 1, 0, 1, 3)
    def repaint_scoreboard(self):
        self.scoreboard.update()
    def pick_away_color_from_setup(self):
        c = QColorDialog.getColor(self.state.away_color, self, "Pick Away Color")
        if c.isValid():
            self.state.away_color = c
            self.away_setup_name.setText(self.away_setup_name.text())  # no-op but keeps UI consistent
            self.repaint_scoreboard()

    def pick_home_color_from_setup(self):
        c = QColorDialog.getColor(self.state.home_color, self, "Pick Home Color")
        if c.isValid():
            self.state.home_color = c
            self.home_setup_name.setText(self.home_setup_name.text())
            self.repaint_scoreboard()

    def load_away_logo_from_setup(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open away logo", "", "Images (*.png *.jpg *.bmp)")
        if path:
            pm = QPixmap(path)
            pm = pm.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.state.away_logo = pm
            self.repaint_scoreboard()
    def update_base_buttons(self):
        self.btn_first.setEnabled(not self.state.first_base)
        self.btn_second.setEnabled(not self.state.second_base)
        self.btn_third.setEnabled(not self.state.third_base)
    def load_home_logo_from_setup(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open home logo", "", "Images (*.png *.jpg *.bmp)")
        if path:
            pm = QPixmap(path)
            pm = pm.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.state.home_logo = pm
            self.repaint_scoreboard()
    def draw_rect(self, p, x, y, w, h, color):
        shadow = QColor(0, 0, 0, 120)

        for i in range(8):
            alpha = 120 - (i * 15)
            shadow.setAlpha(max(alpha, 0))
            p.setBrush(shadow)
            p.drawRect(int(x + 6 + i), int(y + 6 + i), int(w - i*2), int(h - i*2))

        p.setBrush(color)
        p.drawRect(int(x), int(y), int(w), int(h))
    def submit_away_setup(self):
        text = self.away_setup_name.text().strip() or self.state.away_name
        metrics = QFontMetrics(self.title_font)  
        if metrics.horizontalAdvance(text) > 150:
            QMessageBox.warning(self, "Name Too Long", "The away team name is too long.\nPlease enter a shorter name.")
            return

        self.state.away_name = text
        try:
            self.state.away_record_wins = int(self.away_record_wins_edit.text().strip())
        except Exception:
            pass
        try:
            self.state.away_record_losses = int(self.away_record_losses_edit.text().strip())
        except Exception:
            pass
        try:
            self.state.away_district_wins = int(self.away_district_wins_edit.text().strip())
        except Exception:
            pass
        try:
            self.state.away_district_losses = int(self.away_district_losses_edit.text().strip())
        except Exception:
            pass
        self.repaint_scoreboard()

    def submit_home_setup(self):
        text = self.home_setup_name.text().strip() or self.state.home_name
        metrics = QFontMetrics(self.title_font)  
        if metrics.horizontalAdvance(text) > 200:
            QMessageBox.warning(self, "Name Too Long", "The home team name is too long.\nPlease enter a shorter name.")
            return

        self.state.home_name = text
        try:
            self.state.home_record_wins = int(self.home_record_wins_edit.text().strip())
        except Exception:
            pass
        try:
            self.state.home_record_losses = int(self.home_record_losses_edit.text().strip())
        except Exception:
            pass
        try:
            self.state.home_district_wins = int(self.home_district_wins_edit.text().strip())
        except Exception:
            pass
        try:
            self.state.home_district_losses = int(self.home_district_losses_edit.text().strip())
        except Exception:
            pass

        self.repaint_scoreboard()
    def set_possession(self, side):
        self.state.bspossession = side
        self.update()
    def add_runs(self, team, runs):
        runs = int(runs)
        if team == "away":
            self.state.bsaway_score += runs
            self.away_lcd.display(self.state.bsaway_score)
        else:
            self.state.bshome_score += runs
            self.home_lcd.display(self.state.bshome_score)
        self.scoreboard.update()
    def set_base(self, base):
        if base == 1:
            self.state.first_base = True
        elif base == 2:
            self.state.second_base = True
        elif base == 3:
            self.state.third_base = True

        self.repaint_scoreboard()
    def clear_bases(self):
        self.state.first_base = False
        self.state.second_base = False
        self.state.third_base = False
        self.repaint_scoreboard()
    def change_ball(self, v):
        self.state.balls += v

        if self.state.balls >= 4:

            # save old state first (prevents overwrite bugs)
            first = self.state.first_base
            second = self.state.second_base
            third = self.state.third_base

            # runner advance (MLB correct order)
            self.state.third_base = second
            self.state.second_base = first
            self.state.first_base = True

            # ONLY reset count (NOT bases)
            self.reset_count()

            self.repaint_scoreboard()
            return

        self.update_count()
        self.repaint_scoreboard()


    def change_strike(self, v):
        self.state.strikes += v

        if self.state.strikes >= 3:
            self.state.outs += 1
            self.reset_count()

            if self.state.outs >= 3:
                self.state.outs = 0
                self.state.strikes = 0
                self.state.balls = 0

                self.state.first_base = False
                self.state.second_base = False
                self.state.third_base = False

                self.state.is_bottom = not self.state.is_bottom

            self.repaint_scoreboard()
            return

        self.update_count()
        self.repaint_scoreboard()


    def change_out(self, v):
        self.state.outs += v

        # inning reset at 3 outs (IMPORTANT FIX)
        if self.state.outs >= 3:
            self.state.outs = 0
            self.state.strikes = 0
            self.state.balls = 0

            # optional inning advance hook
            # self.next_inning()

        self.update_count()
        self.repaint_scoreboard()

    def reset_count(self):
        self.state.balls = 0
        self.state.strikes = 0

        self.update_count()
        self.repaint_scoreboard()

    def update_count(self):
        self.balls_lcd.display(self.state.balls)
        self.strikes_lcd.display(self.state.strikes)
        self.outs_lcd.display(self.state.outs)

    def set_half(self, top):
        self.state.top_inning = top
        self.repaint_scoreboard()

    def next_inning(self):
        self.state.inning += 1
        self.state.top_inning = True

        self.state.balls = 0
        self.state.strikes = 0
        self.state.outs = 0

        # RESET BASES ON NEW INNING
        self.state.first_base = False
        self.state.second_base = False
        self.state.third_base = False

        self.inning_lcd.display(self.state.inning)
        self.update_count()

        self.repaint_scoreboard()
    def hit_home_run(self):
        team, ok = QInputDialog.getItem(
            self,
            "Home Run",
            "Select scoring team:",
            ["Home", "Away"],
            0,
            False
        )

        if not ok:
            return  # user cancelled

        runs = 1  # batter always scores

        # clear bases and count runners
        if self.state.first_base:
            runs += 1
            self.state.first_base = False

        if self.state.second_base:
            runs += 1
            self.state.second_base = False

        if self.state.third_base:
            runs += 1
            self.state.third_base = False

        # assign score based on popup choice
        if team == "Home":
            self.state.bshome_score += runs
        else:
            self.state.bsaway_score += runs

        # reset count
        self.state.balls = 0
        self.state.strikes = 0

        self.repaint_scoreboard()
