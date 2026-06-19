from shared.shared import *
class VolleyballScoreboard(QWidget, ScoreboardToolkit):
    def __init__(self, state: ScoreState, mode="transparent", parent=None):
        super().__init__(parent)
        self.state = state
        self.mode = mode
        self.flash_on = False
        self.show_volleyball_intro = False
        self.show_volleyball_breakboard = False
        self.show_volleyball_scorebug = True

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

        self.sets_font = QFont("College", 22, QFont.Bold)
        self.title_font = QFont("BigNoodleTitling", 20, QFont.Bold)
        self.timer_font = QFont("College", 30, QFont.Bold)
        self.setNumber_font = QFont("College", 18, QFont.Bold)
        self.set_font = QFont("College", 18, QFont.Bold)
        self.score_font = QFont("College", 25, QFont.Bold)
        self.record_font = QFont("College", 12, QFont.Bold)
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

    def force_repaint(self):
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

        if self.show_volleyball_intro:
            self.draw_volleyball_intro(p)

        if self.show_volleyball_scorebug:
            self.draw_volleyball_scorebug(p)

        if self.show_volleyball_breakboard:
            self.draw_volleyball_breakboard(p)
    def draw_volleyball_intro(self, p):
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
    def draw_volleyball_breakboard(self, p):
        pass
    def draw_volleyball_scorebug(self, p):
        left_x = 45
        left_w = 275
        right_x = 45
        right_w = 275
        sx = 275
        sw = 45
        sy = 10
        yx = 15
        yw = 35
        cx = 320
        cw = 65
        cy = 10
        rw = self.state.away_record_wins
        rl = self.state.away_record_losses
        dw = self.state.away_district_wins
        dl = self.state.away_district_losses
        hw = self.state.home_record_wins
        hl = self.state.home_record_losses
        hdw    = self.state.home_district_wins
        hdl    = self.state.home_district_losses
        self.draw_rect(p, left_x, 10, left_w, 50, self.state.away_color)
        logo_x, logo_y, logo_w, logo_h = left_x + 7, 13, 40, 45
        p.save()
        self.draw_logo_in_top_rounded_window(p,logo_x,logo_y,logo_w,logo_h,self.state.away_logo)
        p.restore()      
        p.setFont(self.record_font)
        p.setPen(Qt.white)
        if not (rw == 0 and rl == 0):
            p.drawText(left_x+155, 41, left_w - 20, 20, Qt.AlignLeft | Qt.AlignVCenter, f"{rw}-{rl}")
        if not (dw == 0 and dl == 0):
            p.drawText(left_x+185, 39, left_w - 20, 20, Qt.AlignLeft | Qt.AlignVCenter, f"({dw}-{dl})")
        p.setFont(self.title_font)
        p.setPen(Qt.white)
        p.drawText(left_x + 55, 20, left_w - 20, 25, Qt.AlignLeft | Qt.AlignVCenter, self.state.away_name)
        self.draw_vbtimeout_rects(p, left_x + 55, 53, self.state.away_timeouts_volleyball, align="right")
        self.draw_rect_transparent(p, sx, sy, sw, 50, QColor("#000000"))
        p.setFont(self.score_font)
        p.setPen(Qt.white)
        p.drawText(left_x+192, 2, 120, 70, Qt.AlignCenter, str(self.state.away_pts))

        ## -- HOME SECTION --
        self.draw_rect(p, right_x, 60, right_w, 50, self.state.home_color)
        logo_x, logo_y, logo_w, logo_h = right_x + 7, 65, 40, 45
        p.save()
        self.draw_logo_in_top_rounded_window(p,logo_x,logo_y,logo_w,logo_h,self.state.home_logo)
        p.restore()
        self.draw_vbtimeout_rects(p, right_x+55, 102, self.state.home_timeouts_volleyball, align="right")
        p.setFont(self.title_font)
        p.setPen(Qt.white)
        p.drawText(right_x+55, 70, right_w - 20, 25, Qt.AlignLeft | Qt.AlignVCenter, self.state.home_name)
        p.setFont(self.record_font)
        p.setPen(Qt.white)
        if not (hw == 0 and hl == 0):
            p.drawText(right_x+155, 91, right_w - 20, 20, Qt.AlignLeft | Qt.AlignVCenter, f"{hw}-{hl}")
        if not (hdw == 0 and hdl == 0):
            p.drawText(right_x+185, 89, right_w - 20, 20, Qt.AlignLeft | Qt.AlignVCenter, f"({hdw}-{hdl})")
        self.draw_rect_transparent(p, sx, sy+50, sw, 50, QColor("#000000"))
        p.setFont(self.score_font)
        p.setPen(Qt.white)
        p.drawText(right_x+192, 50, 120, 70, Qt.AlignCenter, str(self.state.home_pts))

        # -- CENTER SECTION -- #
        self.draw_rect(p, cx, cy, cw, 100, QColor("#2b2d2f"))
        p.drawText(cx, cy + 50, cw, 26, Qt.AlignCenter, f"{self.vbperiod_text()}")
        p.setFont(self.set_font)
        p.setPen(Qt.white)
        period = self.state.vbperiod
        period_text = self.vbperiod_text()
        if period == 6:
            p.drawText(cx, cy + 38, cw, 26, Qt.AlignCenter, period_text)
        else:
            p.drawText(cx, cy + 32, cw, 18, Qt.AlignCenter, "SET")
            p.drawText(cx, cy + 54, cw, 18, Qt.AlignCenter, self.vbperiod_text())    
        p.setFont(self.sets_font)
        p.setPen(Qt.white)
        home_sets = self.state.home_sets_won
        away_sets = self.state.away_sets_won
        both_zero = (home_sets == 0 and away_sets == 0)
        if not both_zero:
            self.draw_rect(p, yx, 10, yw, 100, QColor("#2b2d2f"))
            self.draw_center_line(p, yx, 10, yw, 198, QColor("#FFFFFF"), 2)
            self.draw_center_vertical_line(p, yx-16, 12, yw, 96, QColor("#FFFFFF"), 2)
            self.draw_center_line(p, yx, 10, yw, 2, QColor("#FFFFFF"), 2)
            self.draw_center_line(p, yx, 10, yw, 100, QColor("#FFFFFF"), 2)
            self.draw_center_line(p, yx+37, 10, yw+232, 100, QColor("#FFFFFF"), 2)
            self.draw_center_line(p, yx+37, 10, yw+297, 2,   QColor("#FFFFFF"), 2)
            self.draw_center_line(p, yx+37, 10, yw+297, 198, QColor("#FFFFFF"), 2)
            self.draw_center_vertical_line(p, yx+289, 12, yw, 96, QColor("#FFFFFF"), 2)
            self.draw_center_vertical_line(p, yx+353, 12, yw, 96, QColor("#FFFFFF"), 2)
            self.draw_center_vertical_line(p, yx+18,  12, yw, 96, QColor("#FFFFFF"), 2)
        if both_zero:
            self.draw_center_line(p, yx+31, 10, yw+238, 100, QColor("#FFFFFF"), 2)
            self.draw_center_line(p, yx+31, 10, yw+303, 2,   QColor("#FFFFFF"), 2)
            self.draw_center_line(p, yx+31, 10, yw+303, 198, QColor("#FFFFFF"), 2)
            self.draw_center_vertical_line(p, yx+289, 12, yw, 96, QColor("#FFFFFF"), 2)
            self.draw_center_vertical_line(p, yx+353, 12, yw, 96, QColor("#FFFFFF"), 2)
            self.draw_center_vertical_line(p, yx+14,  12, yw, 96, QColor("#FFFFFF"), 2)
        if away_sets != 0:
            p.drawText(yx-5, 2, 45, 70, Qt.AlignCenter, str(away_sets))
            p.drawText(yx-5, 50, 45, 70, Qt.AlignCenter, str(home_sets))
        if home_sets != 0:
            p.drawText(yx-5, 50, 45, 70, Qt.AlignCenter, str(home_sets))
            p.drawText(yx-5, 2, 45, 70, Qt.AlignCenter, str(away_sets))
    def draw_volleyball_final(self, p):
        left_x = 550
        left_w = 400
        right_x = 950
        right_w = 400
        cx = 750
        cw = 175
        cy = 865
        base_home = QColor(self.state.home_color).darker(160)
        base_away = QColor(self.state.away_color).darker(160)
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
            logo_y = 760
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
class VolleyballControl(QMainWindow):
    def __init__(self, state: ScoreState, scoreboard: VolleyballScoreboard):
        super().__init__()
        self.state = state
        self.title_font = QFont("BigNoodleTitling", 20, QFont.Bold)
        self.scoreboard = scoreboard
        version = beta_version if beta_mode else current_version

        self.setWindowTitle(
            f"Volleyball Scoreboard (Version: {version}"
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



        # ----------------- PAGE 1 CONTENT (kept same layout) -----------------
        btn_serial = QPushButton("Start Connection")
        btn_serial.clicked.connect(self.start_serial)
        grid.addWidget(btn_serial, 16, 3)
        btn_serial1 = QPushButton("Stop Connection")
        btn_serial1.clicked.connect(self.stop_serial)
        grid.addWidget(btn_serial1, 16, 4)
        grid.addWidget(QLabel("Away TO:"), 7, 0)
        self.away_to_lcd = QLCDNumber()
        self.away_to_lcd.setDigitCount(1)
        self.away_to_lcd.setSegmentStyle(QLCDNumber.Flat)
        self.away_to_lcd.display(self.state.away_timeouts_volleyball)
        self.away_to_lcd.setStyleSheet("""QLCDNumber { color: white;background-color: black;border: 2px solid #333;padding: 2px;}""")
        self.chk_district = QCheckBox("District Opponent")
        self.chk_district.setChecked(False)
        self.chk_district.stateChanged.connect(self.update_district_flag)
        self.chk_district.setStyleSheet("QCheckBox{color:white;} QCheckBox::indicator{width:15px;height:15px;border:2px solid white;background:#121212;} QCheckBox::indicator:checked{background:white;}")
        grid_info.addWidget(self.chk_district, 5, 0, 1 , 5)
        grid.addWidget(self.away_to_lcd, 7, 1)
        btn_away_use = QPushButton("-")
        btn_away_use.clicked.connect(lambda: self.change_timeout("away", -1))
        grid.addWidget(btn_away_use, 7, 2)
        btn_away_restore = QPushButton("+")
        btn_away_restore.clicked.connect(lambda: self.change_timeout("away", +1))
        grid.addWidget(btn_away_restore, 7, 3)
        grid.addWidget(QLabel("Home TO:"), 7, 4)
        self.home_to_lcd = QLCDNumber()
        self.home_to_lcd.setDigitCount(1)
        self.home_to_lcd.setSegmentStyle(QLCDNumber.Flat)
        self.home_to_lcd.display(self.state.home_timeouts_volleyball)
        self.home_to_lcd.setStyleSheet("""QLCDNumber { color: white;background-color: black;border: 2px solid #333;padding: 2px;}""")
        grid.addWidget(self.home_to_lcd, 7, 5)
        btn_home_use = QPushButton("-")
        btn_home_use.clicked.connect(lambda: self.change_timeout("home", -1))
        grid.addWidget(btn_home_use, 7, 6)
        btn_home_restore = QPushButton("+")
        btn_home_restore.clicked.connect(lambda: self.change_timeout("home", +1))
        grid.addWidget(btn_home_restore, 7, 7)
        grid.addWidget(QLabel("Away Score:"), 2, 0)
        self.aw_score_box = QSpinBox()
        self.aw_score_box.setRange(0, 999)
        self.aw_score_box.setValue(self.state.away_pts)
        self.aw_score_box.hide()    # <--- hide it from UI
        btn_aw_set = QPushButton("Set")
        btn_aw_set.clicked.connect(self.set_away_score)
        grid.addWidget(btn_aw_set, 2, 2)
        self.aw_lcd = QLCDNumber()
        self.aw_lcd.setDigitCount(3)
        self.aw_lcd.setSegmentStyle(QLCDNumber.Flat)
        self.aw_lcd.setStyleSheet("""QLCDNumber { color: white;background-color: black;border: 2px solid #333;padding: 4px;}""")
        grid.addWidget(self.aw_lcd, 2, 1, 1, 1)
        self.aw_score_box.valueChanged.connect(self.aw_lcd.display)
        self.aw_score_box.valueChanged.connect(self.on_away_score_changed)
        grid.addWidget(QLabel("Home Score:"), 2, 4)
        self.hm_score_box = QSpinBox()
        self.hm_score_box.setRange(0, 999)
        self.hm_score_box.setValue(self.state.home_pts)
        self.hm_score_box.hide()
        grid.addWidget(self.hm_score_box, 2, 5)
        btn_hm_set = QPushButton("Set")
        btn_hm_set.clicked.connect(self.set_home_score)
        grid.addWidget(btn_hm_set, 2, 6)
        self.hm_lcd = QLCDNumber()
        self.hm_lcd.setDigitCount(3)
        self.hm_lcd.setSegmentStyle(QLCDNumber.Flat)
        self.hm_lcd.setStyleSheet("""QLCDNumber { color: white;background-color: black;border: 2px solid #333;padding: 4px;}""")
        grid.addWidget(self.hm_lcd, 2, 5, 1, 1)
        self.hm_score_box.valueChanged.connect(self.hm_lcd.display)
        self.hm_score_box.valueChanged.connect(self.on_home_score_changed)
        grid.addWidget(QLabel("Away Sets:"), 3, 0)
        self.aw_sets_box = QSpinBox()
        self.aw_sets_box.setRange(0, 999)
        self.aw_sets_box.setValue(self.state.away_sets_won)
        btn_aw_sets = QPushButton("Set")
        btn_aw_sets.clicked.connect(self.set_away_sets)   # new function below
        grid.addWidget(btn_aw_sets, 3, 2)
        self.aw_sets_lcd = QLCDNumber()
        self.aw_sets_lcd.setDigitCount(3)
        self.aw_sets_lcd.setSegmentStyle(QLCDNumber.Flat)
        self.aw_sets_lcd.setStyleSheet("""QLCDNumber { color: white;background-color: black;border: 2px solid #333;padding: 4px;}""")
        grid.addWidget(self.aw_sets_lcd, 3, 1, 1, 1)
        self.aw_sets_box.valueChanged.connect(self.aw_sets_lcd.display)
        grid.addWidget(QLabel("Home Sets:"), 3, 4)
        self.hm_sets_box = QSpinBox()
        self.hm_sets_box.setRange(0, 999)
        self.hm_sets_box.setValue(self.state.home_sets_won)
        self.hm_sets_box.hide()
        btn_hm_sets = QPushButton("Set")
        btn_hm_sets.clicked.connect(self.set_home_sets)   # new function below
        grid.addWidget(btn_hm_sets, 3, 6)
        grid.addWidget(self.hm_sets_box, 3, 5)
        self.hm_sets_lcd = QLCDNumber()
        self.hm_sets_lcd.setDigitCount(3)
        self.hm_sets_lcd.setSegmentStyle(QLCDNumber.Flat)
        self.hm_sets_lcd.setStyleSheet("""QLCDNumber { color: white;background-color: black;border: 2px solid #333;padding: 4px;}""")
        grid.addWidget(self.hm_sets_lcd, 3, 5, 1, 1)
        self.hm_sets_box.valueChanged.connect(self.hm_sets_lcd.display)
        btn_away_plus1 = QPushButton("+1")
        btn_away_plus1.clicked.connect(lambda: self.add_points(1, "away"))
        grid.addWidget(btn_away_plus1, 0, 0)
        btn_away_minus1 = QPushButton("-1")
        btn_away_minus1.clicked.connect(lambda: self.add_points(-1, "away"))
        grid.addWidget(btn_away_minus1, 4, 0)
        btn_home_plus1 = QPushButton("+1")
        btn_home_plus1.clicked.connect(lambda: self.add_points(1, "home"))
        grid.addWidget(btn_home_plus1, 0, 4)
        btn_home_minus1 = QPushButton("-1")
        btn_home_minus1.clicked.connect(lambda: self.add_points(-1, "home"))
        grid.addWidget(btn_home_minus1, 4, 4)
        btn_away_set_plus1 = QPushButton("+1 Set")
        btn_away_set_plus1.clicked.connect(lambda: self.add_sets(1, "away"))
        grid.addWidget(btn_away_set_plus1, 0, 1)
        btn_away_set_minus1 = QPushButton("-1 Set")
        btn_away_set_minus1.clicked.connect(lambda: self.add_sets(-1, "away"))
        grid.addWidget(btn_away_set_minus1, 4, 1)
        btn_home_set_plus1 = QPushButton("+1 Set")
        btn_home_set_plus1.clicked.connect(lambda: self.add_sets(1, "home"))
        grid.addWidget(btn_home_set_plus1, 0, 5)
        btn_home_set_minus1 = QPushButton("-1 Set")
        btn_home_set_minus1.clicked.connect(lambda: self.add_sets(-1, "home"))
        grid.addWidget(btn_home_set_minus1, 4, 5)
        grid.addWidget(QLabel("Possession:"), 5, 3)
        btn_poss_none = QPushButton("None")
        btn_poss_none.clicked.connect(lambda: self.set_possession_direct(None))
        grid.addWidget(btn_poss_none, 5, 5)
        btn_poss_away = QPushButton("Away")
        btn_poss_away.clicked.connect(lambda: self.set_possession_direct("away"))
        grid.addWidget(btn_poss_away, 5, 4)
        btn_poss_home = QPushButton("Home")
        btn_poss_home.clicked.connect(lambda: self.set_possession_direct("home"))
        grid.addWidget(btn_poss_home, 5, 6)
        grid.addWidget(QLabel("Period:"), 5, 0)
        self.period_spin = QSpinBox()
        self.period_spin.setRange(1, 12)
        self.period_spin.setValue(self.state.period)
        grid.addWidget(self.period_spin, 5, 1)
        btn_set_periodv = QPushButton("Set Period")
        btn_set_periodv.clicked.connect(self.set_periodv)
        grid.addWidget(btn_set_periodv, 5, 2)
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
        
        def style_children(w):
            for c in w.findChildren(QWidget):
                if not isinstance(c, QLCDNumber):
                    c.setStyleSheet("QLabel{color:white;} QPushButton,QLineEdit,QSpinBox,QCheckBox{background:white;color:black;} QCheckBox::indicator{background:white;}")

        style_children(page1)
        style_children(page2)
        style_children(page3)
        style_children(page4)


    # ----- PAGE 1 slots & helpers (kept same behavior) -----
    def on_home_score_changed(self, value):
        self.state.home_pts = value
        self.check_set_win()
        self.repaint_scoreboard()


    def on_away_score_changed(self, value):
        self.state.away_pts = value
        self.check_set_win()
        self.repaint_scoreboard()

    def start_serial(self):
        if getattr(self.state, "serial_thread", None) and self.state.serial_thread.is_alive():
            QMessageBox.warning(self, "Scoreboard", "Serial thread is already running")
            return
        self.state.serial_enabled = True
        self.state.serial_thread = shared.ScoreboardReader(self.state,parsers=[shared.DaktronicsParser(), shared.NevcoParser(), shared.FairPlayParser()])
        self.state.serial_thread.start()
        QMessageBox.information(self, "Scoreboard", "Serial connection started")
    def stop_serial(self):
        print("[Dak] Stop requested")

    # disable further reading
        self.state.serial_enabled = False

        t = self.state.serial_thread

        if t:
            try:
            # call reader.stop() if implemented
                if hasattr(t, "stop"):
                    t.stop()
            except Exception as e:
                print("[Dak] stop() error:", e)

            try:
                t.join(timeout=1)
                print("[Dak] Thread joined")
            except Exception as e:
                print("[Dak] join() error:", e)

    # clear pointer so we know it's stopped
        self.state.serial_thread = None

        QMessageBox.information(self, "Daktronics", "Serial connection stopped.")
     
    def repaint_scoreboard(self):
        self.scoreboard.update()

    def set_possession_direct(self, team):
        self.state.possession = team
        self.repaint_scoreboard()
    def set_away_name(self):
        text = self.away_name_edit.text().strip() or "AWAY"
        metrics = self.fontMetrics()
        if metrics.horizontalAdvance(text) > 175:
            QMessageBox.warning(self, "Name Too Long", "The away team name is too long.\nPlease enter a shorter name.")
            return
        self.state.away_name = text
        self.repaint_scoreboard()

    def set_home_name(self):
        text = self.home_name_edit.text().strip() or "HOME"
        metrics = self.fontMetrics()
        if metrics.horizontalAdvance(text) > 175:
            QMessageBox.warning(self, "Name Too Long", "The home team name is too long.\nPlease enter a shorter name.")
            return
        self.state.home_name = text
        self.repaint_scoreboard()
    def set_away_score(self):
        try:
            self.state.away_pts = int(self.aw_score_box.value())
        except Exception:
            pass

    # auto check for set win
        self.check_set_win()

        self.repaint_scoreboard()   
    def set_away_sets(self):
        try:
            self.state.away_sets_won = int(self.away_sets_box.value())
        except Exception:
            pass

        self.repaint_scoreboard()
    def check_set_win(self):
        home = self.state.home_pts
        away = self.state.away_pts
        period = self.state.period  # set number

    # Target points
        target = 15 if period == 5 else 25

    # Home wins set
        if home >= target and (home - away) >= 2:
            self.state.home_sets_won += 1
            self.start_new_set()
            return

    # Away wins set
        if away >= target and (away - home) >= 2:
            self.state.away_sets_won += 1
            self.start_new_set()
            return


    def update_district_flag(self, state):
        # checkbox checked = district game
        self.state.is_district_game = (state == Qt.Checked)

    def set_home_score(self):
        try:
            self.state.home_pts = int(self.hm_score_box.value())
        except Exception:
            pass

    # auto check for set win
        self.check_set_win()

        self.repaint_scoreboard()
    def reset_points(self):
        self.state.home_pts = 0
        self.state.away_pts = 0

    # also reset UI spinboxes
        self.hm_score_box.setValue(0)
        self.aw_score_box.setValue(0)

    def set_home_sets(self):
        try:
            self.state.home_sets_won = int(self.home_sets_box.value())
        except Exception:
            pass

        self.repaint_scoreboard()
    def start_new_set(self):
    # bump set period
        self.state.period += 1

    # reset points
        self.state.home_pts = 0
        self.state.away_pts = 0
        self.hm_lcd.display(0)
        self.aw_lcd.display(0)
    # reset timeouts
        self.state.home_timeouts_volleyball = 2
        self.state.away_timeouts_volleyball = 2

    # update timeouts LCDs
        if hasattr(self, "home_to_lcd"):
            self.home_to_lcd.display(2)
        if hasattr(self, "away_to_lcd"):
            self.away_to_lcd.display(2)

    # update period spin widget too if exists
        if hasattr(self, "period_spin"):
            self.period_spin.setValue(self.state.period)

        self.repaint_scoreboard()


    def add_points(self, pts, team):
        if team == "home":
            self.state.home_pts = max(0, self.state.home_pts + pts)
        else:
            self.state.away_pts = max(0, self.state.away_pts + pts)
        self.hm_score_box.setValue(self.state.home_pts)
        self.aw_score_box.setValue(self.state.away_pts)
        self.repaint_scoreboard()

    def add_sets(self, delta, team):
        if team == "home":
            self.state.home_sets_won = max(0, self.state.home_sets_won + delta)
        else:
            self.state.away_sets_won = max(0, self.state.away_sets_won + delta)

        self.repaint_scoreboard()  # redraw screen

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
    def change_timeout(self, team, delta):
        if team == "away":
            self.state.away_timeouts_volleyball = max(0, min(2, self.state.away_timeouts_volleyball + delta))
            self.away_to_lcd.display(self.state.away_timeouts_volleyball)
        else:
            self.state.home_timeouts_volleyball = max(0, min(2, self.state.home_timeouts_volleyball + delta))
            self.home_to_lcd.display(self.state.home_timeouts_volleyball)
        if self.timer.isActive():
            self.timer.stop()
            self.state.game_running = False
        self.time_lcd.display(f"{self.state.minutes_basketball:02d}:{self.state.seconds_basketball:02d}")
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

    def set_periodv(self):
        try:
            self.state.period = int(self.period_spin.value())
        except Exception:
            pass
            
        if hasattr(self, "home_to_lcd"):
            self.home_to_lcd.display(2)
            self.state.home_timeouts_volleyball = 2
            self.state.away_timeouts_volleyball = 2
        if hasattr(self, "away_to_lcd"):
            self.away_to_lcd.display(2)
            self.state.home_timeouts_volleyball = 2
            self.state.away_timeouts_volleyball = 2
            self.repaint_scoreboard()
            return



        self.repaint_scoreboard()



    # Helper: read minutes & seconds from either min_spin/sec_spin OR a single time_edit "MM:SS"
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

    # clamp
        if m < 0:
            m = 0
        if s < 0:
            s = 0
        if s > 59:
            s = s % 60

    # update state
        self.state.minutes_basketball = m
        self.state.seconds_basketball = s

    # update LCD
        if hasattr(self, "time_lcd"):
            self.time_lcd.display(f"{m:02d}:{s:02d}")

    # optional scoreboard redraw
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
            pm = pm.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.state.away_logo = pm
            self.repaint_scoreboard()

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
