from flask import Flask, render_template, jsonify, request, flash, redirect
from pymongo import MongoClient
app = Flask(__name__)

# 회원가입시 비번 암호화 -> 개발자(나)가 회원 비번 못보도록.
import hashlib

# 토큰에 만료시간을 주기위해
import datetime

# 같이 설치(jwt, pyJWT)
import jwt


client = MongoClient('localhost',27017)
db = client.dbtodolist


SECRET_KEY = 'SPARTA'

@app.route('/')
def home():
   return render_template('index.html');


@app.route('/login', methods=['GET','POST'])
def login():
    return render_template('login.html');

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    else:
        return render_template('login.html')
   


   
@app.route('/api/signup', methods=['POST'])
def api_register():
   
	username_receive = request.form['username_give']
	id_receive = request.form['id_give']
	pw_receive = request.form['pw_give']
	pw2_receive = request.form['pw2_give']
	


	pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

	user_info = {'user_id': id_receive,
				'user_pw': pw_hash,
				'user_name': username_receive
	}

	db.user.insert_one(user_info)

	return  render_template('login.html')

@app.route('/api/login', methods=['POST'])
def api_login():
	id_receive = request.form['id_give']
	pw_receive = request.form['pw_give']


	pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

	result = db.user.find_one({'user_id':id_receive, 'user_pw':pw_hash})
	


	if result is not None:
			payload = {
					'id': id_receive,
					'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=300)
			}
			token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
			# token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

			# 토큰 주기
			return jsonify({'result':'success', 'token':token})
	else:
			return jsonify({'result':'fail', 'msg':'아이디/비밀번호가 일치하지 않습니다.'})

if __name__ == '__main__':  
   app.run('127.0.0.1', port=5000, debug=True)
   