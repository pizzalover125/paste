import os
import sqlite3
import secrets
from datetime import datetime
from flask import Flask, g, render_template, request, redirect, url_for, abort, Response


def get_db():
    from flask import current_app
    db_path = current_app.config['DATABASE']
    if 'db' not in g:
        # auto-init DB if it doesn't exist
        if not os.path.exists(db_path):
            init_db(current_app)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        g.db = conn
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db(app):
    db = sqlite3.connect(app.config['DATABASE'])
    try:
        with app.open_resource('schema.sql') as f:
            db.executescript(f.read().decode('utf8'))
        db.commit()
    finally:
        db.close()





def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'paste.sqlite'),
    )

    if test_config is not None:
        app.config.update(test_config)

    # ensure instance folder
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # register db handlers
    @app.teardown_appcontext
    def teardown_db(exception):
        close_db()

    # routes
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/paste/new', methods=('GET', 'POST'))
    def new_paste():
        if request.method == 'POST':
            title = request.form.get('title', '').strip() or 'Untitled'
            content = request.form.get('content', '').strip()
            if not content:
                return render_template('new.html', error='Content required', title=title, content=content)
            pid = secrets.token_urlsafe(6)
            created_at = datetime.utcnow().isoformat()
            db = get_db()
            db.execute('INSERT INTO pastes (id, title, content, created_at) VALUES (?, ?, ?, ?)',
                       (pid, title, content, created_at))
            db.commit()
            return redirect(url_for('view_paste', pid=pid))
        return render_template('new.html')

    @app.route('/paste/<pid>')
    def view_paste(pid):
        db = get_db()
        cur = db.execute('SELECT id, title, content, created_at FROM pastes WHERE id = ?', (pid,))
        paste = cur.fetchone()
        if paste is None:
            abort(404)
        return render_template('view.html', paste=paste)

    @app.route('/paste/<pid>/raw')
    def raw_paste(pid):
        db = get_db()
        cur = db.execute('SELECT content FROM pastes WHERE id = ?', (pid,))
        paste = cur.fetchone()
        if paste is None:
            abort(404)
        return Response(paste['content'], mimetype='text/plain')

    # expose init_db for CLI/tests
    app.init_db = lambda: init_db(app)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
