import os
import sys
import ctypes

# --- Make Windows per-monitor DPI aware ---
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # 2 = PER_MONITOR_AWARE
except Exception:
    pass

# --- Let Qt scale automatically based on monitor DPI ---
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"  # enable auto scaling
# os.environ["QT_SCALE_FACTOR"] = "1"            # optional: only set if you want manual override
import serial
import serial.tools.list_ports
import threading
import requests
import webbrowser
import time
import os
import math
from PySide6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLineEdit, QFileDialog, QDialog, QRadioButton, QGraphicsRectItem ,  QColorDialog, QSpinBox, QMessageBox, QComboBox, QTabWidget, QLCDNumber, QCheckBox,
    QGraphicsScene, QGraphicsPolygonItem, QGraphicsBlurEffect, QMenu, QInputDialog, QSizePolicy, QGroupBox, QGridLayout, QVBoxLayout
)
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PySide6.QtCore import Qt, QTimer, QRect, QPointF, QRectF, QObject, Signal, QUrl, Property, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import (
    QPainter, QPolygonF, QColor, QIntValidator, QFont, QFontMetrics, QPixmap, QBrush,
    QPen, QLinearGradient, QPainterPath, QRadialGradient, QImage, QTextOption, QFontDatabase, QFont, QIcon
)
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "0"
os.environ["QT_SCALE_FACTOR"] = "1"
current_version = "2.2.1"
required_update = True
version_url = "https://raw.githubusercontent.com/CamronAnderson2025/Offical-Scorebug/main/version.txt"
download_url = "https://github.com/CamronAnderson2025/Offical-Scorebug/releases"
class LogoWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)       
        # Layout
        layout = QVBoxLayout(self)
        
        # Input field for custom URL
        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText("Enter image URL here")
        layout.addWidget(self.url_input)
        
        # Load button
        self.load_btn = QPushButton("Load A Logo", self)
        layout.addWidget(self.load_btn)
        
        # Label to display logo
        self.logo_label = QLabel(self)
        layout.addWidget(self.logo_label)
        
        # Connect button click to loading function
        self.load_btn.clicked.connect(self.on_load_clicked)
        
        # Network manager
        self._logo_manager = QNetworkAccessManager(self)
        self._logo_manager.finished.connect(self._on_logo_loaded)

    # Called when the user clicks "Load Logo"
    def on_load_clicked(self):
        url = self.url_input.text().strip()
        if url:
            self._load_logo(url)
        
    # Fetch the image from URL
    def _load_logo(self, image_url: str):
        request = QNetworkRequest(QUrl(image_url))
        self._logo_manager.get(request)

    # Callback when the image is loaded
    def _on_logo_loaded(self, reply):
        data = reply.readAll()
        pixmap = QPixmap()
        if pixmap.loadFromData(data):
            self.logo_label.setPixmap(pixmap)
        reply.deleteLater()

def check_for_updates():
    try:
        latest = requests.get(version_url, timeout=3).text.strip()
        if latest != current_version:
            msg = f"A new version ({latest}) is available!"
            if required_update:
                msg += "\nYou must update to continue."

            reply = QMessageBox.question(
                None,
                "Update Available",
                msg,
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                webbrowser.open(download_url)
                if required_update:
                    sys.exit(0)  # Close old app
            else:
                if required_update:
                    sys.exit(0)  # Close old app if update is required
    except Exception:
        pass


class LogoReveal(QObject):
    def __init__(self):
        super().__init__()
        self._progress = 0.0  # 0 → hidden, 1 → fully shown

    def get(self):
        return self._progress

    def set(self, v):
        self._progress = v

    progress = Property(float, get, set)

class ScoreState:
    def __init__(self):
        self.home_pts = 0
        self.td_timer = 0
        self.goal_timer = 0
        self.away_logo_score_anim = 0
        self.home_logo_score_anim = 0
        self.away_pts = 0
        self.home_name = "HOME"
        self.away_name = "AWAY"
        self.home_mascot = "HM Mascot"
        self.away_mascot = "AW Mascot"
        self.away_rank = 0
        self.home_rank = 0
        self.tenths_basketball = 0
        self.touchdown_text = "TOUCHDOWN"
        self.goal_text = "G          O          A          L!"
        self.breakboard_timer = 0
        self.home_color = QColor("#009639")
        self.away_color = QColor("#efbf04")
        self.home_logo = None
        self.trigger_scorebug = False
        self.away_logo = None
        self.center_logo = None
        self.possession = None
        self.serial_port = "COM16"
        self.serial_baud = 19200
        self.serial_enabled = False
        self.breakboard_started = False
        self.last_intro_press = 0
        self.flag_text = "FLAG"
        self.final_text = "FINAL"
        self.final_ot_text = ""
        self.flag = False
        self.home_logo_timer = 0
        self.away_logo_timer = 0
        self.LOGO_TOTAL = 30  
        self.serial_thread = None
        self.minutes = 12
        self.seconds = 0
        self.minutes_basketball = 8
        self.seconds_basketball = 0
        self.minutes_soccer = 40
        self.seconds_soccer = 0
        self.animations_initialized = False
        self.home_3_made = 0
        self.home_3_total = 0
        self.home_ft_made = 0
        self.home_ft_total = 0
        self.away_3_made = 0
        self.away_3_total = 0
        self.away_ft_made = 0
        self.away_ft_total = 0
        self.game_running = False
        self.play_running = False
        self.is_district_game = False
        self.final_record_updated = False
        self.game_final = False
        self.home_event_active = False
        self.home_event_text = ""
        self.away_event_active = False
        self.away_event_text = ""
        self.stat_upper_text = ""
        self.period = 1
        self.down = 1
        self.distance = 10
        self.playclock = 40
        self.away_record_wins = 0
        self.away_record_losses = 0
        self.away_district_wins = 0
        self.away_district_losses = 0
        self.away_timeout_pop_timer = 0
        self.away_timeout_text = ""
        self.away_timeout_bar_timer = 0
        self.home_timeout_bar_timer = 0
        self.home_timeout_pop_timer = 0
        self.home_timeout_text = ""
        self.bottom_event_active = False
        self.bottom_event_animating = False
        self.bottom_event_direction = 1
        self.bottom_event_progress = 0.0
        self.bottom_event_start_time = 0
        self.bottom_event_text_football = ""
        self.bottom_event_text_basketball = ""
        self.bottom_event_text_soccer = ""
        self.upperbb_event_active = True
        self.upperbb_event_text_basketball = ""
        self.event_location_school_text = ""
        self.event_location_city_text = ""
        self.away_timeouts = 3
        self.home_timeouts = 3
        self.period_timeout_applied = False
        self.home_timeouts_basketball = 5
        self.away_timeouts_basketball = 5
        self.home_timeouts_volleyball = 2
        self.away_timeouts_volleyball = 2
        self.away_sets_won = 0
        self.home_sets_won = 0
        self.home_record_wins = 0
        self.home_record_losses = 0
        self.home_district_wins = 0
        self.home_district_losses = 0
        self.away_fouls = 0
        self.home_fouls = 0
        self.home_event_animating = False
        self.home_event_progress = 0.0
        self.home_event_start_time = None
        self.home_event_direction = 1
        self.scenter_scorebug_direction = 1
        self.scenter_scorebug_animating = False
        self.scenter_scorebug_progress = 0.0
        self.scenter_scorebug_start_time = None
        self.scenter_scorebug_active = False
        self.away_event_animating = False
        self.away_event_progress = 0.0
        self.away_event_start_time = None
        self.away_event_direction = 1
        self.stat_home_upper_text = ""
        self.right_box_direction = 1
        self.right_box_animating = False
        self.right_box_progress = 0.0
        self.right_box_start_time = None
        self.right_box_active = False  
        self.away_box_active = False
        self.away_box_animating = False
        self.away_box_progress = 0.0
        self.away_box_start_time = None
        self.away_box_direction = 1
        self.center_rect_active = False
        self.center_rect_animating = False
        self.center_rect_progress = 0.0
        self.center_rect_start_time = None
        self.center_rect_direction = 1
        self.right_break_box_active = False
        self.right_break_box_animating = False
        self.right_break_box_progress = 0.0
        self.right_break_box_start_time = None
        self.right_break_box_direction = 1
        self.left_break_box_active = False
        self.left_break_box_animating = False
        self.left_break_box_progress = 0.0
        self.left_break_box_start_time = None
        self.left_break_box_direction = 1
        self.icenter_rect_active = False
        self.icenter_rect_animating = False
        self.icenter_rect_progress = 0.0
        self.icenter_rect_start_time = None
        self.icenter_rect_direction = 1
        self.iright_break_box_active = False
        self.iright_break_box_animating = False
        self.iright_break_box_progress = 0.0
        self.iright_break_box_start_time = None
        self.iright_break_box_direction = 1
        self.ileft_break_box_active = False
        self.ileft_break_box_animating = False
        self.ileft_break_box_progress = 0.0
        self.ileft_break_box_start_time = None
        self.ileft_break_box_direction = 1
        self.bcenter_rect_active = False
        self.center_rect_animating = False
        self.center_rect_progress = 0.0
        self.center_rect_start_time = None
        self.center_rect_direction = 1
        self.right_break_box_active = False
        self.right_break_box_animating = False
        self.right_break_box_progress = 0.0
        self.right_break_box_start_time = None
        self.right_break_box_direction = 1
        self.left_break_box_active = False
        self.left_break_box_animating = False
        self.left_break_box_progress = 0.0
        self.left_break_box_start_time = None
        self.left_break_box_direction = 1
        self.scenter_rect_active = False
        self.scenter_rect_animating = False
        self.scenter_rect_progress = 0.0
        self.scenter_rect_start_time = None
        self.scenter_rect_direction = 1
        self.sright_break_box_active = False
        self.sright_break_box_animating = False
        self.sright_break_box_progress = 0.0
        self.sright_break_box_start_time = None
        self.sright_break_box_direction = 1
        self.sleft_break_box_active = False
        self.sleft_break_box_animating = False
        self.sleft_break_box_progress = 0.0
        self.sleft_break_box_start_time = None
        self.sleft_break_box_direction = 1
        self.fcenter_rect_active = False
        self.fcenter_rect_animating = False
        self.fcenter_rect_progress = 0.0
        self.fcenter_rect_start_time = None
        self.fcenter_rect_direction = 1
        self.fright_break_box_active = False
        self.fright_break_box_animating = False
        self.fright_break_box_progress = 0.0
        self.fright_break_box_start_time = None
        self.fright_break_box_direction = 1
        self.fleft_break_box_active = False
        self.fleft_break_box_animating = False
        self.fleft_break_box_progress = 0.0
        self.fleft_break_box_start_time = None
        self.fleft_break_box_direction = 1
        self.cfinal_box_active=False
        self.cfinal_box_animating=False
        self.cfinal_box_progress=0.0
        self.cfinal_box_start_time=None
        self.cfinal_box_direction=1
        self.faway_box_active = False
        self.faway_box_animating = False
        self.faway_box_progress = 0.0
        self.faway_box_start_time = None
        self.faway_box_direction = 1
        self.fhome_box_active = False
        self.fhome_box_animating = False
        self.fhome_box_progress = 0.0
        self.fhome_box_start_time = None
        self.fhome_box_direction = 1
        self.saway_box_active = False
        self.saway_box_animating = False
        self.saway_box_progress = 0.0
        self.saway_box_start_time = None
        self.saway_box_direction = 1
        self.shome_box_active = False
        self.shome_box_animating = False
        self.shome_box_progress = 0.0
        self.shome_box_start_time = None
        self.shome_box_direction = 1
        self.centerintro_active = False
        self.centerintro_animating = False
        self.centerintro_progress = 0.0
        self.centerintro_start_time = None
        self.centerintro_direction = 1
        self.homeintro_active = False
        self.homeintro_animating = False
        self.homeintro_progress = 0.0
        self.homeintro_start_time = None
        self.homeintro_direction = 1
        self.awayintro_active = False
        self.awayintro_animating = False
        self.awayintro_progress = 0.0
        self.awayintro_start_time = None
        self.awayintro_direction = 1
        self.centerbreak_active = False
        self.centerbreak_animating = False
        self.centerbreak_progress = 0.0
        self.centerbreak_start_time = None
        self.centerbreak_direction = 1
        self.home_touchdown_active = False
        self.home_touchdown_animating = False
        self.home_touchdown_progress = 0.0
        self.home_touchdown_start_time = None
        self.home_touchdown_direction = 1
        self.away_touchdown_active = False
        self.away_touchdown_animating = False
        self.away_touchdown_progress = 0.0
        self.away_touchdown_start_time = None
        self.away_touchdown_direction = 1
state = ScoreState()

class UIUpdater(QObject):
    refresh = Signal()
ui_updater = UIUpdater()

class FootballScoreboard(QWidget):
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
        self.setMinimumSize(1920, 1080)
        self.resize(1920, 1080)
        self.monument_font = QFont("Monument Extended", 40)
        self.mascot_font = QFont("College", 33, QFont.Bold)
        self.big_font = QFont("College", 40, QFont.Bold)
        self.mid_font = QFont("College", 22, QFont.Bold)
        self.small_font = QFont("College", 14)
        self.title_font = QFont("BigNoodleTitling", 16, QFont.Bold)
        self.tdtitle_font = QFont("BigNoodleTitling", 18, QFont.Bold)
        self.introtitle_font = QFont("BigNoodleTitling", 33, QFont.Bold)
        self.introupper_font = QFont("BigNoodleTitling", 25, QFont.Bold)
        self.rank_font = QFont("BigNoodleTitling", 14)
        self.tdrank_font = QFont("BigNoodleTitling", 16)
        self.introrank_font = QFont("BigNoodleTitling", 30)
        self.introschool_font = QFont("BigNoodleTitling", 30, QFont.Bold)
        self.introcity_font = QFont("BigNoodleTitling", 22, QFont.Bold)
        self.timer_font = QFont("Legacy", 25, QFont.Bold)
        self.bbtimer_font = QFont("Legacy", 15)
        self.period_font = QFont("Legacy", 15, QFont.Bold)
        self.bbperiod_font = QFont("Legacy", 15)
        self.dd_font = QFont("Legacy", 18, QFont.Bold)
        self.pc_font = QFont("Legacy", 15, QFont.Bold)
        self.score_font = QFont("Octin Sports", 40, QFont.Bold)
        self.final_font = QFont("BigNoodleTitling", 30, QFont.Bold)
        self.bbscore_font = QFont("Octin Sports", 55, QFont.Bold)
        self.event_font = QFont("Legacy", 12, QFont.Bold)
        self.td_font = QFont("Octin Sports", 44, QFont.Bold)
        self.record_font = QFont("College", 12, QFont.Bold)
        self.introrecord_font = QFont("College", 24, QFont.Bold)
        self.center_logo_label = QLabel(self)
        self.center_logo_label.setAlignment(Qt.AlignCenter)
        self.request_logo_file()
        ui_updater.refresh.connect(self.update)
        if self.mode == "transparent":
            self.setAttribute(Qt.WA_TranslucentBackground)
        else:
            self.bg_color = QColor(255, 0, 255)  # green chroma key for vMix
        self.setAutoFillBackground(False)

    def request_logo_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Center Logo", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)")
        if file_path:
            self._load_center_logo(file_path)

    def _load_center_logo(self, file_path: str = ""):
        if not file_path:
            return
        pixmap = QPixmap(file_path)
        if pixmap.isNull():
            QMessageBox.warning(self, "Error", "Failed to load image from the selected file.")
        else:
            self.state.center_logo = pixmap
            self.update()

    def paintEvent(self, event):
        DESIGN_W=1920
        DESIGN_H=1080
        p=QPainter(self)
        p.setRenderHints(QPainter.Antialiasing|QPainter.TextAntialiasing)
        scale=min(self.width()/DESIGN_W,self.height()/DESIGN_H)  # scale to fit window
        offset_x=(self.width()-DESIGN_W*scale)/2
        offset_y=(self.height()-DESIGN_H*scale)/2
        p.translate(offset_x,offset_y)
        p.scale(scale,scale)  # ignore Windows DPI completely
        if self.mode == "keyable":
            # solid green for chroma key
            p.fillRect(self.rect(), self.bg_color)
        if self.show_intro:
            self.draw_intro(p)
        if self.show_scorebug and not (self.state.home_touchdown_active or self.state.away_touchdown_active):
            self.draw_scorebug(p)
        if self.show_home_touchdown:
            self.draw_home_touchdown(p)
        if self.show_away_touchdown:
            self.draw_away_touchdown(p)
        if self.show_breakboard:
            self.draw_breakboard(p)
        if self.show_football_final:
            self.draw_football_final(p)
            return
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
            if not (rw==0 and rl==0):
                p.drawText(left_x+200,964.5,120,35,Qt.AlignLeft,f"{rw}-{rl}")
            if not (dw==0 and dl==0):
                p.drawText(left_x+180,960,120,35,Qt.AlignLeft,f"({dw}-{dl})")
            rank,name=self.format_rank_name(self.state.away_rank,self.state.away_name)
            metrics_rank=QFontMetrics(self.introrank_font)
            metrics_name=QFontMetrics(self.introtitle_font)
            rank_w=metrics_rank.horizontalAdvance(rank) if rank else 0
            name_w=metrics_name.horizontalAdvance(name) if name else 0
            base_x=left_x+20
            gap=5
            total_w=rank_w+(gap if rank else 0)+name_w
            right_limit=left_x+275
            available=right_limit-base_x-5
            scale=1.0
            if total_w>available and available>0:
                scale=available/total_w
            rank_w=int(rank_w*scale)
            name_w=int(name_w*scale)
            if rank:
                font=QFont(self.introrank_font)
                font.setPointSizeF(font.pointSizeF()*scale)
                p.setFont(font)
                p.drawText(base_x,880,rank_w,35,Qt.AlignRight|Qt.AlignVCenter,rank)
                name_x=base_x+rank_w+gap
            else:
                name_x=base_x
            font=QFont(self.introtitle_font)
            font.setPointSizeF(font.pointSizeF()*scale)
            p.setFont(font)
            p.drawText(name_x,880,name_w+2,35,Qt.AlignLeft|Qt.AlignVCenter,name)
            mascot=getattr(self.state,"away_mascot",None)
            if mascot:
                metrics_mascot=QFontMetrics(self.introtitle_font)
                mascot_w=metrics_mascot.horizontalAdvance(mascot)
                mascot_y=928
                mascot_max_w=right_limit-name_x-6
                if mascot_max_w>0 and mascot_w>mascot_max_w:
                    mascot=metrics_mascot.elidedText(mascot,Qt.ElideRight,mascot_max_w)
                    mascot_w=metrics_mascot.horizontalAdvance(mascot)
                used_w=min(mascot_w,mascot_max_w) if mascot_max_w>0 else mascot_w
                mascot_x=right_limit-used_w-10
                p.drawText(mascot_x,mascot_y,used_w,30,Qt.AlignRight|Qt.AlignVCenter,mascot)
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
            rank,name=self.format_rank_name(self.state.home_rank,self.state.home_name)
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
            p.drawText(cx-30,800,480,35,Qt.AlignLeft,"High School Football")
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
        # -- KEY INFORMATUION (DO NOT CHANGE W/O PROPER TESTING) -- #
        left_x = 615
        left_w = 370
        right_x = 935
        right_w = 370
        dd_x = 876
        dd_w = 170
        cx = 866
        cw = 190
        cy = 945
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

            bar_height = 20
            start_y = 965
            end_y = 945
            if t > ANIM:  # sliding up or steady
                bar_y = int(start_y - (start_y - end_y) * progress)
            else:         # sliding down
                bar_y = int(end_y + (start_y - end_y) * (1 - progress))

            self.draw_top_rounded_rect(p, left_x + 3, bar_y, left_w - 115, bar_height, QColor("#2a2a2a"), radius=7)
            self.draw_glow_top_round(p, left_x + 3, bar_y, left_w - 115, bar_height, self.state.away_color)

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
            self.draw_timeout_popup(p, left_x + 58, bar_y, self.state.away_timeout_text)
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
            bar_height = 20
            start_y = 965
            end_y = 945
            bar_y = int(start_y - (start_y - end_y) * progress)
            self.draw_top_rounded_rect(p, right_x + 113, bar_y, right_w - 115, bar_height, QColor("#2a2a2a"), radius=7)
            self.draw_glow_top_round(p, right_x + 113, bar_y, right_w - 115, bar_height, self.state.home_color)
            if t > TOTAL - FADE_IN: alpha = (TOTAL - FADE_IN - t) / FADE_IN
            elif t < FADE_OUT: alpha = t / FADE_OUT
            else: alpha = 1.0
            alpha = max(0.0, min(alpha, 1.0))
            p.save()
            p.setOpacity(alpha)
            self.draw_timeout_popup(p, right_x + 168, bar_y, self.state.home_timeout_text)
            p.restore()
            self.state.home_timeout_bar_timer -= 1
        if self.state.home_event_active or self.state.home_event_animating:
            progress = max(0.0, min(self.state.home_event_progress, 1.0))
            bar_height = 20
            start_y = 965  # fully hidden
            end_y = 945    # fully visible
            bar_y = int(start_y - (start_y - end_y) * progress)
            self.draw_top_rounded_rect(p, right_x + 113, bar_y, right_w - 115, bar_height, QColor("#2a2a2a"), radius=7)
            self.draw_glow_top_round(p, right_x + 113, bar_y, right_w - 115, 20, self.state.home_color)
            if progress > 0.7:
                alpha = min((progress - 0.7)/0.2, 1.0)
            else:
                alpha = 0.0
            p.save()
            p.setOpacity(alpha)
            self.draw_event_text(p, right_x + 120, bar_y, self.state.home_event_text)
            p.restore()
        if self.state.away_event_active or self.state.away_event_animating:
            progress = max(0.0, min(self.state.away_event_progress, 1.0))
            bar_height = 20
            start_y = 965  # fully hidden
            end_y = 945    # fully visible
            bar_y = int(start_y - (start_y - end_y) * progress)
            self.draw_top_rounded_rect(p, left_x + 3, bar_y, left_w - 115, bar_height, QColor("#2a2a2a"), radius=7)
            self.draw_glow_top_round(p, left_x + 3, bar_y, left_w - 115, 20, self.state.away_color)
            if progress > 0.7:
                alpha = min((progress - 0.7) / 0.2, 1.0)
            else:
                alpha = 0.0
            p.save()
            p.setOpacity(alpha)
            self.draw_event_text(p, left_x + 13, bar_y, self.state.away_event_text)
            p.restore()        
        # -- AWAY SECTION -- #      
        if self.state.saway_box_active:
            p.setFont(self.record_font)
            p.setPen(Qt.white)
            progress=self.state.saway_box_progress
            full_width=left_w+330
            center_x=left_x-4+full_width//2
            curr_w=int(full_width*progress)
            self.draw_fully_rounded_rect(p,center_x-curr_w//2,965,curr_w,80,QColor("#2a2a2a"))
            bottom_w=697
            bottom_center=612+bottom_w//2
            curr_bottom=int(bottom_w*progress)
            self.draw_bottom_round_rect(p,bottom_center-curr_bottom//2,1035,curr_bottom,10,QColor("#5E5E5E"),10)
            if self.state.possession == 'away':
                self.draw_glow_round_left(p,left_x-3,965,left_w+22,80,self.state.away_color)
            if self.state.possession == 'home':
                self.draw_glow_round_right(p,right_x-20,965,right_w+23,80,self.state.home_color)  
            curr_width = int(left_w * self.state.saway_box_progress)
            self.draw_base_bar(p, left_x + left_w - curr_width, 985, curr_width, 55)
            pod_full_width = left_w - 255
            pod_start_progress = 0.5  # start after base bar fully extended
            if progress >= pod_start_progress:
    # compute relative progress for pod (0 → 1)
                pod_progress = (progress - pod_start_progress) / (1.0 - pod_start_progress)
                curr_pod_width = int(pod_full_width * pod_progress)
                self.draw_pod(p, left_x + pod_full_width - curr_pod_width, 985, curr_pod_width, 55, self.state.away_color)

            logo_x = left_x + 5
            logo_y = 968
            logo_w = 80
            logo_h = 75
            p.save()
            self.clip_to_rounded_rect(p, left_x, 985, left_w - 5, 55)
            self.draw_logo_in_top_rounded_window(p, logo_x, logo_y, logo_w, logo_h, self.state.away_logo)
            p.restore()
            fade_delay = 0.7
            if progress <= fade_delay:
                opacity = 0.0
            else:
                opacity = (progress - fade_delay) / (1.0 - fade_delay)
            opacity = min(max(opacity, 0.0), 1.0)
            p.setOpacity(opacity)
            if not (rw == 0 and rl == 0):
                p.drawText(logo_x + 120, logo_y + 50, 120, 18, Qt.AlignLeft, f"{rw}-{rl}")
            if not (dw == 0 and dl == 0):
                p.drawText(logo_x + 113, logo_y + 70, 120, 18, Qt.AlignLeft, f"({dw}-{dl})")
            rank, name = self.format_rank_name(self.state.away_rank, self.state.away_name)
            metrics_rank = QFontMetrics(self.rank_font)
            rank_w = metrics_rank.horizontalAdvance(rank) if rank else 0
            rank_x = left_x + 10
            if rank:
                p.setFont(self.rank_font)
                p.setPen(Qt.white)
                p.drawText(rank_x, 962, rank_w, 26, Qt.AlignLeft | Qt.AlignVCenter, rank)
            metrics_name = QFontMetrics(self.title_font)
            name_w = metrics_name.horizontalAdvance(name)
            name_x = rank_x + rank_w + 6
            p.setFont(self.title_font)
            p.setPen(Qt.white)
            p.drawText(name_x, 962, name_w, 26, Qt.AlignLeft | Qt.AlignVCenter, name)
            p.setFont(self.score_font)
            p.setPen(Qt.white)
            p.drawText(left_x + 157 , 970, 120, 70, Qt.AlignCenter, str(self.state.away_pts))
            self.draw_timeout_rects(p, left_x + 180, 1030, self.state.away_timeouts)
            p.setOpacity(1.0)

        # -- HOME SECTION -- #
        if self.state.shome_box_active:
            progress = self.state.shome_box_progress
            curr_width = int(right_w * progress)
            self.draw_hmbase_bar(p, right_x, 985, curr_width, 55)
            pod_full_width = right_w - 255
            pod_start_progress = 0.5  # start after 50% of base bar animation
            if progress >= pod_start_progress:
                pod_progress = (progress - pod_start_progress) / (1.0 - pod_start_progress)
                curr_pod_width = int(pod_full_width * pod_progress)
                self.draw_hmpod(p, right_x + 255, 985, curr_pod_width, 55, self.state.home_color)
            logo_x = right_x + 280
            logo_y = 975
            logo_w = 80
            logo_h = 75
            p.save()
            self.clip_to_rounded_rect(p, right_x, 985, right_w, 55)
            self.draw_logo_in_top_rounded_window(p, logo_x, logo_y, logo_w, logo_h, self.state.home_logo)
            p.restore()
            fade_delay = 0.7
            if progress <= fade_delay:
                opacity = 0.0
            else:
                opacity = (progress - fade_delay) / (1.0 - fade_delay)
            opacity = min(max(opacity, 0.0), 1.0)
            p.setOpacity(opacity)
            if not (hw == 0 and hl == 0):
                p.drawText(logo_x - 154, logo_y + 50, 120, 18, Qt.AlignRight, f"{hw}-{hl}")
            if not (hdw == 0 and hdl == 0):
                p.drawText(logo_x - 147, logo_y + 70, 120, 18, Qt.AlignRight, f"({hdw}-{hdl})")
            rank, name = self.format_rank_name(self.state.home_rank, self.state.home_name)
            metrics_rank = QFontMetrics(self.rank_font)
            rank_w = metrics_rank.horizontalAdvance(rank) if rank else 0
            metrics_name = QFontMetrics(self.title_font)
            name_w = metrics_name.horizontalAdvance(name)
            name_x = right_x + right_w - name_w - 10
            p.setFont(self.title_font)
            p.setPen(Qt.white)
            p.drawText(name_x, 962, name_w, 26, Qt.AlignLeft | Qt.AlignVCenter, name)
            if rank:
                p.setFont(self.rank_font)
                p.setPen(Qt.white)
                metrics_rank = QFontMetrics(self.rank_font)
                rank_w = metrics_rank.horizontalAdvance(rank)
                rank_x = name_x - rank_w - 6
                p.drawText(rank_x, 962, rank_w, 26, Qt.AlignLeft | Qt.AlignVCenter, rank)
            p.setFont(self.score_font)
            p.setPen(Qt.white)
            p.drawText(right_x + 97, 970, 120, 70, Qt.AlignCenter, str(self.state.home_pts))
            self.draw_timeout_rects(p, right_x + 120, 1030, self.state.home_timeouts, align="left")
            p.setOpacity(1.0)
        if self.state.shome_box_active:  # make sure you have a progress flag
            progress = self.state.shome_box_progress  # 0.0 → 1.0
            full_width = dd_w
            center_x = dd_x + full_width // 2
            curr_w = int(full_width * progress)  # current animated width
            self.draw_fully_rounded_rect(p, center_x - curr_w // 2, 960, curr_w, 25, QColor("#1d1d1d"), radius=7)
            if self.state.possession == 'away':
                self.draw_glow_round_ddleft(p,dd_x,960,dd_w-22,25,self.state.away_color)
            if self.state.possession == 'home':
                self.draw_glow_round_ddright(p,dd_x+22, 960, dd_w-22, 25, self.state.home_color)
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
            dist     = str(self.state.distance).strip().lower()
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
            p.drawText(dd_x, 938, dd_w, 70, Qt.AlignCenter, dd_text)
            p.setFont(self.timer_font)
            p.setPen(Qt.white)
            tstring = f"{self.state.minutes}:{self.state.seconds:02d}"
            p.drawText(cx, cy+40, cw, 60, Qt.AlignCenter, tstring)
            p.setFont(self.period_font)
            p.drawText(cx - 57, cy + 57, cw, 26, Qt.AlignCenter, f"{self.period_text()}")
            if self.state.play_running:
                p.setFont(self.pc_font)
            if self.state.playclock <= 10:
                p.setPen(Qt.red)
            else:
                p.setPen(Qt.yellow)
            if self.show_playclock is True:
                rect = QRect(cx + 111, 1005, 100, 22)
                p.drawText(rect, Qt.AlignCenter, f":{self.state.playclock:02d}")
            p.setOpacity(1.0)
        # -- FLAG SECTION -- #
        if self.state.flag is True:
            self.draw_fully_rounded_rect(p,dd_x,960,dd_w,25,QColor("#ffd609"),radius=7)
            self.draw_fpanel_base(p,left_x - 4,965,right_w + 328,79,QColor("#ffd609"))
            tri_w = 18
            tri_h = 22
            center_x = left_x + (right_w + 318) // 2
            center_y = 935 + (79 // 2)
            self.draw_left_triangle(p,center_x - 45,center_y,tri_w,tri_h,QColor("#e6c400"))
            self.draw_right_triangle(p,center_x + 45,center_y,tri_w,tri_h,QColor("#e6c400"))
            p.setPen(Qt.white)
            p.setFont(self.dd_font)
            p.drawText(QRect(left_x, 935, right_w + 318, 79), Qt.AlignCenter |Qt.AlignHCenter, self.state.flag_text)      
    # -- POSSESSION SECTION -- #
        if self.state.possession == 'away':
            self.draw_possession_triangle(p, left_x+217, 971, self.state.away_color)
        elif self.state.possession == 'home':
            self.draw_possession_triangle(p, right_x+157, 971, self.state.home_color)
        if self.state.bottom_event_active:
            self.draw_semitransparent_rounded_rect(p, left_x+11, 1045, left_w+300, 20, QColor("#2a2a2a"))
        if self.state.bottom_event_active:
            self.draw_bottom_event_text(p, left_x+25, 1045, self.state.bottom_event_text_football) 
    def draw_home_touchdown(self, p):
        if self.state.home_touchdown_active:
            left_x = 20
            left_w = 270
            right_x = 275
            right_w = 270
            dd_w = 170
            dd_x = 195
            cx = 195
            cw = 190
            cy = 945
            progress = max(0.0, min(self.state.home_touchdown_progress, 1.0))
            full_width = dd_w + 500
            animated_width = int(full_width * progress)
            animated_x = right_x + right_w + 20 
            base_away = QColor(self.state.away_color)
            bg_away = QColor(self.state.away_color)
            base_away.setAlpha(120)
            bg_away.setAlpha(190)
            self.draw_round_left(p, left_x-4, 945, left_w+2, 80, QColor("#2a2a2a"))
            lower2 = QColor("#2a2a2a")
            lower = QColor("#2a2a2a")
            lower2.setAlpha(120)
            lower.setAlpha(210)
            hmdarker = self.state.home_color.darker(125)
            shadow_grad = QLinearGradient(right_x, 955, right_x, 60)
            shadow_grad.setColorAt(0.0, QColor(0, 0, 0, 110))
            shadow_grad.setColorAt(1.0, QColor(0, 0, 0, 0))
            p.setBrush(QBrush(shadow_grad))
            p.setPen(Qt.NoPen)
            p.drawRect(right_x, 955, right_w, 25)
            self.draw_round_right(p, right_x+2, 945, right_w+2, 80, QColor("#2a2a2a"))
            if self.state.possession == 'home':
                self.draw_glow_round_right(p, right_x-20, 945, right_w+23, 80, self.state.home_color)
            self.draw_base_bar(p, left_x, 965, left_w, 55)
            self.draw_pod(p, left_x, 965, left_w-160, 55, self.state.away_color)
            self.draw_hmbase_bar(p, right_x, 965, right_w, 55)
            self.draw_hmpod(p, right_x+160, 965, right_w-160, 55, self.state.home_color)
            self.draw_fully_rounded_rect(p, animated_x, 945, animated_width, 80, self.state.home_color, radius=10)
            self.draw_tdpanel_base(p, animated_x, 945, animated_width, 80, hmdarker)
            self.draw_fully_rounded_rect(p, dd_x, 940, dd_w, 25, QColor("#1d1d1d"), radius=7)
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
            down_raw=str(self.state.down).strip()
            dist=str(self.state.distance).strip().lower()
            if down_raw=="" and dist=="":
                dd_text=""
            elif down_raw=="":
                dd_text=dist
            elif "down" in dist:
                dd_text=f"{self.ordinal(int(down_raw))} {dist}"
            elif "final" in dist:
                dd_text=dist
            elif "halftime" in dist:
                dd_text=dist
            else:
                if dist=="":
                    dd_text=f"{self.ordinal(int(down_raw))}"
                else:
                    dd_text=f"{self.ordinal(int(down_raw))} & {dist}"
            p.drawText(dd_x,918,dd_w,70,Qt.AlignCenter,dd_text)
            p.setFont(self.timer_font)
            p.setPen(Qt.white)
            tstring=f"{self.state.minutes}:{self.state.seconds:02d}"
            p.drawText(cx,cy+20,cw,60,Qt.AlignCenter,tstring)
            p.setFont(self.period_font)
            p.setPen(Qt.white)
            p.drawText(cx-63,cy+37,cw,26,Qt.AlignCenter,f"{self.period_text()}")
            if self.state.play_running:
                p.setFont(self.pc_font)
            if self.state.playclock <= 10:
                p.setPen(Qt.red)
            else:
                p.setPen(Qt.yellow)
            if self.show_playclock is True:
                rect = QRect(cx + 100, cy+40, 100, 22)
                p.drawText(rect, Qt.AlignCenter, f":{self.state.playclock:02d}")
            rank,name=self.format_rank_name(self.state.home_rank,self.state.home_name)
            p.setFont(self.tdrank_font)
            metrics_rank=QFontMetrics(self.tdrank_font)
            rank_w=metrics_rank.horizontalAdvance(rank) if rank else 0
            rank_x=animated_x+265
            if rank:
                p.drawText(rank_x,945,rank_w,26,Qt.AlignLeft|Qt.AlignVCenter,rank)
            p.setFont(self.tdtitle_font)
            p.setPen(Qt.white)
            metrics_name=QFontMetrics(self.tdtitle_font)
            name_w=metrics_name.horizontalAdvance(name)
            name_x=rank_x+rank_w+6
            p.drawText(name_x,945,name_w,26,Qt.AlignLeft|Qt.AlignVCenter,name)
            mascot=self.state.home_mascot
            metrics_mascot=QFontMetrics(self.tdtitle_font)
            mascot_w=metrics_mascot.horizontalAdvance(mascot)
            mascot_x=name_x+name_w+10
            p.drawText(mascot_x,945,mascot_w,26,Qt.AlignLeft|Qt.AlignVCenter,mascot)
            p.setFont(self.monument_font)
            p.setPen(Qt.white)
            p.drawText(animated_x, 957, dd_w+500, 80, Qt.AlignCenter, self.state.touchdown_text)
            logo_x=left_x+5
            logo_y=948
            logo_w=80
            logo_h=85
            p.save()
            self.clip_to_rounded_rect(p,logo_x,965,logo_w,105)
            self.draw_logo_in_top_rounded_window(p,logo_x,logo_y,logo_w,logo_h,self.state.away_logo)
            p.restore()
            logo_x2=right_x+280
            logo_y2=948
            logo_w2=80
            logo_h2=85
            p.save()
            self.clip_to_rounded_rect(p,right_x,965,right_w,105)
            self.draw_logo_in_top_rounded_window(p,logo_x2,logo_y2,logo_w2,logo_h2,self.state.home_logo)
            p.restore()
            p.setFont(self.score_font)
            p.setPen(Qt.white)
            p.drawText(left_x+85,950,120,70,Qt.AlignCenter,str(self.state.away_pts))
            p.drawText(right_x+70,950,120,70,Qt.AlignCenter,str(self.state.home_pts))
            self.draw_timeout_rects(p,left_x+100,1010,self.state.away_timeouts)
            self.draw_timeout_rects(p,right_x+90,1010,self.state.home_timeouts,align="left")
            p.restore()
    def draw_away_touchdown(self, p):
        if self.state.away_touchdown_active:
            left_x = 1310
            left_w = 270
            right_x = 1575
            right_w = 270
            dd_w = 170
            dd_x = 1495
            cx = 1495
            cw = 190
            cy = 945
            progress = max(0.0, min(self.state.away_touchdown_progress, 1.0))
            full_width = dd_w + 500
            animated_width = int(full_width * progress)
            animated_x = (left_x - 20) - animated_width
            base_away = QColor(self.state.away_color)
            bg_away = QColor(self.state.away_color)
            base_away.setAlpha(120)
            bg_away.setAlpha(190)
            self.draw_round_left(p, left_x-4, 945, left_w+2, 80, QColor("#2a2a2a"))
            lower2 = QColor("#2a2a2a")
            lower = QColor("#2a2a2a")
            lower2.setAlpha(120)
            lower.setAlpha(210)
            shadow_grad = QLinearGradient(right_x, 955, right_x, 60)
            shadow_grad.setColorAt(0.0, QColor(0,0,0,110))
            shadow_grad.setColorAt(1.0, QColor(0,0,0,0))
            p.setBrush(QBrush(shadow_grad))
            p.setPen(Qt.NoPen)
            p.drawRect(right_x, 955, right_w, 25)
            self.draw_round_right(p, right_x+2, 945, right_w+2, 80, QColor("#2a2a2a"))
            if self.state.possession == 'away':
                self.draw_glow_round_left(p, left_x-3, 945, left_w+22, 80, self.state.away_color)
            self.draw_base_bar(p, left_x, 965, left_w, 55)
            self.draw_pod(p, left_x, 965, left_w-160, 55, self.state.away_color)
            self.draw_hmbase_bar(p, right_x, 965, right_w, 55)
            self.draw_hmpod(p, right_x+160, 965, right_w-160, 55, self.state.home_color)
            self.draw_fully_rounded_rect(p, animated_x, 945, animated_width, 80, self.state.away_color, radius=10)
            self.draw_tdpanel_base(p, animated_x, 945, animated_width, 80, self.state.away_color.darker(125))
            self.draw_fully_rounded_rect(p, dd_x, 940, dd_w, 25, QColor("#1d1d1d"), radius=7)
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
            p.drawText(dd_x, 918, dd_w, 70, Qt.AlignCenter, dd_text)
            p.setFont(self.timer_font)
            p.setPen(Qt.white)
            tstring = f"{self.state.minutes}:{self.state.seconds:02d}"
            p.drawText(cx, cy+20, cw, 60, Qt.AlignCenter, tstring)
            p.setFont(self.period_font)
            p.drawText(cx-63, cy+37, cw, 26, Qt.AlignCenter, f"{self.period_text()}")
            if self.state.play_running:
                p.setFont(self.pc_font)
            if self.state.playclock <= 10:
                p.setPen(Qt.red)
            else:
                p.setPen(Qt.yellow)
            if self.show_playclock is True:
                rect = QRect(cx + 100, cy+40, 100, 22)
                p.drawText(rect, Qt.AlignCenter, f":{self.state.playclock:02d}")
            rank, name = self.format_rank_name(self.state.away_rank, self.state.away_name)
            p.setFont(self.tdrank_font)
            p.setPen(Qt.white)
            metrics_rank = QFontMetrics(self.tdrank_font)
            rank_w = metrics_rank.horizontalAdvance(rank) if rank else 0
            rank_x = animated_x + 265
            if rank:
                p.drawText(rank_x, 945, rank_w, 26, Qt.AlignLeft | Qt.AlignVCenter, rank)
            p.setFont(self.tdtitle_font)
            p.setPen(Qt.white)
            metrics_name = QFontMetrics(self.tdtitle_font)
            name_w = metrics_name.horizontalAdvance(name)
            name_x = rank_x + rank_w + 6
            p.drawText(name_x, 945, name_w, 26, Qt.AlignLeft | Qt.AlignVCenter, name)
            mascot = self.state.away_mascot
            metrics_mascot = QFontMetrics(self.tdtitle_font)
            mascot_w = metrics_mascot.horizontalAdvance(mascot)
            mascot_x = name_x + name_w + 10
            p.drawText(mascot_x, 945, mascot_w, 26, Qt.AlignLeft | Qt.AlignVCenter, mascot)
            p.setFont(self.monument_font)
            p.setPen(Qt.white)
            p.drawText(animated_x, 957, dd_w+500, 80, Qt.AlignCenter, self.state.touchdown_text)
            logo_x = left_x + 5
            logo_y = 948
            logo_w = 80
            logo_h = 85
            p.save()
            self.clip_to_rounded_rect(p, logo_x, 965, logo_w, 105)
            self.draw_logo_in_top_rounded_window(p, logo_x, logo_y, logo_w, logo_h, self.state.away_logo)
            p.restore()
            logo_x2 = right_x + 280
            logo_y2 = 948
            logo_w2 = 80
            logo_h2 = 85
            p.save()
            self.clip_to_rounded_rect(p, right_x, 965, right_w, 105)
            self.draw_logo_in_top_rounded_window(p, logo_x2, logo_y2, logo_w2, logo_h2, self.state.home_logo)
            p.restore()
            p.setFont(self.score_font)
            p.setPen(Qt.white)
            p.drawText(left_x + 85, 950, 120, 70, Qt.AlignCenter, str(self.state.away_pts))
            p.drawText(right_x + 70, 950, 120, 70, Qt.AlignCenter, str(self.state.home_pts))
            self.draw_timeout_rects(p, left_x + 100, 1010, self.state.away_timeouts)
            self.draw_timeout_rects(p, right_x + 90, 1010, self.state.home_timeouts, align="left")
            p.restore()
    def draw_football_final(self, p):
        # -- KEY INFORMATUION (DO NOT CHANGE W/O PROPER TESTING) -- #
        left_x = 615
        left_w = 370
        cx = 866
        cw = 140
        cy = 985
        right_x = 935
        right_w = 370
        rw = self.state.away_record_wins
        rl = self.state.away_record_losses
        dw = self.state.away_district_wins
        dl = self.state.away_district_losses
        hw = self.state.home_record_wins
        hl = self.state.home_record_losses
        hdw = self.state.home_district_wins
        hdl = self.state.home_district_losses     
        if self.state.faway_box_active:
            p.setFont(self.record_font)
            p.setPen(Qt.white)
            progress=self.state.faway_box_progress
            full_width=left_w+330
            center_x=left_x-4+full_width//2
            curr_w=int(full_width*progress)
            self.draw_fully_rounded_rect(p,center_x-curr_w//2,965,curr_w,80,QColor("#2a2a2a"))
            bottom_w=697
            bottom_center=612+bottom_w//2
            curr_bottom=int(bottom_w*progress)
            self.draw_bottom_round_rect(p,bottom_center-curr_bottom//2,1035,curr_bottom,10,QColor("#5E5E5E"),10)
            curr_width = int(left_w * self.state.faway_box_progress)
            self.draw_base_bar(p, left_x + left_w - curr_width, 985, curr_width, 55)
            pod_full_width = left_w - 255
            pod_start_progress = 0.5  # start after base bar fully extended
            if progress >= pod_start_progress:
    # compute relative progress for pod (0 → 1)
                pod_progress = (progress - pod_start_progress) / (1.0 - pod_start_progress)
                curr_pod_width = int(pod_full_width * pod_progress)
                self.draw_pod(p, left_x + pod_full_width - curr_pod_width, 985, curr_pod_width, 55, self.state.away_color)

            logo_x = left_x + 5
            logo_y = 948
            logo_w = 80
            logo_h = 85
            p.save()
            self.clip_to_rounded_rect(p, left_x, 985, left_w - 5, 105)
            self.draw_logo_in_top_rounded_window(p, logo_x, logo_y, logo_w, logo_h, self.state.away_logo)
            p.restore()
            fade_delay = 0.7
            if progress <= fade_delay:
                opacity = 0.0
            else:
                opacity = (progress - fade_delay) / (1.0 - fade_delay)
            opacity = min(max(opacity, 0.0), 1.0)
            p.setOpacity(opacity)
            if not (rw == 0 and rl == 0):
                p.drawText(logo_x + 120, logo_y + 50, 120, 18, Qt.AlignLeft, f"{rw}-{rl}")
            if not (dw == 0 and dl == 0):
                p.drawText(logo_x + 113, logo_y + 70, 120, 18, Qt.AlignLeft, f"({dw}-{dl})")
            rank, name = self.format_rank_name(self.state.away_rank, self.state.away_name)
            metrics_rank = QFontMetrics(self.rank_font)
            rank_w = metrics_rank.horizontalAdvance(rank) if rank else 0
            rank_x = left_x + 10
            if rank:
                p.setFont(self.rank_font)
                p.setPen(Qt.white)
                p.drawText(rank_x, 962, rank_w, 26, Qt.AlignLeft | Qt.AlignVCenter, rank)
            metrics_name = QFontMetrics(self.title_font)
            name_w = metrics_name.horizontalAdvance(name)
            name_x = rank_x + rank_w + 6
            p.setFont(self.title_font)
            p.setPen(Qt.white)
            p.drawText(name_x, 962, name_w, 26, Qt.AlignLeft | Qt.AlignVCenter, name)
            p.setFont(self.score_font)
            p.setPen(Qt.white)
            p.drawText(left_x + 157 , 970, 120, 70, Qt.AlignCenter, str(self.state.away_pts))
            self.draw_timeout_rects(p, left_x + 180, 1030, self.state.away_timeouts)
            p.setOpacity(1.0)

        # -- HOME SECTION -- #
        if self.state.fhome_box_active:
            progress = self.state.fhome_box_progress
            curr_width = int(right_w * progress)
            self.draw_hmbase_bar(p, right_x, 985, curr_width, 55)
            pod_full_width = right_w - 255
            pod_start_progress = 0.5  # start after 50% of base bar animation
            if progress >= pod_start_progress:
                pod_progress = (progress - pod_start_progress) / (1.0 - pod_start_progress)
                curr_pod_width = int(pod_full_width * pod_progress)
                self.draw_hmpod(p, right_x + 255, 985, curr_pod_width, 55, self.state.home_color)
            logo_x2 = right_x + 280,
            logo_y2 = 955
            logo_w2 = 80
            logo_h2 = 85
            p.save()
            self.clip_to_rounded_rect(p, right_x, 985, right_w, 105)
            self.draw_logo_in_top_rounded_window(p, logo_x2, 955, logo_w2, logo_h2, self.state.home_logo)
            p.restore()
            fade_delay = 0.7
            if progress <= fade_delay:
                opacity = 0.0
            else:
                opacity = (progress - fade_delay) / (1.0 - fade_delay)
            opacity = min(max(opacity, 0.0), 1.0)
            p.setOpacity(opacity)
            if not (hw == 0 and hl == 0):
                p.drawText(logo_x2 - 154, logo_y2 + 50, 120, 18, Qt.AlignRight, f"{hw}-{hl}")
            if not (hdw == 0 and hdl == 0):
                p.drawText(logo_x2 - 147, logo_y2 + 70, 120, 18, Qt.AlignRight, f"({hdw}-{hdl})")
            rank, name = self.format_rank_name(self.state.home_rank, self.state.home_name)
            metrics_rank = QFontMetrics(self.rank_font)
            rank_w = metrics_rank.horizontalAdvance(rank) if rank else 0
            metrics_name = QFontMetrics(self.title_font)
            name_w = metrics_name.horizontalAdvance(name)
            name_x = right_x + right_w - name_w - 10
            p.setFont(self.title_font)
            p.setPen(Qt.white)
            p.drawText(name_x, 962, name_w, 26, Qt.AlignLeft | Qt.AlignVCenter, name)
            if rank:
                p.setFont(self.rank_font)
                p.setPen(Qt.white)
                metrics_rank = QFontMetrics(self.rank_font)
                rank_w = metrics_rank.horizontalAdvance(rank)
                rank_x = name_x - rank_w - 6
                p.drawText(rank_x, 962, rank_w, 26, Qt.AlignLeft | Qt.AlignVCenter, rank)
            p.setFont(self.score_font)
            p.setPen(Qt.white)
            p.drawText(right_x + 97, 970, 120, 70, Qt.AlignCenter, str(self.state.home_pts))
            self.draw_timeout_rects(p, right_x + 120, 1030, self.state.home_timeouts, align="left")
            p.setOpacity(1.0)
        if self.state.cfinal_box_active:
            progress=self.state.cfinal_box_progress
            curr_w=int(cw*progress)
            draw_x=cx+25+(cw-curr_w)//2
            self.draw_fully_rounded_rect(p,draw_x,cy-10,curr_w,55,QColor("#232323"),radius=8)
            fade_delay=0.7
            if progress<=fade_delay:
                opacity=0.0
            else:
                opacity=(progress-fade_delay)/(1.0-fade_delay)
            opacity=min(max(opacity,0.0),1.0)
            p.setOpacity(opacity)
            period=self.state.period
            if period<=4:
                self.state.final_text="FINAL"
            elif period==5:
                self.state.final_text="FINAL/OT"
            else:
                self.state.final_text=f"FINAL/{period-4} OT"
            p.setFont(self.final_font)
            p.setPen(Qt.white)
            p.drawText(cx+25,cy-5,cw,45,Qt.AlignCenter,self.state.final_text)
            p.setOpacity(1.0)
        if self.state.bottom_event_active:
            self.draw_semitransparent_rounded_rect(p, left_x+11, 1045, left_w+300, 20, QColor("#2a2a2a"))
        if self.state.bottom_event_active:
            self.draw_bottom_event_text(p, left_x+25, 1045, self.state.bottom_event_text_football)
        p.end()
    def draw_left_triangle(self, p: QPainter, x, y, w, h, color: QColor):
        path = QPainterPath()
        path.moveTo(x - w / 3, y)          # tip (left)
        path.lineTo(x + w / 3, y - h / 3)  # top-right
        path.lineTo(x + w / 3, y + h / 3)  # bottom-right
        path.closeSubpath()
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(color))
        p.drawPath(path)
    def draw_right_triangle(self, p: QPainter, x, y, w, h, color: QColor):
        path = QPainterPath()
        path.moveTo(x + w / 3, y)          # tip (right)
        path.lineTo(x - w / 3, y - h / 3)  # top-left
        path.lineTo(x - w / 3, y + h / 3)  # bottom-left
        path.closeSubpath()
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(color))
        p.drawPath(path)
    def draw_transparent_to_black_rect(self, p: QPainter, x, y, w, h, radius: int = 12):
        grad = QLinearGradient(x, y, x + w, y + h)
        grad.setColorAt(0.0, QColor(0, 0, 0, 0))   # alpha = 0
        grad.setColorAt(0.5, QColor(0, 0, 0, 200))
        grad.setColorAt(1.0, QColor(0, 0, 0, 255))
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(grad))
        p.drawRoundedRect(QRect(int(x), int(y), int(w), int(h)), radius, radius)
    def draw_fully_gradient_rect(self, p: QPainter, x, y, w, h, color: QColor, radius: int = 12):
        darker = color.darker(225)   # 175 = 75% darker; adjust if needed
        sdarker = color.darker(125) 
        grad = QLinearGradient(x, y, x + w, y)
        grad.setColorAt(0.0, color)
        grad.setColorAt(0.5, darker)
        grad.setColorAt(1.0, darker)
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(grad))
        p.drawRoundedRect(QRect(int(x), int(y), int(w), int(h)), radius, radius)
    def draw_panel_base(self, p, x, y, w, h, color: QColor, thickness: int =5):
        radius = 10
        pen = QPen(color)
        pen.setWidth(thickness)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(x, y, w, h, radius , radius)
    def draw_ppanel_base(self, p, x, y, w, h, color: QColor, thickness: int =3):
        radius = 10
        pen = QPen(color)
        pen.setWidth(thickness)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(x, y, w, h, radius , radius)
    def draw_fpanel_base(self, p, x, y, w, h, color: QColor, thickness: int =2):
        radius = 10
        pen = QPen(color)
        pen.setWidth(thickness)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(x, y, w, h, radius , radius)
    def draw_tdpanel_base(self, p, x, y, w, h, color: QColor, thickness: int = 4):
        radius = 10
        pen = QPen(color)
        pen.setWidth(thickness)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(x, y, w, h, radius, radius)
        shadow_color = QColor(color)
        shadow_color.setAlpha(150)  # adjust transparency
        p.setPen(Qt.NoPen)
        p.setBrush(shadow_color)
        for i in range(20):  # number of layers
            inset = i + 1
            p.drawRoundedRect(x + inset, y + inset, w - 2*inset, h - 2*inset, radius - inset, radius - inset)  
    def draw_away_notch(self, p: QPainter, x, y, w, h, color: QColor):
        offset = h * 0.25
        p.setPen(Qt.NoPen)
        p.setBrush(color)
        path = QPainterPath()
        path.moveTo(x, y)
        path.lineTo(x + w, y + offset)
        path.lineTo(x + w, y + h - offset )
        path.lineTo(x, y + h)
        path.closeSubpath
        p.drawPath(path)
    def draw_home_notch(self, p: QPainter, x, y, w, h, color: QColor):
        offset = h * 0.25
        p.save()
        p.setPen(Qt.NoPen)
        p.setBrush(color)
        path = QPainterPath()
        path.moveTo(x + w, y)                 # top-right
        path.lineTo(x, y + offset)            # top-left inward
        path.lineTo(x, y + h - offset)        # bottom-left inward
        path.lineTo(x + w, y + h)             # bottom-right
        path.closeSubpath()
        p.drawPath(path)
        p.restore()
    def draw_bottom_event_text(self, p: QPainter, x: int, y: int, text: str):
        if not text:
            return
        w = 640
        h= 22
        p.setFont(self.event_font)
        p.setPen(Qt.white)
        p.drawText(QRect(x, y, w, h), Qt.AlignCenter, text)
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
    def draw_panel_glow(self, p, x, y, w, h, color: QColor):
        radius = 10
        glow_rect = QRectF(x+2, y+2, w-4, h-4)
        base = QColor(color)
        color_outer_rim = QColor(color).darker(100)
        color_inner_fill = QColor(color).lighter(150)
        rim_grad = QLinearGradient(glow_rect.left(), glow_rect.center().y(),glow_rect.right(), glow_rect.center().y())
        rim_grad.setColorAt(0.00, color_outer_rim)
        rim_grad.setColorAt(0.12, color_outer_rim)
        rim_grad.setColorAt(0.20, color_outer_rim)
        rim_grad.setColorAt(0.80, color_outer_rim)
        rim_grad.setColorAt(0.88, color_outer_rim)
        rim_grad.setColorAt(1.00, color_outer_rim)
        p.setPen(Qt.NoPen)
        p.setBrush(rim_grad)
        p.drawRoundedRect(glow_rect, radius, radius)
        fill_grad = QLinearGradient(glow_rect.left(), glow_rect.center().y(),glow_rect.right(), glow_rect.center().y())
        fill_grad.setColorAt(0.00, color_outer_rim)
        fill_grad.setColorAt(0.15, color_outer_rim)
        fill_grad.setColorAt(0.50, color_inner_fill)
        fill_grad.setColorAt(0.85, color_inner_fill)
        fill_grad.setColorAt(1.00, color_inner_fill)
        p.setBrush(fill_grad)
        p.drawRoundedRect(glow_rect, radius, radius)
        white_strong = QColor(255, 255, 255, 160)
        white_soft   = QColor(255, 255, 255, 60)
        bloom = QLinearGradient(glow_rect.center().x(), glow_rect.bottom(), glow_rect.center().x(), glow_rect.top())
        bloom.setColorAt(0.00, color_outer_rim)  # base edge
        bloom.setColorAt(0.20, color_outer_rim)    # fade
        bloom.setColorAt(0.45, Qt.transparent)  # vanish
        p.setBrush(bloom)
        p.drawRoundedRect(glow_rect, radius, radius)
    def format_rank_name(self, rank, name):
        try:
            r = int(rank)
        except:
            r = 0
        name = name.upper()
        if r <= 0:
            return "", name
        return str(r), name
    def draw_top_gloss(self, p: QPainter, x, y, w, h):
        gloss_h = int(h * 0.35)
        gloss_y = int(y + h * 0.12)
        grad = QLinearGradient(x, gloss_y, x + w, gloss_y)
        grad.setColorAt(0.00, QColor(255, 255, 255, 0))
        grad.setColorAt(0.20, QColor(255, 255, 255, 50))
        grad.setColorAt(0.50, QColor(255, 255, 255, 70))  # brightest middle
        grad.setColorAt(0.80, QColor(255, 255, 255, 50))
        grad.setColorAt(1.00, QColor(255, 255, 255, 0))
        p.save()
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(grad))
        p.drawRect(int(x), gloss_y, int(w), gloss_h)
        p.restore()
    def draw_horizontal_glow(p, x, y, w, h, color: QColor):
        grad = QLinearGradient(x, y, x + w, y)
        c0 = QColor(color)
        c0.setAlpha(0)
        c1 = QColor(color)
        c1.setAlpha(160)
        c2 = QColor(color)
        c2.setAlpha(0)
        grad.setColorAt(0.0, c0)
        grad.setColorAt(0.50, c1)
        grad.setColorAt(1.0, c2)
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(grad))
        p.drawRoundedRect(x, y, w, h, h/2, h/2)
    def draw_round_left(self, p: QPainter, x, y, w, h, color: QColor, r=10):
        p.setPen(Qt.NoPen)
        p.setBrush(color)
        path = QPainterPath()
        path.moveTo(x + r, y)
        path.lineTo(x + w, y)
        path.lineTo(x + w, y + h)
        path.lineTo(x + r, y + h)
        path.quadTo(x, y + h, x, y + h - r)
        path.lineTo(x, y + r)
        path.quadTo(x, y, x + r, y)
        p.drawPath(path)
    def draw_rounded_rect(self, p: QPainter, x, y, w, h, color: QColor):
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(color))
        radius = 12
        path = QPainterPath()
        path.moveTo(x, y)
        path.lineTo(x + w, y)
        path.lineTo(x + w, y + h - radius)
        path.quadTo(x + w, y + h, x + w - radius, y + h)
        path.lineTo(x + radius, y + h)
        path.quadTo(x, y + h, x, y + h - radius)
        path.lineTo(x, y)
        p.drawPath(path)
    def draw_introround_left(self, p: QPainter, x, y, w, h, color: QColor, r=10):
        path = QPainterPath()
        path.moveTo(x + r, y)
        path.lineTo(x + w, y)
        path.lineTo(x + w, y + h)
        path.lineTo(x + r, y + h)
        path.quadTo(x, y + h, x, y + h - r)
        path.lineTo(x, y + r)
        path.quadTo(x, y, x + r, y)
        p.save()
        p.setPen(Qt.NoPen)
        grad = QLinearGradient(x, y, x + w, y)
        darker = color.darker(150)
        darke = color.darker(175)
        sdarker = color.darker(200)
        dark = color.darker(225)
        darkest = color.darker(250)
        grad.setColorAt(0.0, darker)      # left team color
        grad.setColorAt(0.2, darke)
        grad.setColorAt(0.4, sdarker)     # darker
        grad.setColorAt(0.4, dark)
        grad.setColorAt(0.6, darkest)
        grad.setColorAt(0.8, QColor(0,0,0))    # very dark
        grad.setColorAt(1.0, QColor(0,0,0))  # black
        p.setBrush(QBrush(grad))
        p.drawPath(path)
        p.restore()
    def draw_semitransparent_rounded_rect(self, p: QPainter, x, y, w, h, color: QColor):
        c = QColor(color)
        c.setAlpha(225)
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(c))
        radius = 12
        path = QPainterPath()
        path.moveTo(x, y)
        path.lineTo(x + w, y)
        path.lineTo(x + w, y + h - radius)
        path.quadTo(x + w, y + h, x + w - radius, y + h)
        path.lineTo(x + radius, y + h)
        path.quadTo(x, y + h, x, y + h - radius)
        path.lineTo(x, y)
        p.drawPath(path)
    def draw_round_right(self, p: QPainter, x, y, w, h, color: QColor, r=10):
        p.setPen(Qt.NoPen)
        p.setBrush(color)
        path = QPainterPath()
        path.moveTo(x, y)
        path.lineTo(x + w - r, y)
        path.quadTo(x + w, y, x + w, y + r)
        path.lineTo(x + w, y + h - r)
        path.quadTo(x + w, y + h, x + w - r, y + h)
        path.lineTo(x, y + h)
        path.lineTo(x, y)
        p.drawPath(path)
    def draw_introround_right(self, p: QPainter, x, y, w, h, color: QColor, r=10):
        path = QPainterPath()
        path.moveTo(x, y)
        path.lineTo(x + w - r, y)
        path.quadTo(x + w, y, x + w, y + r)
        path.lineTo(x + w, y + h - r)
        path.quadTo(x + w, y + h, x + w - r, y + h)
        path.lineTo(x, y + h)
        path.lineTo(x, y)
        p.save()
        p.setPen(Qt.NoPen)
        darker = color.darker(150)
        darke = color.darker(175)
        sdarker = color.darker(200)
        dark = color.darker(225)
        darkest = color.darker(250)
        grad = QLinearGradient(x + w, y, x, y)
        grad.setColorAt(0.0, darker)      # left team color
        grad.setColorAt(0.2, darke)
        grad.setColorAt(0.4, sdarker)     # darker
        grad.setColorAt(0.4, dark)
        grad.setColorAt(0.6, darkest)
        grad.setColorAt(0.8, QColor(0,0,0))    # very dark
        grad.setColorAt(1.0, QColor(0,0,0))  # black
        p.setBrush(QBrush(grad))
        p.drawPath(path)
        p.restore()
    def draw_bottom_round_rect(self, p: QPainter, x, y, w, h, color: QColor, radius=12):
        p.setPen(Qt.NoPen)
        p.setBrush(color)
        path = QPainterPath()
        path.moveTo(x, y)
        path.lineTo(x + w, y)
        path.lineTo(x + w, y + h - radius)
        path.quadTo(x + w, y + h,x + w - radius, y + h)
        path.lineTo(x + radius, y + h)
        path.quadTo(x, y + h,x, y + h - radius)
        path.lineTo(x, y)
        p.drawPath(path)
    def draw_glow_top_round(self, p: QPainter, x, y, w, h, color: QColor, thickness=2):
        r = 10
        glow_radius = 18
        img = QImage(w, h, QImage.Format_ARGB32_Premultiplied)
        img.fill(Qt.transparent)
        offp = QPainter(img)
        offp.setRenderHint(QPainter.Antialiasing, True)
        grad = QRadialGradient(w/2, h/2, max(w, h) * 0.75)
        c1 = QColor(color)
        c1.setAlpha(160)
        c2 = QColor(color)
        c2.setAlpha(0)
        grad.setColorAt(0.00, c1)
        grad.setColorAt(0.45, c1)
        grad.setColorAt(1.00, c2)
        offp.setPen(Qt.NoPen)
        offp.setBrush(grad)
        path = QPainterPath()
        path.moveTo(r, 0)
        path.quadTo(0, 0, 0, r)
        path.lineTo(0, h)
        path.lineTo(w, h)
        path.lineTo(w, r)
        path.quadTo(w, 0, w - r, 0)
        path.lineTo(r, 0)
        offp.drawPath(path)
        offp.end()
        blurred = QImage(w, h, QImage.Format_ARGB32_Premultiplied)
        blurred.fill(Qt.transparent)
        scene = QGraphicsScene()
        item = scene.addPixmap(QPixmap.fromImage(img))
        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(glow_radius)
        item.setGraphicsEffect(blur)
        rp = QPainter(blurred)
        scene.render(rp)
        rp.end()
        p.drawImage(x, y, blurred)
        p.setRenderHint(QPainter.Antialiasing, True)
        pen = QPen(color, thickness)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        outline = QPainterPath()
        outline.moveTo(x + r, y)
        outline.quadTo(x, y, x, y + r)
        outline.lineTo(x, y + h)
        outline.lineTo(x + w, y + h)
        outline.lineTo(x + w, y + r)
        outline.quadTo(x + w, y, x + w - r, y)
        outline.lineTo(x + r, y)
        p.drawPath(outline)
    def draw_glow_round_left(self, p: QPainter, x, y, w, h, color: QColor, thickness=2):
        r = 10
        glow_radius = 18
        img = QImage(w, h, QImage.Format_ARGB32_Premultiplied)
        img.fill(Qt.transparent)
        offp = QPainter(img)
        offp.setRenderHint(QPainter.Antialiasing, True)
        grad = QRadialGradient(w/2, h/2, max(w, h) * 0.75)
        c1 = QColor(color)
        c1.setAlpha(160)
        c2 = QColor(color)
        c2.setAlpha(0)
        grad.setColorAt(0.00, c1)
        grad.setColorAt(0.45, c1)
        grad.setColorAt(1.00, c2)
        offp.setPen(Qt.NoPen)
        offp.setBrush(grad)
        path = QPainterPath()
        path.moveTo(r, 0)
        path.quadTo(0, 0, 0, r)
        path.lineTo(0, h - r)
        path.quadTo(0, h, r, h)
        path.lineTo(w, h)         # bottom to right (open)
        path.lineTo(w, 0)         # right side (open)
        path.lineTo(r, 0)
        offp.drawPath(path)
        offp.end()
        blurred = QImage(w, h, QImage.Format_ARGB32_Premultiplied)
        blurred.fill(Qt.transparent)
        scene = QGraphicsScene()
        item = scene.addPixmap(QPixmap.fromImage(img))
        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(glow_radius)
        item.setGraphicsEffect(blur)
        rp = QPainter(blurred)
        scene.render(rp)
        rp.end()
        p.drawImage(x, y, blurred)
        p.setRenderHint(QPainter.Antialiasing, True)
        pen = QPen(color, thickness)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        outline = QPainterPath()
        outline.moveTo(x + r, y)
        outline.quadTo(x, y, x, y + r)
        outline.lineTo(x, y + h - r)
        outline.quadTo(x, y + h, x + r, y + h)
        outline.lineTo(x + w, y + h)
        outline.moveTo(x + w, y)
        outline.lineTo(x + r, y)
        p.drawPath(outline)
    def draw_glow_round_ddleft(self, p: QPainter, x, y, w, h, color: QColor, thickness=2):
        r = 10
        glow_radius = 18
        top_inset = 125   # <-- adjustable top inset
        img = QImage(w, h, QImage.Format_ARGB32_Premultiplied)
        img.fill(Qt.transparent)
        offp = QPainter(img)
        offp.setRenderHint(QPainter.Antialiasing, True)
        grad = QLinearGradient(0, h/2, w*0.5, h/2)
        c1 = QColor(color)
        c1.setAlpha(200)
        c2 = QColor(color)
        c2.setAlpha(0)
        grad.setColorAt(0.0, c1)
        grad.setColorAt(1.0, c2)
        offp.setPen(Qt.NoPen)
        offp.setBrush(grad)
        path = QPainterPath()
        path.moveTo(r, 0)
        path.quadTo(0, 0, 0, r)
        path.lineTo(0, h - r)
        path.quadTo(0, h, r, h)
        path.lineTo(w, h)
        path.lineTo(w, 0)
        path.closeSubpath()
        offp.drawPath(path)
        offp.end()
        blurred = QImage(w, h, QImage.Format_ARGB32_Premultiplied)
        blurred.fill(Qt.transparent)
        scene = QGraphicsScene()
        item = scene.addPixmap(QPixmap.fromImage(img))
        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(glow_radius)
        item.setGraphicsEffect(blur)
        rp = QPainter(blurred)
        scene.render(rp)
        rp.end()
        p.drawImage(x, y, blurred)
        p.setRenderHint(QPainter.Antialiasing, True)
        pen = QPen(color, thickness)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        outline = QPainterPath()
        outline.moveTo(x + w, y + h)
        outline.lineTo(x + r, y + h)
        outline.quadTo(x, y + h, x, y + h - r)
        outline.lineTo(x, y + r)
        outline.quadTo(x, y, x + r, y)
        outline.lineTo(x + top_inset, y)
        p.drawPath(outline)
    def draw_glow_round_ddright(self, p: QPainter, x, y, w, h, color: QColor, thickness=1):
        r = 10
        glow_radius = 18
        top_inset = 25   # <-- adjustable top indent
        img = QImage(w, h, QImage.Format_ARGB32_Premultiplied)
        img.fill(Qt.transparent)
        offp = QPainter(img)
        offp.setRenderHint(QPainter.Antialiasing, True)
        grad = QLinearGradient(w, h/2, w*0.5, h/2)
        c1 = QColor(color)
        c1.setAlpha(200)  # strong inside
        c2 = QColor(color)
        c2.setAlpha(0)    # fade inside
        grad.setColorAt(0.00, c1)
        grad.setColorAt(1.00, c2)
        offp.setPen(Qt.NoPen)
        offp.setBrush(grad)
        path = QPainterPath()
        path.moveTo(0, 0)
        path.lineTo(w - r, 0)
        path.quadTo(w, 0, w, r)
        path.lineTo(w, h - r)
        path.quadTo(w, h, w - r, h)
        path.lineTo(0, h)
        path.closeSubpath()
        offp.drawPath(path)
        offp.end()
        blurred = QImage(w, h, QImage.Format_ARGB32_Premultiplied)
        blurred.fill(Qt.transparent)
        scene = QGraphicsScene()
        item = scene.addPixmap(QPixmap.fromImage(img))
        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(glow_radius)
        item.setGraphicsEffect(blur)
        rp = QPainter(blurred)
        scene.render(rp)
        rp.end()
        p.drawImage(x, y, blurred)
        p.setRenderHint(QPainter.Antialiasing, True)
        pen = QPen(color, thickness)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        outline = QPainterPath()
        outline.moveTo(x, y + h)
        outline.lineTo(x + w - r, y + h)
        outline.quadTo(x + w, y + h, x + w, y + h - r)
        outline.lineTo(x + w, y + r)
        outline.quadTo(x + w, y, x + w - r, y)
        outline.lineTo(x + top_inset, y)
        p.drawPath(outline)
    def draw_glow_round_right(self, p: QPainter, x, y, w, h, color: QColor, thickness=2):
        r = 10
        glow_radius = 18
        img = QImage(w, h, QImage.Format_ARGB32_Premultiplied)
        img.fill(Qt.transparent)
        offp = QPainter(img)
        offp.setRenderHint(QPainter.Antialiasing, True)
        grad = QRadialGradient(w/2, h/2, max(w, h) * 0.75)
        c1 = QColor(color)
        c1.setAlpha(160)
        c2 = QColor(color)
        c2.setAlpha(0)
        grad.setColorAt(0.00, c1)
        grad.setColorAt(0.45, c1)
        grad.setColorAt(1.00, c2)
        offp.setPen(Qt.NoPen)
        offp.setBrush(grad)
        path = QPainterPath()
        path.moveTo(0, 0)
        path.lineTo(w - r, 0)
        path.quadTo(w, 0, w, r)
        path.lineTo(w, h - r)
        path.quadTo(w, h, w - r, h)
        path.lineTo(0, h)
        offp.drawPath(path)
        offp.end()
        blurred = QImage(w, h, QImage.Format_ARGB32_Premultiplied)
        blurred.fill(Qt.transparent)
        scene = QGraphicsScene()
        item = scene.addPixmap(QPixmap.fromImage(img))
        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(glow_radius)
        item.setGraphicsEffect(blur)
        rp = QPainter(blurred)
        scene.render(rp)
        rp.end()
        p.drawImage(x, y, blurred)
        p.setRenderHint(QPainter.Antialiasing, True)
        pen = QPen(color, thickness)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        outline = QPainterPath()
        outline.moveTo(x, y)
        outline.lineTo(x + w - r, y)
        outline.quadTo(x + w, y, x + w, y + r)
        outline.lineTo(x + w, y + h - r)
        outline.quadTo(x + w, y + h, x + w - r, y + h)
        outline.lineTo(x, y + h)
        p.drawPath(outline)
    def draw_base_bar(self, p: QPainter, x, y, w, h):
        radius = 10
        path = QPainterPath()
        path.moveTo(x + radius, y)
        path.lineTo(x + w, y)
        path.lineTo(x + w, y + h)
        path.lineTo(x + radius, y + h)
        path.quadTo(x, y + h, x, y + h - radius)
        path.lineTo(x, y + radius)
        path.quadTo(x, y, x + radius, y)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(25, 25, 25))
        p.drawPath(path)
    def draw_hmbase_bar(self, p: QPainter, x, y, w, h):
        radius = 10
        path = QPainterPath()
        path.moveTo(x, y)
        path.lineTo(x + w - radius, y)
        path.quadTo(x + w, y, x + w, y + radius)
        path.lineTo(x + w, y + h - radius)
        path.quadTo(x + w, y + h, x + w - radius, y + h)
        path.lineTo(x, y + h)
        path.lineTo(x, y)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(25, 25, 25))
        p.drawPath(path)
    def draw_pod(self, p: QPainter, x, y, pod_w, h, base_color: QColor):
        left_r = 10     # left side radius
        right_r = 62    # bottom-right radius
        path = QPainterPath()
        path.moveTo(x + left_r, y)
        path.lineTo(x + pod_w, y)    # FLAT TOP RIGHT
        path.lineTo(x + pod_w, y + h - right_r)
        path.quadTo(x + pod_w, y + h, x + pod_w - right_r, y + h)
        path.lineTo(x + left_r, y + h)
        path.quadTo(x, y + h, x, y + h - left_r)
        path.lineTo(x, y + left_r)
        path.quadTo(x, y, x + left_r, y)
        path.closeSubpath()
        cx = x + pod_w * 0.45
        cy = y + h * 0.20
        rad = pod_w * 1.2
        glow = QRadialGradient(cx, cy, rad)
        glow.setColorAt(0.00, base_color)
        glow.setColorAt(0.30, base_color)
        glow.setColorAt(0.60, base_color)
        glow.setColorAt(0.85, base_color.lighter(160))
        glow.setColorAt(1.00, QColor(25, 25, 25))
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(glow))
        p.drawPath(path)
        fade = QLinearGradient(x, y, x + pod_w, y)
        fade.setColorAt(0.0, QColor(0, 0, 0, 0))
        fade.setColorAt(1.0, QColor(0, 0, 0, 60))
        p.setBrush(QBrush(fade))
        p.drawPath(path)
    def draw_hmpod(self, p: QPainter, x, y, pod_w, h, base_color: QColor):
        left_r  = 62     # bottom-left radius
        right_r = 10     # top-right and bottom-right radius
        path = QPainterPath()
        path.moveTo(x, y)
        path.lineTo(x + pod_w - right_r, y)
        path.quadTo(x + pod_w, y, x + pod_w, y + right_r)
        path.lineTo(x + pod_w, y + h - right_r)
        path.quadTo(x + pod_w, y + h, x + pod_w - right_r, y + h)
        path.lineTo(x + left_r, y + h)
        path.quadTo(x, y + h, x, y + h - left_r)
        path.lineTo(x, y)
        path.closeSubpath()
        cx = x + pod_w * 0.45
        cy = y + h * 0.20
        rad = pod_w * 1.2
        glow = QRadialGradient(cx, cy, rad)
        glow.setColorAt(0.00, base_color)
        glow.setColorAt(0.30, base_color)
        glow.setColorAt(0.60, base_color)
        glow.setColorAt(0.85, base_color.lighter(160))
        glow.setColorAt(1.00, QColor(25, 25, 25))
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(glow))
        p.drawPath(path)
    def draw_inner_edge_glow(self, p: QPainter, x, y, w, h, color: QColor):
        img = QImage(w, h, QImage.Format_ARGB32_Premultiplied)
        img.fill(Qt.transparent)
        off = QPainter(img)
        off.setRenderHint(QPainter.Antialiasing, True)
        r = h * 0.22  # same rounding as panel
        path = QPainterPath()
        path.addRoundedRect(0, 0, w, h, r, r)
        off.setClipPath(path)
        grad = QLinearGradient(0, 0, w, 0)
        grad.setColorAt(0.00, color)                 # leading edge = strong team color
        grad.setColorAt(0.28, QColor(255,255,255))   # hotspot inside
        grad.setColorAt(0.55, QColor(255,255,255,0)) # fade toward interior
        grad.setColorAt(1.00, QColor(0,0,0,0))       # vanish fully
        off.setPen(Qt.NoPen)
        off.setBrush(grad)
        strip_h = int(h * 0.45)  # thickness of glow zone
        off.drawRect(0, (h-strip_h)//2, w, strip_h)
        off.end()
        blurred = QImage(w, h, QImage.Format_ARGB32_Premultiplied)
        blurred.fill(Qt.transparent)
        scene = QGraphicsScene()
        item = scene.addPixmap(QPixmap.fromImage(img))
        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(10)   # <- small blur keeps glow inside borders
        item.setGraphicsEffect(blur)
        rp = QPainter(blurred)
        scene.render(rp)
        rp.end()
        p.drawImage(x, y, blurred)
    def draw_timeout_rects(self, p: QPainter, x, y, remaining, max_count=3, align="right"):
        w = 21
        h = 3
        spacing = 7
        radius = 1
        remaining = max(0, min(max_count, int(remaining)))
        p.setPen(Qt.NoPen)
        if align == "left":
            for i in range(max_count):
                rect_x = x + i * (w + spacing)
                filled = (i < remaining)                      # <-- FIX
                p.setBrush(QColor("white") if filled else QColor(255,255,255,60))
                p.drawRoundedRect(QRect(int(rect_x), int(y), int(w), int(h)), radius, radius)
        if align == "right":
            total_w = max_count * w + (max_count - 1) * spacing
            for i in range(max_count):
                rect_x = x + i * (w + spacing)
                idx_from_right = max_count - 1 - i
                filled = (idx_from_right < remaining)
                p.setBrush(QColor("white") if filled else QColor(255,255,255,60))
                p.drawRoundedRect(QRect(int(rect_x), int(y), int(w), int(h)), radius, radius)
    def draw_top_flat_rect(self, p: QPainter, x, y, w, h, color: QColor, radius: int = 12):
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(color))
        path = QPainterPath()
        path.moveTo(x, y)
        path.lineTo(x + w, y)
        path.lineTo(x + w, y + h - radius)
        path.quadTo(x + w, y + h, x + w - radius, y + h)
        path.lineTo(x + radius, y + h)
        path.quadTo(x, y + h, x, y + h - radius)
        path.lineTo(x, y)
        p.drawPath(path)
    def draw_fully_grounded_rect(self, p: QPainter, x, y, w, h, radius: int = 12):
        grad = QLinearGradient(x, y, x + w, y)
        grad.setColorAt(0.0, QColor(0, 0, 0))
        grad.setColorAt(0.5, QColor(128, 128, 128))
        grad.setColorAt(1.0, QColor(0, 0, 0))
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(grad))
        p.drawRoundedRect(QRect(int(x), int(y), int(w), int(h)), radius, radius)
    def draw_fully_rounded_rect(self, p: QPainter, x, y, w, h, color: QColor, radius: int = 12):
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(color))
        p.drawRoundedRect(QRect(int(x), int(y), int(w), int(h)), radius, radius)
    def draw_bottom1_rounded_rect(self, p: QPainter, x, y, w, h, color: QColor, radius: int = 7):
        path = QPainterPath()
        path.moveTo(x, y)                 # top-left (flat)
        path.lineTo(x + w, y)             # top-right (flat)
        path.lineTo(x + w, y + h - radius)
        path.quadTo(x + w, y + h, x + w - radius, y + h)
        path.lineTo(x + radius, y + h)
        path.quadTo(x, y + h, x, y + h - radius)
        path.lineTo(x, y)

        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(color))
        p.drawPath(path)
    def draw_bottom2_rounded_rect(self,p:QPainter,x,y,w,h,color:QColor,radius:int=7):
        path=QPainterPath()
        path.moveTo(x+radius,y)
        path.lineTo(x+w-radius,y)
        path.quadTo(x+w,y,x+w,y+radius)
        path.lineTo(x+w,y+h)
        path.lineTo(x,y+h)
        path.lineTo(x,y+radius)
        path.quadTo(x,y,x+radius,y)
        path.closeSubpath()
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(color))
        p.drawPath(path)
    def draw_ffully_rounded_rect(self, p: QPainter, x, y, w, h, radius: int = 10):
        p.save()
        p.setPen(Qt.NoPen)
        grad = QLinearGradient(x, y, x, y + h)
        grad.setColorAt(0.0, QColor(200, 200, 200))
        grad.setColorAt(0.2, QColor(40, 40, 40))
        grad.setColorAt(0.4, QColor(40, 40, 40))
        grad.setColorAt(0.5, QColor(40, 40, 40))
        grad.setColorAt(0.6, QColor(40, 40, 40))
        grad.setColorAt(0.8, QColor(40, 40, 40))
        grad.setColorAt(1.0, QColor(200, 200, 200))
        p.setBrush(QBrush(grad))
        p.drawRoundedRect(QRect(int(x), int(y), int(w), int(h)), radius, radius)
        p.restore()
    def draw_top_rounded_rect(self, p: QPainter, x, y, w, h, color: QColor, radius: int = 12):
        p.setPen(Qt.NoPen)
        p.setBrush(color)
        path = QPainterPath()
        path.moveTo(x + radius, y)
        path.lineTo(x + w - radius, y)
        path.quadTo(x + w, y, x + w, y + radius)
        path.lineTo(x + w, y + h)
        path.lineTo(x, y + h)
        path.lineTo(x, y + radius)
        path.quadTo(x, y, x + radius, y)
        path.closeSubpath()
        p.drawPath(path)
    def draw_rect_shadow(self, p, x, y, w, h, color):
        shadow_color = QColor(255,255,255,140)
        for i in range(6):
            shadow_color.setAlpha(80 - i*12)
            p.setBrush(shadow_color)
            p.drawRect(int(x + 4 + i), int(y + 4 + i), int(w - 2*i), int(h - 2*i))
        p.setBrush(color)
        p.drawRect(int(x), int(y), int(w), int(h))
    def draw_possession_triangle(self, p: QPainter, x, y, color: QColor):
        tri = QPolygonF([QPointF(x - 26, y - 6),QPointF(x + 26, y - 6),QPointF(x,      y + 3),])
        size = 100
        half = size / 2
        img = QImage(size, size, QImage.Format_ARGB32_Premultiplied)
        img.fill(Qt.transparent)
        offp = QPainter(img)
        offp.setRenderHint(QPainter.Antialiasing, True)
        path = QPainterPath()
        path.addPolygon(tri.translated(-x + half, -y + half))
        offp.setClipPath(path)
        grad = QRadialGradient(half, half + 10,size * 0.50)
        grad.setColorAt(0.00, QColor(255,255,255,0))
        grad.setColorAt(0.50, QColor(255,255,255,0))
        grad.setColorAt(0.70, QColor(255,255,255,0))
        grad.setColorAt(1.00, QColor(255,255,255,0))
        offp.setPen(Qt.NoPen)
        offp.setBrush(grad)
        offp.drawRect(0, 0, size, size)
        offp.end()
        blurred = QImage(size, size, QImage.Format_ARGB32_Premultiplied)
        blurred.fill(Qt.transparent)
        scene = QGraphicsScene()
        item = scene.addPixmap(QPixmap.fromImage(img))
        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(14)
        item.setGraphicsEffect(blur)
        rp = QPainter(blurred)
        scene.render(rp)
        rp.end()
        maskp = QPainter(blurred)
        maskp.setCompositionMode(QPainter.CompositionMode_Clear)
        maskp.fillRect(0, 0, size, int(half - 16), Qt.transparent)
        maskp.end()
        p.drawImage(int(x - half), int(y - half), blurred)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setPen(Qt.NoPen)
        vgrad = QLinearGradient(
        x, y - 6,      # top
        x, y + 6       # bottom
    )
        vgrad.setColorAt(0.00, color)
        vgrad.setColorAt(0.45, QColor(255,255,255))
        vgrad.setColorAt(0.55, QColor(255,255,255))
        vgrad.setColorAt(1.00, QColor(255,255,255))
        p.setBrush(vgrad)
        p.drawPolygon(tri)
    def period_text(self):
        p = self.state.period
    # --- regular periods ---
        if 1 <= p <= 4:
            suffix = ["1st", "2nd", "3rd", "4th"][p-1]
            return f"{suffix}"
    # --- overtime periods ---
        ot_mapping = {
        5: "1 OT",
        6: "2 OT",
        7: "3 OT",
        8: "4 OT",
        9: "5 OT"
    }
        return ot_mapping.get(p, "")  # returns "" if period is 10+
    def ordinal(self, n):
        if n == 1: return "1st"
        if n == 2: return "2nd"
        if n == 3: return "3rd"
        return f"{n}th"
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
    def draw_logo_in_top_rounded_window(self, p, x, y, w, h, logo, radius=12):
        if logo is None or not isinstance(logo, QPixmap) or logo.isNull():
            return 
        p.save()
        p.setRenderHint(QPainter.SmoothPixmapTransform, True)
        path = QPainterPath()
        path.moveTo(x + radius, y)
        path.lineTo(x + w - radius, y)
        path.quadTo(x + w, y, x + w, y + radius)
        path.lineTo(x + w, y + h)      # flat bottom
        path.lineTo(x, y + h)
        path.lineTo(x, y + radius)
        path.quadTo(x, y, x + radius, y)
        p.setClipPath(path, Qt.IntersectClip)
        logo_scaled = logo.scaled(
            w, 9999,
        Qt.KeepAspectRatio,
        Qt.SmoothTransformation
    )
        lx = x + (w - logo_scaled.width()) // 2
        ly = y + (h - logo_scaled.height()) // 2
        p.drawPixmap(lx, ly, logo_scaled)
        p.restore()
    def clip_to_rounded_rect(self, p, x, y, w, h, radius=12):
        path = QPainterPath()
        rect = QRectF(x, y, w, h)
        path.addRoundedRect(rect, radius, radius)
        p.setClipPath(path, Qt.IntersectClip)

class BasketballScoreboard(QWidget):
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
        if self.mode == "transparent":
            self.setAttribute(Qt.WA_TranslucentBackground)
        else:
            self.bg_color = QColor(255, 0, 255)  # green chroma key for vMix
        self.setAutoFillBackground(False)
        ui_updater.refresh.connect(self.update)

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
    def paintEvent(self,event):
        DESIGN_W=1920
        DESIGN_H=1080
        p=QPainter(self)
        p.setRenderHints(QPainter.Antialiasing|QPainter.TextAntialiasing)
        scale=min(self.width()/DESIGN_W,self.height()/DESIGN_H)  # scale to fit window
        offset_x=(self.width()-DESIGN_W*scale)/2
        offset_y=(self.height()-DESIGN_H*scale)/2
        p.translate(offset_x,offset_y)
        p.scale(scale,scale)  # ignore Windows DPI completely
        if self.mode=="keyable":
            p.fillRect(0,0,DESIGN_W,DESIGN_H,self.bg_color)
        if self.show_basketball_intro:
            self.draw_basketball_intro(p)
        if self.show_basketball_scorebug:
            self.draw_basketball_scorebug(p)
        if self.show_basketball_breakboard:
            self.draw_basketball_breakboard(p)
        if self.state.breakboard_timer>0:
            self.draw_basketball_breakboard(p)
        if self.show_basketball_final:
            self.draw_basketball_final(p)
            return
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
            self.draw_timeout_rects(p,left_x+230,993,self.state.away_timeouts_basketball)
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
            self.draw_timeout_rects(p, 999 + 85, 993, self.state.home_timeouts_basketball)
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
    def draw_circular_outline(p: QPainter, x: float, y: float, radius: float):
        rect = QRectF(x - radius, y - radius, 2*radius, 2*radius)
        pen_top = QPen(QColor("white"), 2)
        pen_top.setStyle(Qt.SolidLine)
        p.setPen(pen_top)
        p.drawArc(rect, 0 * 16, 180 * 16)  # top half
        pen_bottom = QPen(QColor("white"), 2)
        pen_bottom.setStyle(Qt.DashLine)
        p.setPen(pen_bottom)
        p.drawArc(rect, 180 * 16, 180 * 16)  # bottom half

    def draw_top_gloss(self, p: QPainter, x, y, w, h):
        gloss_h = int(h * 0.35)
        gloss_y = int(y + h * 0.12)
        grad = QLinearGradient(x, gloss_y, x + w, gloss_y)
        grad.setColorAt(0.00, QColor(255, 255, 255, 0))
        grad.setColorAt(0.20, QColor(255, 255, 255, 50))
        grad.setColorAt(0.50, QColor(255, 255, 255, 70))  # brightest middle
        grad.setColorAt(0.80, QColor(255, 255, 255, 50))
        grad.setColorAt(1.00, QColor(255, 255, 255, 0))
        p.save()
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(grad))
        p.drawRect(int(x), gloss_y, int(w), gloss_h)
        p.restore()
    def draw_flat_segment(self, p, x, y, w, h, left_color: QColor, right_color: QColor):
        grad = QLinearGradient(x, y, x + w, y)
        grad.setColorAt(0.0, left_color)
        grad.setColorAt(1.0, right_color)
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(grad))
        p.drawRect(x, y, w, h)
    def draw_flat_segment_home(self, p, x, y, w, h, left_color: QColor, right_color: QColor):
        grad = QLinearGradient(x + w, y, x, y)
        grad.setColorAt(0.0, left_color)   # left side (end)
        grad.setColorAt(1.0, right_color)  # right side (start)
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(grad))
        p.drawRect(x, y, w, h)
    def draw_inset_border(self, p: QPainter, x, y, w, h, base_radius=12):
        inset = 2
        rx = x + inset
        ry = y + inset
        rw = w - inset*2
        rh = h - inset*2
        border = QColor("#505355")
        pen = QPen(border)
        pen.setWidth(2)     # thickness of the border
        pen.setJoinStyle(Qt.RoundJoin)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        radius = max(1, base_radius - inset)
        path = QPainterPath()
        path.moveTo(rx, ry + radius)
        path.lineTo(rx, ry + rh - radius)
        path.quadTo(rx, ry + rh, rx + radius, ry + rh)
        path.lineTo(rx + rw - radius, ry + rh)
        path.quadTo(rx + rw, ry + rh, rx + rw, ry + rh - radius)
        path.lineTo(rx + rw, ry + radius)
        p.drawPath(path)
        p.setPen(Qt.NoPen)        
    def draw_round_segment(self, p, x, y, w, h, color):
        radius = h / 1.5
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(color))
        p.drawRoundedRect(x, y, w, h, radius, radius)
        gloss_height = int(h * 1)  # top portion of gloss
        grad = QLinearGradient(x, y, x, y + gloss_height)
        grad.setColorAt(0.0, QColor(255, 255, 255, 110))  # top bright
        grad.setColorAt(1.0, QColor(255, 255, 255, 0))    # fade out
        p.setBrush(grad)
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(x, y, w, gloss_height,radius, radius)
    def draw_rounded_rect(self, p: QPainter, x, y, w, h, color: QColor):
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(color))
        radius = 12
        path = QPainterPath()
        path.moveTo(x, y)
        path.lineTo(x + w, y)
        path.lineTo(x + w, y + h - radius)
        path.quadTo(x + w, y + h, x + w - radius, y + h)
        path.lineTo(x + radius, y + h)
        path.quadTo(x, y + h, x, y + h - radius)
        path.lineTo(x, y)
        p.drawPath(path)
    def draw_timerounded_rect(self, p: QPainter, x, y, w, h, color: QColor):
        radius = 12
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(color))
        path = QPainterPath()
        path.moveTo(x, y)
        path.lineTo(x + w, y)
        path.lineTo(x + w, y + h - radius)
        path.quadTo(x + w, y + h, x + w - radius, y + h)
        path.lineTo(x + radius, y + h)
        path.quadTo(x, y + h, x, y + h - radius)
        path.lineTo(x, y)
        p.drawPath(path)
        border = QColor("#3a3c3e")
        p.save()
        pen = QPen(border, 2)
        pen.setJoinStyle(Qt.RoundJoin)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        inset = 1
        boost = 0  
        path2 = QPainterPath()
        start_y = y + radius + inset - boost
        if start_y < y:   # safety clamp so it doesn't go above rect
            start_y = y + inset
        path2.moveTo(x + inset, start_y)
        path2.lineTo(x + inset, y + h - radius - inset)
        path2.quadTo(x + inset,y + h - inset,x + radius + inset,y + h - inset)
        path2.lineTo(x + w - radius - inset, y + h - inset)
        path2.quadTo(x + w - inset,y + h - inset,x + w - inset,y + h - radius - inset)
        path2.lineTo(x + w - inset, start_y)
        p.drawPath(path2)
        p.restore()
    def draw_open_triangle(self, p: QPainter, x, y, size, color: QColor):
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(color))

        top = QPointF(x + size / 2, y)
        left = QPointF(x, y + size)
        right = QPointF(x + size, y + size)

        # left side
        p.drawLine(top, left)
        # right side
        p.drawLine(top, right)
    def draw_triangle_line(self, p: QPainter, x, y, size, count, spacing, color: QColor):
        for i in range(count):
            tx = x + i * (size + spacing)
            self.draw_open_triangle(p, tx, y, size, color)
    def draw_triangle_grid(self, p: QPainter, x, y, size, count_per_line, spacing, color: QColor):
        for row in range(6):
            ty = y + row * 4
            self.draw_triangle_line(
                p,
                x,
                ty,
                size,
                count_per_line,
                spacing,
                color
            )


    def clip_to_rect(self, p, x, y, w, h):
        path = QPainterPath()
        rect = QRectF(x, y, w, h)
        path.addRect(rect)
        p.setClipPath(path)
    def draw_leftrounded_rect(self, p: QPainter, x, y, w, h, color: QColor):
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(color))
        radius = 12
        path = QPainterPath()
        path.moveTo(x + radius, y)
        path.lineTo(x + w, y)
        path.lineTo(x + w, y + h)
        path.lineTo(x + radius, y + h)
        path.quadTo(x, y + h, x, y + h - radius)
        path.lineTo(x, y + radius)
        path.quadTo(x, y, x + radius, y)
        p.drawPath(path)       
    def draw_rightrounded_rect(self, p: QPainter, x, y, w, h, color: QColor):
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(color))
        radius = 12
        path = QPainterPath()
        path.moveTo(x, y)
        path.lineTo(x + w - radius, y)
        path.quadTo(x + w, y, x + w, y + radius)
        path.lineTo(x + w, y + h - radius)
        path.quadTo(x + w, y + h, x + w - radius, y + h)
        path.lineTo(x, y + h)
        path.lineTo(x, y)
        p.drawPath(path)
    def draw_rect(self, p, x, y, w, h, color):
        p.setPen(Qt.NoPen)
        p.setBrush(color)
        p.drawRect(int(x), int(y), int(w), int(h))
    def draw_left_triangle(self, p: QPainter, x, y, w, h, color: QColor):
        path = QPainterPath()
        path.moveTo(x - w / 3, y)          # tip (left)
        path.lineTo(x + w / 3, y - h / 3)  # top-right
        path.lineTo(x + w / 3, y + h / 3)  # bottom-right
        path.closeSubpath()
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(color))
        p.drawPath(path)
    def draw_right_triangle(self, p: QPainter, x, y, w, h, color: QColor):
        path = QPainterPath()
        path.moveTo(x + w / 3, y)          # tip (right)
        path.lineTo(x - w / 3, y - h / 3)  # top-left
        path.lineTo(x - w / 3, y + h / 3)  # bottom-left
        path.closeSubpath()
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(color))
        p.drawPath(path)
    def draw_transparent_to_black_rect(self, p: QPainter, x, y, w, h, radius: int = 12):
        grad = QLinearGradient(x, y, x + w, y + h)
        grad.setColorAt(0.0, QColor(0, 0, 0, 0))   # alpha = 0
        grad.setColorAt(0.5, QColor(0, 0, 0, 200))
        grad.setColorAt(1.0, QColor(0, 0, 0, 255))
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(grad))
        p.drawRoundedRect(QRect(int(x), int(y), int(w), int(h)), radius, radius)
    def draw_fully_gradient_rect(self, p: QPainter, x, y, w, h, color: QColor, radius: int = 12):
        darker = color.darker(225)   # 175 = 75% darker; adjust if needed
        sdarker = color.darker(125) 
        grad = QLinearGradient(x, y, x + w, y)
        grad.setColorAt(0.0, color)
        grad.setColorAt(0.5, darker)
        grad.setColorAt(1.0, darker)
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(grad))
        p.drawRoundedRect(QRect(int(x), int(y), int(w), int(h)), radius, radius)
    def draw_panel_base(self, p, x, y, w, h, color: QColor, thickness: int =5):
        radius = 10
        pen = QPen(color)
        pen.setWidth(thickness)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(x, y, w, h, radius , radius)
    def draw_ppanel_base(self, p, x, y, w, h, color: QColor, thickness: int =3):
        radius = 10
        pen = QPen(color)
        pen.setWidth(thickness)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(x, y, w, h, radius , radius)
    def draw_fpanel_base(self, p, x, y, w, h, color: QColor, thickness: int =2):
        radius = 10
        pen = QPen(color)
        pen.setWidth(thickness)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(x, y, w, h, radius , radius)   
    def draw_away_notch(self, p: QPainter, x, y, w, h, color: QColor):
        offset = h * 0.25
        p.setPen(Qt.NoPen)
        p.setBrush(color)
        path = QPainterPath()
        path.moveTo(x, y)
        path.lineTo(x + w, y + offset)
        path.lineTo(x + w, y + h - offset )
        path.lineTo(x, y + h)
        path.closeSubpath
        p.drawPath(path)
    def draw_home_notch(self, p: QPainter, x, y, w, h, color: QColor):
        offset = h * 0.25
        p.save()
        p.setPen(Qt.NoPen)
        p.setBrush(color)
        path = QPainterPath()
        path.moveTo(x + w, y)                 # top-right
        path.lineTo(x, y + offset)            # top-left inward
        path.lineTo(x, y + h - offset)        # bottom-left inward
        path.lineTo(x + w, y + h)             # bottom-right
        path.closeSubpath()
        p.drawPath(path)
        p.restore()
    def draw_bottom_event_text(self, p: QPainter, x: int, y: int, text: str):
        if not text:
            return
        w = 640
        h= 22
        p.setFont(self.event_font)
        p.setPen(Qt.white)
        p.drawText(QRect(x, y, w, h), Qt.AlignCenter, text)
    def draw_upper_event_text(self, p: QPainter, x: int, y: int, text: str):
        if not text:
            return
        w = 640
        h= 42
        p.setFont(self.introupper_font)
        p.setPen(Qt.white)
        p.drawText(QRect(x, y, w, h), Qt.AlignCenter, text)
    def draw_bbevent_text(self, p: QPainter, x: int, y: int, text: str):
        if not text:
            return
        w = 240
        h= 40
        p.setFont(self.upperevent_font)
        p.setPen(Qt.white)
        p.drawText(QRect(x, y, w, h), Qt.AlignVCenter | Qt.AlignHCenter, text)
    def draw_bevent_text(self, p: QPainter, x: int, y: int, text: str):
        if not text:
            return
        w = 240
        h= 40
        p.setFont(self.scoreevent_font)
        p.setPen(Qt.white)
        p.drawText(QRect(x, y, w, h), Qt.AlignVCenter | Qt.AlignHCenter, text)
    
    def draw_timeout_popup(self, p: QPainter, x, y, text):
        w = 240
        h = 45
        radius = 7
        p.setFont(self.timeout_font)
        p.setPen(Qt.white)
        p.drawText(QRect(x, y, w, h), Qt.AlignCenter, text)
    def draw_panel_glow(self, p, x, y, w, h, color: QColor):
        radius = 10
        glow_rect = QRectF(x+2, y+2, w-4, h-4)
        base = QColor(color)
        color_outer_rim = QColor(color).darker(100)
        color_inner_fill = QColor(color).lighter(150)
        rim_grad = QLinearGradient(
        glow_rect.left(), glow_rect.center().y(),
        glow_rect.right(), glow_rect.center().y())
        rim_grad.setColorAt(0.00, color_outer_rim)
        rim_grad.setColorAt(0.12, color_outer_rim)
        rim_grad.setColorAt(0.20, color_outer_rim)
        rim_grad.setColorAt(0.80, color_outer_rim)
        rim_grad.setColorAt(0.88, color_outer_rim)
        rim_grad.setColorAt(1.00, color_outer_rim)
        p.setPen(Qt.NoPen)
        p.setBrush(rim_grad)
        p.drawRoundedRect(glow_rect, radius, radius)
        fill_grad = QLinearGradient(
        glow_rect.left(), glow_rect.center().y(),
        glow_rect.right(), glow_rect.center().y())
        fill_grad.setColorAt(0.00, color_outer_rim)
        fill_grad.setColorAt(0.15, color_outer_rim)
        fill_grad.setColorAt(0.50, color_inner_fill)
        fill_grad.setColorAt(0.85, color_inner_fill)
        fill_grad.setColorAt(1.00, color_inner_fill)
        p.setBrush(fill_grad)
        p.drawRoundedRect(glow_rect, radius, radius)
        white_strong = QColor(255, 255, 255, 160)
        white_soft   = QColor(255, 255, 255, 60)
        bloom = QLinearGradient(
        glow_rect.center().x(), glow_rect.bottom(),
        glow_rect.center().x(), glow_rect.top())
        bloom.setColorAt(0.00, color_outer_rim)  # base edge
        bloom.setColorAt(0.20, color_outer_rim)    # fade
        bloom.setColorAt(0.45, Qt.transparent)  # vanish
        p.setBrush(bloom)
        p.drawRoundedRect(glow_rect, radius, radius)
    def format_rank_name(self, rank, name):
        try:
            r = int(rank)
        except:
            r = 0
        name = name.upper()
        if r <= 0:
            return "", name
        return str(r), name
    def draw_top_gloss(self, p: QPainter, x, y, w, h):
        gloss_h = int(h * 0.35)
        gloss_y = int(y + h * 0.12)
        grad = QLinearGradient(x, gloss_y, x + w, gloss_y)
        grad.setColorAt(0.00, QColor(255, 255, 255, 0))
        grad.setColorAt(0.20, QColor(255, 255, 255, 50))
        grad.setColorAt(0.50, QColor(255, 255, 255, 70))  # brightest middle
        grad.setColorAt(0.80, QColor(255, 255, 255, 50))
        grad.setColorAt(1.00, QColor(255, 255, 255, 0))
        p.save()
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(grad))
        p.drawRect(int(x), gloss_y, int(w), gloss_h)
        p.restore()
    def draw_horizontal_glow(p, x, y, w, h, color: QColor):
        grad = QLinearGradient(x, y, x + w, y)
        c0 = QColor(color)
        c0.setAlpha(0)
        c1 = QColor(color)
        c1.setAlpha(160)
        c2 = QColor(color)
        c2.setAlpha(0)
        grad.setColorAt(0.0, c0)
        grad.setColorAt(0.50, c1)
        grad.setColorAt(1.0, c2)
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(grad))
        p.drawRoundedRect(x, y, w, h, h/2, h/2)
    def draw_round_left(self, p: QPainter, x, y, w, h, color: QColor, r=10):
        p.setPen(Qt.NoPen)
        p.setBrush(color)
        path = QPainterPath()
        path.moveTo(x + r, y)
        path.lineTo(x + w, y)
        path.lineTo(x + w, y + h)
        path.lineTo(x + r, y + h)
        path.quadTo(x, y + h, x, y + h - r)
        path.lineTo(x, y + r)
        p.drawPath(path)
    def draw_rounded_rect(self, p: QPainter, x, y, w, h, color: QColor):
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(color))
        radius = 12
        path = QPainterPath()
        path.moveTo(x, y)
        path.lineTo(x + w, y)
        path.lineTo(x + w, y + h - radius)
        path.quadTo(x + w, y + h, x + w - radius, y + h)
        path.lineTo(x + radius, y + h)
        path.quadTo(x, y + h, x, y + h - radius)
        path.lineTo(x, y)
        p.drawPath(path)
    def draw_introround_left(self, p: QPainter, x, y, w, h, color: QColor, r=10):
        path = QPainterPath()
        path.moveTo(x + r, y)
        path.lineTo(x + w, y)
        path.lineTo(x + w, y + h)
        path.lineTo(x + r, y + h)
        path.quadTo(x, y + h, x, y + h - r)
        path.lineTo(x, y + r)
        path.quadTo(x, y, x + r, y)
        p.save()
        p.setPen(Qt.NoPen)
        grad = QLinearGradient(x, y, x + w, y)
        darker = color.darker(150)
        darke = color.darker(175)
        sdarker = color.darker(200)
        dark = color.darker(225)
        darkest = color.darker(250)
        grad.setColorAt(0.0, darker)      # left team color
        grad.setColorAt(0.2, darke)
        grad.setColorAt(0.4, sdarker)     # darker
        grad.setColorAt(0.4, dark)
        grad.setColorAt(0.6, darkest)
        grad.setColorAt(0.8, QColor(0,0,0))    # very dark
        grad.setColorAt(1.0, QColor(0,0,0))  # black
        p.setBrush(QBrush(grad))
        p.drawPath(path)
        p.restore()
    def draw_semitransparent_rounded_rect(self, p: QPainter, x, y, w, h, color: QColor):
        c = QColor(color)
        c.setAlpha(225)
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(c))
        radius = 12
        path = QPainterPath()
        path.moveTo(x, y)
        path.lineTo(x + w, y)
        path.lineTo(x + w, y + h - radius)
        path.quadTo(x + w, y + h, x + w - radius, y + h)
        path.lineTo(x + radius, y + h)
        path.quadTo(x, y + h, x, y + h - radius)
        path.lineTo(x, y)
        p.drawPath(path)
    def draw_round_right(self, p: QPainter, x, y, w, h, color: QColor, r=10):
        p.setPen(Qt.NoPen)
        p.setBrush(color)
        path = QPainterPath()
        path.moveTo(x, y)
        path.lineTo(x + w - r, y)
        path.quadTo(x + w, y, x + w, y + r)
        path.lineTo(x + w, y + h - r)
        path.quadTo(x + w, y + h, x + w - r, y + h)
        path.lineTo(x, y + h)
        path.lineTo(x, y)
        p.drawPath(path)
    def draw_introround_right(self, p: QPainter, x, y, w, h, color: QColor, r=10):
        path = QPainterPath()
        path.moveTo(x, y)
        path.lineTo(x + w - r, y)
        path.quadTo(x + w, y, x + w, y + r)
        path.lineTo(x + w, y + h - r)
        path.quadTo(x + w, y + h, x + w - r, y + h)
        path.lineTo(x, y + h)
        path.lineTo(x, y)
        p.save()
        p.setPen(Qt.NoPen)
        darker = color.darker(150)
        darke = color.darker(175)
        sdarker = color.darker(200)
        dark = color.darker(225)
        darkest = color.darker(250)
        grad = QLinearGradient(x + w, y, x, y)
        grad.setColorAt(0.0, darker)     
        grad.setColorAt(0.2, darke)
        grad.setColorAt(0.4, sdarker)    
        grad.setColorAt(0.4, dark)
        grad.setColorAt(0.6, darkest)
        grad.setColorAt(0.8, QColor(0,0,0))   
        grad.setColorAt(1.0, QColor(0,0,0)) 
        p.setBrush(QBrush(grad))
        p.drawPath(path)
        p.restore()
    def draw_bottom_round_rect(self, p: QPainter, x, y, w, h, color: QColor, radius=12):
        p.setPen(Qt.NoPen)
        p.setBrush(color)
        path = QPainterPath()
        path.moveTo(x, y)
        path.lineTo(x + w, y)
        path.lineTo(x + w, y + h - radius)
        path.quadTo(x + w, y + h,x + w - radius, y + h)
        path.lineTo(x + radius, y + h)
        path.quadTo(x, y + h,x, y + h - radius)
        path.lineTo(x, y)
        p.drawPath(path)
    def draw_glow_top_round(self, p: QPainter, x, y, w, h, color: QColor, thickness=2):
        r = 10
        glow_radius = 18
        img = QImage(w, h, QImage.Format_ARGB32_Premultiplied)
        img.fill(Qt.transparent)
        offp = QPainter(img)
        offp.setRenderHint(QPainter.Antialiasing, True)
        grad = QRadialGradient(w/2, h/2, max(w, h) * 0.75)
        c1 = QColor(color)
        c1.setAlpha(160)
        c2 = QColor(color)
        c2.setAlpha(0)
        grad.setColorAt(0.00, c1)
        grad.setColorAt(0.45, c1)
        grad.setColorAt(1.00, c2)
        offp.setPen(Qt.NoPen)
        offp.setBrush(grad)
        path = QPainterPath()
        path.moveTo(r, 0)
        path.quadTo(0, 0, 0, r)
        path.lineTo(0, h)
        path.lineTo(w, h)
        path.lineTo(w, r)
        path.quadTo(w, 0, w - r, 0)
        path.lineTo(r, 0)
        offp.drawPath(path)
        offp.end()
        blurred = QImage(w, h, QImage.Format_ARGB32_Premultiplied)
        blurred.fill(Qt.transparent)
        scene = QGraphicsScene()
        item = scene.addPixmap(QPixmap.fromImage(img))
        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(glow_radius)
        item.setGraphicsEffect(blur)
        rp = QPainter(blurred)
        scene.render(rp)
        rp.end()
        p.drawImage(x, y, blurred)
        p.setRenderHint(QPainter.Antialiasing, True)
        pen = QPen(color, thickness)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        outline = QPainterPath()
        outline.moveTo(x + r, y)
        outline.quadTo(x, y, x, y + r)
        outline.lineTo(x, y + h)
        outline.lineTo(x + w, y + h)
        outline.lineTo(x + w, y + r)
        outline.quadTo(x + w, y, x + w - r, y)
        outline.lineTo(x + r, y)
        p.drawPath(outline)
    def draw_glow_round_left(self, p: QPainter, x, y, w, h, color: QColor, thickness=2):
        r = 10
        glow_radius = 18
        img = QImage(w, h, QImage.Format_ARGB32_Premultiplied)
        img.fill(Qt.transparent)
        offp = QPainter(img)
        offp.setRenderHint(QPainter.Antialiasing, True)
        grad = QRadialGradient(w/2, h/2, max(w, h) * 0.75)
        c1 = QColor(color)
        c1.setAlpha(160)
        c2 = QColor(color)
        c2.setAlpha(0)
        grad.setColorAt(0.00, c1)
        grad.setColorAt(0.45, c1)
        grad.setColorAt(1.00, c2)
        offp.setPen(Qt.NoPen)
        offp.setBrush(grad)
        path = QPainterPath()
        path.moveTo(r, 0)
        path.quadTo(0, 0, 0, r)
        path.lineTo(0, h - r)
        path.quadTo(0, h, r, h)
        path.lineTo(w, h)         
        path.lineTo(w, 0)         
        path.lineTo(r, 0)
        offp.drawPath(path)
        offp.end()
        blurred = QImage(w, h, QImage.Format_ARGB32_Premultiplied)
        blurred.fill(Qt.transparent)
        scene = QGraphicsScene()
        item = scene.addPixmap(QPixmap.fromImage(img))
        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(glow_radius)
        item.setGraphicsEffect(blur)
        rp = QPainter(blurred)
        scene.render(rp)
        rp.end()
        p.drawImage(x, y, blurred)
        p.setRenderHint(QPainter.Antialiasing, True)
        pen = QPen(color, thickness)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        outline = QPainterPath()
        outline.moveTo(x + r, y)
        outline.quadTo(x, y, x, y + r)
        outline.lineTo(x, y + h - r)
        outline.quadTo(x, y + h, x + r, y + h)
        outline.lineTo(x + w, y + h)
        outline.moveTo(x + w, y)
        outline.lineTo(x + r, y)
        p.drawPath(outline)
    def draw_glow_round_ddleft(self, p: QPainter, x, y, w, h, color: QColor, thickness=2):
        r = 10
        glow_radius = 18
        top_inset = 125   # <-- adjustable top inset
        img = QImage(w, h, QImage.Format_ARGB32_Premultiplied)
        img.fill(Qt.transparent)
        offp = QPainter(img)
        offp.setRenderHint(QPainter.Antialiasing, True)
        grad = QLinearGradient(0, h/2, w*0.5, h/2)
        c1 = QColor(color)
        c1.setAlpha(200)
        c2 = QColor(color)
        c2.setAlpha(0)
        grad.setColorAt(0.0, c1)
        grad.setColorAt(1.0, c2)
        offp.setPen(Qt.NoPen)
        offp.setBrush(grad)
        path = QPainterPath()
        path.moveTo(r, 0)
        path.quadTo(0, 0, 0, r)
        path.lineTo(0, h - r)
        path.quadTo(0, h, r, h)
        path.lineTo(w, h)
        path.lineTo(w, 0)
        path.closeSubpath()
        offp.drawPath(path)
        offp.end()
        blurred = QImage(w, h, QImage.Format_ARGB32_Premultiplied)
        blurred.fill(Qt.transparent)
        scene = QGraphicsScene()
        item = scene.addPixmap(QPixmap.fromImage(img))
        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(glow_radius)
        item.setGraphicsEffect(blur)
        rp = QPainter(blurred)
        scene.render(rp)
        rp.end()
        p.drawImage(x, y, blurred)
        p.setRenderHint(QPainter.Antialiasing, True)
        pen = QPen(color, thickness)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        outline = QPainterPath()
        outline.moveTo(x + w, y + h)
        outline.lineTo(x + r, y + h)
        outline.quadTo(x, y + h, x, y + h - r)
        outline.lineTo(x, y + r)
        outline.quadTo(x, y, x + r, y)
        outline.lineTo(x + top_inset, y)
        p.drawPath(outline)
    def draw_glow_round_ddright(self, p: QPainter, x, y, w, h, color: QColor, thickness=1):
        r = 10
        glow_radius = 18
        top_inset = 25   # <-- adjustable top indent
        img = QImage(w, h, QImage.Format_ARGB32_Premultiplied)
        img.fill(Qt.transparent)
        offp = QPainter(img)
        offp.setRenderHint(QPainter.Antialiasing, True)
        grad = QLinearGradient(w, h/2, w*0.5, h/2)
        c1 = QColor(color)
        c1.setAlpha(200)  # strong inside
        c2 = QColor(color)
        c2.setAlpha(0)    # fade inside
        grad.setColorAt(0.00, c1)
        grad.setColorAt(1.00, c2)
        offp.setPen(Qt.NoPen)
        offp.setBrush(grad)
        path = QPainterPath()
        path.moveTo(0, 0)
        path.lineTo(w - r, 0)
        path.quadTo(w, 0, w, r)
        path.lineTo(w, h - r)
        path.quadTo(w, h, w - r, h)
        path.lineTo(0, h)
        path.closeSubpath()
        offp.drawPath(path)
        offp.end()
        blurred = QImage(w, h, QImage.Format_ARGB32_Premultiplied)
        blurred.fill(Qt.transparent)
        scene = QGraphicsScene()
        item = scene.addPixmap(QPixmap.fromImage(img))
        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(glow_radius)
        item.setGraphicsEffect(blur)
        rp = QPainter(blurred)
        scene.render(rp)
        rp.end()
        p.drawImage(x, y, blurred)
        p.setRenderHint(QPainter.Antialiasing, True)
        pen = QPen(color, thickness)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        outline = QPainterPath()
        outline.moveTo(x, y + h)
        outline.lineTo(x + w - r, y + h)
        outline.quadTo(x + w, y + h, x + w, y + h - r)
        outline.lineTo(x + w, y + r)
        outline.quadTo(x + w, y, x + w - r, y)
        outline.lineTo(x + top_inset, y)
        p.drawPath(outline)
    def draw_glow_round_right(self, p: QPainter, x, y, w, h, color: QColor, thickness=2):
        r = 10
        glow_radius = 18
        img = QImage(w, h, QImage.Format_ARGB32_Premultiplied)
        img.fill(Qt.transparent)
        offp = QPainter(img)
        offp.setRenderHint(QPainter.Antialiasing, True)
        grad = QRadialGradient(w/2, h/2, max(w, h) * 0.75)
        c1 = QColor(color)
        c1.setAlpha(160)
        c2 = QColor(color)
        c2.setAlpha(0)
        grad.setColorAt(0.00, c1)
        grad.setColorAt(0.45, c1)
        grad.setColorAt(1.00, c2)
        offp.setPen(Qt.NoPen)
        offp.setBrush(grad)
        path = QPainterPath()
        path.moveTo(0, 0)
        path.lineTo(w - r, 0)
        path.quadTo(w, 0, w, r)
        path.lineTo(w, h - r)
        path.quadTo(w, h, w - r, h)
        path.lineTo(0, h)
        offp.drawPath(path)
        offp.end()
        blurred = QImage(w, h, QImage.Format_ARGB32_Premultiplied)
        blurred.fill(Qt.transparent)
        scene = QGraphicsScene()
        item = scene.addPixmap(QPixmap.fromImage(img))
        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(glow_radius)
        item.setGraphicsEffect(blur)
        rp = QPainter(blurred)
        scene.render(rp)
        rp.end()
        p.drawImage(x, y, blurred)
        p.setRenderHint(QPainter.Antialiasing, True)
        pen = QPen(color, thickness)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)        
        outline = QPainterPath()
        outline.moveTo(x, y)
        outline.lineTo(x + w - r, y)
        outline.quadTo(x + w, y, x + w, y + r)
        outline.lineTo(x + w, y + h - r)
        outline.quadTo(x + w, y + h, x + w - r, y + h)
        outline.lineTo(x, y + h)
        p.drawPath(outline)
    def draw_inner_edge_glow(self,p:QPainter,x,y,w,h,color:QColor):
        img=QImage(w,h,QImage.Format_ARGB32_Premultiplied)
        img.fill(Qt.transparent)
        off=QPainter(img)
        off.setRenderHint(QPainter.Antialiasing,True)
        r=h*0.22
        path=QPainterPath()
        path.addRoundedRect(0,0,w,h,r,r)
        off.setClipPath(path)
        grad=QLinearGradient(0,0,w,0)
        grad.setColorAt(0.00,color)
        grad.setColorAt(0.28,QColor(255,255,255))
        grad.setColorAt(0.55,QColor(255,255,255,0))
        grad.setColorAt(1.00,QColor(0,0,0,0))
        off.setPen(Qt.NoPen)
        off.setBrush(grad)
        strip_h=int(h*0.45)
        off.drawRect(0,(h-strip_h)//2,w,strip_h)
        off.end()
        blurred=QImage(w,h,QImage.Format_ARGB32_Premultiplied)
        blurred.fill(Qt.transparent)
        scene=QGraphicsScene()
        item=scene.addPixmap(QPixmap.fromImage(img))
        blur=QGraphicsBlurEffect()
        blur.setBlurRadius(10)
        item.setGraphicsEffect(blur)
        rp=QPainter(blurred)
        scene.render(rp)
        rp.end()
        p.drawImage(x,y,blurred)
    def draw_timeout_rects(self, p: QPainter, x: int, y: int, remaining: int, max_count: int = 5):
        size = 6
        spacing = 3
        remaining = max(0, min(max_count, int(remaining)))
        p.setPen(Qt.NoPen)  
        for i in range(max_count):
            cy = y + (max_count - 1 - i) * (size + spacing)
            filled = (i < remaining)
            p.setBrush(QColor("white") if filled else QColor(255, 255, 255, 60))
            p.drawEllipse(int(x), int(cy), size, size)
    def draw_fully_gradient_rect(self,p:QPainter,x,y,w,h,color:QColor,radius:int=12):
        darker=color.darker(175)
        sdarker=color.darker(125)
        grad=QLinearGradient(x,y,x+w,y)
        grad.setColorAt(0.0,color)
        grad.setColorAt(0.5,sdarker)
        grad.setColorAt(1.0,darker)
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(grad))
        p.drawRoundedRect(QRect(int(x),int(y),int(w),int(h)),radius,radius)
    def draw_top_flat_rect(self,p:QPainter,x,y,w,h,color:QColor,radius:int=12):
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(color))
        path=QPainterPath()
        path.moveTo(x,y)
        path.lineTo(x+w,y)
        path.lineTo(x+w,y+h-radius)
        path.quadTo(x+w,y+h,x+w-radius,y+h)
        path.lineTo(x+radius,y+h)
        path.quadTo(x,y+h,x,y+h-radius)
        path.lineTo(x,y)
        p.drawPath(path)
    def draw_fully_grounded_rect(self,p:QPainter,x,y,w,h,radius:int=12):
        grad=QLinearGradient(x,y,x+w,y)
        grad.setColorAt(0.0,QColor(0,0,0))
        grad.setColorAt(0.5,QColor(128,128,128))
        grad.setColorAt(1.0,QColor(0,0,0))
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(grad))
        p.drawRoundedRect(QRect(int(x),int(y),int(w),int(h)),radius,radius)
    def draw_fully_rounded_rect(self, p: QPainter, x, y, w, h, color: QColor):
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(color))
        radius = 12 
        p.drawRoundedRect(QRect(int(x), int(y), int(w), int(h)), radius, radius)
    def draw_normal_rect(self, p: QPainter, x, y, w, h, color: QColor):
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(color))
        p.drawRect(QRect(int(x), int(y), int(w), int(h)))
    def draw_transparentnormal_rect(self, p: QPainter, x, y, w, h, color: QColor):
        p.setPen(Qt.NoPen)
        color.setAlpha(240)
        p.setBrush(QBrush(color))
        p.drawRect(QRect(int(x), int(y), int(w), int(h)))

    def draw_top_right_flat(self,p:QPainter,x,y,w,h,color:QColor):
        radius=12
        path=QPainterPath()
        path.moveTo(x+radius,y)
        path.lineTo(x+w,y)
        path.lineTo(x+w,y+h-radius)
        path.quadTo(x+w,y+h,x+w-radius,y+h)
        path.lineTo(x+radius,y+h)
        path.quadTo(x,y+h,x,y+h-radius)
        path.lineTo(x,y+radius)
        path.quadTo(x,y,x+radius,y)
        path.closeSubpath()
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(color))
        p.drawPath(path)
    def draw_rect_shadow(self, p, x, y, w, h, color):
        shadow_color = QColor(255,255,255,140)
        for i in range(6):
            shadow_color.setAlpha(80 - i*12)
            p.setBrush(shadow_color)
            p.drawRect(int(x + 4 + i), int(y + 4 + i), int(w - 2*i), int(h - 2*i))
        p.setBrush(color)
        p.drawRect(int(x), int(y), int(w), int(h))
    def draw_possession_text(self, p: QPainter, x, y, color: QColor):
        p.setPen(color)
        font = p.font()
        font.setPointSize(11)   # adjust if needed
        font.setBold(True)
        p.setFont(font)
        p.drawText(x, y, "POSS")
    def draw_fouls_text(self, p: QPainter, x, y, color: QColor):
        p.setPen(color)
        font = p.font()
        font.setPointSize(11)   # adjust if needed
        font.setBold(True)
        p.setFont(font)
        p.drawText(x, y, "Fouls")
    def draw_ffully_rounded_rect(self, p: QPainter, x, y, w, h, radius: int = 10):
        p.save()
        p.setPen(Qt.NoPen)
        grad = QLinearGradient(x, y, x, y + h)
        grad.setColorAt(0.0, QColor(200, 200, 200))
        grad.setColorAt(0.2, QColor(40, 40, 40))
        grad.setColorAt(0.4, QColor(40, 40, 40))
        grad.setColorAt(0.5, QColor(40, 40, 40))
        grad.setColorAt(0.6, QColor(40, 40, 40))
        grad.setColorAt(0.8, QColor(40, 40, 40))
        grad.setColorAt(1.0, QColor(200, 200, 200))
        p.setBrush(QBrush(grad))
        p.drawRoundedRect(QRect(int(x), int(y), int(w), int(h)), radius, radius)
        p.restore()
    def draw_top_rounded_rect(self, p: QPainter, x, y, w, h, color: QColor, radius: int = 12):
        p.setPen(Qt.NoPen)
        p.setBrush(color)
        path = QPainterPath()
        path.moveTo(x + radius, y)
        path.lineTo(x + w - radius, y)
        path.quadTo(x + w, y, x + w, y + radius)
        path.lineTo(x + w, y + h)
        path.lineTo(x, y + h)
        path.lineTo(x, y + radius)
        path.quadTo(x, y, x + radius, y)
        path.closeSubpath()
        p.drawPath(path)
    def draw_rect_shadow(self, p, x, y, w, h, color):
        shadow_color = QColor(255,255,255,140)
        for i in range(6):
            shadow_color.setAlpha(80 - i*12)
            p.setBrush(shadow_color)
            p.drawRect(int(x + 4 + i), int(y + 4 + i), int(w - 2*i), int(h - 2*i))
        p.setBrush(color)
        p.drawRect(int(x), int(y), int(w), int(h))
    def draw_fully_gradient_rect(self, p: QPainter, x, y, w, h, color: QColor, radius: int = 12):
        darker = color.darker(225)   # 175 = 75% darker; adjust if needed
        sdarker = color.darker(125) 
        grad = QLinearGradient(x, y, x + w, y)
        grad.setColorAt(0.0, color)
        grad.setColorAt(0.5, darker)
        grad.setColorAt(1.0, darker)
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(grad))
        p.drawRoundedRect(QRect(int(x), int(y), int(w), int(h)), radius, radius)
    def draw_panel_base(self, p, x, y, w, h, color: QColor, thickness: int =5):
        radius = 10
        pen = QPen(color)
        pen.setWidth(thickness)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(x, y, w, h, radius , radius)
    def draw_ppanel_base(self, p, x, y, w, h, color: QColor, thickness: int =3):
        radius = 10
        pen = QPen(color)
        pen.setWidth(thickness)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(x, y, w, h, radius , radius)
    def draw_fpanel_base(self, p, x, y, w, h, color: QColor, thickness: int =2):
        radius = 10
        pen = QPen(color)
        pen.setWidth(thickness)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(x, y, w, h, radius , radius)   
    def draw_away_notch(self, p: QPainter, x, y, w, h, color: QColor):
        offset = h * 0.25
        p.setPen(Qt.NoPen)
        p.setBrush(color)
        path = QPainterPath()
        path.moveTo(x, y)
        path.lineTo(x + w, y + offset)
        path.lineTo(x + w, y + h - offset )
        path.lineTo(x, y + h)
        path.closeSubpath
        p.drawPath(path)
    def draw_home_notch(self, p: QPainter, x, y, w, h, color: QColor):
        offset = h * 0.25
        p.save()
        p.setPen(Qt.NoPen)
        p.setBrush(color)
        path = QPainterPath()
        path.moveTo(x + w, y)                 # top-right
        path.lineTo(x, y + offset)            # top-left inward
        path.lineTo(x, y + h - offset)        # bottom-left inward
        path.lineTo(x + w, y + h)             # bottom-right
        path.closeSubpath()
        p.drawPath(path)
        p.restore()
    def draw_bottom_event_text(self, p: QPainter, x: int, y: int, text: str):
        if not text:
            return
        w = 640
        h= 22
        p.setFont(self.event_font)
        p.setPen(Qt.white)
        p.drawText(QRect(x, y, w, h), Qt.AlignCenter, text)
    def draw_event_text(self, p: QPainter, x: int, y: int, text: str):
        if not text:
            return
        w = 240
        h= 22
        p.setFont(self.record_font)
        p.setPen(Qt.white)
        p.drawText(QRect(x, y, w, h), Qt.AlignVCenter | Qt.AlignHCenter, text)
    def draw_fully_gradient_rect(self, p: QPainter, x, y, w, h, color: QColor, radius: int = 12):
        darker = color.darker(225)   # 175 = 75% darker; adjust if needed
        sdarker = color.darker(125) 
        grad = QLinearGradient(x, y, x + w, y)
        grad.setColorAt(0.0, color)
        grad.setColorAt(0.5, darker)
        grad.setColorAt(1.0, darker)
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(grad))
        p.drawRoundedRect(QRect(int(x), int(y), int(w), int(h)), radius, radius)
    def draw_panel_base(self, p, x, y, w, h, color: QColor, thickness: int =5):
        radius = 10
        pen = QPen(color)
        pen.setWidth(thickness)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(x, y, w, h, radius , radius)
    def draw_ppanel_base(self, p, x, y, w, h, color: QColor, thickness: int =3):
        radius = 10
        pen = QPen(color)
        pen.setWidth(thickness)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(x, y, w, h, radius , radius)
    def draw_fpanel_base(self, p, x, y, w, h, color: QColor, thickness: int =2):
        radius = 10
        pen = QPen(color)
        pen.setWidth(thickness)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(x, y, w, h, radius , radius)   
    def draw_away_notch(self, p: QPainter, x, y, w, h, color: QColor):
        offset = h * 0.25
        p.setPen(Qt.NoPen)
        p.setBrush(color)
        path = QPainterPath()
        path.moveTo(x, y)
        path.lineTo(x + w, y + offset)
        path.lineTo(x + w, y + h - offset )
        path.lineTo(x, y + h)
        path.closeSubpath
        p.drawPath(path)
    def draw_home_notch(self, p: QPainter, x, y, w, h, color: QColor):
        offset = h * 0.25
        p.save()
        p.setPen(Qt.NoPen)
        p.setBrush(color)
        path = QPainterPath()
        path.moveTo(x + w, y)                 # top-right
        path.lineTo(x, y + offset)            # top-left inward
        path.lineTo(x, y + h - offset)        # bottom-left inward
        path.lineTo(x + w, y + h)             # bottom-right
        path.closeSubpath()
        p.drawPath(path)
        p.restore()
    def draw_bottom_event_text(self, p: QPainter, x: int, y: int, text: str):
        if not text:
            return
        w = 640
        h= 22
        p.setFont(self.event_font)
        p.setPen(Qt.white)
        p.drawText(QRect(x, y, w, h), Qt.AlignCenter, text)
    def draw_event_text(self, p: QPainter, x: int, y: int, text: str):
        if not text:
            return
        w = 240
        h= 22
        p.setFont(self.record_font)
        p.setPen(Qt.white)
        p.drawText(QRect(x, y, w, h), Qt.AlignVCenter | Qt.AlignHCenter, text)
    def period_text(self):
        p = self.state.period
        if 1 <= p <= 4:
            suffix = ["1st", "2nd", "3rd", "4th"][p-1]
            return f"{suffix}"
        ot_mapping = {
        5: "1 OT",
        6: "2 OT",
        7: "3 OT",
        8: "4 OT",
        9: "5 OT",
        11: "FINAL"
    }
        return ot_mapping.get(p, "")  # returns "" if period is 10+
    def ordinal(self, n):
        if n == 1: return "1st"
        if n == 2: return "2nd"
        if n == 3: return "3rd"
        return f"{n}th"
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
    def draw_logo_in_top_rounded_window(self, p, x, y, w, h, logo, radius=12):
        if logo is None or logo.isNull():
            return
        p.save()
        p.setRenderHint(QPainter.SmoothPixmapTransform, True)
        path = QPainterPath()
        path.moveTo(x + radius, y)
        path.lineTo(x + w - radius, y)
        path.quadTo(x + w, y, x + w, y + radius)
        path.lineTo(x + w, y + h)      # flat bottom
        path.lineTo(x, y + h)
        path.lineTo(x, y + radius)
        path.quadTo(x, y, x + radius, y)
        p.setClipPath(path, Qt.IntersectClip)
        logo_scaled = logo.scaled(w, 9999,Qt.KeepAspectRatio,Qt.SmoothTransformation)
        lx = x + (w - logo_scaled.width()) // 2
        ly = y + (h - logo_scaled.height()) // 2
        p.drawPixmap(lx, ly, logo_scaled)
        p.restore()
    def clip_to_rounded_rect(self, p, x, y, w, h, radius=12):
        path = QPainterPath()
        rect = QRectF(x, y, w, h)
        path.addRoundedRect(rect, radius, radius)
        p.setClipPath(path, Qt.IntersectClip)
    def pct(self, made, missed):
        total = made + missed
        if total == 0:
            return "0%"
        return f"{round((made / total) * 100):d}%"
class VolleyballScoreboard(QWidget):
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
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing)
        w = self.width()
        h = self.height()
        if self.mode == "keyable":
            p.fillRect(self.rect(), self.bg_color)
        if self.show_volleyball_intro:
            self.draw_volleyball_intro(p)
        if self.show_volleyball_scorebug:
            self.draw_volleyball_scorebug(p)
        if self.show_volleyball_breakboard:
            self.draw_volleyball_breakboard(p)

            return
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
        self.draw_timeout_rects(p, left_x + 55, 53, self.state.away_timeouts_volleyball, align="right")
        self.draw_rect_transparent(p, sx, sy, sw, 50, QColor("#000000"))
        p.setFont(self.score_font)
        p.setPen(Qt.white)
        p.drawText(left_x+192, 2, 120, 70, Qt.AlignCenter, str(self.state.away_pts))

        ## -- HOME SECTION --
        logo_x, logo_y, logo_w, logo_h = right_x + 7, 75, 40, 4
        p.save()
        self.draw_logo_in_top_rounded_window(p,logo_x,logo_y,logo_w,logo_h,self.state.home_logo)
        p.restore()
        self.draw_rect(p, right_x, 60, right_w, 50, self.state.home_color)

        self.draw_timeout_rects(p, right_x+55, 102, self.state.home_timeouts_volleyball, align="right")
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
        p.drawText(cx, cy + 50, cw, 26, Qt.AlignCenter, f"{self.period_text()}")
        p.setFont(self.set_font)
        p.setPen(Qt.white)
        period = self.state.period
        period_text = self.period_text()
        if period == 6:
            p.drawText(cx, cy + 38, cw, 26, Qt.AlignCenter, period_text)
        else:
            p.drawText(cx, cy + 32, cw, 18, Qt.AlignCenter, "SET")
            p.drawText(cx, cy + 54, cw, 18, Qt.AlignCenter, self.period_text())    
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
    def draw_normal_rect(self, p: QPainter, x, y, w, h, color: QColor):
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(color))
        p.drawRect(QRect(int(x), int(y), int(w), int(h)))
    def draw_bottom_event_text(self, p: QPainter, x: int, y: int, text: str):
        if not text:
            return
        w = 640
        h= 22
        p.setFont(self.event_font)
        p.setPen(Qt.white)
        p.drawText(QRect(x, y, w, h), Qt.AlignCenter, text)
    def draw_upper_event_text(self, p: QPainter, x: int, y: int, text: str):
        if not text:
            return
        w = 640
        h= 42
        p.setFont(self.introupper_font)
        p.setPen(Qt.white)
        p.drawText(QRect(x, y, w, h), Qt.AlignCenter, text)
    def draw_bbevent_text(self, p: QPainter, x: int, y: int, text: str):
        if not text:
            return
        w = 240
        h= 40
        p.setFont(self.upperevent_font)
        p.setPen(Qt.white)
        p.drawText(QRect(x, y, w, h), Qt.AlignVCenter | Qt.AlignHCenter, text)
    def draw_bevent_text(self, p: QPainter, x: int, y: int, text: str):
        if not text:
            return
        w = 240
        h= 40
        p.setFont(self.scoreevent_font)
        p.setPen(Qt.white)
        p.drawText(QRect(x, y, w, h), Qt.AlignVCenter | Qt.AlignHCenter, text)
    def clip_to_rounded_rect(self, p, x, y, w, h, radius=12):
        path = QPainterPath()
        rect = QRectF(x, y, w, h)
        path.addRoundedRect(rect, radius, radius)
        p.setClipPath(path, Qt.IntersectClip)
    def draw_center_line(self, p, x, y, w, h, color=QColor(0, 0, 0), thickness=2):
        mid_y = y + h // 2
        pen = QPen(color, thickness)
        pen.setCosmetic(True)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        p.drawLine(x, mid_y, x + w, mid_y)
    def draw_center_vertical_line(self, p, x, y, w, h, color=QColor(0, 0, 0), thickness=2):
        mid_x = x + w // 2
        pen = QPen(color, thickness)
        pen.setCosmetic(True)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        p.drawLine(mid_x, y, mid_x, y + h)
    def draw_timeout_rects(self, p: QPainter, x, y, remaining, max_count=2, align="left"):
        w = 43
        h = 4
        spacing = 7
        radius = 1

        remaining = max(0, min(max_count, int(remaining)))
        p.setPen(Qt.NoPen)

        if align == "left":
            for i in range(max_count):
                rect_x = x + i * (w + spacing)
                idx_from_left = max_count - 1 - i
                filled = (idx_from_left < remaining)
                p.setBrush(QColor("white") if filled else QColor(255,255,255,60))
                p.drawRoundedRect(QRect(int(rect_x), int(y), int(w), int(h)), radius, radius)

        if  align == "right":
            total_w = max_count * w + (max_count - 1) * spacing
            for i in range(max_count):
            # i==0 is leftmost visual cell; determine whether it's filled by comparing index from right
                rect_x = x + i * (w + spacing)
            # The index from the right side:
                idx_from_right = max_count - 1 - i
                filled = (idx_from_right < remaining)
                p.setBrush(QColor("white") if filled else QColor(255,255,255,60))
                p.drawRoundedRect(QRect(int(rect_x), int(y), int(w), int(h)), radius, radius)
    def draw_rect_transparent(self, p, x, y, w, h, color):
        fill = QColor(color)
        fill.setAlpha(120)  # adjust transparency (0-255)

        p.setPen(Qt.NoPen)       # no outline
        p.setBrush(fill)         # transparent fill
        p.drawRect(int(x), int(y), int(w), int(h))
    def period_text(self):
        p = self.state.period
        if p == 1: return "1"
        if p == 2: return "2"
        if p == 3: return "3"
        if p == 4: return "4"
        if p == 5: return "5"
        if p == 6: return "Final"
        return ""
    def draw_rect(self, p, x, y, w, h, color):
        p.setPen(Qt.NoPen)
        p.setBrush(color)
        p.drawRect(int(x), int(y), int(w), int(h))
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
    def draw_logo_in_top_rounded_window(self, p, x, y, w, h, logo, radius=12):
        if not logo:
            return

        p.setRenderHint(QPainter.SmoothPixmapTransform, True)
        img = logo.toImage()
        img = img.scaled(w,9999,Qt.KeepAspectRatio,Qt.SmoothTransformation)
        logo_scaled = QPixmap.fromImage(img)
        lx = x
        ly = y + (h - logo_scaled.height()) // 2
        path = QPainterPath()
        path.moveTo(x + radius, y)
        path.lineTo(x + w - radius, y)
        path.quadTo(x + w, y, x + w, y + radius)
        path.lineTo(x + w, y + h)
        path.lineTo(x, y + h)
        path.lineTo(x, y + radius)
        path.quadTo(x, y, x + radius, y)
        p.save()
        p.setClipPath(path, Qt.IntersectClip)
        p.drawPixmap(lx, ly, logo_scaled)
        p.restore()   
class SoccerScoreboard(QWidget):
    def __init__(self, state: ScoreState, mode="transparent", parent=None):
        super().__init__(parent)
        self.state = state
        self.mode = mode
        self.flash_on = False
        self.show_soccer_intro = False
        self.show_soccer_breakboard = False
        self.show_soccer_scorebug = True
        self.show_home_goal = False
        self.show_away_goal = False
        screen = QApplication.primaryScreen()
        dpi_scale = screen.devicePixelRatio()
        self.setFixedSize(int(1920*dpi_scale), int(1080*dpi_scale))
        if self.mode == "transparent":
            self.setAttribute(Qt.WA_TranslucentBackground)
        else:
            self.bg_color = QColor(255, 0, 255) # green chroma key for vMix
        self.setAutoFillBackground(False)

        # fonts
        self.title_font = QFont("BigNoodleTitling", 20)
        self.timer_font = QFont("College", 21, QFont.Bold)
        self.period_font = QFont("College", 18, QFont.Bold)
        self.score_font = QFont("College", 25, QFont.Bold)
        self.event_font = QFont("BigNoodleTitling", 15, QFont.Bold)
        self.record_font = QFont("College", 12, QFont.Bold)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing)
        w = self.width()
        h = self.height()
        if self.mode == "keyable":
            p.fillRect(self.rect(), self.bg_color)
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

            return
    def draw_soccer_intro(self, p):
        pass
    def draw_soccer_breakboard(self, p):
        pass
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
        self.draw_rect(p, left_x, 35, left_w, 35, self.state.home_color)
        self.draw_rect(p, right_x, 35, right_w, 35, self.state.away_color)
        self.draw_rect(p, px, 35, pw, 35, QColor("#1d1d1d"))
        self.draw_rect(p, tx, 35, tw, 35, QColor("#2b2d2f"))
        self.draw_transparentnormal_rect(p, left_x+190, 35, 35, 35, QColor("#2a2a2a"))
        self.draw_transparentnormal_rect(p, right_x+190, 35, 35, 35, QColor("#2a2a2a"))
        self.draw_transparentnormal_rect(p, left_x, 35, 48, 35, darker_home)
        self.draw_transparentnormal_rect(p, right_x, 35, 48, 35, darker_away)
        p.setFont(self.score_font)
        p.setPen(Qt.white)
        p.drawText(left_x+183, 35, 50, 35, Qt.AlignCenter, str(self.state.home_pts))
        p.setFont(self.title_font)
        p.setPen(Qt.white)
        p.drawText(left_x+50, 40, 135, 25, Qt.AlignLeft | Qt.AlignVCenter, self.state.home_name)
        p.setFont(self.score_font)
        p.setPen(Qt.white)
        p.drawText(right_x+183, 35, 50, 35, Qt.AlignCenter, str(self.state.away_pts))
        p.setFont(self.title_font)
        p.setPen(Qt.white)
        p.drawText(right_x+50, 40, 135, 25, Qt.AlignLeft | Qt.AlignVCenter, self.state.away_name)
        #self.draw_transparentnormal_rect(p, left_x, 10, 515, 25, QColor("#1d1d1d"))
        p.setFont(self.title_font)
        p.setPen(Qt.white)
        p.drawText(px+5, 35, pw, 35, Qt.AlignLeft | Qt.AlignVCenter, f"{self.period_text()}")
        if self.state.bottom_event_active:
            self.draw_transparentnormal_rect(p, left_x, 10, 515, 25, QColor("#2a2a2a"))
            self.draw_bottom_event_text(p, left_x+5.5, 12, self.state.bottom_event_text_soccer)
        p.setFont(self.timer_font)
        p.setPen(Qt.white)
        tstring = f"{self.state.minutes_soccer}:{self.state.seconds_soccer:02d}"
        p.drawText(tx, 35, tw, 35, Qt.AlignCenter, tstring)
        logo_x=right_x+2
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
        self.draw_logo_in_top_rounded_window(p,logo_x,logo_y,logo_w,logo_h,self.state.home_logo)
        p.restore()
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
        pass
        p.end()
    def draw_logo_in_top_rounded_window(self, p, x, y, w, h, logo, radius=12):
        if logo is None or not isinstance(logo, QPixmap) or logo.isNull():
            return 
        p.save()
        p.setRenderHint(QPainter.SmoothPixmapTransform, True)
        path = QPainterPath()
        path.moveTo(x + radius, y)
        path.lineTo(x + w - radius, y)
        path.quadTo(x + w, y, x + w, y + radius)
        path.lineTo(x + w, y + h)      # flat bottom
        path.lineTo(x, y + h)
        path.lineTo(x, y + radius)
        path.quadTo(x, y, x + radius, y)
        p.setClipPath(path, Qt.IntersectClip)
        logo_scaled = logo.scaled(
            w, 9999,
        Qt.KeepAspectRatio,
        Qt.SmoothTransformation
    )
        lx = x + (w - logo_scaled.width()) // 2
        ly = y + (h - logo_scaled.height()) // 2
        p.drawPixmap(lx, ly, logo_scaled)
        p.restore()
    def clip_to_rounded_rect(self, p, x, y, w, h, radius=12):
        path = QPainterPath()
        rect = QRectF(x, y, w, h)
        path.addRoundedRect(rect, radius, radius)
        p.setClipPath(path, Qt.IntersectClip)
    def draw_bottom_event_text(self, p: QPainter, x: int, y: int, text: str):
        if not text:
            return
        w = 515
        h= 22
        p.setFont(self.event_font)
        p.setPen(Qt.white)
        p.drawText(QRect(x, y, w, h), Qt.AlignCenter, text)
    def draw_transparentnormal_rect(self, p: QPainter, x, y, w, h, color: QColor):
        p.setPen(Qt.NoPen)
        color.setAlpha(240)
        p.setBrush(QBrush(color))
        p.drawRect(QRect(int(x), int(y), int(w), int(h)))
    def draw_rect(self, p, x, y, w, h, color):
        p.setPen(Qt.NoPen)
        p.setBrush(color)
        p.drawRect(int(x), int(y), int(w), int(h))
    def period_text(self):
        p = self.state.period
    # --- regular periods ---
        if 1 <= p <= 2:
            suffix = ["1st", "2nd"][p-1]
            return f"{suffix}"
    # --- overtime periods ---
        ot_mapping = {3: "OT", 4: "2OT", 5: "PKS",}
        return ot_mapping.get(p, "")  # returns "" if period is 10+
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
# ---------- Control window ----------
class FootballControl(QMainWindow):
    def __init__(self, state: ScoreState, scoreboard: FootballScoreboard):
        super().__init__()
        self.state = state
        self.show_playclock = False
        self.td_timer = QTimer(self)
        self.td_timer.setSingleShot(True)
        self.td_timer.timeout.connect(self.end_touchdown)
        self.ui_timer = QTimer(self)
        self.ui_timer.timeout.connect(self.ui_tick)
        self.ui_timer.start(100)
        self.scoreboard = scoreboard
        self.setWindowTitle("Football Scoreboard Control "   "(Version: "f"{current_version})")
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
        score_group = QGroupBox("Score Control")
        clock_group = QGroupBox("Clock Control")
        game_group = QGroupBox("Game Control")
        system_group = QGroupBox("System")
        score_layout = QGridLayout()
        clock_layout = QGridLayout()
        game_layout = QGridLayout()
        system_layout = QVBoxLayout()

        # Assign layouts to group boxes
        score_group.setLayout(score_layout)
        clock_group.setLayout(clock_layout)
        game_group.setLayout(game_layout)
        system_group.setLayout(system_layout)
        grid.addWidget(score_group, 0, 0)
        grid.addWidget(clock_group, 0, 1)
        grid.addWidget(game_group, 1, 0)
        grid.addWidget(system_group, 1, 1)
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
        # --- FOULS (HOME) ---
        btn_nothing = QPushButton("Home Team")
        btn_nothing.clicked.connect(lambda: None)
        btn_nothing.setStyleSheet("QPushButton { background-color: #121212; color: white; }")
        score_layout.addWidget(btn_nothing, 0, 5, 1, 2)

        btn_nothing = QPushButton("Away Team")
        btn_nothing.clicked.connect(lambda: None)
        btn_nothing.setStyleSheet("QPushButton { background-color: #121212; color: white; }")
        score_layout.addWidget(btn_nothing, 0, 1, 1, 2)
        btn_away_plus6 = QPushButton("+6")
        btn_away_plus6.setStyleSheet("background-color:white; color:black;")
        btn_away_plus6.clicked.connect(lambda: self.add_points(6, "away"))
        score_layout.addWidget(btn_away_plus6, 1, 0)
        btn_away_plus3 = QPushButton("+3")
        btn_away_plus3.setStyleSheet("background-color:white; color:black;")
        btn_away_plus3.clicked.connect(lambda: self.add_points(3, "away"))
        score_layout.addWidget(btn_away_plus3, 1, 1)
        btn_away_plus2 = QPushButton("+2")
        btn_away_plus2.setStyleSheet("background-color:white; color:black;")
        btn_away_plus2.clicked.connect(lambda: self.add_points(2, "away"))
        score_layout.addWidget(btn_away_plus2, 1, 2)
        btn_away_plus1 = QPushButton("+1")
        btn_away_plus1.setStyleSheet("background-color:white; color:black;")
        btn_away_plus1.clicked.connect(lambda: self.add_points(1, "away"))
        score_layout.addWidget(btn_away_plus1, 1, 3)
        btn_home_plus6 = QPushButton("+6")
        btn_home_plus6.setStyleSheet("background-color:white; color:black;")
        btn_home_plus6.clicked.connect(lambda: self.add_points(6, "home"))
        score_layout.addWidget(btn_home_plus6, 1, 4)
        btn_home_plus3 = QPushButton("+3")
        btn_home_plus3.setStyleSheet("background-color:white; color:black;")
        btn_home_plus3.clicked.connect(lambda: self.add_points(3, "home"))
        score_layout.addWidget(btn_home_plus3, 1, 5)
        btn_home_plus2 = QPushButton("+2")
        btn_home_plus2.setStyleSheet("background-color:white; color:black;")
        btn_home_plus2.clicked.connect(lambda: self.add_points(2, "home"))
        score_layout.addWidget(btn_home_plus2, 1, 6)
        btn_home_plus1 = QPushButton("+1")
        btn_home_plus1.setStyleSheet("background-color:white; color:black;")
        btn_home_plus1.clicked.connect(lambda: self.add_points(1, "home"))
        score_layout.addWidget(btn_home_plus1, 1, 7)
        self.aw_score_box = QSpinBox()
        self.aw_score_box.setRange(0, 999)
        self.aw_score_box.setValue(self.state.away_pts)
        self.aw_score_box.hide()    # <--- hide it from UI
        self.aw_lcd = QLCDNumber()
        self.aw_lcd.setDigitCount(3)
        self.aw_lcd.setSegmentStyle(QLCDNumber.Flat)
        self.aw_lcd.setStyleSheet("""QLCDNumber { color: white;background-color: black;border: 2px solid #333;padding: 2px;}""")
        self.aw_lcd.setFixedWidth(240)  # adjust width to visually cover 4 columns
        self.aw_lcd.setFixedHeight(60)  # optional, keep it one row tall
        self.aw_lcd.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed) 
        score_layout.addWidget(self.aw_lcd, 2, 1, 1, 4)  # only one row, one column 
        self.aw_score_box.valueChanged.connect(self.aw_lcd.display)
        self.hm_score_box = QSpinBox()
        self.hm_score_box.setRange(0, 999)
        self.hm_score_box.setValue(self.state.home_pts)
        self.hm_score_box.hide()
        score_layout.addWidget(self.hm_score_box, 2, 5)
        self.hm_lcd = QLCDNumber()
        self.hm_lcd.setDigitCount(3)
        self.hm_lcd.setSegmentStyle(QLCDNumber.Flat)
        self.hm_lcd.setStyleSheet("""
        QLCDNumber { color: white;background-color: black;border: 2px solid #333;padding: 2px;}""")
        self.hm_lcd.setFixedWidth(240)
        self.hm_lcd.setFixedHeight(60)
        self.hm_lcd.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        score_layout.addWidget(self.hm_lcd, 2, 5, 1 ,4)
        btn_away_minus6 = QPushButton("-6")
        btn_away_minus6.setStyleSheet("background-color:white; color:black;")
        btn_away_minus6.clicked.connect(lambda: self.add_points(-6, "away"))
        score_layout.addWidget(btn_away_minus6, 3, 0)
        btn_away_minus3 = QPushButton("-3")
        btn_away_minus3.setStyleSheet("background-color:white; color:black;")
        btn_away_minus3.clicked.connect(lambda: self.add_points(-3, "away"))
        score_layout.addWidget(btn_away_minus3, 3, 1)
        btn_away_minus2 = QPushButton("-2")
        btn_away_minus2.setStyleSheet("background-color:white; color:black;")
        btn_away_minus2.clicked.connect(lambda: self.add_points(-2, "away"))
        score_layout.addWidget(btn_away_minus2, 3, 2)
        btn_away_minus1 = QPushButton("-1")
        btn_away_minus1.setStyleSheet("background-color:white; color:black;")
        btn_away_minus1.clicked.connect(lambda: self.add_points(-1, "away"))
        score_layout.addWidget(btn_away_minus1, 3, 3)
        btn_home_minus6 = QPushButton("-6")
        btn_home_minus6.setStyleSheet("background-color:white; color:black;")
        btn_home_minus6.clicked.connect(lambda: self.add_points(-6, "home"))
        score_layout.addWidget(btn_home_minus6, 3, 4)
        btn_home_minus3 = QPushButton("-3")
        btn_home_minus3.setStyleSheet("background-color:white; color:black;")
        btn_home_minus3.clicked.connect(lambda: self.add_points(-3, "home"))
        score_layout.addWidget(btn_home_minus3, 3, 5)
        btn_home_minus2 = QPushButton("-2")
        btn_home_minus2.setStyleSheet("background-color:white; color:black;")
        btn_home_minus2.clicked.connect(lambda: self.add_points(-2, "home"))
        score_layout.addWidget(btn_home_minus2, 3, 6)
        btn_home_minus1 = QPushButton("-1")
        btn_home_minus1.setStyleSheet("background-color:white; color:black;")
        btn_home_minus1.clicked.connect(lambda: self.add_points(-1, "home"))
        score_layout.addWidget(btn_home_minus1, 3, 7)
        btn_poss_none = QPushButton("None")
        btn_poss_none.setStyleSheet("background-color:white; color:black;")
        btn_poss_none.clicked.connect(lambda: self.set_possession_direct(None))
        game_layout.addWidget(btn_poss_none, 4, 3 ,1 ,2)
        btn_poss_away = QPushButton("Away")
        btn_poss_away.setStyleSheet("background-color:white; color:black;")
        btn_poss_away.clicked.connect(lambda: self.set_possession_direct("away"))
        game_layout.addWidget(btn_poss_away, 4, 0, 1, 3)
        btn_poss_home = QPushButton("Home")
        btn_poss_home.setStyleSheet("background-color:white; color:black;")
        btn_poss_home.clicked.connect(lambda: self.set_possession_direct("home"))
        game_layout.addWidget(btn_poss_home, 4, 5, 1, 3)
        btn_nothing = QPushButton("Timeouts Left")
        btn_nothing.clicked.connect(lambda: None)
        btn_nothing.setStyleSheet("QPushButton { background-color: #121212; color: white; }")
        game_layout.addWidget(btn_nothing, 5, 3, 1, 2)
        self.away_to_lcd = QLCDNumber()
        self.away_to_lcd.setDigitCount(1)
        self.away_to_lcd.setSegmentStyle(QLCDNumber.Flat)
        self.away_to_lcd.display(self.state.away_timeouts)
        self.away_to_lcd.setStyleSheet("""QLCDNumber { color: white;background-color: black;border: 2px solid #333;padding: 2px;}""")
        game_layout.addWidget(self.away_to_lcd, 5, 1, 1, 1)
        btn_away_use = QPushButton("-")
        btn_away_use.clicked.connect(lambda: self.change_timeout("away", -1))
        btn_away_use.setStyleSheet("background-color:white; color:black;")
        game_layout.addWidget(btn_away_use, 5,0)
        btn_away_restore = QPushButton("+")
        btn_away_restore.clicked.connect(lambda: self.change_timeout("away", +1))
        btn_away_restore.setStyleSheet("background-color:white; color:black;")
        game_layout.addWidget(btn_away_restore, 5, 2)
        self.home_to_lcd = QLCDNumber()
        self.home_to_lcd.setDigitCount(1)
        self.home_to_lcd.setSegmentStyle(QLCDNumber.Flat)
        self.home_to_lcd.display(self.state.home_timeouts)
        self.home_to_lcd.setStyleSheet("""QLCDNumber { color: white;background-color: black;border: 2px solid #333;padding: 2px;}""")
        game_layout.addWidget(self.home_to_lcd, 5, 6, 1, 1)
        btn_home_use = QPushButton("-")
        btn_home_use.setStyleSheet("background-color:white; color:black;")
        btn_home_use.clicked.connect(lambda: self.change_timeout("home", -1))
        game_layout.addWidget(btn_home_use, 5, 5)
        btn_home_restore = QPushButton("+")
        btn_home_restore.setStyleSheet("background-color:white; color:black;")
        btn_home_restore.clicked.connect(lambda: self.change_timeout("home", +1))
        game_layout.addWidget(btn_home_restore, 5, 7)
        self.time_lcd = QLCDNumber()
        self.time_lcd.setDigitCount(5)  # MM:SS
        self.time_lcd.setSegmentStyle(QLCDNumber.Flat)
        self.time_lcd.display(f"{self.state.minutes:02d}:{self.state.seconds:02d}")
        self.time_lcd.setStyleSheet("""QLCDNumber { color: white;background-color: black;border: 2px solid #333;padding: 2px;}""")
        clock_layout.addWidget(self.time_lcd, 6, 1, 1, 1)
        self.min_edit = QSpinBox()
        self.min_edit.setRange(0, 90)
        self.min_edit.setValue(self.state.minutes)
        self.min_edit.setFixedWidth(60)
        self.min_edit.setStyleSheet("background-color:white; color:black;")
        self.min_edit.editingFinished.connect(self.set_lcd_clock_from_inputs)
        clock_layout.addWidget(self.min_edit, 6, 5)
        self.sec_edit = QSpinBox()
        self.sec_edit.setRange(0, 59)
        self.sec_edit.setValue(self.state.seconds)
        self.sec_edit.setFixedWidth(60)
        self.sec_edit.setStyleSheet("background-color:white; color:black;")
        self.sec_edit.editingFinished.connect(self.set_lcd_clock_from_inputs)
        clock_layout.addWidget(self.sec_edit, 6, 6)
        btn_set_clock = QPushButton("Set")
        btn_set_clock.setStyleSheet("background-color:white; color:black;")
        btn_set_clock.clicked.connect(self.set_lcd_clock_from_inputs)
        clock_layout.addWidget(btn_set_clock, 6, 7)
        btn_start = QPushButton("Start Clock")
        btn_start.clicked.connect(self.start_clock)
        btn_start.setStyleSheet("background-color:white; color:black;")
        clock_layout.addWidget(btn_start, 6, 0)
        btn_stop = QPushButton("Stop Clock")
        btn_stop.clicked.connect(self.stop_clock)
        btn_stop.setStyleSheet("background-color:white; color:black;")
        clock_layout.addWidget(btn_stop, 6, 2)
        btn_reset = QPushButton("Reset Clock")
        btn_reset.setStyleSheet("background-color:white; color:black;")
        btn_reset.clicked.connect(self.reset_clock)
        clock_layout.addWidget(btn_reset, 6, 3)
        self.pc_spin = QSpinBox()
        self.pc_spin.setRange(0, 99)
        self.pc_spin.setValue(self.state.playclock)
        self.pc_spin.setStyleSheet("background-color:white; color:black;")
        clock_layout.addWidget(self.pc_spin, 7, 1)
        btn_pc = QPushButton("PC Time")
        btn_pc.setStyleSheet("background-color:white; color:black;")
        btn_pc.clicked.connect(lambda: self.toggle_playclock_preset(btn_pc))
        clock_layout.addWidget(btn_pc, 7, 4)
        btn_start = QPushButton("Start Play Clock")
        btn_start.clicked.connect(self.start_play_clock)
        btn_start.setStyleSheet("background-color:white; color:black;")
        clock_layout.addWidget(btn_start, 7, 0)
        btn_stop = QPushButton("Stop Play Clock")
        btn_stop.setStyleSheet("background-color:white; color:black;")
        btn_stop.clicked.connect(self.stop_play_clock)
        clock_layout.addWidget(btn_stop, 7, 2)
        btn_reset = QPushButton("Reset Play Clock")
        btn_reset.setStyleSheet("background-color:white; color:black;")
        btn_reset.clicked.connect(self.reset_play_clock)
        clock_layout.addWidget(btn_reset, 7, 3)
        btn_nothing = QPushButton("<- Down | Distance ->")
        btn_nothing.clicked.connect(lambda: None)
        btn_nothing.setStyleSheet("QPushButton { background-color: #121212; color: white; }")
        game_layout.addWidget(btn_nothing, 8, 3, 1, 2)
        self.down_spin = QComboBox()
        self.down_spin.addItems(["1", "2", "3", "4" ,""])
        self.down_spin.setCurrentText(str(self.state.down))
        self.down_spin.setStyleSheet("background-color:white; color:black;")
        game_layout.addWidget(self.down_spin, 8, 0, 1, 3)
        self.dist_edit = QComboBox()
        self.dist_edit.setStyleSheet("background-color:white; color:black;")
        self.dist_edit.setEditable(True)
        self.dist_edit.addItems(["Down", "Goal", "1", "2", "3", "4", "5", "7", "10", "Inches","Final", "Final/OT" ,"HALFTIME", ""])
        self.dist_edit.setCurrentText(str(self.state.distance))
        game_layout.addWidget(self.dist_edit, 8, 5, 1, 2)
        btn_set_dd = QPushButton("Set Down/Distance")
        btn_set_dd.clicked.connect(self.set_down_distance)
        btn_set_dd.setStyleSheet("background-color:white; color:black;")
        game_layout.addWidget(btn_set_dd, 8, 7, 1, 1)
        self.period_spin = QSpinBox()
        self.period_spin.setRange(1, 10)
        self.period_spin.setValue(self.state.period)
        self.period_spin.setStyleSheet("background-color:white; color:black;")
        game_layout.addWidget(self.period_spin, 9, 0)
        btn_set_period = QPushButton("Set Period")
        btn_set_period.setStyleSheet("background-color:white; color:black;")
        btn_set_period.clicked.connect(self.set_period)
        game_layout.addWidget(btn_set_period, 9, 1)
        btn_2pt = QPushButton("2PT Attempt")
        btn_2pt.setStyleSheet("background-color:white; color:black;")
        btn_2pt.clicked.connect(self.on_2pt_clicked)
        game_layout.addWidget(btn_2pt, 9, 3)
        btn_fg = QPushButton("Field Goal")
        btn_fg.setStyleSheet("background-color:white; color:black;")
        btn_fg.clicked.connect(self.on_fg_clicked)
        game_layout.addWidget(btn_fg, 9, 4)
        self.btn_remove_event = QPushButton("Remove Event")
        self.btn_remove_event.clicked.connect(self.on_remove_event)
        self.btn_remove_event.setStyleSheet("background-color:white; color:black;")
        game_layout.addWidget(self.btn_remove_event, 9, 5)
        btn_serial = QPushButton("Serial Connection")
        btn_serial.clicked.connect(self.on_serial_button_clicked)
        btn_serial.setStyleSheet("background-color:white; color:black;")
        system_layout.addWidget(btn_serial, 9, 6)
        self.flag_button = QPushButton("Flag")
        self.flag_button.setStyleSheet("background-color:white; color:black;")
        self.flag_button.clicked.connect(self.toggle_flag)
        game_layout.addWidget(self.flag_button, 9, 2)
        self.timer = QTimer()
        self.timer.setInterval(1000)  # 1 sec
        self.timer.timeout.connect(self.game_tick)
        self.play_timer = QTimer()
        self.play_timer.setInterval(1000)
        self.play_timer.timeout.connect(self.play_tick)
        #- ----------------- PAGE 2: Away Setup -----------------
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
        lbl = QLabel("Away Team Rank:")
        lbl.setStyleSheet("color:white;")
        grid_away.addWidget(lbl, 1, 3)
        self.away_rank_edit = QLineEdit()
        self.away_rank_edit.setText(str(self.state.away_rank or ""))
        self.away_rank_edit.setStyleSheet("background-color:white; color:black;")
        validator = QIntValidator(0, 25, self)
        self.away_rank_edit.setValidator(validator)
        grid_away.addWidget(self.away_rank_edit, 1, 4)
        lbl = QLabel("Away Mascot:")
        lbl.setStyleSheet("color:white;")
        grid_away.addWidget(lbl, 2, 2)
        self.away_setup_mascot = QLineEdit(self.state.away_mascot)
        self.away_setup_mascot.setStyleSheet("background-color:white; color:black;")
        grid_away.addWidget(self.away_setup_mascot, 2, 3)
        btn = QPushButton("Submit")
        btn.setStyleSheet("background-color:white; color:black;")
        btn.clicked.connect(self.submit_away_setup)
        grid_away.addWidget(btn, 2, 4)
        btn = QPushButton("Submit")
        btn.setStyleSheet("background-color:white; color:black;")
        btn.clicked.connect(self.submit_away_setup)
        grid_away.addWidget(btn, 1, 5)
        lbl = QLabel("Away Team Color:")
        lbl.setStyleSheet("color:white;")
        grid_away.addWidget(lbl, 2, 0)
        btn = QPushButton("🎨")
        btn.setStyleSheet("background-color:white; color:black;")
        btn.clicked.connect(self.pick_away_color_from_setup)
        grid_away.addWidget(btn, 2, 1)
        lbl = QLabel("Away Team Logo:")
        lbl.setStyleSheet("color:white;")
        grid_away.addWidget(lbl, 3, 0)
        btn = QPushButton("🖼")
        btn.setStyleSheet("background-color:white; color:black;")
        btn.clicked.connect(self.load_away_logo_from_setup)
        grid_away.addWidget(btn, 3, 1)
        lbl = QLabel("Away Team Record:")
        lbl.setStyleSheet("color:white;")
        grid_away.addWidget(lbl, 4, 0)
        self.away_record_wins_edit = QLineEdit(str(self.state.away_record_wins))
        self.away_record_wins_edit.setStyleSheet("background-color:white; color:black;")
        self.away_record_losses_edit = QLineEdit(str(self.state.away_record_losses))
        self.away_record_losses_edit.setStyleSheet("background-color:white; color:black;")
        grid_away.addWidget(self.away_record_wins_edit, 4, 1)
        grid_away.addWidget(self.away_record_losses_edit, 4, 2)
        btn = QPushButton("Submit")
        btn.setStyleSheet("background-color:white; color:black;")
        btn.clicked.connect(self.submit_away_setup)
        grid_away.addWidget(btn, 4, 3)
        lbl = QLabel("Away District Record:")
        lbl.setStyleSheet("color:white;")
        grid_away.addWidget(lbl, 5, 0)
        self.away_district_wins_edit = QLineEdit(str(self.state.away_district_wins))
        self.away_district_wins_edit.setStyleSheet("background-color:white; color:black;")
        self.away_district_losses_edit = QLineEdit(str(self.state.away_district_losses))
        self.away_district_losses_edit.setStyleSheet("background-color:white; color:black;")
        grid_away.addWidget(self.away_district_wins_edit, 5, 1)
        grid_away.addWidget(self.away_district_losses_edit, 5, 2)
        btn = QPushButton("Submit")
        btn.setStyleSheet("background-color:white; color:black;")
        btn.clicked.connect(self.submit_away_setup)
        grid_away.addWidget(btn, 5, 3)   

        # ----------------- PAGE 3: Home Setup -----------------
        self.chk_district = QCheckBox("District Opponent")
        self.chk_district.setChecked(False)
        self.chk_district.stateChanged.connect(self.update_district_flag)
        self.chk_district.setStyleSheet("QCheckBox{color:white;} QCheckBox::indicator{width:15px;height:15px;border:2px solid white;background:#121212;} QCheckBox::indicator:checked{background:white;}")
        grid_info.addWidget(self.chk_district, 5, 0, 1 , 5)
        grid_home.addWidget(QLabel("<b>Home Team Setup</b>"), -4, 0)
        lbl = QLabel("Enter Home Name:")
        lbl.setStyleSheet("color:white;")
        grid_home.addWidget(lbl, 0, 0)
        self.home_setup_name = QLineEdit(self.state.home_name)
        self.home_setup_name.setStyleSheet("background-color:white; color:black;")
        grid_home.addWidget(self.home_setup_name, 0, 1)
        btn = QPushButton("Submit")
        btn.setStyleSheet("background-color:white; color:black;")
        btn.clicked.connect(self.submit_home_setup)
        grid_home.addWidget(btn, 0, 2)
        lbl = QLabel("Home Team Rank:")
        lbl.setStyleSheet("color:white;")
        grid_home.addWidget(lbl, 0, 3)
        self.home_rank_edit = QLineEdit()
        self.home_rank_edit.setText(str(self.state.home_rank or ""))
        self.home_rank_edit.setStyleSheet("background-color:white; color:black;")
        validator = QIntValidator(0, 25, self)
        self.home_rank_edit.setValidator(validator)
        grid_home.addWidget(self.home_rank_edit, 0, 4)
        btn = QPushButton("Submit")
        btn.setStyleSheet("background-color:white; color:black;")
        btn.clicked.connect(self.submit_home_setup)
        grid_home.addWidget(btn, 0, 5)
        lbl = QLabel("Home Mascot:")
        lbl.setStyleSheet("color:white;")
        grid_home.addWidget(lbl, 1, 2)
        self.home_setup_mascot = QLineEdit(self.state.home_mascot)
        self.home_setup_mascot.setStyleSheet("background-color:white; color:black;")
        grid_home.addWidget(self.home_setup_mascot, 1, 3)
        btn = QPushButton("Submit")
        btn.setStyleSheet("background-color:white; color:black;")
        btn.clicked.connect(self.submit_home_setup)
        grid_home.addWidget(btn, 1, 4)
        lbl = QLabel("Home Team Color:")
        lbl.setStyleSheet("color:white;")
        grid_home.addWidget(lbl, 1, 0)
        btn = QPushButton("🎨")
        btn.setStyleSheet("background-color:white; color:black;")
        btn.clicked.connect(self.pick_home_color_from_setup)
        grid_home.addWidget(btn, 1, 1)
        lbl = QLabel("Home Team Logo:")
        lbl.setStyleSheet("color:white;")
        grid_home.addWidget(lbl, 2, 0)
        btn = QPushButton("🖼")
        btn.setStyleSheet("background-color:white; color:black;")
        btn.clicked.connect(self.load_home_logo_from_setup)
        grid_home.addWidget(btn, 2, 1)
        lbl = QLabel("Home Team Record:")
        lbl.setStyleSheet("color:white;")
        grid_home.addWidget(lbl, 3, 0)
        self.home_record_wins_edit = QLineEdit(str(self.state.home_record_wins))
        self.home_record_wins_edit.setStyleSheet("background-color:white; color:black;")
        self.home_record_losses_edit = QLineEdit(str(self.state.home_record_losses))
        self.home_record_losses_edit.setStyleSheet("background-color:white; color:black;")
        grid_home.addWidget(self.home_record_wins_edit, 3, 1)
        grid_home.addWidget(self.home_record_losses_edit, 3, 2)
        btn = QPushButton("Submit")
        btn.setStyleSheet("background-color:white; color:black;")
        btn.clicked.connect(self.submit_home_setup)
        grid_home.addWidget(btn, 3, 3)
        lbl = QLabel("Home District Record:")
        lbl.setStyleSheet("color:white;")
        grid_home.addWidget(lbl, 4, 0)
        self.home_district_wins_edit = QLineEdit(str(self.state.home_district_wins))
        self.home_district_wins_edit.setStyleSheet("background-color:white; color:black;")
        self.home_district_losses_edit = QLineEdit(str(self.state.home_district_losses))
        self.home_district_losses_edit.setStyleSheet("background-color:white; color:black;")
        grid_home.addWidget(self.home_district_wins_edit, 4, 1)
        grid_home.addWidget(self.home_district_losses_edit, 4, 2)
        btn = QPushButton("Submit")
        btn.setStyleSheet("background-color:white; color:black;")
        btn.clicked.connect(self.submit_home_setup)
        grid_home.addWidget(btn, 4, 3)

        # ------  PAGE 4 Buttons ------
        grid_info.addWidget(QLabel("hehe"),-1,0)
        lbl = QLabel("Graphics:")
        lbl.setStyleSheet("color:white;")
        grid_info.addWidget(lbl, 3, 0)
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
        lbl = QLabel("Event Location:")
        lbl.setStyleSheet("color:white;")
        grid_info.addWidget(lbl, 1, 0)
        self.event_location_edit = QLineEdit()
        self.event_location_edit.setPlaceholderText("Enter school / event text...")
        self.event_location_edit.setStyleSheet("background-color:white; color:black;")
        grid_info.addWidget(self.event_location_edit, 1, 1)
        self.event_city_edit = QLineEdit()
        self.event_city_edit.setPlaceholderText("Enter city...")
        self.event_city_edit.setStyleSheet("background-color:white; color:black;")
        grid_info.addWidget(self.event_city_edit, 1, 2)
        btn = QPushButton("Submit")
        btn.setStyleSheet("background-color:white; color:black;")
        btn.clicked.connect(self.submit_event_location)
        grid_info.addWidget(btn, 1, 3)
        lbl = QLabel("Event Info:")
        lbl.setStyleSheet("color:white;")
        grid_info.addWidget(lbl, 2, 0)
        self.bottom_event_edit = QLineEdit()
        self.bottom_event_edit.setPlaceholderText("Enter event info text...")
        self.bottom_event_edit.setStyleSheet("background-color:white; color:black;")
        grid_info.addWidget(self.bottom_event_edit, 2, 1, 1, 2)
        btn = QPushButton("Submit")
        btn.setStyleSheet("background-color:white; color:black;")
        btn.clicked.connect(self.submit_bottom_event)
        grid_info.addWidget(btn, 2, 3)
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
    def submit_event_location(self):
        school_text = self.event_location_edit.text().strip()
        city_text = self.event_city_edit.text().strip()
        self.state.event_location_school_text = school_text or ""
        self.state.event_location_city_text = city_text or ""

        self.repaint_scoreboard()
    def submit_bottom_event(self):
        text = self.bottom_event_edit.text().strip()
        self.state.bottom_event_text_football = text or ""
        self.state.bottom_event_active = bool(text)
        self.repaint_scoreboard()
    def toggle_playclock_preset(self, btn):
        v, ok = QInputDialog.getItem(self,"Set Play Clock","Select play clock:",["25","40"],False)
        if ok:
            self.quick_set_playclock(int(v))


    def toggle_flag(self):
        self.state.flag = not self.state.flag
        self.repaint_scoreboard()
    def show_intro(self, force_double=False):
        first_group=[
        ("saway_box",-1),
        ("shome_box",-1),
        ("faway_box",-1),
        ("fhome_box",-1),
        ("cfinal_box",-1),
        ("centerbreak",-1)
    ]
        second_group=[
        ("centerintro",1),
        ("homeintro",1),
        ("awayintro",1)
    ]
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
    def show_breakboard(self, force_double=False):
        first_group=[
        ("saway_box",-1),
        ("shome_box",-1),
        ("faway_box",-1),
        ("fhome_box",-1),
        ("cfinal_box",-1),
        ("centerintro",-1),
        ("homeintro",-1),
        ("awayintro",-1)
    ]
        second_group=[
        ("centerbreak",1)
    ]
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
    def show_scorebug(self, force_double=False):
        first_group=[("faway_box",-1),("fhome_box",-1),("cfinal_box", -1),("centerintro",-1),("homeintro",-1),("awayintro",-1),("centerbreak",-1)]
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
    def show_final(self, force_double=False):
        first_group=[("saway_box",-1),("shome_box",-1),("centerintro",-1),("homeintro",-1),("awayintro",-1),("centerbreak",-1)]
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
    def on_fg_clicked(self):
        team, ok = QInputDialog.getItem(self,"Select Team","Which team?",["Home", "Away"],editable=False)
        if ok:
            if (yards := QInputDialog.getInt(
                self,
                f"{team} Field Goal","Enter yards for attempt:",0,0,99)[0]):
                if team == "Home":
                    self.trigger_home_event(f"{yards} Yard Attempt")
                else:
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
        if (not self.state.saway_box_active and not self.state.saway_box_animating and
            not self.state.shome_box_active and not self.state.shome_box_animating and 
            not self.state.faway_box_active and not self.state.faway_box_animating and
            not self.state.cfinal_box_active and not self.state.cfinal_box_animating and
            not self.state.centerbreak_active and not self.state.centerbreak_animating):
            if not self.scoreboard.show_intro:
                self.scoreboard.show_intro = True
                self.scoreboard.show_breakboard = False
                self.scoreboard.show_scorebug = False
                self.scoreboard.show_football_final = False
        if (not self.state.saway_box_active and not self.state.saway_box_animating and
            not self.state.shome_box_active and not self.state.shome_box_animating and 
            not self.state.faway_box_active and not self.state.faway_box_animating and
            not self.state.cfinal_box_active and not self.state.cfinal_box_animating and
            not self.state.centerintro_active and not self.state.centerintro_animating and
            not self.state.homeintro_active and not self.state.homeintro_animating and 
            not self.state.awayintro_active and not self.state.awayintro_animating):
            if not self.scoreboard.show_breakboard:
                self.scoreboard.show_intro = False
                self.scoreboard.show_breakboard = True
                self.scoreboard.show_scorebug = False
                self.scoreboard.show_football_final = False
        if (not self.state.faway_box_active and not self.state.faway_box_animating and
            not self.state.cfinal_box_active and not self.state.cfinal_box_animating and
            not self.state.centerintro_active and not self.state.centerintro_animating and
            not self.state.homeintro_active and not self.state.homeintro_animating and 
            not self.state.awayintro_active and not self.state.awayintro_animating and 
            not self.state.centerbreak_active and not self.state.centerbreak_animating):
            if not self.scoreboard.show_scorebug:
                self.scoreboard.show_intro = False
                self.scoreboard.show_breakboard = False
                self.scoreboard.show_scorebug = True
                self.scoreboard.show_football_final = False
        if (not self.state.saway_box_active and not self.state.saway_box_animating and
            not self.state.shome_box_active and not self.state.shome_box_animating and
            not self.state.centerintro_active and not self.state.centerintro_animating and
            not self.state.homeintro_active and not self.state.homeintro_animating and 
            not self.state.awayintro_active and not self.state.awayintro_animating and 
            not self.state.centerbreak_active and not self.state.centerbreak_animating):
            if not self.scoreboard.show_football_final:
                self.scoreboard.show_intro = False
                self.scoreboard.show_breakboard = False
                self.scoreboard.show_scorebug = False
                self.scoreboard.show_football_final = True
        if changed:
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
        self.update()
    def add_points(self, pts, team):
        if team == "home":
            self.state.home_pts = max(0, self.state.home_pts + pts)
        else:
            self.state.away_pts = max(0, self.state.away_pts + pts)
        self.hm_score_box.setValue(self.state.home_pts)
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

        # Only show popup when timeouts DECREASE
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

        # Only show popup when timeouts DECREASE
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

        # --- HIGH QUALITY SCALING ---
            pm = pm.scaled(
            60, 100,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation  # <-- Best quality resampling
        )

        # Make sure it's ARGB32 for blending & clipping correctly
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

    # --- one-time rule for first period 3 set ---
        if new_period == 3 and not getattr(self, 'period_timeout_applied', False):
            self.state.home_timeouts = 3
            self.state.away_timeouts = 3  # mirror home if desired
            self.state.period_timeout_applied = True  # lock it out

    # --- reset game clock ---
        if 1 <= new_period <= 4:  # regular periods
            self.state.minutes = 12
        else:  # overtime periods
            self.state.minutes = 0  # typical OT length, adjust if needed
            self.state.seconds = 0
        if new_period == 10:
            self.state.minutes = 20  # typical OT length, adjust if needed
            self.state.seconds = 0            
         
        if hasattr(self, "time_lcd"):
            self.time_lcd.display(f"{self.state.minutes:02d}:{self.state.seconds:02d}")

    # --- update timeout LCDs ---
        if hasattr(self, "home_to_lcd"):
            self.home_to_lcd.display(self.state.home_timeouts)
        if hasattr(self, "away_to_lcd"):
            self.away_to_lcd.display(self.state.away_timeouts)

    # --- refresh scoreboard ---
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
            return self.state.minutes, self.state.seconds
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
        self.state.minutes = m
        self.state.seconds = s

    # update LCD
        if hasattr(self, "time_lcd"):
            self.time_lcd.display(f"{m:02d}:{s:02d}")

    # optional scoreboard redraw
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
        self.state.playclock = int(self.pc_spin.value())
        self.repaint_scoreboard()


    def game_tick(self):
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

    # update LCD + fields
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

class BasketballControl(QMainWindow):
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
        self.setWindowTitle("Basketball Scoreboard Control "   "(Version: "f"{current_version})")
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
        if hasattr(self, "time_lcd"):
            self.time_lcd.display("08:00")

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
class VolleyballControl(QMainWindow):
    def __init__(self, state: ScoreState, scoreboard: VolleyballScoreboard):
        super().__init__()
        self.state = state
        self.title_font = QFont("BigNoodleTitling", 20, QFont.Bold)
        self.scoreboard = scoreboard
        self.setWindowTitle("Volleyball Scoreboard  "   "(Version: "f"{current_version})")
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
        self.state.serial_thread = ScoreboardReader(self.state,parsers=[DaktronicsParser(), NevcoParser(), FairPlayParser()])
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
class SoccerControl(QMainWindow):
    def __init__(self, state: ScoreState, scoreboard: SoccerScoreboard):
        super().__init__()
        self.state = state
        self.goal_timer = QTimer(self)
        self.goal_timer.setSingleShot(True)
        self.goal_timer.timeout.connect(self.end_goal)
        #self.ui_timer = QTimer(self)
        #self.ui_timer.timeout.connect(self.ui_tick)
        #self.ui_timer.start(100)
        self.scoreboard = scoreboard
        self.setWindowTitle("Soccer Scoreboard Control "   "(Version: "f"{current_version})")
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
        grid_info.addWidget(QLabel("Event Info:"), 2, 0)
        self.bottom_event_edit = QLineEdit()
        self.bottom_event_edit.setPlaceholderText("Enter event info text...")
        grid_info.addWidget(self.bottom_event_edit, 2, 1, 1, 2)  # QLineEdit
        btn_bottom_event_submit = QPushButton("Submit")
        btn_bottom_event_submit.clicked.connect(self.submit_bottom_event)
        grid_info.addWidget(btn_bottom_event_submit, 2, 3)
        def style_children(w):
            for c in w.findChildren(QWidget):
                if not isinstance(c, QLCDNumber):
                    c.setStyleSheet("QLabel{color:white;} QPushButton,QLineEdit,QSpinBox,QCheckBox{background:white;color:black;} QCheckBox::indicator{background:white;}")

        style_children(page1)
        style_children(page2)
        style_children(page3)
        style_children(page4)
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



    #def show_intro(self):
        #self.scoreboard.show_intro = True
        #self.scoreboard.show_breakboard = False
        #self.scoreboard.show_scorebug = False
        #self.scoreboard.show_football_final = False
        #self.scoreboard.update()
    #def show_breakboard(self):
        #if self.state.saway_box_active and not self.state.saway_box_animating:
            #self.state.saway_box_animating = True
            #self.state.saway_box_direction = -1
            #self.state.saway_box_start_time = time.time()
        #if self.state.shome_box_active and not self.state.shome_box_animating:
            #self.state.shome_box_animating = True
            #self.state.shome_box_direction = -1
            #self.state.shome_box_start_time = time.time()
            #self.scoreboard.update()
    #def show_scorebug(self):
        #self.scoreboard.show_intro = False
        #self.scoreboard.show_breakboard = False
        #self.scoreboard.show_scorebug = True
        #self.scoreboard.show_football_final = False
        #self.state.saway_box_active = True
        #self.state.saway_box_animating = True
        #self.state.saway_box_direction = 1
        #self.state.saway_box_progress = 0.0
        #self.state.saway_box_start_time = time.time()
        #self.state.shome_box_active = True
        #self.state.shome_box_animating = True
        #self.state.shome_box_direction = 1
        #self.state.shome_box_progress = 0.0
        #self.state.shome_box_start_time = time.time()
        #self.scoreboard.update()
    def show_final(self):
        if self.state.saway_box_active and not self.state.saway_box_animating:
            self.state.saway_box_animating = True
            self.state.saway_box_direction = -1
            self.state.saway_box_start_time = time.time()
        if self.state.shome_box_active and not self.state.shome_box_animating:
            self.state.shome_box_animating = True
            self.state.shome_box_direction = -1
            self.state.shome_box_start_time = time.time()
        self.state.cfinal_box_active = True
        self.state.cfinal_box_animating = True
        self.state.cfinal_box_progress = 0.0
        self.state.cfinal_box_start_time = time.time()
        self.state.cfinal_box_direction = 1
        self.state.faway_box_active = True
        self.state.faway_box_animating = True
        self.state.faway_box_direction = 1
        self.state.faway_box_progress = 0.0
        self.state.faway_box_start_time = time.time()
        self.state.fhome_box_active = True
        self.state.fhome_box_animating = True
        self.state.fhome_box_direction = 1
        self.state.fhome_box_progress = 0.0
        self.state.fhome_box_start_time = time.time()
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
        # Store old scores to detect change
        old_home_pts = self.state.home_pts
        old_away_pts = self.state.away_pts

        # Update scores based on team (still needed for scoreboard logic)
        if team == "home":
            self.state.home_pts = max(0, self.state.home_pts + pts)
        else:
            self.state.away_pts = max(0, self.state.away_pts + pts)

        # Update score boxes
        self.hm_score_box.setValue(self.state.home_pts)
        self.aw_score_box.setValue(self.state.away_pts)

        # Trigger goal animations based on which score increased
        if self.state.home_pts > old_home_pts:
            self.start_home_goal()  # home goal triggered by score change

        if self.state.away_pts > old_away_pts:
            self.start_away_goal()  # away goal triggered by score change

        # Refresh scoreboard
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
        path, _ = QFileDialog.getOpenFileName(
        self,
        "Open home logo",
        "",
        "Images (*.png *.jpg *.jpeg *.bmp *.webp)"
    )

        if path:
            pm = QPixmap()
            pm.load(path)

        # --- HIGH QUALITY SCALING ---
            pm = pm.scaled(
            60, 100,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation  # <-- Best quality resampling
        )

        # Make sure it's ARGB32 for blending & clipping correctly
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
            return self.state.minutes_soccer, self.state.seconds_soccer
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
        self.state.minutes_soccer = m
        self.state.seconds_soccer = s

    # update LCD
        if hasattr(self, "time_lcd"):
            self.time_lcd.display(f"{m:02d}:{s:02d}")

    # optional scoreboard redraw
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

        if hasattr(self, "time_lcd"):
            self.time_lcd.display("40:00")

        if hasattr(self, "min_edit"):
            self.min_edit.setValue(self.state.minutes_soccer)
        if hasattr(self, "sec_edit"):
            self.sec_edit.setValue(self.state.seconds_soccer)

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

    # update LCD + fields
        self.time_lcd.display(f"{self.state.minutes_soccer}:{self.state.seconds_soccer:02d}")
        self.min_edit.setValue(self.state.minutes_soccer)
        self.sec_edit.setValue(self.state.seconds_soccer)

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
class ProgramSelector(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Streaming Program")

        layout = QVBoxLayout(self)

        # Combo box for program selection
        self.combo = QComboBox()
        self.combo.addItems(["OBS/Streamlabs", "vMix"])
        layout.addWidget(self.combo)

        # OK button
        btn = QPushButton("OK")
        btn.clicked.connect(self.on_ok)
        layout.addWidget(btn)

        # Store selection
        self.selection = None

    def on_ok(self):
        # Save the selected program
        self.selection = self.combo.currentText()
        self.accept()
class WindowModeSelector(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Window Mode")

        layout = QVBoxLayout(self)

        self.combo = QComboBox()
        self.combo.addItem("Frameless (Broadcast Overlay)")
        self.combo.addItem("Framed (Normal Window)")

        layout.addWidget(QLabel("Select window style:"))
        layout.addWidget(self.combo)

        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        layout.addWidget(ok_btn)

    def get_mode(self):
        return "frameless" if self.combo.currentIndex() == 0 else "framed"

class ScoreboardSelector(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Select Scoreboard")

        layout = QVBoxLayout(self)

        # --- Drop-down for scoreboard selection ---
        self.combo = QComboBox()
        self.combo.addItems(["Football", "Basketball", "Volleyball", "Soccer"])
        self.combo.setCurrentIndex(-1)  # No default selected
        layout.addWidget(self.combo)

        # --- OK button ---
        btn = QPushButton("OK")
        btn.clicked.connect(self.on_ok)
        layout.addWidget(btn)

        self.selection = None

    def on_ok(self):
        # Validate selection
        if self.combo.currentIndex() == -1:
            QMessageBox.critical(self, "Error", "You must select a scoreboard.")
            return  # Don't close
        self.selection = self.combo.currentText()
        self.accept()

    def get_selection(self):
        return self.selection
class ScoreboardParser:
    def parse(self, raw_bytes):
        raise NotImplementedError

class DaktronicsParser(ScoreboardParser):
    def parse(self, raw_bytes):
        try:
            txt = raw_bytes.decode(errors="ignore").strip()
            txt = txt.strip('\x02\x03')
            if len(txt) < 14: return None

            away = int(txt[7:9])
            home = int(txt[9:11])

            # Parse clock with optional tenths: MM:SS.t
            clock = txt[0:6]  # e.g., "12:34.5"
            if '.' in clock:
                mm_ss, t = clock.split('.')
                mm, ss = mm_ss.split(':')
                tenths = int(t)
            else:
                mm, ss = clock.split(':')
                tenths = 0

            period = int(txt[11])
            poss = 'home' if 'L' in txt else 'away' if 'R' in txt else None
            home_to = int(txt[-2]) if txt[-2].isdigit() else 0
            away_to = int(txt[-1]) if txt[-1].isdigit() else 0

            return {
                'away_pts': away,
                'home_pts': home,
                'minutes': int(mm),
                'seconds': int(ss),
                'tenths': tenths,
                'period': period,
                'possession': poss,
                'home_to': home_to,
                'away_to': away_to
            }
        except:
            return None

class NevcoParser(ScoreboardParser):
    def parse(self, raw_bytes):
        try:
            txt=raw_bytes.decode(errors="ignore").strip()
            if not txt.startswith("N") or len(txt)<10:return None
            home=int(txt[1:3]);away=int(txt[3:5])
            mm=int(txt[5:7]);ss=int(txt[7:9])
            period=int(txt[9]);poss=None;home_to=away_to=0
            return {'away_pts':away,'home_pts':home,'minutes':mm,'seconds':ss,'period':period,'possession':poss,'home_to':home_to,'away_to':away_to}
        except:
            return None

class FairPlayParser(ScoreboardParser):
    def parse(self, raw_bytes):
        try:
            txt=raw_bytes.decode(errors="ignore").strip()
            if not txt.startswith("FP") or len(txt)<12:return None
            home=int(txt[2:4]);away=int(txt[4:6])
            mm=int(txt[6:8]);ss=int(txt[8:10])
            period=int(txt[10]);poss=None;home_to=away_to=0
            return {'away_pts':away,'home_pts':home,'minutes':mm,'seconds':ss,'period':period,'possession':poss,'home_to':home_to,'away_to':away_to}
        except:
            return None

class ScoreboardReader(threading.Thread):
    def __init__(self,state,parsers=None):
        super().__init__(daemon=True)
        self.state=state
        self.running=False
        self.ser=None
        self.parser=None
        self.parsers=parsers or [DaktronicsParser(),NevcoParser(),FairPlayParser()]

    def auto_detect_port(self):
        ports=serial.tools.list_ports.comports()
        for port in ports:
            try:
                serial.Serial(port.device,self.state.serial_baud,timeout=0.05).close()
                return port.device
            except: continue
        return None

    def open_port(self):
        port=getattr(self.state,"serial_port",None) or self.auto_detect_port()
        if not port: self.running=False; return
        try: self.ser=serial.Serial(port,self.state.serial_baud,timeout=0.05); self.running=True
        except: self.running=False

    def stop(self):
        self.running=False
        if self.ser:
            try: self.ser.close()
            except: pass

    def detect_parser(self,msg):
        for p in self.parsers:
            try:
                if p.parse(msg): return p
            except: continue
        return None

    def run(self):
        self.open_port()
        if not self.running: return
        buf=b""
        while self.running:
            try:
                data=self.ser.read(128)
                if not data: continue
                buf += data
                while b"\x02" in buf and b"\x03" in buf:
                    s=buf.index(b"\x02"); e=buf.index(b"\x03")
                    if e<=s: buf=buf[s+1:]; continue
                    msg=buf[s+1:e]; buf=buf[e+1:]
                    if not self.parser:
                        self.parser=self.detect_parser(msg)
                        if not self.parser: continue
                    parsed=self.parser.parse(msg)
                    if parsed: self.update_state(parsed)
            except: time.sleep(0.2)

    def update_state(self,data):
        self.state.away_pts = data['away_pts']
        self.state.home_pts = data['home_pts']
        self.state.minutes = data['minutes']
        self.state.seconds = data['seconds']
        self.state.period = data['period']
        self.state.possession = data['possession']
        self.state.home_timeouts = data.get('home_to', self.state.home_timeouts)
        self.state.away_timeouts = data.get('away_to', self.state.away_timeouts)

        # Mirror to basketball state if needed
        self.state.minutes_basketball = data['minutes']
        self.state.seconds_basketball = data['seconds']
        self.state.tenths_basketball = data.get('tenths', 0)

        # UI update
        try: ui_updater.refresh.emit()
        except: pass
def main():
    app = QApplication(sys.argv)

    # --- Run update check ---
    check_for_updates()  

    # --- Window mode selection ---
    window_mode_dialog = WindowModeSelector()
    if window_mode_dialog.exec() != QDialog.Accepted:
        sys.exit(0)
    window_mode = window_mode_dialog.get_mode()

    # --- Program selector (OBS/Streamlabs or vMix) ---
    program_dialog = ProgramSelector()
    if program_dialog.exec() != QDialog.Accepted:
        sys.exit(0)
    program = program_dialog.selection
    mode = "transparent" if program == "OBS/Streamlabs" else "keyable"

    # --- Scoreboard selector (Football, Basketball, etc.) ---
    selector = ScoreboardSelector()
    if selector.exec() != QDialog.Accepted:
        sys.exit(0)
    sport = selector.get_selection()

    # --- Shared state ---
    state = ScoreState()

    # --- Map sport to scoreboard + control classes ---
    if sport == "Football":
        sb_class = FootballScoreboard
        ctl_class = FootballControl
    elif sport == "Basketball":
        sb_class = BasketballScoreboard
        ctl_class = BasketballControl
    elif sport == "Volleyball":
        sb_class = VolleyballScoreboard
        ctl_class = VolleyballControl
    elif sport == "Soccer":
        sb_class = SoccerScoreboard
        ctl_class = SoccerControl
    else:
        raise ValueError("Unknown sport selected!")

    # --- Instantiate scoreboard (pass state + mode) ---
    scoreboard = sb_class(state, mode=mode)

    # --- Main scoreboard window ---
    sb_win = QMainWindow()
    sb_win.setCentralWidget(scoreboard)

    # --- Window flags ---
    flags = Qt.Window
    if window_mode == "frameless":
        flags |= Qt.FramelessWindowHint
    else:
        flags |= Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint
    sb_win.setWindowFlags(flags)

    # --- Set the icon for taskbar and Alt+Tab ---
    sb_win.setWindowIcon(QIcon("scorebug.ico"))      # main window
    scoreboard.setWindowIcon(QIcon("scorebug.ico"))  # scoreboard widget itself

    # --- Transparent background for OBS ---
    if mode == "transparent":
        sb_win.setAttribute(Qt.WA_TranslucentBackground)

    # --- Right-click menu ---
    sb_win.mousePressEvent = lambda event: (
        QMenu().addAction("Close", sb_win.close).exec(event.globalPosition().toPoint())
    ) if event.button() == Qt.RightButton else None

    sb_win.show()

    # --- Instantiate control window ---
    control = ctl_class(state, scoreboard)
    control.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()