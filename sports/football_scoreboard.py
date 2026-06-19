from shared.shared import *
logging.basicConfig(filename='serieshistory_debug.log', level=logging.DEBUG, format='%(asctime)s %(message)s')

class FootballScoreboard(QWidget, ScoreboardToolkit):
    def __init__(self, state: "ScoreState", mode="transparent", parent=None):
        super().__init__(parent)

        self.state = state
        self.show_playclock = True
        self.show_intro = True
        self.mode = mode
        self.show_scorebug = False
        self.show_breakboard = False
        self.show_football_final = False
        self.show_home_touchdown = False
        self.show_away_touchdown = False
        self.show_weather = False
        self.show_lower3rd = False
        self.show_crew = False
        self.show_crew3 = False
        self.show_serieshistory = False
        self.show_crew4 = False
        self.setMinimumSize(1920, 1080)
        self.resize(1920, 1080)

        if self.mode == "transparent":
            self.setAttribute(Qt.WA_TranslucentBackground)
            self.setAttribute(Qt.WA_NoSystemBackground, True)
            self.setAttribute(Qt.WA_OpaquePaintEvent, False)
        else:
            self.bg_color = QColor(255, 0, 255)

        self.setAutoFillBackground(False)

        ui_updater.refresh.connect(self.force_repaint)

        self.monument_font = QFont("Monument Extended", 40)
        self.mascot_font = QFont("College", 33, QFont.Bold)
        self.big_font = QFont("College", 40, QFont.Bold)
        self.mid_font = QFont("College", 22, QFont.Bold)
        self.small_font = QFont("College", 14)
        self.title_font = QFont("BigNoodleTitling", 16, QFont.Bold)
        self.stitle_font = QFont("Legacy", 22, QFont.Bold)     
        self.tdtitle_font = QFont("BigNoodleTitling", 28, QFont.Bold)
        self.introtitle_font = QFont("BigNoodleTitling", 33, QFont.Bold)
        self.introupper_font = QFont("BigNoodleTitling", 25, QFont.Bold)
        self.rank_font = QFont("BigNoodleTitling", 14)
        self.srank_font = QFont("Legacy", 20)
        self.tdrank_font = QFont("BigNoodleTitling", 16)
        self.introrank_font = QFont("BigNoodleTitling", 30)
        self.introschool_font = QFont("BigNoodleTitling", 30, QFont.Bold)
        self.introcity_font = QFont("BigNoodleTitling", 22, QFont.Bold)
        self.timer_font = QFont("Legacy", 35, QFont.Bold)
        self.bbtimer_font = QFont("Legacy", 15)
        self.period_font = QFont("Legacy", 25, QFont.Bold)
        self.bbperiod_font = QFont("Legacy", 15)
        self.dd_font = QFont("Legacy", 28, QFont.Bold)
        self.pc_font = QFont("Legacy", 25, QFont.Bold)
        self.score_font = QFont("Octin Sports", 50, QFont.Bold)
        self.final_font = QFont("BigNoodleTitling", 40, QFont.Bold)
        self.bbscore_font = QFont("Octin Sports", 55, QFont.Bold)
        self.event_font = QFont("Legacy", 22, QFont.Bold)
        self.td_font = QFont("Octin Sports", 44, QFont.Bold)
        self.record_font = QFont("College", 17, QFont.Bold)
        self.introrecord_font = QFont("College", 24, QFont.Bold)
        self.weather_font = QFont("Legacy", 12, QFont.Bold)
        self.mainweather_font = QFont("Legacy", 18, QFont.Bold)
        self.center_logo_label = QLabel(self)
        self.center_logo_label.setAlignment(Qt.AlignCenter)
        self.smalltitle_font = QFont("Legacy", 30, QFont.Bold)
        self.bigtitle_font = QFont("Legacy", 50, QFont.Bold)
        self.lower3rd_font = QFont("Legacy", 30, QFont.Bold)
        self.shscore_font = QFont("Octin Sports", 80, QFont.Bold)
        self.request_logo_file()
    def force_repaint(self):
        self.repaint()
    def request_logo_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self,"Select Center Logo","","Image Files (*.png *.jpg *.jpeg *.bmp *.gif)")
        if file_path:
            self._load_center_logo(file_path)
    def _load_center_logo(self, file_path: str = ""):
        if not file_path:
            return
        pixmap = QPixmap(file_path)
        if pixmap.isNull():
            QMessageBox.warning(self,"Error","Failed to load image from the selected file.")
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
        p.setRenderHints(QPainter.Antialiasing |QPainter.TextAntialiasing)
        scale = min(self.width() / DESIGN_W,self.height() / DESIGN_H )
        offset_x = (self.width() - DESIGN_W * scale) / 2
        offset_y = (self.height() - DESIGN_H * scale) / 2
        p.translate(offset_x, offset_y)
        p.scale(scale, scale)
        if self.mode == "keyable":
            p.fillRect(0, 0, DESIGN_W, DESIGN_H, self.bg_color)
        if self.show_intro:
            self.draw_intro(p)
        if self.show_scorebug and not ( self.state.home_touchdown_active or self.state.away_touchdown_active):
            self.draw_scorebug(p)
        if self.show_home_touchdown:
            self.draw_home_touchdown(p)
        if self.show_away_touchdown:
            self.draw_away_touchdown(p)
        if self.show_breakboard:
            self.draw_breakboard(p)
        if self.show_weather:
            self.draw_weather(p)
        if self.show_lower3rd:
            self.draw_lower3rd(p)
        if self.show_crew:
            self.draw_crew(p)
        if self.show_crew3:
            self.draw_3man_crew(p)
        if self.show_crew4:
            self.draw_4man_crew(p)
        if self.show_football_final:
            self.draw_football_final(p)
        if self.show_serieshistory:
            self.draw_serieshistory(p)
        return
    def draw_weather(self,p):
        if self.state.weather_active:
            progress=self.state.weather_progress
            alpha=min(max((progress-0.7)/0.2,0.0),1.0)if progress>0.7 else 0.0
            left_x,left_w=60,520
            base_x=left_x-20
            big_w_full=260
            big_h_full=260
            small_w_full,small_h_full=220,25
            big_w=int(big_w_full*progress)
            big_h=int(big_h_full*progress)
            small_w=int(small_w_full*progress)
            small_h=int(small_h_full*progress)
            base_y=1015
            big_x,big_y=base_x,base_y-big_h
            small_x=big_x+(big_w_full-small_w_full)//2
            small_y=big_y-12-small_h
            if big_w>0 and big_h>0:
                self.draw_weather_rect(p,big_x,big_y,big_w,big_h)
            if small_w>0 and small_h>0:
                self.draw_weather_rect(p,small_x,small_y,small_w,small_h)
                p.save()
                p.setOpacity(alpha)
                p.setFont(self.weather_font)
                p.setPen(Qt.white)
                p.drawText(small_x,small_y,small_w,small_h,Qt.AlignCenter,"TONIGHT'S WEATHER")
                p.restore()
            if big_w>0 and big_h>0:
                pad_x=10
                top_y=big_y+18
                gap=55
                labels=["TEMP:","HUMIDITY:","WIND:","CONDITION:"]
                values=[f"{self.state.weather_temp}°F",f"{self.state.weather_humidity}%",f"{self.state.weather_wind} MPH",self.state.weather_condition]
                p.setFont(self.mainweather_font)
                p.setPen(Qt.white)
                fm=QFontMetrics(self.mainweather_font)
                text_h=fm.height()
                for i in range(4):
                    y=top_y+(i*gap)
                    line_y=y+text_h+6
                    text=f"{labels[i]} {values[i]}"
                    self.draw_line(p,big_x+6,line_y,big_x+big_w-6,line_y,QColor("white"),2)
                    p.save()
                    p.setOpacity(alpha)
                    p.drawText(big_x+pad_x,y,big_w-16,text_h,Qt.AlignLeft|Qt.AlignVCenter,text)
                    p.restore()
                p.save()
                p.setOpacity(alpha)
                p.setFont(self.weather_font)
                p.setPen(Qt.white)
                p.drawText(big_x+pad_x,big_y+big_h-30,big_w-16,25,Qt.AlignLeft|Qt.AlignVCenter,self.event_location_city_text or "")
                p.restore()
    def draw_lower3rd(self,p):
        if self.state.lower3rd_active:
            progress=max(0.0,min(1.0,self.state.lower3rd_progress))
            alpha=min(max((progress-0.4)/0.3,0.0),1.0)
            left_x,left_w=70,520
            base_x=left_x-20
            big_w_full,big_h_full=770,110
            small_w_full,small_h_full=453,34
            big_w=int(big_w_full*progress)
            small_w=int(small_w_full*progress)
            big_h=big_h_full
            small_h=small_h_full
            base_y=1015
            big_x=base_x
            big_y=base_y-big_h_full
            small_x=big_x+(big_w_full-small_w_full)//2
            small_y=big_y-12-small_h_full
            full_big_rect_w=big_w_full
            full_small_rect_w=small_w_full
            fixed_big_h=big_h_full
            fixed_small_h=small_h_full
            logo=(getattr(self.state,"home_logo",None) if getattr(self.state,"team_side","center")=="home"
                else getattr(self.state,"away_logo",None) if self.state.team_side=="away"
                else getattr(self.state,"center_logo",None))
            scale=(1.4 if logo and max(logo.width(),logo.height())<250
                else 1.2 if logo and max(logo.width(),logo.height())<500
                else 1.0)
            base_w=125
            base_h=130
            logo_w=int(base_w*scale)
            logo_h=int(base_h*scale)
            logo_x=big_x-(logo_w//2)
            logo_y=big_y+((big_h_full-logo_h)//2)
            if big_w>0:
                self.draw_lower3rd_rect(p,big_x,big_y,big_w,big_h)
            if small_w>0:
                self.draw_lower3rd_rect(p,small_x,small_y,small_w,small_h)
            if big_w>0 and logo:
                p.save()
                self.draw_logo_in_top_rounded_window(p,logo_x,logo_y,logo_w,logo_h,logo)
                p.restore()
            if small_w>0:
                p.save()
                p.setOpacity(alpha)
                p.setFont(self.smalltitle_font)
                p.setPen(Qt.white)
                small_title=self.state.lower3rdsmalltitle or ""
                p.drawText(small_x,small_y,full_small_rect_w,fixed_small_h,Qt.AlignCenter,small_title)
                p.restore()
            if big_w>0:
                p.save()
                p.setOpacity(alpha)
                p.setFont(self.bigtitle_font)
                p.setPen(Qt.white)
                title_pad_top=15
                title_pad_bottom=45
                text_x=big_x+90
                text_y=big_y+title_pad_top-5
                text_h=fixed_big_h-title_pad_top-title_pad_bottom+5
                big_title=self.state.lower3rdbigtitle or ""
                p.drawText(text_x,text_y,full_big_rect_w-100,text_h,Qt.AlignLeft|Qt.AlignVCenter,big_title)
                p.restore()
            if big_w>0:
                p.save()
                p.setOpacity(alpha)
                p.setFont(self.lower3rd_font)
                p.setPen(Qt.white)
                text_x=big_x+90
                text_y=big_y+big_h_full-28
                text_w=full_big_rect_w-110
                p.drawText(text_x,text_y,text_w,30,Qt.AlignLeft|Qt.AlignVCenter,self.state.lower3rd_text or "")
                p.restore()
    def draw_crew(self,p):
        if self.state.crew_active:
            progress=self.state.crew_progress
            progress=max(0.0,min(1.0,progress))
            alpha=min(max((progress-0.7)/0.2,0.0),1.0)if progress>0.7 else 0.0
            screen_w=1920
            center_x=screen_w//2
            big_w_full,big_h_full=600,50
            small_w_full,small_h_full=320,25
            big_w=int(big_w_full*progress)
            big_h=int(big_h_full*progress)
            small_w=int(small_w_full*progress)
            small_h=int(small_h_full*progress)
            big_x=center_x-(big_w_full//2)
            small_x=center_x-(small_w_full//2)
            base_y=1015
            big_y=base_y-big_h
            small_y=big_y+big_h+3
            if small_w>0 and small_h>0:
                self.draw_crew_rect(p,small_x,small_y,small_w,small_h)
                p.save()
                p.setOpacity(alpha)
                p.setFont(self.weather_font)
                p.setPen(Qt.white)
                p.drawText(small_x,small_y,small_w,small_h,Qt.AlignCenter,"TONIGHT'S ANNOUNCERS")
                p.restore()
            if big_w>0 and big_h>0:
                self.draw_crew_rect(p,big_x,big_y,big_w,big_h)
                logo_size=36
                logo_center_x=center_x
                logo_y=big_y+6
                logo_zone_w=90
                left_logo_line_x=logo_center_x-(logo_zone_w//2)
                right_logo_line_x=logo_center_x+(logo_zone_w//2)
                self.draw_line(p,left_logo_line_x,big_y+6,left_logo_line_x,big_y+big_h-6,QColor("white"),2)
                self.draw_line(p,right_logo_line_x,big_y+6,right_logo_line_x,big_y+big_h-6,QColor("white"),2)
                left_area_x=big_x
                left_area_w=left_logo_line_x-big_x
                right_area_x=right_logo_line_x
                right_area_w=(big_x+big_w_full)-right_logo_line_x
                labels=["PLAY BY PLAY","COLOR COMMENTATOR"]
                names=[self.state.crew_playbyplay_name or "---",self.state.crew_color_name or "---"]
                label_y=big_y+big_h-20
                name_y=label_y-18
                p.save()
                p.setOpacity(alpha)
                p.setPen(Qt.white)
                p.setFont(self.weather_font)
                p.drawText(left_area_x,label_y,left_area_w,20,Qt.AlignCenter,labels[0])
                p.drawText(right_area_x,label_y,right_area_w,20,Qt.AlignCenter,labels[1])
                p.setFont(self.mainweather_font)
                p.drawText(left_area_x,name_y,left_area_w,20,Qt.AlignCenter,names[0])
                p.drawText(right_area_x,name_y,right_area_w,20,Qt.AlignCenter,names[1])
                if getattr(self.state,"center_logo",None):
                    p.save()
                    self.draw_logo_in_top_rounded_window(p,logo_center_x-logo_size//2,logo_y,logo_size,logo_size,self.state.center_logo)
                    p.restore()
                p.restore()
    def draw_3man_crew(self,p):
        if self.state.crew3_active:
            progress=self.state.crew3_progress
            progress=max(0.0,min(1.0,progress))
            alpha=min(max((progress-0.7)/0.2,0.0),1.0)if progress>0.7 else 0.0
            screen_w=1920
            center_x=screen_w//2
            big_w_full,big_h_full=900,50
            small_w_full,small_h_full=320,25
            big_w=int(big_w_full*progress)
            big_h=int(big_h_full*progress)
            small_w=int(small_w_full*progress)
            small_h=int(small_h_full*progress)
            big_x=center_x-(big_w_full//2)
            small_x=center_x-(small_w_full//2)
            base_y=1015
            big_y=base_y-big_h
            small_y=big_y+big_h+3
            if small_w>0 and small_h>0:
                self.draw_crew_rect(p,small_x,small_y,small_w,small_h)
                p.save()
                p.setOpacity(alpha)
                p.setFont(self.weather_font)
                p.setPen(Qt.white)
                p.drawText(small_x,small_y,small_w,small_h,Qt.AlignCenter,"TONIGHT'S TEAM")
                p.restore()
            if big_w>0 and big_h>0:
                self.draw_crew_rect(p,big_x,big_y,big_w,big_h)
                third=big_w_full//3
                left_area_x=big_x
                mid_area_x=big_x+third
                right_area_x=big_x+(third*2)
                col_w=third
                labels=["DIRECTOR","TECHNICAL DIRECTOR","CAMERA OPERATOR"]
                names=[self.state.crew_director_name or "---",self.state.crew_td_name or "---",self.state.crew_camera_name or "---"]
                label_y=big_y+big_h-20
                name_y=label_y-18
                p.save()
                p.setOpacity(alpha)
                self.draw_line(p,big_x+third,big_y+6,big_x+third,big_y+big_h-6,QColor("white"),2)
                self.draw_line(p,big_x+(third*2),big_y+6,big_x+(third*2),big_y+big_h-6,QColor("white"),2)
                p.setPen(Qt.white)
                p.setFont(self.weather_font)
                p.drawText(left_area_x,label_y,col_w,20,Qt.AlignCenter,labels[0])
                p.drawText(mid_area_x,label_y,col_w,20,Qt.AlignCenter,labels[1])
                p.drawText(right_area_x,label_y,col_w,20,Qt.AlignCenter,labels[2])
                p.setFont(self.mainweather_font)
                p.drawText(left_area_x,name_y,col_w,20,Qt.AlignCenter,names[0])
                p.drawText(mid_area_x,name_y,col_w,20,Qt.AlignCenter,names[1])
                p.drawText(right_area_x,name_y,col_w,20,Qt.AlignCenter,names[2])
                p.restore()
    def draw_4man_crew(self,p):
        if self.state.crew4_active:
            progress=self.state.crew4_progress
            progress=max(0.0,min(1.0,progress))
            alpha=min(max((progress-0.7)/0.2,0.0),1.0)if progress>0.7 else 0.0
            screen_w=1920
            center_x=screen_w//2
            big_w_full,big_h_full=1200,50
            small_w_full,small_h_full=320,25
            big_w=int(big_w_full*progress)
            big_h=int(big_h_full*progress)
            small_w=int(small_w_full*progress)
            small_h=int(small_h_full*progress)
            big_x=center_x-(big_w_full//2)
            small_x=center_x-(small_w_full//2)
            base_y=1015
            big_y=base_y-big_h
            small_y=big_y+big_h+3
            if small_w>0 and small_h>0:
                self.draw_crew_rect(p,small_x,small_y,small_w,small_h)
                p.save()
                p.setOpacity(alpha)
                p.setFont(self.weather_font)
                p.setPen(Qt.white)
                p.drawText(small_x,small_y,small_w,small_h,Qt.AlignCenter,"TONIGHT'S TEAM")
                p.restore()
            if big_w>0 and big_h>0:
                self.draw_crew_rect(p,big_x,big_y,big_w,big_h)
                quad=big_w_full//4
                col1_x=big_x
                col2_x=big_x+quad
                col3_x=big_x+(quad*2)
                col4_x=big_x+(quad*3)
                col_w=quad
                labels=["DIRECTOR","TECHNICAL DIRECTOR","CAMERA OPERATOR","FIELD CAMERA OPERATOR"]
                names=[self.state.crew_director_name or "---",self.state.crew_td_name or "---",self.state.crew_camera_name or "---",self.state.crew_field_camera_name or "---"]
                label_y=big_y+big_h-20
                name_y=label_y-18
                p.save()
                p.setOpacity(alpha)
                self.draw_line(p,big_x+quad,big_y+6,big_x+quad,big_y+big_h-6,QColor("white"),2)
                self.draw_line(p,big_x+(quad*2),big_y+6,big_x+(quad*2),big_y+big_h-6,QColor("white"),2)
                self.draw_line(p,big_x+(quad*3),big_y+6,big_x+(quad*3),big_y+big_h-6,QColor("white"),2)
                p.setPen(Qt.white)
                p.setFont(self.weather_font)
                p.drawText(col1_x,label_y,col_w,20,Qt.AlignCenter,labels[0])
                p.drawText(col2_x,label_y,col_w,20,Qt.AlignCenter,labels[1])
                p.drawText(col3_x,label_y,col_w,20,Qt.AlignCenter,labels[2])
                p.drawText(col4_x,label_y,col_w,20,Qt.AlignCenter,labels[3])
                p.setFont(self.mainweather_font)
                p.drawText(col1_x,name_y,col_w,20,Qt.AlignCenter,names[0])
                p.drawText(col2_x,name_y,col_w,20,Qt.AlignCenter,names[1])
                p.drawText(col3_x,name_y,col_w,20,Qt.AlignCenter,names[2])
                p.drawText(col4_x,name_y,col_w,20,Qt.AlignCenter,names[3])
                p.restore()
    def draw_keysyovictory(self, p):
        pass
    def draw_serieshistory(self, p):
        if not self.state.series_history_active:
            return
        import logging
        log = logging.getLogger("serieshistory")
        if not log.handlers:
            fh = logging.FileHandler("serieshistory_debug.log")
            fh.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
            log.addHandler(fh)
            log.setLevel(logging.DEBUG)
        progress = max(0.0, min(1.0, self.state.series_history_progress))
        logo_alpha = min(max((progress - 0.7) / 0.3, 0.0), 1.0)
        content_alpha = 1.0 if progress >= 0.99 else 0.0
        log.debug(f"progress={progress} logo_alpha={logo_alpha} content_alpha={content_alpha}")
        center_x = 960
        rect_w_full = 863
        top_h_full = 138
        body_h_full = 322
        top_w = int(rect_w_full * progress)
        body_w = int(rect_w_full * progress)
        top_x = center_x - (top_w // 2)
        body_x = center_x - (body_w // 2)
        full_top_x = center_x - (rect_w_full // 2)
        full_body_x = center_x - (rect_w_full // 2)
        base_y = 740
        body_y = base_y - body_h_full
        top_y = body_y - top_h_full - 9
        log.debug(f"top_w={top_w} body_w={body_w} top_x={top_x} top_y={top_y} body_x={body_x} body_y={body_y}")
        if top_w > 0:
            p.save()
            self.draw_sh(p, top_x, top_y, top_w, top_h_full)
            p.restore()
        if body_w > 0:
            p.save()
            self.draw_sh(p, body_x, body_y, body_w, body_h_full)
            p.restore()
        away_logo_x = full_top_x
        away_logo_y = top_y
        away_logo_w = 150
        away_logo_h = top_h_full
        home_logo_x = full_top_x + rect_w_full - 150
        home_logo_y = top_y
        home_logo_w = 150
        home_logo_h = top_h_full
        if top_w > 0:
            log.debug(f"drawing color rects away_color={self.state.away_color} home_color={self.state.home_color}")
            p.save()
            p.setOpacity(logo_alpha)
            self.draw_1fully_rounded_rect(p, away_logo_x, away_logo_y, away_logo_w, away_logo_h, self.state.away_color)
            self.draw_1fully_rounded_rect(p, home_logo_x, home_logo_y, home_logo_w, home_logo_h, self.state.home_color)
            p.restore()
        if top_w > 0:
            log.debug(f"drawing away logo away_logo={self.state.away_logo}")
            p.save()
            p.setOpacity(logo_alpha)
            self.draw_logo_in_top_rounded_window(p, away_logo_x + 17, away_logo_y + 12, away_logo_w - 35, away_logo_h - 23, self.state.away_logo)
            p.restore()
        if top_w > 0:
            log.debug(f"drawing home logo home_logo={self.state.home_logo}")
            p.save()
            p.setOpacity(logo_alpha)
            self.draw_logo_in_top_rounded_window(p, home_logo_x + 17, home_logo_y + 12, home_logo_w - 35, home_logo_h - 23, self.state.home_logo)
            p.restore()
        if top_w > 0:
            log.debug(f"drawing scores away={self.state.series_away_score} home={self.state.series_home_score}")
            p.save()
            try:
                p.setOpacity(1.0 if progress >= 0.99 else 0.0)
                p.setPen(Qt.white)
                p.setFont(self.shscore_font)
                p.drawText(full_top_x + 167, top_y, 138, top_h_full, Qt.AlignCenter, str(self.state.series_away_score))
                p.drawText(full_top_x + rect_w_full - 305, top_y, 138, top_h_full, Qt.AlignCenter, str(self.state.series_home_score))
                log.debug("scores drawn successfully")
            except Exception:
                log.exception("scores draw failed")
            finally:
                p.restore()
        if top_w > 0:
            log.debug(f"drawing X at x={full_top_x + (rect_w_full // 2) - 17} y={top_y + 46}")
            p.save()
            try:
                p.setOpacity(content_alpha)
                self.draw_x(p, full_top_x + (rect_w_full // 2) - 17, top_y + 46, 35, 35, 6)
                log.debug("X mark drawn successfully")
            except Exception:
                log.exception("X mark draw failed")
            finally:
                p.restore()
        line1_y = body_y + 69
        line2_y = body_y + 150
        line3_y = body_y + 230
        if body_w > 0:
            log.debug(f"drawing lines at line1_y={line1_y} line2_y={line2_y} line3_y={line3_y}")
            p.save()
            p.setOpacity(content_alpha)
            self.draw_line(p, full_body_x + 29, line1_y, full_body_x + rect_w_full - 29, line1_y, QColor("white"), 2)
            self.draw_line(p, full_body_x + 29, line2_y, full_body_x + rect_w_full - 29, line2_y, QColor("white"), 2)
            self.draw_line(p, full_body_x + 29, line3_y, full_body_x + rect_w_full - 29, line3_y, QColor("white"), 2)
            p.restore()
        if body_w > 0:
            label = "LAST MEETING"
            date_text = self.state.series_date or ""
            combined = f"{label}  —  {date_text}" if date_text else label
            log.debug(f"drawing header '{combined}'")
            p.save()
            try:
                p.setOpacity(content_alpha)
                p.setPen(Qt.white)
                p.setFont(self.mainweather_font)
                p.drawText(full_body_x, body_y + 9, rect_w_full, 46, Qt.AlignCenter, combined)
                log.debug("header text drawn successfully")
            except Exception:
                log.exception("header text draw failed")
            finally:
                p.restore()
        def draw_auto_text(text, cell_x, cell_y, cell_w, cell_h):
            if not text:
                log.debug(f"draw_auto_text skipped empty text at cell_x={cell_x} cell_y={cell_y}")
                return
            try:
                font = QFont(self.mainweather_font)
                fm = QFontMetrics(font)
                while fm.horizontalAdvance(str(text)) > cell_w - 23 and font.pointSizeF() > 6:
                    font.setPointSizeF(font.pointSizeF() - 0.5)
                    fm = QFontMetrics(font)
                log.debug(f"draw_auto_text '{text}' font_size={font.pointSizeF()}")
                p.save()
                p.setOpacity(content_alpha)
                p.setFont(font)
                p.setPen(Qt.white)
                p.drawText(cell_x, cell_y, cell_w, cell_h, Qt.AlignCenter, str(text))
                p.restore()
                log.debug(f"draw_auto_text '{text}' drawn successfully")
            except Exception:
                log.exception(f"draw_auto_text failed for '{text}'")
        cell_w = rect_w_full
        cell_h = 63
        if body_w > 0:
            draw_auto_text(self.state.series_stat1, full_body_x, line1_y + 6, cell_w, cell_h)
            draw_auto_text(self.state.series_stat2, full_body_x, line2_y + 6, cell_w, cell_h)
            draw_auto_text(self.state.series_stat3, full_body_x, line3_y + 6, cell_w, cell_h)


    def draw_intro(self, p):
        left_x = 310
        left_w = 520
        right_x = 1007
        right_w = 500
        cx = 830
        cw = 175 
        darker_home = self.state.home_color.darker(175)
        lighter_home = self.state.home_color.lighter(125)
        darker_away = self.state.away_color.darker(175)
        lighter_away = self.state.away_color.lighter(125)
        hw = self.state.home_record_wins
        hl = self.state.home_record_losses
        hdw    = self.state.home_district_wins
        hdl    = self.state.home_district_losses
        rw = self.state.away_record_wins
        rl = self.state.away_record_losses
        dw = self.state.away_district_wins
        dl = self.state.away_district_losses
 # -- AWAY SECTION -- #
        if self.state.awayintro_active:
            progress=self.state.awayintro_progress
            end_x=left_x+left_w+90
            full_w=left_w+130
            curr_w=int(full_w*progress)
            start_x=end_x-curr_w
            self.draw_introround_left(p,start_x,835,curr_w,190,self.state.away_color)
            full_w=left_w
            curr_w=int(full_w*progress)
            start_x=(left_x-20)+full_w-curr_w
            self.draw_fully_rounded_rect(p,start_x,850,curr_w,155,darker_away)
            full_w=left_w-305
            curr_w=int(full_w*progress)
            start_x=(left_x+285)+full_w-curr_w
            self.draw_fully_rounded_rect(p,start_x,851,max(0,curr_w),153,lighter_away)
            full_w=left_w
            curr_w=int(full_w*progress)
            start_x=(left_x-20)+full_w-curr_w
            self.draw_panel_base(p,start_x,850,curr_w,155,self.state.away_color)
            full_w=left_w-505
            curr_w=int(full_w*progress)
            start_x=(left_x-20)+full_w-curr_w
            self.draw_away_notch(p,start_x,865,max(0,curr_w),120,self.state.away_color)
            fade_delay=0.65
            if progress>fade_delay:
                p.setOpacity((progress-fade_delay)/(1.0-fade_delay))
            else:
                p.setOpacity(0.0)
            p.setFont(self.introrecord_font)
            p.setPen(Qt.white)
            has_record = not (rw == 0 and rl == 0)
            has_district = not (dw == 0 and dl == 0)
            if has_record:
                if has_district:
                    # Normal position when both exist
                    p.drawText(left_x + 145, 964.5, 120, 35, Qt.AlignLeft, f"{rw}-{rl}")
                else:
                    # Move into district spot when district is missing
                    p.drawText(left_x + 210, 960, 120, 35, Qt.AlignLeft, f"{rw}-{rl}")
            if has_district:
                p.drawText(left_x + 205, 960, 120, 35, Qt.AlignLeft, f"({dw}-{dl})")
            rank, name = self.format_rank_name(self.state.away_rank, self.state.away_name)
            metrics_rank = QFontMetrics(self.introrank_font)
            metrics_name = QFontMetrics(self.introtitle_font)
            rank_w = metrics_rank.horizontalAdvance(rank) if rank else 0
            name_w = metrics_name.horizontalAdvance(name) if name else 0
            base_x = left_x + 20
            gap = 5
            right_limit = left_x + 275
            mascot_right = right_limit - 10
            mascot = getattr(self.state, "away_mascot", None)
            if mascot:
                metrics_mascot = QFontMetrics(self.introtitle_font)
                mascot_w = metrics_mascot.horizontalAdvance(mascot)
                mascot_max_w = right_limit - base_x - 10
                if mascot_max_w > 0 and mascot_w > mascot_max_w:
                    mascot = metrics_mascot.elidedText(mascot, Qt.ElideRight, mascot_max_w)
                    mascot_w = metrics_mascot.horizontalAdvance(mascot)
                mascot_x = mascot_right - mascot_w
            else:
                mascot_w = 0
                mascot_x = mascot_right
            name_x = mascot_right - name_w
            p.setFont(self.introtitle_font)
            p.drawText(name_x, 880, name_w + 2, 35, Qt.AlignLeft | Qt.AlignVCenter, name)
            if rank:
                rank_x = name_x - rank_w - gap
                p.setFont(self.introrank_font)
                p.drawText(rank_x, 880, rank_w, 35, Qt.AlignLeft | Qt.AlignVCenter, rank)

            # --- Draw mascot ---
            if mascot:
                p.setFont(self.introtitle_font)
                p.drawText(mascot_x, 928, mascot_w, 30, Qt.AlignRight | Qt.AlignVCenter, mascot)
            logo_x=left_x+295
            logo_y=830
            logo_w=180
            logo_h=185
            p.save()
            self.clip_to_rounded_rect(p,logo_x,830,logo_w,205)
            self.draw_logo_in_top_rounded_window(p,logo_x,logo_y,logo_w,logo_h,self.state.away_logo)
            p.restore()
            p.setOpacity(1.0)
 # -- HOME SECTION -- #
        if self.state.homeintro_active:
            progress=self.state.homeintro_progress
            start_x=right_x
            full_w=right_w+127.5
            curr_w=int(full_w*progress)
            self.draw_introround_right(p,start_x-90,835,curr_w,190,self.state.home_color)
            full_w=right_w+20
            curr_w=int(full_w*progress)
            self.draw_fully_rounded_rect(p,start_x,850,curr_w,155,darker_home)
            self.draw_fully_rounded_rect(p,start_x,851,max(0,curr_w-305),153,lighter_home)
            self.draw_panel_base(p,start_x,850,curr_w,155,self.state.home_color)
            self.draw_home_notch(p,start_x+505,865,max(0,curr_w-505),120,self.state.home_color)
            fade_delay=0.65
            if progress>fade_delay:
                p.setOpacity((progress-fade_delay)/(1.0-fade_delay))
            else:
                p.setOpacity(0.0)
            p.setFont(self.introrecord_font)
            p.setPen(Qt.white)
            if not (hw==0 and hl==0):
                p.drawText(right_x+164,964.5,120,35,Qt.AlignRight,f"{hw}-{hl}")
            if not (hdw==0 and hdl==0):
                p.drawText(right_x+257,960,120,35,Qt.AlignRight,f"({hdw}-{hdl})")
            logo_x=right_x+15
            logo_y=830
            logo_w=185
            logo_h=190
            p.save()
            self.clip_to_rounded_rect(p,right_x,855,min(curr_w,right_w),210)
            self.draw_logo_in_top_rounded_window(p,logo_x,logo_y,logo_w,logo_h,self.state.home_logo)
            p.restore()
            rank, name=self.format_rank_name(self.state.home_rank,self.state.home_name)
            metrics_name=QFontMetrics(self.introtitle_font)
            metrics_rank=QFontMetrics(self.introrank_font)
            rank_w=metrics_rank.horizontalAdvance(rank) if rank else 0
            name_w=metrics_name.horizontalAdvance(name)
            pod_right=right_x+(right_w-285)
            x_start=pod_right+8
            max_total_width=(right_x+505)-x_start-5
            total_w=rank_w+(6 if rank else 0)+name_w
            scale=1.0
            if total_w>max_total_width:
                scale=max_total_width/total_w
            rank_w=int(rank_w*scale)
            name_w=int(name_w*scale)
            if rank:
                font=QFont(self.introrank_font)
                font.setPointSizeF(font.pointSizeF()*scale)
                p.setFont(font)
                p.drawText(x_start,880,rank_w,35,Qt.AlignLeft|Qt.AlignVCenter,rank)
                name_x=x_start+rank_w+6
            else:
                name_x=x_start
            font=QFont(self.introtitle_font)
            font.setPointSizeF(font.pointSizeF()*scale)
            p.setFont(font)
            p.drawText(name_x,880,name_w,35,Qt.AlignLeft|Qt.AlignVCenter,name)
            mascot=getattr(self.state,"home_mascot",None)
            if mascot:
                metrics_mascot=QFontMetrics(self.introtitle_font)
                mascot_w=metrics_mascot.horizontalAdvance(mascot)
                mascot_x=x_start
                mascot_y=918
                right_limit=right_x+min(curr_w,right_w)
                max_mascot_width=right_limit-mascot_x-5
                if max_mascot_width>0 and mascot_w>max_mascot_width:
                    mascot=metrics_mascot.elidedText(mascot,Qt.ElideRight,max_mascot_width)
                p.drawText(mascot_x,mascot_y,max_mascot_width if max_mascot_width>0 else mascot_w,30,Qt.AlignLeft|Qt.AlignVCenter,mascot)
            p.setOpacity(1.0)
 # -- CENTER SECTION -- #
        if self.state.centerintro_active:
            progress=self.state.centerintro_progress
            left_x=830
            base_w=175
            center_x=left_x+(base_w//2)
            top_w=int((right_w-100)*progress)
            top_x=center_x-(top_w//2)
            full_w=right_w-100
            curr_w=int(full_w*progress)
            draw_x=center_x-(curr_w//2)
            self.draw_bottom2_rounded_rect(p,draw_x,800,curr_w,45,QColor("#1d1d1d"))

            full_w=190
            curr_w=int(full_w*progress)
            draw_x=center_x-(curr_w//2)
            self.draw_ffully_rounded_rect(p,draw_x-10,850,curr_w,155)
            full_w=650
            curr_w=int(full_w*progress)
            bottom_center=center_x
            self.draw_bottom1_rounded_rect(p,bottom_center-curr_w//2,1025,curr_w,35,QColor("#ffffff"),radius=7)
            fade_delay=0.65
            if progress>fade_delay:
                p.setOpacity((progress-fade_delay)/(1.0-fade_delay))
            else:
                p.setOpacity(0.0)
            p.setFont(self.introupper_font)
            p.setPen(Qt.white)
            text=self.state.top_text
            text_w=p.fontMetrics().horizontalAdvance(text)
            p.drawText(top_x+(top_w-text_w)//2,800,text_w,35,Qt.AlignLeft,text)
            logo_x=cx-15
            logo_y=830
            logo_w=180
            logo_h=185
            p.save()
            self.clip_to_rounded_rect(p,logo_x,830,logo_w,205)
            if self.state.center_logo is not None:
                self.draw_logo_in_top_rounded_window(p,logo_x,logo_y,logo_w,logo_h,self.state.center_logo)
            p.restore()
            school=getattr(self.state,"event_location_school_text","") or ""
            city=getattr(self.state,"event_location_city_text","") or ""
            if school or city:
                rect_x=right_x-475
                rect_y=990
                rect_w=right_w+275
                pad_x=20
                gap_school=10
                tri_w=16
                gap_city=15
                max_w=rect_w-(pad_x*2)
                fixed_w=gap_school+tri_w+gap_city
                avail_text=max_w-fixed_w
                half=avail_text//2
                p.setFont(self.introschool_font)
                fm_school=QFontMetrics(self.introschool_font)
                school_w=fm_school.horizontalAdvance(school)
                if school_w>half:
                    school=fm_school.elidedText(school,Qt.ElideRight,half)
                    school_w=fm_school.horizontalAdvance(school)
                p.setFont(self.introcity_font)
                fm_city=QFontMetrics(self.introcity_font)
                city_w=fm_city.horizontalAdvance(city)
                if city_w>half:
                    city=fm_city.elidedText(city,Qt.ElideRight,half)
                    city_w=fm_city.horizontalAdvance(city)
                total_w=school_w+fixed_w+city_w
                start_x=rect_x+pad_x+(max_w-total_w)//2
                p.setFont(self.introschool_font)
                p.setPen(Qt.black)
                p.drawText(QRect(start_x,rect_y+33,school_w,40),Qt.AlignLeft|Qt.AlignVCenter,school)
                tri_x=start_x+school_w+gap_school
                self.draw_right_triangle(p,tri_x,rect_y+55,tri_w,22,QColor("black"))
                p.setFont(self.introcity_font)
                p.setPen(Qt.black)
                city_x=tri_x+gap_city
                p.drawText(QRect(city_x,rect_y+35,city_w,40),Qt.AlignLeft|Qt.AlignVCenter,city)
            p.setOpacity(1.0)
    def draw_breakboard(self, p):
        if self.state.centerbreak_active:
            progress=self.state.centerbreak_progress
            left_x=15
            left_w=300
            center_x=left_x+(left_w//2)
            darker_home=self.state.home_color.darker(175)
            darker_away=self.state.away_color.darker(175)
            full_w=left_w
            curr_w=int(full_w*progress)
            draw_x=center_x-(curr_w//2)
            self.draw_fully_grounded_rect(p,draw_x,735,curr_w,315)
            full_w=left_w-20
            curr_w=int(full_w*progress)
            draw_x=center_x-(curr_w//2)
            self.draw_fully_rounded_rect(p,draw_x,1015,curr_w,25,QColor("#ffffff"), radius=7)
            full_w=left_w-20
            curr_w=int(full_w*progress)
            draw_x=center_x-(curr_w//2)
            self.draw_fully_gradient_rect(p,draw_x,750,curr_w,125,darker_away)
            self.draw_top_flat_rect(p,draw_x,850,curr_w,25,darker_away)
            self.draw_ppanel_base(p,draw_x,750,curr_w,125,self.state.away_color)
            full_w=left_w-175
            curr_w=int(full_w*progress)
            draw_x=center_x-(curr_w//2)
            self.draw_transparent_to_black_rect(p,draw_x+65,765,curr_w,75)
            self.draw_fpanel_base(p,draw_x+65,765,curr_w,75,self.state.away_color)
            full_w=left_w-20
            curr_w=int(full_w*progress)
            draw_x=center_x-(curr_w//2)
            self.draw_fully_gradient_rect(p,draw_x,885,curr_w,125,darker_home)
            self.draw_top_flat_rect(p,draw_x,985,curr_w,25,darker_home)
            self.draw_ppanel_base(p,draw_x,885,curr_w,125,self.state.home_color)
            full_w=left_w-175
            curr_w=int(full_w*progress)
            draw_x=center_x-(curr_w//2)
            self.draw_transparent_to_black_rect(p,draw_x+65,900,curr_w,75)
            self.draw_fpanel_base(p,draw_x+65,900,curr_w,75,self.state.home_color)
            fade_delay=0.65
            if progress>fade_delay:
                p.setOpacity((progress-fade_delay)/(1.0-fade_delay))
            else:
                p.setOpacity(0.0)
            p.setFont(self.bbscore_font)
            p.setPen(Qt.white)
            p.drawText(left_x+155,900,120,70,Qt.AlignCenter,str(self.state.home_pts))
            p.drawText(left_x+155,765,120,70,Qt.AlignCenter,str(self.state.away_pts))
            p_num=self.state.period
            if p_num==10:
                period_text="Halftime"
            elif 1<=p_num<=4:
                period_text=f"{self.period_text()} Quarter"
            elif p_num==5:
                period_text="Overtime"
            elif 6<=p_num<=9:
                period_text=f"{p_num-4} Overtime"
            else:
                period_text=""
            time_text=f"{self.state.minutes:02d}:{self.state.seconds:02d}"
            p.setFont(self.bbperiod_font)
            p.setPen(Qt.black)
            p.drawText(left_x+10,1014,left_w//2-20,26,Qt.AlignRight|Qt.AlignVCenter,period_text)
            self.draw_right_triangle(p,left_x+left_w//2+7,1027,16,16,QColor("black"))
            p.setFont(self.bbperiod_font)
            p.setPen(Qt.black)
            p.drawText(left_x+left_w//2+20,1016,left_w//2-20,26,Qt.AlignLeft|Qt.AlignVCenter,time_text)
            p.save()
            self.clip_to_rounded_rect(p,left_x,755,left_w,95)
            self.draw_logo_in_top_rounded_window(p,left_x+10,730,135,140,self.state.away_logo)
            p.restore()
            p.save()
            self.clip_to_rounded_rect(p,left_x,890,left_w,95)
            self.draw_logo_in_top_rounded_window(p,left_x+10,865,135,140,self.state.home_logo)
            p.restore()
            rank,name=self.format_rank_name(self.state.away_rank,self.state.away_name)
            p.setFont(self.rank_font)
            p.setPen(Qt.white)
            p.drawText(left_x+33,843,120,35,Qt.AlignLeft|Qt.AlignVCenter,rank)
            p.setFont(self.title_font)
            p.drawText(left_x+33+QFontMetrics(self.rank_font).horizontalAdvance(rank)+6,843,200,35,Qt.AlignLeft|Qt.AlignVCenter,name)
            rank,name=self.format_rank_name(self.state.home_rank,self.state.home_name)
            p.setFont(self.rank_font)
            p.drawText(left_x+33,978,120,35,Qt.AlignLeft|Qt.AlignVCenter,rank)
            p.setFont(self.title_font)
            p.drawText(left_x+33+QFontMetrics(self.rank_font).horizontalAdvance(rank)+6,978,200,35,Qt.AlignLeft|Qt.AlignVCenter,name)
            self.draw_away_notch(p,left_x+10,755,left_w-290,95,self.state.away_color)
            self.draw_away_notch(p,left_x+10,890,left_w-290,95,self.state.home_color)
            p.setOpacity(1.0)
         
    def draw_scorebug(self, p):
        # -- KEY INFORMATION (DO NOT CHANGE W/O PROPER TESTING) -- #
        left_x = 529    # was 615
        left_w = 463    # was 370
        right_x = 929   # was 935
        right_w = 463   # was 370
        dd_x = 855      # was 876
        dd_w = 213      # was 170
        cx = 843        # was 866
        cw = 238        # was 190
        cy = 931        # was 945
        rw = self.state.away_record_wins
        rl = self.state.away_record_losses
        dw = self.state.away_district_wins
        dl = self.state.away_district_losses
        hw = self.state.home_record_wins
        hl = self.state.home_record_losses
        hdw = self.state.home_district_wins
        hdl = self.state.home_district_losses
        base_away = QColor(self.state.away_color)
        bg_away = QColor(self.state.away_color)
        base_away.setAlpha(120)
        bg_away.setAlpha(190)
        if self.state.away_timeout_bar_timer > 0 and self.state.away_timeout_text:
            TOTAL = 150
            ANIM = 30
            FADE_IN = 15
            FADE_OUT = 30
            t = self.state.away_timeout_bar_timer
            if t > TOTAL - ANIM:  # slide up at start
                progress = (TOTAL - t) / ANIM
            elif t < ANIM:        # slide down at end
                progress = t / ANIM
            else:
                progress = 1.0
            progress = max(0.0, min(progress, 1.0))
            bar_height = 25       # was 20
            start_y = 956         # was 965
            end_y = 931           # was 945
            if t > ANIM:          # sliding up or steady
                bar_y = int(start_y - (start_y - end_y) * progress)
            else:                 # sliding down
                bar_y = int(end_y + (start_y - end_y) * (1 - progress))
            self.draw_top_rounded_rect(p, left_x + 4, bar_y, left_w - 144, bar_height, QColor("#2a2a2a"), radius=9)
            self.draw_glow_top_round(p, left_x + 4, bar_y, left_w - 144, bar_height, self.state.away_color)
            # Use same timer for fade-in/fade-out of the popup
            if t > TOTAL - FADE_IN:
                alpha = (TOTAL - FADE_IN - t) / FADE_IN
            elif t < FADE_OUT:
                alpha = t / FADE_OUT
            else:
                alpha = 1.0
            alpha = max(0.0, min(alpha, 1.0))
            p.save()
            p.setOpacity(alpha)
            self.draw_timeout_popup(p, left_x + 73, bar_y, self.state.away_timeout_text)
            p.restore()
            self.state.away_timeout_bar_timer -= 1
        if self.state.home_timeout_bar_timer > 0 and self.state.home_timeout_text:
            TOTAL = 150
            ANIM = 30
            FADE_IN = 15
            FADE_OUT = 30
            t = self.state.home_timeout_bar_timer
            if t > TOTAL - ANIM: progress = (TOTAL - t) / ANIM
            elif t > ANIM: progress = 1.0
            else: progress = t / ANIM
            progress = max(0.0, min(progress, 1.0))
            bar_height = 25       # was 20
            start_y = 956         # was 965
            end_y = 931           # was 945
            bar_y = int(start_y - (start_y - end_y) * progress)
            self.draw_top_rounded_rect(p, right_x + 141, bar_y, right_w - 144, bar_height, QColor("#2a2a2a"), radius=9)
            self.draw_glow_top_round(p, right_x + 141, bar_y, right_w - 144, bar_height, self.state.home_color)
            if t > TOTAL - FADE_IN: alpha = (TOTAL - FADE_IN - t) / FADE_IN
            elif t < FADE_OUT: alpha = t / FADE_OUT
            else: alpha = 1.0
            alpha = max(0.0, min(alpha, 1.0))
            p.save()
            p.setOpacity(alpha)
            self.draw_timeout_popup(p, right_x + 210, bar_y, self.state.home_timeout_text)
            p.restore()
            self.state.home_timeout_bar_timer -= 1
        # Draw Home Event (no forced yellow)
        if self.state.home_event_active or self.state.home_event_animating:
            progress = max(0.0, min(self.state.home_event_progress, 1.0))
            bar_height = 25       # was 20
            start_y = 956         # was 965
            end_y = 931           # was 945
            bar_y = int(start_y - (start_y - end_y) * progress)
            self.draw_top_rounded_rect(p, right_x + 141, bar_y, right_w - 144, bar_height, QColor("#2a2a2a"), radius=9)
            self.draw_glow_top_round(p, right_x + 141, bar_y, right_w - 144, 25, self.state.home_color)
            alpha = min(max((progress - 0.7) / 0.2, 0.0), 1.0) if progress > 0.7 else 0.0
            p.save()
            p.setOpacity(alpha)
            self.draw_event_text(p, right_x + 150, bar_y, self.state.home_event_text)
            p.restore()
        # Draw Away Event (no forced yellow)
        if self.state.away_event_active or self.state.away_event_animating:
            progress = max(0.0, min(self.state.away_event_progress, 1.0))
            bar_height = 25       # was 20
            start_y = 956         # was 965
            end_y = 931           # was 945
            bar_y = int(start_y - (start_y - end_y) * progress)
            self.draw_top_rounded_rect(p, left_x + 4, bar_y, left_w - 144, bar_height, QColor("#2a2a2a"), radius=9)
            self.draw_glow_top_round(p, left_x + 4, bar_y, left_w - 144, 25, self.state.away_color)
            alpha = min(max((progress - 0.7) / 0.2, 0.0), 1.0) if progress > 0.7 else 0.0
            p.save()
            p.setOpacity(alpha)
            self.draw_event_text(p, left_x + 16, bar_y, self.state.away_event_text)
            p.restore()
        # Draw Home Flag Event
        if self.state.home_event_flag_active or self.state.home_event_flag_animating:
            progress = max(0.0, min(self.state.home_event_flag_progress, 1.0))
            bar_height = 25       # was 20
            start_y = 956         # was 965
            end_y = 931           # was 945
            bar_y = int(start_y - (start_y - end_y) * progress)
            self.draw_top_rounded_rect(p, right_x + 141, bar_y, right_w - 144, bar_height, QColor("#2a2a2a"), radius=9)
            self.draw_glow_top_round(p, right_x + 141, bar_y, right_w - 144, 25, QColor("#FFD700"))
            alpha = min(max((progress - 0.7) / 0.2, 0.0), 1.0) if progress > 0.7 else 0.0
            p.save()
            p.setOpacity(alpha)
            self.draw_event_text(p, right_x + 150, bar_y, self.state.home_event_flag_text)
            p.restore()
        # Draw Away Flag Event
        if self.state.away_event_flag_active or self.state.away_event_flag_animating:
            progress = max(0.0, min(self.state.away_event_flag_progress, 1.0))
            bar_height = 25       # was 20
            start_y = 956         # was 965
            end_y = 931           # was 945
            bar_y = int(start_y - (start_y - end_y) * progress)
            self.draw_top_rounded_rect(p, left_x + 4, bar_y, left_w - 144, bar_height, QColor("#2a2a2a"), radius=9)
            self.draw_glow_top_round(p, left_x + 4, bar_y, left_w - 144, 25, QColor("#FFD700"))
            alpha = min(max((progress - 0.7) / 0.2, 0.0), 1.0) if progress > 0.7 else 0.0
            p.save()
            p.setOpacity(alpha)
            self.draw_event_text(p, left_x + 16, bar_y, self.state.away_event_flag_text)
            p.restore()
        # -- AWAY SECTION -- #
        if self.state.saway_box_active:
            p.setFont(self.record_font)
            p.setPen(Qt.white)
            progress = self.state.saway_box_progress
            full_width = left_w + 413          # was left_w + 330
            center_x = left_x - 5 + full_width // 2   # was left_x - 4
            curr_w = int(full_width * progress)
            self.draw_fully_rounded_rect(p, center_x - curr_w // 2, 956, curr_w, 100, QColor("#2a2a2a"))
            bottom_w = 871                     # was 697
            bottom_center = 525 + bottom_w // 2    # was 612 + bottom_w // 2
            curr_bottom = int(bottom_w * progress)
            self.draw_bottom_round_rect(p, bottom_center - curr_bottom // 2, 1044, curr_bottom, 13, QColor("#5E5E5E"), 13)
            if self.state.possession == 'away':
                self.draw_glow_round_left(p, left_x - 4, 956, left_w + 28, 100, self.state.away_color)
            if self.state.possession == 'home':
                self.draw_glow_round_right(p, right_x - 25, 956, right_w + 29, 100, self.state.home_color)
            curr_width = int(left_w * self.state.saway_box_progress)
            self.draw_base_bar(p, left_x + left_w - curr_width, 981, curr_width, 69)
            pod_full_width = left_w - 319      # was left_w - 255
            pod_start_progress = 0.5
            if progress >= pod_start_progress:
                pod_progress = (progress - pod_start_progress) / (1.0 - pod_start_progress)
                curr_pod_width = int(pod_full_width * pod_progress)
                self.draw_pod(p, left_x + pod_full_width - curr_pod_width, 981, curr_pod_width, 69, self.state.away_color)
            logo_x = left_x + 6               # was left_x + 5
            logo_y = 969                       # was 975
            logo_w = 100                       # was 80
            logo_h = 94                        # was 75
            p.save()
            self.clip_to_rounded_rect(p, left_x, 981, left_w - 6, 69)
            self.draw_logo_in_top_rounded_window(p, logo_x, logo_y, logo_w, logo_h, self.state.away_logo)
            p.restore()
            fade_delay = 0.7
            if progress <= fade_delay:
                opacity = 0.0
            else:
                opacity = (progress - fade_delay) / (1.0 - fade_delay)
            opacity = min(max(opacity, 0.0), 1.0)
            p.setOpacity(opacity)
            p.setFont(self.record_font)
            p.setPen(Qt.white)
            if not (rw == 0 and rl == 0):
                p.drawText(logo_x + 150, logo_y + 19, 150, 30, Qt.AlignLeft, f"{rw}-{rl}")
            if not (dw == 0 and dl == 0):
                p.drawText(logo_x + 141, logo_y + 44, 150, 30, Qt.AlignLeft, f"({dw}-{dl})")
            rank, name = self.format_rank_name(self.state.away_rank, self.state.away_name)
            metrics_rank = QFontMetrics(self.srank_font)
            metrics_name = QFontMetrics(self.stitle_font)
            rank_w = metrics_rank.horizontalAdvance(rank) if rank else 0
            name_w = metrics_name.horizontalAdvance(name) + 5
            spacing = 8
            max_text_w = left_w - 120
            total_w = rank_w + spacing + name_w if rank else name_w
            start_x = left_x + 13
            rank_x = start_x
            if rank:
                p.setFont(self.srank_font)
                p.setPen(Qt.white)
                p.drawText(rank_x, 953, rank_w , 33, Qt.AlignLeft | Qt.AlignVCenter, rank)
            name_x = rank_x + rank_w + spacing
            p.setFont(self.stitle_font)
            p.setPen(Qt.white)
            p.drawText(name_x, 953, name_w, 33, Qt.AlignLeft | Qt.AlignVCenter, name)
            p.setFont(self.score_font)
            p.setPen(Qt.white)
            p.drawText(left_x + 186, 963, 150, 88, Qt.AlignCenter, str(self.state.away_pts))
            self.draw_timeout_rects(p, left_x + 225, 1038, self.state.away_timeouts)
            p.setOpacity(1.0)
        if self.state.shome_box_active:
                progress = self.state.shome_box_progress
                curr_width = int(right_w * progress)
                self.draw_hmbase_bar(p, right_x, 981, curr_width, 69)
                pod_full_width = right_w - 319     # was right_w - 255
                pod_start_progress = 0.5
                if progress >= pod_start_progress:
                    pod_progress = (progress - pod_start_progress) / (1.0 - pod_start_progress)
                    curr_pod_width = int(pod_full_width * pod_progress)
                    self.draw_hmpod(p, right_x + 319, 981, curr_pod_width, 69, self.state.home_color)
                logo_x = right_x + 350            # was right_x + 280
                logo_y = 969                       # was 975
                logo_w = 100                       # was 80
                logo_h = 94                        # was 75
                p.save()
                self.clip_to_rounded_rect(p, right_x, 981, right_w, 69)
                self.draw_logo_in_top_rounded_window(p, logo_x, logo_y, logo_w, logo_h, self.state.home_logo)
                p.restore()
                fade_delay = 0.7
                if progress <= fade_delay:
                    opacity = 0.0
                else:
                    opacity = (progress - fade_delay) / (1.0 - fade_delay)
                opacity = min(max(opacity, 0.0), 1.0)
                p.setOpacity(opacity)
                p.setFont(self.record_font)
                p.setPen(Qt.white)
                if not (hw == 0 and hl == 0):
                    p.drawText(logo_x - 190, logo_y + 19, 150, 30, Qt.AlignRight, f"{hw}-{hl}")
                if not (hdw == 0 and hdl == 0):
                    p.drawText(logo_x - 181, logo_y + 44, 150, 30, Qt.AlignRight, f"({hdw}-{hdl})")
                rank, name = self.format_rank_name(self.state.home_rank, self.state.home_name)
                metrics_rank = QFontMetrics(self.srank_font)
                rank_w = metrics_rank.horizontalAdvance(rank) if rank else 0
                metrics_name = QFontMetrics(self.stitle_font)
                name_w = metrics_name.horizontalAdvance(name) + 5
                name_x = right_x + right_w - name_w - 13  # was - 10
                p.setFont(self.stitle_font)
                p.setPen(Qt.white)
                p.drawText(name_x, 953, name_w, 33, Qt.AlignLeft | Qt.AlignVCenter, name)
                if rank:
                    p.setFont(self.srank_font)
                    p.setPen(Qt.white)
                    metrics_rank = QFontMetrics(self.srank_font)
                    rank_w = metrics_rank.horizontalAdvance(rank)
                    rank_x = name_x - rank_w - 8  # was - 6
                    p.drawText(rank_x, 953, rank_w, 33, Qt.AlignLeft | Qt.AlignVCenter, rank)
                p.setFont(self.score_font)
                p.setPen(Qt.white)
                p.drawText(right_x + 116, 963, 150, 88, Qt.AlignCenter, str(self.state.home_pts))
                self.draw_timeout_rects(p, right_x + 150, 1038, self.state.home_timeouts, align="left")
                p.setOpacity(1.0)
        if self.state.shome_box_active:
                progress = self.state.shome_box_progress
                full_width = dd_w
                center_x = dd_x + full_width // 2
                curr_w = int(full_width * progress)
                self.draw_fully_rounded_rect(p, center_x - curr_w // 2, 950, curr_w, 31, QColor("#1d1d1d"), radius=9)
                if self.state.possession == 'away':
                    self.draw_glow_round_ddleft(p, dd_x, 950, dd_w - 28, 31, self.state.away_color)
                if self.state.possession == 'home':
                    self.draw_glow_round_ddright(p, dd_x + 28, 950, dd_w - 28, 31, self.state.home_color)
                fade_delay = 0.7
                if progress <= fade_delay:
                    opacity = 0.0
                else:
                    opacity = (progress - fade_delay) / (1.0 - fade_delay)
                opacity = min(max(opacity, 0.0), 1.0)
                p.setOpacity(opacity)
                p.setFont(self.dd_font)
                p.setPen(Qt.white)
                down_raw = str(self.state.down).strip()
                dist_raw = str(self.state.distance).strip()
                dist = dist_raw.lower()
    
                if down_raw == "" and dist == "":
                    dd_text = ""
    
                elif "final" in dist:
                    dd_text = dist_raw
    
                elif "halftime" in dist:
                    dd_text = dist_raw
    
                elif dist in ["1st down", "2nd down", "3rd down", "4th down"]:
                    try:
                        fixed_down = dist.split(" ")[0]
                        dd_text = f"{fixed_down} Down"
                    except:
                        dd_text = dist_raw
    
                elif "down" in dist and "-" in dist:
                    dd_text = dist_raw
    
                elif down_raw == "":
                    dd_text = dist_raw
    
                elif "down" in dist:
                    dd_text = f"{self.ordinal(int(down_raw))} Down"
    
                else:
                    if dist == "":
                        dd_text = f"{self.ordinal(int(down_raw))}"
                    else:
                        dd_text = f"{self.ordinal(int(down_raw))} & {dist_raw}"
    
                p.drawText(dd_x, 923, dd_w, 88, Qt.AlignCenter, dd_text)
                p.setFont(self.timer_font)
                p.setPen(Qt.white)
                tstring = f"{self.state.minutes}:{self.state.seconds:02d}"
                p.drawText(cx, cy + 50, cw, 75, Qt.AlignCenter, tstring)
                p.setFont(self.period_font)
                p.drawText(cx - 81, cy + 71, cw, 33, Qt.AlignCenter, f"{self.period_text()}")
                if self.state.play_running and self.show_playclock:
                    p.setFont(self.pc_font)
                    if self.state.playclock <= 10:
                        p.setPen(Qt.red)
                    else:
                        p.setPen(Qt.yellow)
                    rect = QRect(cx + 139, 1006, 125, 28)
                    p.drawText(rect, Qt.AlignCenter, f":{self.state.playclock:02d}")
                p.setOpacity(1.0)
            # -- FLAG SECTION -- #
        if self.state.flag is True:
                self.draw_fully_rounded_rect(p, dd_x, 950, dd_w, 31, QColor("#ffd609"), radius=9)
                self.draw_fpanel_base(p, left_x - 5, 956, right_w + 410, 99, QColor("#ffd609"))
                tri_w = 23                         # was 18
                tri_h = 28                         # was 22
                center_x = left_x - 5 + (right_w + 410) // 2
                center_y = 923 + (99 // 2)
                self.draw_left_triangle(p, center_x - 56, center_y, tri_w, tri_h, QColor("#e6c400"))
                self.draw_right_triangle(p, center_x + 56, center_y, tri_w, tri_h, QColor("#e6c400"))
                p.setPen(Qt.black)
                p.setFont(self.dd_font)
                p.drawText(QRect(left_x, 923, right_w + 398, 99), Qt.AlignCenter | Qt.AlignHCenter, self.state.flag_text)
            # -- POSSESSION SECTION -- #
        if self.state.possession == 'away':
                self.draw_possession_triangle(p, left_x + 271, 964, self.state.away_color)
        elif self.state.possession == 'home':
                self.draw_possession_triangle(p, right_x + 196, 964, self.state.home_color)
        if self.state.bottom_event_active:
            rect_x = left_x + 14
            rect_w = left_w + 375
            self.draw_semitransparent_rounded_rect(p, rect_x, 1056, rect_w, 25, QColor("#2a2a2a"))
            text = self.state.bottom_event_text_football
            text_w = p.fontMetrics().horizontalAdvance(text)
            self.draw_bottom_event_text(p,rect_x + (rect_w - text_w)//2,1056,text)
    def draw_home_touchdown(self, p):
        if self.state.home_touchdown_active:
            # Scaled 25% from anchor (0, 1000) — left-edge anchored
            left_x = 25      # was 20
            left_w = 338     # was 270
            right_x = 344    # was 275
            right_w = 338    # was 270
            dd_w = 213       # was 170
            dd_x = 244       # was 195
            cx = 244         # was 195
            cw = 238         # was 190
            cy = 931         # was 945
            progress = max(0.0, min(self.state.home_touchdown_progress, 1.0))
            full_width = dd_w + 625          # was dd_w + 500
            animated_width = int(full_width * progress)
            animated_x = right_x + right_w + 25   # was + 20
            base_away = QColor(self.state.away_color)
            bg_away = QColor(self.state.away_color)
            base_away.setAlpha(120)
            bg_away.setAlpha(190)
            self.draw_round_left(p, left_x - 5, 931, left_w + 3, 100, QColor("#2a2a2a"))
            lower2 = QColor("#2a2a2a")
            lower = QColor("#2a2a2a")
            lower2.setAlpha(120)
            lower.setAlpha(210)
            hmdarker = self.state.home_color.darker(125)
            shadow_grad = QLinearGradient(right_x, 944, right_x, -175)
            shadow_grad.setColorAt(0.0, QColor(0, 0, 0, 110))
            shadow_grad.setColorAt(1.0, QColor(0, 0, 0, 0))
            p.setBrush(QBrush(shadow_grad))
            p.setPen(Qt.NoPen)
            p.drawRect(right_x, 944, right_w, 31)
            self.draw_round_right(p, right_x + 3, 931, right_w + 3, 100, QColor("#2a2a2a"))
            if self.state.possession == 'home':
                self.draw_glow_round_right(p, right_x - 25, 931, right_w + 29, 100, self.state.home_color)
            self.draw_base_bar(p, left_x, 956, left_w, 69)
            self.draw_pod(p, left_x, 956, left_w - 200, 69, self.state.away_color)
            self.draw_hmbase_bar(p, right_x, 956, right_w, 69)
            self.draw_hmpod(p, right_x + 200, 956, right_w - 200, 69, self.state.home_color)
            self.draw_fully_rounded_rect(p, animated_x, 931, animated_width, 100, self.state.home_color, radius=13)
            self.draw_tdpanel_base(p, animated_x, 931, animated_width, 100, hmdarker)
            self.draw_fully_rounded_rect(p, dd_x, 925, dd_w, 31, QColor("#1d1d1d"), radius=9)
            fade_delay = 0.7
            if progress <= fade_delay:
                opacity = 0.0
            else:
                opacity = (progress - fade_delay) / (1.0 - fade_delay)
            opacity = min(max(opacity, 0.0), 1.0)
            p.save()
            p.setOpacity(opacity)
            p.setFont(self.dd_font)
            p.setPen(Qt.white)
            down_raw = str(self.state.down).strip()
            dist = str(self.state.distance).strip().lower()
            if down_raw == "" and dist == "":
                dd_text = ""
            elif down_raw == "":
                dd_text = dist
            elif "down" in dist:
                dd_text = f"{self.ordinal(int(down_raw))} {dist}"
            elif "final" in dist:
                dd_text = dist
            elif "halftime" in dist:
                dd_text = dist
            else:
                if dist == "":
                    dd_text = f"{self.ordinal(int(down_raw))}"
                else:
                    dd_text = f"{self.ordinal(int(down_raw))} & {dist}"
            p.drawText(dd_x, 898, dd_w, 88, Qt.AlignCenter, dd_text)
            p.setFont(self.timer_font)
            p.setPen(Qt.white)
            tstring = f"{self.state.minutes}:{self.state.seconds:02d}"
            p.drawText(cx, cy + 25, cw, 75, Qt.AlignCenter, tstring)
            p.setFont(self.period_font)
            p.setPen(Qt.white)
            p.drawText(cx - 79, cy + 46, cw, 33, Qt.AlignCenter, f"{self.period_text()}")
            if self.state.play_running and self.show_playclock:
                p.setFont(self.pc_font)
                if self.state.playclock <= 10:
                    p.setPen(Qt.red)
                else:
                    p.setPen(Qt.yellow)
                rect = QRect(cx + 125, cy + 50, 125, 28)
                p.drawText(rect, Qt.AlignCenter, f":{self.state.playclock:02d}")
            rank, name = self.format_rank_name(self.state.home_rank, self.state.home_name)
            p.setFont(self.tdrank_font)
            metrics_rank = QFontMetrics(self.tdrank_font)
            rank_w = metrics_rank.horizontalAdvance(rank) if rank else 0
            rank_x = animated_x + 331        # was + 265
            if rank:
                p.drawText(rank_x, 931, rank_w, 33, Qt.AlignLeft | Qt.AlignVCenter, rank)
            p.setFont(self.tdtitle_font)
            p.setPen(Qt.white)
            metrics_name = QFontMetrics(self.tdtitle_font)
            name_w = metrics_name.horizontalAdvance(name)
            name_x = rank_x + rank_w + 8     # was + 6
            p.drawText(name_x, 931, name_w, 33, Qt.AlignLeft | Qt.AlignVCenter, name)
            mascot = self.state.home_mascot
            metrics_mascot = QFontMetrics(self.tdtitle_font)
            mascot_w = metrics_mascot.horizontalAdvance(mascot)
            mascot_x = name_x + name_w + 13  # was + 10
            p.drawText(mascot_x, 931, mascot_w, 33, Qt.AlignLeft | Qt.AlignVCenter, mascot)
            p.setFont(self.monument_font)
            p.setPen(Qt.white)
            p.drawText(animated_x, 946, dd_w + 625, 100, Qt.AlignCenter, self.state.touchdown_text)
            logo_x = left_x + 6              # was + 5
            logo_y = 935                     # was 948
            logo_w = 100                     # was 80
            logo_h = 106                     # was 85
            p.save()
            self.clip_to_rounded_rect(p, logo_x, 981, logo_w, 131)
            self.draw_logo_in_top_rounded_window(p, logo_x, logo_y, logo_w, logo_h, self.state.away_logo)
            p.restore()
            logo_x2 = right_x + 350         # was + 280
            logo_y2 = 935                    # was 948
            logo_w2 = 100                    # was 80
            logo_h2 = 106                    # was 85
            p.save()
            self.clip_to_rounded_rect(p, right_x, 981, right_w, 131)
            self.draw_logo_in_top_rounded_window(p, logo_x2, logo_y2, logo_w2, logo_h2, self.state.home_logo)
            p.restore()
            p.setFont(self.score_font)
            p.setPen(Qt.white)
            p.drawText(left_x + 106, 938, 150, 88, Qt.AlignCenter, str(self.state.away_pts))
            p.drawText(right_x + 88, 938, 150, 88, Qt.AlignCenter, str(self.state.home_pts))
            self.draw_timeout_rects(p, left_x + 125, 1013, self.state.away_timeouts)
            self.draw_timeout_rects(p, right_x + 113, 1013, self.state.home_timeouts, align="left")
            p.restore()

    def draw_away_touchdown(self, p):
        if self.state.away_touchdown_active:
            # Scaled 25% from anchor (1920, 1000) — right-edge anchored
            left_x = 1158    # was 1310
            left_w = 338     # was 270
            right_x = 1489   # was 1575
            right_w = 338    # was 270
            dd_w = 213       # was 170
            dd_x = 1389      # was 1495
            cx = 1389        # was 1495
            cw = 238         # was 190
            cy = 931         # was 945
            progress = max(0.0, min(self.state.away_touchdown_progress, 1.0))
            full_width = dd_w + 625          # was dd_w + 500
            animated_width = int(full_width * progress)
            animated_x = (left_x - 25) - animated_width   # was - 20
            base_away = QColor(self.state.away_color)
            bg_away = QColor(self.state.away_color)
            base_away.setAlpha(120)
            bg_away.setAlpha(190)
            self.draw_round_left(p, left_x - 5, 931, left_w + 3, 100, QColor("#2a2a2a"))
            lower2 = QColor("#2a2a2a")
            lower = QColor("#2a2a2a")
            lower2.setAlpha(120)
            lower.setAlpha(210)
            shadow_grad = QLinearGradient(right_x, 944, right_x, -175)
            shadow_grad.setColorAt(0.0, QColor(0, 0, 0, 110))
            shadow_grad.setColorAt(1.0, QColor(0, 0, 0, 0))
            p.setBrush(QBrush(shadow_grad))
            p.setPen(Qt.NoPen)
            p.drawRect(right_x, 944, right_w, 31)
            self.draw_round_right(p, right_x + 3, 931, right_w + 3, 100, QColor("#2a2a2a"))
            if self.state.possession == 'away':
                self.draw_glow_round_left(p, left_x - 4, 931, left_w + 28, 100, self.state.away_color)
            self.draw_base_bar(p, left_x, 956, left_w, 69)
            self.draw_pod(p, left_x, 956, left_w - 200, 69, self.state.away_color)
            self.draw_hmbase_bar(p, right_x, 956, right_w, 69)
            self.draw_hmpod(p, right_x + 200, 956, right_w - 200, 69, self.state.home_color)
            self.draw_fully_rounded_rect(p, animated_x, 931, animated_width, 100, self.state.away_color, radius=13)
            self.draw_tdpanel_base(p, animated_x, 931, animated_width, 100, self.state.away_color.darker(125))
            self.draw_fully_rounded_rect(p, dd_x, 925, dd_w, 31, QColor("#1d1d1d"), radius=9)
            fade_delay = 0.7
            if progress <= fade_delay:
                opacity = 0.0
            else:
                opacity = (progress - fade_delay) / (1.0 - fade_delay)
            opacity = min(max(opacity, 0.0), 1.0)
            p.save()
            p.setOpacity(opacity)
            p.setFont(self.dd_font)
            p.setPen(Qt.white)
            down_raw = str(self.state.down).strip()
            dist = str(self.state.distance).strip().lower()
            if down_raw == "" and dist == "":
                dd_text = ""
            elif down_raw == "":
                dd_text = dist
            elif "down" in dist:
                dd_text = f"{self.ordinal(int(down_raw))} {dist}"
            elif "final" in dist:
                dd_text = dist
            elif "halftime" in dist:
                dd_text = dist
            else:
                if dist == "":
                    dd_text = f"{self.ordinal(int(down_raw))}"
                else:
                    dd_text = f"{self.ordinal(int(down_raw))} & {dist}"
            p.drawText(dd_x, 898, dd_w, 88, Qt.AlignCenter, dd_text)
            p.setFont(self.timer_font)
            p.setPen(Qt.white)
            tstring = f"{self.state.minutes}:{self.state.seconds:02d}"
            p.drawText(cx, cy + 25, cw, 75, Qt.AlignCenter, tstring)
            p.setFont(self.period_font)
            p.drawText(cx - 79, cy + 46, cw, 33, Qt.AlignCenter, f"{self.period_text()}")
            if self.state.play_running and self.show_playclock:
                p.setFont(self.pc_font)
                if self.state.playclock <= 10:
                    p.setPen(Qt.red)
                else:
                    p.setPen(Qt.yellow)
                rect = QRect(cx + 125, cy + 50, 125, 28)
                p.drawText(rect, Qt.AlignCenter, f":{self.state.playclock:02d}")
            rank, name = self.format_rank_name(self.state.away_rank, self.state.away_name)
            p.setFont(self.tdrank_font)
            p.setPen(Qt.white)
            metrics_rank = QFontMetrics(self.tdrank_font)
            rank_w = metrics_rank.horizontalAdvance(rank) if rank else 0
            rank_x = animated_x + 331        # was + 265
            if rank:
                p.drawText(rank_x, 931, rank_w, 33, Qt.AlignLeft | Qt.AlignVCenter, rank)
            p.setFont(self.tdtitle_font)
            p.setPen(Qt.white)
            metrics_name = QFontMetrics(self.tdtitle_font)
            name_w = metrics_name.horizontalAdvance(name)
            name_x = rank_x + rank_w + 8     # was + 6
            p.drawText(name_x, 931, name_w, 33, Qt.AlignLeft | Qt.AlignVCenter, name)
            mascot = self.state.away_mascot
            metrics_mascot = QFontMetrics(self.tdtitle_font)
            mascot_w = metrics_mascot.horizontalAdvance(mascot)
            mascot_x = name_x + name_w + 13  # was + 10
            p.drawText(mascot_x, 931, mascot_w, 33, Qt.AlignLeft | Qt.AlignVCenter, mascot)
            p.setFont(self.monument_font)
            p.setPen(Qt.white)
            p.drawText(animated_x, 946, dd_w + 625, 100, Qt.AlignCenter, self.state.touchdown_text)
            logo_x = left_x + 6              # was + 5
            logo_y = 935                     # was 948
            logo_w = 100                     # was 80
            logo_h = 106                     # was 85
            p.save()
            self.clip_to_rounded_rect(p, logo_x, 981, logo_w, 131)
            self.draw_logo_in_top_rounded_window(p, logo_x, logo_y, logo_w, logo_h, self.state.away_logo)
            p.restore()
            logo_x2 = right_x + 350         # was + 280
            logo_y2 = 935                    # was 948
            logo_w2 = 100                    # was 80
            logo_h2 = 106                    # was 85
            p.save()
            self.clip_to_rounded_rect(p, right_x, 981, right_w, 131)
            self.draw_logo_in_top_rounded_window(p, logo_x2, logo_y2, logo_w2, logo_h2, self.state.home_logo)
            p.restore()
            p.setFont(self.score_font)
            p.setPen(Qt.white)
            p.drawText(left_x + 106, 938, 150, 88, Qt.AlignCenter, str(self.state.away_pts))
            p.drawText(right_x + 88, 938, 150, 88, Qt.AlignCenter, str(self.state.home_pts))
            self.draw_timeout_rects(p, left_x + 125, 1013, self.state.away_timeouts)
            self.draw_timeout_rects(p, right_x + 113, 1013, self.state.home_timeouts, align="left")
            p.restore()

    def draw_football_final(self, p):
        # -- KEY INFORMATION (DO NOT CHANGE W/O PROPER TESTING) -- #
        # Scaled 25% from anchor (960, 1000) — matches draw_scorebug
        left_x = 529     # was 615
        left_w = 463     # was 370
        cx = 843         # was 866
        cw = 175         # was 140
        cy = 981         # was 985
        right_x = 929    # was 935
        right_w = 463    # was 370
        rw = self.state.away_record_wins
        rl = self.state.away_record_losses
        dw = self.state.away_district_wins
        dl = self.state.away_district_losses
        hw = self.state.home_record_wins
        hl = self.state.home_record_losses
        hdw = self.state.home_district_wins
        hdl = self.state.home_district_losses
 
        # -- AWAY SECTION -- #
        if self.state.faway_box_active:
            progress = self.state.faway_box_progress
            full_width = left_w + 413        # was left_w + 330
            center_x = left_x - 5 + full_width // 2   # was left_x - 4
            curr_w = int(full_width * progress)
            self.draw_fully_rounded_rect(p, center_x - curr_w // 2, 956, curr_w, 100, QColor("#2a2a2a"))
            bottom_w = 871                   # was 697
            bottom_center = 525 + bottom_w // 2       # was 612 + ...
            curr_bottom = int(bottom_w * progress)
            self.draw_bottom_round_rect(p, bottom_center - curr_bottom // 2, 1044, curr_bottom, 13, QColor("#5E5E5E"), 13)
            curr_width = int(left_w * self.state.faway_box_progress)
            self.draw_base_bar(p, left_x + left_w - curr_width, 981, curr_width, 69)
            pod_full_width = left_w - 319    # was left_w - 255
            pod_start_progress = 0.5
            if progress >= pod_start_progress:
                pod_progress = (progress - pod_start_progress) / (1.0 - pod_start_progress)
                curr_pod_width = int(pod_full_width * pod_progress)
                self.draw_pod(p, left_x + pod_full_width - curr_pod_width, 981, curr_pod_width, 69, self.state.away_color)
 
            logo_x = left_x + 6             # was + 5
            logo_y = 960                     # was 968
            logo_w = 100                     # was 80
            logo_h = 106                     # was 85
            p.save()
            self.clip_to_rounded_rect(p, left_x, 981, left_w - 6, 69)
            self.draw_logo_in_top_rounded_window(p, logo_x, logo_y, logo_w, logo_h, self.state.away_logo)
            p.restore()
            fade_delay = 0.7
            if progress <= fade_delay:
                opacity = 0.0
            else:
                opacity = (progress - fade_delay) / (1.0 - fade_delay)
            opacity = min(max(opacity, 0.0), 1.0)
            p.setOpacity(opacity)
            p.setFont(self.record_font)
            p.setPen(Qt.white)
            if not (rw == 0 and rl == 0):
                p.drawText(logo_x + 150, logo_y + 25, 150, 23, Qt.AlignLeft, f"{rw}-{rl}")
            if not (dw == 0 and dl == 0):
                p.drawText(logo_x + 141, logo_y + 53, 150, 23, Qt.AlignLeft, f"({dw}-{dl})")
            rank, name = self.format_rank_name(self.state.away_rank, self.state.away_name)
            metrics_rank = QFontMetrics(self.rank_font)
            rank_w = metrics_rank.horizontalAdvance(rank) if rank else 0
            rank_x = left_x + 13            # was + 10
            if rank:
                p.setFont(self.rank_font)
                p.setPen(Qt.white)
                p.drawText(rank_x, 953, rank_w, 33, Qt.AlignLeft | Qt.AlignVCenter, rank)
            metrics_name = QFontMetrics(self.title_font)
            name_w = metrics_name.horizontalAdvance(name)
            name_x = rank_x + rank_w + 8    # was + 6
            p.setFont(self.title_font)
            p.setPen(Qt.white)
            p.drawText(name_x, 953, name_w, 33, Qt.AlignLeft | Qt.AlignVCenter, name)
            p.setFont(self.score_font)
            p.setPen(Qt.white)
            p.drawText(left_x + 196, 963, 150, 88, Qt.AlignCenter, str(self.state.away_pts))
            self.draw_timeout_rects(p, left_x + 225, 1038, self.state.away_timeouts)
            p.setOpacity(1.0)
 
        # -- HOME SECTION -- #
        if self.state.fhome_box_active:
            progress = self.state.fhome_box_progress
            curr_width = int(right_w * progress)
            self.draw_hmbase_bar(p, right_x, 981, curr_width, 69)
            pod_full_width = right_w - 319   # was right_w - 255
            pod_start_progress = 0.5
            if progress >= pod_start_progress:
                pod_progress = (progress - pod_start_progress) / (1.0 - pod_start_progress)
                curr_pod_width = int(pod_full_width * pod_progress)
                self.draw_hmpod(p, right_x + 319, 981, curr_pod_width, 69, self.state.home_color)
            logo_x2 = right_x + 350         # was + 280
            logo_y2 = 960                    # was 968
            logo_w2 = 100                    # was 80
            logo_h2 = 106                    # was 85
            p.save()
            self.clip_to_rounded_rect(p, right_x, 981, right_w, 69)
            self.draw_logo_in_top_rounded_window(p, logo_x2, logo_y2, logo_w2, logo_h2, self.state.home_logo)
            p.restore()
            fade_delay = 0.7
            if progress <= fade_delay:
                opacity = 0.0
            else:
                opacity = (progress - fade_delay) / (1.0 - fade_delay)
            opacity = min(max(opacity, 0.0), 1.0)
            p.setOpacity(opacity)
            p.setFont(self.record_font)
            p.setPen(Qt.white)
            if not (hw == 0 and hl == 0):
                p.drawText(logo_x2 - 193, logo_y2 + 31, 150, 23, Qt.AlignRight, f"{hw}-{hl}")
            if not (hdw == 0 and hdl == 0):
                p.drawText(logo_x2 - 184, logo_y2 + 56, 150, 23, Qt.AlignRight, f"({hdw}-{hdl})")
            rank, name = self.format_rank_name(self.state.home_rank, self.state.home_name)
            metrics_rank = QFontMetrics(self.rank_font)
            rank_w = metrics_rank.horizontalAdvance(rank) if rank else 0
            metrics_name = QFontMetrics(self.title_font)
            name_w = metrics_name.horizontalAdvance(name)
            name_x = right_x + right_w - name_w - 13   # was - 10
            p.setFont(self.title_font)
            p.setPen(Qt.white)
            p.drawText(name_x, 953, name_w, 33, Qt.AlignLeft | Qt.AlignVCenter, name)
            if rank:
                p.setFont(self.rank_font)
                p.setPen(Qt.white)
                metrics_rank = QFontMetrics(self.rank_font)
                rank_w = metrics_rank.horizontalAdvance(rank)
                rank_x = name_x - rank_w - 8            # was - 6
                p.drawText(rank_x, 953, rank_w, 33, Qt.AlignLeft | Qt.AlignVCenter, rank)
            p.setFont(self.score_font)
            p.setPen(Qt.white)
            p.drawText(right_x + 121, 963, 150, 88, Qt.AlignCenter, str(self.state.home_pts))
            self.draw_timeout_rects(p, right_x + 150, 1038, self.state.home_timeouts, align="left")
            p.setOpacity(1.0)
 
        if self.state.cfinal_box_active:
            progress = self.state.cfinal_box_progress
            curr_w = int(cw * progress)
            draw_x = cx + 31 + (cw - curr_w) // 2     # was cx + 25
            self.draw_fully_rounded_rect(p, draw_x, cy - 13, curr_w, 69, QColor("#232323"), radius=10)
            fade_delay = 0.7
            if progress <= fade_delay:
                opacity = 0.0
            else:
                opacity = (progress - fade_delay) / (1.0 - fade_delay)
            opacity = min(max(opacity, 0.0), 1.0)
            p.setOpacity(opacity)
            period = self.state.period
            if period <= 4:
                self.state.final_text = "FINAL"
            elif period == 5:
                self.state.final_text = "FINAL/OT"
            else:
                self.state.final_text = f"FINAL/{period - 4} OT"
            p.setFont(self.final_font)
            p.setPen(Qt.white)
            p.drawText(cx + 31, cy - 6, cw, 56, Qt.AlignCenter, self.state.final_text)
            p.setOpacity(1.0)
        if self.state.bottom_event_active:
            self.draw_semitransparent_rounded_rect(p, left_x + 14, 1056, left_w + 375, 25, QColor("#2a2a2a"))
        if self.state.bottom_event_active:
            self.draw_bottom_event_text(p, left_x + 31, 1056, self.state.bottom_event_text_football)
        p.end()
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()
    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            global_pos = event.globalPosition().toPoint()
            delta = global_pos - self._drag_pos
            self.window().move(self.window().pos() + delta)
            self._drag_pos = global_pos
    def mouseReleaseEvent(self, event):
        self._drag_pos = None
    def draw_event_text(self, p: QPainter, x: int, y: int, text: str):
        if not text:
            return
        w = 240
        h= 22
        p.setFont(self.record_font)
        p.setPen(Qt.white)
        p.drawText(QRect(x, y, w, h), Qt.AlignVCenter | Qt.AlignHCenter, text)
    def draw_timeout_popup(self, p: QPainter, x, y, text):
        w = 140
        h = 22
        radius = 7
        p.setFont(self.record_font)
        p.setPen(Qt.white)
        p.drawText(QRect(x, y, w, h), Qt.AlignCenter, text)
class FootballControl(QMainWindow):
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


    def __init__(self, state: ScoreState, scoreboard: FootballScoreboard):

        super().__init__()
        self.state = state
        self.scoreboard = scoreboard

        self.show_playclock = False
        display_version = beta_version if beta_mode else current_version

        self.setWindowTitle(
            f"Football Scoreboard Control (Version: {display_version}"
            f"{' - BETA' if beta_mode else ''})"
        )

        self.setMinimumSize(720, 520)

        # ---------------- TIMERS ----------------

        self.td_timer = QTimer(self)
        self.td_timer.setSingleShot(True)
        self.td_timer.timeout.connect(self.end_touchdown)

        self.ui_timer = QTimer(self)
        self.ui_timer.timeout.connect(self.ui_tick)
        self.ui_timer.start(100)
        self.setFocusPolicy(Qt.StrongFocus)
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.game_tick)

        self.play_timer = QTimer()
        self.play_timer.setInterval(1000)
        self.play_timer.timeout.connect(self.play_tick)

        # ---------------- TABS ----------------

        tabs = QTabWidget()
        self.setCentralWidget(tabs)

        # PAGE 1
        page1 = QWidget()
        page1.setStyleSheet("background-color: #121212;")
        grid_info = QGridLayout()
        page1.setLayout(grid_info)
        tabs.addTab(page1, "Game Info Setup")

        # PAGE 2
        page2 = QWidget()
        page2.setStyleSheet("background-color: #121212;")
        grid = QGridLayout()
        page2.setLayout(grid)
        tabs.addTab(page2, "Main Controls")

        # PAGE 3
        page3 = QWidget()
        page3.setStyleSheet("background-color: #121212;")
        grid_away = QGridLayout()
        page3.setLayout(grid_away)
        tabs.addTab(page3, "Away Setup")

        # PAGE 4
        page4 = QWidget()
        page4.setStyleSheet("background-color: #121212;")
        grid_home = QGridLayout()
        page4.setLayout(grid_home)
        tabs.addTab(page4, "Home Setup")

        page5 = QWidget()
        page5.setStyleSheet("background-color: #121212;")
        grid_graphics = QGridLayout()
        page5.setLayout(grid_graphics)
        tabs.addTab(page5, "Graphics Control")

        page6 = QWidget()
        page6.setStyleSheet("background-color: #121212;")
        grid_series = QGridLayout()  
        page6.setLayout(grid_series)
        tabs.addTab(page6, "Series History Control")
        # ---------------- GROUPS ----------------

        score_group = QGroupBox("Score Control")
        clock_group = QGroupBox("Clock Control")
        game_group = QGroupBox("Game Control")

        score_layout = QGridLayout()
        clock_layout = QGridLayout()
        game_layout = QGridLayout()

        score_group.setLayout(score_layout)
        clock_group.setLayout(clock_layout)
        game_group.setLayout(game_layout)

        crew_group = QGroupBox("Announcers")
        crew_layout = QGridLayout()
        crew_group.setLayout(crew_layout)

        crew3_group = QGroupBox("3 Person Crew")
        crew3_layout = QGridLayout()
        crew3_group.setLayout(crew3_layout)

        crew4_group = QGroupBox("4 Person Crew")
        crew4_layout = QGridLayout()
        crew4_group.setLayout(crew4_layout)

        weather_group = QGroupBox("Weather Info")
        weather_layout = QGridLayout()
        weather_group.setLayout(weather_layout)

        series_group = QGroupBox("Series History")
        series_layout = QGridLayout()
        series_group.setLayout(series_layout)

        lower3rd_group = QGroupBox("Lower 3rd Control")
        lower3rd_layout = QGridLayout()
        score_group.setStyleSheet("QGroupBox{color:white;border:1px solid white;background:transparent;margin-top:10px;}")
        clock_group.setStyleSheet("QGroupBox{color:white;border:1px solid white;background:transparent;margin-top:10px;}")
        game_group.setStyleSheet("QGroupBox{color:white;border:1px solid white;background:transparent;margin-top:10px;}")
        crew_group.setStyleSheet("QGroupBox{color:white;border:1px solid white;background:transparent;margin-top:10px;}")
        crew3_group.setStyleSheet("QGroupBox{color:white;border:1px solid white;background:transparent;margin-top:10px;}")
        crew4_group.setStyleSheet("QGroupBox{color:white;border:1px solid white;background:transparent;margin-top:10px;}")
        weather_group.setStyleSheet("QGroupBox{color:white;border:1px solid white;background:transparent;margin-top:10px;}")
        lower3rd_group.setStyleSheet("QGroupBox{color:white;border:1px solid white;background:transparent;margin-top:10px;}")
        series_group.setStyleSheet("QGroupBox{color:white;border:1px solid white;background:transparent;margin-top:10px;}")
        lower3rd_group.setLayout(lower3rd_layout)
        grid_graphics.addWidget(weather_group, 0, 0)
        grid_graphics.addWidget(lower3rd_group, 0, 1)
        grid_graphics.addWidget(crew3_group, 1, 1)
        grid_graphics.addWidget(crew4_group, 2, 0, 1, 2)
        grid_graphics.addWidget(crew_group, 1, 0)
        grid_series.addWidget(series_group, 0, 0, 2, 2)
        grid.addWidget(score_group, 0, 0, 1, 2)
        grid.addWidget(clock_group, 1, 1)
        grid.addWidget(game_group, 1, 0)

        score_layout.addWidget(self.make_label_button("Away Team"),0, 0, 1, 2)
        score_layout.addWidget(self.make_label_button("Home Team"),0, 3, 1, 2)
        combo_away_plus = self.create_points_combo("Add Points",[6, 3, 2, 1],"away")
        score_layout.addWidget(combo_away_plus,1, 0, 1, 2)
        combo_home_plus = self.create_points_combo("Add Points",[6, 3, 2, 1],"home")
        score_layout.addWidget(combo_home_plus,1, 3, 1, 2)
        self.aw_score_box, self.aw_lcd = self.make_team_score_display(self.state.away_pts)
        score_layout.addWidget(self.aw_lcd,2, 0, 1, 3)
        self.hm_score_box, self.hm_lcd = self.make_team_score_display(self.state.home_pts)
        score_layout.addWidget(self.hm_lcd,2, 3, 1, 3)
        combo_away_minus = self.create_points_combo("Remove Points",[-6, -3, -2, -1],"away")
        score_layout.addWidget(combo_away_minus,3, 0, 1, 2)
        combo_home_minus = self.create_points_combo("Remove Points",[-6, -3, -2, -1],"home")
        score_layout.addWidget(combo_home_minus,3, 3, 1, 2)
        btn_poss_away = self.make_button("Away",lambda: self.set_possession_direct("away"))
        game_layout.addWidget(btn_poss_away,4, 0, 1, 3)
        btn_poss_none = self.make_button("None",lambda: self.set_possession_direct(None))
        game_layout.addWidget(btn_poss_none,4, 3, 1, 2)
        btn_poss_home = self.make_button("Home",lambda: self.set_possession_direct("home"))
        game_layout.addWidget(btn_poss_home,4, 5, 1, 3)
        game_layout.addWidget(self.make_label_button("Timeouts Left"),5, 3, 1, 2)
        self.away_to_lcd = self.make_timeout_display(self.state.away_timeouts)
        game_layout.addWidget(self.away_to_lcd,5, 1)
        btn_away_use = self.make_button("-",lambda: self.change_timeout("away", -1))
        game_layout.addWidget(btn_away_use,5, 0)
        btn_away_restore = self.make_button("+",lambda: self.change_timeout("away", 1))
        game_layout.addWidget(btn_away_restore,5, 2)
        self.home_to_lcd = self.make_timeout_display(self.state.home_timeouts)
        game_layout.addWidget(self.home_to_lcd,5, 6)
        btn_home_use = self.make_button("-",lambda: self.change_timeout("home", -1))
        game_layout.addWidget(btn_home_use,5, 5)
        btn_home_restore = self.make_button("+",lambda: self.change_timeout("home", 1))
        game_layout.addWidget(btn_home_restore,5, 7)
        self.time_lcd = self.make_lcd(5)
        self.time_lcd.display(f"{self.state.minutes:02d}:{self.state.seconds:02d}")
        clock_layout.addWidget(self.time_lcd,6, 1)
        self.min_edit = self.make_spinbox(0,90,self.state.minutes,width=60)
        self.min_edit.editingFinished.connect(self.set_lcd_clock_from_inputs)
        clock_layout.addWidget(self.min_edit,5, 0)
        self.sec_edit = self.make_spinbox(0,59,self.state.seconds,width=60)
        self.sec_edit.editingFinished.connect(self.set_lcd_clock_from_inputs)
        clock_layout.addWidget(self.sec_edit,5, 1)
        btn_set_clock = self.make_button("Set",self.set_lcd_clock_from_inputs)
        clock_layout.addWidget(btn_set_clock,5, 2)
        btn_start_clock = self.make_button("Start Clock",self.start_clock)
        clock_layout.addWidget(btn_start_clock,6, 0)
        btn_stop_clock = self.make_button("Stop Clock",self.stop_clock)
        clock_layout.addWidget(btn_stop_clock,6, 2)
        btn_reset_clock = self.make_button("Reset Clock",self.reset_clock)
        clock_layout.addWidget(btn_reset_clock,6, 3)
        self.pc_spin = self.make_spinbox(0,99,self.state.playclock)
        clock_layout.addWidget(self.pc_spin,7, 1)
        btn_pc = self.make_button("PC Time",lambda: self.toggle_playclock_preset(btn_pc))
        clock_layout.addWidget(btn_pc,7, 4)
        btn_start_pc = self.make_button("Start Play Clock",self.start_play_clock)
        clock_layout.addWidget(btn_start_pc,7, 0)
        btn_stop_pc = self.make_button("Stop Play Clock",self.stop_play_clock)
        clock_layout.addWidget(btn_stop_pc,7, 2)
        btn_reset_pc = self.make_button("Reset Play Clock",self.reset_play_clock)
        clock_layout.addWidget(btn_reset_pc,7, 3)
        game_layout.addWidget(self.make_label_button("<- Down | Distance ->"),8, 3, 1, 2)
        self.down_spin = QComboBox()
        self.down_spin.addItems(["1","2","3","4",""])
        self.down_spin.setCurrentText(str(self.state.down))
        self.down_spin.setStyleSheet(self.BUTTON_STYLE)
        game_layout.addWidget(self.down_spin,8, 0, 1, 3)
        self.dist_edit = QComboBox()
        self.dist_edit.setEditable(True)
        self.dist_edit.addItems(["Down","Goal","1","2","3","4","5","6","7","8","9","10","Inches","Final","Final/OT","HALFTIME","1st Down", "2nd Down", "3rd Down", "4th Down", ""])
        self.dist_edit.setCurrentText(str(self.state.distance))
        self.dist_edit.setStyleSheet(self.BUTTON_STYLE)
        game_layout.addWidget(self.dist_edit,8, 5, 1, 2)
        btn_set_dd = self.make_button("Set Down/Distance",self.set_down_distance)
        game_layout.addWidget(btn_set_dd,8, 7)
        self.period_spin = self.make_spinbox(1,10,self.state.period)
        game_layout.addWidget(self.period_spin,9, 0)
        btn_set_period = self.make_button("Set Period",self.set_period)
        game_layout.addWidget(btn_set_period,9, 1)
        def scoring_callback(choice):
            if choice == "2PT Attempt":
                self.on_2pt_clicked()
            elif choice == "Field Goal":
                self.on_fg_clicked()
        combo_scoring = self.create_action_combo("Select 2PT or FG",["2PT Attempt","Field Goal"],scoring_callback)
        game_layout.addWidget(combo_scoring,9, 3)
        self.btn_remove_event = self.make_button("Remove Event",self.on_remove_event)
        game_layout.addWidget(self.btn_remove_event,9, 5)
        self.flag_button = self.make_button("Flag",self.toggle_flag)
        game_layout.addWidget(self.flag_button,9, 2)
        btn_serial = self.make_button("Serial Connection",self.on_serial_button_clicked)
        grid_info.addWidget(btn_serial,10, 1)
        def on_score_type_changed(index):
            if index == 0:
                return  # placeholder selected, do nothing
            choice = combo_scoring.currentText()
            if choice == "2PT Attempt":
                self.on_2pt_clicked()
            elif choice == "Field Goal":
                self.on_fg_clicked()
            combo_scoring.setCurrentIndex(0)  # reset to placeholder after selection
        combo_scoring.currentIndexChanged.connect(on_score_type_changed)
        game_layout.addWidget(combo_scoring, 9, 3, 1, 1)  # spans 2 columns where old buttons were
        self.timer = QTimer()
        self.timer.setInterval(1000)  # 1 sec
        self.timer.timeout.connect(self.game_tick)
        self.play_timer = QTimer()
        self.play_timer.setInterval(1000)
        self.play_timer.timeout.connect(self.play_tick)
        grid_away.addWidget(self.make_label_button("Away Team Setup"),-1,0)
        grid_away.addWidget(self.make_label_button("Enter Away Name:"),1,0)
        self.away_setup_name=QLineEdit(self.state.away_name)
        self.away_setup_name.setStyleSheet(self.BUTTON_STYLE)
        grid_away.addWidget(self.away_setup_name,1,1)
        grid_away.addWidget(self.make_button("Submit",self.submit_away_setup),1,2)
        grid_away.addWidget(self.make_label_button("Away Team Rank:"),1,3)
        self.away_rank_edit=QLineEdit()
        self.away_rank_edit.setText(str(self.state.away_rank or ""))
        self.away_rank_edit.setStyleSheet(self.BUTTON_STYLE)
        self.away_rank_edit.setValidator(QIntValidator(0,25,self))
        grid_away.addWidget(self.away_rank_edit,1,4)
        grid_away.addWidget(self.make_label_button("Away Mascot:"),2,2)
        self.away_setup_mascot=QLineEdit(self.state.away_mascot)
        self.away_setup_mascot.setStyleSheet(self.BUTTON_STYLE)
        grid_away.addWidget(self.away_setup_mascot,2,3)
        grid_away.addWidget(self.make_button("Submit",self.submit_away_setup),2,4)
        grid_away.addWidget(self.make_button("Submit",self.submit_away_setup),1,5)
        grid_away.addWidget(self.make_label_button("Away Team Color:"),2,0)
        btn=self.make_button("🎨",self.pick_away_color_from_setup)
        grid_away.addWidget(btn,2,1)
        grid_away.addWidget(self.make_label_button("Away Team Logo:"),3,0)
        btn=self.make_button("🖼",self.load_away_logo_from_setup)
        grid_away.addWidget(btn,3,1)
        grid_away.addWidget(self.make_label_button("Away Team Record:"),4,0)
        self.away_record_wins_edit=QLineEdit(str(self.state.away_record_wins))
        self.away_record_wins_edit.setStyleSheet(self.BUTTON_STYLE)
        self.away_record_losses_edit=QLineEdit(str(self.state.away_record_losses))
        self.away_record_losses_edit.setStyleSheet(self.BUTTON_STYLE)
        grid_away.addWidget(self.away_record_wins_edit,4,1)
        grid_away.addWidget(self.away_record_losses_edit,4,2)
        grid_away.addWidget(self.make_button("Submit",self.submit_away_setup),4,3)
        grid_away.addWidget(self.make_label_button("Away District Record:"),5,0)
        self.away_district_wins_edit=QLineEdit(str(self.state.away_district_wins))
        self.away_district_wins_edit.setStyleSheet(self.BUTTON_STYLE)
        self.away_district_losses_edit=QLineEdit(str(self.state.away_district_losses))
        self.away_district_losses_edit.setStyleSheet(self.BUTTON_STYLE)
        grid_away.addWidget(self.away_district_wins_edit,5,1)
        grid_away.addWidget(self.away_district_losses_edit,5,2)
        grid_away.addWidget(self.make_button("Submit",self.submit_away_setup),5,3)
        self.chk_district=QCheckBox("District Opponent")
        self.chk_district.setChecked(False)
        self.chk_district.stateChanged.connect(self.update_district_flag)
        self.chk_district.setStyleSheet("QCheckBox{color:white;} QCheckBox::indicator{width:15px;height:15px;border:2px solid white;background:#121212;} QCheckBox::indicator:checked{background:white;}")
        grid_info.addWidget(self.chk_district,9,0,1,5)
        grid_home.addWidget(self.make_label_button("Home Team Setup"),-4,0)
        grid_home.addWidget(self.make_label_button("Enter Home Name:"),0,0)
        self.home_setup_name=QLineEdit(self.state.home_name)
        self.home_setup_name.setStyleSheet(self.BUTTON_STYLE)
        grid_home.addWidget(self.home_setup_name,0,1)
        grid_home.addWidget(self.make_button("Submit",self.submit_home_setup),0,2)
        grid_home.addWidget(self.make_label_button("Home Team Rank:"),0,3)
        self.home_rank_edit=QLineEdit()
        self.home_rank_edit.setText(str(self.state.home_rank or ""))
        self.home_rank_edit.setStyleSheet(self.BUTTON_STYLE)
        self.home_rank_edit.setValidator(QIntValidator(0,25,self))
        grid_home.addWidget(self.home_rank_edit,0,4)
        grid_home.addWidget(self.make_button("Submit",self.submit_home_setup),0,5)
        grid_home.addWidget(self.make_label_button("Home Mascot:"),1,2)
        self.home_setup_mascot=QLineEdit(self.state.home_mascot)
        self.home_setup_mascot.setStyleSheet(self.BUTTON_STYLE)
        grid_home.addWidget(self.home_setup_mascot,1,3)
        grid_home.addWidget(self.make_button("Submit",self.submit_home_setup),1,4)
        grid_home.addWidget(self.make_label_button("Home Team Color:"),1,0)
        btn=self.make_button("🎨",self.pick_home_color_from_setup)
        grid_home.addWidget(btn,1,1)
        grid_home.addWidget(self.make_label_button("Home Team Logo:"),2,0)
        btn=self.make_button("🖼",self.load_home_logo_from_setup)
        grid_home.addWidget(btn,2,1)
        grid_home.addWidget(self.make_label_button("Home Team Record:"),3,0)
        self.home_record_wins_edit=QLineEdit(str(self.state.home_record_wins))
        self.home_record_wins_edit.setStyleSheet(self.BUTTON_STYLE)
        self.home_record_losses_edit=QLineEdit(str(self.state.home_record_losses))
        self.home_record_losses_edit.setStyleSheet(self.BUTTON_STYLE)
        grid_home.addWidget(self.home_record_wins_edit,3,1)
        grid_home.addWidget(self.home_record_losses_edit,3,2)
        grid_home.addWidget(self.make_button("Submit",self.submit_home_setup),3,3)
        grid_home.addWidget(self.make_label_button("Home District Record:"),4,0)
        self.home_district_wins_edit=QLineEdit(str(self.state.home_district_wins))
        self.home_district_wins_edit.setStyleSheet(self.BUTTON_STYLE)
        self.home_district_losses_edit=QLineEdit(str(self.state.home_district_losses))
        self.home_district_losses_edit.setStyleSheet(self.BUTTON_STYLE)
        grid_home.addWidget(self.home_district_wins_edit,4,1)
        grid_home.addWidget(self.home_district_losses_edit,4,2)
        grid_home.addWidget(self.make_button("Submit",self.submit_home_setup),4,3)
        grid_info.addWidget(self.make_label_button("hehe"),-1,0)
        grid_info.addWidget(self.make_label_button("Graphics:"),4,0)
        self.btn_show_intro=FlashingButton("Show Intro Graphic")
        self.btn_show_intro.setStyleSheet(self.BUTTON_STYLE)
        self.btn_show_intro.clicked.connect(lambda:self.show_intro(force_double=True))
        grid_info.addWidget(self.btn_show_intro,4,1)
        self.btn_show_scorebug=FlashingButton("Show Scorebug")
        self.btn_show_scorebug.setStyleSheet(self.BUTTON_STYLE)
        self.btn_show_scorebug.clicked.connect(lambda:self.show_scorebug(force_double=True))
        grid_info.addWidget(self.btn_show_scorebug,4,2)
        self.btn_show_breakboard=FlashingButton("Show Breakboard")
        self.btn_show_breakboard.setStyleSheet(self.BUTTON_STYLE)
        self.btn_show_breakboard.clicked.connect(lambda:self.show_breakboard(force_double=True))
        grid_info.addWidget(self.btn_show_breakboard,4,3)
        self.btn_show_final=FlashingButton("Show Final")
        self.btn_show_final.setStyleSheet(self.BUTTON_STYLE)
        self.btn_show_final.clicked.connect(lambda:self.show_final(force_double=True))
        grid_info.addWidget(self.btn_show_final,4,4)
        self.btn_show_weather=FlashingButton("Show Weather")
        self.btn_show_weather.setStyleSheet(self.BUTTON_STYLE)
        self.btn_show_weather.clicked.connect(lambda:self.show_weather(force_double=True))
        grid_info.addWidget(self.btn_show_weather,5,1)
        self.btn_show_lower3rd=FlashingButton("Show Lower 3rd")
        self.btn_show_lower3rd.setStyleSheet(self.BUTTON_STYLE)
        self.btn_show_lower3rd.clicked.connect(lambda:self.show_lower3rd(force_double=True))
        grid_info.addWidget(self.btn_show_lower3rd,5,2)
        self.btn_show_crew=FlashingButton("Show Announcers")
        self.btn_show_crew.setStyleSheet(self.BUTTON_STYLE)
        self.btn_show_crew.clicked.connect(lambda:self.show_crew(force_double=True))
        grid_info.addWidget(self.btn_show_crew,5,3)
        self.btn_show_3crew=FlashingButton("Show 3 Person Crew")
        self.btn_show_3crew.setStyleSheet(self.BUTTON_STYLE)
        self.btn_show_3crew.clicked.connect(lambda:self.show_crew3(force_double=True))
        grid_info.addWidget(self.btn_show_3crew,5,4)
        self.btn_show_4crew=FlashingButton("Show 4 Person Crew")
        self.btn_show_4crew.setStyleSheet(self.BUTTON_STYLE)
        self.btn_show_4crew.clicked.connect(lambda:self.show_crew4(force_double=True))
        grid_info.addWidget(self.btn_show_4crew,6,1)
        self.btn_show_series=FlashingButton("Show Series History")
        self.btn_show_series.setStyleSheet(self.BUTTON_STYLE)
        self.btn_show_series.clicked.connect(lambda:self.show_serieshistory(force_double=True))
        grid_info.addWidget(self.btn_show_series,6,2)
        grid_info.addWidget(self.make_label_button("Event Location:"),1,0)
        self.event_location_edit=QLineEdit()
        self.event_location_edit.setPlaceholderText("Enter school / event text...")
        self.event_location_edit.setStyleSheet(self.BUTTON_STYLE)
        grid_info.addWidget(self.event_location_edit,1,1)
        self.event_city_edit=QLineEdit()
        self.event_city_edit.setPlaceholderText("Enter city...")
        self.event_city_edit.setStyleSheet(self.BUTTON_STYLE)
        grid_info.addWidget(self.event_city_edit,1,2)
        grid_info.addWidget(self.make_button("Submit",self.submit_event_location),1,3)        
        weather_layout.addWidget(self.make_label_button("Temperature"),0,0)
        self.weather_temp_edit=QLineEdit()
        self.weather_temp_edit.setPlaceholderText("Enter temperature...")
        self.weather_temp_edit.setStyleSheet(self.BUTTON_STYLE)
        weather_layout.addWidget(self.weather_temp_edit,1,0)
        weather_layout.addWidget(self.make_label_button("Humidity"),0,1)
        self.weather_humidity_edit=QLineEdit()
        self.weather_humidity_edit.setPlaceholderText("Enter humidity...")
        self.weather_humidity_edit.setStyleSheet(self.BUTTON_STYLE)
        weather_layout.addWidget(self.weather_humidity_edit,1,1)
        weather_layout.addWidget(self.make_label_button("Wind Speed"),2,0)
        self.weather_wind_edit=QLineEdit()
        self.weather_wind_edit.setPlaceholderText("Enter wind speed...")
        self.weather_wind_edit.setStyleSheet(self.BUTTON_STYLE)
        weather_layout.addWidget(self.weather_wind_edit,3,0)
        self.weather_condition_edit=QLineEdit()
        weather_layout.addWidget(self.make_label_button("Conditions"),2,1)
        self.weather_condition_edit.setPlaceholderText("Enter condition...")
        self.weather_condition_edit.setStyleSheet(self.BUTTON_STYLE)
        weather_layout.addWidget(self.weather_condition_edit,3,1)
        weather_layout.addWidget(self.make_button("Submit Weather",self.submit_weather),4,0,1,2)
        lower3rd_layout.addWidget(self.make_label_button("Player Name"),0,1)
        self.lower3rdbigtitle_edit=QLineEdit()
        self.lower3rdbigtitle_edit.setPlaceholderText("Enter main title...")
        self.lower3rdbigtitle_edit.setStyleSheet(self.BUTTON_STYLE)
        lower3rd_layout.addWidget(self.lower3rdbigtitle_edit,1,1)
        self.lower3rdsmalltitle_edit=QLineEdit()
        lower3rd_layout.addWidget(self.make_label_button("School Name and Mascot"),0,0)
        self.lower3rdsmalltitle_edit.setPlaceholderText("Enter small title...")
        self.lower3rdsmalltitle_edit.setStyleSheet(self.BUTTON_STYLE)
        lower3rd_layout.addWidget(self.lower3rdsmalltitle_edit,1,0)
        lower3rd_layout.addWidget(self.make_label_button("Stats/Other Information"),2,0)
        self.lower3rd_text_edit=QLineEdit()
        self.lower3rd_text_edit.setPlaceholderText("Enter lower third text...")
        self.lower3rd_text_edit.setStyleSheet(self.BUTTON_STYLE)
        lower3rd_layout.addWidget(self.lower3rd_text_edit,3,0)
        lower3rd_layout.addWidget(self.make_button("Submit Lower 3rd",self.submit_lower3rd),3,1)
        lower3rd_layout.addWidget(self.make_button("Pick Logo", self.show_logo_picker), 4, 0, 1, 2)
        self.crew_playbyplay_edit=QLineEdit()
        self.crew_playbyplay_edit.setPlaceholderText("Play-by-play announcer name...")
        self.crew_playbyplay_edit.setStyleSheet(self.BUTTON_STYLE)
        crew_layout.addWidget(self.make_label_button("Play-by-Play"),0,0)
        crew_layout.addWidget(self.crew_playbyplay_edit,1,0)
        self.crew_color_edit=QLineEdit()
        crew_layout.addWidget(self.make_label_button("Color Commentator"),0,1)
        self.crew_color_edit.setPlaceholderText("Color commentator name...")
        self.crew_color_edit.setStyleSheet(self.BUTTON_STYLE)
        crew_layout.addWidget(self.crew_color_edit,1,1)
        crew_layout.addWidget(self.make_button("Submit Crew",self.submit_crew),2,0, 1,2)
        grid_info.addWidget(self.make_label_button("Event Info:"),2,0)
        self.bottom_event_edit=QLineEdit()
        self.bottom_event_edit.setStyleSheet(self.BUTTON_STYLE)
        grid_info.addWidget(self.bottom_event_edit,2,1)
        self.bottom_event_edit.setPlaceholderText("Enter event info text...")
        self.bottom_event_edit.setStyleSheet(self.BUTTON_STYLE)
        grid_info.addWidget(self.bottom_event_edit,2,1,1,2)
        grid_info.addWidget(self.make_button("Submit",self.submit_bottom_event),2,3)
        grid_info.addWidget(self.make_label_button("Top Text:"),3,0)
        self.top_text_edit=QLineEdit()
        self.top_text_edit.setPlaceholderText("Enter top text...")
        self.top_text_edit.setStyleSheet(self.BUTTON_STYLE)
        grid_info.addWidget(self.top_text_edit,3,1)
        grid_info.addWidget(self.make_button("Submit",self.submit_top_text),3,3)
        self.series_stat1_edit = QLineEdit()
        self.series_stat2_edit = QLineEdit()
        self.series_stat3_edit = QLineEdit()
        self.series_away_score_edit = QLineEdit()
        self.series_home_score_edit = QLineEdit()
        self.series_date_edit = QLineEdit()
        series_layout.addWidget(self.make_label_button("Series Stat 1"), 0, 0)
        self.series_stat1_edit.setPlaceholderText("Enter stat 1...")
        self.series_stat1_edit.setStyleSheet(self.BUTTON_STYLE)
        series_layout.addWidget(self.series_stat1_edit, 1, 0)
        series_layout.addWidget(self.make_label_button("Series Stat 2"), 0, 1)
        self.series_stat2_edit.setPlaceholderText("Enter stat 2...")
        self.series_stat2_edit.setStyleSheet(self.BUTTON_STYLE)
        series_layout.addWidget(self.series_stat2_edit, 1, 1)
        series_layout.addWidget(self.make_label_button("Series Stat 3"), 0, 2)
        self.series_stat3_edit.setPlaceholderText("Enter stat 3...")
        self.series_stat3_edit.setStyleSheet(self.BUTTON_STYLE)
        series_layout.addWidget(self.series_stat3_edit, 1, 2)
        series_layout.addWidget(self.make_label_button("Away Score"), 2, 0)
        self.series_away_score_edit.setPlaceholderText("Enter away score...")
        self.series_away_score_edit.setStyleSheet(self.BUTTON_STYLE)
        series_layout.addWidget(self.series_away_score_edit, 3, 0)
        series_layout.addWidget(self.make_label_button("Home Score"), 2, 1)
        self.series_home_score_edit.setPlaceholderText("Enter home score...")
        self.series_home_score_edit.setStyleSheet(self.BUTTON_STYLE)
        series_layout.addWidget(self.series_home_score_edit, 3, 1)
        series_layout.addWidget(self.make_label_button("Game Date"), 2, 2)
        self.series_date_edit.setPlaceholderText("Enter date...")
        self.series_date_edit.setStyleSheet(self.BUTTON_STYLE)
        series_layout.addWidget(self.series_date_edit, 3, 2)
        self.series_submit_btn = QPushButton("Submit Series History")
        self.series_submit_btn.setStyleSheet(self.BUTTON_STYLE)
        self.series_submit_btn.clicked.connect(self.submit_series_history)
        series_layout.addWidget(self.series_submit_btn, 4, 0, 1, 3)
    def show_logo_picker(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Pick a Logo")
        dialog.setFixedSize(300, 200)

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        layout.addWidget(QLabel("Which logo do you want to use?"))

        def choose(side):
            self.state.team_side = side
            dialog.accept()

        home_btn = QPushButton("HOME")
        home_btn.setStyleSheet(self.BUTTON_STYLE)
        home_btn.clicked.connect(lambda: choose("home"))

        away_btn = QPushButton("AWAY")
        away_btn.setStyleSheet(self.BUTTON_STYLE)
        away_btn.clicked.connect(lambda: choose("away"))

        center_btn = QPushButton("CENTER")
        center_btn.setStyleSheet(self.BUTTON_STYLE)
        center_btn.clicked.connect(lambda: choose("center"))

        layout.addWidget(home_btn)
        layout.addWidget(away_btn)
        layout.addWidget(center_btn)

        dialog.setLayout(layout)
        dialog.exec()
    def on_serial_button_clicked(self):
        action, ok = QInputDialog.getItem(self,"Serial Connection","Select action:",["Start Connection", "Stop Connection"],editable=False)
        if ok:
            if action == "Start Connection":
                self.start_serial()
            elif action == "Stop Connection":
                self.stop_serial()
    def on_2pt_clicked(self):
        team, ok = QInputDialog.getItem(self,"Select Team","Which team?",["Home", "Away"],editable=False)
        if ok:
            if team == "Home":
                self.trigger_home_event("2 POINT-ATTEMPT")
            else:
                self.trigger_away_event("2 POINT-ATTEMPT")
    def on_home_2pt_clicked(self):
        self.trigger_home_event("2 POINT-ATTEMPT")
    def on_away_2pt_clicked(self):
        self.trigger_away_event("2 POINT-ATTEMPT")
    def submit_event_location(self):
        school_text = self.event_location_edit.text().strip()
        city_text = self.event_city_edit.text().strip()
        self.state.event_location_school_text = school_text or ""
        self.state.event_location_city_text = city_text or ""
    def submit_weather(self):
        self.state.weather_temp = self.weather_temp_edit.text().strip() or "--"
        self.state.weather_humidity = self.weather_humidity_edit.text().strip() or "--"
        self.state.weather_wind = self.weather_wind_edit.text().strip() or "--"
        self.state.weather_condition = self.weather_condition_edit.text().strip() or "---"
        self.repaint_scoreboard()
    def submit_series_history(self):
        self.state.series_stat1=self.series_stat1_edit.text().strip() or "Note or Stat 1"
        self.state.series_stat2=self.series_stat2_edit.text().strip() or "Note or Stat 2"
        self.state.series_stat3=self.series_stat3_edit.text().strip() or "Note or Stat 3"
        self.state.series_away_score=self.series_away_score_edit.text().strip() or "0"
        self.state.series_home_score=self.series_home_score_edit.text().strip() or "0"
        self.state.series_date=self.series_date_edit.text().strip() or "DATE"
        self.repaint_scoreboard()
    def submit_lower3rd(self):
        self.state.lower3rdbigtitle = self.lower3rdbigtitle_edit.text().strip() or "---"
        self.state.lower3rdsmalltitle = self.lower3rdsmalltitle_edit.text().strip() or "---"
        self.state.lower3rd_text = self.lower3rd_text_edit.text().strip() or "---"
        self.repaint_scoreboard()
    def submit_crew(self):
        self.state.crew_playbyplay_name=self.crew_playbyplay_edit.text().strip() or "---"
        self.state.crew_color_name=self.crew_color_edit.text().strip() or "---"
        self.repaint_scoreboard()
    def submit_bottom_event(self):
        text = self.bottom_event_edit.text().strip()
        self.state.bottom_event_text_football = text or ""
        self.state.bottom_event_active = bool(text)
        self.repaint_scoreboard()
    def submit_top_text(self):
        text = self.top_text_edit.text().strip()
        self.state.top_text = text or "High School Football"
        self.repaint_scoreboard()
    def toggle_playclock_preset(self, btn):
        v, ok = QInputDialog.getItem(self,"Set Play Clock","Select play clock:",["25","40"],False)
        if ok:
            self.quick_set_playclock(int(v))
    def set_playclock_25(self):
        self.quick_set_playclock(25)

    def set_playclock_40(self):
        self.quick_set_playclock(40)

    def toggle_flag(self):
        dialog = QDialog()
        dialog.setWindowTitle("Select Flag Event")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Select team:"))
        team_selector = QComboBox()
        team_selector.addItems(["Home", "Away"])
        layout.addWidget(team_selector)
        layout.addWidget(QLabel("Select flag event:"))
        flag_list = QListWidget()
        common_flags = ["Delay of Game", "Encroachment", "False Start",
        "Holding", "Illegal Formation", "Illegal Forward Pass", "Illegal Motion",
        "Offsides", "Pass Interference", "Personal Foul", "Roughing the Passer",
        "Roughing the Kicker", "Targeting", "Unnecessary Roughness", "Unsportsmanlike Conduct"]
        for flag in common_flags:
            flag_list.addItem(QListWidgetItem(flag))
        layout.addWidget(flag_list)
        layout.addWidget(QLabel("Or enter custom flag:"))
        custom_flag_input = QLineEdit()
        layout.addWidget(custom_flag_input)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        dialog.setLayout(layout)

        if dialog.exec_() == QDialog.Accepted:
            selected_team = team_selector.currentText()
            selected_flag_item = flag_list.currentItem()
            custom_flag = custom_flag_input.text().strip()
            event_text = custom_flag if custom_flag else (selected_flag_item.text() if selected_flag_item else None)
            if not event_text:
                return

            self.state.flag = True
            self.state.flag_text = "FLAG"  # Center panel always says FLAG

            # Trigger the **separate flag events**
            if selected_team == "Home":
                self.trigger_home_flag(event_text)
            else:
                self.trigger_away_flag(event_text)

            QTimer.singleShot(20000, lambda: self.clear_flag_event(selected_team))
        self.repaint_scoreboard()


    def trigger_home_flag(self, text):
        if self.state.home_event_flag_active:
            self.state.home_event_flag_active = False
            self.state.home_event_flag_text = ""
            self.state.home_event_flag_direction = -1
            self.state.home_event_flag_animating = True
            self.state.home_event_flag_start_time = time.time()
        else:
            self.state.home_event_flag_active = True
            self.state.home_event_flag_animating = True
            self.state.home_event_flag_progress = 0.0
            self.state.home_event_flag_direction = 1  # expanding
            self.state.home_event_flag_start_time = time.time()
            self.state.home_event_flag_text = text.upper()
        self.repaint_scoreboard()

    def trigger_away_flag(self, text):
        if self.state.away_event_flag_active:
            self.state.away_event_flag_active = False
            self.state.away_event_flag_text = ""
            self.state.away_event_flag_direction = -1
            self.state.away_event_flag_animating = True
            self.state.away_event_flag_start_time = time.time()
        else:
            self.state.away_event_flag_active = True
            self.state.away_event_flag_animating = True
            self.state.away_event_flag_progress = 0.0
            self.state.away_event_flag_direction = 1  # expanding
            self.state.away_event_flag_start_time = time.time()
            self.state.away_event_flag_text = text.upper()
        self.repaint_scoreboard()
    def clear_flag_event(self, team):
        if team == "Home":
            self.state.home_event_flag_active = False
            self.state.home_event_flag_text = ""
            self.state.home_event_flag_direction = -1
            self.state.home_event_flag_animating = True
            self.state.home_event_flag_start_time = time.time()
        else:
            self.state.away_event_flag_active = False
            self.state.away_event_flag_text = ""
            self.state.away_event_flag_direction = -1
            self.state.away_event_flag_animating = True
            self.state.away_event_flag_start_time = time.time()
        if (
            not self.state.home_event_flag_active
            and
            not self.state.away_event_flag_active
        ):
            self.state.flag = False
            self.state.flag_text = ""
        self.repaint_scoreboard()
    def show_intro(self, force_double=False):
        first_group=[("saway_box",-1),("shome_box",-1),("faway_box",-1),("fhome_box",-1),("cfinal_box",-1),("centerbreak",-1),("weather",-1),("lower3rd",-1),("crew",-1),("crew3",-1),("crew4",-1),("series_history",-1)]
        second_group=[("centerintro",1),("homeintro",1),("awayintro",1)]
        for name,direction in first_group:
            if getattr(self.state,f"{name}_active") and not getattr(self.state,f"{name}_animating"):
                setattr(self.state,f"{name}_animating",True)
                setattr(self.state,f"{name}_direction",direction)
                setattr(self.state,f"{name}_start_time",time.time())
        def start_second_group():
            now=time.time()
            for name,direction in second_group:
                setattr(self.state,f"{name}_animating",False)
                setattr(self.state,f"{name}_active",False)
                setattr(self.state,f"{name}_active",True)
                setattr(self.state,f"{name}_animating",True)
                setattr(self.state,f"{name}_progress",0.0)
                setattr(self.state,f"{name}_direction",direction)
                setattr(self.state,f"{name}_start_time",now)
        def wait_for_first_then_start():
            all_done=all(not getattr(self.state,f"{name}_animating") for name,_ in first_group)
            if all_done and not getattr(self.state,"intro_second_started",False):
                start_second_group()
            else:
                QTimer.singleShot(30,wait_for_first_then_start)
        if force_double:
            wait_for_first_then_start()
        else:
            all_done=all(not getattr(self.state,f"{name}_animating") for name,_ in first_group)
            if all_done and not getattr(self.state,"intro_second_started",False):
                start_second_group()
        self.scoreboard.update()
        self.btn_show_intro.set_active(True)
        self.btn_show_scorebug.set_active(False)
        self.btn_show_breakboard.set_active(False)
        self.btn_show_final.set_active(False)
        self.btn_show_weather.set_active(False)
        self.btn_show_lower3rd.set_active(False)
        self.btn_show_crew.set_active(False)
        self.btn_show_3crew.set_active(False)
        self.btn_show_4crew.set_active(False)
        self.btn_show_series.set_active(False)
    def show_breakboard(self, force_double=False):
        first_group=[("saway_box",-1),("shome_box",-1),("faway_box",-1),("fhome_box",-1),("cfinal_box",-1),("centerintro",-1),("homeintro",-1),("awayintro",-1),("weather",-1),("lower3rd",-1),("crew",-1),("crew3",-1),("crew4",-1),("series_history",-1)]
        second_group=[("centerbreak",1)]
        for name,direction in first_group:
            if getattr(self.state,f"{name}_active") and not getattr(self.state,f"{name}_animating"):
                setattr(self.state,f"{name}_animating",True)
                setattr(self.state,f"{name}_direction",direction)
                setattr(self.state,f"{name}_start_time",time.time())
        def start_second_group():
            now=time.time()
            for name,direction in second_group:
                setattr(self.state,f"{name}_animating",False)
                setattr(self.state,f"{name}_active",False)
                setattr(self.state,f"{name}_active",True)
                setattr(self.state,f"{name}_animating",True)
                setattr(self.state,f"{name}_progress",0.0)
                setattr(self.state,f"{name}_direction",direction)
                setattr(self.state,f"{name}_start_time",now)
        def wait_for_first_then_start():
            all_done=all(not getattr(self.state,f"{name}_animating") for name,_ in first_group)
            if all_done and not getattr(self.state,"breakboard_second_started",False):
                start_second_group()
            else:
                QTimer.singleShot(30,wait_for_first_then_start)
        if force_double:
            wait_for_first_then_start()
        else:
            all_done=all(not getattr(self.state,f"{name}_animating") for name,_ in first_group)
            if all_done and not getattr(self.state,"breakboard_second_started",False):
                start_second_group()
        self.scoreboard.update()
        self.btn_show_intro.set_active(False)
        self.btn_show_scorebug.set_active(False)
        self.btn_show_breakboard.set_active(True)
        self.btn_show_final.set_active(False)
        self.btn_show_weather.set_active(False)
        self.btn_show_lower3rd.set_active(False)
        self.btn_show_series.set_active(False)
        self.btn_show_crew.set_active(False)
        self.btn_show_3crew.set_active(False)
        self.btn_show_4crew.set_active(False)
    def show_scorebug(self, force_double=False):
        first_group=[("faway_box",-1),("fhome_box",-1),("cfinal_box", -1),("centerintro",-1),("homeintro",-1),("awayintro",-1),("centerbreak",-1),("weather",-1),("lower3rd",-1),("crew",-1),("crew3",-1),("crew4",-1),("series_history",-1)]
        second_group=[("saway_box",1),("shome_box",1)]
        for name,direction in first_group:
            if getattr(self.state,f"{name}_active") and not getattr(self.state,f"{name}_animating"):
                setattr(self.state,f"{name}_animating",True)
                setattr(self.state,f"{name}_direction",direction)
                setattr(self.state,f"{name}_start_time",time.time())
        def start_second_group():
            for name,direction in second_group:
                setattr(self.state,f"{name}_animating",False)
                setattr(self.state,f"{name}_active",False)
                setattr(self.state,f"{name}_active",True)
                setattr(self.state,f"{name}_animating",True)
                setattr(self.state,f"{name}_progress",0.0)
                setattr(self.state,f"{name}_direction",direction)
                setattr(self.state,f"{name}_start_time",time.time())
        def wait_for_first_then_start():
            all_done=all(not getattr(self.state,f"{name}_animating") for name,_ in first_group)
            if all_done and not getattr(self.state,"scorebug_second_started",False):
                start_second_group()
            else:
                QTimer.singleShot(30,wait_for_first_then_start)
        if force_double:
            wait_for_first_then_start()
        else:
            all_done=all(not getattr(self.state,f"{name}_animating") for name,_ in first_group)
            if all_done and not getattr(self.state,"scorebug_second_started",False):
                start_second_group()
        self.scoreboard.update()
        self.btn_show_intro.set_active(False)
        self.btn_show_scorebug.set_active(True)
        self.btn_show_breakboard.set_active(False)
        self.btn_show_final.set_active(False)
        self.btn_show_weather.set_active(False)
        self.btn_show_lower3rd.set_active(False)
        self.btn_show_series.set_active(False)
        self.btn_show_crew.set_active(False)
        self.btn_show_3crew.set_active(False)
        self.btn_show_4crew.set_active(False)
    def show_final(self, force_double=False):
        first_group=[("saway_box",-1),("shome_box",-1),("centerintro",-1),("homeintro",-1),("awayintro",-1),("centerbreak",-1),("weather",-1),("lower3rd",-1),("crew",-1),("crew3",-1),("crew4",-1),("series_history",-1)]
        second_group=[("cfinal_box",1),("faway_box",1),("fhome_box",1)]
        for name,direction in first_group:
            if getattr(self.state,f"{name}_active") and not getattr(self.state,f"{name}_animating"):
                setattr(self.state,f"{name}_animating",True)
                setattr(self.state,f"{name}_direction",direction)
                setattr(self.state,f"{name}_start_time",time.time())
        def start_second_group():
            for name,direction in second_group:
                setattr(self.state,f"{name}_animating",False)
                setattr(self.state,f"{name}_active",False)
                setattr(self.state,f"{name}_active",True)
                setattr(self.state,f"{name}_animating",True)
                setattr(self.state,f"{name}_progress",0.0)
                setattr(self.state,f"{name}_direction",direction)
                setattr(self.state,f"{name}_start_time",time.time())
        def wait_for_first_then_start():
            all_done=all(not getattr(self.state,f"{name}_animating") for name,_ in first_group)
            if all_done and not getattr(self.state,"final_second_started",False):
                start_second_group()
            else:
                QTimer.singleShot(30,wait_for_first_then_start)
        if force_double:
            wait_for_first_then_start()
        else:
            all_done=all(not getattr(self.state,f"{name}_animating") for name,_ in first_group)
            if all_done and not getattr(self.state,"final_second_started",False):
                start_second_group()
        self.scoreboard.update()
        self.btn_show_intro.set_active(False)
        self.btn_show_scorebug.set_active(False)
        self.btn_show_breakboard.set_active(False)
        self.btn_show_final.set_active(True)  
        self.btn_show_weather.set_active(False)
        self.btn_show_lower3rd.set_active(False)
        self.btn_show_crew.set_active(False)
        self.btn_show_3crew.set_active(False)
        self.btn_show_4crew.set_active(False)
        self.btn_show_series.set_active(False)
    def show_weather(self, force_double=False):
        first_group=[("saway_box",-1),("shome_box",-1),("faway_box",-1),("fhome_box",-1),("cfinal_box",-1),("centerbreak",-1),("centerintro",-1),("homeintro",-1),("awayintro",-1),("crew",-1),("lower3rd",-1),("crew3",-1),("crew4",-1),("series_history",-1)]
        second_group=[("weather",1)]
        for name,direction in first_group:
            if getattr(self.state,f"{name}_active") and not getattr(self.state,f"{name}_animating"):
                setattr(self.state,f"{name}_animating",True)
                setattr(self.state,f"{name}_direction",direction)
                setattr(self.state,f"{name}_start_time",time.time())
        def start_second_group():
            now=time.time()
            for name,direction in second_group:
                setattr(self.state,f"{name}_animating",False)
                setattr(self.state,f"{name}_active",False)
                setattr(self.state,f"{name}_active",True)
                setattr(self.state,f"{name}_animating",True)
                setattr(self.state,f"{name}_progress",0.0)
                setattr(self.state,f"{name}_direction",direction)
                setattr(self.state,f"{name}_start_time",now)
        def wait_for_first_then_start():
            all_done=all(not getattr(self.state,f"{name}_animating") for name,_ in first_group)
            if all_done and not getattr(self.state,"weather_second_started",False):
                start_second_group()
            else:
                QTimer.singleShot(30,wait_for_first_then_start)
        if force_double:
            wait_for_first_then_start()
        else:
            all_done=all(not getattr(self.state,f"{name}_animating") for name,_ in first_group)
            if all_done and not getattr(self.state,"weather_second_started",False):
                start_second_group()
        self.scoreboard.update()
        self.btn_show_intro.set_active(False)
        self.btn_show_scorebug.set_active(False)
        self.btn_show_breakboard.set_active(False)
        self.btn_show_final.set_active(False)
        self.btn_show_weather.set_active(True)
        self.btn_show_lower3rd.set_active(False)
        self.btn_show_crew.set_active(False)
        self.btn_show_series.set_active(False)
        self.btn_show_3crew.set_active(False)
        self.btn_show_4crew.set_active(False)
    def show_lower3rd(self, force_double=False):
        first_group=[("saway_box",-1),("shome_box",-1),("faway_box",-1),("fhome_box",-1),("cfinal_box",-1),("centerbreak",-1),("centerintro",-1),("homeintro",-1),("awayintro",-1),("weather",-1),("crew",-1),("crew3",-1),("crew4",-1),("series_history",-1)]
        second_group=[("lower3rd",1)]
        for name,direction in first_group:
            if getattr(self.state,f"{name}_active") and not getattr(self.state,f"{name}_animating"):
                setattr(self.state,f"{name}_animating",True)
                setattr(self.state,f"{name}_direction",direction)
                setattr(self.state,f"{name}_start_time",time.time())
        def start_second_group():
            now=time.time()
            for name,direction in second_group:
                setattr(self.state,f"{name}_animating",False)
                setattr(self.state,f"{name}_active",False)
                setattr(self.state,f"{name}_active",True)
                setattr(self.state,f"{name}_animating",True)
                setattr(self.state,f"{name}_progress",0.0)
                setattr(self.state,f"{name}_direction",direction)
                setattr(self.state,f"{name}_start_time",now)
        def wait_for_first_then_start():
            all_done=all(not getattr(self.state,f"{name}_animating") for name,_ in first_group)
            if all_done and not getattr(self.state,"lower3rd_second_started",False):
                start_second_group()
            else:
                QTimer.singleShot(30,wait_for_first_then_start)
        if force_double:
            wait_for_first_then_start()
        else:
            all_done=all(not getattr(self.state,f"{name}_animating") for name,_ in first_group)
            if all_done and not getattr(self.state,"lower3rd_second_started",False):
                start_second_group()
        self.scoreboard.update()
        self.btn_show_intro.set_active(False)
        self.btn_show_scorebug.set_active(False)
        self.btn_show_breakboard.set_active(False)
        self.btn_show_final.set_active(False)
        self.btn_show_weather.set_active(False)
        self.btn_show_series.set_active(False)
        self.btn_show_lower3rd.set_active(True)
        self.btn_show_crew.set_active(False)
        self.btn_show_3crew.set_active(False)
        self.btn_show_4crew.set_active(False)
    def show_crew(self, force_double=False):
        first_group=[("saway_box",-1),("shome_box",-1),("faway_box",-1),("fhome_box",-1),("cfinal_box",-1),("centerbreak",-1),("centerintro",-1),("homeintro",-1),("awayintro",-1),("crew3", -1),("crew4", -1),("weather",-1),("lower3rd",-1),("series_history",-1)]
        second_group=[("crew",1)]
        for name,direction in first_group:
            if getattr(self.state,f"{name}_active") and not getattr(self.state,f"{name}_animating"):
                setattr(self.state,f"{name}_animating",True)
                setattr(self.state,f"{name}_direction",direction)
                setattr(self.state,f"{name}_start_time",time.time())
        def start_second_group():
            now=time.time()
            for name,direction in second_group:
                setattr(self.state,f"{name}_animating",False)
                setattr(self.state,f"{name}_active",False)
                setattr(self.state,f"{name}_active",True)
                setattr(self.state,f"{name}_animating",True)
                setattr(self.state,f"{name}_progress",0.0)
                setattr(self.state,f"{name}_direction",direction)
                setattr(self.state,f"{name}_start_time",now)
        def wait_for_first_then_start():
            all_done=all(not getattr(self.state,f"{name}_animating") for name,_ in first_group)
            if all_done and not getattr(self.state,"crew_second_started",False):
                start_second_group()
            else:
                QTimer.singleShot(30,wait_for_first_then_start)
        if force_double:
            wait_for_first_then_start()
        else:
            all_done=all(not getattr(self.state,f"{name}_animating") for name,_ in first_group)
            if all_done and not getattr(self.state,"crew_second_started",False):
                start_second_group()
        self.scoreboard.update()
        self.btn_show_intro.set_active(False)
        self.btn_show_scorebug.set_active(False)
        self.btn_show_breakboard.set_active(False)
        self.btn_show_final.set_active(False)
        self.btn_show_weather.set_active(False)
        self.btn_show_lower3rd.set_active(False)
        self.btn_show_crew.set_active(True)
        self.btn_show_3crew.set_active(False)
        self.btn_show_series.set_active(False)
        self.btn_show_4crew.set_active(False)
    def show_crew3(self, force_double=False):
        first_group=[("saway_box",-1),("shome_box",-1),("faway_box",-1),("fhome_box",-1),("cfinal_box",-1),("centerbreak",-1),("centerintro",-1),("homeintro",-1),("awayintro",-1),("crew4", -1),("crew", -1),("weather",-1),("lower3rd",-1),("series_history",-1)]
        second_group=[("crew3",1)]
        for name,direction in first_group:
            if getattr(self.state,f"{name}_active") and not getattr(self.state,f"{name}_animating"):
                setattr(self.state,f"{name}_animating",True)
                setattr(self.state,f"{name}_direction",direction)
                setattr(self.state,f"{name}_start_time",time.time())
        def start_second_group():
            now=time.time()
            for name,direction in second_group:
                setattr(self.state,f"{name}_animating",False)
                setattr(self.state,f"{name}_active",False)
                setattr(self.state,f"{name}_active",True)
                setattr(self.state,f"{name}_animating",True)
                setattr(self.state,f"{name}_progress",0.0)
                setattr(self.state,f"{name}_direction",direction)
                setattr(self.state,f"{name}_start_time",now)
        def wait_for_first_then_start():
            all_done=all(not getattr(self.state,f"{name}_animating") for name,_ in first_group)
            if all_done and not getattr(self.state,"crew3_second_started",False):
                start_second_group()
            else:
                QTimer.singleShot(30,wait_for_first_then_start)
        if force_double:
            wait_for_first_then_start()
        else:
            all_done=all(not getattr(self.state,f"{name}_animating") for name,_ in first_group)
            if all_done and not getattr(self.state,"crew3_second_started",False):
                start_second_group()
        self.scoreboard.update()
        self.btn_show_intro.set_active(False)
        self.btn_show_scorebug.set_active(False)
        self.btn_show_breakboard.set_active(False)
        self.btn_show_final.set_active(False)
        self.btn_show_weather.set_active(False)
        self.btn_show_lower3rd.set_active(False)
        self.btn_show_crew.set_active(False)
        self.btn_show_3crew.set_active(True)
        self.btn_show_4crew.set_active(False)
        self.btn_show_series.set_active(False)
    def show_crew4(self, force_double=False):
        first_group=[("saway_box",-1),("shome_box",-1),("faway_box",-1),("fhome_box",-1),("cfinal_box",-1),("centerbreak",-1),("centerintro",-1),("homeintro",-1),("awayintro",-1),("crew3", -1),("crew", -1),("weather",-1),("lower3rd",-1),("series_history",-1)]
        second_group=[("crew4",1)]
        for name,direction in first_group:
            if getattr(self.state,f"{name}_active") and not getattr(self.state,f"{name}_animating"):
                setattr(self.state,f"{name}_animating",True)
                setattr(self.state,f"{name}_direction",direction)
                setattr(self.state,f"{name}_start_time",time.time())
        def start_second_group():
            now=time.time()
            for name,direction in second_group:
                setattr(self.state,f"{name}_animating",False)
                setattr(self.state,f"{name}_active",False)
                setattr(self.state,f"{name}_active",True)
                setattr(self.state,f"{name}_animating",True)
                setattr(self.state,f"{name}_progress",0.0)
                setattr(self.state,f"{name}_direction",direction)
                setattr(self.state,f"{name}_start_time",now)
        def wait_for_first_then_start():
            all_done=all(not getattr(self.state,f"{name}_animating") for name,_ in first_group)
            if all_done and not getattr(self.state,"crew4_second_started",False):
                start_second_group()
            else:
                QTimer.singleShot(30,wait_for_first_then_start)
        if force_double:
            wait_for_first_then_start()
        else:
            all_done=all(not getattr(self.state,f"{name}_animating") for name,_ in first_group)
            if all_done and not getattr(self.state,"crew4_second_started",False):
                start_second_group()
        self.scoreboard.update()
        self.btn_show_intro.set_active(False)
        self.btn_show_scorebug.set_active(False)
        self.btn_show_breakboard.set_active(False)
        self.btn_show_final.set_active(False)
        self.btn_show_weather.set_active(False)
        self.btn_show_lower3rd.set_active(False)
        self.btn_show_crew.set_active(False)
        self.btn_show_3crew.set_active(False)
        self.btn_show_4crew.set_active(True)
        self.btn_show_series.set_active(False)
    def show_serieshistory(self, force_double=False):
        first_group=[("saway_box",-1),("shome_box",-1),("faway_box",-1),("fhome_box",-1),("cfinal_box",-1),("centerbreak",-1),("centerintro",-1),("homeintro",-1),("awayintro",-1),("crew",-1),("lower3rd",-1),("weather",-1),("crew3",-1),("crew4",-1)]
        second_group=[("series_history",1)]
        for name,direction in first_group:
            if getattr(self.state,f"{name}_active") and not getattr(self.state,f"{name}_animating"):
                setattr(self.state,f"{name}_animating",True)
                setattr(self.state,f"{name}_direction",direction)
                setattr(self.state,f"{name}_start_time",time.time())
        def start_second_group():
            now=time.time()
            for name,direction in second_group:
                setattr(self.state,f"{name}_animating",False)
                setattr(self.state,f"{name}_active",False)
                setattr(self.state,f"{name}_active",True)
                setattr(self.state,f"{name}_animating",True)
                setattr(self.state,f"{name}_progress",0.0)
                setattr(self.state,f"{name}_direction",direction)
                setattr(self.state,f"{name}_start_time",now)
        def wait_for_first_then_start():
            all_done=all(not getattr(self.state,f"{name}_animating") for name,_ in first_group)
            if all_done and not getattr(self.state,"sh_second_started",False):
                start_second_group()
            else:
                QTimer.singleShot(30,wait_for_first_then_start)
        if force_double:
            wait_for_first_then_start()
        else:
            all_done=all(not getattr(self.state,f"{name}_animating") for name,_ in first_group)
            if all_done and not getattr(self.state,"sh_second_started",False):
                start_second_group()
        self.scoreboard.update()
        self.btn_show_intro.set_active(False)
        self.btn_show_scorebug.set_active(False)
        self.btn_show_breakboard.set_active(False)
        self.btn_show_final.set_active(False)
        self.btn_show_weather.set_active(False)
        self.btn_show_lower3rd.set_active(False)
        self.btn_show_crew.set_active(False)
        self.btn_show_3crew.set_active(False)
        self.btn_show_4crew.set_active(False)
        self.btn_show_series.set_active(True)
    def on_fg_clicked(self):
        team, ok = QInputDialog.getItem(self,"Select Team","Which team?",["Home", "Away"],editable=False)
        if ok:
            if (yards := QInputDialog.getInt(self,f"{team} Field Goal","Enter yards for attempt:",0,0,99)[0]):
                if team == "Home":
                    self.trigger_home_event(f"{yards} Yard Attempt")
                else:
                    self.trigger_away_event(f"{yards} Yard Attempt")
    def set_team_side(self, value):
        self.state.team_side = value
        self.team_side_button.setText(value.upper())
    def on_home_fg_clicked(self, yards):
        self.trigger_home_event(f"{yards} Yard Attempt")
    def on_away_fg_clicked(self, yards):
        self.trigger_away_event(f"{yards} Yard Attempt")
    def on_remove_event(self):
        if self.state.home_event_active:
            self.trigger_home_event("")  # hides home event
        elif self.state.away_event_active:
            self.trigger_away_event("")  # hides away event
    def trigger_home_event(self, text):
        if self.state.home_event_active:
            self.state.home_event_active = False
            self.state.home_event_text = ""
            self.state.home_event_direction -= 1
            self.state.home_event_animating = True
            self.state.home_event_start_time = time.time()
        else:
            self.state.home_event_active = True
            self.state.home_event_animating = True
            self.state.home_event_progress = 0.0
            self.state.home_event_direction = 1  # expanding
            self.state.home_event_start_time = time.time()
            self.state.home_event_text = text.upper()
        self.repaint_scoreboard()           
    def trigger_away_event(self, text):
        if self.state.away_event_active:
            self.state.away_event_active = False
            self.state.away_event_text = ""
            self.state.away_event_direction -= 1
            self.state.away_event_animating = True
            self.state.away_event_start_time = time.time()
        else:
            self.state.away_event_active = True
            self.state.away_event_animating = True
            self.state.away_event_progress = 0.0
            self.state.away_event_direction = 1  # expanding
            self.state.away_event_start_time = time.time()
            self.state.away_event_text = text.upper()
        self.repaint_scoreboard()
    def intro_clear(self):
        return ( not self.state.homeintro_active and not self.state.homeintro_animating and
                 not self.state.awayintro_active and not self.state.awayintro_animating and
                 not self.state.centerintro_active and not self.state.centerintro_animating
        )
    def breakboard_clear(self):
        return ( not self.state.centerbreak_active and not self.state.centerbreak_animating )
    def scorebug_clear(self):
        return ( not self.state.shome_box_active and not self.state.shome_box_animating and
                 not self.state.saway_box_active and not self.state.saway_box_animating )
    def final_clear(self):
        return ( not self.state.cfinal_box_active and not self.state.cfinal_box_animating and
                 not self.state.fhome_box_active and not self.state.fhome_box_animating and
                 not self.state.faway_box_active and not self.state.faway_box_animating )
    def weather_clear(self):
        return ( not self.state.weather_active and not self.state.weather_animating )
    def lower3rd_clear(self):
        return ( not self.state.lower3rd_active and not self.state.lower3rd_animating )
    def crew_clear(self):
        return ( not self.state.crew_active and not self.state.crew_animating )
    def crew3_clear(self):
        return ( not self.state.crew3_active and not self.state.crew3_animating )
    def crew4_clear(self):
        return ( not self.state.crew4_active and not self.state.crew4_animating )
    def sh_clear(self):
        return ( not self.state.series_history_active and not self.state.series_history_animating )
    def ui_tick(self):
        changed = False
        if self.state.breakboard_timer > 0:
            self.state.breakboard_timer -= 1
            changed = True
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
        if self.state.home_event_flag_animating:
            elapsed = time.time() - (self.state.home_event_flag_start_time or time.time())
            progress = elapsed / 3.0  # 3-second animation
            if self.state.home_event_flag_direction == 1:  # expanding
                self.state.home_event_flag_progress = min(self.state.home_event_flag_progress + progress, 1.0)
                if self.state.home_event_flag_progress >= 1.0:
                    self.state.home_event_flag_animating = False
            else:  # collapsing
                self.state.home_event_flag_progress = max(self.state.home_event_flag_progress - progress, 0.0)
                if self.state.home_event_flag_progress <= 0.0:
                    self.state.home_event_flag_animating = False
                    self.state.home_event_flag_active = False
            changed = True
        if self.state.away_event_flag_animating:
            elapsed = time.time() - (self.state.away_event_flag_start_time or time.time())
            progress = elapsed / 3.0  # 3-second animation
            if self.state.away_event_flag_direction == 1:  # expanding
                self.state.away_event_flag_progress = min(self.state.away_event_flag_progress + progress, 1.0)
                if self.state.away_event_flag_progress >= 1.0:
                    self.state.away_event_flag_animating = False
            else:  # collapsing
                self.state.away_event_flag_progress = max(self.state.away_event_flag_progress - progress, 0.0)
                if self.state.away_event_flag_progress <= 0.0:
                    self.state.away_event_flag_animating = False
                    self.state.away_event_flag_active = False
            changed = True
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
        if self.state.series_history_animating:
            elapsed = time.time() - self.state.series_history_start_time
            progress = elapsed / 3.0  # 3-second animation
            if self.state.series_history_direction == 1:  # expanding
                self.state.series_history_progress = min(self.state.series_history_progress + progress, 1.0)
                if self.state.series_history_progress >= 1.0:
                    self.state.series_history_animating = False
            else:  # collapsing
                self.state.series_history_progress = max(self.state.series_history_progress - progress, 0.0)
                if self.state.series_history_progress <= 0.0:
                    self.state.series_history_animating = False
                    self.state.series_history_active = False
            self.repaint_scoreboard()  
        if self.state.home_touchdown_animating:
            elapsed = time.time() - self.state.home_touchdown_start_time
            progress = elapsed / 3.0  # 3-second animation
            if self.state.home_touchdown_direction == 1:  # expanding
                self.state.home_touchdown_progress = min(self.state.home_touchdown_progress + progress, 1.0)
                if self.state.home_touchdown_progress >= 1.0:
                    self.state.home_touchdown_animating = False
            else:  # collapsing
                self.state.home_touchdown_progress = max(self.state.home_touchdown_progress - progress, 0.0)
                if self.state.home_touchdown_progress <= 0.0:
                    self.state.home_touchdown_animating = False
                    self.state.home_touchdown_active = False
                    self.state.trigger_scorebug = True
        if self.state.away_touchdown_animating:
            elapsed = time.time() - self.state.away_touchdown_start_time
            progress = elapsed / 3.0  # 3-second animation
            if self.state.away_touchdown_direction == 1:  # expanding
                self.state.away_touchdown_progress = min(self.state.away_touchdown_progress + progress, 1.0)
                if self.state.away_touchdown_progress >= 1.0:
                    self.state.away_touchdown_animating = False
            else:  # collapsing
                self.state.away_touchdown_progress = max(self.state.away_touchdown_progress - progress, 0.0)
                if self.state.away_touchdown_progress <= 0.0:
                    self.state.away_touchdown_animating = False
                    self.state.away_touchdown_active = False
                    self.state.trigger_scorebug = True
        if getattr(self.state, 'trigger_scorebug', False):
            self.show_scorebug(force_double=True)
            self.state.trigger_scorebug = False
            changed = True
        if getattr(self.state, 'td_timer', 0) > 0:
            print(f"[DEBUG] td_timer before decrement: {self.state.td_timer}")
            self.state.td_timer -= 1
            print(f"[DEBUG] td_timer after decrement: {self.state.td_timer}")
            changed = True
            if self.state.td_timer == 0:
                print("[DEBUG] td_timer reached 0, calling end_touchdown()")
                self.end_touchdown()
        if self.state.cfinal_box_animating:
                elapsed = time.time() - self.state.cfinal_box_start_time
                progress = elapsed / 2.5
                if self.state.cfinal_box_direction == 1:
                    self.state.cfinal_box_progress = min(self.state.cfinal_box_progress + progress, 1.0)
                    if self.state.cfinal_box_progress >= 1.0: self.state.cfinal_box_animating = False
                else:
                    self.state.cfinal_box_progress = max(self.state.cfinal_box_progress - progress, 0.0)
                    if self.state.cfinal_box_progress <= 0.0:
                        self.state.cfinal_box_animating = False
                        self.state.cfinal_box_active = False
                self.repaint_scoreboard()      
        if self.state.faway_box_animating:
                elapsed = time.time() - self.state.faway_box_start_time
                progress = elapsed / 1.0
                if self.state.faway_box_direction == 1:
                    self.state.faway_box_progress = min(self.state.faway_box_progress + progress, 1.0)
                    if self.state.faway_box_progress >= 1.0: self.state.faway_box_animating = False
                else:
                    self.state.faway_box_progress = max(self.state.faway_box_progress - progress, 0.0)
                    if self.state.faway_box_progress <= 0.0:
                        self.state.faway_box_animating = False
                        self.state.faway_box_active = False
                self.repaint_scoreboard()
        if self.state.fhome_box_animating:
                elapsed = time.time() - self.state.fhome_box_start_time
                progress = elapsed / 1.0
                if self.state.fhome_box_direction == 1:
                    self.state.fhome_box_progress = min(self.state.fhome_box_progress + progress, 1.0)
                    if self.state.fhome_box_progress >= 1.0: self.state.fhome_box_animating = False
                else:
                    self.state.fhome_box_progress = max(self.state.fhome_box_progress - progress, 0.0)
                    if self.state.fhome_box_progress <= 0.0:
                        self.state.fhome_box_animating = False
                        self.state.fhome_box_active = False
        if self.state.saway_box_animating:
                elapsed = time.time() - self.state.saway_box_start_time
                progress = elapsed / 1.0
                if self.state.saway_box_direction == 1:
                    self.state.saway_box_progress = min(self.state.saway_box_progress + progress, 1.0)
                    if self.state.saway_box_progress >= 1.0: self.state.saway_box_animating = False
                else:
                    self.state.saway_box_progress = max(self.state.saway_box_progress - progress, 0.0)
                    if self.state.saway_box_progress <= 0.0:
                        self.state.saway_box_animating = False
                        self.state.saway_box_active = False
                self.repaint_scoreboard()
        if self.state.shome_box_animating:
                elapsed = time.time() - self.state.shome_box_start_time
                progress = elapsed / 1.0
                if self.state.shome_box_direction == 1:
                    self.state.shome_box_progress = min(self.state.shome_box_progress + progress, 1.0)
                    if self.state.shome_box_progress >= 1.0: self.state.shome_box_animating = False
                else:
                    self.state.shome_box_progress = max(self.state.shome_box_progress - progress, 0.0)
                    if self.state.shome_box_progress <= 0.0:
                        self.state.shome_box_animating = False
                        self.state.shome_box_active = False
                self.repaint_scoreboard()
        if self.state.awayintro_animating:
                elapsed = time.time() - self.state.awayintro_start_time
                progress = elapsed / 2.5
                if self.state.awayintro_direction == 1:
                    self.state.awayintro_progress = min(self.state.awayintro_progress + progress, 1.0)
                    if self.state.awayintro_progress >= 1.0: self.state.awayintro_animating = False
                else:
                    self.state.awayintro_progress = max(self.state.awayintro_progress - progress, 0.0)
                    if self.state.awayintro_progress <= 0.0:
                        self.state.awayintro_animating = False
                        self.state.awayintro_active = False
                self.repaint_scoreboard()
        if self.state.weather_animating:
            elapsed = time.time() - self.state.weather_start_time
            progress = elapsed / 2.5
            if self.state.weather_direction == 1:
                self.state.weather_progress = min(self.state.weather_progress + progress, 1.0)
                if self.state.weather_progress >= 1.0:
                    self.state.weather_animating = False
            else:
                self.state.weather_progress = max(self.state.weather_progress - progress, 0.0)
                if self.state.weather_progress <= 0.0:
                    self.state.weather_animating = False
                    self.state.weather_active = False
            self.repaint_scoreboard()
        if self.state.crew_animating:
            elapsed = time.time() - self.state.crew_start_time
            progress = elapsed / 2.5
            if self.state.crew_direction == 1:
                self.state.crew_progress = min(self.state.crew_progress + progress, 1.0)
                if self.state.crew_progress >= 1.0:
                    self.state.crew_animating = False
            else:
                self.state.crew_progress = max(self.state.crew_progress - progress, 0.0)
                if self.state.crew_progress <= 0.0:
                    self.state.crew_animating = False
                    self.state.crew_active = False
            self.repaint_scoreboard()
        if self.state.crew3_animating:
            elapsed = time.time() - self.state.crew3_start_time
            progress = elapsed / 2.5
            if self.state.crew3_direction == 1:
                self.state.crew3_progress = min(self.state.crew3_progress + progress, 1.0)
                if self.state.crew3_progress >= 1.0:
                    self.state.crew3_animating = False
            else:
                self.state.crew3_progress = max(self.state.crew3_progress - progress, 0.0)
                if self.state.crew3_progress <= 0.0:
                    self.state.crew3_animating = False
                    self.state.crew3_active = False
            self.repaint_scoreboard()
        if self.state.crew4_animating:
            elapsed = time.time() - self.state.crew4_start_time
            progress = elapsed / 2.5
            if self.state.crew4_direction == 1:
                self.state.crew4_progress = min(self.state.crew4_progress + progress, 1.0)
                if self.state.crew4_progress >= 1.0:
                    self.state.crew4_animating = False
            else:
                self.state.crew4_progress = max(self.state.crew4_progress - progress, 0.0)
                if self.state.crew4_progress <= 0.0:
                    self.state.crew4_animating = False
                    self.state.crew4_active = False
            self.repaint_scoreboard()
        if self.state.lower3rd_animating:
            elapsed = time.time() - self.state.lower3rd_start_time
            progress = elapsed / 2.5
            if self.state.lower3rd_direction == 1:
                self.state.lower3rd_progress = min(self.state.lower3rd_progress + progress, 1.0)
                if self.state.lower3rd_progress >= 1.0:
                    self.state.lower3rd_animating = False
            else:
                self.state.lower3rd_progress = max(self.state.lower3rd_progress - progress, 0.0)
                if self.state.lower3rd_progress <= 0.0:
                    self.state.lower3rd_animating = False
                    self.state.lower3rd_active = False
            self.repaint_scoreboard()
        if self.state.centerbreak_animating:
                elapsed = time.time() - self.state.centerbreak_start_time
                progress = elapsed / 2.5
                if self.state.centerbreak_direction == 1:
                    self.state.centerbreak_progress = min(self.state.centerbreak_progress + progress, 1.0)
                    if self.state.centerbreak_progress >= 1.0: self.state.centerbreak_animating = False
                else:
                    self.state.centerbreak_progress = max(self.state.centerbreak_progress - progress, 0.0)
                    if self.state.centerbreak_progress <= 0.0:
                        self.state.centerbreak_animating = False
                        self.state.centerbreak_active = False
                self.repaint_scoreboard()
        if self.state.homeintro_animating:
                elapsed = time.time() - self.state.homeintro_start_time
                progress = elapsed / 2.5
                if self.state.homeintro_direction == 1:
                    self.state.homeintro_progress = min(self.state.homeintro_progress + progress, 1.0)
                    if self.state.homeintro_progress >= 1.0: self.state.homeintro_animating = False
                else:
                    self.state.homeintro_progress = max(self.state.homeintro_progress - progress, 0.0)
                    if self.state.homeintro_progress <= 0.0:
                        self.state.homeintro_animating = False
                        self.state.homeintro_active = False
                self.repaint_scoreboard()
        if self.state.centerintro_animating:
                elapsed = time.time() - self.state.centerintro_start_time
                progress = elapsed / 2.5
                if self.state.centerintro_direction == 1:
                    self.state.centerintro_progress = min(self.state.centerintro_progress + progress, 1.0)
                    if self.state.centerintro_progress >= 1.0: self.state.centerintro_animating = False
                else:
                    self.state.centerintro_progress = max(self.state.centerintro_progress - progress, 0.0)
                    if self.state.centerintro_progress <= 0.0:
                        self.state.centerintro_animating = False
                        self.state.centerintro_active = False
                self.repaint_scoreboard()
        if (self.breakboard_clear() and self.scorebug_clear() and
            self.final_clear() and self.weather_clear() and
            self.lower3rd_clear() and self.crew_clear() and
            self.crew3_clear() and self.crew4_clear() and self.sh_clear()):
            if not self.scoreboard.show_intro:
                self.scoreboard.show_intro = True
                self.scoreboard.show_breakboard = False
                self.scoreboard.show_scorebug = False
                self.scoreboard.show_weather = False
                self.scoreboard.show_football_final = False
                self.scoreboard.show_lower3rd = False
                self.scoreboard.show_crew = False
                self.scoreboard.show_crew3 = False
                self.scoreboard.show_crew4 = False
                self.scoreboard.show_serieshistory = False
        elif (self.intro_clear() and self.scorebug_clear() 
              and self.final_clear() and self.weather_clear() 
              and self.lower3rd_clear() and self.crew_clear() and
              self.crew3_clear() and self.crew4_clear() and self.sh_clear()):
            if not self.scoreboard.show_breakboard:
                self.scoreboard.show_intro = False
                self.scoreboard.show_breakboard = True
                self.scoreboard.show_scorebug = False
                self.scoreboard.show_weather = False
                self.scoreboard.show_football_final = False
                self.scoreboard.show_lower3rd = False
                self.scoreboard.show_crew = False
                self.scoreboard.show_crew3 = False
                self.scoreboard.show_crew4 = False
                self.scoreboard.show_serieshistory = False
        elif (self.intro_clear() and self.breakboard_clear() 
              and self.final_clear() and self.weather_clear() 
              and self.lower3rd_clear() and self.crew_clear() and
              self.crew3_clear() and self.crew4_clear() and self.sh_clear()):
            if not self.scoreboard.show_scorebug:
                self.scoreboard.show_intro = False
                self.scoreboard.show_breakboard = False
                self.scoreboard.show_scorebug = True
                self.scoreboard.show_weather = False
                self.scoreboard.show_football_final = False
                self.scoreboard.show_lower3rd = False
                self.scoreboard.show_crew = False
                self.scoreboard.show_crew3 = False
                self.scoreboard.show_crew4 = False
                self.scoreboard.show_serieshistory = False
        elif (self.intro_clear() and self.breakboard_clear()
                and self.scorebug_clear() and self.weather_clear() 
                and self.lower3rd_clear() and self.crew_clear() and
                self.crew3_clear() and self.crew4_clear() and self.sh_clear()):
            if not self.scoreboard.show_football_final:
                self.scoreboard.show_intro = False
                self.scoreboard.show_breakboard = False
                self.scoreboard.show_scorebug = False
                self.scoreboard.show_weather = False
                self.scoreboard.show_football_final = True
                self.scoreboard.show_lower3rd = False
                self.scoreboard.show_crew = False
                self.scoreboard.show_crew3 = False
                self.scoreboard.show_crew4 = False
                self.scoreboard.show_serieshistory = False
        elif (self.intro_clear() and self.breakboard_clear()
                and self.scorebug_clear() and self.final_clear()
                and self.lower3rd_clear() and self.crew_clear() and
                self.crew3_clear() and self.crew4_clear() and self.sh_clear()):
            if not self.scoreboard.show_weather:
                self.scoreboard.show_intro = False
                self.scoreboard.show_breakboard = False
                self.scoreboard.show_scorebug = False
                self.scoreboard.show_football_final = False
                self.scoreboard.show_weather = True
                self.scoreboard.show_lower3rd = False
                self.scoreboard.show_crew = False
                self.scoreboard.show_crew3 = False
                self.scoreboard.show_crew4 = False
                self.scoreboard.show_serieshistory = False
        elif (self.intro_clear() and self.breakboard_clear() and
              self.scorebug_clear() and self.final_clear() and 
              self.crew_clear() and self.weather_clear() and 
              self.crew3_clear() and self.crew4_clear() and self.sh_clear()):
            if not self.scoreboard.show_lower3rd:
                self.scoreboard.show_intro = False
                self.scoreboard.show_breakboard = False
                self.scoreboard.show_scorebug = False
                self.scoreboard.show_football_final = False
                self.scoreboard.show_weather = False
                self.scoreboard.show_lower3rd = True
                self.scoreboard.show_crew = False
                self.scoreboard.show_crew3 = False
                self.scoreboard.show_crew4 = False
                self.scoreboard.show_serieshistory = False
        elif (self.intro_clear() and self.breakboard_clear()
                and self.scorebug_clear() and self.final_clear()
                and self.lower3rd_clear() and self.weather_clear()
                and self.crew3_clear() and self.crew4_clear() and self.sh_clear()):
            if not self.scoreboard.show_crew:
                self.scoreboard.show_intro = False
                self.scoreboard.show_breakboard = False
                self.scoreboard.show_scorebug = False
                self.scoreboard.show_football_final = False
                self.scoreboard.show_weather = False
                self.scoreboard.show_lower3rd = False
                self.scoreboard.show_crew = True
                self.scoreboard.show_crew3 = False
                self.scoreboard.show_crew4 = False
                self.scoreboard.show_serieshistory = False
        elif (self.intro_clear() and self.breakboard_clear()
                and self.scorebug_clear() and self.final_clear()
                and self.lower3rd_clear() and self.weather_clear()
                and self.crew_clear() and self.crew4_clear() and self.sh_clear()):
            if not self.scoreboard.show_crew3:
                self.scoreboard.show_intro = False
                self.scoreboard.show_breakboard = False
                self.scoreboard.show_scorebug = False
                self.scoreboard.show_football_final = False
                self.scoreboard.show_weather = False
                self.scoreboard.show_lower3rd = False
                self.scoreboard.show_crew = True
                self.scoreboard.show_crew3 = True
                self.scoreboard.show_crew4 = False
                self.scoreboard.show_serieshistory = False
        elif (self.intro_clear() and self.breakboard_clear()
                and self.scorebug_clear() and self.final_clear()
                and self.lower3rd_clear() and self.weather_clear()
                and self.crew_clear() and self.crew3_clear() and self.sh_clear()):
            if not self.scoreboard.show_crew4:
                self.scoreboard.show_intro = False
                self.scoreboard.show_breakboard = False
                self.scoreboard.show_scorebug = False
                self.scoreboard.show_football_final = False
                self.scoreboard.show_weather = False
                self.scoreboard.show_lower3rd = False
                self.scoreboard.show_crew = False
                self.scoreboard.show_crew3 = False
                self.scoreboard.show_crew4 = True
                self.scoreboard.show_serieshistory = False
        elif (self.intro_clear() and self.breakboard_clear() and self.scorebug_clear() 
              and self.final_clear() and self.lower3rd_clear() and self.weather_clear()
                and self.crew_clear() and self.crew3_clear() and self.crew4_clear()):
            if not self.scoreboard.show_serieshistory:
                self.scoreboard.show_intro = False
                self.scoreboard.show_breakboard = False
                self.scoreboard.show_scorebug = False
                self.scoreboard.show_football_final = False
                self.scoreboard.show_weather = False
                self.scoreboard.show_lower3rd = False
                self.scoreboard.show_crew = False
                self.scoreboard.show_crew3 = False
                self.scoreboard.show_crew4 = False
                self.scoreboard.show_serieshistory = True
        if changed:
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
    def set_home_possession(self):
        self.set_possession_direct("home")
    def set_away_possession(self):
        self.set_possession_direct("away")
    def set_none_possession(self):
        self.set_possession_direct(None)
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
        self.state.is_district_game = (state == Qt.Checked)
    def set_home_score(self):
        try:
            self.state.home_pts = int(self.hm_score_box.value())
        except Exception:
            pass
        self.repaint_scoreboard()
    def add_points(self, pts, team):
        if team == "home":
            self.state.home_pts += pts
            self.hm_score_box.setValue(self.state.home_pts)
        else:
            self.state.away_pts += pts
            self.aw_score_box.setValue(self.state.away_pts)
        if pts == 6:
            self.start_touchdown(team)
        self.repaint_scoreboard()
    def start_touchdown(self, scoring_team: str):
        self.scoreboard.show_scorebug = False
        if self.scoreboard.show_scorebug:
            print("[DEBUG] Warning: failed to hide scorebug!")
        else:
            print("[DEBUG] Scorebug successfully hidden at touchdown start")
        self.state.td_timer = 65
        print(f"[DEBUG] td_timer set to {self.state.td_timer}")
        if scoring_team == "home":
            self.state.home_touchdown_active = True
            self.state.home_touchdown_animating = True
            self.state.home_touchdown_direction = 1
            self.state.home_touchdown_progress = 0.0
            self.state.home_touchdown_start_time = time.time()
            self.scoreboard.show_home_touchdown = True
            self.scoreboard.show_away_touchdown = False
            print("[DEBUG] Home touchdown started, show_home_touchdown=True, show_away_touchdown=False")
        elif scoring_team == "away":
            self.state.away_touchdown_active = True
            self.state.away_touchdown_animating = True
            self.state.away_touchdown_direction = 1
            self.state.away_touchdown_progress = 0.0
            self.state.away_touchdown_start_time = time.time()
            self.scoreboard.show_away_touchdown = True
            self.scoreboard.show_home_touchdown = False
            print("[DEBUG] Away touchdown started, show_away_touchdown=True, show_home_touchdown=False")
        print(f"[DEBUG] Scorebug status: show_scorebug={getattr(self.scoreboard, 'show_scorebug', None)}")
        self.scoreboard.update()
    def end_touchdown(self):
        if self.state.home_touchdown_active:
            self.state.home_touchdown_direction -= 1
            self.state.home_touchdown_animating = True
            self.state.home_touchdown_progress = 0.0
            self.state.home_touchdown_start_time = time.time()
        if self.state.away_touchdown_active:
            self.state.away_touchdown_direction -= 1
            self.state.away_touchdown_animating = True
            self.state.away_touchdown_progress = 0.0
            self.state.away_touchdown_start_time = time.time()
        self.scoreboard.update()
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
            prev = self.state.away_timeouts
            self.state.away_timeouts = max(0, min(3, prev + delta))
            self.away_to_lcd.display(self.state.away_timeouts)
            if delta < 0 and self.state.away_timeouts < prev:
                self.stop_clock()
                taken_number = 3 - self.state.away_timeouts  # 1, 2, or 3
                suffix = ["1st", "2nd", "3rd"]
                self.state.away_timeout_text = f"{suffix[taken_number - 1]} Timeout"
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
            prev = self.state.home_timeouts
            self.state.home_timeouts = max(0, min(3, prev + delta))
            self.home_to_lcd.display(self.state.home_timeouts)
            if delta < 0 and self.state.home_timeouts < prev:
                self.stop_clock()
                taken_number = 3 - self.state.home_timeouts
                suffix = ["1st", "2nd", "3rd"]
                self.state.home_timeout_text = f"{suffix[taken_number - 1]} Timeout"
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
        path, _ = QFileDialog.getOpenFileName(
        self,
        "Open home logo",
        "",
        "Images (*.png *.jpg *.jpeg *.bmp *.webp)"
    )
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
    def set_possession(self):
        val = self.possession_combo.currentText()
        if val == "None":
            self.state.possession = None
        elif val == "Away":
            self.state.possession = "away"
        else:
            self.state.possession = "home"
        self.repaint_scoreboard()
    def set_period(self):
        try:
            new_period = int(self.period_spin.value())
            self.state.period = new_period
        except Exception:
            return
        if new_period == 3 and not getattr(self, 'period_timeout_applied', False):
            self.state.home_timeouts = 3
            self.state.away_timeouts = 3
            self.state.period_timeout_applied = True
        if 1 <= new_period <= 4:
            self.state.minutes = 12
            self.state.seconds = 0
        elif new_period == 10:
            self.state.minutes = 20
            self.state.seconds = 0
            self.state.distance = "HALFTIME"
            if hasattr(self, "dist_edit"):
                self.dist_edit.setCurrentText("HALFTIME")
        else:
            self.state.minutes = 0
            self.state.seconds = 0
        if hasattr(self, "time_lcd"):
            self.time_lcd.display(f"{self.state.minutes:02d}:{self.state.seconds:02d}")
        if hasattr(self, "home_to_lcd"):
            self.home_to_lcd.display(self.state.home_timeouts)
        if hasattr(self, "away_to_lcd"):
            self.away_to_lcd.display(self.state.away_timeouts)
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
            return self.state.minutes, self.state.seconds
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
        self.state.minutes = m
        self.state.seconds = s
        if hasattr(self, "time_lcd"):
            self.time_lcd.display(f"{m:02d}:{s:02d}")
        self.repaint_scoreboard()
    def start_clock(self):
        m, s = self._read_clock_inputs()
        # store to state and start timer
        self.state.minutes = m
        self.state.seconds = s
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
        self.state.minutes = 12
        self.state.seconds = 0
        if hasattr(self, "time_lcd"):
            self.time_lcd.display("12:00")
        if hasattr(self, "min_edit"):
            self.min_edit.setValue(12)
        if hasattr(self, "sec_edit"):
            self.sec_edit.setValue(0)
        self.repaint_scoreboard()
    def start_play_clock(self):
        self.state.playclock = int(self.pc_spin.value())
        if not self.play_timer.isActive():
            self.play_timer.start()
        self.state.play_running = True
        self.repaint_scoreboard()
    def stop_play_clock(self):
     if self.play_timer.isActive():
        self.play_timer.stop()
        self.state.play_running = False
     self.repaint_scoreboard()
    def reset_play_clock(self):
        self.state.playclock = int(self.pc_spin.value(40))
        self.repaint_scoreboard()
    def game_tick(self):
        self.state.game_running = True
        total = self.state.minutes * 60 + self.state.seconds
        if total <= 0:
            self.state.minutes = 0
            self.state.seconds = 0
            self.timer.stop()
            self.state.game_running = False

            self.time_lcd.display("00:00")
            self.repaint_scoreboard()
            return
        total -= 1
        self.state.minutes = total // 60
        self.state.seconds = total % 60
        self.time_lcd.display(f"{self.state.minutes}:{self.state.seconds:02d}")
        self.min_edit.setValue(self.state.minutes)
        self.sec_edit.setValue(self.state.seconds)
        self.repaint_scoreboard()
    def play_tick(self):
        if self.state.playclock > 0:
            self.state.playclock -= 1
        else:
            self.play_timer.stop()
            self.state.play_running = False
        self.pc_spin.setValue(self.state.playclock)
        self.repaint_scoreboard()
    def set_down_distance(self):
        try:
            self.state.down = int(self.down_spin.currentText())
        except Exception:
            pass
        text = self.dist_edit.currentText().strip()
        self.state.distance = text
        dist = text.lower()
        away = self.state.away_pts
        home = self.state.home_pts
        if "final" in dist and hasattr(self, "btn_show_final"):
            if not self.scoreboard.show_football_final:
                self.btn_show_final.click()
        if "final" in dist:
            if not self.state.final_record_updated:
                if away > home:
                    self.state.away_record_wins += 1
                    self.state.home_record_losses += 1
                elif home > away:
                    self.state.home_record_wins += 1
                    self.state.away_record_losses += 1
            if self.chk_district.isChecked():
                if away > home:
                    self.state.away_district_wins += 1
                    self.state.home_district_losses += 1
                elif home > away:
                    self.state.home_district_wins += 1
                    self.state.away_district_losses += 1
            self.state.final_record_updated = True
        else:
            self.state.final_record_updated = False
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
    def set_team_side(self,side):
        if side not in ["home","away","center"]:
            return
        self.state.team_side=side
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