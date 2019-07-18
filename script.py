from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
import psycopg2 as pg
import re
from textblob import TextBlob
app=Flask('__name__')       

@app.route('/')
def home():
	if 'uname' in session:
        
		return redirect(url_for('Dashboard',name=session['uname']))
	
	return render_template('OL.html')

@app.route('/About')
def About():
	if 'uname' in session:
		return render_template('About.html',name=session['uname'])
	else:
		return render_template(redirect(url_for('home')))
@app.route('/signout')
def Signout():
    if 'uname' in session:
        session.clear()
    return redirect(url_for('home'))
@app.route('/Summary',methods=['POST','GET'])
def Summary():
    conn=pg.connect("dbname='database1' user='postgres' password='postgre'")
    curr=conn.cursor()
    if request.method=='POST':
        if 'uname' in session:
           
            name1=str(request.form['bookname'])
            content1=str(request.form['editor1'])
            try:
                curr.execute("insert into summary (name,content,mail) values(%s,%s,%s)",(name1,content1,str(session['uname'])))
                conn.commit()

            except Exception as e:
                    conn.rollback()
            
            curr=conn.cursor()
            name2=str(session['uname'])
            query1="select name,content,id from summary where mail='{}'".format(name2)
            curr.execute(query1)
            ans=curr.fetchall()
            return render_template('Summa.html',name=session['uname'],posts=ans)
    else:    
        name=str(session['uname'])
        query1="select name,content,id from summary where mail='{}'".format(name)
        curr.execute(query1)
        ans=curr.fetchall()
        return render_template('Summa.html',name=session['uname'],posts=ans)

@app.route('/home')
def login():
    if 'uname' in session:
        return render_template("Recently.html",name=session['uname'])
    if 'reg' in session:
        session.pop("reg",None)
        return render_template('signin.html',reg="error")
    if 'msg' in session:
        session.pop("msg",None)
        return render_template('signin.html',msg="error")
    
    return render_template('signin.html')
@app.route('/register',methods=['GET','POST'])
def register():
    reg=''
   
    if request.method=='POST':
        try:
            conn=pg.connect("dbname='database1' user='postgres' password='postgre'")
            curr=conn.cursor()
            email=str(request.form['email'])
            pwd=str(request.form['password'])
            first=str(request.form['first'])
            last=str(request.form['last'])
           
            curr.execute("insert into login (name,password,first,last) values(%s,%s,%s,%s)",(email,pwd,first,last))
            conn.commit()
            return redirect(url_for('home'))
        except Exception:
            reg="Already Registered"
            session["reg"]=reg
            print("insert error")
            return redirect(url_for('login'))
        finally:
            conn.close()
            
    return render_template('register.html')

@app.route('/search',methods=['GET','POST'])
def Search():
    if request.method=='POST':
        name=str(request.form['Query'])
        name=name.lower()
        blob=TextBlob(name)
        name=str(blob.correct())
        name=re.sub(r'[^a-z]','',name)
        
        
       
        
        
        conn=pg.connect("dbname='database1' user='postgres' password='postgre'")
        curr=conn.cursor()
        query="select * from books where bname like '%{}%' or author like '%{}%'".format(name,name)
        curr.execute(query)
        results=curr.fetchall()
        if len(results)>0:
            tup=results[0]
            try:
                curr.execute("insert into user_tab (name,bname) values(%s,%s)",(str(session['email']),str(tup[0])))
               
                conn.commit()
                
               
            except Exception:
                print('insert error')
            finally:
                curr.close()
                conn.close()

        return render_template('search.html',results=results,name=session['uname'])
       
    else:
        return redirect(url_for('Dashboard'))


@app.route('/delete',methods=['POST','GET'])
def Delete():
    conn=pg.connect("dbname='database1' user='postgres' password='postgre'")
    curr=conn.cursor()
    if request.method=='POST':
        id1=int(request.form['numid'])
        try:
            curr.execute("delete from summary where id={}".format(id1))
            conn.commit()
        except Exception as e:
            conn.rollback()
        return redirect(url_for('Summary'))
    return redirect(url_for('Dashboard'))
    
        
 


@app.route('/Dashboard',methods=['GET','POST'])
def Dashboard():
    if request.method=='POST':
        pwd=str(request.form['inputPassword'])
        email=str(request.form['inputEmail'])
        conn=pg.connect("dbname='database1' user='postgres' password='postgre'")
        curr=conn.cursor()
        query="select * from login where name='{}'".format(email)

        curr.execute(query)
        li=[]
        li=curr.fetchall()
         
        
       

        """Error coming check needs flashing messaging"""


        if len(li)<=0:
            session['msg']="Wrong credentials"
            curr.close()
            conn.close()
            return redirect(url_for('login'))

        if li[0][1]==pwd:
            session['uname']=li[0][2]
            session['email']=email
            
            query="select distinct(b.*) from books b natural join user_tab where name='{}'".format(email)
            curr.execute(query);
            recent=curr.fetchall()
            session['recent']=recent
            query="select * from books order by tim_add desc limit 3"
            curr.execute(query)
            arrival=curr.fetchall()
            session['arrival']=arrival
            
            curr.close()
            conn.close()
            
            return render_template("Recently.html",name=session['uname'],recent=recent,arrival=session['arrival'])

        elif li[0][0]==email and li[0][1]!=pwd:
            session['msg']="Wrong credentials"
            curr.close()
            conn.close()
            return redirect(url_for('login'))
       


		
    else:
        if 'uname' in session:
            return render_template("Recently.html",name=session['uname'],recent=session['recent'],arrival=session['arrival'])
           
        else:
            return redirect(url_for('home'))




if __name__=='__main__':
	app.secret_key='secret12345'
	app.run(debug=True)