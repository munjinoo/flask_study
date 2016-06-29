#-*- coding: utf-8 -*-

from setting import redis_pass, redis_port
from flask import Flask, render_template, url_for, redirect, request
import redis

#Flask를 app에 담아주는 코드
app = Flask(__name__)

#redis에 연결해주는 코드
#port에는 레디스의 포트, 비밀번호는 있을 시 그 비밀번호를 넣어주고 없으면 "password =" 부분을 생략해주면된다
r = redis.Redis('localhost', port = redis_port, password = redis_pass)

#메인페이지
@app.route('/')
def home():
    return render_template('main.html')

#글쓰기페이지
@app.route('/write/')
def write():
    return render_template('write.html')

#post요청에 대한 처리
@app.route('/write/', methods = ['POST'])
def writing():
    if request.method == 'POST':
        text = request.form['text']
        count = int(r.hget('flask', 'Count'))
        r.hset('flask', '%d' % (count + 1), text)
        r.hincrby('flask', 'Count', 1)
        return redirect(url_for('show_posts'))

#num번 글로 연결
@app.route('/post/<int:num>/')
def show_post(num):
    count = int(r.hget('flask', 'Count'))
    if num in range(1, count + 1):
        post = r.hget('flask', '%d' % num).decode('utf-8')
        return render_template('post.html', post = post)
    
    else:
        return redirect(url_for('show_posts'))
        
#글 목록 보여주기
@app.route('/post/')
def show_posts():
    count = int(r.hget('flask', 'Count'))
    return render_template('list.html', count = count)


if __name__ == '__main__':
    app.run(host = '0.0.0.0', debug = False, port = 8123)
