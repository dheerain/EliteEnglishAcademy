from flask import *  
from flask_login import login_required
from config import userCredentialDict
from  student_module import *
from datetime import timedelta


app = Flask(__name__, static_url_path="", static_folder="templates")  
app.secret_key ='dheerain'


@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=10)

@app.route('/')  
def index():  
      user = session.get('username', None)
      if user == None:
            return redirect("/login")      
      session_toggle = "Logout" if user else "Login"
      table = getFeesDelayTable(user.lower())
      return render_template('index.html',user= user,
                              session_toggle = session_toggle,renderTable = table )
      

@app.route('/dashboard')  
def dashboard():
      user = session.get('username', None)
      if user == None:
            return redirect("/login")      
      session_toggle = "Logout" if user else "Login"
      return render_template('dashboard.html',user= user.upper(),session_toggle = session_toggle)  


@app.route('/login')  
def login():  
      #If Login Credentials are correct  or User is already logged in then Open the Dashboard
      print("Going to render Login.html File")
      username = session.get('username')
      if not username:
            return render_template('login.html',response= "")
      else:
            session['username']=None
            return render_template('index.html',user= None,session_toggle = "Login")

@app.route('/submit',methods = ['POST'])  
def submit():  
      isSuccessful = False
      if request.method == 'POST':
            result = request.form
            print(result)
            isSuccessful = authenticate(result.get('username'),result.get('password'))
      if isSuccessful:
            session['username'] = result.get('username')
            user = session['username'].upper() if session['username'] else None
            table = getFeesDelayTable(user.lower())
            return render_template('index.html',user=user ,session_toggle = "Logout",renderTable = table )
      else:
            return render_template('login.html',response= "Invalid Credentials")
      
@app.route('/newadmission')  
def newadmission(): 
      user = session.get('username', None)
      if user == None:
            return redirect("/login")      
      user = session.get('username', None)
      user = user.upper() if user else None
      session_toggle = "Logout" if user else "Login"
      return render_template('newStudent.html',user= user,
                              session_toggle = session_toggle)


def authenticate(username,password):
      userData = userCredentialDict.get(username) 
      if userData and userData.get('password') == password:
            return True
      else:
            return False

@app.route('/result',methods = ['POST', 'GET'])
def result():
   if request.method == 'POST':
      result = request.form
      return result

@app.route('/submitadmissiondata',methods = ['POST'])
def submitAdmissionData():
      
      user = session.get('username', None)
      if user == None:
            return redirect("/login")      
      if request.method == 'POST': 
            result = request.form.to_dict()
            status  = saveStudentData(result)
      
      return render_template('congratulations.html',user= user,session_toggle = "Logout", information = status)
      
@app.route('/attendance_pte')
def attenance_pte():
      user = session.get('username', None)
      if user == None:
            return redirect("/login")      
      data = getPTEStudentList()
      # print(data)
      return render_template('attendance_pte.html',user=user ,session_toggle = "Logout",date = datetime.date.today().strftime('%Y-%m-%d'),data =enumerate(data))

@app.route('/attendance_ielts')
def attenance_ielts():
      user = session.get('username', None)
      if user == None:
            return redirect("/login")      
      data = getIELTSStudentList()
      return render_template('attendance_ielts.html',user=user ,session_toggle = "Logout",date = datetime.date.today().strftime('%Y-%m-%d'),data =enumerate(data))

@app.route('/submit_attendance_data_pte',methods = ['POST'])
def submit_attenance_pte():
      user = session.get('username', None)
      if user == None:
            return redirect("/login" )      
      if request.method == 'POST':
            print("Dheerain")
            result = request.form
            print(result)
            saveAttendanceDataPTE(result)
      
      return render_template('success.html',user= user,session_toggle = "Logout", head1='Attendance For ' ,head2=  result.to_dict().get('attendanceDate'),information = 'Successfully Saved ')
      
@app.route('/submit_attendance_data_ielts',methods = ['POST'])
def submit_attenance_ielts():
      user = session.get('username', None)
      if user == None:
            return redirect("/login" )      
      if request.method == 'POST':
            print("Dheerain")
            result = request.form
            print(result)
            saveAttendanceDataIELTS(result)
      
      return render_template('success.html',user= user,session_toggle = "Logout", head1='Attendance For' ,head2=  result.to_dict().get('attendanceDate'),information = 'Successfully Saved')

@app.route('/search',methods= ['GET','POST'])
def search():
      user = session.get('username', None) 
      if user == None:
            return redirect("/login" )      
      
      if request.method == 'POST':
            result = request.form.to_dict().get('name')
            data = searchStudentDatabyName(result)
            # print(data)
            return  render_template('search.html' ,user= user,session_toggle = "Logout", head1='Search For Student Data' ,head2= '',information = '', data=enumerate(data))
      return render_template('search.html',user= user,session_toggle = "Logout", head1='Search For Student Data' ,head2= '',information = '')

@app.route('/getStudentData',methods= ['POST'])
def getStudentData():
      user = session.get('username', None) 
      if user == None:
            return redirect("/login" )
      if request.method == 'POST':
            result = request.form.to_dict().get('name')
            return  render_template('success.html' ,user= user,session_toggle = "Logout", head1='Search For Student Data' ,head2= '',information = '')


@app.route('/showstudentdata/<studentid>',methods= ['GET','POST'])
def showStudentData(studentid):
      print(studentid)
      user = session.get('username', None) 
      if user:
            data = searchStudentDatabyID(studentid)
            attendanceData = getAttendanceDatabyID(studentid)
            installment = getPendingInstallmentStatus(studentid).get('COMMENT')
            paymentData = getPaymentInfo(studentid)
            return  render_template('show_edit_student_data.html' ,user= user,session_toggle = "Logout", head1='Search For Student Data' ,head2= '',information = '',data=data[0],attendance = attendanceData, installment = installment, paymentData = paymentData)
      else:
            return  redirect("/login" ) # ,user= user,session_toggle = "Logout", head1='Search For Student Data' ,head2= '',information = '')

@app.route('/dopayment/<studentid>')
def doPayment(studentid):
      print(studentid)
      user = session.get('username', None) 
      if user:
            userData = userCredentialDict.get(user.lower())
            if userData.get('adminAccess') :
                  data = getPendingInstallmentStatus(studentid)
                  data['date'] = datetime.date.today()
                  return  render_template('dopayment.html' ,user= user,session_toggle = "Logout", data = data)
            else:
                  return redirect("/")
      else:
            return  redirect("/login" )


@app.route('/savepayment/<studentid>')
def confirmpayment(studentid):
      print(studentid)
      user = session.get('username', None) 
      if user:
            data = savePayment(studentid)
            return  redirect('/')
      else:
            return redirect("/login" )

@app.route('/updatestudentdata',methods= ['GET','POST'])
def updateStudentData():
      user = session.get('username', None) 
      if not user:
            return redirect("/login" )
      if request.method == 'POST':
            result = request.form.to_dict()
            print(result)
            userData = userCredentialDict.get(user) 
            if userData and userData.get('adminAccess'):                             
                  updateStudentDatabyID(result)
                  data = searchStudentDatabyID(result['STUDENT_ID'])
                  attendanceData = getAttendanceDatabyID(result['STUDENT_ID'])
                  paymentData = getPaymentInfo(result['STUDENT_ID'])
                  return  render_template('show_edit_student_data.html' ,user= user,session_toggle = "Logout", head1='Search For Student Data' ,head2= '',information = '',data=data[0],attendance = attendanceData,paymentData=paymentData)
            else:
                  data = searchStudentDatabyID(result['STUDENT_ID'])
                  attendanceData = getAttendanceDatabyID(result['STUDENT_ID'])
                  return  render_template('show_edit_student_data.html' ,user= user,session_toggle = "Logout", head1='Search For Student Data' ,head2= 'Do not have access to edit',information = '',data=data[0],attendance = attendanceData)


@app.route('/<name>.html')
def restrictFileAccess(name):
      print(name)
      if name == 'components':
            return render_template('components.html')
      user = session.get('username', None) 
      if not user:
            return redirect("/login" )
      else:
            return redirect("/" )

if __name__ == '__main__':  
   app.run( host='0.0.0.0',debug = True,port=5000)  