from shared.shared import *
class HockeyScoreboard(QWidget):
    def __init__(self, state: ScoreState, mode="transparent", parent=None):
        super().__init__(parent)
        self.state = state
        self.mode = mode
        self.flash_on = False
        self.show_hockey_intro = False
        self.show_hockey_breakboard = False
        self.show_hockey_scorebug = True 
        self.show_hockey_final = False
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
        if self.show_hockey_intro:
            self.draw_hockey_intro(p)
        if self.show_hockey_scorebug:
            self.draw_hockey_scorebug(p)
        if self.show_hockey_breakboard:
            self.draw_hockey_breakboard(p)
        if self.show_hockey_final:
            self.draw_hockey_final(p)

            return
    def draw_hockey_intro(self, p):
        pass
    def draw_hockey_breakboard(self, p):
        pass
    def draw_hockey_scorebug(self, p):
        pass
    def draw_hockey_final(self, p):
        pass
# ---------- Control window ----------
class HockeyControl(QMainWindow):
    pass
