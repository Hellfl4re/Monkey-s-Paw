"""A tiny, no-account Monkey's Paw party game for Flask hosts."""

from __future__ import annotations

import os
import random
import re
import secrets
import threading
from datetime import datetime

from flask import Flask, redirect, render_template_string, request, session, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))

# Rooms are intentionally ephemeral: no database or account setup is needed.
rooms: dict[str, dict] = {}
rooms_lock = threading.RLock()

STYLE = """
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600;700;800&family=Fredoka:wght@500;600;700&display=swap');
:root{--ink:#241d34;--muted:#777188;--paper:#fffaf0;--purple:#6d4ce3;--orange:#f47849;--line:#eee8dc;--green:#286854}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at 10% 0%,#f1eaff 0,transparent 34%),radial-gradient(ellipse at 95% 95%,#fff0dc 0,transparent 32%),var(--paper);color:var(--ink);font:16px 'DM Sans',sans-serif;min-height:100vh}
.wrap{max-width:1000px;margin:auto;padding:26px 24px 60px}.top{display:flex;align-items:center;justify-content:space-between;margin-bottom:36px}.brand{display:flex;align-items:center;gap:11px;text-decoration:none;color:inherit;font:700 21px Fredoka,sans-serif}.paw{width:40px;height:40px;background:var(--purple);border-radius:14px;display:grid;place-items:center;color:white;font-size:22px;box-shadow:0 5px 0 #4e35b4}.tag{color:var(--muted);font-size:13px}.hero{max-width:620px;margin:50px auto 38px;text-align:center}.eyebrow{color:var(--purple);font:500 12px 'DM Mono',monospace;letter-spacing:1.3px;text-transform:uppercase}.hero h1{font:700 clamp(42px,7vw,67px)/1.03 Fredoka,sans-serif;letter-spacing:-2px;margin:14px 0}.hero h1 span{color:var(--orange)}.hero p{color:var(--muted);font-size:17px;line-height:1.65;margin:14px auto 0;max-width:510px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px;max-width:760px;margin:0 auto}.card{background:#fff;border:1px solid var(--line);border-radius:22px;padding:27px;box-shadow:0 12px 35px #35264b0a}.card h2,.section-title{font:600 22px Fredoka,sans-serif;margin:0 0 7px}.card p{color:var(--muted);line-height:1.5;margin:0 0 22px;font-size:14px}.icon{font-size:28px;margin-bottom:16px}.field{display:block;font-weight:700;font-size:13px;margin:16px 0 7px}.input{width:100%;border:1.5px solid #e7e1ee;background:#fffdf9;border-radius:12px;padding:13px 14px;font:500 15px 'DM Sans',sans-serif;color:var(--ink);outline:none}.input:focus{border-color:var(--purple);box-shadow:0 0 0 3px #6d4ce31c}.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;border:0;border-radius:12px;padding:13px 17px;background:var(--purple);color:white;font:700 15px 'DM Sans',sans-serif;cursor:pointer;text-decoration:none;box-shadow:0 4px 0 #4e35b4;width:100%;margin-top:14px}.btn:hover{filter:brightness(1.06);transform:translateY(-1px)}.btn.orange{background:var(--orange);box-shadow:0 4px 0 #ca5730}.btn.light{color:var(--purple);background:#f0ebff;box-shadow:none}.hint{font-size:12px;color:var(--muted);margin-top:12px}.rules{max-width:760px;margin:25px auto 0;display:flex;align-items:center;gap:12px;color:var(--muted);font-size:13px;justify-content:center;flex-wrap:wrap}.pill{background:#f0ebff;color:#6246c2;border-radius:30px;padding:7px 12px;font-size:12px;font-weight:700}.room-head{display:flex;justify-content:space-between;align-items:center;gap:15px;margin:20px 0 24px}.room-code{font:500 20px 'DM Mono',monospace;letter-spacing:3px;background:#f0ebff;color:#5139b2;padding:11px 15px;border-radius:12px}.panel{background:#fff;border:1px solid var(--line);border-radius:20px;padding:24px;margin-bottom:16px}.players{display:flex;gap:9px;flex-wrap:wrap;margin-top:14px}.player{display:flex;align-items:center;gap:8px;background:#faf7ff;border:1px solid #eee8fb;border-radius:99px;padding:8px 13px;font-size:14px;font-weight:600}.dot{width:9px;height:9px;border-radius:50%;background:#76b49b}.turn{background:#fff5e8;color:#a75726}.wishbox{background:#28213b;color:white;border-radius:20px;padding:24px;margin:16px 0}.wishbox h2{font:600 22px Fredoka,sans-serif;margin:0 0 7px}.wishbox p{color:#d2ccdf;margin:0}.wishbox .field{color:white}.wishbox .input{background:#fff}.result{border-left:4px solid var(--orange);background:#fff7ef;border-radius:0 16px 16px 0;padding:19px 22px;margin-top:15px}.result blockquote{font:600 18px Fredoka,sans-serif;margin:8px 0;color:#5139b2}.result p{line-height:1.6;margin:8px 0 0}.feed{display:grid;gap:12px;margin-top:14px}.feeditem{border-bottom:1px solid var(--line);padding:0 0 13px}.feeditem:last-child{border:0;padding:0}.feeditem small{color:var(--muted)}.feeditem p{margin:6px 0;line-height:1.5}.empty{color:var(--muted);padding:12px 0}.notice{max-width:760px;margin:0 auto 18px;padding:13px 16px;border-radius:12px;background:#fff1e9;color:#9a4926;font-weight:600}.footer{text-align:center;color:#9b95a6;font-size:12px;margin-top:35px}
@media(max-width:650px){.wrap{padding:19px 15px 40px}.top{margin-bottom:15px}.tag{display:none}.hero{margin:35px auto 27px}.grid{grid-template-columns:1fr;gap:13px}.card{padding:22px}.room-head{align-items:flex-start;flex-direction:column}.room-code{font-size:17px}.panel{padding:19px}}
"""

BASE = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#fffaf0">{% if live_refresh %}<meta http-equiv="refresh" content="3">{% endif %}<title>{{ title }} · Monkey's Paw</title><style>""" + STYLE + """</style></head><body><div class="wrap"><header class="top"><a class="brand" href="{{ url_for('home') }}"><span class="paw">✦</span> Monkey's Paw</a><span class="tag">A little wishful thinking. A lot of questionable outcomes.</span></header>{% if notice %}<div class="notice">{{ notice }}</div>{% endif %}{{ body|safe }}<div class="footer">No accounts. No downloads. Just one suspiciously helpful paw. 🐾</div></div></body></html>"""

HOME = """
<main><section class="hero"><div class="eyebrow">✦ The wish-granting party game ✦</div><h1>Wish big.<br><span>Regret creatively.</span></h1><p>Make a wish, then let the Monkey's Paw twist it into something gloriously inconvenient. Grab your friends and see what fate has in store.</p></section>
<section class="grid"><form class="card" method="post" action="{{ url_for('create_room') }}"><div class="icon">🪄</div><h2>Start a new game</h2><p>You'll get a room code to share with your friends.</p><label class="field" for="host">Your nickname</label><input class="input" id="host" name="name" maxlength="18" placeholder="e.g. Wisher-in-Chief" required><button class="btn" type="submit">Create a room <span>→</span></button></form>
<form class="card" method="post" action="{{ url_for('join_room') }}"><div class="icon">🚪</div><h2>Join a room</h2><p>Already got a code? Pop in and join the wishes.</p><label class="field" for="joinname">Your nickname</label><input class="input" id="joinname" name="name" maxlength="18" placeholder="What should we call you?" required><label class="field" for="code">Room code</label><input class="input" id="code" name="code" maxlength="5" placeholder="e.g. PAW42" required style="text-transform:uppercase;letter-spacing:3px;font-family:'DM Mono',monospace"><button class="btn orange" type="submit">Join the fun <span>→</span></button></form></section>
<div class="rules"><span class="pill">2+ players</span><span>One wish each turn</span><span>·</span><span>Everyone else writes a catch</span><span>·</span><span>Room updates automatically</span></div></main>"""

ROOM = """
<main><div class="room-head"><div><div class="eyebrow">Your wishing circle</div><h1 style="font:700 36px Fredoka,sans-serif;margin:6px 0 0">The room is open</h1></div><div class="room-code" title="Share this code with friends">{{ room.code }}</div></div>
<section class="panel"><div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap"><div><h2 class="section-title">Who's here?</h2><span class="hint">Share the room code so everyone can join.</span></div><span class="pill">{{ room.players|length }} player{{ '' if room.players|length == 1 else 's' }}</span></div><div class="players">{% for p in room.players %}<div class="player"><span class="dot"></span>{{ p.name }}{% if p.id == player_id %}<span class="pill" style="padding:3px 8px">you</span>{% endif %}</div>{% endfor %}</div>
{% if room.players|length < 2 %}<p class="hint" style="margin-top:16px">Waiting for one more wisher… The paw is getting impatient.</p>{% endif %}</section>
{% if room.players|length >= 2 and not active %}<section class="wishbox"><h2>{% if current and current.id == player_id %}Your turn, {{ current.name }}!{% else %}{{ current.name if current else 'The wishing circle' }} is up next{% endif %}</h2><p>{% if current and current.id == player_id %}Make a wish. Everyone else will invent the catches.{% else %}Waiting for {{ current.name if current else 'the next player' }} to make a wish…{% endif %}</p>{% if current and current.id == player_id %}<form method="post" action="{{ url_for('make_wish', code=room.code) }}"><label class="field" for="wish">I wish…</label><input class="input" id="wish" name="wish" maxlength="180" placeholder="…for a million dollars" required><button class="btn orange" type="submit">Make your wish <span>✦</span></button></form>{% endif %}</section>{% endif %}
{% if active %}<section class="panel"><div class="eyebrow">Wish in progress</div><h2 class="section-title" style="margin-top:8px">{{ active.name }} wished…</h2><div class="result"><blockquote>“{{ active.wish }}”</blockquote></div><p style="font-weight:700;margin:20px 0 5px">The catch writers are thinking…</p><span class="pill">{{ active.catches|length }} of {{ active.eligible|length }} catches in</span>
{% if player_id in active.eligible and player_id not in active.catches %}<form method="post" action="{{ url_for('add_catch', code=room.code) }}"><label class="field" for="catch">Add your catch</label><input class="input" id="catch" name="catch" maxlength="180" placeholder="…but the money is all in coins" required><button class="btn orange" type="submit">Add my catch <span>✦</span></button></form>{% elif player_id in active.catches %}<p class="hint">Your catch is in! It stays secret until everyone has written one.</p>{% elif player_id == active.wisher_id %}<p class="hint">Everyone else is writing a catch. The reveal is almost ready…</p>{% else %}<p class="hint">This round started before you joined, so watch the reveal!</p>{% endif %}</section>{% endif %}
<section class="panel"><h2 class="section-title">The wish ledger</h2>{% if room.wishes %}<div class="feed">{% for w in room.wishes|reverse %}<article class="feeditem"><small>{{ w.time }} · {{ w.name }} wished</small><div class="result"><blockquote>“{{ w.wish }}”</blockquote>{% for c in w.catches %}<p><b>{{ c.name }}'s catch:</b> {{ c.catch }}</p>{% endfor %}</div></article>{% endfor %}</div>{% else %}<div class="empty">No wishes yet. Every legend starts with a questionable idea.</div>{% endif %}</section>
<p class="hint" style="text-align:center">This room updates automatically every few seconds.</p></main>"""

def page(title: str, body: str, notice: str = ""):
    return render_template_string(BASE, title=title, body=render_template_string(body), notice=notice, live_refresh=False)


def clean_name(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())[:18]


def participant(room: dict, player_id: str) -> dict | None:
    return next((p for p in room["players"] if p["id"] == player_id), None)


@app.get("/")
def home():
    session.setdefault("player_id", secrets.token_urlsafe(12))
    return page("Make a wish", HOME)


@app.post("/create")
def create_room():
    name = clean_name(request.form.get("name"))
    if not name:
        return page("Make a wish", HOME, "Pick a nickname first so your friends know who to blame.")
    with rooms_lock:
        code = "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=5))
        while code in rooms:
            code = "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=5))
        pid = session.setdefault("player_id", secrets.token_urlsafe(12))
        rooms[code] = {"code": code, "players": [{"id": pid, "name": name}], "wishes": [], "turn": 0, "active": None}
        session["room"] = code
    return redirect(url_for("show_room", code=code))


@app.post("/join")
def join_room():
    code = re.sub(r"[^A-Z0-9]", "", request.form.get("code", "").upper())[:5]
    name = clean_name(request.form.get("name"))
    if not name:
        return page("Join a room", HOME, "Pick a nickname before joining the wishing circle.")
    with rooms_lock:
        room = rooms.get(code)
        if not room:
            return page("Room not found", HOME, "That room code didn't work. Double-check it with your host and try again.")
        pid = session.setdefault("player_id", secrets.token_urlsafe(12))
        existing = participant(room, pid)
        if existing:
            existing["name"] = name
        else:
            room["players"].append({"id": pid, "name": name})
        session["room"] = code
    return redirect(url_for("show_room", code=code))


@app.get("/room/<code>")
def show_room(code):
    code = code.upper()
    with rooms_lock:
        room = rooms.get(code)
        if not room:
            return page("Room not found", HOME, "This room has vanished into the paw's mysterious archives. Start a new one!")
        pid = session.get("player_id")
        player = participant(room, pid) if pid else None
        if not player:
            return redirect(url_for("home"))
        current = room["players"][room["turn"] % len(room["players"])] if room["players"] else None
        active = room["active"]
        has_open_form = (active is None and current and current["id"] == pid) or (active and pid in active["eligible"] and pid not in active["catches"])
        return render_template_string(BASE, title=f"Room {code}", body=render_template_string(ROOM, room=room, player_id=pid, current=current, active=active), notice="", live_refresh=not has_open_form)


@app.post("/room/<code>/wish")
def make_wish(code):
    wish = re.sub(r"\s+", " ", request.form.get("wish", "").strip())[:180]
    with rooms_lock:
        room = rooms.get(code.upper())
        if not room:
            return redirect(url_for("home"))
        pid = session.get("player_id")
        player = participant(room, pid) if pid else None
        if not player or len(room["players"]) < 2:
            return redirect(url_for("show_room", code=room["code"]))
        current = room["players"][room["turn"] % len(room["players"])]
        if current["id"] == pid and wish and room["active"] is None:
            eligible = [p["id"] for p in room["players"] if p["id"] != pid]
            room["active"] = {"wisher_id": pid, "name": player["name"], "wish": wish, "eligible": eligible, "catches": {}, "time": datetime.now().strftime("%I:%M %p").lstrip("0")}
    return redirect(url_for("show_room", code=code.upper()))


@app.post("/room/<code>/catch")
def add_catch(code):
    catch = re.sub(r"\s+", " ", request.form.get("catch", "").strip())[:180]
    with rooms_lock:
        room = rooms.get(code.upper())
        if not room:
            return redirect(url_for("home"))
        pid = session.get("player_id")
        player = participant(room, pid) if pid else None
        active = room["active"]
        if player and active and catch and pid in active["eligible"] and pid not in active["catches"]:
            active["catches"][pid] = {"name": player["name"], "catch": catch}
            if all(eligible_id in active["catches"] for eligible_id in active["eligible"]):
                room["wishes"].append({"name": active["name"], "wish": active["wish"], "catches": list(active["catches"].values()), "time": active["time"]})
                room["active"] = None
                room["turn"] += 1
    return redirect(url_for("show_room", code=code.upper()))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False, threaded=True)
