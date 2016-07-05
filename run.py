#-*- coding: utf-8 -*-

from setting import redis_pass, redis_port, session_key
from flask import *
import redis, hashlib

#Flask settings
app = Flask(__name__)
app.secret_key = session_key #flask session의 암호key

#redis에 연결해주는 코드
#port에는 레디스의 포트, 비밀번호는 있을 시 그 비밀번호를 넣어주고 없으면 "password =" 부분을 생략해주면된다
r = redis.Redis('localhost', port = redis_port, password = redis_pass)

#메인페이지
@app.route('/')
def home():
    user = None
    if 'username' in session:
        user = escape(session['username'])
    return render_template('main.html', user = user)

#가입신청페이지
@app.route('/join')
def join_page():
    error = None
    user = None
    if 'username' in session:
        return "You have ID!"
    return render_template('join.html', user = user, error = error)

#가입요청 처리
@app.route('/join', methods = ['POST'])
def join():
    if request.method == 'POST':
        ID = request.form['ID']
        password_temp = hashlib.sha256(bytes(request.form['password'], 'utf-8'))
        password = password_temp.hexdigest()
        mem_list = r.hkeys('flask_member')
        if bytes(ID, 'utf-8') in mem_list:
            return render_template('join.html', error = "There's same ID.")
        else:
            r.hset('flask_member', ID, password)
            flash("You're successfully joined!")
            return redirect(url_for('login'))

#글쓰기페이지
@app.route('/write/')
def write():
    user = None
    if 'username' in session:
        user = escape(session['username'])
    return render_template('write.html', user = user)

#post요청에 대한 처리
@app.route('/write/', methods = ['POST'])
def writing():
    if request.method == 'POST':
        text = request.form['text']
        if 'username' in session:
            author = escape(session['username'])
        else:
            author = 'guest'

        count = int(r.hget('flask', 'Count'))
        r.hmset('flask', {'%d' % (count + 1): text, '%dauthor' % (count + 1): author})
        r.hincrby('flask', 'Count', 1)
        return redirect(url_for('show_posts'))

#num번 글로 연결
@app.route('/post/<int:num>/')
def show_post(num):
    user = None
    if 'username' in session:
        user = escape(session['username'])
    count = int(r.hget('flask', 'Count'))
    if num in range(1, count + 1):
        post = r.hget('flask', '%d' % num).decode('utf-8')
        author = r.hget('flask', '%dauthor' % num).decode('utf-8')
        return render_template('post.html', post = post, author = author, user = user)
    
    else:
        return redirect(url_for('show_posts'))
        
#글 목록 보여주기
@app.route('/post/', methods = ['GET'])
def show_posts():
    user = None
    page_num = 1
    if request.method == 'GET' and request.args.get('page', ''):
        page_num = int(request.args.get('page', ''))
    if 'username' in session:
        user = escape(session['username'])
    count = int(r.hget('flask', 'Count'))
    max_of_page = 5
    if count % max_of_page == 0:
        last_page = count / max_of_page
    else:
        last_page = count / max_of_page + 1
    last_page = int(last_page)
    return render_template('list.html', count = count, page = page_num, max = max_of_page, user = user, last_page = last_page)

#로그인페이지 && 로그인요청처리
@app.route('/login', methods = ['POST', 'GET'])
def login():
    user = None
    if 'username' in session:
        user = escape(session['username'])
    if request.method == 'POST':
        password_temp = hashlib.sha256(bytes(request.form['password'], 'utf-8'))
        password = password_temp.hexdigest()
        if r.hget('flask_member', '%s' % request.form['ID']) and r.hget('flask_member', '%s' % request.form['ID']).decode('utf-8') == password:
            session['username'] = request.form['ID']
            return redirect(url_for('home'))
        else:
            return redirect(url_for('home'))
    return render_template('login.html', user = user)

#로그아웃요청처리
@app.route('/logout', methods = ['POST', 'GET'])
def logout():
    user = None
    if 'username' in session:
        user = escape(session['username'])
    if request.method == 'POST':
        if session['username'] != False:
            session.pop('username', None)
            return redirect(url_for('home'))
        else:
            return redirect(url_for('home'))

#그냥 이런것도 되려나 실험해본 페이지
@app.route('/test', methods = ['POST', 'GET'])
def test():
    aaa = None
    if request.method == 'POST':
        aaa = 'asdf'
    return render_template('test.html', aaa = aaa)

if __name__ == '__main__':
    app.run(host = '0.0.0.0', debug = False, port = 8123)
