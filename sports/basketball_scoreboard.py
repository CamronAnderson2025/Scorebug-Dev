from shared.shared import *
class BasketballScoreboard(QWidget, ScoreboardToolkit):
    def __init__(self, state: ScoreState, mode="transparent", parent=None):
        super().__init__(parent)

        self.state = state
        self.flash_on = False
        self.mode = mode

        self.show_basketball_intro = False
        self.show_basketball_breakboard = False
        self.show_basketball_scorebug = True
        self.show_basketball_final = False

        self.away_logo_state = LogoReveal()
        self.home_logo_state = LogoReveal()

        self.setMinimumSize(1920, 1080)
        self.resize(1920, 1080)

        # --- Transparent / Keyable Setup ---
        if self.mode == "transparent":
            self.setAttribute(Qt.WA_TranslucentBackground)
            self.setAttribute(Qt.WA_NoSystemBackground, True)
            self.setAttribute(Qt.WA_OpaquePaintEvent, False)
        else:
            self.bg_color = QColor(255, 0, 255)  # green chroma key for vMix

        self.setAutoFillBackground(False)

        # --- Fonts ---
        self.big_font = QFont("College", 40, QFont.Bold)
        self.timeout_font = QFont("BigNoodleTitling", 35, QFont.Bold)
        self.introupper_font = QFont("BigNoodleTitling", 25, QFont.Bold)
        self.introtitle_font = QFont("College", 30, QFont.Bold)
        self.introupper1_font = QFont("BigNoodleTitling", 25)
        self.introlower_font = QFont("BigNoodleTitling", 20)
        self.mid_font = QFont("College", 22, QFont.Bold)
        self.POSS_font = QFont("College", 14, QFont.Bold)
        self.brank_font = QFont("BigNoodleTitling", 15)
        self.rank_font = QFont("BigNoodleTitling", 14)
        self.mascot_font = QFont("BigNoodleTitling", 28, QFont.Bold)
        self.title_font = QFont("BigNoodleTitling", 20)
        self.ftitle_font = QFont("BigNoodleTitling", 30)
        self.frank_font = QFont("BigNoodleTitling", 23)
        self.bbtitle_font = QFont("BigNoodleTitling", 16, QFont.Bold)
        self.timer_font = QFont("College", 20, QFont.Bold)
        self.period_font = QFont("College", 15, QFont.Bold)
        self.score_font = QFont("Octin Sports", 50, QFont.Bold)
        self.fscore_font = QFont("Octin Sports", 125, QFont.Bold)
        self.record_font = QFont("College", 14, QFont.Bold)
        self.fouls_font = QFont("College", 12, QFont.Bold)
        self.scoreevent_font = QFont("BigNoodleTitling", 25, QFont.Bold)
        self.upperevent_font = QFont("BigNoodleTitling", 20, QFont.Bold)
        self.introrank_font = QFont("BigNoodleTitling", 30)
        self.introschool_font = QFont("BigNoodleTitling", 30, QFont.Bold)
        self.introcity_font = QFont("BigNoodleTitling", 25)
        self.bbtimer_font = QFont("Legacy", 15)
        self.bbperiod_font = QFont("Legacy", 15)
        self.final_font = QFont("BigNoodleTitling", 30, QFont.Bold)
        self.bbscore_font = QFont("Octin Sports", 55, QFont.Bold)
        self.event_font = QFont("Legacy", 12, QFont.Bold)
        self.introrecord_font = QFont("College", 24, QFont.Bold)

        # --- Center Logo ---
        self.center_logo_label = QLabel(self)
        self.center_logo_label.setAlignment(Qt.AlignCenter)

        self.request_logo_file()

        # --- Force Full Repaint For Transparent Animation ---
        ui_updater.refresh.connect(self.force_repaint)


    def force_repaint(self):
        self.repaint()


    def request_logo_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Center Logo",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )

        if file_path:
            self._load_center_logo(file_path)


    def _load_center_logo(self, file_path: str = ""):
        if not file_path:
            return

        pixmap = QPixmap(file_path)

        if pixmap.isNull():
            QMessageBox.warning(
                self,
                "Error",
                "Failed to load image from the selected file."
            )
        else:
            self.state.center_logo = pixmap
            self.repaint()


    def paintEvent(self, event):
        DESIGN_W = 1920
        DESIGN_H = 1080

        p = QPainter(self)

        # --- CLEAR PREVIOUS FRAME ---
        if self.mode == "transparent":
            p.setCompositionMode(QPainter.CompositionMode_Source)
            p.fillRect(self.rect(), Qt.transparent)
            p.setCompositionMode(QPainter.CompositionMode_SourceOver)

        p.setRenderHints(
            QPainter.Antialiasing |
            QPainter.TextAntialiasing
        )

        scale = min(
            self.width() / DESIGN_W,
            self.height() / DESIGN_H
        )

        offset_x = (self.width() - DESIGN_W * scale) / 2
        offset_y = (self.height() - DESIGN_H * scale) / 2

        p.translate(offset_x, offset_y)
        p.scale(scale, scale)

        if self.mode == "keyable":
            p.fillRect(0, 0, DESIGN_W, DESIGN_H, self.bg_color)

        if self.show_basketball_intro:
            self.draw_basketball_intro(p)

        if self.show_basketball_scorebug:
            self.draw_basketball_scorebug(p)

        if self.show_basketball_breakboard:
            self.draw_basketball_breakboard(p)

        if self.state.breakboard_timer > 0:
            self.draw_basketball_breakboard(p)

        if self.show_basketball_final:
            self.draw_basketball_final(p)
    def draw_basketball_intro(self, p):
        left_x = 550
        left_w = 400
        right_x = 950
        right_w = 400
        cx = 750
        cw = 175
        cy = 865
        base_home = QColor(self.state.home_color).darker(160)
        bg_home   = QColor(self.state.home_color).darker(160)
        base_away = QColor(self.state.away_color).darker(160)
        bg_away   = QColor(self.state.away_color).darker(160)
        rw = self.state.away_record_wins
        rl = self.state.away_record_losses
        dw = self.state.away_district_wins
        dl = self.state.away_district_losses
        hw = self.state.home_record_wins
        hl = self.state.home_record_losses
        hdw = self.state.home_district_wins
        hdl = self.state.home_district_losses

    # -- AWAY SECTION -- #
        if self.state.ileft_break_box_active:
            progress = self.state.ileft_break_box_progress
            curr_width1 = int((left_w + 100) * progress)
            curr_width2 = int(left_w * progress)
            self.draw_normal_rect(p, left_x + left_w - curr_width1, 790, curr_width1, 150, base_away)
            self.draw_normal_rect(p, left_x + 100 + left_w - curr_width2, 790, curr_width2-100, 150, self.state.away_color)
            fade_delay = .7  # fraction of animation before fade starts (30%)
            if progress <= fade_delay:
                opacity = 0.0
            else:
                opacity = (progress - fade_delay) / (1.0 - fade_delay)
            opacity = min(max(opacity, 0.0), 1.0)  # clamp between 0 and 1
            p.setOpacity(opacity)
            logo_x = left_x-100
            logo_y = 760
            logo_w = 200
            logo_h = 206
            p.save()
            self.clip_to_rounded_rect(p, left_x - 100 + left_w - curr_width2, 790, curr_width2, 150)
            self.draw_logo_in_top_rounded_window(p, logo_x, logo_y, logo_w, logo_h, self.state.away_logo)
            p.restore()
            rank,name=self.format_rank_name(self.state.away_rank,self.state.away_name)
            p.setPen(Qt.white)
            center_x=800
            text_y=810
            mascot_y=850
            spacing=6 if rank else 0
            rank_font=self.frank_font
            name_font=self.ftitle_font
            metrics_rank=QFontMetrics(rank_font)
            metrics_name=QFontMetrics(name_font)
            rank_w=metrics_rank.horizontalAdvance(rank) if rank else 0
            name_w=metrics_name.horizontalAdvance(name)
            total_w=rank_w+spacing+name_w
            rect_left=left_x+left_w-total_w
            left_limit=rect_left-8
            left_x_text=center_x-(total_w//2)
            if left_x_text<left_limit:
                max_w=center_x-left_limit
                if max_w>0 and total_w>0:
                    left_x_text=center_x-max_w//2
            name_x=center_x-(name_w//2)
            if rank:
                rank_x=name_x-spacing-rank_w
                p.setFont(rank_font)
                p.drawText(rank_x,text_y,rank_w,50,Qt.AlignRight|Qt.AlignVCenter,rank)
            p.setFont(name_font)
            p.drawText(name_x,text_y,name_w,45,Qt.AlignLeft|Qt.AlignVCenter,name)
            mascot=getattr(self.state,"away_mascot",None)
            if mascot:
                metrics_mascot=QFontMetrics(self.mascot_font)
                mascot_w=metrics_mascot.horizontalAdvance(mascot)
                mascot_center_x=center_x
                mascot_x=mascot_center_x-(mascot_w//2)
                max_mascot_width=800
                if mascot_w>max_mascot_width:
                    mascot=metrics_mascot.elidedText(mascot,Qt.ElideRight,max_mascot_width)
                    mascot_w=metrics_mascot.horizontalAdvance(mascot)
                    mascot_x=mascot_center_x-(mascot_w//2)
                p.setFont(self.mascot_font)
                p.drawText(mascot_x,mascot_y,mascot_w,45,Qt.AlignCenter|Qt.AlignVCenter,mascot)
            p.setPen(Qt.white)
            if not (rw == 0 and rl == 0):
                p.drawText(760, 838.5, curr_width1 - 20, 150, Qt.AlignLeft | Qt.AlignVCenter, f"{rw}-{rl}")
            if not (dw == 0 and dl == 0):
                p.drawText(800, 837.5, curr_width1 - 20, 150, Qt.AlignLeft | Qt.AlignVCenter, f"({dw}-{dl})")
            p.setOpacity(1.0)

    # -- HOME SECTION -- #
        if self.state.iright_break_box_active:
            progress = self.state.iright_break_box_progress
            curr_width = int(right_w * progress)
            self.draw_normal_rect(p, right_x+100, 790, int((right_w)*progress), 150, base_home)
            self.draw_normal_rect(p, right_x, 790, int((right_w-100)*progress), 150, self.state.home_color)
            fade_delay = .7  # fraction of animation before fade starts (30%)
            if progress <= fade_delay:
                opacity = 0.0
            else:
                opacity = (progress - fade_delay) / (1.0 - fade_delay)
            opacity = min(max(opacity, 0.0), 1.0)  # clamp between 0 and 1
            p.setOpacity(opacity)
            logo_x = right_x + 300
            logo_y = 760
            logo_w = 200
            logo_h = 206
            p.save()
            self.clip_to_rounded_rect(p, right_x, 790, int((right_w+205)*progress), 200)
            self.draw_logo_in_top_rounded_window(p, logo_x, logo_y, logo_w, logo_h, self.state.home_logo)
            p.restore()
            p.setFont(self.frank_font)
            p.setPen(Qt.white)
            if not (hw == 0 and hl == 0):
                p.drawText(1054, 838.5, curr_width - 20, 150, Qt.AlignLeft | Qt.AlignVCenter, f"{hw}-{hl}")
            if not (hdw == 0 and hdl == 0):
                p.drawText(1094, 837.5, curr_width - 20, 150, Qt.AlignLeft | Qt.AlignVCenter, f"({hdw}-{hdl})")      
            rank, name = self.format_rank_name(self.state.home_rank, self.state.home_name)
            p.setPen(Qt.white)
            p.setFont(self.frank_font)
            metrics_rank = QFontMetrics(self.frank_font)
            rank_w = metrics_rank.horizontalAdvance(rank) if rank else 0
            p.setFont(self.ftitle_font)
            metrics_name = QFontMetrics(self.ftitle_font)
            name_w = metrics_name.horizontalAdvance(name)
            name_center_x = 1100
            name_x = name_center_x - (name_w // 2)
            if rank:
                spacing = 6
                rank_x = name_x - spacing - rank_w
                p.setFont(self.frank_font)
                p.drawText(rank_x, 810, rank_w, 50, Qt.AlignRight | Qt.AlignVCenter, rank)
            p.setFont(self.ftitle_font)
            p.drawText(name_x, 810, name_w, 45, Qt.AlignLeft | Qt.AlignVCenter, name)
            mascot = getattr(self.state, "home_mascot", None)
            if mascot:
                p.setFont(self.mascot_font)
                metrics_mascot = QFontMetrics(self.mascot_font)
                mascot_w = metrics_mascot.horizontalAdvance(mascot)
                mascot_center_x = 1100
                mascot_x = mascot_center_x - (mascot_w // 2)
                mascot_y = 850
                max_mascot_width = 800
                if mascot_w > max_mascot_width:
                    mascot = metrics_mascot.elidedText(mascot, Qt.ElideRight, max_mascot_width)
                    mascot_w = metrics_mascot.horizontalAdvance(mascot)
                    mascot_x = mascot_center_x - (mascot_w // 2)
                p.drawText(mascot_x, mascot_y, mascot_w, 45, Qt.AlignCenter | Qt.AlignVCenter, mascot)

    # -- CENTER SECTION -- #
        if self.state.icenter_rect_active:
            progress = self.state.icenter_rect_progress
            half_width1 = int((left_w + 600) / 2 * progress)
            rect1_x = left_x - 100 + ((left_w + 600) / 2 - half_width1)
            self.draw_normal_rect(p, rect1_x, 740, half_width1 * 2, 50, QColor("#191919"))
            half_width2 = int((left_w - 200) / 2 * progress)
            rect2_x = left_x -100 + ((left_w + 600) / 2 - half_width1)
            self.draw_normal_rect(p, rect2_x, 940, half_width1 * 2, 35, QColor("#ffffff"))
            self.draw_normal_rect(p, left_x + 360, 820, 90, 90, QColor("white"))
            logo_x = left_x + 360
            logo_y = 820
            logo_w = 90
            logo_h = 90
            p.save()
            self.clip_to_rounded_rect(p, logo_x, 830, logo_w, 205)
            if self.state.center_logo is not None:
                self.draw_logo_in_top_rounded_window(p, logo_x, logo_y, logo_w, logo_h, self.state.center_logo)
            p.restore()
            fade_delay = .7  # fraction of animation before fade starts (30%)
            if progress <= fade_delay:
                opacity = 0.0
            else:
                opacity = (progress - fade_delay) / (1.0 - fade_delay)
            opacity = min(max(opacity, 0.0), 1.0)  # clamp between 0 and 1
            school = getattr(self.state, "event_location_school_text", "") or ""
            city   = getattr(self.state, "event_location_city_text", "") or ""
            if not school and not city:
                return
            rect_x = right_x - 475
            rect_y = 900
            rect_w = right_w + 575
            rect_h = 150
            pad_x = 20
            pad_y = 35
            max_w = rect_w - (pad_x * 2)
            p.setFont(self.introupper1_font)
            p.setPen(Qt.black)
            fm_school = QFontMetrics(self.introupper1_font)
            school_w = fm_school.horizontalAdvance(school)
            if school_w > max_w // 2:
                school = fm_school.elidedText(school, Qt.ElideRight, max_w // 2)
                school_w = fm_school.horizontalAdvance(school)
            p.setFont(self.introlower_font)
            fm_city = QFontMetrics(self.introlower_font)
            city_w = fm_city.horizontalAdvance(city)
            triangle_w = 16
            gap_after_school = 10
            gap_after_triangle = 15
            total_w = school_w + gap_after_school + triangle_w + gap_after_triangle + city_w
            start_x = rect_x + pad_x + (max_w - total_w) // 2
            p.setFont(self.introupper1_font)
            school_rect = QRect(start_x, rect_y + pad_y, school_w, 40)
            p.drawText(school_rect, Qt.AlignLeft | Qt.AlignVCenter, school)
            tri_center_x = start_x + school_w + gap_after_school
            tri_center_y = rect_y + pad_y + 20
            self.draw_right_triangle(p, tri_center_x, tri_center_y, triangle_w, 22, QColor("black"))
            p.setFont(self.introlower_font)
            p.setPen(Qt.black)
            city_x = tri_center_x + gap_after_triangle
            city_rect = QRect(city_x, rect_y + pad_y + 5, city_w+100, 40)
            p.drawText(city_rect, Qt.AlignLeft | Qt.AlignVCenter, city)
            if self.state.upperbb_event_active:
                self.draw_upper_event_text(p, left_x+45, 745, self.state.upperbb_event_text_basketball)         
            p.setOpacity(1.0)
            p.setOpacity(1.0)
    def draw_basketball_breakboard(self, p):
        left_x = 550
        left_w = 400
        right_x = 950
        right_w = 400
        cx = 750
        cw = 175
        cy = 865
        base_home = QColor(self.state.home_color).darker(160)
        bg_home   = QColor(self.state.home_color).darker(160)
        base_away = QColor(self.state.away_color).darker(160)
        bg_away   = QColor(self.state.away_color).darker(160)
    # -- AWAY SECTION -- #
        if self.state.left_break_box_active:
            progress = self.state.left_break_box_progress
            curr_width1 = int((left_w + 100) * progress)
            curr_width2 = int(left_w * progress)
            self.draw_normal_rect(p, left_x + left_w - curr_width1, 790, curr_width1, 200, base_away)
            self.draw_normal_rect(p, left_x + 200 + left_w - curr_width2, 790, curr_width2, 200, self.state.away_color)
            fade_delay = .7  # fraction of animation before fade starts (30%)
            if progress <= fade_delay:
                opacity = 0.0
            else:
                opacity = (progress - fade_delay) / (1.0 - fade_delay)
            opacity = min(max(opacity, 0.0), 1.0)  # clamp between 0 and 1
            p.setOpacity(opacity)
            logo_x = left_x + 205
            logo_y = 780
            logo_w = 200
            logo_h = 206
            p.save()
            self.clip_to_rounded_rect(p, left_x + 200 + left_w - curr_width2, 790, curr_width2, 200)
            self.draw_logo_in_top_rounded_window(p, logo_x, logo_y, logo_w, logo_h, self.state.away_logo)
            p.restore()
            rank, name = self.format_rank_name(self.state.away_rank, self.state.away_name)
            p.setPen(Qt.white)
            p.setFont(self.frank_font)
            metrics_rank = QFontMetrics(self.frank_font)
            rank_w = metrics_rank.horizontalAdvance(rank) if rank else 0
            p.setFont(self.ftitle_font)
            metrics_name = QFontMetrics(self.ftitle_font)
            name_w = metrics_name.horizontalAdvance(name)
            name_center_x = 600
            name_x = name_center_x - (name_w // 2)
            if rank:
                spacing = 6
                rank_x = name_x - spacing - rank_w
                p.setFont(self.frank_font)
                p.drawText(rank_x, 790, rank_w, 50, Qt.AlignRight | Qt.AlignVCenter, rank)
            p.setFont(self.ftitle_font)
            p.drawText(name_x, 790, name_w, 45, Qt.AlignLeft | Qt.AlignVCenter, name)
            p.setFont(self.fscore_font)
            p.setPen(Qt.white)
            p.drawText(left_x - 75, 810, 220, 175, Qt.AlignCenter, str(self.state.away_pts))
            p.setOpacity(1.0)

    # -- HOME SECTION -- #
        if self.state.right_break_box_active:
            progress = self.state.right_break_box_progress
            curr_width = int(right_w * progress)
            self.draw_normal_rect(p, right_x, 790, int((right_w+100)*progress), 200, base_home)
            self.draw_normal_rect(p, right_x, 790, int((right_w-200)*progress), 200, self.state.home_color)
            fade_delay = .7  # fraction of animation before fade starts (30%)
            if progress <= fade_delay:
                opacity = 0.0
            else:
                opacity = (progress - fade_delay) / (1.0 - fade_delay)
            opacity = min(max(opacity, 0.0), 1.0)  # clamp between 0 and 1
            p.setOpacity(opacity)
            logo_x = right_x
            logo_y = 780
            logo_w = 200
            logo_h = 206
            p.save()
            self.clip_to_rounded_rect(p, right_x, 790, int((right_w-205)*progress), 200)
            self.draw_logo_in_top_rounded_window(p, logo_x, logo_y, logo_w, logo_h, self.state.home_logo)
            p.restore()
            p.setFont(self.fscore_font)
            p.setPen(Qt.white)
            p.drawText(right_x+225, 810, 220, 175, Qt.AlignCenter, str(self.state.home_pts))
            rank, name = self.format_rank_name(self.state.home_rank, self.state.home_name)
            p.setPen(Qt.white)
            p.setFont(self.frank_font)
            metrics_rank = QFontMetrics(self.frank_font)
            rank_w = metrics_rank.horizontalAdvance(rank) if rank else 0
            p.setFont(self.ftitle_font)
            metrics_name = QFontMetrics(self.ftitle_font)
            name_w = metrics_name.horizontalAdvance(name)
            name_center_x = 1300
            name_x = name_center_x - (name_w // 2)
            if rank:
                spacing = 6
                rank_x = name_x - spacing - rank_w
                p.setFont(self.frank_font)
                p.drawText(rank_x, 790, rank_w, 50, Qt.AlignRight | Qt.AlignVCenter, rank)
            p.setFont(self.ftitle_font)
            p.drawText(name_x, 790, name_w, 45, Qt.AlignLeft | Qt.AlignVCenter, name)
            p.setOpacity(1.0)

    # -- CENTER SECTION -- #
        if self.state.center_rect_active:
            progress = self.state.center_rect_progress
            half_width1 = int((left_w + 600) / 2 * progress)
            rect1_x = left_x - 100 + ((left_w + 600) / 2 - half_width1)
            self.draw_normal_rect(p, rect1_x, 740, half_width1 * 2, 50, QColor("#191919"))
            half_width2 = int((left_w - 200) / 2 * progress)
            rect2_x = left_x + 290 + ((left_w - 200) / 2 - half_width2)
            self.draw_normal_rect(p, rect2_x, 990, half_width2 * 2, 35, QColor("#ffffff"))
            fade_delay = .7  # fraction of animation before fade starts (30%)
            if progress <= fade_delay:
                opacity = 0.0
            else:
                opacity = (progress - fade_delay) / (1.0 - fade_delay)
            opacity = min(max(opacity, 0.0), 1.0)  # clamp between 0 and 1
            p.setOpacity(opacity)
            p_num = self.state.period
            if p_num == 10:
                period_text = "Halftime"
            elif 1 <= p_num <= 4:
                period_text = f"{self.period_text()} Period"
            elif p_num == 5:
                period_text = "Overtime"
            elif 6 <= p_num <= 9:
                ot_number = p_num - 4
                period_text = f"{ot_number} Overtime"
            else:
                period_text = ""
            total_seconds = self.state.minutes_basketball * 60 + self.state.seconds_basketball + self.state.tenths_basketball / 10
            if total_seconds >= 60:
                tstring = f"{self.state.minutes_basketball:02d}:{self.state.seconds_basketball:02d}"
            else:
                tstring = f"{self.state.seconds_basketball}.{self.state.tenths_basketball}"
            p.setFont(self.bbperiod_font)
            p.setPen(Qt.black)
            p.drawText(cx + 68, cy + 120, cw, 45, Qt.AlignCenter, period_text)
            p.setFont(self.bbperiod_font)
            p.setPen(Qt.black)
            p.drawText(cx + 158, cy + 121, cw, 45, Qt.AlignCenter, tstring)
            triangle_w = 16
            triangle_h = 16
            triangle_x = cx + 130 + cw / 2 - triangle_w / 2
            triangle_y = cy + 142
            self.draw_right_triangle(p, triangle_x, triangle_y, triangle_w, triangle_h, QColor("black"))
            if self.state.upperbb_event_active:
                self.draw_upper_event_text(p, left_x+45, 745, self.state.upperbb_event_text_basketball) 
            p.setOpacity(1.0)
    def draw_basketball_scorebug(self, p):
    # -- KEY INFORMATION (DO NOT CHANGE W/O PROPER TESTING) -- #
        left_x = 600
        left_w = 260
        right_x = 999
        right_w = 260
        cx = 920
        cw = 80
        cy = 990
        tx = 887.5
        tw = 80
        ty = 990
        rw = self.state.away_record_wins
        rl = self.state.away_record_losses
        dw = self.state.away_district_wins
        dl = self.state.away_district_losses
        hw = self.state.home_record_wins
        hl = self.state.home_record_losses
        hdw = self.state.home_district_wins
        hdl = self.state.home_district_losses
        base_home = QColor(self.state.home_color).darker(160)
        base_away = QColor(self.state.away_color).darker(160)
        bg_away   = QColor(self.state.away_color).darker(160)
        if self.state.bottom_event_active:
            slide_progress = self.state.bottom_event_progress  # float from 0.0 to 1.0
            start_y = 970 + 20  # start below the box
            end_y = 970        # final resting position
            curr_y = start_y - (start_y - end_y) * slide_progress
            self.draw_normal_rect(p, left_x, curr_y, left_w + 480, 20, QColor("#191919"))
            self.draw_bottom_event_text(p, left_x + 45, curr_y, self.state.bottom_event_text_basketball)
    # -- AWAY SECTION -- #
        if self.state.away_box_active:
            progress=self.state.away_box_progress
            if self.state.away_box_direction==1:
                box_x=left_x+left_w-int(left_w*progress)
            else:
                box_x=left_x+int(left_w*(1-progress))
            curr_width=int(left_w*progress)
            inner1_width=int((left_w-255)*progress)
            inner2_width=int((left_w-185)*progress)
            self.draw_normal_rect(p,left_x+315,990,inner1_width,70,QColor("#ffffff"))
            inner2_x = left_x + 240 + (left_w - 185) - inner2_width  # anchor right, grow left
            self.draw_normal_rect(p, inner2_x, 990, inner2_width, 70, self.state.away_color)
            delay_progress = 0.5
            if progress >= delay_progress:
                delayed_progress = (progress - delay_progress) / (1.0 - delay_progress)
                curr_width = int(left_w * delayed_progress)
                if self.state.away_box_direction == 1:
                    box_x = left_x + left_w - curr_width
                else:
                    box_x = left_x + int(left_w * (1 - delayed_progress))
                self.draw_normal_rect(p, box_x, 990, curr_width-20, 70, base_away)
                self.draw_normal_rect(p, box_x, 990, curr_width-20, 48, self.state.away_color)
            fade_delay=.7
            if progress<=fade_delay:
                opacity=0.0
            else:
                opacity=(progress-fade_delay)/(1.0-fade_delay)
            opacity=min(max(opacity,0.0),1.0)
            p.setOpacity(opacity)
            rank,name=self.format_rank_name(self.state.away_rank,self.state.away_name)
            p.setPen(Qt.white)
            p.setFont(self.brank_font)
            metrics_rank=QFontMetrics(self.brank_font)
            rank_w=metrics_rank.horizontalAdvance(rank) if rank else 0
            p.setFont(self.title_font)
            metrics_name=QFontMetrics(self.title_font)
            name_w=metrics_name.horizontalAdvance(name)
            gap=6
            total_w=rank_w+(gap if rank else 0)+name_w
            rect_left=left_x+227
            block_right=rect_left-6
            block_left=block_right-total_w
            if rank:
                p.setFont(self.brank_font)
                p.drawText(block_left,986,rank_w,46,Qt.AlignLeft|Qt.AlignVCenter,rank)
            name_x=block_left+rank_w+(gap if rank else 0)
            p.setFont(self.title_font)
            p.drawText(name_x,993,name_w,26,Qt.AlignLeft|Qt.AlignVCenter,name)
            p.setFont(self.score_font)
            p.setPen(Qt.white)
            p.drawText(left_x+220,990,120,70,Qt.AlignCenter,str(self.state.away_pts))
            self.draw_basketball_timeout_rects(p,left_x+230,993,self.state.away_timeouts_basketball)
            p.setFont(self.record_font)
            p.setPen(Qt.white)
            font_metrics = QFontMetrics(p.font())
            text1 = f"{rw}-{rl}" if (rw != 0 or rl != 0) else ""
            text2 = f"({dw}-{dl})" if (dw != 0 or dl != 0) else ""
            if not text1 and not text2:
                pass
            elif text1 and not text2:
                p.drawText(left_x - 20, 1018.5, left_w - 20, 20, Qt.AlignRight | Qt.AlignVCenter, text1)
            elif text1 and text2:
                text2_width = font_metrics.horizontalAdvance(text2)
                text1_width = font_metrics.horizontalAdvance(text1)
                x1 = (left_x - 40) - text1_width - 5
                p.drawText(x1, 1018.5, left_w - 20, 20, Qt.AlignRight | Qt.AlignVCenter, text1)
                p.drawText(left_x - 20, 1017, left_w - 20, 20, Qt.AlignRight | Qt.AlignVCenter, text2)
            elif not text1 and text2:
                p.drawText(left_x - 20, 1017, left_w - 20, 20, Qt.AlignRight | Qt.AlignVCenter, text2)
            p.setOpacity(1.0)
        box_x = left_x + 240
        box_y = 990
        box_w = left_w - 185
        box_h = 70
        logo_w, logo_h = 70, 75
        logo_x = box_x + 6
        logo_y = box_y + (box_h - logo_h)//2
        t = self.state.away_logo_score_anim
        if t > 0:
            prog = 1 - t/18
            ease = 1 - pow(1 - prog, 3)
            mask_w = int(box_w * ease)
            jaggle_height = 4
            path = QPainterPath()
            path.moveTo(box_x + box_w, box_y)
            for i in range(mask_w):
                y_offset = math.sin(i * 0.3) * jaggle_height
                path.lineTo(box_x + box_w - i, box_y + y_offset)
            path.lineTo(box_x + box_w - mask_w, box_y + box_h)
            path.lineTo(box_x + box_w, box_y + box_h)
            path.closeSubpath()
            p.save()
            p.setClipPath(path)
            p.setOpacity(1.0)
            self.draw_normal_rect(p, box_x, box_y, box_w, box_h, self.state.away_color)
            p.setOpacity(ease)
            scale = 0.85 + 0.15 * ease
            p.translate(logo_x + logo_w/2, logo_y + logo_h/2)
            p.scale(scale, scale)
            p.translate(-logo_w/2, -logo_h/2)
            self.draw_logo_in_top_rounded_window(p, 0, 0, logo_w, logo_h, self.state.away_logo)
            p.restore()
            self.state.away_logo_score_anim -= 1
        if self.state.away_event_active or self.state.away_event_progress > 0:
            anchor_x = left_x
            offset = int(self.state.away_event_progress * left_w)
            rect_x = anchor_x - offset
            self.draw_normal_rect(p, rect_x, 990, offset, 70, self.state.away_color)
            self.draw_normal_rect(p, rect_x, 990, offset, 48, self.state.away_color)
            progress = self.state.away_event_progress
            alpha = 0.0
            if progress > 0.7:
                alpha = min((progress - 0.7) / 0.2, 1.0)
            p.save()
            p.setOpacity(alpha)
            self.draw_bbevent_text(p, rect_x + 65, 985, self.state.stat_upper_text)
            self.draw_bevent_text(p, rect_x + 65, 1020, self.state.away_event_text)
            p.restore()
            logo_w,logo_h=80,80
            logo_start_x=left_x-345
            logo_end_x=rect_x+15
            logo_x=int(logo_start_x+(logo_end_x-logo_start_x)*progress)
            logo_y=985
            p.save()
            p.setOpacity(alpha)
            self.clip_to_rect(p, rect_x, 990, offset, 70)
            self.draw_logo_in_top_rounded_window(p,logo_x,logo_y,logo_w,logo_h,self.state.away_logo)
            p.restore()
        if self.state.away_timeout_bar_timer>0 and self.state.away_timeout_text:
            TOTAL=150
            ANIM=30
            FADE_IN=15
            FADE_OUT=30
            t=self.state.away_timeout_bar_timer
            if t>TOTAL-ANIM:progress=(TOTAL-t)/ANIM
            elif t>ANIM:progress=1.0
            else:progress=t/ANIM
            progress=max(0.0,min(progress,1.0))
            anim_w=int(left_w*progress)
            bar_x=left_x-260+left_w-anim_w
            self.draw_normal_rect(p,bar_x,990,anim_w,70,self.state.away_color)
            self.draw_normal_rect(p,bar_x,990,anim_w,48,self.state.away_color)
            base_x=left_x-276
            off_x=left_x-345
            draw_x=int(off_x+(base_x-off_x)*progress)
            if t>TOTAL-ANIM-FADE_IN:alpha=(TOTAL-ANIM-t)/FADE_IN
            elif t>ANIM+FADE_OUT:alpha=1.0
            elif t>ANIM:alpha=(t-ANIM)/FADE_OUT
            else: alpha=0.0
            alpha=max(0.0,min(alpha,1.0))
            if alpha>0 and self.state.away_logo:
                logo_w,logo_h=80,80
                logo_start_x=left_x-345
                logo_end_x=bar_x+15
                logo_x=int(logo_start_x+(logo_end_x-logo_start_x)*progress)
                logo_y=985
                p.save()
                p.setOpacity(alpha)
                self.clip_to_rect(p, bar_x, 990, anim_w, 70)
                self.draw_logo_in_top_rounded_window(p,logo_x,logo_y,logo_w,logo_h,self.state.away_logo)
                p.restore()
                p.save()
                p.setOpacity(alpha)
                self.draw_timeout_popup(p,draw_x+85,1005,self.state.away_timeout_text)
                p.restore()
            self.state.away_timeout_bar_timer-=1


    # -- HOME SECTION -- #
        if self.state.right_box_active:
            curr_width = int(260 * self.state.right_box_progress)
            self.draw_normal_rect(p, right_x+80, 990, curr_width, 70, base_home)
            self.draw_normal_rect(p, 999+80, 990, curr_width, 48, self.state.home_color)
            inner_width1 = int((260 - 255) * self.state.right_box_progress)
            inner_width2 = int((260 - 185) * self.state.right_box_progress)
            self.draw_normal_rect(p, 999, 990, inner_width1, 70, QColor("#ffffff"))
            self.draw_normal_rect(p, 999 + 5, 990, inner_width2, 70, self.state.home_color)
            progress = self.state.right_box_progress
            fade_delay = 0.7
            if progress <= fade_delay:
                opacity = 0.0
            else:
                opacity = (progress - fade_delay) / (1.0 - fade_delay)
            opacity = min(max(opacity, 0.0), 1.0)
            p.setOpacity(opacity)
            self.draw_basketball_timeout_rects(p, 999 + 85, 993, self.state.home_timeouts_basketball)
            p.setFont(self.score_font)
            p.setPen(Qt.white)
            p.drawText(right_x- 90, 990, curr_width, 70, Qt.AlignCenter, str(self.state.home_pts))
            rank,name=self.format_rank_name(self.state.home_rank,self.state.home_name)
            max_width=250
            gap=6
            p.setFont(self.brank_font)
            metrics_rank=QFontMetrics(self.brank_font)
            rank_w=metrics_rank.horizontalAdvance(rank)if rank else 0
            available_name_w=max_width-rank_w-(gap if rank else 0)
            if available_name_w<0:available_name_w=0
            name_font=QFont(self.title_font)
            metrics_name=QFontMetrics(name_font)
            name_w=metrics_name.horizontalAdvance(name)
            while name_w>available_name_w and name_font.pointSize()>6:
                name_font.setPointSize(name_font.pointSize()-1)
                metrics_name=QFontMetrics(name_font)
                name_w=metrics_name.horizontalAdvance(name)
            rect_right=999+195+(curr_width-360)
            block_left=rect_right+6
            if rank:
                p.setFont(self.brank_font)
                p.setPen(Qt.white)
                p.drawText(block_left,995,rank_w,26,Qt.AlignLeft|Qt.AlignVCenter,rank)
            name_x=block_left+rank_w+(gap if rank else 0)
            p.setFont(name_font)
            p.drawText(name_x,983,name_w,46,Qt.AlignLeft|Qt.AlignVCenter,name)
            p.setFont(self.record_font)
            p.setPen(Qt.white)
            font_metrics = QFontMetrics(p.font())
            if not (hw == 0 and hl == 0):
                text1 = f"{hw}-{hl}"
                x1 = 999 + 100
                y1 = 1018.5
                p.drawText(x1, y1, curr_width - 20, 20, Qt.AlignLeft | Qt.AlignVCenter, text1)
                text1_width = font_metrics.horizontalAdvance(text1)
            else:
                text1_width = 0  # so second text starts at the fixed base if first doesn't exist
            if not (hdw == 0 and hdl == 0):
                text2 = f"({hdw}-{hdl})"
                x2 = 999 + 100 + text1_width + 5  # dynamic, accounts for first text width
                y2 = 1017
                p.drawText(x2, y2, curr_width - 20, 20, Qt.AlignLeft | Qt.AlignVCenter, text2)
            p.setOpacity(1.0)
        if self.state.home_event_active or self.state.home_event_progress > 0:
            anchor_x = right_x + 340
            offset = int(self.state.home_event_progress * right_w)
            self.draw_normal_rect(p, anchor_x, 990, offset, 70, self.state.home_color)
            self.draw_normal_rect(p, anchor_x, 990, offset, 48, self.state.home_color)
            progress = self.state.home_event_progress
            alpha = 0.0
            if progress > 0.7:
                alpha = min((progress - 0.7) / 0.2, 1.0)
            p.save()
            p.setOpacity(alpha)
            self.draw_bbevent_text(p, anchor_x-45, 985, self.state.stat_home_upper_text)
            self.draw_bevent_text(p, anchor_x -40, 1020, self.state.home_event_text)
            p.restore()
            anim_w=int(right_w*progress)
            bar_x=right_x+340
            logo_w,logo_h=80,80
            logo_start_x=right_x+285
            logo_end_x=bar_x+175
            logo_x=int(logo_start_x+(logo_end_x-logo_start_x)*progress)
            logo_y=985
            p.save()
            p.setOpacity(alpha)
            self.clip_to_rect(p, bar_x, 990, anim_w, 70)
            self.draw_logo_in_top_rounded_window(p,logo_x,logo_y,logo_w,logo_h,self.state.home_logo)
            p.restore()
        if self.state.home_timeout_bar_timer>0 and self.state.home_timeout_text:
            TOTAL=150
            ANIM=30
            FADE_IN=15
            FADE_OUT=30
            t=self.state.home_timeout_bar_timer
            if t>TOTAL-ANIM:progress=(TOTAL-t)/ANIM
            elif t>ANIM:progress=1.0
            else:progress=t/ANIM
            progress=max(0.0,min(progress,1.0))
            anim_w=int(right_w*progress)
            bar_x=right_x+340
            self.draw_normal_rect(p,bar_x,990,anim_w,70,self.state.home_color)
            self.draw_normal_rect(p,bar_x,990,anim_w,48,self.state.home_color)
            base_x=right_x+346
            off_x=right_x+285
            draw_x=int(off_x+(base_x-off_x)*progress)
            if t>TOTAL-ANIM-FADE_IN:alpha=(TOTAL-ANIM-t)/FADE_IN
            elif t>ANIM+FADE_OUT:alpha=1.0
            elif t>ANIM:alpha=(t-ANIM)/FADE_OUT
            else:alpha=0.0
            alpha=max(0.0,min(alpha,1.0))
            if alpha>0 and self.state.home_logo:
                logo_w,logo_h=80,80
                logo_start_x=right_x+285
                logo_end_x=bar_x+175
                logo_x=int(logo_start_x+(logo_end_x-logo_start_x)*progress)
                logo_y=985
                p.save()
                p.setOpacity(alpha)
                self.clip_to_rect(p, bar_x, 990, anim_w, 70)
                self.draw_logo_in_top_rounded_window(p,logo_x,logo_y,logo_w,logo_h,self.state.home_logo)
                p.restore()
                p.save()
                p.setOpacity(alpha)
                self.draw_timeout_popup(p,draw_x-50,1005,self.state.home_timeout_text)
                p.restore()
            self.state.home_timeout_bar_timer-=1

        box_x = right_x + 5
        box_y = 990
        box_w = right_w - 185
        box_h = 70
        logo_w, logo_h = 70, 75
        logo_x = box_x + box_w - logo_w - 6
        logo_y = box_y + (box_h - logo_h)//2
        t = self.state.home_logo_score_anim
        if t > 0:
            prog = 1 - t/18
            ease = 1 - pow(1 - prog, 3)
            mask_w = int(box_w * ease)
            jaggle_height = 4
            path = QPainterPath()
            path.moveTo(box_x, box_y)
            for i in range(mask_w):
                y_offset = math.sin(i * 0.3) * jaggle_height
                path.lineTo(box_x + i, box_y + y_offset)
            path.lineTo(box_x + mask_w, box_y + box_h)
            path.lineTo(box_x, box_y + box_h)
            path.closeSubpath()
            p.save()
            p.setClipPath(path)
            p.setOpacity(1.0)
            self.draw_normal_rect(p, box_x, box_y, box_w, box_h, self.state.home_color)
            p.setOpacity(ease)
            scale = 0.85 + 0.15 * ease
            p.translate(logo_x + logo_w/2, logo_y + logo_h/2)
            p.scale(scale, scale)
            p.translate(-logo_w/2, -logo_h/2)
            self.draw_logo_in_top_rounded_window(p, 0, 0, logo_w, logo_h, self.state.home_logo)
            p.restore()
            self.state.home_logo_score_anim -= 1
            #if self.state.bottom_event_active:
                #self.draw_transparentnormal_rect(p, left_x, 970, left_w + 480, 20, QColor("#191919"))
                #self.draw_bottom_event_text(p, left_x + 45, 970, self.state.bottom_event_text_basketball)

    # -- CENTER SECTION -- #
        if self.state.scenter_scorebug_active:
            current_width = int(cw * self.state.scenter_scorebug_progress)
            rect_x = cx + (cw // 2) - (current_width // 2)  # keep expanding from center of the space
            rect_width = current_width
            self.draw_normal_rect(p, rect_x, cy, rect_width, 70, QColor("#191919"))
            fade_delay = .7  # fraction of animation before fade starts (30%)
            progress = self.state.scenter_scorebug_progress
            if progress <= fade_delay:
                opacity = 0.0
            else:
                opacity = (progress - fade_delay) / (1.0 - fade_delay)
            opacity = min(max(opacity, 0.0), 1.0)  # clamp between 0 and 1
            p.setOpacity(opacity) # applies to all drawing after this
            p.setFont(self.timer_font)
            p.setPen(Qt.white)
            total_seconds = self.state.minutes_basketball * 60 + self.state.seconds_basketball + self.state.tenths_basketball / 10
            if total_seconds >= 60:
                tstring = f"{self.state.minutes_basketball:02d}:{self.state.seconds_basketball:02d}"
            else:
                tstring = f"{self.state.seconds_basketball}.{self.state.tenths_basketball}"
            p.drawText(cx, cy-7, tw, 60, Qt.AlignCenter, tstring)
            p.setFont(self.period_font)
            p.setPen(Qt.white)
            p.drawText(cx, cy + 40, cw, 26, Qt.AlignCenter, f"{self.period_text()}")
            p.setOpacity(1.0)

        if self.state.possession == 'away':
            self.draw_possession_text(p, left_x+200, 1053, QColor("#ffffff"))
        elif self.state.possession == 'home':
            self.draw_possession_text(p, right_x+85, 1053, QColor("#ffffff"))
# -- FOULS/BONUS SECTION -- #
        p.setFont(self.fouls_font)
        p.setPen(Qt.white)
        hf = self.state.home_fouls
        if hf == 0:
            pass  # draw nothing
        elif hf >= 5:
            p.setFont(self.fouls_font)
            p.setPen(QColor("white"))
            p.drawText(left_x + 90, 1043, 80, 20, Qt.AlignLeft, "BONUS")
        else:
            p.setFont(self.fouls_font)
            p.setPen(Qt.white)
            p.drawText(right_x + 270, 1043, 80, 20, Qt.AlignLeft, f"Fouls: {hf}")
        af = self.state.away_fouls
        if af == 0:
            pass  # draw nothing
        elif af >= 5:
            p.setFont(self.fouls_font)
            p.setPen(QColor("white"))
            p.drawText(right_x + 200, 1043, 80, 20, Qt.AlignLeft, "BONUS")
        else:
            p.setFont(self.fouls_font)
            p.setPen(Qt.white)
            p.drawText(left_x + 5, 1043, 80, 20, Qt.AlignLeft, f"Fouls: {af}")
    def draw_basketball_final(self, p):
        left_x = 550
        left_w = 400
        right_x = 950
        right_w = 400
        cx = 750
        cw = 175
        cy = 865
        base_home = QColor(self.state.home_color).darker(160)
        bg_home   = QColor(self.state.home_color).darker(160)
        base_away = QColor(self.state.away_color).darker(160)
        bg_away   = QColor(self.state.away_color).darker(160)
        rw = self.state.away_record_wins
        rl = self.state.away_record_losses
        dw = self.state.away_district_wins
        dl = self.state.away_district_losses
        hw = self.state.home_record_wins
        hl = self.state.home_record_losses
        hdw = self.state.home_district_wins
        hdl = self.state.home_district_losses
    # -- AWAY SECTION -- #
        if self.state.fleft_break_box_active:
            progress = self.state.fleft_break_box_progress
            curr_width1 = int((left_w + 100) * progress)
            curr_width2 = int(left_w * progress)
            self.draw_normal_rect(p, left_x + left_w - curr_width1, 790, curr_width1, 200, base_away)
            self.draw_normal_rect(p, left_x + 200 + left_w - curr_width2, 790, curr_width2, 200, self.state.away_color)
            fade_delay = .7  # fraction of animation before fade starts (30%)
            if progress <= fade_delay:
                opacity = 0.0
            else:
                opacity = (progress - fade_delay) / (1.0 - fade_delay)
            opacity = min(max(opacity, 0.0), 1.0)  # clamp between 0 and 1
            p.setOpacity(opacity)
            logo_x = left_x + 200
            logo_y = 780
            logo_w = 200
            logo_h = 206
            p.save()
            self.clip_to_rounded_rect(p, left_x + 200 + left_w - curr_width2, 790, curr_width2, 200)
            self.draw_logo_in_top_rounded_window(p, logo_x, logo_y, logo_w, logo_h, self.state.away_logo)
            p.restore()
            rank, name = self.format_rank_name(self.state.away_rank, self.state.away_name)
            p.setPen(Qt.white)
            p.setFont(self.frank_font)
            metrics_rank = QFontMetrics(self.frank_font)
            rank_w = metrics_rank.horizontalAdvance(rank) if rank else 0
            p.setFont(self.ftitle_font)
            metrics_name = QFontMetrics(self.ftitle_font)
            name_w = metrics_name.horizontalAdvance(name)
            name_center_x = 600
            name_x = name_center_x - (name_w // 2)
            if rank:
                spacing = 6
                rank_x = name_x - spacing - rank_w
                p.setFont(self.frank_font)
                p.drawText(rank_x, 790, rank_w, 50, Qt.AlignRight | Qt.AlignVCenter, rank)
            p.setFont(self.ftitle_font)
            p.drawText(name_x, 790, name_w, 45, Qt.AlignLeft | Qt.AlignVCenter, name)
            p.setFont(self.frank_font)
            p.setPen(Qt.white)
            if not (rw == 0 and rl == 0):
                p.drawText(560, 768.5, curr_width1 - 20, 150, Qt.AlignLeft | Qt.AlignVCenter, f"{rw}-{rl}")
            if not (dw == 0 and dl == 0):
                p.drawText(600, 767.5, curr_width1 - 20, 150, Qt.AlignLeft | Qt.AlignVCenter, f"({dw}-{dl})")
            p.setFont(self.fscore_font)
            p.setPen(Qt.white)
            p.drawText(left_x - 65, 810, 220, 215, Qt.AlignCenter, str(self.state.away_pts))
            p.setOpacity(1.0)

    # -- HOME SECTION -- #
        if self.state.fright_break_box_active:
            progress = self.state.fright_break_box_progress
            curr_width = int(right_w * progress)
            self.draw_normal_rect(p, right_x, 790, int((right_w+100)*progress), 200, base_home)
            self.draw_normal_rect(p, right_x, 790, int((right_w-200)*progress), 200, self.state.home_color)
            fade_delay = .7  # fraction of animation before fade starts (30%)
            if progress <= fade_delay:
                opacity = 0.0
            else:
                opacity = (progress - fade_delay) / (1.0 - fade_delay)
            opacity = min(max(opacity, 0.0), 1.0)  # clamp between 0 and 1
            p.setOpacity(opacity)
            logo_x = right_x
            logo_y = 780
            logo_w = 200
            logo_h = 206
            p.save()
            self.clip_to_rounded_rect(p, right_x, 790, int((right_w-205)*progress), 200)
            self.draw_logo_in_top_rounded_window(p, logo_x, logo_y, logo_w, logo_h, self.state.home_logo)
            p.restore()
            p.setFont(self.frank_font)
            p.setPen(Qt.white)
            if not (hw == 0 and hl == 0):
                p.drawText(1254, 768.5, curr_width - 20, 150, Qt.AlignLeft | Qt.AlignVCenter, f"{hw}-{hl}")
            if not (hdw == 0 and hdl == 0):
                p.drawText(1294, 767.5, curr_width - 20, 150, Qt.AlignLeft | Qt.AlignVCenter, f"({hdw}-{hdl})")

            p.setFont(self.fscore_font)
            p.setPen(Qt.white)
            p.drawText(right_x + 235, 810, 220, 215, Qt.AlignCenter, str(self.state.home_pts))
            
            rank, name = self.format_rank_name(self.state.home_rank, self.state.home_name)
            p.setPen(Qt.white)
            p.setFont(self.frank_font)
            metrics_rank = QFontMetrics(self.frank_font)
            rank_w = metrics_rank.horizontalAdvance(rank) if rank else 0
            p.setFont(self.ftitle_font)
            metrics_name = QFontMetrics(self.ftitle_font)
            name_w = metrics_name.horizontalAdvance(name)
            name_center_x = 1300
            name_x = name_center_x - (name_w // 2)
            if rank:
                spacing = 6
                rank_x = name_x - spacing - rank_w
                p.setFont(self.frank_font)
                p.drawText(rank_x, 790, rank_w, 50, Qt.AlignRight | Qt.AlignVCenter, rank)
            p.setFont(self.ftitle_font)
            p.drawText(name_x, 790, name_w, 45, Qt.AlignLeft | Qt.AlignVCenter, name)
            p.setOpacity(1.0)

    # -- CENTER SECTION -- #
        if self.state.fcenter_rect_active:
            progress = self.state.fcenter_rect_progress
            half_width1 = int((left_w + 600) / 2 * progress)
            rect1_x = left_x - 100 + ((left_w + 600) / 2 - half_width1)
            self.draw_normal_rect(p, rect1_x, 740, half_width1 * 2, 50, QColor("#191919"))
            half_width2 = int((left_w - 200) / 2 * progress)
            rect2_x = left_x + 290 + ((left_w - 200) / 2 - half_width2)
            self.draw_normal_rect(p, rect2_x, 990, half_width2 * 2, 35, QColor("#ffffff"))
            fade_delay = .7  # fraction of animation before fade starts (30%)
            if progress <= fade_delay:
                opacity = 0.0
            else:
                opacity = (progress - fade_delay) / (1.0 - fade_delay)
            opacity = min(max(opacity, 0.0), 1.0)  # clamp between 0 and 1
            period = self.state.period
            if period >= 5 and period <= 9:
                self.state.last_ot_period = period
            elif period <= 4:
                if not hasattr(self.state, "last_ot_period"):
                    self.state.last_ot_period = None
            if period <= 4:
                self.state.final_text = "FINAL"
            elif period == 5:
                self.state.final_text = "FINAL/OT"
            elif 6 <= period <= 9:
                self.state.final_text = f"FINAL/{period - 4} OT"
            elif period == 11:
                last_ot = getattr(self.state, "last_ot_period", None)
                if last_ot is None or last_ot <= 4:
                    self.state.final_text = "FINAL"
                elif last_ot == 5:
                    self.state.final_text = "FINAL/OT"
                else:
                    self.state.final_text = f"FINAL/{last_ot - 4} OT"
            else:
                self.state.final_text = "FINAL"
            p.setFont(self.final_font)
            p.setPen(Qt.black)
            p.drawText(cx + 108, cy + 120, cw, 45, Qt.AlignCenter, self.state.final_text)
            if self.state.upperbb_event_active:
                self.draw_upper_event_text(p, left_x+45, 745, self.state.upperbb_event_text_basketball) 
            p.setOpacity(1.0)
            p.end()
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self._drag_pos
            self.window().move(self.window().pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
class BasketballControl(QMainWindow):
    BUTTON_STYLE = "background-color:white; color:black;"
    DARK_LABEL_STYLE = "QPushButton { background-color: #121212; color: white; }"
    def make_button(self, text, slot=None, style=None):
        btn = QPushButton(text)
        if style is None:
            style = self.BUTTON_STYLE
        btn.setStyleSheet(style)
        if slot:
            btn.clicked.connect(slot)
        return btn
    def make_label_button(self, text):
        return self.make_button(text,lambda: None,self.DARK_LABEL_STYLE)
    def make_lcd(self, digits, value=None):
        lcd = QLCDNumber()
        lcd.setDigitCount(digits)
        lcd.setSegmentStyle(QLCDNumber.Flat)
        lcd.setStyleSheet("""
            QLCDNumber {
                color: white;
                background-color: black;
                border: 2px solid #333;
                padding: 2px;
            }
        """)
        if value is not None:
            lcd.display(value)
        return lcd
    def make_spinbox(self,minimum,maximum,value,width=None,hidden=False):
        spin = QSpinBox()
        spin.setRange(minimum, maximum)
        spin.setValue(value)
        spin.setStyleSheet(self.BUTTON_STYLE)
        if width:
            spin.setFixedWidth(width)
        if hidden:
            spin.hide()
        return spin
    def create_points_combo(self, text, values, team):
        combo = QComboBox()
        combo.setStyleSheet(self.BUTTON_STYLE)
        combo.addItem(text)
        for value in values:
            combo.addItem(str(value))
        def on_changed(index):
            if index == 0:
                return
            points = int(combo.currentText())
            self.add_points(points, team)
            combo.setCurrentIndex(0)
        combo.currentIndexChanged.connect(on_changed)
        return combo
    def create_action_combo(self, placeholder, items, callback):
        combo = QComboBox()
        combo.setStyleSheet(self.BUTTON_STYLE)
        combo.addItem(placeholder)
        for item in items:
            combo.addItem(item)
        def on_changed(index):
            if index == 0:
                return
            callback(combo.currentText())
            combo.setCurrentIndex(0)
        combo.currentIndexChanged.connect(on_changed)
        return combo
    def make_team_score_display(self, value):
        spin = self.make_spinbox(0,999,value,hidden=True)
        lcd = self.make_lcd(3)
        lcd.setFixedWidth(240)
        lcd.setFixedHeight(60)
        lcd.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        spin.valueChanged.connect(lcd.display)
        return spin, lcd
    def make_timeout_display(self, value):
        lcd = self.make_lcd(1, value)
        return lcd
    def __init__(self, state: ScoreState, scoreboard: BasketballScoreboard):
        super().__init__()
        self.state = state
        self.ui_timer = QTimer(self)
        self.ui_timer.timeout.connect(self.ui_tick)
        self.ui_timer.start(100)
        self.timer = QTimer(self)  # must exist before you call setInterval
        self.timer.timeout.connect(self.game_tick)
        self.timer.stop()
        self.scoreboard = scoreboard
        version = beta_version if beta_mode else current_version

        self.setWindowTitle(
            f"Basketball Scoreboard Control (Version: {version}"
            f"{' - BETA' if beta_mode else ''})"
        )        
        self.setMinimumSize(720, 520)

        # Tab widget as central
        tabs = QTabWidget()
        self.setCentralWidget(tabs)

        page1 = QWidget()
        tabs.addTab(page1, "Game Info Setup")
        grid_info = QGridLayout()
        page1.setStyleSheet("background-color: #121212;")
        page1.setLayout(grid_info)

        page2 = QWidget()
        tabs.addTab(page2, "Main Controls")
        grid = QGridLayout()
        page2.setStyleSheet("background-color: #121212;")
        page2.setLayout(grid)

        # Page 2 — Away Setup
        page3 = QWidget()
        tabs.addTab(page3, "Away Setup")
        grid_away = QGridLayout()
        page3.setStyleSheet("background-color: #121212;")
        page3.setLayout(grid_away)

        # Page 3 — Home Setup
        page4 = QWidget()
        tabs.addTab(page4, "Home Setup")
        grid_home = QGridLayout()
        page4.setStyleSheet("background-color: #121212;")
        page4.setLayout(grid_home)
        

        # ----------------- PAGE 1 CONTENT (kept same layout) -----------------
        btn_nothing = QPushButton("Home Team")
        btn_nothing.clicked.connect(lambda: None)
        btn_nothing.setStyleSheet("QPushButton { background-color: #121212; color: white; }")
        grid.addWidget(btn_nothing, 0, 4, 1, 3)
        btn_nothing = QPushButton("Away Team")
        btn_nothing.clicked.connect(lambda: None)
        btn_nothing.setStyleSheet("QPushButton { background-color: #121212; color: white; }")
        grid.addWidget(btn_nothing, 0, 0, 1, 3)
        btn_serial = QPushButton("Serial Connection")
        btn_serial.setStyleSheet("background-color:white; color:black;")
        btn_serial.clicked.connect(self.on_serial_button_clicked)
        grid.addWidget(btn_serial, 12, 5)
        self.home_foul_label = QLabel("              0")
        self.home_foul_label.setStyleSheet("color:white;")
        grid.addWidget(self.home_foul_label, 11, 5)
        btn_home_foul_add = QPushButton("+")
        btn_home_foul_add.setStyleSheet("background-color:white; color:black;")
        btn_home_foul_add.clicked.connect(lambda: self.change_fouls("home", +1))
        grid.addWidget(btn_home_foul_add, 11, 4)
        btn_home_foul_sub = QPushButton("-")
        btn_home_foul_sub.setStyleSheet("background-color:white; color:black;")
        btn_home_foul_sub.clicked.connect(lambda: self.change_fouls("home", -1))
        grid.addWidget(btn_home_foul_sub, 11, 6)
        lbl_away_fouls = QLabel("      Team Fouls")
        lbl_away_fouls.setStyleSheet("color:white;")
        grid.addWidget(lbl_away_fouls, 11, 3)
        lbl_away_fouls = QLabel("       3 Pointers")
        lbl_away_fouls.setStyleSheet("color:white;")
        grid.addWidget(lbl_away_fouls, 10, 3)
        lbl_away_fouls = QLabel("     Free Throws")
        lbl_away_fouls.setStyleSheet("color:white;")
        grid.addWidget(lbl_away_fouls, 9, 3)
        lbl_away_fouls = QLabel("     Timeouts")
        lbl_away_fouls.setStyleSheet("color:white;")
        grid.addWidget(lbl_away_fouls, 7, 3)
        self.away_foul_label = QLabel("              0")
        self.away_foul_label.setStyleSheet("color:white;")
        grid.addWidget(self.away_foul_label, 11, 1)
        btn_away_foul_add = QPushButton("+")
        btn_away_foul_add.setStyleSheet("background-color:white; color:black;")
        btn_away_foul_add.clicked.connect(lambda: self.change_fouls("away", +1))
        grid.addWidget(btn_away_foul_add, 11, 0)
        btn_away_foul_sub = QPushButton("-")
        btn_away_foul_sub.setStyleSheet("background-color:white; color:black;")
        btn_away_foul_sub.clicked.connect(lambda: self.change_fouls("away", -1))
        grid.addWidget(btn_away_foul_sub, 11, 2)
        self.away_to_lcd = QLCDNumber()
        self.away_to_lcd.setDigitCount(1)
        self.away_to_lcd.setSegmentStyle(QLCDNumber.Flat)
        self.away_to_lcd.display(self.state.away_timeouts_basketball)
        self.away_to_lcd.setStyleSheet("""QLCDNumber { color: white;background-color: black;border: 2px solid #333;padding: 2px;}""")
        grid.addWidget(self.away_to_lcd, 7, 1)
        btn_away_use = QPushButton("-")
        btn_away_use.setStyleSheet("background-color:white; color:black;")
        btn_away_use.clicked.connect(lambda: self.change_timeout("away", -1))
        grid.addWidget(btn_away_use, 7, 0)
        btn_away_restore = QPushButton("+")
        btn_away_restore.setStyleSheet("background-color:white; color:black;")
        btn_away_restore.clicked.connect(lambda: self.change_timeout("away", +1))
        grid.addWidget(btn_away_restore, 7, 2)
        self.home_to_lcd = QLCDNumber()
        self.home_to_lcd.setDigitCount(1)
        self.home_to_lcd.setSegmentStyle(QLCDNumber.Flat)
        self.home_to_lcd.display(self.state.home_timeouts_basketball)
        self.home_to_lcd.setStyleSheet("""QLCDNumber { color: white;background-color: black;border: 2px solid #333;padding: 2px;}""")
        grid.addWidget(self.home_to_lcd, 7, 5)
        btn_home_use = QPushButton("-")
        btn_home_use.setStyleSheet("background-color:white; color:black;")
        btn_home_use.clicked.connect(lambda: self.change_timeout("home", -1))
        grid.addWidget(btn_home_use, 7, 4)
        btn_home_restore = QPushButton("+")
        btn_home_restore.setStyleSheet("background-color:white; color:black;")
        btn_home_restore.clicked.connect(lambda: self.change_timeout("home", +1))
        grid.addWidget(btn_home_restore, 7, 6)
        self.aw_score_box = QSpinBox()
        self.aw_score_box.setRange(0, 999)
        self.aw_score_box.setValue(self.state.away_pts)
        self.aw_score_box.hide()    # <--- hide it from UI
        self.aw_lcd = QLCDNumber()
        self.aw_lcd.setDigitCount(3)
        self.aw_lcd.setSegmentStyle(QLCDNumber.Flat)
        self.aw_lcd.setStyleSheet("""QLCDNumber { color: white;background-color: black;border: 2px solid #333;padding: 4px;}""")
        self.aw_lcd.setFixedWidth(240)
        self.aw_lcd.setFixedHeight(60)
        self.aw_lcd.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        grid.addWidget(self.aw_lcd, 3, 0, 1, 3)
        self.aw_score_box.valueChanged.connect(self.aw_lcd.display)
        self.hm_score_box = QSpinBox()
        self.hm_score_box.setRange(0, 999)
        self.hm_score_box.setValue(self.state.home_pts)
        self.hm_score_box.setStyleSheet("background-color:white; color:black;")
        self.hm_score_box.hide()
        grid.addWidget(self.hm_score_box, 2, 5)
        self.hm_lcd = QLCDNumber()
        self.hm_lcd.setDigitCount(3)
        self.hm_lcd.setSegmentStyle(QLCDNumber.Flat)
        self.hm_lcd.setStyleSheet("""QLCDNumber { color: white;background-color: black;border: 2px solid #333;padding: 4px;}""")
        self.hm_lcd.setFixedWidth(240)
        self.hm_lcd.setFixedHeight(60)
        self.hm_lcd.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        grid.addWidget(self.hm_lcd, 3, 4, 1, 3)
        self.hm_score_box.valueChanged.connect(self.hm_lcd.display)
        btn_away_plus3 = QPushButton("+3")
        btn_away_plus3.setStyleSheet("background-color:white; color:black;")
        btn_away_plus3.clicked.connect(lambda: self.add_points(3, "away"))
        grid.addWidget(btn_away_plus3, 1, 0, 1, 1)
        btn_away_plus2 = QPushButton("+2")
        btn_away_plus2.setStyleSheet("background-color:white; color:black;")
        btn_away_plus2.clicked.connect(lambda: self.add_points(2, "away"))
        grid.addWidget(btn_away_plus2, 1, 1, 1, 1)
        btn_away_plus1 = QPushButton("+1")
        btn_away_plus1.setStyleSheet("background-color:white; color:black;")
        btn_away_plus1.clicked.connect(lambda: self.add_points(1, "away"))
        grid.addWidget(btn_away_plus1, 1, 2, 1, 1)
        btn_away_minus3 = QPushButton("-3")
        btn_away_minus3.setStyleSheet("background-color:white; color:black;")
        btn_away_minus3.clicked.connect(lambda: self.add_points(-3, "away"))
        grid.addWidget(btn_away_minus3, 4, 0, 1, 1)
        btn_away_minus2 = QPushButton("-2")
        btn_away_minus2.setStyleSheet("background-color:white; color:black;")
        btn_away_minus2.clicked.connect(lambda: self.add_points(-2, "away"))
        grid.addWidget(btn_away_minus2, 4, 1, 1, 1)
        btn_away_minus1 = QPushButton("-1")
        btn_away_minus1.setStyleSheet("background-color:white; color:black;")
        btn_away_minus1.clicked.connect(lambda: self.add_points(-1, "away"))
        grid.addWidget(btn_away_minus1, 4, 2, 1, 1)
        btn_home_plus3 = QPushButton("+3")
        btn_home_plus3.setStyleSheet("background-color:white; color:black;")
        btn_home_plus3.clicked.connect(lambda: self.add_points(3, "home"))
        grid.addWidget(btn_home_plus3, 1, 4, 1, 1)
        btn_home_plus2 = QPushButton("+2")
        btn_home_plus2.setStyleSheet("background-color:white; color:black;")
        btn_home_plus2.clicked.connect(lambda: self.add_points(2, "home"))
        grid.addWidget(btn_home_plus2, 1, 5, 1, 1)
        btn_home_plus1 = QPushButton("+1")
        btn_home_plus1.setStyleSheet("background-color:white; color:black;")
        btn_home_plus1.clicked.connect(lambda: self.add_points(1, "home"))
        grid.addWidget(btn_home_plus1, 1, 6, 1, 1)
        btn_home_minus3 = QPushButton("-3")
        btn_home_minus3.setStyleSheet("background-color:white; color:black;")
        btn_home_minus3.clicked.connect(lambda: self.add_points(-3, "home"))
        grid.addWidget(btn_home_minus3, 4, 4, 1, 1)
        btn_home_minus2 = QPushButton("-2")
        btn_home_minus2.setStyleSheet("background-color:white; color:black;")
        btn_home_minus2.clicked.connect(lambda: self.add_points(-2, "home"))
        grid.addWidget(btn_home_minus2, 4, 5, 1, 1)
        btn_home_minus1 = QPushButton("-1")
        btn_home_minus1.setStyleSheet("background-color:white; color:black;")
        btn_home_minus1.clicked.connect(lambda: self.add_points(-1, "home"))
        grid.addWidget(btn_home_minus1, 4, 6, 1, 1)

        btn_poss_none = QPushButton("None")
        btn_poss_none.setStyleSheet("background-color:white; color:black;")
        btn_poss_none.clicked.connect(lambda: self.set_possession_direct(None))
        grid.addWidget(btn_poss_none, 5, 3)
        btn_poss_away = QPushButton("Away")
        btn_poss_away.setStyleSheet("background-color:white; color:black;")
        btn_poss_away.clicked.connect(lambda: self.set_possession_direct("away"))
        grid.addWidget(btn_poss_away, 5, 0, 1, 3)
        btn_poss_home = QPushButton("Home")
        btn_poss_home.setStyleSheet("background-color:white; color:black;")
        btn_poss_home.clicked.connect(lambda: self.set_possession_direct("home"))
        grid.addWidget(btn_poss_home, 5, 4 , 1, 3)
        self.period_spin = QSpinBox()
        self.period_spin.setRange(1, 12)
        self.period_spin.setValue(self.state.period)
        self.period_spin.setStyleSheet("background-color:white; color:black;")
        grid.addWidget(self.period_spin, 12, 0)
        btn_set_periodb = QPushButton("Set Period")
        btn_set_periodb.setStyleSheet("background-color:white; color:black;")
        btn_set_periodb.clicked.connect(self.set_periodb)
        grid.addWidget(btn_set_periodb, 12, 1)
        self.time_lcd = QLCDNumber()
        self.time_lcd.setDigitCount(5)  # MM:SS
        self.time_lcd.setSegmentStyle(QLCDNumber.Flat)
        self.time_lcd.display(f"{self.state.minutes_basketball:02d}:{self.state.seconds_basketball:02d}")
        self.time_lcd.setStyleSheet("""QLCDNumber { color: white;background-color: black;border: 2px solid #333;padding: 4px;}""")
        grid.addWidget(self.time_lcd, 8, 1, 1, 1)
        self.min_edit = QSpinBox()
        self.min_edit.setRange(0, 90)
        self.min_edit.setValue(self.state.minutes_basketball)
        self.min_edit.setFixedWidth(60)
        self.min_edit.setStyleSheet("background-color:white; color:black;")
        self.min_edit.editingFinished.connect(self.set_lcd_clock_from_inputs)
        grid.addWidget(self.min_edit, 8, 4)
        self.sec_edit = QSpinBox()
        self.sec_edit.setRange(0, 59)
        self.sec_edit.setValue(self.state.seconds_basketball)
        self.sec_edit.setFixedWidth(60)
        self.sec_edit.setStyleSheet("background-color:white; color:black;")
        self.sec_edit.editingFinished.connect(self.set_lcd_clock_from_inputs)
        grid.addWidget(self.sec_edit, 8, 5)
        btn_start = QPushButton("Start Clock")
        btn_start.setStyleSheet("background-color:white; color:black;")
        btn_start.clicked.connect(self.start_clock)
        grid.addWidget(btn_start, 8, 0)
        btn_stop = QPushButton("Stop Clock")
        btn_stop.setStyleSheet("background-color:white; color:black;")
        btn_stop.clicked.connect(self.stop_clock)
        grid.addWidget(btn_stop, 8, 2)
        btn_reset = QPushButton("Reset Clock")
        btn_reset.setStyleSheet("background-color:white; color:black;")
        btn_reset.clicked.connect(self.reset_clock)
        grid.addWidget(btn_reset, 8, 3)
        self.timer = QTimer()
        self.timer.setInterval(1000)  # 1 sec
        self.timer.timeout.connect(self.game_tick)
        grid_away.addWidget(QLabel("<b>Away Team Setup</b>"), -1, 0)
        lbl_away_name = QLabel("Enter Away Name:")
        lbl_away_name.setStyleSheet("color:white;")
        grid_away.addWidget(lbl_away_name, 1, 0)
        self.away_setup_name = QLineEdit(self.state.away_name)
        self.away_setup_name.setStyleSheet("background-color:white; color:black;")
        grid_away.addWidget(self.away_setup_name, 1, 1)
        btn_away_name_submit = QPushButton("Submit")
        btn_away_name_submit.setStyleSheet("background-color:white; color:black;")
        btn_away_name_submit.clicked.connect(self.submit_away_setup)
        grid_away.addWidget(btn_away_name_submit, 1, 2)
        lbl_away_rank = QLabel("Away Team Rank:")
        lbl_away_rank.setStyleSheet("color:white;")
        grid_away.addWidget(lbl_away_rank, 1, 3)
        self.away_rank_edit = QLineEdit()
        self.away_rank_edit.setText(str(self.state.away_rank or ""))
        self.away_rank_edit.setStyleSheet("background-color:white; color:black;")
        validator = QIntValidator(0, 25, self)
        self.away_rank_edit.setValidator(validator)
        grid_away.addWidget(self.away_rank_edit, 1, 4)
        lbl_mascot = QLabel("Mascot:")
        lbl_mascot.setStyleSheet("color:white;")
        grid_away.addWidget(lbl_mascot, 2, 2)
        self.away_setup_mascot = QLineEdit(self.state.away_mascot)
        self.away_setup_mascot.setStyleSheet("background-color:white; color:black;")
        grid_away.addWidget(self.away_setup_mascot, 2, 3)
        btn_away_mascot_submit = QPushButton("Submit")
        btn_away_mascot_submit.setStyleSheet("background-color:white; color:black;")
        btn_away_mascot_submit.clicked.connect(self.submit_away_setup)
        grid_away.addWidget(btn_away_mascot_submit, 2, 4)
        lbl_away_color = QLabel("Away Team Color:")
        lbl_away_color.setStyleSheet("color:white;")
        grid_away.addWidget(lbl_away_color, 2, 0)
        btn_away_pick_color = QPushButton("🎨")
        btn_away_pick_color.setStyleSheet("background-color:white; color:black;")
        btn_away_pick_color.clicked.connect(self.pick_away_color_from_setup)
        grid_away.addWidget(btn_away_pick_color, 2, 1)
        lbl_away_logo = QLabel("Away Team Logo:")
        lbl_away_logo.setStyleSheet("color:white;")
        grid_away.addWidget(lbl_away_logo, 3, 0)
        btn_away_load_logo = QPushButton("🖼")
        btn_away_load_logo.setStyleSheet("background-color:white; color:black;")
        btn_away_load_logo.clicked.connect(self.load_away_logo_from_setup)
        grid_away.addWidget(btn_away_load_logo, 3, 1)
        lbl_away_record = QLabel("Away Team Record:")
        lbl_away_record.setStyleSheet("color:white;")
        grid_away.addWidget(lbl_away_record, 4, 0)
        self.away_record_wins_edit = QLineEdit(str(self.state.away_record_wins))
        self.away_record_wins_edit.setStyleSheet("background-color:white; color:black;")
        self.away_record_losses_edit = QLineEdit(str(self.state.away_record_losses))
        self.away_record_losses_edit.setStyleSheet("background-color:white; color:black;")
        grid_away.addWidget(self.away_record_wins_edit, 4, 1)
        grid_away.addWidget(self.away_record_losses_edit, 4, 2)
        btn_away_record_submit = QPushButton("Submit")
        btn_away_record_submit.setStyleSheet("background-color:white; color:black;")
        btn_away_record_submit.clicked.connect(self.submit_away_setup)
        grid_away.addWidget(btn_away_record_submit, 4, 3)
        lbl_away_district = QLabel("Away District Record:")
        lbl_away_district.setStyleSheet("color:white;")
        grid_away.addWidget(lbl_away_district, 5, 0)
        self.away_district_wins_edit = QLineEdit(str(self.state.away_district_wins))
        self.away_district_wins_edit.setStyleSheet("background-color:white; color:black;")
        self.away_district_losses_edit = QLineEdit(str(self.state.away_district_losses))
        self.away_district_losses_edit.setStyleSheet("background-color:white; color:black;")
        grid_away.addWidget(self.away_district_wins_edit, 5, 1)
        grid_away.addWidget(self.away_district_losses_edit, 5, 2)
        btn_away_district_submit = QPushButton("Submit")
        btn_away_district_submit.setStyleSheet("background-color:white; color:black;")
        btn_away_district_submit.clicked.connect(self.submit_away_setup)
        grid_away.addWidget(btn_away_district_submit, 5, 3)
        lbl_home_title = QLabel("<b>Home Team Setup</b>")
        lbl_home_title.setStyleSheet("color:white;")
        grid_home.addWidget(lbl_home_title, -4, 0)
        lbl_home_name = QLabel("Enter Home Name:")
        lbl_home_name.setStyleSheet("color:white;")
        grid_home.addWidget(lbl_home_name, 0, 0)
        self.home_setup_name = QLineEdit(self.state.home_name)
        self.home_setup_name.setStyleSheet("background-color:white; color:black;")
        grid_home.addWidget(self.home_setup_name, 0, 1)
        btn_home_name_submit = QPushButton("Submit")
        btn_home_name_submit.setStyleSheet("background-color:white; color:black;")
        btn_home_name_submit.clicked.connect(self.submit_home_setup)
        grid_home.addWidget(btn_home_name_submit, 0, 2)
        lbl_home_rank = QLabel("Home Team Rank:")
        lbl_home_rank.setStyleSheet("color:white;")
        grid_home.addWidget(lbl_home_rank, 0, 3)
        self.home_rank_edit = QLineEdit()
        self.home_rank_edit.setText(str(self.state.home_rank or ""))
        self.home_rank_edit.setStyleSheet("background-color:white; color:black;")
        validator = QIntValidator(0, 25, self)
        self.home_rank_edit.setValidator(validator)
        grid_home.addWidget(self.home_rank_edit, 0, 4)
        btn_home_rank_submit = QPushButton("Submit")
        btn_home_rank_submit.setStyleSheet("background-color:white; color:black;")
        btn_home_rank_submit.clicked.connect(self.submit_home_setup)
        grid_home.addWidget(btn_home_rank_submit, 0, 5)
        lbl_home_mascot = QLabel("Home Mascot:")
        lbl_home_mascot.setStyleSheet("color:white;")
        grid_home.addWidget(lbl_home_mascot, 1, 2)
        self.home_setup_mascot = QLineEdit(self.state.home_mascot)
        self.home_setup_mascot.setStyleSheet("background-color:white; color:black;")
        grid_home.addWidget(self.home_setup_mascot, 1, 3)
        btn_home_setup_mascot = QPushButton("Submit")
        btn_home_setup_mascot.setStyleSheet("background-color:white; color:black;")
        btn_home_setup_mascot.clicked.connect(self.submit_home_setup)
        grid_home.addWidget(btn_home_setup_mascot, 1, 4)
        lbl_home_color = QLabel("Home Team Color:")
        lbl_home_color.setStyleSheet("color:white;")
        grid_home.addWidget(lbl_home_color, 1, 0)
        btn_home_pick_color = QPushButton("🎨")
        btn_home_pick_color.setStyleSheet("background-color:white; color:black;")
        btn_home_pick_color.clicked.connect(self.pick_home_color_from_setup)
        grid_home.addWidget(btn_home_pick_color, 1, 1)
        lbl_home_logo = QLabel("Home Team Logo:")
        lbl_home_logo.setStyleSheet("color:white;")
        grid_home.addWidget(lbl_home_logo, 2, 0)
        btn_home_load_logo = QPushButton("🖼")
        btn_home_load_logo.setStyleSheet("background-color:white; color:black;")
        btn_home_load_logo.clicked.connect(self.load_home_logo_from_setup)
        grid_home.addWidget(btn_home_load_logo, 2, 1)
        lbl_home_record = QLabel("Home Team Record:")
        lbl_home_record.setStyleSheet("color:white;")
        grid_home.addWidget(lbl_home_record, 3, 0)
        self.home_record_wins_edit = QLineEdit(str(self.state.home_record_wins))
        self.home_record_wins_edit.setStyleSheet("background-color:white; color:black;")
        self.home_record_losses_edit = QLineEdit(str(self.state.home_record_losses))
        self.home_record_losses_edit.setStyleSheet("background-color:white; color:black;")
        grid_home.addWidget(self.home_record_wins_edit, 3, 1)
        grid_home.addWidget(self.home_record_losses_edit, 3, 2)
        btn_home_record_submit = QPushButton("Submit")
        btn_home_record_submit.setStyleSheet("background-color:white; color:black;")
        btn_home_record_submit.clicked.connect(self.submit_home_setup)
        grid_home.addWidget(btn_home_record_submit, 3, 3)
        lbl_home_district = QLabel("Home District Record:")
        lbl_home_district.setStyleSheet("color:white;")
        grid_home.addWidget(lbl_home_district, 4, 0)
        self.home_district_wins_edit = QLineEdit(str(self.state.home_district_wins))
        self.home_district_wins_edit.setStyleSheet("background-color:white; color:black;")
        self.home_district_losses_edit = QLineEdit(str(self.state.home_district_losses))
        self.home_district_losses_edit.setStyleSheet("background-color:white; color:black;")
        grid_home.addWidget(self.home_district_wins_edit, 4, 1)
        grid_home.addWidget(self.home_district_losses_edit, 4, 2)
        btn_home_district_submit = QPushButton("Submit")
        btn_home_district_submit.setStyleSheet("background-color:white; color:black;")
        btn_home_district_submit.clicked.connect(self.submit_home_setup)
        grid_home.addWidget(btn_home_district_submit, 4, 3)
        lbl_graphics = QLabel("Graphics:")
        lbl_graphics.setStyleSheet("color:white;")
        grid_info.addWidget(lbl_graphics, 3, 0)
        self.btn_show_intro = QPushButton("Show Intro Graphic")
        self.btn_show_intro.setStyleSheet("background-color:white; color:black;")
        self.btn_show_intro.clicked.connect(lambda: self.show_intro(force_double=True))
        grid_info.addWidget(self.btn_show_intro, 3, 1)
        self.btn_show_scorebug = QPushButton("Show Scorebug")
        self.btn_show_scorebug.setStyleSheet("background-color:white; color:black;")
        self.btn_show_scorebug.clicked.connect(lambda: self.show_scorebug(force_double=True))
        grid_info.addWidget(self.btn_show_scorebug, 3, 2)
        self.btn_show_breakboard = QPushButton("Show Breakboard")
        self.btn_show_breakboard.setStyleSheet("background-color:white; color:black;")
        self.btn_show_breakboard.clicked.connect(lambda: self.show_breakboard(force_double=True))
        grid_info.addWidget(self.btn_show_breakboard, 3, 3)
        self.btn_show_final = QPushButton("Show Final")
        self.btn_show_final.setStyleSheet("background-color:white; color:black;")
        self.btn_show_final.clicked.connect(lambda: self.show_final(force_double=True))
        grid_info.addWidget(self.btn_show_final, 3, 4)
        lbl_event_location = QLabel("Event Location:")
        lbl_event_location.setStyleSheet("color:white;")
        grid_info.addWidget(lbl_event_location, 1, 0)
        self.event_location_edit = QLineEdit()
        self.event_location_edit.setStyleSheet("background-color:white; color:black;")
        self.event_location_edit.setPlaceholderText("Enter school / event text...")
        grid_info.addWidget(self.event_location_edit, 1, 1)
        self.event_city_edit = QLineEdit()
        self.event_city_edit.setStyleSheet("background-color:white; color:black;")
        self.event_city_edit.setPlaceholderText("Enter city...")
        grid_info.addWidget(self.event_city_edit, 1, 2)
        btn_event_submit = QPushButton("Submit")
        btn_event_submit.setStyleSheet("background-color:white; color:black;")
        btn_event_submit.clicked.connect(self.submit_event_location)
        grid_info.addWidget(btn_event_submit, 1, 3)
        lbl_event_info = QLabel("Event Information:")
        lbl_event_info.setStyleSheet("color:white;")
        grid_info.addWidget(lbl_event_info, 2, 0)
        self.bottom_event_edit = QLineEdit()
        self.bottom_event_edit.setStyleSheet("background-color:white; color:black;")
        self.bottom_event_edit.setPlaceholderText("Enter event info text...")
        grid_info.addWidget(self.bottom_event_edit, 2, 1, 1, 2)
        btn_bottom_event_submit = QPushButton("Submit")
        btn_bottom_event_submit.setStyleSheet("background-color:white; color:black;")
        btn_bottom_event_submit.clicked.connect(self.submit_bottom_event)
        grid_info.addWidget(btn_bottom_event_submit, 2, 3)
        self.chk_district = QCheckBox("District Opponent")
        self.chk_district.setChecked(False)
        self.chk_district.stateChanged.connect(self.update_district_flag)
        self.chk_district.setStyleSheet("QCheckBox{color:white;} QCheckBox::indicator{width:15px;height:15px;border:2px solid white;background:#121212;} QCheckBox::indicator:checked{background:white;}")
        grid_info.addWidget(self.chk_district, 5, 0, 1 , 5)
        self.btn_home_3pt_made = QPushButton("3PT Made")
        self.btn_home_3pt_made.setStyleSheet("background-color:white; color:black;")
        self.btn_home_3pt_made.clicked.connect(lambda: self.add_stat("3pt", 1, "home", True))
        grid.addWidget(self.btn_home_3pt_made, 10, 4)
        self.btn_home_3pt_missed = QPushButton("3PT Missed")
        self.btn_home_3pt_missed.setStyleSheet("background-color:white; color:black;")
        self.btn_home_3pt_missed.clicked.connect(lambda: self.add_stat("3pt", 1, "home", False))
        grid.addWidget(self.btn_home_3pt_missed, 10, 6)
        self.btn_home_ft_made = QPushButton("FT Made")
        self.btn_home_ft_made.setStyleSheet("background-color:white; color:black;")
        self.btn_home_ft_made.clicked.connect(lambda: self.add_stat("ft", 1, "home", True))
        grid.addWidget(self.btn_home_ft_made, 9, 4)
        self.btn_home_ft_missed = QPushButton("FT Missed")
        self.btn_home_ft_missed.setStyleSheet("background-color:white; color:black;")
        self.btn_home_ft_missed.clicked.connect(lambda: self.add_stat("ft", 1, "home", False))
        grid.addWidget(self.btn_home_ft_missed, 9, 6)
        btn_show_home_stat = QPushButton("Show Home Stat")
        btn_show_home_stat.setStyleSheet("background-color:white; color:black;")
        btn_show_home_stat.clicked.connect(self.on_show_home_stat_clicked)
        grid.addWidget(btn_show_home_stat, 12, 4)
        self.btn_away_3pt_made = QPushButton("3PT Made")
        self.btn_away_3pt_made.setStyleSheet("background-color:white; color:black;")
        self.btn_away_3pt_made.clicked.connect(lambda: self.add_stat("3pt", 1, "away", True))
        grid.addWidget(self.btn_away_3pt_made, 10, 0)
        self.btn_away_3pt_missed = QPushButton("3PT Missed")
        self.btn_away_3pt_missed.setStyleSheet("background-color:white; color:black;")
        self.btn_away_3pt_missed.clicked.connect(lambda: self.add_stat("3pt", 1, "away", False))
        grid.addWidget(self.btn_away_3pt_missed, 10, 2)
        btn_show_away_stat = QPushButton("Show Away Stat")
        btn_show_away_stat.setStyleSheet("background-color:white; color:black;")
        btn_show_away_stat.clicked.connect(self.on_show_away_stat_clicked)
        grid.addWidget(btn_show_away_stat, 12, 2)
        self.btn_away_ft_made = QPushButton("FT Made")
        self.btn_away_ft_made.setStyleSheet("background-color:white; color:black;")
        self.btn_away_ft_made.clicked.connect(lambda: self.add_stat("ft", 1, "away", True))
        grid.addWidget(self.btn_away_ft_made, 9, 0)
        self.btn_away_ft_missed = QPushButton("FT Missed")
        self.btn_away_ft_missed.setStyleSheet("background-color:white; color:black;")
        self.btn_away_ft_missed.clicked.connect(lambda: self.add_stat("ft", 1, "away", False))
        grid.addWidget(self.btn_away_ft_missed, 9, 2)
        self.home_3_display = QLabel("")
        self.home_3_display.setStyleSheet("color:white;")
        self.home_ft_display = QLabel("")
        self.home_ft_display.setStyleSheet("color:white;")
        self.away_3_display = QLabel("")
        self.away_3_display.setStyleSheet("color:white;")
        self.away_ft_display = QLabel("")
        self.away_ft_display.setStyleSheet("color:white;")
        grid.addWidget(self.home_3_display, 10, 5)
        grid.addWidget(self.home_ft_display, 9, 5)
        grid.addWidget(self.away_3_display, 10, 1)
        grid.addWidget(self.away_ft_display, 9, 1)
        btn_remove_stat = QPushButton("Remove Stat")
        btn_remove_stat.setStyleSheet("background-color:white; color:black;")
        btn_remove_stat.clicked.connect(self.on_remove_basketball_event)
        grid.addWidget(btn_remove_stat, 12, 3)
    # ----- PAGE 1 slots & helpers (kept same behavior) -----
    def submit_bottom_event(self):
        text1 = self.bottom_event_edit.text().strip()
        text2 = self.bottom_event_edit.text().strip()
        self.state.bottom_event_text_basketball = text1 or ""
        self.state.bottom_event_active = bool(text1)
        if text1:
            self.state.bottom_event_progress = 0.0
            self.state.bottom_event_direction = 1
            self.state.bottom_event_animating = True
            self.state.bottom_event_start_time = time.time()
        self.state.upperbb_event_text_basketball = text2 or ""
        self.repaint_scoreboard()


  
    def submit_event_location(self):
    # Read both fields
        school_text = self.event_location_edit.text().strip()
        city_text = self.event_city_edit.text().strip()

    # Store into state
        self.state.event_location_school_text = school_text or ""
        self.state.event_location_city_text = city_text or ""

    # Repaint scorebug
        self.repaint_scoreboard()
    def add_stat(self, stat_type, amount, team, made):
        if team == "home":
            if stat_type == "3pt":
                if made:
                    self.state.home_3_made += amount
                self.state.home_3_total += amount
                self.home_3_display.setText(
                    f"    {self.pct_str(self.state.home_3_made, self.state.home_3_total)}"
            )
            elif stat_type == "ft":  # moved inside team == "home"
                if made:
                    self.state.home_ft_made += amount
                self.state.home_ft_total += amount
                self.home_ft_display.setText(
                    f"    {self.pct_str(self.state.home_ft_made, self.state.home_ft_total)}"
            )
        elif team == "away":  # away
            if stat_type == "3pt":
                if made:
                    self.state.away_3_made += amount
                self.state.away_3_total += amount
                self.away_3_display.setText(f"      {self.pct_str(self.state.away_3_made, self.state.away_3_total)}")
            elif stat_type == "ft":  # moved inside team == "away"
                if made:
                    self.state.away_ft_made += amount
                self.state.away_ft_total += amount
                self.away_ft_display.setText(f"      {self.pct_str(self.state.away_ft_made, self.state.away_ft_total)}")
    def show_stat(self, stat_type, team):
        if team == "home":
            if not self.state.home_event_active:
                self.state.home_event_active = True
                self.state.home_event_animating = True
                self.state.home_event_progress = 0.0
                self.state.home_event_start_time = time.time()
                self.state.home_event_direction = 1
                if stat_type == "3pt":
                    made, total = self.state.home_3_made, self.state.home_3_total
                    self.state.stat_home_upper_text = "FROM THE ARC"
                elif stat_type == "ft":
                    made, total = self.state.home_ft_made, self.state.home_ft_total
                    self.state.stat_home_upper_text = "FROM THE LINE"
                else:
                    made, total = 0, 0
                self.state.home_event_text = self.pct_str(made, total)
            else:
                self.state.home_event_animating = True
                self.state.home_event_start_time = time.time()
                self.state.home_event_direction = -1
        elif team == "away":
            if not self.state.away_event_active:
                self.state.away_event_active = True
                self.state.away_event_animating = True
                self.state.away_event_progress = 0.0
                self.state.away_event_start_time = time.time()
                self.state.away_event_direction = 1
                if stat_type == "3pt":
                    made, total = self.state.away_3_made, self.state.away_3_total
                    self.state.stat_upper_text = "FROM THE ARC"
                elif stat_type == "ft":
                    made, total = self.state.away_ft_made, self.state.away_ft_total
                    self.state.stat_upper_text = "FROM THE LINE"
                else:
                    made, total = 0, 0
                self.state.away_event_text = self.pct_str(made, total)
            else:
                self.state.away_event_animating = True
                self.state.away_event_start_time = time.time()
                self.state.away_event_direction = -1
        self.repaint_scoreboard()
    def on_show_home_stat_clicked(self):
        stat_choice, ok = QInputDialog.getItem(self, "Show Home Stat", "Select stat:", ["FT", "3PT"], editable=False)
        if not ok: return
        stat_type = "3pt" if stat_choice == "3PT" else "ft"
        if not self.state.home_event_active:
            self.state.home_event_active = True
            self.state.home_event_animating = True
            self.state.home_event_progress = 0.0
            self.state.home_event_start_time = time.time()
            self.state.home_event_direction = 1
            if stat_type == "3pt":
                made, total = self.state.home_3_made, self.state.home_3_total
                self.state.stat_home_upper_text = "FROM THE ARC"
            elif stat_type == "ft":
                made, total = self.state.home_ft_made, self.state.home_ft_total
                self.state.stat_home_upper_text = "FROM THE LINE"
            self.state.home_event_text = self.pct_str(made, total)
    def on_show_away_stat_clicked(self):
        stat_choice, ok = QInputDialog.getItem(self, "Show Away Stat", "Select stat:", ["FT", "3PT"], editable=False)
        if not ok: return
        stat_type = "3pt" if stat_choice == "3PT" else "ft"
        if not self.state.away_event_active:
            self.state.away_event_active = True
            self.state.away_event_animating = True
            self.state.away_event_progress = 0.0
            self.state.away_event_start_time = time.time()
            self.state.away_event_direction = 1
            if stat_type == "3pt":
                made, total = self.state.away_3_made, self.state.away_3_total
                self.state.stat_upper_text = "FROM THE ARC"
            elif stat_type == "ft":
                made, total = self.state.away_ft_made, self.state.away_ft_total
                self.state.stat_upper_text = "FROM THE LINE"
            self.state.away_event_text = self.pct_str(made, total)
    def on_remove_basketball_event(self):
        if self.state.home_event_active:
            self.state.home_event_animating = True
            self.state.home_event_start_time = time.time()
            self.state.home_event_direction -= 1
        elif self.state.away_event_active:
            self.state.away_event_animating = True
            self.state.away_event_start_time = time.time()
            self.state.away_event_direction -= 1
    def handle_single_as_double(self):
        self.show_intro()  # first “press”
        self.show_intro()
    def show_intro(self, force_double=False):
        first_group=[("bottom_event", lambda d: -1), ("fcenter_rect", lambda d: -1), ("fright_break_box", lambda d: -1), ("fleft_break_box", lambda d: d-1),("center_rect",lambda d:-1),("right_break_box",lambda d:-1),("left_break_box",lambda d:d-1),("away_box",lambda d:-1),("right_box",lambda d:-1),("scenter_scorebug",lambda d:d-1)]
        second_group=[("icenter_rect",1),("iright_break_box",1),("ileft_break_box",1)]
        for name,op in first_group:
            if getattr(self.state,f"{name}_active") and not getattr(self.state,f"{name}_animating"):
                setattr(self.state,f"{name}_animating",True)
                setattr(self.state,f"{name}_direction",op(getattr(self.state,f"{name}_direction")))
                setattr(self.state,f"{name}_start_time",time.time())
        def start_second_group():
            for name,direction in second_group:
                setattr(self.state,f"{name}_animating",False)
                setattr(self.state,f"{name}_active",False)
                setattr(self.state,f"{name}_active",True)
                setattr(self.state,f"{name}_animating",True)
                setattr(self.state,f"{name}_progress",0.0)
                setattr(self.state,f"{name}_start_time",time.time())
                setattr(self.state,f"{name}_direction",direction)
        def wait_for_first_then_start():
            all_first_done = all(not getattr(self.state, f"{name}_animating") for name, _ in first_group)
            if all_first_done and not getattr(self.state, "second_group_started", False):
                start_second_group()
            else:
                QTimer.singleShot(30, wait_for_first_then_start)  # check again in 30 ms

        if force_double:
            wait_for_first_then_start()
        else:
    # normal behavior: start second group if first group already done
            all_first_done = all(not getattr(self.state, f"{name}_animating") for name, _ in first_group)
            if all_first_done and not getattr(self.state, "second_group_started", False):
                start_second_group()
        self.scoreboard.update()
    def show_breakboard(self,force_double=False):
        first_group = [("bottom_event", lambda d: -1), ("fcenter_rect", lambda d: -1), ("fright_break_box", lambda d: -1), ("fleft_break_box", lambda d: d-1), ("icenter_rect", lambda d: -1), ("iright_break_box", lambda d: -1), ("ileft_break_box", lambda d: d-1), ("away_box", lambda d: -1), ("right_box", lambda d: -1), ("scenter_scorebug", lambda d: d-1)]
        second_group=[("center_rect", 1),("right_break_box",1),("left_break_box",1)]
        for name,op in first_group:
            if getattr(self.state,f"{name}_active") and not getattr(self.state,f"{name}_animating"):
                setattr(self.state,f"{name}_animating",True)
                setattr(self.state,f"{name}_direction",op(getattr(self.state,f"{name}_direction")))
                setattr(self.state,f"{name}_start_time",time.time())
        def start_second_group():
            for name,direction in second_group:
                setattr(self.state,f"{name}_animating",False)
                setattr(self.state,f"{name}_active",False)
                setattr(self.state,f"{name}_active",True)
                setattr(self.state,f"{name}_animating",True)
                setattr(self.state,f"{name}_progress",0.0)
                setattr(self.state,f"{name}_start_time",time.time())
                setattr(self.state,f"{name}_direction",direction)
        def wait_for_first_then_start():
            all_first_done = all(not getattr(self.state, f"{name}_animating") for name, _ in first_group)
            if all_first_done and not getattr(self.state, "second_group_started", False):
                start_second_group()
            else:
                QTimer.singleShot(30, wait_for_first_then_start)  # check again in 30 ms

        if force_double:
            wait_for_first_then_start()
        else:
    # normal behavior: start second group if first group already done
            all_first_done = all(not getattr(self.state, f"{name}_animating") for name, _ in first_group)
            if all_first_done and not getattr(self.state, "second_group_started", False):
                start_second_group()
        self.scoreboard.update()
    def show_scorebug(self,force_double=False):
        first_group=[("center_rect", lambda d: -1), ("right_break_box", lambda d: -1), ("left_break_box", lambda d: d-1), ("icenter_rect", lambda d: -1), ("iright_break_box", lambda d: -1), ("ileft_break_box", lambda d: -1),("fcenter_rect", lambda d: -1), ("fright_break_box", lambda d: -1), ("fleft_break_box", lambda d: d-1)]
        second_group=[("scenter_scorebug", 1), ("right_box", 1), ("away_box", 1)] 
        for name,op in first_group:
            if getattr(self.state,f"{name}_active") and not getattr(self.state,f"{name}_animating"):
                setattr(self.state,f"{name}_animating",True)
                setattr(self.state,f"{name}_direction",op(getattr(self.state,f"{name}_direction")))
                setattr(self.state,f"{name}_start_time",time.time())
        def start_second_group():
            for name,direction in second_group:
                setattr(self.state,f"{name}_animating",False)
                setattr(self.state,f"{name}_active",False)
                setattr(self.state,f"{name}_active",True)
                setattr(self.state,f"{name}_animating",True)
                setattr(self.state,f"{name}_progress",0.0)
                setattr(self.state,f"{name}_start_time",time.time())
                setattr(self.state,f"{name}_direction",direction)
        def wait_for_first_then_start():
            all_first_done = all(not getattr(self.state, f"{name}_animating") for name, _ in first_group)
            if all_first_done and not getattr(self.state, "second_group_started", False):
                start_second_group()
            else:
                QTimer.singleShot(30, wait_for_first_then_start)  # check again in 30 ms

        if force_double:
            wait_for_first_then_start()
        else:
    # normal behavior: start second group if first group already done
            all_first_done = all(not getattr(self.state, f"{name}_animating") for name, _ in first_group)
            if all_first_done and not getattr(self.state, "second_group_started", False):
                start_second_group()
        self.scoreboard.update()
    def show_final(self,force_double=False):
        first_group=[("bottom_event", lambda d: -1),("away_box", lambda d: -1),("right_box", lambda d: -1),("scenter_scorebug", lambda d: d-1),("center_rect", lambda d: -1),("right_break_box", lambda d: -1),("left_break_box", lambda d: d-1),("icenter_rect", lambda d: -1),("iright_break_box", lambda d: -1),("ileft_break_box", lambda d: d-1),]
        second_group=[("fcenter_rect",1),("fleft_break_box",1),("fright_break_box",1)]
        for name,op in first_group:
            if getattr(self.state,f"{name}_active") and not getattr(self.state,f"{name}_animating"):
                setattr(self.state,f"{name}_animating",True)
                setattr(self.state,f"{name}_direction",op(getattr(self.state,f"{name}_direction")))
                setattr(self.state,f"{name}_start_time",time.time())
        def start_second_group():
            for name,direction in second_group:
                setattr(self.state,f"{name}_animating",False)
                setattr(self.state,f"{name}_active",False)
                setattr(self.state,f"{name}_active",True)
                setattr(self.state,f"{name}_animating",True)
                setattr(self.state,f"{name}_progress",0.0)
                setattr(self.state,f"{name}_start_time",time.time())
                setattr(self.state,f"{name}_direction",direction)
        def wait_for_first_then_start():
            all_first_done = all(not getattr(self.state, f"{name}_animating") for name, _ in first_group)
            if all_first_done and not getattr(self.state, "second_group_started", False):
                start_second_group()
            else:
                QTimer.singleShot(30, wait_for_first_then_start)  # check again in 30 ms

        if force_double:
            wait_for_first_then_start()
        else:
    # normal behavior: start second group if first group already done
            all_first_done = all(not getattr(self.state, f"{name}_animating") for name, _ in first_group)
            if all_first_done and not getattr(self.state, "second_group_started", False):
                start_second_group()
        self.scoreboard.update()
    def change_fouls(self, team, amount):
    # Make sure the state attribute exists
        if not hasattr(self.state, 'home_fouls'):
            self.state.home_fouls = 0
        if not hasattr(self.state, 'away_fouls'):
            self.state.away_fouls = 0

    # Update fouls
        if team == "home":
            self.state.home_fouls = max(0, self.state.home_fouls + amount)  # prevent negative fouls
            self.home_foul_label.setText(str(self.state.home_fouls))
        elif team == "away":
            self.state.away_fouls = max(0, self.state.away_fouls + amount)
            self.away_foul_label.setText(str(self.state.away_fouls))

    # Optional: repaint scoreboard if needed
        self.repaint_scoreboard()
    def ui_tick(self):
        changed = False 
    # --- Breakboard timer ---
        if self.state.breakboard_timer > 0:
            self.state.breakboard_timer -= 1
            changed = True

    # --- Existing animations ---
        if self.state.home_timeout_pop_timer > 0:
            self.state.home_timeout_pop_timer -= 1
            changed = True

        if self.state.home_timeout_bar_timer > 0:
            self.state.home_timeout_bar_timer -= 1
            changed = True

        if self.state.away_timeout_pop_timer > 0:
            self.state.away_timeout_pop_timer -= 1
            changed = True

        if self.state.away_timeout_bar_timer > 0:
            self.state.away_timeout_bar_timer -= 1
            changed = True
        if self.state.away_logo_score_anim > 0:
            self.state.away_logo_score_anim -= 1
            changed = True
        if self.state.home_logo_score_anim > 0:
            self.state.home_logo_score_anim -= 1
            changed = True
        if self.state.home_event_animating:
            elapsed = time.time() - self.state.home_event_start_time
            progress = elapsed / 3.0  # 3-second animation

            if self.state.home_event_direction == 1:  # expanding
                self.state.home_event_progress = min(self.state.home_event_progress + progress, 1.0)
                if self.state.home_event_progress >= 1.0:
                    self.state.home_event_animating = False
            else:  # collapsing
                self.state.home_event_progress = max(self.state.home_event_progress - progress, 0.0)
                if self.state.home_event_progress <= 0.0:
                    self.state.home_event_animating = False
                    self.state.home_event_active = False
            changed = True
        if self.state.scenter_scorebug_animating:
            elapsed = time.time() - self.state.scenter_scorebug_start_time

    # Configure delays (in seconds)
            enter_delay = 0.0      # delay before starting "in" animation
            exit_delay = 0.5       # delay before starting "out" animation
            anim_duration = 1.0    # duration of the animation itself

    # Determine which direction
            if self.state.scenter_scorebug_direction == 1:
        #        Entering animation
                if elapsed > enter_delay:
                    progress = (elapsed - enter_delay) / anim_duration
                    self.state.scenter_scorebug_progress = min(self.state.scenter_scorebug_progress + progress, 1.0)
                    if self.state.scenter_scorebug_progress >= 1.0:
                        self.state.scenter_scorebug_animating = False
            else:
        # Exiting animation
                if elapsed > exit_delay:
                    progress = (elapsed - exit_delay) / anim_duration
                    self.state.scenter_scorebug_progress = max(self.state.scenter_scorebug_progress - progress, 0.0)
                    if self.state.scenter_scorebug_progress <= 0.0:
                        self.state.scenter_scorebug_animating = False
                        self.state.scenter_scorebug_active = False

        self.repaint_scoreboard()
        if self.state.right_box_animating:
            elapsed = time.time() - self.state.right_box_start_time
            progress = elapsed / 2  # 2-second total animation

            if self.state.right_box_direction == 1:
        # Entering animation
                self.state.right_box_progress = min(self.state.right_box_progress + progress, 1.0)
                if self.state.right_box_progress >= 1.0:
                    self.state.right_box_animating = False
            else:
        # Exiting animation
                self.state.right_box_progress = max(self.state.right_box_progress - progress, 0.0)
                if self.state.right_box_progress <= 0.0:
                    self.state.right_box_animating = False
                    self.state.right_box_active = False

            self.repaint_scoreboard()


# Away box fade-out / animation
        if self.state.away_box_animating:
            elapsed = time.time() - self.state.away_box_start_time
            progress = elapsed / 2  # 2-second total animation

            if self.state.away_box_direction == 1:
                # Entering animation
                self.state.away_box_progress = min(self.state.away_box_progress + progress, 1.0)
                if self.state.away_box_progress >= 1.0:
                    self.state.away_box_animating = False
            else:
        # Exiting animation
                self.state.away_box_progress = max(self.state.away_box_progress - progress, 0.0)
                if self.state.away_box_progress <= 0.0:
                    self.state.away_box_animating = False
                    self.state.away_box_active = False

        self.repaint_scoreboard()
        if self.state.icenter_rect_animating:
            elapsed = time.time() - self.state.icenter_rect_start_time
            progress = elapsed / 1
            if self.state.icenter_rect_direction == 1:
                self.state.icenter_rect_progress = min(self.state.icenter_rect_progress + progress, 1.0)
                if self.state.icenter_rect_progress >= 1.0:
                    self.state.icenter_rect_animating = False
            else:
                self.state.icenter_rect_progress = max(self.state.icenter_rect_progress - progress, 0.0)
                if self.state.icenter_rect_progress <= 0.0:
                    self.state.icenter_rect_animating = False
                    self.state.icenter_rect_active = False
            self.repaint_scoreboard()
        if self.state.iright_break_box_animating:
            elapsed = time.time() - self.state.iright_break_box_start_time
            progress = elapsed / 2
            if self.state.iright_break_box_direction == 1:
                self.state.iright_break_box_progress = min(self.state.iright_break_box_progress + progress, 1.0)
                if self.state.iright_break_box_progress >= 1.0:
                    self.state.iright_break_box_animating = False
            else:
                self.state.iright_break_box_progress = max(self.state.iright_break_box_progress - progress, 0.0)
                if self.state.iright_break_box_progress <= 0.0:
                    self.state.iright_break_box_animating = False
                    self.state.iright_break_box_active = False
            self.repaint_scoreboard()
        if self.state.ileft_break_box_animating:
            elapsed = time.time() - self.state.ileft_break_box_start_time
            progress = elapsed / 2
            if self.state.ileft_break_box_direction == 1:
                self.state.ileft_break_box_progress = min(self.state.ileft_break_box_progress + progress, 1.0)
                if self.state.ileft_break_box_progress >= 1.0:
                    self.state.ileft_break_box_animating = False
            else:
                self.state.ileft_break_box_progress = max(self.state.ileft_break_box_progress - progress, 0.0)
                if self.state.ileft_break_box_progress <= 0.0:
                    self.state.ileft_break_box_animating = False
                    self.state.ileft_break_box_active = False
            self.repaint_scoreboard()
        if self.state.center_rect_animating:
            elapsed = time.time() - self.state.center_rect_start_time
            progress = elapsed / 1
            if self.state.center_rect_direction == 1:
                self.state.center_rect_progress = min(self.state.center_rect_progress + progress, 1.0)
                if self.state.center_rect_progress >= 1.0:
                    self.state.center_rect_animating = False
            else:
                self.state.center_rect_progress = max(self.state.center_rect_progress - progress, 0.0)
                if self.state.center_rect_progress <= 0.0:
                    self.state.center_rect_animating = False
                    self.state.center_rect_active = False
            self.repaint_scoreboard()
        if self.state.right_break_box_animating:
            elapsed = time.time() - self.state.right_break_box_start_time
            progress = elapsed / 2
            if self.state.right_break_box_direction == 1:
                self.state.right_break_box_progress = min(self.state.right_break_box_progress + progress, 1.0)
                if self.state.right_break_box_progress >= 1.0:
                    self.state.right_break_box_animating = False
            else:
                self.state.right_break_box_progress = max(self.state.right_break_box_progress - progress, 0.0)
                if self.state.right_break_box_progress <= 0.0:
                    self.state.right_break_box_animating = False
                    self.state.right_break_box_active = False
            self.repaint_scoreboard()
        if self.state.left_break_box_animating:
            elapsed = time.time() - self.state.left_break_box_start_time
            progress = elapsed / 2
            if self.state.left_break_box_direction == 1:
                self.state.left_break_box_progress = min(self.state.left_break_box_progress + progress, 1.0)
                if self.state.left_break_box_progress >= 1.0:
                    self.state.left_break_box_animating = False
            else:
                self.state.left_break_box_progress = max(self.state.left_break_box_progress - progress, 0.0)
                if self.state.left_break_box_progress <= 0.0:
                    self.state.left_break_box_animating = False
                    self.state.left_break_box_active = False
            self.repaint_scoreboard()
        if self.state.fcenter_rect_animating:
            elapsed = time.time() - self.state.fcenter_rect_start_time
            progress = elapsed / 1
            if self.state.fcenter_rect_direction == 1:
                self.state.fcenter_rect_progress = min(self.state.fcenter_rect_progress + progress, 1.0)
                if self.state.fcenter_rect_progress >= 1.0:
                    self.state.fcenter_rect_animating = False
            else:
                self.state.fcenter_rect_progress = max(self.state.fcenter_rect_progress - progress, 0.0)
                if self.state.fcenter_rect_progress <= 0.0:
                    self.state.fcenter_rect_animating = False
                    self.state.fcenter_rect_active = False
            self.repaint_scoreboard()
        if self.state.fright_break_box_animating:
            elapsed = time.time() - self.state.fright_break_box_start_time
            progress = elapsed / 2
            if self.state.fright_break_box_direction == 1:
                self.state.fright_break_box_progress = min(self.state.fright_break_box_progress + progress, 1.0)
                if self.state.fright_break_box_progress >= 1.0:
                    self.state.fright_break_box_animating = False
            else:
                self.state.fright_break_box_progress = max(self.state.fright_break_box_progress - progress, 0.0)
                if self.state.fright_break_box_progress <= 0.0:
                    self.state.fright_break_box_animating = False
                    self.state.fright_break_box_active = False
            self.repaint_scoreboard()
        if self.state.fleft_break_box_animating:
            elapsed = time.time() - self.state.fleft_break_box_start_time
            progress = elapsed / 2
            if self.state.fleft_break_box_direction == 1:
                self.state.fleft_break_box_progress = min(self.state.fleft_break_box_progress + progress, 1.0)
                if self.state.fleft_break_box_progress >= 1.0:
                    self.state.fleft_break_box_animating = False
            else:
                self.state.fleft_break_box_progress = max(self.state.fleft_break_box_progress - progress, 0.0)
                if self.state.fleft_break_box_progress <= 0.0:
                    self.state.fleft_break_box_animating = False
                    self.state.fleft_break_box_active = False
            self.repaint_scoreboard()

# Away animation
        if self.state.away_event_animating:
            elapsed = time.time() - self.state.away_event_start_time
            progress = elapsed / 3.0  # 3-second animation

            if self.state.away_event_direction == 1:  # expanding
                self.state.away_event_progress = min(self.state.away_event_progress + progress, 1.0)
                if self.state.away_event_progress >= 1.0:
                    self.state.away_event_animating = False
            else:  # collapsing
                self.state.away_event_progress = max(self.state.away_event_progress - progress, 0.0)
                if self.state.away_event_progress <= 0.0:
                    self.state.away_event_animating = False
                    self.state.away_event_active = False
            changed = True
        if self.state.bottom_event_animating:
            elapsed = time.time() - self.state.bottom_event_start_time
            progress = elapsed / 0.25  # duration

            if self.state.bottom_event_direction == 1:
                self.state.bottom_event_progress = min(
                    self.state.bottom_event_progress + progress, 1.0
        )
                if self.state.bottom_event_progress >= 1.0:
                    self.state.bottom_event_animating = False
            else:
                self.state.bottom_event_progress = max(
                    self.state.bottom_event_progress - progress, 0.0
        )
                if self.state.bottom_event_progress <= 0.0:
                    self.state.bottom_event_animating = False
                    self.state.bottom_event_active = False
            print("bottom progress:", self.state.bottom_event_progress)
            changed = True

        if (not self.state.icenter_rect_active and not self.state.icenter_rect_animating and
            not self.state.iright_break_box_active and not self.state.iright_break_box_animating and not self.state.ileft_break_box_animating 
            and not self.state.away_box_active and not self.state.away_box_animating and not self.state.right_box_active and not self.state.right_box_animating
            and not self.state.scenter_scorebug_active and not self.state.scenter_scorebug_animating):
            if not self.scoreboard.show_basketball_breakboard:
                self.scoreboard.show_basketball_intro = False
                self.scoreboard.show_basketball_breakboard = True
                self.scoreboard.show_basketball_scorebug = False
                self.scoreboard.show_basketball_final = False
        if (not self.state.icenter_rect_active and not self.state.icenter_rect_animating and
            not self.state.iright_break_box_active and not self.state.iright_break_box_animating and not self.state.ileft_break_box_active
            and not self.state.ileft_break_box_animating and not self.state.center_rect_active and not self.state.center_rect_animating and
            not self.state.right_break_box_active and not self.state.right_break_box_animating and not self.state.left_break_box_active
            and not self.state.left_break_box_animating and not self.state.fcenter_rect_active and not self.state.fcenter_rect_animating and
            not self.state.fright_break_box_active and not self.state.fright_break_box_animating and not self.state.fleft_break_box_active
            and not self.state.fleft_break_box_animating):
            if not self.scoreboard.show_basketball_scorebug:
                self.scoreboard.show_basketball_final = False
                self.scoreboard.show_basketball_intro = False
                self.scoreboard.show_basketball_breakboard = False
                self.scoreboard.show_basketball_scorebug = True
        if (not self.state.icenter_rect_active and not self.state.icenter_rect_animating and
            not self.state.iright_break_box_active and not self.state.iright_break_box_animating and not self.state.ileft_break_box_active
            and not self.state.ileft_break_box_animating and not self.state.center_rect_active and not self.state.center_rect_animating and
            not self.state.right_break_box_active and not self.state.right_break_box_animating and not self.state.left_break_box_active
            and not self.state.left_break_box_animating and not self.state.away_box_active and not self.state.away_box_animating and
            not self.state.right_box_active and not self.state.right_box_animating and not self.state.scenter_scorebug_active
            and not self.state.scenter_scorebug_animating):
            if not self.scoreboard.show_basketball_final:
                self.scoreboard.show_basketball_final = True
                self.scoreboard.show_basketball_intro = False
                self.scoreboard.show_basketball_breakboard = False
                self.scoreboard.show_basketball_scorebug = False
        if (not self.state.fcenter_rect_active and not self.state.fcenter_rect_animating and
            not self.state.fright_break_box_active and not self.state.fright_break_box_animating and not self.state.fleft_break_box_active
            and not self.state.fleft_break_box_animating and not self.state.center_rect_active and not self.state.center_rect_animating and
            not self.state.right_break_box_active and not self.state.right_break_box_animating and not self.state.left_break_box_active
            and not self.state.left_break_box_animating and not self.state.away_box_active and not self.state.away_box_animating and
            not self.state.right_box_active and not self.state.right_box_animating and not self.state.scenter_scorebug_active
            and not self.state.scenter_scorebug_animating):
            if not self.scoreboard.show_basketball_intro:
                self.scoreboard.show_basketball_final = False
                self.scoreboard.show_basketball_intro = True
                self.scoreboard.show_basketball_breakboard = False
                self.scoreboard.show_basketball_scorebug = False
        if changed:
            self.repaint_scoreboard()
    def pct_str(self, made, total):
        if total == 0:
            return "0/0  (0%)"
        percent = round((made / total) * 100)
        return f"{made}/{total}   ({percent}%)"




    def trigger_home_event(self, stat_type="3PT"):
        if self.state.home_event_active:
            self.state.home_event_active = False
            self.state.home_event_text = ""
        else:
            self.state.home_event_active = True
            if stat_type == "3PT":
                    self.state.home_event_text = self.pct_str(self.state.home_3_made, self.state.home_3_total)
            elif stat_type == "FT":
                    self.state.home_event_text = self.pct_str(self.state.home_ft_made, self.state.home_ft_total)
        self.repaint_scoreboard()

    def trigger_away_event(self, stat_type="3PT"):
        if self.state.away_event_active:
            self.state.away_event_active = False
            self.state.away_event_text = ""
        else:
            self.state.away_event_active = True
            if stat_type == "3PT":
                self.state.away_event_text = self.pct_str(self.state.away_3_made, self.state.away_3_total)
            elif stat_type == "FT":
                self.state.away_event_text = self.pct_str(self.state.away_ft_made, self.state.away_ft_total)
        self.repaint_scoreboard()

    def on_serial_button_clicked(self):
        action, ok = QInputDialog.getItem(self,"Serial Connection","Select action:",["Start Connection", "Stop Connection"],editable=False)
        if ok:
            if action == "Start Connection":
                self.start_serial()
            elif action == "Stop Connection":
                self.stop_serial()
    def start_serial(self):
        if getattr(self.state, "serial_thread", None) and self.state.serial_thread.is_alive():
            QMessageBox.warning(self, "Scoreboard", "Serial thread is already running")
            return
        self.state.serial_enabled = True
        self.state.serial_thread = shared.ScoreboardReader(self.state,parsers=[shared.DaktronicsParser(), shared.NevcoParser(), shared.FairPlayParser()])
        self.state.serial_thread.start()
        QMessageBox.information(self, "Scoreboard", "Serial connection started")
    def stop_serial(self):
        self.state.serial_enabled = False
        thread = getattr(self.state, "serial_thread", None)
        if thread and thread.is_alive():
            thread.stop()
            thread.join(timeout=1)
            QMessageBox.information(self, "Scoreboard", "Serial stopped")
            self.state.serial_thread = None
     
    def repaint_scoreboard(self):
        self.scoreboard.update()

    def set_possession_direct(self, team):
        self.state.possession = team
        self.repaint_scoreboard()
    def set_away_name(self):
        self.state.away_name = self.away_name_edit.text().strip() or "AWAY"
        self.repaint_scoreboard()

    def set_home_name(self):
        self.state.home_name = self.home_name_edit.text().strip() or "HOME"
        self.repaint_scoreboard()
    def quick_set_playclock(self, value):
        self.pc_spin.setValue(value)
        self.state.playclock = value
        self.repaint_scoreboard()
    def set_away_score(self):
        try:
            self.state.away_pts = int(self.aw_score_box.value())
        except Exception:
            pass
        self.repaint_scoreboard()        
    def update_district_flag(self, state):
        # checkbox checked = district game
        self.state.is_district_game = (state == Qt.Checked)

    def set_home_score(self):
        try:
            self.state.home_pts = int(self.hm_score_box.value())
        except Exception:
            pass
        self.repaint_scoreboard()

    def add_points(self, pts, team):
        if team == "home":
            self.state.home_pts = max(0, self.state.home_pts + pts)
            if pts > 0:
                self.state.home_logo_score_anim = 18 
        else:
            self.state.away_pts = max(0, self.state.away_pts + pts)
            if pts > 0:
                self.state.away_logo_score_anim = 18 
        self.hm_score_box.setValue(self.state.home_pts)
        self.aw_score_box.setValue(self.state.away_pts)
        self.repaint_scoreboard()
    def pick_away_color(self):
        c = QColorDialog.getColor(self.state.away_color, self, "Pick Away Color")
        if c.isValid():
            self.state.away_color = c
            self.repaint_scoreboard()

    def pick_home_color(self):
        c = QColorDialog.getColor(self.state.home_color, self, "Pick Home Color")
        if c.isValid():
            self.state.home_color = c
            self.repaint_scoreboard()

    def load_away_logo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open away logo", "", "Images (*.png *.jpg *.bmp)")
        if path:
            pm = QPixmap(path)
            pm = pm.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.state.away_logo = pm
            self.repaint_scoreboard()
    def load_center_logo_from_setup(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open away logo", "", "Images (*.png *.jpg *.bmp)")
        if path:
            pm = QPixmap(path)
            pm = pm.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.state.center_logo = pm
            self.repaint_scoreboard()
    def load_center_logo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open away logo", "", "Images (*.png *.jpg *.bmp)")
        if path:
            pm = QPixmap(path)
            pm = pm.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.state.center_logo = pm
            self.repaint_scoreboard()
    def change_timeout(self, team, delta):
        if team == "away":
            prev = self.state.away_timeouts_basketball
            self.state.away_timeouts_basketball = max(0, min(5, prev + delta))
            self.away_to_lcd.display(self.state.away_timeouts_basketball)

            if delta < 0 and self.state.away_timeouts_basketball < prev:
                taken_number = 5 - self.state.away_timeouts_basketball
                self.state.game_running = False
                if hasattr(self, "timer") and self.timer.isActive():
                    self.timer.stop()
                suffix = ["1st", "2nd", "3rd", "4th", "5th"]
                self.state.away_timeout_text = "Timeout"
                self.state.away_timeout_pop_timer = 100
                self.state.away_timeout_bar_timer = 100
            def check_and_show_breakboard():
                if self.state.away_timeout_pop_timer <= 0 and self.state.away_timeout_bar_timer <= 0:
                    self.show_breakboard(force_double=True)
                    QTimer.singleShot(15000, lambda: self.show_scorebug(force_double=True))
                else:
                    QTimer.singleShot(50, check_and_show_breakboard)

            check_and_show_breakboard()

        else:
            prev = self.state.home_timeouts_basketball
            self.state.home_timeouts_basketball = max(0, min(5, prev + delta))
            self.home_to_lcd.display(self.state.home_timeouts_basketball)

            if delta < 0 and self.state.home_timeouts_basketball < prev:
                taken_number = 5 - self.state.home_timeouts_basketball
                self.state.game_running = False
                if hasattr(self, "timer") and self.timer.isActive():
                    self.timer.stop()
                suffix = ["1st", "2nd", "3rd", "4th", "5th"]
                self.state.home_timeout_text = "Timeout"
                self.state.home_timeout_pop_timer = 100
                self.state.home_timeout_bar_timer = 100
            def check_and_show_breakboard():
                if self.state.home_timeout_pop_timer <= 0 and self.state.home_timeout_bar_timer <= 0:
                    self.show_breakboard(force_double=True)
                    QTimer.singleShot(15000, lambda: self.show_scorebug(force_double=True))
                else:
                    QTimer.singleShot(50, check_and_show_breakboard)

            check_and_show_breakboard()

        self.repaint_scoreboard()


    def load_home_logo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open home logo", "", "Images (*.png *.jpg *.bmp)")
        if path:
            pm = QPixmap(path)
            pm = pm.scaled(60, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.state.home_logo = pm
            self.repaint_scoreboard()

    def set_possession(self):
        val = self.possess_combo.currentText()
        if val == "None":
            self.state.possession = None
        elif val == "Away":
            self.state.possession = "away"
        else:
            self.state.possession = "home"
        self.repaint_scoreboard()

    def set_periodb(self):
        try:
            new_period = int(self.period_spin.value())
            self.state.period = new_period
            self.state.game_running = False
        except Exception:
            return
    # --- reset game clock ---
        if 1 <= new_period <= 4:  # regular periods
            self.state.minutes_basketball = 8
            self.state.seconds_basketball = 0
            self.min_edit.setValue(self.state.minutes_basketball)
            self.sec_edit.setValue(self.state.seconds_basketball)
        else:  # overtime periods
            self.state.minutes_basketball = 4
            self.state.seconds_basketball = 0
            self.min_edit.setValue(self.state.minutes_basketball)
            self.sec_edit.setValue(self.state.seconds_basketball)
        if new_period == 10:
            self.state.minutes_basketball = 15
            self.state.seconds_basketball = 0
            self.min_edit.setValue(self.state.minutes_basketball)
            self.sec_edit.setValue(self.state.seconds_basketball)
    # --- reset fouls at the end of a period ---
        if new_period in [1, 2, 3, 4]:
            self.state.home_fouls = 0
            self.state.away_fouls = 0
            if hasattr(self, "home_foul_label"):
                self.home_foul_label.setText("              0")
            if hasattr(self, "away_foul_label"):
                self.away_foul_label.setText("              0")

    # --- update LCDs if present ---
        if hasattr(self, "time_lcd"):
            self.time_lcd.display(f"{self.state.minutes_basketball:02d}:{self.state.seconds_basketball:02d}")
        if hasattr(self, "home_to_lcd"):
            self.home_to_lcd.display(self.state.home_timeouts_basketball)
        if hasattr(self, "away_to_lcd"):
            self.away_to_lcd.display(self.state.away_timeouts_basketball)

    # --- show final and update records if period 11 and not tied ---
        if new_period == 11 and self.state.home_pts != self.state.away_pts and not getattr(self.state, "game_finished", False):
            if self.state.away_box_active and not self.state.away_box_animating:
                self.state.away_box_animating = True
                self.state.away_box_direction = -1
                self.state.away_box_start_time = time.time()
            if self.state.right_box_active and not self.state.right_box_animating:
                self.state.right_box_animating = True
                self.state.right_box_direction = -1
                self.state.right_box_start_time = time.time()
            if self.state.scenter_scorebug_active and not self.state.scenter_scorebug_animating:
                self.state.scenter_scorebug_animating = True
                self.state.scenter_scorebug_direction -= 1
                self.state.scenter_scorebug_start_time = time.time()
            if self.state.center_rect_active and not self.state.center_rect_animating:
                self.state.center_rect_animating = True
                self.state.center_rect_direction = -1
                self.state.center_rect_start_time = time.time()
            if self.state.right_break_box_active and not self.state.right_break_box_animating:
                self.state.right_break_box_animating = True
                self.state.right_break_box_direction = -1
                self.state.right_break_box_start_time = time.time()
            if self.state.left_break_box_active and not self.state.left_break_box_animating:
                self.state.left_break_box_animating = True
                self.state.left_break_box_direction -= 1
                self.state.left_break_box_start_time = time.time()
            if self.state.icenter_rect_active and not self.state.icenter_rect_animating:
                self.state.icenter_rect_animating = True
                self.state.icenter_rect_direction = -1
                self.state.icenter_rect_start_time = time.time()
            if self.state.iright_break_box_active and not self.state.iright_break_box_animating:
                self.state.iright_break_box_animating = True
                self.state.iright_break_box_direction = -1
                self.state.iright_break_box_start_time = time.time()
            if self.state.ileft_break_box_active and not self.state.ileft_break_box_animating:
                self.state.ileft_break_box_animating = True
                self.state.ileft_break_box_direction -= 1
                self.state.ileft_break_box_start_time = time.time()
            self.state.fcenter_rect_active = True
            self.state.fcenter_rect_animating = True
            self.state.fcenter_rect_progress = 0.0
            self.state.fcenter_rect_start_time = time.time()
            self.state.fcenter_rect_direction = 1
            self.state.fright_break_box_active = True
            self.state.fright_break_box_animating = True
            self.state.fright_break_box_progress = 0.0
            self.state.fright_break_box_start_time = time.time()
            self.state.fright_break_box_direction = 1
            self.state.fleft_break_box_active = True
            self.state.fleft_break_box_animating = True
            self.state.fleft_break_box_progress = 0.0
            self.state.fleft_break_box_start_time = time.time()
            self.state.fleft_break_box_direction = 1
        # Update overall wins/losses
            if self.state.home_pts > self.state.away_pts:
                self.state.home_record_wins += 1
                self.state.away_record_losses += 1
            else:
                self.state.away_record_wins += 1
                self.state.home_record_losses += 1

        # Update district records if checked
            if getattr(self, "chk_district", None) and self.chk_district.isChecked():
                if self.state.home_pts > self.state.away_pts:
                    self.state.home_district_wins += 1
                    self.state.away_district_losses += 1
                else:
                    self.state.away_district_wins += 1
                    self.state.home_district_losses += 1

        # Mark game finished to prevent multiple updates
                self.final_record_updated = True

    # --- refresh scoreboard ---
        self.repaint_scoreboard()

    def _read_clock_inputs(self):
        try:
            m = int(self.min_edit.value())
            s = int(self.sec_edit.value())

        # clamp
            if m < 0:
                m = 0
            if s < 0:
                s = 0
            if s > 59:
                s = s % 60

            return m, s

        except Exception:
        # fallback to previous state values
            return self.state.minutes_basketball, self.state.seconds_basketball
    def set_lcd_clock_from_inputs(self):
        try:
            m = int(self.min_edit.value())
            s = int(self.sec_edit.value())
        except Exception:
            return

    # clamp values
        m = max(0, m)
        s = max(0, min(s, 59))

    # update state
        self.state.minutes_basketball = m
        self.state.seconds_basketball = s
        self.state.tenths_basketball = 0  # reset tenths

    # update LCD
        if hasattr(self, "time_lcd"):
            if m >= 1:
                self.time_lcd.display(f"{m:02d}:{s:02d}")
            else:
                # under 1 minute, show seconds.tenths
                self.time_lcd.display(f"{s:02d}.{self.state.tenths_basketball}")

    # optional scoreboard redraw
        self.repaint_scoreboard()


    def start_clock(self):
        m, s = self._read_clock_inputs()

    # clamp
        m = max(0, m)
        s = max(0, min(s, 59))

        self.state.minutes_basketball = m
        self.state.seconds_basketball = s
        self.state.tenths_basketball = 0  # reset tenths

    # start the timer if not already running
        if not self.timer.isActive():
            self.timer.start()

        self.state.game_running = True
        self.repaint_scoreboard()



    def stop_clock(self):
        if self.timer.isActive():
            self.timer.stop()
        self.state.game_running = False
        self.repaint_scoreboard()

    def reset_clock(self):
        self.state.minutes_basketball = 8
        self.state.seconds_basketball = 0
        self.state.tenths_basketball = 0

        # Reset LCD
        if hasattr(self, "time_lcd"):
            self.time_lcd.display("08:00")

        # Reset spin boxes / inputs
        if hasattr(self, "min_edit"):
            self.min_edit.setValue(8)

        if hasattr(self, "sec_edit"):
            self.sec_edit.setValue(0)

        if hasattr(self, "tenth_edit"):
            self.tenth_edit.setValue(0)

        self.repaint_scoreboard()

    def game_tick(self):
        total_seconds = self.state.minutes_basketball * 60 + self.state.seconds_basketball + self.state.tenths_basketball * 0.1

        if total_seconds <= 0:
            self.state.minutes_basketball = 0
            self.state.seconds_basketball = 0
            self.state.tenths_basketball = 0
            self.timer.stop()
            self.state.game_running = False
            if hasattr(self, "time_lcd"):
                self.time_lcd.display("0.0")
            self.repaint_scoreboard()
            return

    # --- Tick logic ---
        if total_seconds >= 60:
        # 1 second tick
            self.state.seconds_basketball -= 1
            if self.state.seconds_basketball < 0:
                if self.state.minutes_basketball > 0:
                    self.state.minutes_basketball -= 1
                    self.state.seconds_basketball = 59
        # Ensure tenths is 0
            self.state.tenths_basketball = 0

        # Keep 1-second interval
            if self.timer.interval() != 1000:
                self.timer.start(1000)

        else:
        # Under 1 minute → 0.1 second tick
            if self.state.tenths_basketball > 0:
                self.state.tenths_basketball -= 1
            else:
                if self.state.seconds_basketball > 0:
                    self.state.seconds_basketball -= 1
                    self.state.tenths_basketball = 9
                else:
                # 0.0 reached
                    self.state.tenths_basketball = 0
                    self.state.seconds_basketball = 0
                    self.state.minutes_basketball = 0
                    self.timer.stop()
                    self.state.game_running = False

        # Switch timer to 0.1 second
            if self.timer.interval() != 100:
                self.timer.start(100)

    # --- Update display ---
        if total_seconds >= 60:
            tstring = f"{self.state.minutes_basketball:02d}:{self.state.seconds_basketball:02d}"
        else:
            tstring = f"{self.state.seconds_basketball:02d}.{self.state.tenths_basketball}"

        if hasattr(self, "time_lcd"):
            self.time_lcd.display(tstring)
        if hasattr(self, "min_edit"):
            self.min_edit.setValue(self.state.minutes_basketball)
        if hasattr(self, "sec_edit"):
            self.sec_edit.setValue(self.state.seconds_basketball)

        self.repaint_scoreboard()
    # ----------------- Away/Home setup helper methods -----------------
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
            pm = pm.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.state.away_logo = pm
            self.repaint_scoreboard()

    def load_home_logo_from_setup(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open home logo", "", "Images (*.png *.jpg *.bmp)")
        if path:
            pm = QPixmap(path)
            pm = pm.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
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
        self.state.away_name = self.away_setup_name.text().strip() or self.state.away_name
        self.state.away_rank = self.away_rank_edit.text().strip() or self.state.away_rank
        self.state.away_mascot = self.away_setup_mascot.text().strip() or self.state.away_mascot

        try:
            self.state.away_record_wins = int(self.away_record_wins_edit.text().strip())
        except:
            pass
        try:
            self.state.away_record_losses = int(self.away_record_losses_edit.text().strip())
        except:
            pass
        try:
            self.state.away_district_wins = int(self.away_district_wins_edit.text().strip())
        except:
            pass
        try:
            self.state.away_district_losses = int(self.away_district_losses_edit.text().strip())
        except:
            pass

        self.repaint_scoreboard()

    def submit_home_setup(self):
        self.state.home_name = self.home_setup_name.text().strip() or self.state.home_name
        self.state.home_rank = self.home_rank_edit.text().strip() or self.state.home_rank
        self.state.home_mascot = self.home_setup_mascot.text().strip() or self.state.home_mascot       
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
