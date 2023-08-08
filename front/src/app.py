from flask import Flask, render_template, jsonify, request, flash
app = Flask(__name__)

# client = MongoClient('localhost', 27017)
# db= client.dbjungle

client = MongoClient('localhost',27017)
db = client.dbtodolist

@app.route('/')
def home():
   return render_template('index.html');


@app.route('/login')
def login():
    return render_template('login.html');

@app.route('/signup')
def signup():
   return render_template('signup.html')

if __name__ == '__main__':  
   app.run('127.0.0.1', port=5000, debug=True)
   
   
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

