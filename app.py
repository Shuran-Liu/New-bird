"""
汇报顺序抽签小程序 - 后端服务器
使用 Flask 框架和 SQLite 数据库
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sqlite3
import uuid
from datetime import datetime
import os

app = Flask(__name__, static_folder='.')
CORS(app)  # 允许跨域请求

DATABASE = 'lottery.db'


def get_db():
    """获取数据库连接"""
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db


def init_db():
    """初始化数据库表"""
    db = get_db()
    cursor = db.cursor()

    # 创建会话表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_slots INTEGER DEFAULT 10
        )
    ''')

    # 创建参与者表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS participants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            name TEXT NOT NULL,
            number INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions (id),
            UNIQUE(session_id, name),
            UNIQUE(session_id, number)
        )
    ''')

    db.commit()
    db.close()


def get_available_numbers(session_id, total_slots=10):
    """获取可用的抽签号码"""
    db = get_db()
    cursor = db.cursor()

    # 获取已使用的号码
    cursor.execute('SELECT number FROM participants WHERE session_id = ?', (session_id,))
    used = set(row[0] for row in cursor.fetchall())

    db.close()

    # 返回可用号码
    return [n for n in range(1, total_slots + 1) if n not in used]


@app.route('/')
def index():
    """返回抽签页面"""
    return send_from_directory('.', 'index.html')


@app.route('/admin.html')
def admin():
    """返回管理页面"""
    return send_from_directory('.', 'admin.html')


@app.route('/api/session', methods=['GET'])
def get_session():
    """获取或创建会话"""
    session_id = request.args.get('session')

    if not session_id:
        # 创建新会话
        session_id = str(uuid.uuid4())[:8]
        db = get_db()
        cursor = db.cursor()
        cursor.execute('INSERT INTO sessions (id) VALUES (?)', (session_id,))
        db.commit()
        db.close()

    # 检查会话是否存在
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM sessions WHERE id = ?', (session_id,))
    session = cursor.fetchone()

    if not session:
        db.close()
        return jsonify({'error': '会话不存在'}), 404

    # 获取参与者列表
    cursor.execute('''
        SELECT name, number, created_at
        FROM participants
        WHERE session_id = ?
        ORDER BY number
    ''', (session_id,))
    participants = [dict(row) for row in cursor.fetchall()]

    db.close()

    # 获取可用号码
    available = get_available_numbers(session_id)

    return jsonify({
        'session_id': session_id,
        'created_at': session['created_at'],
        'participants': participants,
        'available_numbers': available,
        'total_slots': session['total_slots']
    })


@app.route('/api/draw', methods=['POST'])
def draw():
    """执行抽签"""
    data = request.json
    session_id = data.get('session_id')
    name = data.get('name', '').strip()

    if not session_id or not name:
        return jsonify({'error': '缺少必要参数'}), 400

    db = get_db()
    cursor = db.cursor()

    # 检查会话是否存在
    cursor.execute('SELECT total_slots FROM sessions WHERE id = ?', (session_id,))
    session = cursor.fetchone()
    if not session:
        db.close()
        return jsonify({'error': '会话不存在'}), 404

    total_slots = session[0]

    # 检查用户是否已抽签
    cursor.execute(
        'SELECT number FROM participants WHERE session_id = ? AND name = ?',
        (session_id, name)
    )
    existing = cursor.fetchone()
    if existing:
        db.close()
        return jsonify({
            'error': 'already_drawn',
            'message': f'你已经抽过签了！你的顺序是第 {existing[0]} 位'
        }), 400

    # 获取可用号码
    available = get_available_numbers(session_id, total_slots)

    if not available:
        db.close()
        return jsonify({'error': '所有位置都已抽完'}), 400

    # 随机抽取一个号码
    import random
    number = random.choice(available)

    # 保存抽签结果
    cursor.execute('''
        INSERT INTO participants (session_id, name, number)
        VALUES (?, ?, ?)
    ''', (session_id, name, number))

    db.commit()
    db.close()

    return jsonify({
        'success': True,
        'number': number,
        'name': name,
        'message': f'抽签成功！你的顺序是第 {number} 位'
    })


@app.route('/api/participants', methods=['GET'])
def get_participants():
    """获取会话的所有参与者"""
    session_id = request.args.get('session')

    if not session_id:
        return jsonify({'error': '缺少会话ID'}), 400

    db = get_db()
    cursor = db.cursor()

    cursor.execute('''
        SELECT name, number, created_at
        FROM participants
        WHERE session_id = ?
        ORDER BY number
    ''', (session_id,))

    participants = [dict(row) for row in cursor.fetchall()]
    db.close()

    return jsonify({
        'participants': participants,
        'count': len(participants)
    })


@app.route('/api/reset', methods=['POST'])
def reset_session():
    """重置会话（清空抽签记录）"""
    data = request.json
    session_id = data.get('session_id')

    if not session_id:
        return jsonify({'error': '缺少会话ID'}), 400

    db = get_db()
    cursor = db.cursor()

    # 删除该会话的所有参与者
    cursor.execute('DELETE FROM participants WHERE session_id = ?', (session_id,))

    db.commit()
    db.close()

    return jsonify({
        'success': True,
        'message': '抽签已重置'
    })


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取会话统计信息"""
    session_id = request.args.get('session')

    if not session_id:
        return jsonify({'error': '缺少会话ID'}), 400

    db = get_db()
    cursor = db.cursor()

    # 获取参与者数量
    cursor.execute('SELECT COUNT(*) FROM participants WHERE session_id = ?', (session_id,))
    count = cursor.fetchone()[0]

    # 获取总位置数
    cursor.execute('SELECT total_slots FROM sessions WHERE id = ?', (session_id,))
    session = cursor.fetchone()

    if not session:
        db.close()
        return jsonify({'error': '会话不存在'}), 404

    db.close()

    return jsonify({
        'total': session[0],
        'drawn': count,
        'remaining': session[0] - count
    })


if __name__ == '__main__':
    # 初始化数据库
    if not os.path.exists(DATABASE):
        init_db()
        print(f"[OK] Database created: {DATABASE}")

    # 启动服务器
    print("=" * 50)
    print("Lottery Server Starting...")
    print("=" * 50)
    print("Draw page:  http://localhost:5000")
    print("Admin page: http://localhost:5000/admin.html")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)
