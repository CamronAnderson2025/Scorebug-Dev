# main.py  –  entry point for Scorebug
from shared.shared import *
from sports.football_scoreboard   import FootballScoreboard,   FootballControl
from sports.basketball_scoreboard import BasketballScoreboard, BasketballControl
from sports.volleyball_scoreboard import VolleyballScoreboard, VolleyballControl
from sports.soccer_scoreboard     import SoccerScoreboard,     SoccerControl
from sports.baseball_scoreboard   import BaseballSoftballScoreboard, BaseballSoftballControl
from sports.hockey_scoreboard     import HockeyScoreboard,     HockeyControl

class ProgramSelector(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Streaming Program")
        layout = QVBoxLayout(self)
        self.combo = QComboBox()
        self.combo.addItems(["OBS/Streamlabs", "vMix"])
        layout.addWidget(self.combo)
        btn = QPushButton("OK")
        btn.clicked.connect(self.on_ok)
        layout.addWidget(btn)
        self.selection = None
    def on_ok(self):
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
        self.combo = QComboBox()
        self.combo.addItems(["Football", "Basketball", "Volleyball", "Soccer","Baseball/Softball (WIP)","Hockey (WIP)"])
        self.combo.setCurrentIndex(-1)  # No default selected
        layout.addWidget(self.combo)
        btn = QPushButton("OK")
        btn.clicked.connect(self.on_ok)
        layout.addWidget(btn)
        self.selection = None
    def on_ok(self):
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
            return {'away_pts': away,'home_pts': home,'minutes': int(mm),'seconds': int(ss),'tenths': tenths,'period': period,'possession': poss,'home_to': home_to,'away_to': away_to}
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
        self.state.minutes_basketball = data['minutes']
        self.state.seconds_basketball = data['seconds']
        self.state.tenths_basketball = data.get('tenths', 0)
        try: ui_updater.refresh.emit()
        except: pass
    
def main():
    app = QApplication(sys.argv)
    check_for_updates()

    log("App started")

    window_mode_dialog = WindowModeSelector()
    if window_mode_dialog.exec() != QDialog.Accepted:
        sys.exit(0)

    window_mode = window_mode_dialog.get_mode()
    log(f"Window mode: {window_mode}")

    program_dialog = ProgramSelector()
    if program_dialog.exec() != QDialog.Accepted:
        sys.exit(0)

    program = program_dialog.selection
    mode = "transparent" if program == "OBS/Streamlabs" else "keyable"
    log(f"Program: {program} | Mode: {mode}")

    selector = ScoreboardSelector()
    if selector.exec() != QDialog.Accepted:
        sys.exit(0)

    sport = selector.get_selection()
    state = ScoreState()
    log(f"Sport selected: {sport}")

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
    elif sport == "Baseball/Softball (WIP)":
        sb_class = BaseballSoftballScoreboard
        ctl_class = BaseballSoftballControl
    elif sport == "Hockey (WIP)":
        sb_class = HockeyScoreboard
        ctl_class = HockeyControl
    else:
        raise ValueError("Unknown sport selected!")

    scoreboard = sb_class(state, mode=mode)

    sb_win = QMainWindow()
    sb_win.setCentralWidget(scoreboard)

    flags = Qt.Window
    if window_mode == "frameless":
        flags |= Qt.FramelessWindowHint
    else:
        flags |= Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint

    sb_win.setWindowFlags(flags)
    sb_win.setWindowIcon(QIcon("shared/scorebug.ico"))
    scoreboard.setWindowIcon(QIcon("shared/scorebug.ico"))

    if mode == "transparent":
        sb_win.setAttribute(Qt.WA_TranslucentBackground)

    sb_win.mousePressEvent = lambda event: (
        QMenu().addAction("Close", sb_win.close).exec(
            event.globalPosition().toPoint()
        )
    ) if event.button() == Qt.RightButton else None

    sb_win.show()

    control = ctl_class(state, scoreboard)
    control.show()

    # =====================================================
    # BACKEND INIT (LOCAL FLASK) - STARTS SERVER IN SEPARATE THREAD
    # =====================================================

    shared.backend.init_backend(control)

    import threading
    threading.Thread(
        target=shared.backend.start_server,
        daemon=True
    ).start()

    log("LOCAL BACKEND RUNNING AT http://127.0.0.1:5055")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
