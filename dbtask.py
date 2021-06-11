from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime
import sys, traceback

##### directory structure - 
##/root/project/dbtask.py

###dependencies installed
### yum install -y tree python3 python3-pip
### pip3 install flask flask_sqlalchemy flask_marshmallow marshmallow-sqlalchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

db = SQLAlchemy(app)
ma = Marshmallow(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"Todo('{self.id}', '{self.content}', '{self.date_created.date()}')"

class TodoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Todo
        load_instance = True

@app.route('/', methods=['GET']) #### ONLY APPLICABLE FOR PRIV-ALB HEALTHCHECK PATH
def index(): #### ONLY APPLICABLE FOR PRIV-ALB HEALTHCHECK PATH
    print(" HTTP GET REQUEST FROM priv-alb for health check ON PRIVATE IP - {0}".format(request.method)) #### ONLY APPLICABLE FOR PRIV-ALB HEALTHCHECK PATH
    return(jsonify({'status':'HEALTH CHECK FROM PRIV-ALB'})) #### ONLY APPLICABLE FOR PRIV-ALB HEALTHCHECK PATH

@app.route('/dbtask', methods=['POST','GET'])

def dbtask():
 
        if request.method == 'POST':               
            req = request.json     ####### PARSES THE JSON OBJECT IN DATA PAYLOAD OF REQUEST'S BODY INTO A PYTHON DICTIONARY
            print("JSON POST REQUEST RECEIVED EITHER FROM ADDTASK OR UPDATE TASK - {0}".format(req) )
            if req['service'] == 'addtask':
                text = req['text']
                print(" HTTP POST REQUEST FROM ADDTASK.PY ON PRIVATE IP - {0}".format(text))

                try:
                    cursor = Todo.query.filter_by(content=text).first()
                    print("DATA TYPE OF CURSOR - {0} AND IT'S VALUE - {1}".format(type(cursor), cursor))
                    if cursor is not None and cursor.content == text :
                        print("RECORD ALREADY EXISTS IN TABLE SO DON'T INSERT A NEW ONE")
                        return(jsonify({'id':cursor.id}))
                    elif cursor is None:
                        print("RECORD DOES NOT ALREADY EXISTS IN TABLE SO INSERT A NEW ONE")
                        new_task = Todo(content=text) # INSERTS A NEW ROW  IN TODO TABLE 
                        db.session.add(new_task)
                        db.session.commit()
                        q = Todo.query.filter_by(content = text).first()
                        return(jsonify({'id':q.id}))    ##### JSONIFY ACCEPTS A DICT() AS ARGUMENT AND CONTRUCTS A JSON OBJECT OUT OF IT TO SEND TO CLIENT AS RESPONSE
                
                except Exception:
                    print("Exception in INSERT TASK OF DBTASK OCCURED:")
                    print("-"*60)
                    traceback.print_exc(file=sys.stdout)
                    print("-"*60)
                    return(jsonify({'id':0 }))

            elif req['service'] == 'updatetask':
                text = req['text']
                id = req['id']
                print("TEXT AND ID PASSED FROM HTTP POST REQUEST FROM UPDATETASK.PY - {0}, {1} ".format(text,id))
                try:
                    task = Todo.query.filter_by(id=id).first() 
                    task.content = text
                    db.session.commit()
                    updated = Todo.query.filter_by(id=id).first() 
                    if updated.content == text:
                        return jsonify({'status':'updated'})
                    elif updated.content != text:
                        return jsonify({'status':'not updated'})
                except Exception:
                    print("Exception in POST UPDATE TASK OF DBTASK OCCURED:")
                    print("-"*60)
                    traceback.print_exc(file=sys.stdout)
                    print("-"*60)
                    return(jsonify({'status':'exception' }))

                    
                    





        elif request.method == 'GET':      ###### HANDLES VIEW ,DELETE, UPDATE GET REQUESTS    
            if request.args.get('service') == 'viewtask': 
                try:
                
                    cursor = Todo.query.all()  ###ALWAYS RETURNS A LIST OF TODO CLASS OBJECTS - [(todo obj 1),(todo obj 2),(todo obj 3)]
                    print("DATA TYPE OF CURSOR - {0} AND IT'S VALUE - {1}".format(type(cursor), cursor))

                    if len(cursor) != 0:
                        todos_schema = TodoSchema(many=True)   ### DISPLAY MORE THAN 1 MVC OBJECTS IN JSON FORMAT - {'key name':[{todo obj 1},{todo obj 2},{todo obj 3}]}
                        output = todos_schema.dump(cursor) ### CONVERTS THE LIST OF TODO OBJECTS IN A SERIALIZABLE python LIST
                        return(jsonify({'cursor': output}))   ##### JSONIFY ACCEPTS A DICT() AS ARGUMENT AND CONTRUCTS A JSON OBJECT OUT OF IT TO SEND TO CLIENT AS RESPONSE
                       # {'cursor':[{todo obj 1},{todo obj 2},{todo obj 3}]}
                    elif len(cursor) == 0:
                        return(jsonify({'cursor': []}))

                except Exception:
                    print("EXCEPTION OCCURED IN VIEW OF DBTASK:")
                    print("-"*60)
                    traceback.print_exc(file=sys.stdout)
                    print("-"*60)
                    return(jsonify({'cursor':[] ,'status':'exception'}))

            elif request.args.get('service') == 'deletetask':
                id = request.args.get('id')
                try:
                    task = Todo.query.filter_by(id=id).first()
                    print("Task Retrieved using passed ID FOR DELETE DBTASK is - {0}".format(task))
                    db.session.delete(task)
                    db.session.commit()
                    cur = Todo.query.get(id)
                    if cur is None:
                        return jsonify({'status':'deleted'})
                    else:
                        return jsonify({'status':'exists'})

                except Exception:
                    print("EXCEPTION OCCURED IN DELETE OF DBTASK ")
                    print("-"*60)
                    traceback.print_exc(file=sys.stdout)
                    print("-"*60)
                    return(jsonify({'status':'exception in delete DBTASK'}))

            elif request.args.get('service') == 'updatetask':
                id = request.args.get('id')
                try:
                    task = Todo.query.filter_by(id=id).first() #task = Todo('1', 'Ganpati', '2020-10-21')
                    print("Task Retrieved using passed ID FOR UPDATE TASK is - {0}".format(task)) 
                    todo_schema = TodoSchema()   
                    output = todo_schema.dump(task) # output = {'id':'','content':'date_created':''}, type(output) = <dict>
                    print("VALUE OF MARSHMALLOW SERIALIZED TASK OBJ IS - {0} AND IT'S DATA TYPE IS - {1}".format(output,type(output)))
                    return(jsonify({'task': output}))  #{'task':{'id':'','content':'date_created':''}}

                except Exception:
                    print("EXCEPTION OCCURED IN HTTP GET UPDATE OF DBTASK ")
                    print("-"*60)
                    traceback.print_exc(file=sys.stdout)
                    print("-"*60)
                    return(jsonify({'status':'exception in HTTP GET UPDATE DBTASK'}))
                    
                    
if __name__ == "__main__":
    db.create_all() #CREATES TEST.DB IN SQLITE
    app.run(host = "0.0.0.0", port = "5000", debug = True)
