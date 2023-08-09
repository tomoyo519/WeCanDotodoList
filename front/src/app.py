from bson import ObjectId
from flask import Flask, render_template, jsonify, request, flash, redirect, make_response
from pymongo import MongoClient
from flask_jwt_extended import *


app = Flask(__name__)
# JWT 매니저 활성화
app.config['SECRET_KEY'] = 'your_secret_key'

app.config.update(DEBUG = True, JWT_SECRET_KEY = "thisissecertkey" )
jwt = JWTManager(app)

# app.config['JWT_COOKIE_SECURE'] = False # https를 통해서만 cookie가 갈 수 있는지 (production 에선 True)
# app.config['JWT_TOKEN_LOCATION'] = ['cookies']
# app.config['JWT_ACCESS_COOKIE_PATH'] = '/' # access cookie를 보관할 url (Frontend 기준)
# app.config['JWT_REFRESH_COOKIE_PATH'] = '/' # refresh cookie를 보관할 url (Frontend 기준)
# # CSRF 토큰 역시 생성해서 쿠키에 저장할지
# # (이 경우엔 프론트에서 접근해야하기 때문에 httponly가 아님)
# app.config['JWT_COOKIE_CSRF_PROTECT'] = True


# 회원가입시 비번 암호화 -> 개발자(나)가 회원 비번 못보도록.
import hashlib

# 토큰에 만료시간을 주기위해
import datetime

# 같이 설치(jwt, pyJWT)
import jwt


client = MongoClient('localhost',27017)
db = client.mytodolist

# SECRET_KEY = 'SPARTA'

# now = datetime.now()
# now_text = now.strftime("%Y/%m/%d")
# db.todolist.insert_one({'user_id':3,'user_name':3, 'content':'아침 9시에 문지캠퍼스 한바퀴 뛰기', 'datetime':now_text, 'complete':False, 'tag':'운동'})
# db.todolist.insert_one({'user_id':3,'user_name':3, 'content':'아침 10시에 문지캠퍼스 한바퀴 뛰기', 'datetime':now_text, 'complete':False, 'tag':'운동'})
# db.todolist.insert_one({'user_id':3,'user_name':3, 'content':'아침 11시에 문지캠퍼스 한바퀴 뛰기', 'datetime':now_text, 'complete':False, 'tag':'운동'})
# db.todolist.insert_one({'user_id':3,'user_name':3, 'content':'아침 12시에 문지캠퍼스 한바퀴 뛰기', 'datetime':now_text, 'complete':True, 'tag':'운동'})


def create_jwt_token(user_id):
    payload = {
        'sub': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)  # 1일 후 만료
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token

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
   
@app.route('/myTodo', methods=['GET'])
def myTodoList():
    return render_template('myToList.html')

@app.route('/tagList', methods=['GET'])
def tagList():
    tagList = ["#운동", "#개발공부", "#독서", "#식단"]
    return render_template('tagList.html', tagList=tagList)
    

@app.route('/api/signup', methods=['POST'])
def api_register():
   
	username_receive = request.form['username_give']
	id_receive = request.form['id_give']
	pw_receive = request.form['pw_give']
	pw2_receive = request.form['pw2_give']
	

	if username_receive == "" or id_receive == "" or pw_receive == "" or pw2_receive == "":
		# flash("입력되지 않은 값이 있습니다.")
		return jsonify({'result': False, 'msg':'입력되지 않은 값이 있습니다.'})

	if pw_receive != pw2_receive:
		return jsonify({'result': False, 'msg': '비밀번호가 일치하지 않습니다.'})
	
	username_cnt = len(list(db.user.find({"user_id": username_receive}, {'_id': 0})))
	if username_cnt > 0:
		return jsonify({'result': False, 'msg': "중복된 성명입니다."})

	userid_cnt = len(list(db.user.find({"user_id": id_receive}, {'_id': 0})))
	if userid_cnt > 0:
  		return jsonify({'result': False, 'msg': "중복된 성명입니다."})


	pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

	user_info = {'user_id': id_receive,
				'user_pw': pw_hash,
				'user_name': username_receive
	}

	db.user.insert_one(user_info)

	return   jsonify({'result': True})



@app.route('/api/login', methods=['POST'])
def api_login():
	id_receive = request.form['id_give']
	pw_receive = request.form['pw_give']


	pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

	result = db.user.find_one({'user_id':id_receive, 'user_pw':pw_hash}, {'_id': 0})
	
	if id_receive == "" or pw_receive  == "":
		return jsonify({'result': False, 'message':'입력되지 않은 값이 있습니다.'})

	if result is None:
		return jsonify({'message': '로그인에 실패했습니다. 아이디와 비밀번호를 재확인 해주세요.'}), 401

	token = create_jwt_token(result)
	response = make_response(jsonify({'message': 'success'}), 200)
	response.set_cookie('jwt_token', token)
	return response
			




@app.route('/api/chart', methods=['GET'])
def chart():


	todolist_all = list(db.todolist.find({}, {'_id': 0}))
	
	username = []
	usercompleted_rate = []
	for todolist in todolist_all:
		if todolist['user_name'] not in username:
			username.append(todolist['user_name'])
			usercompleted_rate.append([todolist['user_name'], 0, 0])


		if todolist['complete'] == False:
			usercompleted_rate[username.index(todolist['user_name'])][2] += 1
		else:
			usercompleted_rate[username.index(todolist['user_name'])][2] += 1
			usercompleted_rate[username.index(todolist['user_name'])][1] += 1


	return jsonify({'result': 'success', 'usercompleted_rate': usercompleted_rate})


#################################
##       투두리스트 API         ##
#################################

# db: todolist
# ['_id', 'user_id', 'user_name', 'content', 'tag', 'datetime', 'complete']


@app.route('/api/read_mytodolist', methods=['GET'])

def read_mytodolist():
	result = list(db.todolist.find({}))
	for todolist in result:
		todolist['_id'] = str(todolist['_id'])

	return jsonify({'result': 'success', 'mytodolist': result})


@app.route('/api/read_onlymytodolist', methods=['POST'])

def read_myonlytodolist():
	id_receive = request.form['id_give']
	result = list(db.todolist.find({'user_id' : id_receive}))
	for todolist in result:
		todolist['_id'] = str(todolist['_id'])
	

	return jsonify({'result': 'success', 'mytodolist': result})



@app.route('/api/post', methods=['POST'])

def post_todolist():
	id_receive = request.form['id_give']
	username_receive = request.form['username_give']
	content_receive = request.form['content_give']
	tag_receive = request.form['tag_give']



# vc-날짜추가
	now =  datetime.datetime.utcnow()
	now_text = now.strftime("%Y/%m/%d")
	todolist = {
		'user_id' : id_receive,
		'user_name' : username_receive,
		'content' : content_receive,
		'tag' : tag_receive,
		'datetime' : now_text,
		'complete' : False
	}

	db.todolist.insert_one(todolist)

	return jsonify({'result': 'success'})


@app.route('/api/delete', methods=['POST'])
def delete_todolist():
	objectid_receive = request.form['objectid_give']
	db.todolist.delete_one({'_id': ObjectId(objectid_receive)})

	return jsonify({'result': 'success'})


@app.route('/api/complete', methods=['POST'])
def complete_todolist():
	objectid_receive = request.form['objectid_give']
	target_content = db.todolist.find_one({'_id': ObjectId(objectid_receive)})
	if target_content['complete'] == False:
		db.todolist.update_one({'_id': ObjectId(objectid_receive)},{'$set': {'complete':True}})
	else:
		db.todolist.update_one({'_id': ObjectId(objectid_receive)},{'$set': {'complete':False}})
	
	return jsonify({'result': 'success'})


#수수정버튼 누른 todo 정보 받아노는것
@app.route('/api/edit', methods=['POST'])
def edit_todolist():
    objectid_receive = request.form['objectid_give']
    editone = db.todolist.find_one({'_id': ObjectId(objectid_receive)})
    editone['_id'] = str(editone['_id'])
    return jsonify({'result': 'success', 'edittodolist': editone})


# 수정한거를 db에 적용하는것
@app.route('/api/save', methods=['POST'])
def editsave_todolist():
	objectid_receive = request.form['objectid_give']
	content_receive = request.form['content_give']
	tag_receive = request.form['tag_give']

	todolist = {
			'content': content_receive,
			'tag': tag_receive
	}

	db.todolist.update_one({'_id':ObjectId(objectid_receive)},{'$set': todolist})
	return jsonify({'result': 'success'})

# todoList 중 해당 tag만 받아오는 기능


if __name__ == '__main__':  
   app.run('127.0.0.1', port=5000, debug=True)
   