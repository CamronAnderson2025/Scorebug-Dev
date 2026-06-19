from flask import Flask, jsonify, request
import re
from flask_cors import CORS
from PySide6.QtCore import QTimer, QMetaObject, Qt, Q_ARG
import logging
import urllib.request
import socket

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

scoreboard_ref = None


# =====================================================
# INIT
# =====================================================

def init_backend(scoreboard):
    global scoreboard_ref
    scoreboard_ref = scoreboard

# =====================================================
# LAN IP HELPER (ADDED)
# =====================================================

def get_lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

# =====================================================
# QT HELPERS
# =====================================================

def qt_call(method_name: str):

    if not scoreboard_ref:
        return False

    try:
        method = getattr(
            scoreboard_ref,
            method_name,
            None
        )

        if not callable(method):
            print(
                f"[QT] Missing method: "
                f"{method_name}"
            )
            return False

        QMetaObject.invokeMethod(
            scoreboard_ref,
            method_name,
            Qt.QueuedConnection
        )

        return True

    except Exception as e:
        print(
            "QT CALL ERROR:",
            e
        )
        return False


def qt_call_arg(
    method_name: str,
    *args
):

    if not scoreboard_ref:
        return False

    try:

        method = getattr(
            scoreboard_ref,
            method_name,
            None
        )

        if not callable(method):
            print(
                f"[QT] Missing method: "
                f"{method_name}"
            )
            return False

        method(*args)

        return True

    except Exception as e:
        print(
            "QT ARG ERROR:",
            e
        )
        return False


# =====================================================
# STATE HELPERS
# =====================================================
 
def _state():

    if not scoreboard_ref:
        return None

    return getattr(
        scoreboard_ref,
        "state",
        None
    )


def _safe_down(value):

    return max(
        1,
        min(4, value)
    )
@app.route("/football/server-info", methods=["GET", "POST"])
def server_info():
    return jsonify({
        "localhost": "127.0.0.1:5055",
        "lan": f"{get_lan_ip()}:5055"
    })

# =====================================================
# GAME CLOCK
# =====================================================

@app.route("/football/clock/<mode>", methods=["GET", "POST"])
def football_clock_router(mode):

    CLOCK_ACTIONS = {
        "start": "start_clock",
        "stop": "stop_clock",
        "reset": "reset_clock",
    }

    try:
        if mode not in CLOCK_ACTIONS:
            return f"unknown clock mode: {mode}", 404

        qt_call(CLOCK_ACTIONS[mode])

        return "ok"

    except Exception as e:
        print("CLOCK ERROR:", e)
        return "error", 500

@app.route("/football/clock", methods=["GET"])
def football_clock():
    if not scoreboard_ref:
        return jsonify({
            "game_time": "00:00",
            "play_time": "00",
            "game_running": False,
            "play_running": False
        })

    try:
        s = getattr(scoreboard_ref, "state", None)

        if not s:
            return jsonify({
                "game_time": "00:00",
                "play_time": "00",
                "game_running": False,
                "play_running": False
            })

        # GAME CLOCK
        minutes = getattr(s, "minutes", 0)
        seconds = getattr(s, "seconds", 0)
        game_running = getattr(s, "game_running", False)

        # PLAY CLOCK (your real variable)
        playclock = getattr(s, "playclock", 0)
        play_running = getattr(s, "play_running", False)

        return jsonify({
            "game_time": f"{minutes:02d}:{seconds:02d}",
            "play_time": f"{playclock:02d}",
            "game_running": game_running,
            "play_running": play_running
        })

    except Exception as e:
        print("CLOCK STATE ERROR:", e)
        return jsonify({
            "game_time": "00:00",
            "play_time": "00",
            "game_running": False,
            "play_running": False
        })
# =====================================================
# PLAY CLOCK
# =====================================================

@app.route("/football/playclock/<mode>", methods=["GET", "POST"])
def playclock_router(mode):

    if not scoreboard_ref:
        return "no scoreboard", 500

    PLAYCLOCK_ACTIONS = {
        "40": "set_playclock_40",
        "25": "set_playclock_25",
        "start": "start_play_clock",
        "stop": "stop_play_clock",
    }

    try:
        if mode not in PLAYCLOCK_ACTIONS:
            return f"unknown playclock mode: {mode}", 404

        qt_call(PLAYCLOCK_ACTIONS[mode])

        return "ok"

    except Exception as e:
        print("PLAYCLOCK ERROR:", e)
        return "error", 500


# =====================================================
# FLAG
# =====================================================

import threading

@app.route("/football/flag/<team>/<flag>", methods=["GET", "POST"])
def football_flag(team, flag):

    if not scoreboard_ref:
        return "no scoreboard", 500

    try:
        team = (team or "").lower().strip()

        if team not in ["home", "away"]:
            return "invalid team", 400

        flag_text = (flag or "").replace("-", " ").strip()
        if not flag_text:
            return "invalid flag", 400

        flag_text = flag_text.upper()

        # ---- SET FLAG STATE ----
        if hasattr(scoreboard_ref, "state"):
            scoreboard_ref.state.flag = True
            scoreboard_ref.state.flag_text = "FLAG"

        # ---- SINGLE SOURCE OF TRUTH ----
        if team == "home":
            scoreboard_ref.trigger_home_flag(flag_text)
        else:
            scoreboard_ref.trigger_away_flag(flag_text)

        # =====================================================
        # AUTO CLEAR AFTER 20 SECONDS (NON-BLOCKING)
        # =====================================================
        def auto_clear():
            try:
                football_flag_clear()
            except Exception as e:
                print("AUTO CLEAR FLAG ERROR:", e)

        timer = threading.Timer(20.0, auto_clear)
        timer.daemon = True
        timer.start()

        return "ok"

    except Exception as e:
        print("FLAG ERROR:", e)
        return "error", 500

@app.route("/football/flag/clear", methods=["GET", "POST"])
def football_flag_clear():
    if not scoreboard_ref:
        return "no scoreboard", 500

    try:
        # Use the proper method so animation state is set correctly
        scoreboard_ref.clear_flag_event("Home")
        scoreboard_ref.clear_flag_event("Away")

        # Clean up any lingering background timers
        for team_prefix in ["_home", "_away"]:
            timer_name = f"{team_prefix}_flag_timer"
            if hasattr(scoreboard_ref, timer_name):
                try:
                    timer_instance = getattr(scoreboard_ref, timer_name)
                    if timer_instance:
                        timer_instance.stop()
                        timer_instance.deleteLater()
                except Exception:
                    pass
                setattr(scoreboard_ref, timer_name, None)

        return "ok"

    except Exception as e:
        print("CLEAR FLAG ROUTE ERROR:", e)
        return "error", 500
# =====================================================
# POSSESSION (DIRECT LAMBDA EQUIVALENT)
# =====================================================

@app.route("/football/possession/<possession>", methods=["GET", "POST"])
def possession_router(possession):

    if not scoreboard_ref:
        return "no scoreboard", 500

    try:
        possession = (possession or "").lower().strip()

        def call(method_name):
            fn = getattr(scoreboard_ref, method_name, None)
            if callable(fn):
                fn()

        if possession == "home":
            call("set_home_possession")

        elif possession == "away":
            call("set_away_possession")

        elif possession == "none":
            call("set_none_possession")

        else:
            return f"unknown possession: {possession}", 404

        return "ok"

    except Exception as e:
        print("POSSESSION ERROR:", e)
        return "error", 500
# =====================================================
# TIMEOUTS (FIXED)
# =====================================================

@app.route("/football/timeout/<team>/<mode>", methods=["GET", "POST"])
def football_timeout(team, mode):

    if not scoreboard_ref:
        return "no scoreboard", 500

    try:

        if team not in ["home", "away"]:
            return jsonify({
                "ok": False,
                "error": "invalid team"
            }), 400

        if mode not in [
            "add",
            "take",
        ]:
            return jsonify({
                "ok": False,
                "error": "invalid mode"
            }), 400

        if not hasattr(
            scoreboard_ref,
            "timeouts"
        ):
            scoreboard_ref.timeouts = {
                "home": 3,
                "away": 3
            }
        elif mode == "add":

            scoreboard_ref.timeouts[team] = min(
                3,
                scoreboard_ref.timeouts[team] + 1
            )

        elif mode == "take":

            scoreboard_ref.timeouts[team] = max(
                0,
                scoreboard_ref.timeouts[team] - 1
            )

        if hasattr(
            scoreboard_ref,
            "set_timeouts"
        ):
            scoreboard_ref.set_timeouts()

        return jsonify({
            "ok": True,
            "home": scoreboard_ref.timeouts["home"],
            "away": scoreboard_ref.timeouts["away"],
            "timeouts": scoreboard_ref.timeouts[team]
        })

    except Exception as e:

        print(
            "TIMEOUT ERROR:",
            e
        )

        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500
@app.route(
    "/football/event/reset",
    methods=["GET", "POST"]
)
def football_events_reset():

    if not scoreboard_ref:
        return "no scoreboard", 500

    try:

        s = getattr(
            scoreboard_ref,
            "state",
            None
        )

        if s:

            if getattr(
                s,
                "home_event_active",
                False
            ):
                scoreboard_ref.trigger_home_event("")

            if getattr(
                s,
                "away_event_active",
                False
            ):
                scoreboard_ref.trigger_away_event("")

        return "ok"

    except Exception as e:

        print(
            "EVENT RESET ERROR:",
            e
        )

        return "error", 500
@app.route("/football/event/<type>/<team>",methods=["GET", "POST"])
@app.route("/football/event/<type>/<team>/<value>",methods=["GET", "POST"])
def football_unified(type, team, value=None):

    if not scoreboard_ref:
        return "no scoreboard", 500

    try:

        # -------------------------
        # VALIDATION
        # -------------------------
        if type not in ["2pt", "fg"]:
            return jsonify({"ok": False, "error": "invalid type"}), 400

        if team not in ["home", "away"]:
            return jsonify({"ok": False, "error": "invalid team"}), 400

        # -------------------------
        # 2PT (NO VALUE)
        # -------------------------
        if type == "2pt":

            if team == "home":
                scoreboard_ref.trigger_home_event("2 POINT-ATTEMPT")
            else:
                scoreboard_ref.trigger_away_event("2 POINT-ATTEMPT")

            return jsonify({
                "ok": True,
                "type": "2pt",
                "team": team
            })

        # -------------------------
        # FG (REQUIRES VALUE)
        # -------------------------
        if type == "fg":

            if not value:
                return jsonify({"ok": False, "error": "missing yards"}), 400

            try:
                yards = int(value)
            except:
                return jsonify({"ok": False, "error": "invalid yards"}), 400

            if yards <= 0:
                return jsonify({"ok": False, "error": "invalid yards"}), 400

            label = f"{yards} Yard Attempt"

            if team == "home":
                scoreboard_ref.trigger_home_event(label)
            else:
                scoreboard_ref.trigger_away_event(label)

            return jsonify({
                "ok": True,
                "type": "fg",
                "team": team,
                "yards": yards
            })

    except Exception as e:
        print("FOOTBALL EVENT ERROR:", e)
        return jsonify({"ok": False, "error": str(e)}), 500



# =====================================================
# DOWN
# =====================================================

@app.route("/football/down-distance/<type>/<mode>", methods=["GET", "POST"])
@app.route("/football/down-distance/<type>/<mode>/<value>", methods=["GET", "POST"])
def down_distance(type, mode, value=None):
    if not scoreboard_ref:
        return "no scoreboard", 500
    try:
        sb = scoreboard_ref
        if not hasattr(sb, "_pending_down"):
            sb._pending_down = None
        if not hasattr(sb, "_pending_distance"):
            sb._pending_distance = None
        if type not in ["down", "distance", "system"]:
            return jsonify({"ok": False, "error": "invalid type"}), 400
        def suffix(n):
            return {1: "st", 2: "nd", 3: "rd"}.get(n, "th")
        def get_down():
            try:
                return int(sb.down_spin.currentText())
            except:
                return 1
        def get_dist():
            try:
                return int(sb.dist_edit.currentText())
            except:
                return getattr(sb, "_last_numeric_distance", 10)
        if type == "down":
            if mode == "increase":
                sb._pending_down = min(4, (sb._pending_down or get_down()) + 1)
            elif mode == "decrease":
                sb._pending_down = max(1, (sb._pending_down or get_down()) - 1)
            return jsonify({"ok": True, "type": "down", "pending_down": sb._pending_down})
        if type == "distance":
            if mode == "increase":
                sb._pending_distance = (sb._pending_distance or get_dist()) + 1
            elif mode == "decrease":
                sb._pending_distance = max(1, (sb._pending_distance or get_dist()) - 1)
            elif mode == "set" and value:
                down_map = {"1st": 1, "2nd": 2, "3rd": 3, "4th": 4}
                down = down_map.get(value)
                if not down:
                    return jsonify({"ok": False, "error": "invalid down value"}), 400
                sb._pending_down = down
                display = f"{value} Down"
                sb._last_numeric_distance = sb._pending_distance or get_dist()
                sb.down_spin.setCurrentText(str(down))
                sb.dist_edit.setCurrentText(display)
                sb.set_down_distance()
                return jsonify({"ok": True, "type": "distance", "down": down, "display": display})
            return jsonify({"ok": True, "type": "distance", "pending_distance": sb._pending_distance})
        if type == "system":
            if mode == "reset":
                sb._pending_down = 1
                sb._pending_distance = 10
                sb.down_spin.setCurrentText("1")
                sb.dist_edit.setCurrentText("10")
                sb.set_down_distance()
                return jsonify({"ok": True, "display": "1st & 10"})
            if mode == "goal":
                sb._pending_down = 1
                sb._pending_distance = None
                sb.down_spin.setCurrentText("1")
                sb.dist_edit.setCurrentText("GOAL")
                sb.set_down_distance()
                return jsonify({"ok": True, "display": "1st & GOAL"})
            if mode == "set-dd":
                down = sb._pending_down if sb._pending_down is not None else get_down()
                dist = sb._pending_distance if sb._pending_distance is not None else get_dist()
                sb.down_spin.setCurrentText(str(down))
                sb.dist_edit.setCurrentText(str(dist))
                sb.set_down_distance()
                sb._pending_down = None
                sb._pending_distance = None
                return jsonify({"ok": True, "display": f"{down}{suffix(down)} & {dist}"})
        return jsonify({"ok": False, "error": "invalid type/mode"}), 400
    except Exception as e:
        print("DOWN DISTANCE ERROR:", e)
        return jsonify({"ok": False, "error": str(e)}), 500
# =====================================================
# POINTS
# =====================================================

@app.route("/football/points/<team>/<points>", methods=["GET", "POST"])
def football_points(team, points):

    if not scoreboard_ref:
        return "no scoreboard", 500

    try:
        # convert safely
        try:
            value = int(points)
        except ValueError:
            return jsonify({
                "ok": False,
                "error": "points must be a number"
            }), 400

        if team not in ["home", "away"]:
            return jsonify({
                "ok": False,
                "error": "invalid team"
            }), 400

        # -----------------------------
        # MAIN LOGIC (kept identical)
        # -----------------------------
        if hasattr(scoreboard_ref, "add_points"):

            scoreboard_ref.add_points(value, team)

        elif hasattr(scoreboard_ref, "change_score"):

            scoreboard_ref.change_score(team, value)

        else:

            if team == "home":
                scoreboard_ref.state.home_score += value
            else:
                scoreboard_ref.state.away_score += value

            if hasattr(scoreboard_ref, "repaint_scoreboard"):
                scoreboard_ref.repaint_scoreboard()

        return jsonify({
            "ok": True,
            "team": team,
            "points": value
        })

    except Exception as e:
        print("POINT ERROR:", e)

        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500

# =====================================================
# GRAPHICS
# FIXED: SINGLE PRESS
# =====================================================

# =====================================================
# GRAPHICS
# FIXED: RELIABLE SINGLE TRIGGER + SAFE REFRESH
# =====================================================

@app.route(
    "/football/graphics/<graphic>",
    methods=["GET", "POST"]
)
def graphics_router(graphic):

    if not scoreboard_ref:
        return "no scoreboard", 500

    try:

        GRAPHICS_MAP = {

            "intro":
            getattr(
                scoreboard_ref,
                "show_intro",
                None
            ),

            "weather":
            getattr(
                scoreboard_ref,
                "show_weather",
                None
            ),

            "lower3rd":
            getattr(
                scoreboard_ref,
                "show_lower3rd",
                None
            ),

            "crew":
            getattr(
                scoreboard_ref,
                "show_crew",
                None
            ),

            "crew3":
            getattr(
                scoreboard_ref,
                "show_crew3",
                None
            ),

            "3mancrew":
            getattr(
                scoreboard_ref,
                "show_crew3",
                None
            ),

            "crew4":
            getattr(
                scoreboard_ref,
                "show_crew4",
                None
            ),

            "4mancrew":
            getattr(
                scoreboard_ref,
                "show_crew4",
                None
            ),

            "scorebug":
            getattr(
                scoreboard_ref,
                "show_scorebug",
                None
            ),

            "breakboard":
            getattr(
                scoreboard_ref,
                "show_breakboard",
                None
            ),

            "final":
            getattr(
                scoreboard_ref,
                "show_final",
                None
            )
        }

        func = GRAPHICS_MAP.get(
            graphic
        )

        if not callable(func):
            return (
                f"unknown graphic: {graphic}",
                404
            )

        func(
            force_double=True
        )

        scoreboard_ref.repaint_scoreboard()

        return "ok"

    except Exception as e:

        print(
            "GRAPHICS ERROR:",
            e
        )

        return "error", 500

# =====================================================
# PERIODS
# =====================================================

@app.route("/football/period/<period>", methods=["GET", "POST"])
def football_period(period):

    if not scoreboard_ref:
        return "no scoreboard", 500

    try:
        period = int(period)

        if period not in range(1, 11):
            return jsonify({
                "ok": False,
                "error": "invalid period"
            }), 400

        scoreboard_ref.period_spin.setValue(period)
        scoreboard_ref.set_period()

        return jsonify({
            "ok": True,
            "period": scoreboard_ref.state.period
        })

    except Exception as e:
        print("PERIOD ERROR:", e)
        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500

# =====================================================
# STATE
# =====================================================

@app.route("/football/state")
def football_state():

    s = _state()

    if not s:
        return jsonify({
            "down": 1,
            "distance": 10,
            "home_score": 0,
            "away_score": 0,
            "period": 1,
            "possession": "none",
            "pending_down": None,
            "pending_distance": None
        })

    return jsonify({
        "down": getattr(s, "down", 1),
        "distance": getattr(s, "distance", 10),
        "home_score": getattr(s, "home_score", 0),
        "away_score": getattr(s, "away_score", 0),
        "period": getattr(s, "period", 1),
        "possession": getattr(s, "possession", "none"),
        "pending_down": getattr(scoreboard_ref, "_pending_down", None),
        "pending_distance": getattr(scoreboard_ref, "_pending_distance", None)
    })


# =====================================================
# SERVER
# =====================================================

def start_server():

    logging.basicConfig(
        filename="backend.log",
        level=logging.INFO,
        format="%(asctime)s - %(message)s"
    )

    lan_ip = get_lan_ip()

    print(
        "Football backend running http://127.0.0.1:5055"
    )

    print(
        f"LAN ACCESS: http://{lan_ip}:5055"
    )

    app.run(
        host="0.0.0.0",
        port=5055,
        debug=False,
        use_reloader=False,
        threaded=True
    )