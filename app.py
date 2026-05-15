from flask import Flask, jsonify, request, render_template_string, session, redirect, url_for
import datetime
import sqlite3
import os
import hashlib

app = Flask(__name__)
app.secret_key = 'securecloud-secret-2025'
DB = '/app/data/platform.db'

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT NOT NULL,
        details TEXT,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    # Compte admin par defaut
    admin_pass = hash_password('admin123')
    c.execute("INSERT OR IGNORE INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
              ('Admin', 'admin@cloud.local', admin_pass, 'admin'))
    conn.commit()
    conn.close()

def get_user_by_email(email):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    conn.close()
    return dict(user) if user else None

def log_action(action, details=''):
    conn = sqlite3.connect(DB)
    conn.execute("INSERT INTO logs (action, details) VALUES (?, ?)", (action, details))
    conn.commit()
    conn.close()

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated

LOGIN_PAGE = '''
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>SecureCloud — Connexion</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#09090b;color:#fafafa;min-height:100vh;display:flex;align-items:center;justify-content:center}
.box{background:#111114;border:1px solid rgba(255,255,255,0.08);border-radius:16px;padding:40px;width:100%;max-width:400px}
.logo{display:flex;align-items:center;gap:10px;margin-bottom:32px;justify-content:center}
.logo-icon{width:40px;height:40px;border-radius:10px;background:#6366f1;display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:700;color:#fff}
.logo-name{font-size:18px;font-weight:700;color:#fafafa}
h2{font-size:20px;font-weight:700;margin-bottom:6px;text-align:center}
.sub{font-size:13px;color:#71717a;text-align:center;margin-bottom:28px}
.form-group{margin-bottom:16px}
label{font-size:12px;font-weight:500;color:#a1a1aa;display:block;margin-bottom:6px}
input{width:100%;padding:11px 14px;border-radius:8px;border:1px solid rgba(255,255,255,0.1);background:#18181b;color:#fafafa;font-size:14px;outline:none;transition:border 0.2s}
input:focus{border-color:#6366f1}
.btn{width:100%;padding:12px;border-radius:8px;background:#6366f1;color:#fff;font-size:14px;font-weight:600;border:none;cursor:pointer;margin-top:8px;transition:opacity 0.2s}
.btn:hover{opacity:0.88}
.error{background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);color:#f87171;padding:10px 14px;border-radius:8px;font-size:13px;margin-bottom:16px;text-align:center}
.register-link{text-align:center;margin-top:20px;font-size:13px;color:#71717a}
.register-link a{color:#818cf8;text-decoration:none;font-weight:500}
.register-link a:hover{text-decoration:underline}
.divider{text-align:center;color:#3f3f46;font-size:12px;margin:16px 0;position:relative}
.divider::before,.divider::after{content:"";position:absolute;top:50%;width:42%;height:1px;background:#27272a}
.divider::before{left:0}.divider::after{right:0}
</style>
</head>
<body>
<div class="box">
  <div class="logo">
    <div class="logo-icon">SC</div>
    <div class="logo-name">SecureCloud</div>
  </div>
  <h2>Connexion</h2>
  <p class="sub">Connectez-vous a votre compte</p>
  {% if error %}<div class="error">{{ error }}</div>{% endif %}
  <form method="POST" action="/login">
    <div class="form-group">
      <label>Adresse email</label>
      <input type="email" name="email" placeholder="votre@email.com" required>
    </div>
    <div class="form-group">
      <label>Mot de passe</label>
      <input type="password" name="password" placeholder="••••••••" required>
    </div>
    <button type="submit" class="btn">Se connecter</button>
  </form>
  <div class="divider">ou</div>
  <div class="register-link">
    Pas encore de compte ? <a href="/register">Creer un compte</a>
  </div>
</div>
</body>
</html>
'''

REGISTER_PAGE = '''
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>SecureCloud — Inscription</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#09090b;color:#fafafa;min-height:100vh;display:flex;align-items:center;justify-content:center}
.box{background:#111114;border:1px solid rgba(255,255,255,0.08);border-radius:16px;padding:40px;width:100%;max-width:400px}
.logo{display:flex;align-items:center;gap:10px;margin-bottom:32px;justify-content:center}
.logo-icon{width:40px;height:40px;border-radius:10px;background:#6366f1;display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:700;color:#fff}
.logo-name{font-size:18px;font-weight:700;color:#fafafa}
h2{font-size:20px;font-weight:700;margin-bottom:6px;text-align:center}
.sub{font-size:13px;color:#71717a;text-align:center;margin-bottom:28px}
.form-group{margin-bottom:16px}
label{font-size:12px;font-weight:500;color:#a1a1aa;display:block;margin-bottom:6px}
input{width:100%;padding:11px 14px;border-radius:8px;border:1px solid rgba(255,255,255,0.1);background:#18181b;color:#fafafa;font-size:14px;outline:none;transition:border 0.2s}
input:focus{border-color:#6366f1}
.btn{width:100%;padding:12px;border-radius:8px;background:#6366f1;color:#fff;font-size:14px;font-weight:600;border:none;cursor:pointer;margin-top:8px;transition:opacity 0.2s}
.btn:hover{opacity:0.88}
.error{background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);color:#f87171;padding:10px 14px;border-radius:8px;font-size:13px;margin-bottom:16px;text-align:center}
.success{background:rgba(34,197,94,0.1);border:1px solid rgba(34,197,94,0.3);color:#4ade80;padding:10px 14px;border-radius:8px;font-size:13px;margin-bottom:16px;text-align:center}
.login-link{text-align:center;margin-top:20px;font-size:13px;color:#71717a}
.login-link a{color:#818cf8;text-decoration:none;font-weight:500}
.hint{font-size:11px;color:#52525b;margin-top:4px}
</style>
</head>
<body>
<div class="box">
  <div class="logo">
    <div class="logo-icon">SC</div>
    <div class="logo-name">SecureCloud</div>
  </div>
  <h2>Creer un compte</h2>
  <p class="sub">Rejoignez la plateforme SecureCloud</p>
  {% if error %}<div class="error">{{ error }}</div>{% endif %}
  {% if success %}<div class="success">{{ success }}</div>{% endif %}
  <form method="POST" action="/register">
    <div class="form-group">
      <label>Nom complet</label>
      <input type="text" name="name" placeholder="Votre nom" required>
    </div>
    <div class="form-group">
      <label>Adresse email</label>
      <input type="email" name="email" placeholder="votre@email.com" required>
    </div>
    <div class="form-group">
      <label>Mot de passe</label>
      <input type="password" name="password" placeholder="Min. 6 caracteres" required minlength="6">
      <div class="hint">Minimum 6 caracteres</div>
    </div>
    <div class="form-group">
      <label>Confirmer le mot de passe</label>
      <input type="password" name="confirm" placeholder="Repetez le mot de passe" required>
    </div>
    <button type="submit" class="btn">Creer mon compte</button>
  </form>
  <div class="login-link">
    Deja un compte ? <a href="/login">Se connecter</a>
  </div>
</div>
</body>
</html>
'''

DASHBOARD_PAGE = '''
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>SecureCloud — Dashboard</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#09090b;color:#fafafa;min-height:100vh}
.nav{background:#111114;border-bottom:1px solid rgba(255,255,255,0.08);padding:0 32px;height:56px;display:flex;align-items:center;justify-content:space-between}
.nav-left{display:flex;align-items:center;gap:10px}
.logo-icon{width:32px;height:32px;border-radius:8px;background:#6366f1;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:700;color:#fff}
.nav-name{font-size:15px;font-weight:600}
.nav-right{display:flex;align-items:center;gap:12px}
.user-badge{font-size:12px;color:#a1a1aa;background:#18181b;padding:5px 12px;border-radius:6px;border:1px solid rgba(255,255,255,0.08)}
.logout-btn{font-size:12px;color:#f87171;background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.2);padding:5px 12px;border-radius:6px;cursor:pointer;text-decoration:none}
.logout-btn:hover{background:rgba(239,68,68,0.2)}
.main{padding:40px 32px}
.welcome{margin-bottom:32px}
.welcome h1{font-size:26px;font-weight:700;margin-bottom:6px}
.welcome p{font-size:14px;color:#71717a}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:16px;margin-bottom:32px}
.stat-card{background:#111114;border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:20px}
.stat-card .num{font-size:30px;font-weight:700;font-family:monospace}
.stat-card .lbl{font-size:12px;color:#71717a;margin-top:4px;text-transform:uppercase;letter-spacing:0.06em}
.section{background:#111114;border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:24px;margin-bottom:20px}
.section h2{font-size:14px;font-weight:600;color:#a1a1aa;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:16px}
table{width:100%;border-collapse:collapse;font-size:13px}
th{text-align:left;padding:8px 12px;color:#52525b;font-size:11px;text-transform:uppercase;letter-spacing:0.06em;border-bottom:1px solid rgba(255,255,255,0.06)}
td{padding:10px 12px;border-bottom:1px solid rgba(255,255,255,0.04);color:#d4d4d8}
tr:last-child td{border-bottom:none}
.role-badge{font-size:10px;padding:2px 8px;border-radius:5px;font-weight:600}
.admin{background:rgba(99,102,241,0.15);color:#818cf8}
.developer{background:rgba(34,197,94,0.15);color:#4ade80}
.user{background:rgba(161,161,170,0.15);color:#a1a1aa}
</style>
</head>
<body>
<nav class="nav">
  <div class="nav-left">
    <div class="logo-icon">SC</div>
    <span class="nav-name">SecureCloud Platform</span>
  </div>
  <div class="nav-right">
    <span class="user-badge">{{ session.user.name }} — {{ session.user.role }}</span>
    <a href="/logout" class="logout-btn">Deconnexion</a>
  </div>
</nav>
<div class="main">
  <div class="welcome">
    <h1>Bonjour, {{ session.user.name }} !</h1>
    <p>Bienvenue sur SecureCloud Platform — {{ now }}</p>
  </div>
  <div class="grid">
    <div class="stat-card"><div class="num" style="color:#22c55e">{{ stats.users }}</div><div class="lbl">Utilisateurs</div></div>
    <div class="stat-card"><div class="num" style="color:#60a5fa">{{ stats.logs }}</div><div class="lbl">Actions loggees</div></div>
    <div class="stat-card"><div class="num" style="color:#a855f7">2.0</div><div class="lbl">Version API</div></div>
    <div class="stat-card"><div class="num" style="color:#f97316">OK</div><div class="lbl">Statut</div></div>
  </div>
  <div class="section">
    <h2>Utilisateurs de la plateforme</h2>
    <table>
      <tr><th>ID</th><th>Nom</th><th>Email</th><th>Role</th><th>Cree le</th></tr>
      {% for u in users %}
      <tr>
        <td>{{ u.id }}</td>
        <td>{{ u.name }}</td>
        <td>{{ u.email }}</td>
        <td><span class="role-badge {{ u.role }}">{{ u.role }}</span></td>
        <td>{{ u.created_at }}</td>
      </tr>
      {% endfor %}
    </table>
  </div>
  <div class="section">
    <h2>Derniers logs</h2>
    <table>
      <tr><th>Action</th><th>Details</th><th>Timestamp</th></tr>
      {% for l in logs %}
      <tr><td>{{ l.action }}</td><td>{{ l.details }}</td><td>{{ l.timestamp }}</td></tr>
      {% endfor %}
    </table>
  </div>
</div>
</body>
</html>
'''

@app.route('/')
@login_required
def home():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    users = [dict(u) for u in conn.execute("SELECT * FROM users ORDER BY id").fetchall()]
    logs = [dict(l) for l in conn.execute("SELECT * FROM logs ORDER BY id DESC LIMIT 10").fetchall()]
    stats = {
        "users": conn.execute("SELECT COUNT(*) FROM users").fetchone()[0],
        "logs": conn.execute("SELECT COUNT(*) FROM logs").fetchone()[0]
    }
    conn.close()
    return render_template_string(DASHBOARD_PAGE,
        session=session,
        users=users,
        logs=logs,
        stats=stats,
        now=datetime.datetime.now().strftime('%d/%m/%Y %H:%M'))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email','').strip()
        password = request.form.get('password','')
        user = get_user_by_email(email)
        if user and user['password'] == hash_password(password):
            session['user'] = {'id':user['id'],'name':user['name'],'email':user['email'],'role':user['role']}
            log_action('LOGIN', f"{user['name']} connecte")
            return redirect('/')
        return render_template_string(LOGIN_PAGE, error='Email ou mot de passe incorrect')
    return render_template_string(LOGIN_PAGE, error=None)

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name','').strip()
        email = request.form.get('email','').strip()
        password = request.form.get('password','')
        confirm = request.form.get('confirm','')
        if not name or not email or not password:
            return render_template_string(REGISTER_PAGE, error='Tous les champs sont obligatoires', success=None)
        if len(password) < 6:
            return render_template_string(REGISTER_PAGE, error='Mot de passe trop court (min. 6 caracteres)', success=None)
        if password != confirm:
            return render_template_string(REGISTER_PAGE, error='Les mots de passe ne correspondent pas', success=None)
        try:
            conn = sqlite3.connect(DB)
            conn.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                        (name, email, hash_password(password), 'user'))
            conn.commit()
            conn.close()
            log_action('REGISTER', f"Nouveau compte: {name} ({email})")
            return render_template_string(REGISTER_PAGE, error=None, success='Compte cree ! Vous pouvez vous connecter.')
        except sqlite3.IntegrityError:
            return render_template_string(REGISTER_PAGE, error='Cet email est deja utilise', success=None)
    return render_template_string(REGISTER_PAGE, error=None, success=None)

@app.route('/logout')
def logout():
    if 'user' in session:
        log_action('LOGOUT', f"{session['user']['name']} deconnecte")
    session.clear()
    return redirect('/login')

@app.route('/health')
def health():
    return jsonify({"status":"ok","service":"flask-api","version":"2.0","time":str(datetime.datetime.now())})

@app.route('/api/users', methods=['GET'])
@login_required
def get_users():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    users = conn.execute("SELECT id,name,email,role,created_at FROM users").fetchall()
    conn.close()
    return jsonify([dict(u) for u in users])

@app.route('/api/stats', methods=['GET'])
@login_required
def get_stats():
    conn = sqlite3.connect(DB)
    users_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    logs_count = conn.execute("SELECT COUNT(*) FROM logs").fetchone()[0]
    conn.close()
    return jsonify({"users":users_count,"logs":logs_count,"version":"2.0"})

@app.route('/api/logs', methods=['GET'])
@login_required
def get_logs():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    logs = conn.execute("SELECT * FROM logs ORDER BY id DESC LIMIT 50").fetchall()
    conn.close()
    return jsonify([dict(l) for l in logs])

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
