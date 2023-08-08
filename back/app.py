from flask import Flask, render_template, jsonify, request, flash
from pymongo import MongoClient
# from bson.objectid import ObjectId

# 회원가입시 비번 암호화 -> 개발자(나)가 회원 비번 못보도록.
import hashlib

# 토큰에 만료시간을 주기위해
import datetime

# 같이 설치(jwt, pyJWT)
import jwt


app = Flask(__name__)
client = MongoClient('localhost',27017)
db = client.dbtodolist

# JWT 토큰 만들 때 필요한 비밀문자열. 서버만 알고있기에 내 서버에서만 토큰을 인코딩(만들기)/디코딩(풀기) 가능
SECRET_KEY = 'SPARTA'


# db: user
# ['_id', 'user_id', 'user_pw', 'user_name']

# db: todolist
# ['_id', 'user_id', 'user_name', 'content', 'tag', 'datetime', 'completed']


# 메인화면
@app.route('/')
def home():
	return render_template('index.html')

@app.route('/api/chart', methods=['GET'])
def chart():
	# user_info_all = list(db.user.find({}, {'_id':0}))
	# [{'user_id':'jong', 'user_pw':'1234', 'user_name':'장종현'}, ...]
	# username_list = []
	# for user_info in user_info_all:
	# 	username_list.append(user_info['user_name'])

	todolist_all = list(db.todolist.find({}, {'_id': 0}))
	
	usercompleted_rate = {}
	for todolist in todolist_all:
		if todolist['user_name'] not in list(usercompleted_rate.keys):
			usercompleted_rate[todolist['user_name']] = [0, 0]


		if todolist['completed'] == False:
			usercompleted_rate[todolist['user_name']][1] += 1
		else:
			usercompleted_rate[todolist['user_name']][1] += 1
			usercompleted_rate[todolist['user_name']][0] += 1


	# result = list(db.todolist.find({}))
	# for person in result:
	# 		person['_id'] = str(person['_id'])

	return jsonify({'result': 'success', 'usercompleted_rate': usercompleted_rate})


#################################
##        HTML을 주는 부분      ##
#################################
@app.route('/login')
def login():
  msg = request.args.get("msg")
  return render_template('login.html', msg=msg)


@app.route('/register')
def register():
  return render_template('register.html')


@app.route('/starttodolist')
def starttodolist():
	return render_template('starttodolist.html')



#################################
##       로그인을 위한 API      ##
#################################

# 회원가입
@app.route('/api/register', methods=['POST'])
def api_register():
	username_receive = request.form['username_give']
	id_receive = request.form['id_give']
	pw_receive = request.form['pw_give']
	pw2_receive = request.form['pw2_give']
	

	if username_receive == "" or id_receive == "" or pw_receive == "" or pw2_receive == "":
		flash("입력되지 않은 값이 있습니다.")
		return render_template('signup.html')

	if pw_receive != pw2_receive:
		flash("비밀번호가 일치하지 않습니다.")
		return render_template('signup.html')
	
	username_cnt = len(list[db.user.find({"user_id": username_receive}, {'_id': 0})])
	if username_cnt > 0:
		flash("중복된 성명입니다.")
		return render_template("signup.html")

	userid_cnt = len(list[db.user.find({"user_id": id_receive}, {'_id': 0})])
	if userid_cnt > 0:
		flash("중복된 아이디입니다.")
		return render_template("signup.html")


	pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

	user_info = {'user_id': id_receive,
				'user_pw': pw_hash,
				'user_name': username_receive
	}

	db.user.insert_one(user_info)

	return jsonify({'result': 'success'})


#로그인
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

'''
# 로그아웃
@app.route('/api/logout')
def api_logout():
	token_receive = request.cookies.get('mytoken')
	blacktoken = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
	blacklist = {"blacktoken":blacktoken}
	db.black.insert_one(blacklist)
	return redirect(url_for("index"))
'''


#################################
##       투두리스트 API         ##
#################################

# db: todolist
# ['_id', 'user_id', 'user_name', 'content', 'tag', 'datetime', 'completed']

@app.route('/api/read_mytodolist', methods=['GET'])
def read_mytodolist():
	result = list(db.todolist.find({}, {'_id': 0}))
	
	return jsonify({'result': 'success', 'mytodolist': result})


@app.route('/api/post', methods=['POST'])
def post_todolist():
	id_receive = request.form['id_give']
	username_receive = request.form['username_give']
	content_receive = request.form['content_give']
	tag_receive = request.form['tag_give']
	datetime_receive = request.form['datetime_give']


	todolist = {
		'user_id' : id_receive,
		'user_name' : username_receive,
		'content' : content_receive,
		'tag' : tag_receive,
		'datetime' : datetime_receive,
		'completed' : False
	}


	db.todolist.insert_one(todolist)
	# nextId = nextId + 1

	return jsonify({'result': 'success'})






if __name__ == '__main__':
	app.run('0.0.0.0', port=5000, debug=True)