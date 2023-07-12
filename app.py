from flask import Flask, render_template, request,redirect,url_for,session,g
from flask_mysqldb import MySQL
import mysql.connector
import MySQLdb.cursors
import re
import tkinter
import datetime
from tkinter import messagebox

# This code is to hide the main tkinter window
root = tkinter.Tk()
root.withdraw()

app = Flask(__name__)

app.secret_key='abcd'

app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='finalproject'

mysql= MySQL(app)



def generate_id(username):
    cur = mysql.connection.cursor()
    cur.execute("SELECT userid from user where username=%s",[username])
    userdeets=cur.fetchone()
    uuid=userdeets[0]
    return uuid;

def generate_usertype(username):
    cur = mysql.connection.cursor()
    cur.execute("SELECT usertype from user where username=%s",[username])
    type=cur.fetchone()
    usertype=type[0]
    return usertype;


@app.route('/login',methods=['POST','GET'])
def login():
    message=''
    if request.method=='POST' and 'email' in request.form and 'password' in request.form:
        email=request.form['email']
        password=request.form['password']
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('Select * from user where email= % s and password =% s', (email,password,))
        user = cursor.fetchone()
        if user:
            session['loggedin']= True
            session['username']= user['username']
            session['userid']= user['userid']
            session['email']= user['email']
            session['password']= user['password']
            
            uusername=session['username']
            global uuid
            global usertype
            uuid=generate_id(uusername)
            usertype= generate_usertype(uusername)
            print("Current USER ID login: ",uuid)
            print("Current USER ID login: ",usertype)
            return redirect(url_for('main'))
        else:
            return render_template('login.html',message='please enter correct email/password')
    return render_template('login.html', message=message) 



@app.route('/adminlogin',methods=['POST','GET'])
def adminlogin():
    message=''
    if request.method=='POST' and 'email' in request.form and 'password' in request.form:
        email=request.form['email']
        password=request.form['password']
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('Select * from admin where email= % s and password =% s', (email,password,))
        admin = cursor.fetchone()
        if admin:
            print(admin)
            return redirect(url_for('admin'))
        else:
            print(email)
            print(admin)
            return render_template('adminlogin.html',message='please enter correct email/password')
    return render_template('adminlogin.html', message=message) 


@app.route('/register', methods =['GET', 'POST'])
def register():
    message=''
    if request.method=='POST' and 'username' in request.form and 'email' in request.form and 'usertype' in request.form and 'password' in request.form:
        username=request.form['username']
        email=request.form['email']
        usertype=request.form['usertype']
        password=request.form['password']
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('Select email from user where email= % s', (email,))
        account = cursor.fetchone()
        print(email)
        if account:
            return render_template('register.html',message='Account already exits!')
        elif not username or not password or not email:
            return render_template('register.html',message='Please fill out the form!')
        else:
            cursor.execute('insert into user values (%s,%s, %s, %s, %s,%s)', ('NONE',username,email,usertype,password,0))
            mysql.connection.commit()
            return render_template('register.html', message='You have successfully registered!')
    elif request.method=='POST':
        message='Please fill out the form!'
    return render_template('register.html', message=message)



@app.route("/viewqa")
def viewqa():
    return render_template("viewqa.html")


@app.route("/askqa", methods =['GET', 'POST'])
def askqa():
    message=''
    usern=session['username']
    if request.method=='POST' and  'question' in request.form:
        question=request.form['question']
        print("Current USER ID askqa: ",uuid)
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('Select userid,username from user where userid= % s', (uuid,))
        account = cursor.fetchone()
        print("account is getting userid",account)
        if account:
            print("askqa account is ok",account)
            now=datetime.datetime.now()
            cursor.execute('insert into questions values (%s,%s,%s,NULL,%s,%s)', (uuid,usern,question,now.strftime("%I:%M %p"),now.strftime("%d %B %Y")))
            mysql.connection.commit()
            return redirect('ans')
        elif not question:
            return render_template('askqa.html',usern=usern,message='Please fill out the form!')
            
    elif request.method=='POST':
        return render_template('askqa.html',usern=usern,message='Please fill out the form!')
    return render_template('askqa.html', usern=usern, message=message)
           
           


@app.route('/ans', methods =['GET', 'POST'])
def ans():
        
        mycursor=mysql.connection.cursor()
        mycursor.execute('select username,question,questions.question_id,user_id,time,date from questions order by questions.question_id desc')
        question=mycursor.fetchall()
        qid=request.form.get("qid")
        print(ans)
        mysql.connection.commit()
        print(qid)
        return render_template('ans.html', question=question) 
    


@app.route('/ansshow/<int:Number>', methods =['GET', 'POST'])
def show(Number):
    mycursor=mysql.connection.cursor()
    qid =None 
    if Number is not None:
        qid=Number
    else:
        qid=request.form['qid']
    ans=request.form.get("ans")
    qiid=request.form.get("qiid")
    usern=session['username']
    mycursor.execute('select question,questions.question_id,username,time,date from questions where questions.question_id=%s', (qid,))
    question=mycursor.fetchone()
    print(question)
    mycursor.execute('select username,answer,answer_id,question_id,userid,time,date from answer where answer.question_id=%s order by answer_id desc',(qid,))
    answer=mycursor.fetchall()
    mycursor.execute('select status from user where userid=%s',(uuid,))
    status=mycursor.fetchone()
    stat=status[0]
    print("Status: ", stat)
    print("Current USER ID , ansshow: ",uuid,usertype)
    print("usertype is", usertype)
    if request.method=="POST":
            if all([qid==qiid , session['loggedin']]):
                if usertype=='scholar':
                    if stat==1:
                        now=datetime.datetime.now()
                        mycursor.execute('insert into answer values (%s,%s,%s,%s, %s,%s,%s)', (uuid,usern,'NONE',qiid,ans,now.strftime("%I:%M %p"),now.strftime("%d %B %Y")))
                        mysql.connection.commit()
                        print(ans)
                        print(qiid)
                        print("ansshow is working ")
                        return render_template('ansshow.html',answer=answer,question=question,message='Your answer sent successfully!')
                    elif stat==0:
                        print("Scholar is not verified.")
                        return render_template('ansshow.html',answer=answer,question=question,message='You can answer after verification.')
                    else:
                        print("stat is not getting value...")
                elif usertype=='User':
                    print("usertype is user")
                    return render_template('ansshow.html',answer=answer,question=question,message='Only verified scholars can answer.')
                else:
                    print("Something is wrong. Try again!") 
        
            return render_template('ansshow.html', question=question,answer=answer) 
    return render_template('ansshow.html', question=question,answer=answer)   
    



@app.route('/ansshow', methods =['GET', 'POST'])
def ansshow():
    mycursor=mysql.connection.cursor()
    qid=request.form['qid']
    ans=request.form.get("ans")
    qiid=request.form.get("qiid")
    usern=session['username']
    mycursor.execute('select question,questions.question_id,username,time,date from questions where questions.question_id=%s', (qid,))
    question=mycursor.fetchone()
    print(question)
    mycursor.execute('select username,answer,answer_id,question_id,userid,time,date from answer where answer.question_id=%s order by answer_id desc',(qid,))
    answer=mycursor.fetchall()
    mycursor.execute('select status from user where userid=%s',(uuid,))
    status=mycursor.fetchone()
    stat=status[0]
    print("Status: ", stat)
    print("usertype is", usertype)
    if request.method=="POST":
            if all([qid==qiid , session['loggedin']]):
                if usertype=='scholar':
                    if stat==1:
                        now=datetime.datetime.now()
                        mycursor.execute('insert into answer values (%s,%s,%s,%s, %s,%s,%s)', (uuid,usern,'NONE',qiid,ans,now.strftime("%I:%M %p"),now.strftime("%d %B %Y")))
                        mysql.connection.commit()
                        print(ans)
                        print(qiid)
                        print("ansshow is working ")
                        return redirect('/ansshow/'+qid)
                    elif stat==0:
                        print("Scholar is not verified.")
                        return render_template('ansshow.html',answer=answer,question=question,message='You can answer after verification.')
                    else:
                        print("stat is not getting value...")
                elif usertype=='User':
                    print("usertype is user")
                    return render_template('ansshow.html',answer=answer,question=question,message='Only verified scholars can answer.')
                else:
                    print("Something is wrong...") 
        
            return render_template('ansshow.html', question=question,answer=answer) 
    return render_template('ansshow.html', question=question,answer=answer)   
    

    
    
    
@app.route("/admin", methods =['GET', 'POST'])
def admin():
    mycursor=mysql.connection.cursor()
    mycursor.execute('select username, email, usertype, password, status from user where user.usertype="scholar"')
    alluser=mycursor.fetchall()
    if request.method=="POST":
        user=request.form
        category=user['category']
        print (category)
        uemail=request.form.get("email")
        if category=='active':
            mycursor.execute('update user set status="1" where email=%s',(uemail,))
            mysql.connection.commit()
            return redirect("admin")
        elif category=='deactive':
            mycursor.execute('update user set status="0" where email=%s',(uemail,))
            print(uemail)
            mysql.connection.commit()
            return redirect("admin")
        elif category=='delete':
            mycursor.execute('delete from user where email=%s',(uemail,))
            print(uemail)
            mysql.connection.commit()
            return redirect("admin")
    return render_template("admin.html",alluser=alluser)    



@app.route("/")
def home():
    return render_template("home.html")




@app.route('/logout')
def logout():
    session.pop('loggedin',None)
    session.pop('email',None)
    return redirect(url_for('login'))
    

@app.route("/masala")
def masala():
    return render_template("masala.html")

@app.route("/qa")
def qa():
    return render_template("qa.html")

@app.route("/info")
def info():
    return render_template("info.html")

@app.route("/video", methods =['GET', 'POST'])
def video():
    
        category=request.form.get('category')
        print (category)
        if category:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM VIDEO where videocategory=%s",(category,))
            data=cur.fetchall()
            print(data)
            return render_template("video.html",data=data)
        return render_template("video.html")
        

@app.route("/addvideo", methods =['GET', 'POST'])
def addvideo():
    message=''
    if request.method=='POST'  and  'videotitle' in request.form  and  'videocategory' in request.form  and  'videourl' in request.form :
        videotitle=request.form.get('videotitle')
        videocategory=request.form.get('videocategory')
        videourl=request.form.get('videourl')
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('insert into video values (%s,%s, %s, %s)', ('NONE',videotitle,videocategory,videourl))
        mysql.connection.commit()
        return render_template("addvideo.html", message="Video added successfully!")

    return render_template("addvideo.html")
    

@app.route("/calendar")
def calendar():
    return render_template("calendar.html")


@app.route("/main")
def main():
    return render_template("main.html")


@app.route("/articles",  methods =['GET', 'POST'])
def articles():
    name=session['username']
    message=''
    if request.method=='POST' and  'article' in request.form:
        article=request.form['article']
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('Select userid,username from user where userid= % s', (uuid,))
        account = cursor.fetchone()
        
        if account:
            now=datetime.datetime.now()
            cursor.execute('insert into article values (NULL,%s,%s, %s,%s,%s)', (uuid,name,article, now.strftime("%I:%M %p"),now.strftime("%d %B %Y")))
            mysql.connection.commit()
            return redirect('articleshow')
        elif not article:
            return render_template('articles.html',name=name, message='Please fill out the form!')
    return render_template('articles.html',name=name, message=message)



@app.route('/articleshow', methods =['GET', 'POST'])
def articleshow():
    
        mycursor=mysql.connection.cursor()
        mycursor.execute('select article_id,username,article,userid,date,time from article order by article_id desc')
        article=mycursor.fetchall()
        mysql.connection.commit()
        return render_template('articleshow.html', article=article,uuid=uuid)
   
    


@app.route('/editquestion',methods=['GET','POST'])
def editquestion():
    if request.method=="POST":
        info=request.form
        qid=info['qid']
        question=info['question']
        userid=info['userid']
        uid=int(userid)
        print(question)
        if uuid==uid :
            mycursor=mysql.connection.cursor()
            mycursor.execute("""UPDATE questions SET question=%s WHERE question_id=%s""",[question,qid])
            mysql.connection.commit()
            mycursor.close()
            return redirect('/ans')
        elif uuid!=uid:
            return redirect('/ans')
    else:
        return redirect('/ans')


@app.route('/editanswer',methods=['GET','POST'])
def editanswer():
    if request.method=="POST":
        info=request.form
        aid=info['aid']
        qid=info['qid']
        userid=info['userid']
        uid=int(userid)
        answer=info['answer']
        print(answer)
        if uuid==uid:
            mycursor=mysql.connection.cursor()
            mycursor.execute("""UPDATE answer SET answer=%s WHERE answer_id=%s""",[answer,aid])
            mysql.connection.commit()
            mycursor.close()
            return redirect('/ansshow/'+qid)
        elif uuid!=uid:
            return redirect('/ansshow/'+qid)
    else:
        return redirect('/ansshow')



@app.route('/editarticle',methods=['GET','POST'])
def editarticle():
        if request.method=="POST":
            info=request.form
            articleid=info['articleid']
            userid=info['userid']
            uid=int(userid)
            article=info['article']
            print(article)
            print("Userid from html: ",userid)
            print("Userid from html: ",uid)
            print("Userid from session: ",uuid)
            
            if uuid==uid :
                print ("Userid is getting from if: ", userid)
                mycursor=mysql.connection.cursor()
                mycursor.execute("""UPDATE article SET article=%s WHERE article_id=%s""",[article,articleid])
                mysql.connection.commit()
                mycursor.close()
                return redirect('/articleshow')
            elif uuid!=uid:
                print("This is else if")
                return redirect("/articleshow")
            
        return render_template("articleshow.html")



@app.route("/remove",methods=['GET','POST'])
def remove(): 
    if request.method=="POST":
        rev=request.form
        qid=rev['qid']
        userid=rev['userid']
        uid=int(userid)
        print("Qid id: ",qid)
        if uuid==uid :
            mycursor=mysql.connection.cursor()
            mycursor.execute("Delete from questions WHERE question_id=%s",[qid])
            mycursor.execute("Delete from answer WHERE question_id=%s",[qid])
            mysql.connection.commit()
            return redirect('/ans')
        elif uuid!=uid:
            return redirect('/ans')
    else:
        return redirect('/ans')
    
@app.route("/removeanswer",methods=['GET','POST'])
def removeanswer(): 
    if request.method=="POST":
        rev=request.form
        aid=rev['aid']
        qid=rev['qid']
        userid=rev['userid']
        uid=int(userid)
        print("Answer id: ",aid)
        if uuid==uid :
            mycursor=mysql.connection.cursor()
            mycursor.execute("Delete from answer WHERE answer_id=%s",[aid])
            mysql.connection.commit()
            return redirect('/ansshow/'+qid)
        elif uuid!=uid:
            return redirect('/ansshow/'+qid)
    else:
        return redirect('/ansshow')


    
@app.route("/removearticle",methods=['GET','POST'])
def removearticle(): 
    if request.method=="POST":
        rev=request.form
        articleid=rev['articleid']
        userid=rev['userid']
        uid=int(userid)
        print("Article id: ",articleid)
        if uuid==uid :
            mycursor=mysql.connection.cursor()
            mycursor.execute("Delete from article WHERE article_id=%s",[articleid])
            mysql.connection.commit()
            return redirect('/articleshow')
        elif uuid!=uid:
            return redirect('/articleshow')
    else:
        return redirect('/articleshow')


@app.route("/quran")
def quran():
    return render_template('quran.html')

@app.route("/bukhari")
def bukhari():
    return render_template('bukhari.html')

@app.route("/bukhari1")
def bukhari1():
    return render_template('bukhari1.html')

@app.route("/bukhari2")
def bukhari2():
    return render_template('bukhari2.html')

@app.route("/bukhari3")
def bukhari3():
    return render_template('bukhari3.html')

@app.route("/bukhari4")
def bukhari4():
    return render_template('bukhari4.html')

@app.route("/bukhari5")
def bukhari5():
    return render_template('bukhari5.html')

@app.route("/bukhari6")
def bukhari6():
    return render_template('bukhari6.html')

@app.route("/bukhari7")
def bukhari7():
    return render_template('bukhari7.html')

@app.route("/bukhari8")
def bukhari8():
    return render_template('bukhari8.html')

@app.route("/bukhari9")
def bukhari9():
    return render_template('bukhari9.html')

@app.route("/bukhari10")
def bukhari10():
    return render_template('bukhari10.html')


@app.route('/dropsession')
def dropsession():
    session.pop('user',None)
    return redirect('/')

if __name__=="__main__":
    app.run(debug=True)