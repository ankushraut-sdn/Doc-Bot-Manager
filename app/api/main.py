import time
import json
from flask import Blueprint, request, make_response, jsonify
from app.models import Bot

main_bp = Blueprint("main", __name__)

@main_bp.get("/api/health")
def health():
    """Application health status endpoint."""
    return jsonify({"ok": True, "time": int(time.time())})

@main_bp.get("/widget/<int:bot_id>")
def serve_widget(bot_id: int):
    """Serve a minimal, self-contained embedded widget UI to interact with the bot."""
    token = request.args.get("token") or ""
    bot = Bot.query.filter_by(id=bot_id, iframe_token=token).first()
    if not bot:
        return make_response("Unauthorized widget token", 401)

    html = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{bot.name} – Chat Widget</title>
  <style>
    body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 0; padding: 0; }}
    .box {{ display: flex; flex-direction: column; height: 100vh; }}
    .msgs {{ flex: 1; overflow-y: auto; padding: 12px; background: #f7f7f8; }}
    .input {{ display: flex; gap: 8px; padding: 12px; border-top: 1px solid #e5e7eb; }}
    .bubble {{ background: white; border: 1px solid #e5e7eb; border-radius: 12px; padding: 10px 12px; margin-bottom: 8px; }}
    .you {{ background: #eef2ff; border-color: #c7d2fe; }}
  </style>
</head>
<body>
<div class="box">
  <div id="msgs" class="msgs"></div>
  <div class="input">
    <input id="q" placeholder="Ask a question..." style="flex:1;padding:10px;border:1px solid #e5e7eb;border-radius:8px" />
    <button id="send">Send</button>
  </div>
</div>
<script>
  const botId = {bot.id};
  const token = {json.dumps(bot.iframe_token)};
  const msgs = document.getElementById('msgs');
  const input = document.getElementById('q');
  const send = document.getElementById('send');

  function push(role, text) {{
    const div = document.createElement('div');
    div.className = 'bubble' + (role === 'you' ? ' you' : '');
    div.textContent = text;
    msgs.appendChild(div);
    msgs.scrollTop = msgs.scrollHeight;
  }}

  send.onclick = async () => {{
    const q = input.value.trim();
    if (!q) return;
    push('you', q); input.value = '';
    const r = await fetch(`/api/bots/${{botId}}/chat?token=${{token}}`, {{
      method: 'POST', headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify({{ question: q }})
    }});
    const data = await r.json();
    push('bot', data.answer || 'No answer');
  }}
</script>
</body>
</html>
"""
    resp = make_response(html)
    resp.headers["Content-Type"] = "text/html; charset=utf-8"
    return resp
