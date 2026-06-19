import os
import sys
import ctypes
import logging


os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
os.environ["QT_SCALE_FACTOR"] = "1"
import shared.backend
import serial
import serial.tools.list_ports
import threading
import requests
import webbrowser
from dataclasses import dataclass
import time
import json
import math
from PySide6.QtWidgets import QDialogButtonBox, QListWidget, QListWidgetItem, QApplication, QWidget, QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, QLineEdit, QFileDialog, QDialog, QRadioButton, QGraphicsRectItem, QColorDialog, QSpinBox, QMessageBox, QComboBox, QTabWidget, QLCDNumber, QCheckBox, QGraphicsScene, QToolButton, QGraphicsPolygonItem, QGraphicsBlurEffect, QMenu, QInputDialog, QSizePolicy, QGroupBox

from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PySide6.QtCore import Qt,QCoreApplication, QMetaObject, QPoint, QTimer, QRect, QPointF, QRectF, QObject, Signal, QUrl, Property, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QShortcut, QKeySequence, QAction, QPolygon, QPainter, QPolygonF, QColor, QIntValidator, QFont, QFontMetrics, QPixmap, QBrush, QPen, QLinearGradient, QPainterPath, QRadialGradient, QImage, QTextOption, QFontDatabase, QIcon

current_version = "3.1.0"
beta_version = "1.0.0"

required_update = True

version_url = "https://raw.githubusercontent.com/CamronAnderson2025/Offical-Scorebug/main/version.txt"
beta_version_url = "https://raw.githubusercontent.com/CamronAnderson2025/Scorebug-Beta/main/version.txt"

download_url = "https://smnsportslive.org/download"
beta_download_url = "https://smnsportslive.org/betadownload"

beta_mode = False

beta_features = {
    "debug_overlay": False,
    "new_layout": False,
    "experimental_animation": False,
    "beta_download_access": True
}

logging.basicConfig(
    filename="scorebug.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

def log(msg):
    logging.info(str(msg))
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    pass
def get_version_url():
    return beta_version_url if beta_mode else version_url

def get_download_url():
    return beta_download_url if beta_mode else download_url
class FlashingButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.active = False
        self.dot_visible = False
        self.base_text = text
        self.setStyleSheet("background-color:white; color:black;")
        self.timer = QTimer()
        self.timer.timeout.connect(self.flash_dot)

    def set_active(self, active: bool):
        self.active = active
        if active:
            self.timer.start(3000)  # flash every 500ms
        else:
            self.timer.stop()
            self.dot_visible = False
            self.update_dot()

    def flash_dot(self):
        self.dot_visible = not self.dot_visible
        self.update_dot()

    def update_dot(self):
        if self.dot_visible:
            self.setText(f"● {self.base_text}")
            self.setStyleSheet("background-color:white; color:red;")
        else:
            self.setText(self.base_text)
            self.setStyleSheet("background-color:white; color:black;")
class LogoWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)       
        layout = QVBoxLayout(self)  
        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText("Enter image URL here")
        layout.addWidget(self.url_input)
        self.load_btn = QPushButton("Load A Logo", self)
        layout.addWidget(self.load_btn)
        self.logo_label = QLabel(self)
        layout.addWidget(self.logo_label)
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
        if beta_mode:
            latest = requests.get(beta_version_url, timeout=3).text.strip()
            update_url = beta_download_url
        else:
            latest = requests.get(version_url, timeout=3).text.strip()
            update_url = download_url

        if latest != current_version:
            channel = "Beta" if beta_mode else "Production"
            msg = f"{channel} update available ({latest})!"

            if required_update:
                msg += "\nYou must update to continue."

            reply = QMessageBox.question(
                None,
                "Update Available",
                msg,
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                webbrowser.open(update_url)
                if required_update:
                    sys.exit(0)
            else:
                if required_update:
                    sys.exit(0)

    except Exception as e:
        print("Update check failed:", e)

class ScoreboardToolkit:
    def load_center_logo_from_setup(self):
        path,_=QFileDialog.getOpenFileName(self,"Open center logo","","Images (*.png *.jpg *.bmp)")
        if path:
            pm=QPixmap(path).scaled(300,300,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation)
            self.state.center_logo=pm
            self.repaint_scoreboard()
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
    def draw_outs_circle(self, p, x, y, r):
        p.save()

        color = QColor("#ff0000") if self.outs_changed else QColor("#1c1c1c")

        p.setPen(QPen(QColor("#ffffff"), 2))
        p.setBrush(QBrush(color))

        p.drawEllipse(x, y, r, r)

        p.restore()
    def load_center_logo(self):
        path,_=QFileDialog.getOpenFileName(self,"Open center logo","","Images (*.png *.jpg *.bmp)")
        if path:
            pm=QPixmap(path).scaled(60,60,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation)
            self.state.center_logo=pm
            self.repaint_scoreboard()

    def draw_basketball_timeout_rects(self,p:QPainter,x,y,remaining,w:int=3,h:int=3,spacing:int=3):
        remaining=max(0,min(5,int(remaining)))
        p.setPen(Qt.PenStyle.NoPen)
        radius=min(w,h)*2
        for i in range(5):
            cy=y+i*(radius+spacing)
            filled=i<remaining
            p.setBrush(QColor("white") if filled else QColor(255,255,255,60))
            p.drawEllipse(QRect(int(x),int(cy),int(radius),int(radius)))

    def draw_logo_in_top_rounded_window(self,p,x,y,w,h,logo,radius=12):
        if logo is None or not isinstance(logo,QPixmap) or logo.isNull():return
        p.save() 
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform,True)
        path=QPainterPath()
        path.moveTo(x+radius,y)
        path.lineTo(x+w-radius,y)
        path.quadTo(x+w,y,x+w,y+radius)
        path.lineTo(x+w,y+h)
        path.lineTo(x,y+h)
        path.lineTo(x,y+radius)
        path.quadTo(x,y,x+radius,y)
        p.setClipPath(path,Qt.ClipOperation.IntersectClip)
        scaled=logo.scaled(w,9999,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation)
        lx=x+(w-scaled.width())//2
        ly=y+(h-scaled.height())//2
        p.drawPixmap(lx,ly,scaled)
        p.restore()

    def clip_to_rounded_rect(self,p,x,y,w,h,radius=12):
        path=QPainterPath()
        path.addRoundedRect(QRectF(x,y,w,h),radius,radius)
        p.setClipPath(path,Qt.ClipOperation.IntersectClip)

    def clip_to_rect(self,p,x,y,w,h):
        path=QPainterPath()
        path.addRect(QRectF(x,y,w,h))
        p.setClipPath(path)

    def draw_rect(self,p,x,y,w,h,color):
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(color)
        p.drawRect(int(x),int(y),int(w),int(h))

    def draw_diamond(self, p, x, y, size, color):
        points = [
            QPoint(int(x), int(y - size)),
            QPoint(int(x + size), int(y)),
            QPoint(int(x), int(y + size)),
            QPoint(int(x - size), int(y))
        ]

        p.setPen(QPen(QColor("#ffffff"), 2))  # white outline
        p.setBrush(color)                     # fill color
        p.drawPolygon(QPolygon(points))

    def draw_normal_rect(self,p:QPainter,x,y,w,h,color:QColor):
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(color))
        p.drawRect(QRect(int(x),int(y),int(w),int(h)))
    def draw_line(self, p: QPainter, x1, y1, x2, y2, color: QColor, thickness=1):
        pen = QPen(color)
        pen.setWidth(thickness)
        p.setPen(pen)
        p.drawLine(int(x1), int(y1), int(x2), int(y2))
        
    def draw_transparentnormal_rect(self,p:QPainter,x,y,w,h,color:QColor):
        p.setPen(Qt.PenStyle.NoPen)
        c=QColor(color)
        c.setAlpha(240)
        p.setBrush(QBrush(c))
        p.drawRect(QRect(int(x),int(y),int(w),int(h)))

    def draw_rect_transparent(self,p,x,y,w,h,color):
        fill=QColor(color)
        fill.setAlpha(120)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(fill)
        p.drawRect(int(x),int(y),int(w),int(h))

    def draw_rect_shadow(self,p,x,y,w,h,color):
        shadow=QColor(255,255,255,140)
        for i in range(6):
            shadow.setAlpha(80-i*12)
            p.setBrush(shadow)
            p.drawRect(int(x+4+i),int(y+4+i),int(w-2*i),int(h-2*i))
        p.setBrush(color)
        p.drawRect(int(x),int(y),int(w),int(h))

    def draw_fully_rounded_rect(self,p,x,y,w,h,color:QColor,radius:int=12):
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(color))
        p.drawRoundedRect(QRect(int(x),int(y),int(w),int(h)),radius,radius)
    def draw_1fully_rounded_rect(self,p,x,y,w,h,color:QColor,radius:int=12):
        pen=QPen(QColor("white"))
        pen.setWidth(2)
        p.setPen(pen)
        p.setBrush(QBrush(color))
        p.drawRoundedRect(QRect(int(x),int(y),int(w),int(h)),radius,radius)
    def draw_top_rounded_rect(self,p,x,y,w,h,color:QColor,radius:int=12):
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(color)
        path=QPainterPath()
        path.moveTo(x+radius,y)
        path.lineTo(x+w-radius,y)
        path.quadTo(x+w,y,x+w,y+radius)
        path.lineTo(x+w,y+h)
        path.lineTo(x,y+h)
        path.lineTo(x,y+radius)
        path.quadTo(x,y,x+radius,y)
        path.closeSubpath()
        p.drawPath(path)

    def draw_bottom_round_rect(self,p,x,y,w,h,color:QColor,radius:int=12):
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(color)
        path=QPainterPath()
        path.moveTo(x,y)
        path.lineTo(x+w,y)
        path.lineTo(x+w,y+h-radius)
        path.quadTo(x+w,y+h,x+w-radius,y+h)
        path.lineTo(x+radius,y+h)
        path.quadTo(x,y+h,x,y+h-radius)
        path.lineTo(x,y)
        p.drawPath(path)

    def draw_top_flat_rect(self,p,x,y,w,h,color:QColor,radius:int=12):
        self.draw_bottom_round_rect(p,x,y,w,h,color,radius)

    def draw_leftrounded_rect(self,p,x,y,w,h,color:QColor):
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(color))
        radius=12
        path=QPainterPath()
        path.moveTo(x+radius,y)
        path.lineTo(x+w,y)
        path.lineTo(x+w,y+h)
        path.lineTo(x+radius,y+h)
        path.quadTo(x,y+h,x,y+h-radius)
        path.lineTo(x,y+radius)
        path.quadTo(x,y,x+radius,y)
        p.drawPath(path)

    def draw_rightrounded_rect(self,p,x,y,w,h,color:QColor):
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(color))
        radius=12
        path=QPainterPath()
        path.moveTo(x,y)
        path.lineTo(x+w-radius,y)
        path.quadTo(x+w,y,x+w,y+radius)
        path.lineTo(x+w,y+h-radius)
        path.quadTo(x+w,y+h,x+w-radius,y+h)
        path.lineTo(x,y+h)
        path.lineTo(x,y)
        p.drawPath(path)
    def draw_transparentrounded_rect(self, p, x, y, w, h, color: QColor):
        radius = 12
        fill_color = QColor(color)
        fill_color.setAlphaF(0.7)
        border_color = QColor(255, 255, 255, 255)
        path = QPainterPath()
        path.moveTo(x, y)
        path.lineTo(x + w, y)
        path.lineTo(x + w, y + h - radius)
        path.quadTo(x + w, y + h, x + w - radius, y + h)
        path.lineTo(x + radius, y + h)
        path.quadTo(x, y + h, x, y + h - radius)
        path.lineTo(x, y)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(fill_color))
        p.drawPath(path)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(border_color, 2))
        p.drawPath(path)
    def draw_rounded_rect(self,p,x,y,w,h,color:QColor):
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(color))
        radius=12
        path=QPainterPath()
        path.moveTo(x,y)
        path.lineTo(x+w,y)
        path.lineTo(x+w,y+h-radius)
        path.quadTo(x+w,y+h,x+w-radius,y+h)
        path.lineTo(x+radius,y+h)
        path.quadTo(x,y+h,x,y+h-radius)
        path.lineTo(x,y)
        p.drawPath(path)
    def draw_weather_rect(self, p, x, y, w, h):
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        radius = 12
        path = QPainterPath()
        path.moveTo(x + radius, y)
        path.lineTo(x + w - radius, y)
        path.quadTo(x + w, y, x + w, y + radius)
        path.lineTo(x + w, y + h - radius)
        path.quadTo(x + w, y + h, x + w - radius, y + h)
        path.lineTo(x + radius, y + h)
        path.quadTo(x, y + h, x, y + h - radius)
        path.lineTo(x, y + radius)
        path.quadTo(x, y, x + radius, y)
        pen = QPen(QColor("white"))
        pen.setWidth(4)
        p.setPen(pen)
        p.setBrush(QBrush(QColor("black")))
        p.drawPath(path)
    def draw_ktv(self, p, x, y, w, h):
        p.save()
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setOpacity(0.6)
        radius = 12
        path = QPainterPath()
        path.moveTo(x + radius, y)
        path.lineTo(x + w - radius, y)
        path.quadTo(x + w, y, x + w, y + radius)
        path.lineTo(x + w, y + h - radius)
        path.quadTo(x + w, y + h, x + w - radius, y + h)
        path.lineTo(x + radius, y + h)
        path.quadTo(x, y + h, x, y + h - radius)
        path.lineTo(x, y + radius)
        path.quadTo(x, y, x + radius, y)
        pen = QPen(QColor("white"))
        pen.setWidth(4)
        p.setPen(pen)
        p.setBrush(QBrush(QColor("#000000")))
        p.drawPath(path)
        p.restore()
    def draw_x(self, p, x, y, w, h, thickness=4):
        p.save()
        p.setPen(QPen(QColor(255, 255, 255, 255), thickness))
        p.drawLine(x, y, x + w, y + h)
        p.drawLine(x + w, y, x, y + h)
        p.restore()   
    def draw_sh(self, p, x, y, w, h):
        p.save()
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setOpacity(0.85)
        radius = 12
        path = QPainterPath()
        path.moveTo(x + radius, y)
        path.lineTo(x + w - radius, y)
        path.quadTo(x + w, y, x + w, y + radius)
        path.lineTo(x + w, y + h - radius)
        path.quadTo(x + w, y + h, x + w - radius, y + h)
        path.lineTo(x + radius, y + h)
        path.quadTo(x, y + h, x, y + h - radius)
        path.lineTo(x, y + radius)
        path.quadTo(x, y, x + radius, y)
        pen = QPen(QColor("white"))
        pen.setWidth(4)
        p.setPen(pen)
        p.setBrush(QBrush(QColor("black")))
        p.drawPath(path)
        p.restore()
    def draw_lower3rd_rect(self, p, x, y, w, h):
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        radius = 12
        path = QPainterPath()
        path.moveTo(x + radius, y)
        path.lineTo(x + w - radius, y)
        path.quadTo(x + w, y, x + w, y + radius)
        path.lineTo(x + w, y + h - radius)
        path.quadTo(x + w, y + h, x + w - radius, y + h)
        path.lineTo(x + radius, y + h)
        path.quadTo(x, y + h, x, y + h - radius)
        path.lineTo(x, y + radius)
        path.quadTo(x, y, x + radius, y)
        pen = QPen(QColor("white"))
        pen.setWidth(2)
        p.setPen(pen)
        p.setBrush(QBrush(QColor("#262626")))
        p.drawPath(path)
    def draw_crew_rect(self, p, x, y, w, h):
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        radius = 12
        path = QPainterPath()
        path.moveTo(x + radius, y)
        path.lineTo(x + w - radius, y)
        path.quadTo(x + w, y, x + w, y + radius)
        path.lineTo(x + w, y + h - radius)
        path.quadTo(x + w, y + h, x + w - radius, y + h)
        path.lineTo(x + radius, y + h)
        path.quadTo(x, y + h, x, y + h - radius)
        path.lineTo(x, y + radius)
        path.quadTo(x, y, x + radius, y)
        pen = QPen(QColor("white"))
        pen.setWidth(2)
        p.setPen(pen)
        p.setBrush(QBrush(QColor("#262626")))
        p.drawPath(path)
    def draw_semitransparent_rounded_rect(self,p,x,y,w,h,color:QColor):
        c=QColor(color)
        c.setAlpha(225)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(c))
        radius=12
        path=QPainterPath()
        path.moveTo(x,y)
        path.lineTo(x+w,y)
        path.lineTo(x+w,y+h-radius)
        path.quadTo(x+w,y+h,x+w-radius,y+h)
        path.lineTo(x+radius,y+h)
        path.quadTo(x,y+h,x,y+h-radius)
        path.lineTo(x,y)
        p.drawPath(path)

    def draw_timerounded_rect(self,p,x,y,w,h,color:QColor):
        radius=12
        p.setPen(Qt.PenStyle.NoPen)
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

    def draw_bottom1_rounded_rect(self,p,x,y,w,h,color:QColor,radius:int=7):
        path=QPainterPath()
        path.moveTo(x,y)
        path.lineTo(x+w,y)
        path.lineTo(x+w,y+h-radius)
        path.quadTo(x+w,y+h,x+w-radius,y+h)
        path.lineTo(x+radius,y+h)
        path.quadTo(x,y+h,x,y+h-radius)
        path.lineTo(x,y)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(color))
        p.drawPath(path)

    def draw_bottom2_rounded_rect(self,p,x,y,w,h,color:QColor,radius:int=7):
        path=QPainterPath()
        path.moveTo(x+radius,y)
        path.lineTo(x+w-radius,y)
        path.quadTo(x+w,y,x+w,y+radius)
        path.lineTo(x+w,y+h)
        path.lineTo(x,y+h)
        path.lineTo(x,y+radius)
        path.quadTo(x,y,x+radius,y)
        path.closeSubpath()
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(color))
        p.drawPath(path)

    def draw_top_right_flat(self,p,x,y,w,h,color:QColor):
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
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(color))
        p.drawPath(path)

    def draw_fully_gradient_rect(self,p,x,y,w,h,color:QColor,radius:int=12):
        darker=color.darker(225)
        grad=QLinearGradient(x,y,x+w,y)
        grad.setColorAt(0.0,color)
        grad.setColorAt(0.5,darker)
        grad.setColorAt(1.0,darker)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(grad))
        p.drawRoundedRect(QRect(int(x),int(y),int(w),int(h)),radius,radius)

    def draw_fully_grounded_rect(self,p,x,y,w,h,radius:int=12):
        grad=QLinearGradient(x,y,x+w,y)
        grad.setColorAt(0.0,QColor(0,0,0))
        grad.setColorAt(0.5,QColor(128,128,128))
        grad.setColorAt(1.0,QColor(0,0,0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(grad))
        p.drawRoundedRect(QRect(int(x),int(y),int(w),int(h)),radius,radius)

    def draw_ffully_rounded_rect(self,p,x,y,w,h,radius:int=10):
        p.save()
        p.setPen(Qt.PenStyle.NoPen)
        grad=QLinearGradient(x,y,x,y+h)
        grad.setColorAt(0.0,QColor(200,200,200))
        grad.setColorAt(0.2,QColor(40,40,40))
        grad.setColorAt(0.8,QColor(40,40,40))
        grad.setColorAt(1.0,QColor(200,200,200))
        p.setBrush(QBrush(grad))
        p.drawRoundedRect(QRect(int(x),int(y),int(w),int(h)),radius,radius)
        p.restore()

    def draw_transparent_to_black_rect(self,p,x,y,w,h,radius:int=12):
        grad=QLinearGradient(x,y,x+w,y+h)
        grad.setColorAt(0.0,QColor(0,0,0,0))
        grad.setColorAt(0.5,QColor(0,0,0,200))
        grad.setColorAt(1.0,QColor(0,0,0,255))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(grad))
        p.drawRoundedRect(QRect(int(x),int(y),int(w),int(h)),radius,radius)

    def draw_flat_segment(self,p,x,y,w,h,left_color:QColor,right_color:QColor):
        grad=QLinearGradient(x,y,x+w,y)
        grad.setColorAt(0.0,left_color)
        grad.setColorAt(1.0,right_color)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(grad))
        p.drawRect(x,y,w,h)

    def draw_flat_segment_home(self,p,x,y,w,h,left_color:QColor,right_color:QColor):
        grad=QLinearGradient(x+w,y,x,y)
        grad.setColorAt(0.0,left_color)
        grad.setColorAt(1.0,right_color)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(grad))
        p.drawRect(x,y,w,h)

    def draw_tlteam_gradient_rect(self, p, x, y, w, h, color: QColor):
        p.save()
        p.setPen(Qt.PenStyle.NoPen)
        base = QColor(color)
        light = QColor(color).lighter(140)
        grad = QLinearGradient(x, y, x, y + h)
        grad.setColorAt(0.0, base)
        grad.setColorAt(1.0, light)
        path = QPainterPath()
        radius = 10
        path.moveTo(x + radius, y)
        path.lineTo(x + w, y)
        path.lineTo(x + w, y + h)
        path.lineTo(x, y + h)
        path.lineTo(x, y + radius)
        path.quadTo(x, y, x + radius, y)
        p.setBrush(QBrush(grad))
        p.drawPath(path)
        p.restore()
    def draw_blteam_gradient_rect(self, p, x, y, w, h, color: QColor):
        p.save()
        p.setPen(Qt.PenStyle.NoPen)
        base = QColor(color)
        light = QColor(color).lighter(140)
        grad = QLinearGradient(x, y, x, y + h)
        grad.setColorAt(0.0, base)
        grad.setColorAt(1.0, light)
        path = QPainterPath()
        radius = 10
        path.moveTo(x, y)
        path.lineTo(x + w, y)
        path.lineTo(x + w, y + h)
        path.lineTo(x + radius, y + h)
        path.quadTo(x, y + h, x, y + h - radius)
        path.lineTo(x, y)
        p.setBrush(QBrush(grad))
        p.drawPath(path)
        p.restore()
    def draw_out_circle(self,p,x,y,radius,filled:bool):
        p.save()
        p.setRenderHint(QPainter.RenderHint.Antialiasing,True)
        rect=QRectF(x,y,radius*2,radius*2)
        if filled:
            p.setBrush(QBrush(QColor("#ff3b3b")))
        else:
            p.setBrush(Qt.BrushStyle.NoBrush)
        pen=QPen(QColor("white"))
        pen.setWidth(3)
        p.setPen(pen)
        p.drawEllipse(rect)
        p.restore()

    def draw_introround_left(self,p,x,y,w,h,color:QColor,r:int=10):
        path=QPainterPath()
        path.moveTo(x+r,y)
        path.lineTo(x+w,y)
        path.lineTo(x+w,y+h)
        path.lineTo(x+r,y+h)
        path.quadTo(x,y+h,x,y+h-r)
        path.lineTo(x,y+r)
        path.quadTo(x,y,x+r,y)
        p.save()
        p.setPen(Qt.PenStyle.NoPen)
        grad=QLinearGradient(x,y,x+w,y)
        grad.setColorAt(0.0,color.darker(150))
        grad.setColorAt(0.2,color.darker(175))
        grad.setColorAt(0.4,color.darker(200))
        grad.setColorAt(0.5,color.darker(225))
        grad.setColorAt(0.6,color.darker(250))
        grad.setColorAt(0.8,QColor(0,0,0))
        grad.setColorAt(1.0,QColor(0,0,0))
        p.setBrush(QBrush(grad))
        p.drawPath(path)
        p.restore()

    def draw_introround_right(self,p,x,y,w,h,color:QColor,r:int=10):
        path=QPainterPath()
        path.moveTo(x,y)
        path.lineTo(x+w-r,y)
        path.quadTo(x+w,y,x+w,y+r)
        path.lineTo(x+w,y+h-r)
        path.quadTo(x+w,y+h,x+w-r,y+h)
        path.lineTo(x,y+h)
        path.lineTo(x,y)
        p.save()
        p.setPen(Qt.PenStyle.NoPen)
        grad=QLinearGradient(x+w,y,x,y)
        grad.setColorAt(0.0,color.darker(150))
        grad.setColorAt(0.2,color.darker(175))
        grad.setColorAt(0.4,color.darker(200))
        grad.setColorAt(0.5,color.darker(225))
        grad.setColorAt(0.6,color.darker(250))
        grad.setColorAt(0.8,QColor(0,0,0))
        grad.setColorAt(1.0,QColor(0,0,0))
        p.setBrush(QBrush(grad))
        p.drawPath(path)
        p.restore()

    def draw_round_left(self,p,x,y,w,h,color:QColor,r:int=10):
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(color)
        path=QPainterPath()
        path.moveTo(x+r,y)
        path.lineTo(x+w,y)
        path.lineTo(x+w,y+h)
        path.lineTo(x+r,y+h)
        path.quadTo(x,y+h,x,y+h-r)
        path.lineTo(x,y+r)
        path.quadTo(x,y,x+r,y)
        p.drawPath(path)

    def draw_round_right(self,p,x,y,w,h,color:QColor,r:int=10):
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(color)
        path=QPainterPath()
        path.moveTo(x,y)
        path.lineTo(x+w-r,y)
        path.quadTo(x+w,y,x+w,y+r)
        path.lineTo(x+w,y+h-r)
        path.quadTo(x+w,y+h,x+w-r,y+h)
        path.lineTo(x,y+h)
        path.lineTo(x,y)
        p.drawPath(path)

    def draw_away_notch(self,p,x,y,w,h,color:QColor):
        offset=h*0.25
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(color)
        path=QPainterPath()
        path.moveTo(x,y)
        path.lineTo(x+w,y+offset)
        path.lineTo(x+w,y+h-offset)
        path.lineTo(x,y+h)
        path.closeSubpath()
        p.drawPath(path)

    def draw_home_notch(self,p,x,y,w,h,color:QColor):
        offset=h*0.25
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(color)
        path=QPainterPath()
        path.moveTo(x+w,y)
        path.lineTo(x,y+offset)
        path.lineTo(x,y+h-offset)
        path.lineTo(x+w,y+h)
        path.closeSubpath()
        p.drawPath(path)

    def draw_pod(self,p,x,y,pod_w,h,base_color:QColor):
        left_r,right_r=10,62
        path=QPainterPath()
        path.moveTo(x+left_r,y)
        path.lineTo(x+pod_w,y)
        path.lineTo(x+pod_w,y+h-right_r)
        path.quadTo(x+pod_w,y+h,x+pod_w-right_r,y+h)
        path.lineTo(x+left_r,y+h)
        path.quadTo(x,y+h,x,y+h-left_r)
        path.lineTo(x,y+left_r)
        path.quadTo(x,y,x+left_r,y)
        cx,cy,rad=x+pod_w*0.45,y+h*0.20,pod_w*1.2
        glow=QRadialGradient(cx,cy,rad)
        glow.setColorAt(0.0,base_color)
        glow.setColorAt(0.6,base_color)
        glow.setColorAt(0.85,base_color.lighter(160))
        glow.setColorAt(1.0,QColor(25,25,25))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(glow))
        p.drawPath(path)
        fade=QLinearGradient(x,y,x+pod_w,y)
        fade.setColorAt(0.0,QColor(0,0,0,0))
        fade.setColorAt(1.0,QColor(0,0,0,60))
        p.setBrush(QBrush(fade))
        p.drawPath(path)

    def draw_hmpod(self,p,x,y,pod_w,h,base_color:QColor):
        left_r,right_r=62,10
        path=QPainterPath()
        path.moveTo(x,y)
        path.lineTo(x+pod_w-right_r,y)
        path.quadTo(x+pod_w,y,x+pod_w,y+right_r)
        path.lineTo(x+pod_w,y+h-right_r)
        path.quadTo(x+pod_w,y+h,x+pod_w-right_r,y+h)
        path.lineTo(x+left_r,y+h)
        path.quadTo(x,y+h,x,y+h-left_r)
        path.lineTo(x,y)
        cx,cy,rad=x+pod_w*0.45,y+h*0.20,pod_w*1.2
        glow=QRadialGradient(cx,cy,rad)
        glow.setColorAt(0.0,base_color)
        glow.setColorAt(0.6,base_color)
        glow.setColorAt(0.85,base_color.lighter(160))
        glow.setColorAt(1.0,QColor(25,25,25))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(glow))
        p.drawPath(path)

    def draw_base_bar(self,p,x,y,w,h):
        r=10
        path=QPainterPath()
        path.moveTo(x+r,y)
        path.lineTo(x+w,y)
        path.lineTo(x+w,y+h)
        path.lineTo(x+r,y+h)
        path.quadTo(x,y+h,x,y+h-r)
        path.lineTo(x,y+r)
        path.quadTo(x,y,x+r,y)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(25,25,25))
        p.drawPath(path)

    def draw_hmbase_bar(self,p,x,y,w,h):
        r=10
        path=QPainterPath()
        path.moveTo(x,y)
        path.lineTo(x+w-r,y)
        path.quadTo(x+w,y,x+w,y+r)
        path.lineTo(x+w,y+h-r)
        path.quadTo(x+w,y+h,x+w-r,y+h)
        path.lineTo(x,y+h)
        path.lineTo(x,y)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(25,25,25))
        p.drawPath(path)

    def draw_panel_base(self,p,x,y,w,h,color:QColor,thickness:int=5):
        pen=QPen(color)
        pen.setWidth(thickness)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(x,y,w,h,10,10)

    def draw_ppanel_base(self,p,x,y,w,h,color:QColor,thickness:int=3):
        pen=QPen(color)
        pen.setWidth(thickness)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(x,y,w,h,10,10)

    def draw_fpanel_base(self,p,x,y,w,h,color:QColor,thickness:int=2):
        pen=QPen(color)
        pen.setWidth(thickness)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(x,y,w,h,10,10)

    def draw_tdpanel_base(self,p,x,y,w,h,color:QColor,thickness:int=4):
        pen=QPen(color)
        pen.setWidth(thickness)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(x,y,w,h,10,10)
        shadow=QColor(color)
        shadow.setAlpha(150)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(shadow)
        for i in range(1,21):
            p.drawRoundedRect(x+i,y+i,w-2*i,h-2*i,max(0,10-i),max(0,10-i))

    def draw_panel_glow(self,p,x,y,w,h,color:QColor):
        radius=10
        glow_rect=QRectF(x+2,y+2,w-4,h-4)
        outer=QColor(color).darker(100)
        inner=QColor(color).lighter(150)
        cx,cy=glow_rect.left(),glow_rect.center().y()
        rx,_=glow_rect.right(),glow_rect.center().y()
        rim=QLinearGradient(cx,cy,rx,cy)
        for stop in(0.0,0.12,0.20,0.80,0.88,1.0):
            rim.setColorAt(stop,outer)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(rim)
        p.drawRoundedRect(glow_rect,radius,radius)
        fill=QLinearGradient(cx,cy,rx,cy)
        fill.setColorAt(0.0,outer)
        fill.setColorAt(0.15,outer)
        fill.setColorAt(0.5,inner)
        fill.setColorAt(1.0,inner)
        p.setBrush(fill)
        p.drawRoundedRect(glow_rect,radius,radius)
        bloom=QLinearGradient(glow_rect.center().x(),glow_rect.bottom(),glow_rect.center().x(),glow_rect.top())
        bloom.setColorAt(0.0,outer)
        bloom.setColorAt(0.2,outer)
        bloom.setColorAt(0.45,Qt.GlobalColor.transparent)
        p.setBrush(bloom)
        p.drawRoundedRect(glow_rect,radius,radius)

    def draw_inset_border(self,p,x,y,w,h,base_radius:int=12):
        inset=2
        rx,ry=x+inset,y+inset
        rw,rh=w-inset*2,h-inset*2
        radius=max(1,base_radius-inset)
        pen=QPen(QColor("#505355"),2)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        path=QPainterPath()
        path.moveTo(rx,ry+radius)
        path.lineTo(rx,ry+rh-radius)
        path.quadTo(rx,ry+rh,rx+radius,ry+rh)
        path.lineTo(rx+rw-radius,ry+rh)
        path.quadTo(rx+rw,ry+rh,rx+rw,ry+rh-radius)
        path.lineTo(rx+rw,ry+radius)
        p.drawPath(path)
        p.setPen(Qt.PenStyle.NoPen)

    def draw_top_gloss(self,p,x,y,w,h):
        gloss_h=int(h*0.35)
        gloss_y=int(y+h*0.12)
        grad=QLinearGradient(x,gloss_y,x+w,gloss_y)
        grad.setColorAt(0.0,QColor(255,255,255,0))
        grad.setColorAt(0.2,QColor(255,255,255,50))
        grad.setColorAt(0.5,QColor(255,255,255,70))
        grad.setColorAt(0.8,QColor(255,255,255,50))
        grad.setColorAt(1.0,QColor(255,255,255,0))
        p.save()
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(grad))
        p.drawRect(int(x),gloss_y,int(w),gloss_h)
        p.restore()

    def draw_horizontal_glow(self,p,x,y,w,h,color:QColor):
        c0,c1,c2=QColor(color),QColor(color),QColor(color)
        c0.setAlpha(0)
        c1.setAlpha(160)
        c2.setAlpha(0)
        grad=QLinearGradient(x,y,x+w,y)
        grad.setColorAt(0.0,c0)
        grad.setColorAt(0.5,c1)
        grad.setColorAt(1.0,c2)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(grad))
        p.drawRoundedRect(x,y,w,h,h/2,h/2)

    def draw_inner_edge_glow(self,p,x,y,w,h,color:QColor):
        img=QImage(w,h,QImage.Format.Format_ARGB32_Premultiplied)
        img.fill(Qt.GlobalColor.transparent)
        off=QPainter(img)
        off.setRenderHint(QPainter.RenderHint.Antialiasing,True)
        r=h*0.22
        clip=QPainterPath()
        clip.addRoundedRect(0,0,w,h,r,r)
        off.setClipPath(clip)
        grad=QLinearGradient(0,0,w,0)
        grad.setColorAt(0.0,color)
        grad.setColorAt(0.28,QColor(255,255,255))
        grad.setColorAt(0.55,QColor(255,255,255,0))
        grad.setColorAt(1.0,QColor(0,0,0,0))
        off.setPen(Qt.PenStyle.NoPen)
        off.setBrush(grad)
        strip_h=int(h*0.45)
        off.drawRect(0,(h-strip_h)//2,w,strip_h)
        off.end()
        blurred=self._blur_image(img,w,h,radius=10)
        p.drawImage(x,y,blurred)

    def draw_timeout_rects(self,p:QPainter,x,y,remaining,max_count:int=3,align:str="right",w:int=21,h:int=3,spacing:int=7):
        remaining=max(0,min(max_count,int(remaining)))
        p.setPen(Qt.PenStyle.NoPen)
        for i in range(max_count):
            rect_x=x+i*(w+spacing)
            if align=="left":
                filled=i<remaining
            else:
                filled=(max_count-1-i)<remaining
            p.setBrush(QColor("white") if filled else QColor(255,255,255,60))
            p.drawRoundedRect(QRect(int(rect_x),int(y),int(w),int(h)),1,1)
    def draw_vbtimeout_rects(self,p:QPainter,x,y,remaining,max_count:int=2,align:str="right",w:int=21,h:int=3,spacing:int=7):
        remaining=max(0,min(max_count,int(remaining)))
        p.setPen(Qt.PenStyle.NoPen)
        for i in range(max_count):
            rect_x=x+i*(w+spacing)
            if align=="left":
                filled=i<remaining
            else:
                filled=(max_count-1-i)<remaining
            p.setBrush(QColor("white") if filled else QColor(255,255,255,60))
            p.drawRoundedRect(QRect(int(rect_x),int(y),int(w),int(h)),1,1)
    def draw_bottom_event_text(self,p,x,y,text,width:int=640):
        if not text:return
        p.setFont(self.event_font)
        p.setPen(Qt.GlobalColor.white)
        p.drawText(QRect(x,y,width,22),Qt.AlignmentFlag.AlignCenter,text)

    def draw_upper_event_text(self,p,x,y,text):
        if not text:return
        p.setFont(self.introupper_font)
        p.setPen(Qt.GlobalColor.white)
        p.drawText(QRect(x,y,640,42),Qt.AlignmentFlag.AlignCenter,text)

    def draw_event_text(self,p,x,y,text):
        if not text:return
        p.setFont(self.record_font)
        p.setPen(Qt.GlobalColor.white)
        p.drawText(QRect(x,y,240,22),Qt.AlignmentFlag.AlignVCenter|Qt.AlignmentFlag.AlignHCenter,text)

    def draw_bbevent_text(self,p,x,y,text):
        if not text:return
        p.setFont(self.upperevent_font)
        p.setPen(Qt.GlobalColor.white)
        p.drawText(QRect(x,y,240,40),Qt.AlignmentFlag.AlignVCenter|Qt.AlignmentFlag.AlignHCenter,text)

    def draw_bevent_text(self,p,x,y,text):
        if not text:return
        p.setFont(self.scoreevent_font)
        p.setPen(Qt.GlobalColor.white)
        p.drawText(QRect(x,y,240,40),Qt.AlignmentFlag.AlignVCenter|Qt.AlignmentFlag.AlignHCenter,text)

    def draw_timeout_popup(self,p,x,y,text):
        p.setFont(self.timeout_font)
        p.setPen(Qt.GlobalColor.white)
        p.drawText(QRect(x,y,240,45),Qt.AlignmentFlag.AlignCenter,text)

    def draw_possession_text(self,p,x,y,color:QColor):
        p.setPen(color)
        f=p.font()
        f.setPointSize(11)
        f.setBold(True)
        p.setFont(f)
        p.drawText(x,y,"POSS")

    def draw_fouls_text(self,p,x,y,color:QColor):
        p.setPen(color)
        f=p.font()
        f.setPointSize(11)
        f.setBold(True)
        p.setFont(f)
        p.drawText(x,y,"Fouls")

    def mousePressEvent(self,event):
        if event.button()==Qt.MouseButton.LeftButton:
            self._drag_pos=event.globalPosition().toPoint()

    def mouseMoveEvent(self,event):
        if event.buttons()&Qt.MouseButton.LeftButton:
            delta=event.globalPosition().toPoint()-self._drag_pos
            self.window().move(self.window().pos()+delta)
            self._drag_pos=event.globalPosition().toPoint()

    def mouseReleaseEvent(self,event):
        self._drag_pos=None

    def period_text(self)->str:
        p=self.state.period
        labels=["1st","2nd","3rd","4th"]
        if 1<=p<=4:return labels[p-1]
        mapping={5:"1 OT",6:"2 OT",7:"3 OT",8:"4 OT",9:"5 OT",11:"FINAL"}
        return mapping.get(p,"")
    def vbperiod_text(self)->str:
        p=self.state.vbperiod
        if 1<=p<=5:return str(p)
        if p==6:return "FINAL"
        return ""
    @staticmethod
    def ordinal(n:int)->str:
        if n==1:return"1st"
        if n==2:return"2nd"
        if n==3:return"3rd"
        return f"{n}th"

    @staticmethod
    def pct(made:int,missed:int)->str:
        total=made+missed
        if total==0:return"0%"
        return f"{round(made/total*100):d}%"

    @staticmethod
    def format_rank_name(rank,name:str):
        try:r=int(rank)
        except:r=0
        name=name.upper()
        if r<=0:return"",name
        return str(r),name

    @staticmethod
    def _blur_image(img:QImage,w:int,h:int,radius:int=18)->QImage:
        blurred=QImage(w,h,QImage.Format.Format_ARGB32_Premultiplied)
        blurred.fill(Qt.GlobalColor.transparent)
        scene=QGraphicsScene()
        item=scene.addPixmap(QPixmap.fromImage(img))
        blur=QGraphicsBlurEffect()
        blur.setBlurRadius(radius)
        item.setGraphicsEffect(blur)
        rp=QPainter(blurred)
        scene.render(rp)
        rp.end()
        return blurred

    @staticmethod
    def _make_radial_glow_image(w:int,h:int,color:QColor,alpha:int=160)->QImage:
        img=QImage(w,h,QImage.Format.Format_ARGB32_Premultiplied)
        img.fill(Qt.GlobalColor.transparent)
        offp=QPainter(img)
        offp.setRenderHint(QPainter.RenderHint.Antialiasing,True)
        c1,c2=QColor(color),QColor(color)
        c1.setAlpha(alpha)
        c2.setAlpha(0)
        grad=QRadialGradient(w/2,h/2,max(w,h)*0.75)
        grad.setColorAt(0.0,c1)
        grad.setColorAt(0.45,c1)
        grad.setColorAt(1.0,c2)
        offp.setPen(Qt.PenStyle.NoPen)
        offp.setBrush(grad)
        offp.drawRect(0,0,w,h)
        offp.end()
        return img
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
    def draw_up_triangle(self, p: QPainter, x, y, w, h, color: QColor):
        path = QPainterPath()
        path.moveTo(x, y - h / 2)
        path.lineTo(x - w / 2, y + h / 2)
        path.lineTo(x + w / 2, y + h / 2)
        path.closeSubpath()

        p.save()
        p.setPen(QPen(QColor("#ffffff"), 2))
        p.setBrush(QBrush(color))
        p.drawPath(path)
        p.restore()
    def draw_down_triangle(self, p: QPainter, x, y, w, h, color: QColor):
        path = QPainterPath()
        path.moveTo(x, y + h / 2)
        path.lineTo(x - w / 2, y - h / 2)
        path.lineTo(x + w / 2, y - h / 2)
        path.closeSubpath()

        p.save()
        p.setPen(QPen(QColor("#ffffff"), 2))
        p.setBrush(QBrush(color))
        p.drawPath(path)
        p.restore()
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
        self.clock_minutes = 0
        self.clock_seconds = 0
        self.clock_running = False
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
        self.home_event_flag = False
        self.away_event_flag = False
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
        self.home_event_flag_active = False
        self.away_event_flag_active = False
        self.home_event_text = ""
        self.home_event_flag_text = ""
        self.away_event_active = False
        self.away_event_text = ""
        self.away_event_flag_text = ""
        self.stat_upper_text = ""
        self.period = 1
        self.vbperiod = 1
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
        self.weather_temp = "--"
        self.weather_humidity = "--"
        self.weather_wind = "--"
        self.weather_condition = "---"
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
        self.home_event_flag_animating = False
        self.home_event_flag_progress = 0.0
        self.home_event_flag_start_time = None
        self.home_event_flag_direction = 1
        self.away_event_flag_animating = False
        self.away_event_flag_progress = 0.0
        self.away_event_flag_start_time = None
        self.away_event_flag_direction = 1
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
        self.series_history_active = False
        self.series_history_animating = False
        self.series_history_progress = 0.0
        self.series_history_start_time = None
        self.series_history_direction = 1
        self.series_away_score = "0"
        self.series_home_score = "0"
        self.series_date = "DATE"
        self.series_stat1 = "Note or Stat 1"
        self.series_stat2 = "Note or Stat 2"
        self.series_stat3 = "Note or Stat 3"
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
        self.lower3rdbigtitle = "Player Name"
        self.lower3rd_text = "STATS"
        self.lower3rdsmalltitle = "Team & Mascot Name"
        self.intro_active = False
        self.intro_animating = False
        self.intro_progress = 0.0
        self.intro_start_time = None
        self.intro_direction = 1
        self.vbscorebug_active = False
        self.vbscorebug_animating = False
        self.vbscorebug_progress = 0.0
        self.vbscorebug_start_time = None
        self.vbscorebug_direction = 1
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
        self.soccer_active = False
        self.soccer_animating = False
        self.soccer_progress = 0.0
        self.soccer_start_time = None
        self.soccer_direction = 1
        self.bsaway_score = 0
        self.bshome_score = 0
        self.inning = 1
        self.top_inning = True
        self.balls = 0
        self.strikes = 0
        self.outs = 0
        self.bspossession = "top"
        self.first_base = False
        self.second_base = False
        self.third_base = False
        self.pitch_count = 0
        self.weather_active = False
        self.weather_animating = False
        self.weather_progress = 0.0
        self.weather_start_time = None
        self.weather_direction = 1
        self.crew_active = False
        self.crew_animating = False
        self.crew_progress = 0.0
        self.crew_start_time = None
        self.crew_direction = 1
        self.crew3_active = False
        self.crew3_animating = False
        self.crew3_progress = 0.0
        self.crew3_start_time = None
        self.crew3_direction = 1
        self.crew4_active = False
        self.crew4_animating = False
        self.crew4_progress = 0.0
        self.crew4_start_time = None
        self.crew4_direction = 1
        self.lower3rd_active = False
        self.lower3rd_animating = False
        self.lower3rd_progress = 0.0
        self.lower3rd_start_time = None
        self.lower3rd_direction = 1
        self.lower3rd_active = False
        self.lower3rd_animating = False
        self.lower3rd_progress = 0.0
        self.lower3rd_start_time = None
        self.lower3rd_direction = 1
        self.ktv_active = False
        self.ltv_animating = False
        self.ktv_progress = 0.0
        self.ktv_start_time = None
        self.ktv_direction = 1
        self.sh_active = False
        self.sh_animating = False
        self.sh_progress = 0.0
        self.sh_start_time = None
        self.sh_direction = 1
        self.top_text = "High School Football"
        self.crew_playbyplay_name = "First Last"
        self.crew_color_name = "First Last"
        self.crew_director_name = "First Last"
        self.crew_td_name = "First Last"
        self.crew_camera_name = "First Last"
        self.crew_field_camera_name = "First Last"  
        self.team_side = "center"
    
state = ScoreState()

class UIUpdater(QObject):
    refresh = Signal()
ui_updater = UIUpdater()

