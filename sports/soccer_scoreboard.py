from shared.shared import *
class SoccerScoreboard(QWidget, ScoreboardToolkit):
    def __init__(self, state: ScoreState, mode="transparent", parent=None):
        super().__init__(parent)

        self.state = state
        self.mode = mode
        self.flash_on = False

        self.show_soccer_intro = False
        self.show_soccer_breakboard = False
        self.show_soccer_scorebug = True
        self.show_soccer_final = False
        self.show_home_goal = False
        self.show_away_goal = False

        screen = QApplication.primaryScreen()
        dpi_scale = screen.devicePixelRatio()

        self.setFixedSize(
            int(1920 * dpi_scale),
            int(1080 * dpi_scale)
        )

        if self.mode == "transparent":
            self.setAttribute(Qt.WA_TranslucentBackground)
            self.setAttribute(Qt.WA_NoSystemBackground, True)
            self.setAttribute(Qt.WA_OpaquePaintEvent, False)
        else:
            self.bg_color = QColor(255, 0, 255)

        self.setAutoFillBackground(False)

        ui_updater.refresh.connect(self.force_repaint)

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
        self.timer_font = QFont("College", 21, QFont.Bold)
        self.period_font = QFont("College", 18, QFont.Bold)
        self.score_font = QFont("College", 25, QFont.Bold)
        self.event_font = QFont("Legacy", 12, QFont.Bold)
        self.record_font = QFont("College", 12, QFont.Bold)
        self.ftitle_font = QFont("BigNoodleTitling", 30)
        self.frank_font = QFont("BigNoodleTitling", 23)
        self.bbtitle_font = QFont("BigNoodleTitling", 16, QFont.Bold)
        self.fscore_font = QFont("Octin Sports", 125, QFont.Bold)
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
        self.introrecord_font = QFont("College", 24, QFont.Bold)

        self.center_logo_label = QLabel(self)
        self.center_logo_label.setAlignment(Qt.AlignCenter)

        self.request_logo_file()

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

        if self.show_soccer_intro:
            self.draw_soccer_intro(p)

        if self.show_soccer_scorebug:
            self.draw_soccer_scorebug(p)

        if self.show_home_goal:
            self.draw_home_goal(p)

        if self.show_away_goal:
            self.draw_away_goal(p)

        if self.show_soccer_breakboard:
            self.draw_soccer_breakboard(p)

        if self.show_soccer_final:
            self.draw_soccer_final(p)
    def draw_soccer_intro(self, p):
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
        if self.state.ileft_break_box_active:
            progress = self.state.ileft_break_box_progress
            curr_width1 = int((left_w + 100) * progress)
            curr_width2 = int(left_w * progress)
            self.draw_normal_rect(p, left_x + left_w - curr_width1, 790, curr_width1, 150, base_home)
            self.draw_normal_rect(p, left_x + 100 + left_w - curr_width2, 790, curr_width2-100, 150, self.state.home_color)
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
            self.draw_logo_in_top_rounded_window(p, logo_x, logo_y, logo_w, logo_h, self.state.home_logo)
            p.restore()
            rank,name=self.format_rank_name(self.state.home_rank,self.state.home_name)
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
            mascot=getattr(self.state,"home_mascot",None)
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
            if not (hw == 0 and hl == 0):
                p.drawText(760, 838.5, curr_width1 - 20, 150, Qt.AlignLeft | Qt.AlignVCenter, f"{hw}-{hl}")
            if not (hdw == 0 and hdl == 0):
                p.drawText(800, 837.5, curr_width1 - 20, 150, Qt.AlignLeft | Qt.AlignVCenter, f"({hdw}-{hdl})")
            p.setOpacity(1.0)

    # -- HOME SECTION -- #
        if self.state.iright_break_box_active:
            progress = self.state.iright_break_box_progress
            curr_width = int(right_w * progress)
            self.draw_normal_rect(p, right_x+100, 790, int((right_w)*progress), 150, base_away)
            self.draw_normal_rect(p, right_x, 790, int((right_w-100)*progress), 150, self.state.away_color)
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
            self.draw_logo_in_top_rounded_window(p, logo_x, logo_y, logo_w, logo_h, self.state.away_logo)
            p.restore()
            p.setFont(self.frank_font)
            p.setPen(Qt.white)
            if not (rw == 0 and rl == 0):
                p.drawText(1054, 838.5, curr_width - 20, 150, Qt.AlignLeft | Qt.AlignVCenter, f"{rw}-{rl}")
            if not (dw == 0 and dl == 0):
                p.drawText(1094, 837.5, curr_width - 20, 150, Qt.AlignLeft | Qt.AlignVCenter, f"({dw}-{dl})")      
            rank, name = self.format_rank_name(self.state.away_rank, self.state.away_name)
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
            mascot = getattr(self.state, "away_mascot", None)
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
            rect2_x = left_x - 100 + ((left_w + 600) / 2 - half_width1)
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
            fade_delay = 0.7
            if progress <= fade_delay:
                opacity = 0.0
            else:
                opacity = (progress - fade_delay) / (1.0 - fade_delay)
            opacity = min(max(opacity, 0.0), 1.0)
            school = getattr(self.state, "event_location_school_text", "") or ""
            city = getattr(self.state, "event_location_city_text", "") or ""
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
            city_rect = QRect(city_x, rect_y + pad_y + 5, city_w + 100, 40)
            p.drawText(city_rect, Qt.AlignLeft | Qt.AlignVCenter, city)
            if self.state.upperbb_event_active:
                self.draw_upper_event_text(p, left_x + 45, 745, self.state.upperbb_event_text_basketball)
            p.setOpacity(1.0)
    def draw_soccer_breakboard(self, p):
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
        if self.state.left_break_box_active:
            progress = self.state.left_break_box_progress
            curr_width1 = int((left_w + 100) * progress)
            curr_width2 = int(left_w * progress)
            self.draw_normal_rect(p, left_x + left_w - curr_width1, 790, curr_width1, 200, base_home)
            self.draw_normal_rect(p, left_x + 200 + left_w - curr_width2, 790, curr_width2, 200, self.state.home_color)
            fade_delay = .7
            if progress <= fade_delay:
                opacity = 0.0
            else:
                opacity = (progress - fade_delay) / (1.0 - fade_delay)
            opacity = min(max(opacity, 0.0), 1.0)
            p.setOpacity(opacity)
            logo_x = left_x + 205
            logo_y = 780
            logo_w = 200
            logo_h = 206
            p.save()
            self.clip_to_rounded_rect(p, left_x + 200 + left_w - curr_width2, 790, curr_width2, 200)
            self.draw_logo_in_top_rounded_window(p, logo_x, logo_y, logo_w, logo_h, self.state.home_logo)
            p.restore()
            rank, name = self.format_rank_name(self.state.home_rank, self.state.home_name)
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
            p.drawText(left_x - 75, 810, 220, 175, Qt.AlignCenter, str(self.state.home_pts))
            p.setOpacity(1.0)
        if self.state.right_break_box_active:
            progress = self.state.right_break_box_progress
            curr_width = int(right_w * progress)
            self.draw_normal_rect(p, right_x, 790, int((right_w+100)*progress), 200, base_away)
            self.draw_normal_rect(p, right_x, 790, int((right_w-200)*progress), 200, self.state.away_color)
            fade_delay = .7
            if progress <= fade_delay:
                opacity = 0.0
            else:
                opacity = (progress - fade_delay) / (1.0 - fade_delay)
            opacity = min(max(opacity, 0.0), 1.0)
            p.setOpacity(opacity)
            logo_x = right_x
            logo_y = 780
            logo_w = 200
            logo_h = 206
            p.save()
            self.clip_to_rounded_rect(p, right_x, 790, int((right_w-205)*progress), 200)
            self.draw_logo_in_top_rounded_window(p, logo_x, logo_y, logo_w, logo_h, self.state.away_logo)
            p.restore()
            p.setFont(self.fscore_font)
            p.setPen(Qt.white)
            p.drawText(right_x+225, 810, 220, 175, Qt.AlignCenter, str(self.state.away_pts))
            rank, name = self.format_rank_name(self.state.away_rank, self.state.away_name)
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
    def draw_soccer_scorebug(self, p):
        left_x = 45
        left_w = 225
        right_x = 270
        right_w = 225
        px = 495
        pw = 40
        tx = 535
        tw = 75
        darker_home = self.state.home_color.darker(170)
        darker_away = self.state.away_color.darker(170)
        if self.state.soccer_active:
            progress = self.state.soccer_progress
            full_width = left_w + right_w + pw + tw
            curr_width = int(full_width * progress)
            curr_left_w = int(left_w * progress)
            curr_right_w = int(right_w * progress)
            curr_pw = int(pw * progress)
            curr_tw = int(tw * progress)
            curr_dark = int(48 * progress)
            self.draw_rect(p, left_x, 35, curr_left_w, 35, self.state.home_color)
            self.draw_rect(p, left_x + curr_left_w, 35, curr_right_w, 35, self.state.away_color)
            self.draw_rect(p, left_x + curr_left_w + curr_right_w, 35, curr_pw, 35, QColor("#1d1d1d"))
            self.draw_rect(p, left_x + curr_left_w + curr_right_w + curr_pw, 35, curr_tw, 35, QColor("#2b2d2f"))
            self.draw_transparentnormal_rect(p, left_x, 35, curr_dark, 35, darker_home)
            self.draw_transparentnormal_rect(p, left_x + curr_left_w, 35, curr_dark, 35, darker_away)
            self.draw_transparentnormal_rect(p, left_x + 190 * progress, 35, 35, 35, QColor("#2a2a2a"))
            self.draw_transparentnormal_rect(p, left_x + curr_left_w + 190 * progress, 35, 35, 35, QColor("#2a2a2a"))
            delay_progress = 0.5
            if progress >= delay_progress:
                delayed_progress = (progress - delay_progress) / (1.0 - delay_progress)
                fade_delay = 0.7
                opacity = 0.0 if delayed_progress <= fade_delay else (delayed_progress - fade_delay) / (1.0 - fade_delay)
                opacity = min(max(opacity, 0.0), 1.0)
                p.setOpacity(opacity)
                logo_w, logo_h = 45, 35
                logo_x = left_x + 2
                logo_y = 35
                p.save()
                self.clip_to_rounded_rect(p, logo_x, 35, logo_w, logo_h)
                self.draw_logo_in_top_rounded_window(p, logo_x, logo_y, logo_w, logo_h, self.state.home_logo)
                p.restore()
                logo_x = left_x + curr_left_w + 2
                p.save()
                self.clip_to_rounded_rect(p, logo_x, 35, logo_w, logo_h)
                self.draw_logo_in_top_rounded_window(p, logo_x, logo_y, logo_w, logo_h, self.state.away_logo)
                p.restore()
                p.setFont(self.score_font)
                p.setPen(Qt.white)
                p.drawText(left_x + 183, 35, 50, 35, Qt.AlignCenter, str(self.state.home_pts))
                p.drawText(left_x + curr_left_w + 183, 35, 50, 35, Qt.AlignCenter, str(self.state.away_pts))
                p.setFont(self.timer_font)
                p.setPen(Qt.white)
                tstring = f"{self.state.minutes_soccer}:{self.state.seconds_soccer:02d}"
                p.drawText(tx, 35, tw, 35, Qt.AlignCenter, tstring)
                p.setFont(self.title_font)
                p.setPen(Qt.white)
                p.drawText(left_x + 50, 40, 135, 25, Qt.AlignLeft | Qt.AlignVCenter, self.state.home_name)
                p.drawText(left_x + curr_left_w + 50, 40, 135, 25, Qt.AlignLeft | Qt.AlignVCenter, self.state.away_name)
                p.drawText(left_x + curr_left_w + curr_right_w + 5, 35, curr_pw, 35, Qt.AlignLeft | Qt.AlignVCenter, f"{self.period_text()}")
            p.setOpacity(1.0)
        if self.state.bottom_event_active:
            self.draw_transparentnormal_rect(p, left_x, 10, 515, 25, QColor("#2a2a2a"))
            self.draw_bottom_event_text(p, left_x+5.5, 12, self.state.bottom_event_text_soccer)
    def draw_home_goal(self, p):
        left_x = 45
        left_w = 450
        darker_home = self.state.home_color.darker(170)
        darker_away = self.state.away_color.darker(170)
        self.draw_rect(p, left_x, 35, left_w, 35, self.state.home_color)
        self.draw_transparentnormal_rect(p, left_x, 35, 48, 35, darker_home)
        self.draw_transparentnormal_rect(p, left_x+403, 35, 48, 35, darker_home)
        p.setFont(self.title_font)
        p.setPen(Qt.white)
        p.drawText(left_x+150, 40, 236, 25, Qt.AlignLeft | Qt.AlignVCenter, self.state.goal_text)      
        logo_x=left_x+405
        logo_y=35
        logo_w=45
        logo_h=35
        p.save()
        self.clip_to_rounded_rect(p,logo_x,35,logo_w,35)
        self.draw_logo_in_top_rounded_window(p,logo_x,logo_y,logo_w,logo_h,self.state.home_logo)
        p.restore()
        logo_x=left_x+2
        logo_y=35
        logo_w=45
        logo_h=35
        p.save()
        self.clip_to_rounded_rect(p,logo_x,35,logo_w,35)
        self.draw_logo_in_top_rounded_window(p,logo_x,logo_y,logo_w,logo_h,self.state.home_logo)
        p.restore()
    def draw_away_goal(self, p):
        left_x = 45
        left_w = 450
        darker_away = self.state.away_color.darker(170)
        self.draw_rect(p, left_x, 35, left_w, 35, self.state.away_color)
        self.draw_transparentnormal_rect(p, left_x, 35, 48, 35, darker_away)
        self.draw_transparentnormal_rect(p, left_x+403, 35, 48, 35, darker_away)
        p.setFont(self.title_font)
        p.setPen(Qt.white)
        p.drawText(left_x+150, 40, 235, 25, Qt.AlignLeft | Qt.AlignVCenter, self.state.goal_text)      
        logo_x=left_x+405
        logo_y=35
        logo_w=45
        logo_h=35
        p.save()
        self.clip_to_rounded_rect(p,logo_x,35,logo_w,35)
        self.draw_logo_in_top_rounded_window(p,logo_x,logo_y,logo_w,logo_h,self.state.away_logo)
        p.restore()
        logo_x=left_x+2
        logo_y=35
        logo_w=45
        logo_h=35
        p.save()
        self.clip_to_rounded_rect(p,logo_x,35,logo_w,35)
        self.draw_logo_in_top_rounded_window(p,logo_x,logo_y,logo_w,logo_h,self.state.away_logo)
        p.restore()
    def draw_soccer_final(self, p):
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
            self.draw_normal_rect(p, left_x + left_w - curr_width1, 790, curr_width1, 200, base_home)
            self.draw_normal_rect(p, left_x + 200 + left_w - curr_width2, 790, curr_width2, 200, self.state.home_color)
            fade_delay = .7
            if progress <= fade_delay:
                opacity = 0.0
            else:
                opacity = (progress - fade_delay) / (1.0 - fade_delay)
            opacity = min(max(opacity, 0.0), 1.0)
            p.setOpacity(opacity)
            logo_x = left_x + 200
            logo_y = 780
            logo_w = 200
            logo_h = 206
            p.save()
            self.clip_to_rounded_rect(p, left_x + 200 + left_w - curr_width2, 790, curr_width2, 200)
            self.draw_logo_in_top_rounded_window(p, logo_x, logo_y, logo_w, logo_h, self.state.home_logo)
            p.restore()
            rank, name = self.format_rank_name(self.state.home_rank, self.state.home_name)
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
                p.drawText(560, 768.5, curr_width1 - 20, 150, Qt.AlignLeft | Qt.AlignVCenter, f"{hw}-{hl}")
            if not (dw == 0 and dl == 0):
                p.drawText(600, 767.5, curr_width1 - 20, 150, Qt.AlignLeft | Qt.AlignVCenter, f"({hdw}-{hdl})")
            p.setFont(self.fscore_font)
            p.setPen(Qt.white)
            p.drawText(left_x - 65, 810, 220, 215, Qt.AlignCenter, str(self.state.home_pts))
            p.setOpacity(1.0)

    # -- HOME SECTION -- #
        if self.state.fright_break_box_active:
            progress = self.state.fright_break_box_progress
            curr_width = int(right_w * progress)
            self.draw_normal_rect(p, right_x, 790, int((right_w+100)*progress), 200, base_away)
            self.draw_normal_rect(p, right_x, 790, int((right_w-200)*progress), 200, self.state.away_color)
            fade_delay = .7
            if progress <= fade_delay:
                opacity = 0.0
            else:
                opacity = (progress - fade_delay) / (1.0 - fade_delay)
            opacity = min(max(opacity, 0.0), 1.0)
            p.setOpacity(opacity)
            logo_x = right_x
            logo_y = 780
            logo_w = 200
            logo_h = 206
            p.save()
            self.clip_to_rounded_rect(p, right_x, 790, int((right_w-205)*progress), 200)
            self.draw_logo_in_top_rounded_window(p, logo_x, logo_y, logo_w, logo_h, self.state.away_logo)
            p.restore()
            p.setFont(self.frank_font)
            p.setPen(Qt.white)
            if not (hw == 0 and hl == 0):
                p.drawText(1254, 768.5, curr_width - 20, 150, Qt.AlignLeft | Qt.AlignVCenter, f"{rw}-{rl}")
            if not (hdw == 0 and hdl == 0):
                p.drawText(1294, 767.5, curr_width - 20, 150, Qt.AlignLeft | Qt.AlignVCenter, f"({dw}-{dl})")
            p.setFont(self.fscore_font)
            p.setPen(Qt.white)
            p.drawText(right_x + 235, 810, 220, 215, Qt.AlignCenter, str(self.state.away_pts))
            rank, name = self.format_rank_name(self.state.away_rank, self.state.away_name)
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
class SoccerControl(QMainWindow):
    def __init__(self, state: ScoreState, scoreboard: SoccerScoreboard):
        super().__init__()
        self.state = state
        self.goal_timer = QTimer(self)
        self.goal_timer.setSingleShot(True)
        self.goal_timer.timeout.connect(self.end_goal)
        self.ui_timer = QTimer(self)
        self.ui_timer.timeout.connect(self.ui_tick)
        self.ui_timer.start(100)
        self.scoreboard = scoreboard
        version = beta_version if beta_mode else current_version

        self.setWindowTitle(
            f"Soccer Scoreboard Control (Version: {version}"
            f"{' - BETA' if beta_mode else ''})"
        )        
        self.setMinimumSize(720, 520)

        # Tab widget as central
        tabs = QTabWidget()
        self.setCentralWidget(tabs)

        # Page 1 — your original controls (kept structure identical)

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

        btn_serial = QPushButton("Connect Daktronics")
        btn_serial.clicked.connect(self.start_serial)
        grid.addWidget(btn_serial, 13, 5)
        self.chk_district = QCheckBox("District Opponent")
        self.chk_district.setChecked(False)
        self.chk_district.stateChanged.connect(self.update_district_flag)
        self.chk_district.setStyleSheet("QCheckBox{color:white;} QCheckBox::indicator{width:15px;height:15px;border:2px solid white;background:#121212;} QCheckBox::indicator:checked{background:white;}")
        grid_info.addWidget(self.chk_district, 5, 0, 1 , 5)
        grid.addWidget(QLabel("Home Score:"), 2, 0)
        self.hm_score_box = QSpinBox()
        self.hm_score_box.setRange(0, 999)
        self.hm_score_box.setValue(self.state.home_pts)
        self.hm_score_box.hide()    # hide it from UI
        btn_hm_set = QPushButton("Set")
        btn_hm_set.clicked.connect(self.set_home_score)
        grid.addWidget(btn_hm_set, 2, 3)
        self.hm_lcd = QLCDNumber()
        self.hm_lcd.setDigitCount(3)
        self.hm_lcd.setSegmentStyle(QLCDNumber.Flat)
        self.hm_lcd.setStyleSheet("""
        QLCDNumber {
            color: white;
            background-color: black;
            border: 2px solid #333;
            padding: 2px;
        }
        """)
        grid.addWidget(self.hm_lcd, 2, 1, 1, 2)
        self.hm_score_box.valueChanged.connect(self.hm_lcd.display)

        # --- Away Score on the right ---
        grid.addWidget(QLabel("Away Score:"), 2, 4)
        self.aw_score_box = QSpinBox()
        self.aw_score_box.setRange(0, 999)
        self.aw_score_box.setValue(self.state.away_pts)
        self.aw_score_box.hide()    # hide it from UI
        btn_aw_set = QPushButton("Set")
        btn_aw_set.clicked.connect(self.set_away_score)
        grid.addWidget(btn_aw_set, 2, 7)
        self.aw_lcd = QLCDNumber()
        self.aw_lcd.setDigitCount(3)
        self.aw_lcd.setSegmentStyle(QLCDNumber.Flat)
        self.aw_lcd.setStyleSheet("""
        QLCDNumber {
            color: white;
            background-color: black;
            border: 2px solid #333;
            padding: 2px;
        }
        """)
        grid.addWidget(self.aw_lcd, 2, 5, 1, 2)
        self.aw_score_box.valueChanged.connect(self.aw_lcd.display)
        # Quick score buttons
        row, col = 0, 0
        for text, pts in [("+1", 1)]:
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, pts=pts: self.add_points(pts, "home"))
            grid.addWidget(btn, row, col, 1, 4)
            col += 4
        row, col = 3, 0
        for text, pts in [("-1", -1)]:
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, pts=pts: self.add_points(pts, "home"))
            grid.addWidget(btn, row, col, 1, 4)
            col += 4
        row, col = 0, 4
        for text, pts in [("+1", 1)]:
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, pts=pts: self.add_points(pts, "away"))
            grid.addWidget(btn, row, col, 1, 4)
            col += 4
        row, col = 3, 4
        for text, pts in [("-1", -1)]:
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, pts=pts: self.add_points(pts, "away"))
            grid.addWidget(btn, row, col, 1, 4)
            col += 4                
        # Period and time controls
        grid.addWidget(QLabel("Period:"), 5, 2, 1, 2)
        self.period_spin = QSpinBox()
        self.period_spin.setRange(1, 6)
        self.period_spin.setValue(self.state.period)
        grid.addWidget(self.period_spin, 5, 3, 1, 2)
        btn_set_period = QPushButton("Set Period")
        btn_set_period.clicked.connect(self.set_period)
        grid.addWidget(btn_set_period, 5, 5, 1, 2)
        grid.addWidget(QLabel("Game Clock:"), 11, 0)
        self.time_lcd = QLCDNumber()
        self.time_lcd.setDigitCount(5)  # MM:SS
        self.time_lcd.setSegmentStyle(QLCDNumber.Flat)
        self.time_lcd.display(f"{self.state.minutes_soccer:02d}:{self.state.seconds_soccer:02d}")
        self.time_lcd.setStyleSheet("""
QLCDNumber {
    color: white;
    background-color: black;
    border: 2px solid #333;
    padding: 2px;
}
""")
        grid.addWidget(self.time_lcd, 11, 1, 1, 1)
        self.min_edit = QSpinBox()
        self.min_edit.setRange(0, 90)
        self.min_edit.setValue(self.state.minutes_soccer)
        self.min_edit.setFixedWidth(60)
        grid.addWidget(self.min_edit, 11, 5)
        self.sec_edit = QSpinBox()
        self.sec_edit.setRange(0, 59)
        self.sec_edit.setValue(self.state.seconds_soccer)
        self.sec_edit.setFixedWidth(60)
        grid.addWidget(self.sec_edit, 11, 6)
        btn_set_clock = QPushButton("Set")
        btn_set_clock.clicked.connect(self.set_lcd_clock_from_inputs)
        grid.addWidget(btn_set_clock, 11, 7)
        btn_start = QPushButton("Start Clock")
        btn_start.clicked.connect(self.start_clock)
        grid.addWidget(btn_start, 11, 2)
        btn_stop = QPushButton("Stop Clock")
        btn_stop.clicked.connect(self.stop_clock)
        grid.addWidget(btn_stop, 11, 3)
        btn_reset = QPushButton("Reset Clock")
        btn_reset.clicked.connect(self.reset_clock)
        grid.addWidget(btn_reset, 11, 4)
        self.timer = QTimer()
        self.timer.setInterval(1000)  # 1 sec
        self.timer.timeout.connect(self.game_tick)
        self.play_timer = QTimer()
        self.play_timer.setInterval(1000)
        # ----------------- PAGE 2: Away Setup -----------------
        grid_away.addWidget(QLabel("<b>Away Team Setup</b>"), -1, 0)
        grid_away.addWidget(QLabel("Enter Away Name:"), 1, 0)
        self.away_setup_name = QLineEdit(self.state.away_name)
        grid_away.addWidget(self.away_setup_name, 1, 1)
        btn_away_name_submit = QPushButton("Submit")
        btn_away_name_submit.clicked.connect(self.submit_away_setup)
        grid_away.addWidget(btn_away_name_submit, 1, 2)
        grid_away.addWidget(QLabel("Away Team Rank:"), 1, 3)
        self.away_rank_edit = QLineEdit()
        self.away_rank_edit.setText(str(self.state.away_rank or ""))  # safe default
        validator = QIntValidator(0, 25, self)
        self.away_rank_edit.setValidator(validator)
        grid_away.addWidget(self.away_rank_edit, 1, 4)
        grid_away.addWidget(QLabel("Mascot:"), 2, 2)
        self.away_setup_mascot = QLineEdit(self.state.away_mascot)
        grid_away.addWidget(self.away_setup_mascot, 2, 3)
        btn_away_mascot_submit = QPushButton("Submit")
        btn_away_mascot_submit.clicked.connect(self.submit_away_setup)
        grid_away.addWidget(btn_away_mascot_submit, 2, 4)
        btn_away_rank_submit = QPushButton("Submit")
        btn_away_rank_submit.clicked.connect(self.submit_away_setup)
        grid_away.addWidget(btn_away_rank_submit, 1, 5)
        grid_away.addWidget(QLabel("Away Team Color:"), 2, 0)
        btn_away_pick_color = QPushButton("🎨")
        btn_away_pick_color.clicked.connect(self.pick_away_color_from_setup)
        grid_away.addWidget(btn_away_pick_color, 2, 1)
        grid_away.addWidget(QLabel("Away Team Logo:"), 3, 0)
        btn_away_load_logo = QPushButton("🖼")
        btn_away_load_logo.clicked.connect(self.load_away_logo_from_setup)
        grid_away.addWidget(btn_away_load_logo, 3, 1)
        grid_away.addWidget(QLabel("Away Team Record:"), 4, 0)
        self.away_record_wins_edit = QLineEdit(str(self.state.away_record_wins))
        self.away_record_losses_edit = QLineEdit(str(self.state.away_record_losses))
        grid_away.addWidget(self.away_record_wins_edit, 4, 1)
        grid_away.addWidget(self.away_record_losses_edit, 4, 2)
        btn_away_record_submit = QPushButton("Submit")
        btn_away_record_submit.clicked.connect(self.submit_away_setup)
        grid_away.addWidget(btn_away_record_submit, 4, 3)
        grid_away.addWidget(QLabel("Away District Record:"), 5, 0)
        self.away_district_wins_edit = QLineEdit(str(self.state.away_district_wins))
        self.away_district_losses_edit = QLineEdit(str(self.state.away_district_losses))
        grid_away.addWidget(self.away_district_wins_edit, 5, 1)
        grid_away.addWidget(self.away_district_losses_edit, 5, 2)
        btn_away_district_submit = QPushButton("Submit")
        btn_away_district_submit.clicked.connect(self.submit_away_setup)
        grid_away.addWidget(btn_away_district_submit, 5, 3)

        # ----------------- PAGE 3: Home Setup -----------------
        grid_home.addWidget(QLabel("<b>Home Team Setup</b>"), -4, 0)
        grid_home.addWidget(QLabel("Enter Home Name:"), 0, 0)
        self.home_setup_name = QLineEdit(self.state.home_name)
        grid_home.addWidget(self.home_setup_name, 0, 1)
        btn_home_name_submit = QPushButton("Submit")
        btn_home_name_submit.clicked.connect(self.submit_home_setup)
        grid_home.addWidget(btn_home_name_submit, 0, 2)
        grid_home.addWidget(QLabel("Home Team Rank:"), 0, 3)
        self.home_rank_edit = QLineEdit()
        self.home_rank_edit.setText(str(self.state.home_rank or ""))
        validator = QIntValidator(0, 25, self)
        self.home_rank_edit.setValidator(validator)        
        grid_home.addWidget(self.home_rank_edit, 0, 4)
        btn_home_rank_submit = QPushButton("Submit")
        btn_home_rank_submit.clicked.connect(self.submit_home_setup)
        grid_home.addWidget(btn_home_rank_submit, 0, 5)
        grid_home.addWidget(QLabel("Home Mascot:"), 1, 2)
        self.home_setup_mascot = QLineEdit(self.state.home_mascot)
        grid_home.addWidget(self.home_setup_mascot, 1, 3)
        btn_home_setup_mascot = QPushButton("Submit")
        btn_home_setup_mascot.clicked.connect(self.submit_home_setup)
        grid_home.addWidget(btn_home_setup_mascot, 1, 4)
        grid_home.addWidget(QLabel("Home Team Color:"), 1, 0)
        btn_home_pick_color = QPushButton("🎨")
        btn_home_pick_color.clicked.connect(self.pick_home_color_from_setup)
        grid_home.addWidget(btn_home_pick_color, 1, 1)
        grid_home.addWidget(QLabel("Home Team Logo:"), 2, 0)
        btn_home_load_logo = QPushButton("🖼")
        btn_home_load_logo.clicked.connect(self.load_home_logo_from_setup)
        grid_home.addWidget(btn_home_load_logo, 2, 1)
        grid_home.addWidget(QLabel("Home Team Record:"), 3, 0)
        self.home_record_wins_edit = QLineEdit(str(self.state.home_record_wins))
        self.home_record_losses_edit = QLineEdit(str(self.state.home_record_losses))
        grid_home.addWidget(self.home_record_wins_edit, 3, 1)
        grid_home.addWidget(self.home_record_losses_edit, 3, 2)
        btn_home_record_submit = QPushButton("Submit")
        btn_home_record_submit.clicked.connect(self.submit_home_setup)
        grid_home.addWidget(btn_home_record_submit, 3, 3)
        grid_home.addWidget(QLabel("Home District Record:"), 4, 0)
        self.home_district_wins_edit = QLineEdit(str(self.state.home_district_wins))
        self.home_district_losses_edit = QLineEdit(str(self.state.home_district_losses))
        grid_home.addWidget(self.home_district_wins_edit, 4, 1)
        grid_home.addWidget(self.home_district_losses_edit, 4, 2)
        btn_home_district_submit = QPushButton("Submit")
        btn_home_district_submit.clicked.connect(self.submit_home_setup)
        grid_home.addWidget(btn_home_district_submit, 4, 3)
        grid_info.addWidget(QLabel("hehe"),-1,0)
        grid_info.addWidget(QLabel("Graphics:"),3,0)
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
        grid_info.addWidget(QLabel("Event Info:"), 2, 0)
        self.bottom_event_edit = QLineEdit()
        self.bottom_event_edit.setPlaceholderText("Enter event info text...")
        grid_info.addWidget(self.bottom_event_edit, 2, 1, 1, 2)  # QLineEdit
        btn_bottom_event_submit = QPushButton("Submit")
        btn_bottom_event_submit.clicked.connect(self.submit_bottom_event)
        grid_info.addWidget(btn_bottom_event_submit, 2, 3)
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
        def style_children(w):
            for c in w.findChildren(QWidget):
                if not isinstance(c, QLCDNumber):
                    c.setStyleSheet("QLabel{color:white;} QPushButton,QLineEdit,QSpinBox,QCheckBox{background:white;color:black;} QCheckBox::indicator{background:white;}")

        style_children(page1)
        style_children(page2)
        style_children(page3)
        style_children(page4)
    def ui_tick(self):
        changed = False
        if self.state.soccer_animating:
            elapsed = time.time() - self.state.soccer_start_time
            enter_delay = 0.0      # delay before starting "in" animation
            exit_delay = 0.5       # delay before starting "out" animation
            anim_duration = 1.0    # duration of the animation itself
            if self.state.soccer_direction == 1:
                if elapsed > enter_delay:
                    progress = (elapsed - enter_delay) / anim_duration
                    self.state.soccer_progress = min(self.state.soccer_progress + progress, 1.0)
                    if self.state.soccer_progress >= 1.0:
                        self.state.soccer_animating = False
            else:
                if elapsed > exit_delay:
                    progress = (elapsed - exit_delay) / anim_duration
                    self.state.soccer_progress = max(self.state.soccer_progress - progress, 0.0)
                    if self.state.soccer_progress <= 0.0:
                        self.state.soccer_animating = False
                        self.state.soccer_active = False
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
            and not self.state.soccer_active and not self.state.soccer_animating and not self.state.fleft_break_box_active and not self.state.fleft_break_box_animating and not 
            self.state.fright_break_box_active and not self.state.fright_break_box_animating and not self.state.fcenter_rect_active and not self.state.fcenter_rect_animating):
            if not self.scoreboard.show_soccer_breakboard:
                self.scoreboard.show_soccer_intro = False
                self.scoreboard.show_soccer_breakboard = True
                self.scoreboard.show_soccer_scorebug = False
                self.scoreboard.show_soccer_final = False
        if (not self.state.left_break_box_active and not self.state.left_break_box_animating and not self.state.right_break_box_active and not 
        self.state.right_break_box_animating and not self.state.center_rect_active and not self.state.center_rect_animating and not self.state.ileft_break_box_animating and not 
        self.state.iright_break_box_active and not self.state.iright_break_box_animating and not self.state.fleft_break_box_active and not self.state.fleft_break_box_animating and not 
        self.state.fright_break_box_active and not self.state.fright_break_box_animating and not self.state.fcenter_rect_active and not self.state.fcenter_rect_animating):
            if not self.scoreboard.show_soccer_scorebug:
                self.scoreboard.show_soccer_final = False
                self.scoreboard.show_soccer_intro = False
                self.scoreboard.show_soccer_breakboard = False
                self.scoreboard.show_soccer_scorebug = True
        if (not self.state.left_break_box_active and not self.state.left_break_box_animating and not self.state.right_break_box_active and not 
        self.state.right_break_box_animating and not self.state.center_rect_active and not self.state.center_rect_animating and not self.state.soccer_active 
        and not self.state.soccer_animating and not self.state.icenter_rect_active and not self.state.icenter_rect_animating and not self.state.ileft_break_box_active 
        and not self.state.ileft_break_box_animating and not self.state.iright_break_box_active and not self.state.iright_break_box_animating):
            if not self.scoreboard.show_soccer_final:
                self.scoreboard.show_soccer_final = True
                self.scoreboard.show_soccer_intro = False
                self.scoreboard.show_soccer_breakboard = False
                self.scoreboard.show_soccer_scorebug = False
        if (not self.state.left_break_box_active and not self.state.left_break_box_animating and not self.state.right_break_box_active and not 
        self.state.right_break_box_animating and not self.state.center_rect_active and not self.state.center_rect_animating and not self.state.soccer_active 
        and not self.state.soccer_animating and not self.state.fleft_break_box_active and not self.state.fleft_break_box_animating and not 
        self.state.fright_break_box_active and not self.state.fright_break_box_animating and not self.state.fcenter_rect_active and not self.state.fcenter_rect_animating):
            if not self.scoreboard.show_soccer_intro:
                self.scoreboard.show_soccer_final = False
                self.scoreboard.show_soccer_intro = True
                self.scoreboard.show_soccer_breakboard = False
                self.scoreboard.show_soccer_scorebug = False
        if changed:
            self.repaint_scoreboard()
    def handle_points_button(self, pts, team):
        self.add_points(pts, team)  # automatically triggers home/away goal if score increased
        self.update()  # 🔴 FORCE REPAINT

    # End the goal animation after 45 frames/seconds
        QTimer.singleShot(7000, self.end_goal)
    def end_goal(self):
        self.scoreboard.show_home_goal = False
        self.scoreboard.show_away_goal = False
        self.scoreboard.update()
    def submit_event_location(self):
        school_text = self.event_location_edit.text().strip()
        city_text = self.event_city_edit.text().strip()
        self.state.event_location_school_text = school_text or ""
        self.state.event_location_city_text = city_text or ""

        self.repaint_scoreboard()
    def submit_bottom_event(self):
        text = self.bottom_event_edit.text().strip()
        self.state.bottom_event_text_soccer = text or ""
        self.state.bottom_event_active = bool(text)
        self.repaint_scoreboard()
    def show_intro(self, force_double=False):
        first_group=[("bottom_event", lambda d: -1), ("fcenter_rect", lambda d: -1), ("fright_break_box", lambda d: -1), ("fleft_break_box", lambda d: d-1),("center_rect",lambda d:-1),("right_break_box",lambda d:-1),("left_break_box",lambda d:d-1),("soccer",lambda d:d-1)]
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
        first_group = [("bottom_event", lambda d: -1), ("fcenter_rect", lambda d: -1), ("fright_break_box", lambda d: -1), ("fleft_break_box", lambda d: d-1), ("icenter_rect", lambda d: -1), ("iright_break_box", lambda d: -1), ("ileft_break_box", lambda d: d-1), ("soccer", lambda d: d-1)]
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
        second_group=[("soccer", 1)] 
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
        first_group=[("bottom_event", lambda d: -1),("soccer", lambda d: d-1),("center_rect", lambda d: -1),("right_break_box", lambda d: -1),("left_break_box", lambda d: d-1),("icenter_rect", lambda d: -1),("iright_break_box", lambda d: -1),("ileft_break_box", lambda d: d-1),]
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
    def on_home_fg_clicked(self):
        yards = self.spin_home_yards.value()
        text = f"{yards} Yard Attempt"
        self.trigger_home_event(text)
    def on_away_fg_clicked(self):
        yards = self.spin_away_yards.value()
        text = f"{yards} Yard Attempt"
        self.trigger_away_event(text)    
    def trigger_home_event(self, text):
        if self.state.home_event_active:
            self.state.home_event_active = False
            self.state.home_event_text = ""
        else:
            self.state.home_event_active = True
            self.state.home_event_text = text.upper()
        self.repaint_scoreboard()           
    def trigger_away_event(self, text):
        if self.state.away_event_active:
            self.state.away_event_active = False
            self.state.away_event_text = ""
        else:
            self.state.away_event_active = True
            self.state.away_event_text = text.upper()
        self.repaint_scoreboard()  
    def start_serial(self):
        if getattr(self.state, "serial_thread", None) and self.state.serial_thread.is_alive():
            QMessageBox.warning(self, "Scoreboard", "Serial thread is already running")
            return
        self.state.serial_enabled = True
        self.state.serial_thread = ScoreboardReader(self.state,parsers=[DaktronicsParser(), NevcoParser(), FairPlayParser()])
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

    def set_away_score(self):
        try:
            self.state.away_pts = int(self.aw_score_box.value())
        except Exception:
            pass
        self.repaint_scoreboard()        
    def update_district_flag(self, state):
        self.state.is_district_game = (state == Qt.Checked)
    def set_home_score(self):
        try:
            self.state.home_pts = int(self.hm_score_box.value())
        except Exception:
            pass
        self.update()
    def add_points(self, pts, team):
        old_home_pts = self.state.home_pts
        old_away_pts = self.state.away_pts
        if team == "home":
            self.state.home_pts = max(0, self.state.home_pts + pts)
        else:
            self.state.away_pts = max(0, self.state.away_pts + pts)
        self.hm_score_box.setValue(self.state.home_pts)
        self.aw_score_box.setValue(self.state.away_pts)
        if self.state.home_pts > old_home_pts:
            self.start_home_goal()  # home goal triggered by score change
        if self.state.away_pts > old_away_pts:
            self.start_away_goal()  # away goal triggered by score change
        self.repaint_scoreboard()
    def start_home_goal(self):
        self.scoreboard.show_home_goal = True
        self.scoreboard.show_away_goal = False
        self.scoreboard.update()
        QTimer.singleShot(7000, self.end_goal)
    def start_away_goal(self):
        self.scoreboard.show_home_goal = False
        self.scoreboard.show_away_goal = True
        self.scoreboard.update()
        QTimer.singleShot(7000, self.end_goal)
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
    def load_home_logo(self):
        path, _ = QFileDialog.getOpenFileName(self,"Open home logo","","Images (*.png *.jpg *.jpeg *.bmp *.webp)")
        if path:
            pm = QPixmap()
            pm.load(path)
            pm = pm.scaled(
            60, 100,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation  # <-- Best quality resampling
        )
            pm = pm.convertToFormat(QImage.Format_ARGB32)
            self.state.home_logo = pm
            self.repaint_scoreboard()
    def set_period(self):
        try:
            self.state.period = int(self.period_spin.value())
        except Exception:
            pass
        self.repaint_scoreboard()
    def _read_clock_inputs(self):
        try:
            m = int(self.min_edit.value())
            s = int(self.sec_edit.value())
            if m < 0:
                m = 0
            if s < 0:
                s = 0
            if s > 59:
                s = s % 60
            return m, s
        except Exception:
            return self.state.minutes_soccer, self.state.seconds_soccer
    def set_lcd_clock_from_inputs(self):
        try:
            m = int(self.min_edit.value())
            s = int(self.sec_edit.value())
        except Exception:
            return
        if m < 0:
            m = 0
        if s < 0:
            s = 0
        if s > 59:
            s = s % 60
        self.state.minutes_soccer = m
        self.state.seconds_soccer = s
        if hasattr(self, "time_lcd"):
            self.time_lcd.display(f"{m:02d}:{s:02d}")
        self.repaint_scoreboard()
    def start_clock(self):
        m, s = self._read_clock_inputs()
        # store to state and start timer
        self.state.minutes_soccer = m
        self.state.seconds_soccer = s
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
        self.state.minutes_soccer = 40
        self.state.seconds_soccer = 0

        # Reset LCD
        if hasattr(self, "time_lcd"):
            self.time_lcd.display("40:00")

        # Reset spin boxes
        if hasattr(self, "min_edit"):
            self.min_edit.setValue(40)

        if hasattr(self, "sec_edit"):
            self.sec_edit.setValue(0)

        self.repaint_scoreboard()
    def game_tick(self):
        total = self.state.minutes_soccer * 60 + self.state.seconds_soccer
        if total <= 0:
            self.state.minutes_soccer = 0
            self.state.seconds_soccer = 0
            self.timer.stop()
            self.state.game_running = False

            self.time_lcd.display("00:00")
            self.repaint_scoreboard()
            return

        total -= 1
        self.state.minutes_soccer = total // 60
        self.state.seconds_soccer = total % 60
        self.time_lcd.display(f"{self.state.minutes_soccer}:{self.state.seconds_soccer:02d}")
        self.min_edit.setValue(self.state.minutes_soccer)
        self.sec_edit.setValue(self.state.seconds_soccer)

        self.repaint_scoreboard()
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
            pm = pm.scaled(180, 145, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.state.away_logo = pm
            self.repaint_scoreboard()

    def load_home_logo_from_setup(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open home logo", "", "Images (*.png *.jpg *.bmp)")
        if path:
            pm = QPixmap(path)
            pm = pm.scaled(180, 145, Qt.KeepAspectRatio, Qt.SmoothTransformation)
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
        self.serial_thread = None
