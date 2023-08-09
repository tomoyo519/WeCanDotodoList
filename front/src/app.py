from bson import ObjectId
from flask import Flask, render_template, jsonify, request, flash, redirect
from pymongo import MongoClient
app = Flask(__name__)

# 회원가입시 비번 암호화 -> 개발자(나)가 회원 비번 못보도록.
import hashlib

# 토큰에 만료시간을 주기위해
import datetime

# 같이 설치(jwt, pyJWT)
import jwt

from datetime import datetime

client = MongoClient('localhost',27017)
db = client.dbtodolist

SECRET_KEY = 'SPARTA'

# now = datetime.now()
# now_text = now.strftime("%Y/%m/%d")
# db.todolist.insert_one({'user_id':3,'user_name':3, 'content':'아침 9시에 문지캠퍼스 한바퀴 뛰기', 'datetime':now_text, 'complete':False, 'tag':'운동'})
# db.todolist.insert_one({'user_id':3,'user_name':3, 'content':'아침 10시에 문지캠퍼스 한바퀴 뛰기', 'datetime':now_text, 'complete':False, 'tag':'운동'})
# db.todolist.insert_one({'user_id':3,'user_name':3, 'content':'아침 11시에 문지캠퍼스 한바퀴 뛰기', 'datetime':now_text, 'complete':False, 'tag':'운동'})
# db.todolist.insert_one({'user_id':3,'user_name':3, 'content':'아침 12시에 문지캠퍼스 한바퀴 뛰기', 'datetime':now_text, 'complete':True, 'tag':'운동'})



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


@app.route('/api/post', methods=['POST'])
def post_todolist():
	id_receive = request.form['id_give']
	username_receive = request.form['username_give']
	content_receive = request.form['content_give']
	tag_receive = request.form['tag_give']
# vc-날짜추가
	now = datetime.now()
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

if __name__ == '__main__':  
   app.run('127.0.0.1', port=5000, debug=True)
   