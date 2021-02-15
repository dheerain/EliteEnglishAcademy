import datetime
import pymysql
import os
from config import userCredentialDict

connection= pymysql.connect(host='localhost',
                             user='dheerain',
                             password='root',
                             db='ELITE_ACADEMY',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor,
                             autocommit=True
                            )

def generateStudentId(enroll,date):
    id  = enroll[0] + date.strftime('%b').upper() + getLargestNumber()
    return id

def getLargestNumber():
    result = '{0:03}'.format(int(getMaxNumber()%100))
    return result
    
def getMaxNumber():
    res = selectQuery('SELECT MAX(NUMBER) FROM STUDENT;')
    return res[0].get('MAX(NUMBER)')+1 if res[0].get('MAX(NUMBER)') else 1

def selectQuery(query):
    try:
        with connection.cursor() as cur:
            cur.execute(query )
            rows = cur.fetchall()
            return rows
    finally:
        pass
        # connection.close()
    return rows

def updateQuery(query):
    if not isinstance(query,list):
        query =[query]
    try:
        with connection.cursor() as cur:
            for i in query:
                status = cur.execute(i)
                print(status)
    except Exception as e:
        return str(e)
    return 'SUCCESS'

def updateStudentID(currentStudentId,finalStudentId):
    updateStudentTable = 'UPDATE STUDENT SET STUDENT_ID = {0} WHERE STUDENT_ID = {1};'.format(finalStudentId,currentStudentId)
    updateAttendanceTable = 'UPDATE ATTENDANCE SET STUDENT_ID = {0} WHERE STUDENT_ID = {1};'.format(finalStudentId,currentStudentId)
    updatePaymentTable = 'UPDATE STUDENT_FEES SET STUDENT_ID = {0} WHERE STUDENT_ID = {1};'.format(finalStudentId,currentStudentId)
    updateQuery(updateStudentTable)
    updateQuery(updateAttendanceTable)
    updateQuery(updatePaymentTable)

def saveStudentData(result):
    print(result)
    studentId =  result.get('rollnum') if result.get('rollnum') else  generateStudentId(result.get('option'),datetime.date.today()) 
    query ="""INSERT INTO STUDENT (STUDENT_ID,NAME,FATHERS_NAME,MOTHERS_NAME,ADDRESS,MOBILE_NO,ALT_MOBILE_NO,GENDER,DATE_OF_BIRTH,EMAIL,NAME_OF_LAST_SCHOOL,ENROLLED_IN,CONTRACT_STATUS,CONTRACT_START_DATE) VALUES ( """ +\
        "'{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}',{13});".format(
            studentId,
            result.get('name'),
            result.get('father_name'),
            result.get('mothers_name'),
            result.get('address'),
            result.get('mobile'),
            result.get('AltMobile'),
            result.get('gender').upper(),
            datetime.datetime.strptime(result.get('dob'),'%Y-%m-%d').strftime('%Y%m%d'),
            result.get('EmailId'),
            result.get('school'),
            result.get('option'),
            'ACTIVE',
            datetime.date.today().strftime('%Y%m%d')
        )
    print("Inserting Payment Information")

    return insertPaymentInfo(studentId,result,finalQuery=query)
    

def insertPaymentInfo(studentId,result,finalQuery):
    date_1 =datetime.date.today()
    date_2 =datetime.date.today() + datetime.timedelta(days=30)
    date_3 =datetime.date.today() + datetime.timedelta(days=60)
    date_4 =datetime.date.today() + datetime.timedelta(days=90)
    date_5 =datetime.date.today() + datetime.timedelta(days=120)
    date_6 =datetime.date.today() + datetime.timedelta(days=150)
    query = """INSERT INTO STUDENT_FEES (STUDENT_ID,FINALIZED_FEES,FEES_1_DUE_DATE,FEES_1_STATUS,FEES_2_DUE_DATE,
    FEES_2_STATUS,FEES_3_DUE_DATE,FEES_3_STATUS,FEES_4_DUE_DATE,FEES_4_STATUS,FEES_5_DUE_DATE,FEES_5_STATUS,
    FEES_6_DUE_DATE,FEES_6_STATUS) VALUES ('{0}',{1},'{2}','PENDING',
    '{3}','PENDING','{4}','PENDING','{5}','PENDING','{6}','PENDING','{7}','PENDING');"""\
        .format(studentId,int(result.get('fees')),date_1.strftime('%Y%m%d'),date_2.strftime('%Y%m%d'),date_3.strftime('%Y%m%d'),\
        date_4.strftime('%Y%m%d'),date_5.strftime('%Y%m%d'),date_6.strftime('%Y%m%d'))
    listOfQueries = [finalQuery, query]
    return updateQuery(listOfQueries)
    
def searchStudentDatabyName(studentName):
    query = "SELECT * FROM STUDENT WHERE UPPER(NAME) LIKE '%{0}%'".format(studentName)
    data = selectQuery(query)
    return data

def searchStudentDatabyID(studentID=''):
    query = "SELECT * FROM STUDENT WHERE STUDENT_ID  = '{0}'".format(studentID)
    data = selectQuery(query)
    return data

def updateStudentDatabyID(data):
    # if data['CONTRACT_TERMINATION_DATE'] else '1970-01-01' 
    contract_termination_date = None
    if ( not data['CONTRACT_TERMINATION_DATE'] or data['CONTRACT_TERMINATION_DATE'] != '1970-01-01')  and data['CONTRACT_STATUS'] == 'TERMINATED':
        contract_termination_date = datetime.date.today()
    else:
        contract_termination_date = data['CONTRACT_TERMINATION_DATE']

    query = """UPDATE STUDENT SET NAME='{0}',FATHERS_NAME='{1}',MOTHERS_NAME='{2}',ADDRESS='{3}',MOBILE_NO='{4}',
    ALT_MOBILE_NO='{5}',GENDER='{6}',DATE_OF_BIRTH='{7}',EMAIL='{8}',NAME_OF_LAST_SCHOOL='{9}',ENROLLED_IN='{10}',
    CONTRACT_STATUS='{11}',CONTRACT_START_DATE='{12}',CONTRACT_TERMINATION_DATE = '{13}',BANDS_RECEIVED={14} WHERE STUDENT_ID = '{15}';""".format(
    data['NAME'],
    data['FATHERS_NAME'],
    data['MOTHERS_NAME'],
    data['ADDRESS'],
    data['MOBILE_NO'],
    data['ALT_MOBILE_NO'],
    data['GENDER'],
    data['DATE_OF_BIRTH'],
    data['EMAIL'],
    data['NAME_OF_LAST_SCHOOL'],
    data['ENROLLED_IN'],
    data['CONTRACT_STATUS'],
    data['CONTRACT_START_DATE'],
    contract_termination_date,
    float(data['BANDS_RECEIVED']) if data['BANDS_RECEIVED']!= 'None' else 0 ,
    data['STUDENT_ID']
    )

    data = updateQuery(query)
    return "Success" 

def getAttendanceDatabyID(studentID=''):
    query = "SELECT ATTENDANCE_DATE, STATUS FROM ATTENDANCE WHERE STUDENT_ID = '{0}' ORDER BY ATTENDANCE_DATE;".format(studentID)
    data = selectQuery(query)
    return data

def getPTEStudentList():
    query = "SELECT STUDENT_ID, NAME FROM STUDENT WHERE ENROLLED_IN='PTE' AND CONTRACT_STATUS='ACTIVE';"
    data = selectQuery(query)
    return data

def getIELTSStudentList():
    query = "SELECT STUDENT_ID, NAME FROM STUDENT WHERE ENROLLED_IN='IELTS' AND CONTRACT_STATUS='ACTIVE';"
    data = selectQuery(query)
    return data

def saveAttendanceDataPTE(data):
    data = data.to_dict()
    attendanceDate = data.get('attendanceDate')
    attendanceDate = datetime.datetime.strptime(attendanceDate,'%Y-%m-%d').strftime('%Y%m%d')
    del data['attendanceDate']
    numberOfRecords =  len([k for k in data.keys() if k.startswith('studentname')])
    for i in range(0,numberOfRecords):
        findData = """SELECT ATTENDANCE_DATE, STUDENT_ID,CLASS,STATUS ATTENDANCE  FROM ATTENDANCE WHERE ATTENDANCE_DATE='{0}' \
                     AND STUDENT_ID = '{1}' AND CLASS ='PTE';""".format(attendanceDate,data['studentid_' +str(i)])
        getData = selectQuery(findData)
        if getData:
            update = """UPDATE ATTENDANCE SET STATUS='{0}' WHERE ATTENDANCE_DATE='{1}' \
                     AND STUDENT_ID = '{2}' AND CLASS ='PTE';""".format(data.get('present_' +str(i),'off'),attendanceDate,data['studentid_' +str(i)])
            updateQuery(update)
        else:
            query = 'INSERT INTO ATTENDANCE (ATTENDANCE_DATE, STUDENT_ID,CLASS,STATUS) VALUES(' +\
                "'{0}','{1}','{2}','{3}');".format(attendanceDate,data['studentid_' +str(i)],'PTE',data.get('present_' +str(i),'off'))
            updateQuery(query)
    return "Success"

def saveAttendanceDataIELTS(data):
    data = data.to_dict()
    attendanceDate = data.get('attendanceDate')
    attendanceDate = datetime.datetime.strptime(attendanceDate,'%Y-%m-%d').strftime('%Y%m%d')
    del data['attendanceDate']
    numberOfRecords =  len([k for k in data.keys() if k.startswith('studentname')])
    for i in range(0,numberOfRecords):
        findData = """SELECT ATTENDANCE_DATE, STUDENT_ID,CLASS,STATUS ATTENDANCE  FROM ATTENDANCE WHERE ATTENDANCE_DATE='{0}' \
                     AND STUDENT_ID = '{1}' AND CLASS ='IELTS';""".format(attendanceDate,data['studentid_' +str(i)])
        getData = selectQuery(findData)
        if getData:
            update = """UPDATE ATTENDANCE SET STATUS='{0}' WHERE ATTENDANCE_DATE='{1}' \
                     AND STUDENT_ID = '{2}' AND CLASS ='IELTS';""".format(data.get('present_' +str(i),'off'),attendanceDate,data['studentid_' +str(i)])
            updateQuery(update)
        else:
            query = 'INSERT INTO ATTENDANCE (ATTENDANCE_DATE, STUDENT_ID,CLASS,STATUS) VALUES(' +\
                "'{0}','{1}','{2}','{3}');".format(attendanceDate,data['studentid_' +str(i)],'IELTS',data.get('present_' +str(i),'off'))
            updateQuery(query)
    return "Success"

def getFeesDelayTable(user):
    userData = userCredentialDict.get(user)
    query = """SELECT  STUDENT.ENROLLED_IN,STUDENT.NAME,STUDENT.CONTRACT_START_DATE,STUDENT_FEES.*  FROM STUDENT_FEES, STUDENT  WHERE STUDENT.STUDENT_ID = STUDENT_FEES.STUDENT_ID
                AND (FEES_1_STATUS ='PENDING' OR FEES_2_STATUS ='PENDING' OR FEES_3_STATUS ='PENDING' OR FEES_4_STATUS ='PENDING' OR FEES_5_STATUS ='PENDING' OR FEES_6_STATUS ='PENDING') 
                AND STUDENT.CONTRACT_STATUS = 'ACTIVE';"""
    result = (selectQuery(query))
    if  userData.get('takingclass')  in ['IELTS','PTE']:
        # filteredresult = list(filter(lambda d: d['ENROLLED_IN'] == userData.get('takingclass'), result))
        filteredresult = [d for d in result if d['ENROLLED_IN'] == userData.get('takingclass')]
    else:
        filteredresult = result 
    
    pendingFeesStatusTable = []
    
    for data in filteredresult:
        if data['FEES_1_DUE_DATE']<= datetime.date.today() and data['FEES_1_STATUS']=='PENDING':
            print("FIRST_INSTALLMENT_PENDING",data['CONTRACT_START_DATE'].strftime('%Y-%m-%d'))
            pendingFeesStatusTable.append(
                {'ENROLLED_IN': data['ENROLLED_IN'],
                'STUDENT_ID': data['STUDENT_ID'],
                'NAME': data['NAME'],
                'ContractStartDate': data['CONTRACT_START_DATE'].strftime('%Y-%m-%d'),
                 'COMMENT': "FIRST_INSTALLMENT_PENDING",
                 'PENDING_FROM': data['FEES_1_DUE_DATE']}
            )
            continue
        elif data['FEES_2_DUE_DATE']<= datetime.date.today() and data['FEES_2_STATUS']=='PENDING':
            print("SECOND_INSTALLMENT_PENDING")
            pendingFeesStatusTable.append(
                {'ENROLLED_IN': data['ENROLLED_IN'],
                'STUDENT_ID': data['STUDENT_ID'],
                'NAME': data['NAME'],
                'ContractStartDate': data['CONTRACT_START_DATE'].strftime('%Y%m%d'),
                'COMMENT': "SECOND_INSTALLMENT_PENDING",
                'PENDING_FROM': data['FEES_2_DUE_DATE']}
            )
            continue
        elif data['FEES_3_DUE_DATE']<= datetime.date.today() and data['FEES_3_STATUS']=='PENDING':
            print("THIRD_INSTALLMENT_PENDING")
            pendingFeesStatusTable.append(
                {'ENROLLED_IN': data['ENROLLED_IN'],
                'STUDENT_ID': data['STUDENT_ID'],
                'NAME': data['NAME'],
                'ContractStartDate': data['CONTRACT_START_DATE'].strftime('%Y%m%d'),
                 'COMMENT': "THIRD_INSTALLMENT_PENDING",
                 'PENDING_FROM': data['FEES_3_DUE_DATE']}
            )
            continue
        elif data['FEES_4_DUE_DATE']<= datetime.date.today() and data['FEES_4_STATUS']=='PENDING':
            print("FOURTH_INSTALLMENT_PENDING")
            pendingFeesStatusTable.append(
                {'ENROLLED_IN': data['ENROLLED_IN'],
                'STUDENT_ID': data['STUDENT_ID'],
                'NAME': data['NAME'],
                'ContractStartDate': data['CONTRACT_START_DATE'].strftime('%Y%m%d'),
                 'COMMENT': "FOURTH_INSTALLMENT_PENDING",
                 'PENDING_FROM': data['FEES_4_DUE_DATE']}
            )
            continue
        elif data['FEES_5_DUE_DATE']<= datetime.date.today() and data['FEES_5_STATUS']=='PENDING':
            print("FIFTH_INSTALLMENT_PENDING")
            pendingFeesStatusTable.append(
                {'ENROLLED_IN': data['ENROLLED_IN'],
                'STUDENT_ID': data['STUDENT_ID'],
                'NAME': data['NAME'],
                'ContractStartDate': data['CONTRACT_START_DATE'].strftime('%Y%m%d'),
                 'COMMENT': "FIFTH_INSTALLMENT_PENDING",
                 'PENDING_FROM': data['FEES_5_DUE_DATE']}
            )
            continue
        elif data['FEES_6_DUE_DATE']<= datetime.date.today() and data['FEES_6_STATUS']=='PENDING':
            pendingFeesStatusTable.append(
                {'ENROLLED_IN': data['ENROLLED_IN'],
                'STUDENT_ID': data['STUDENT_ID'],
                'NAME': data['NAME'],
                'ContractStartDate': data['CONTRACT_START_DATE'].strftime('%Y%m%d'),
                 'COMMENT': "SIXTH_INSTALLMENT_PENDING",
                 'PENDING_FROM': data['FEES_6_DUE_DATE']}
            )
            print("SIXTH_INSTALLMENT_PENDING")
            continue
    return pendingFeesStatusTable
        # print(i['ENROLLED_IN'],i['STUDENT_ID'],i['NAME'] )


def getPendingInstallmentStatus(studentId):
    query = """SELECT  STUDENT.ENROLLED_IN,STUDENT.NAME,STUDENT.MOBILE_NO,STUDENT.CONTRACT_START_DATE,STUDENT_FEES.*  FROM STUDENT_FEES, STUDENT  WHERE STUDENT.STUDENT_ID = STUDENT_FEES.STUDENT_ID
                AND (FEES_1_STATUS ='PENDING' OR FEES_2_STATUS ='PENDING' OR FEES_3_STATUS ='PENDING' OR FEES_4_STATUS ='PENDING' OR FEES_5_STATUS ='PENDING' OR FEES_6_STATUS ='PENDING') 
                AND STUDENT.STUDENT_ID = '{0}';""".format(studentId)
    result = (selectQuery(query))
    pendingFeesStatusTable = []
    
    for data in result:
        if data['FEES_1_DUE_DATE']<= datetime.date.today() and data['FEES_1_STATUS']=='PENDING':
            print("FIRST_INSTALLMENT_PENDING",data['CONTRACT_START_DATE'].strftime('%Y-%m-%d'))
            pendingFeesStatusTable.append(
                {'ENROLLED_IN': data['ENROLLED_IN'],
                'STUDENT_ID': data['STUDENT_ID'],
                'NAME': data['NAME'],
                'ContractStartDate': data['CONTRACT_START_DATE'].strftime('%Y-%m-%d'),
                 'COMMENT': "First Installment",
                 'MOBILE_NO':  data['MOBILE_NO'],
                 'FEES': data['FINALIZED_FEES'],
                 'PENDING_FROM': data['FEES_1_DUE_DATE'],
                 }
            )
            continue
        elif data['FEES_2_DUE_DATE']<= datetime.date.today() and data['FEES_2_STATUS']=='PENDING':
            print("SECOND_INSTALLMENT_PENDING")
            pendingFeesStatusTable.append(
                {'ENROLLED_IN': data['ENROLLED_IN'],
                'STUDENT_ID': data['STUDENT_ID'],
                'NAME': data['NAME'],
                'ContractStartDate': data['CONTRACT_START_DATE'].strftime('%Y%m%d'),
                'COMMENT':"Second Installment",
                'MOBILE_NO':  data['MOBILE_NO'],
                'FEES': data['FINALIZED_FEES'],
                'PENDING_FROM': data['FEES_2_DUE_DATE']}
            )
            continue
        elif data['FEES_3_DUE_DATE']<= datetime.date.today() and data['FEES_3_STATUS']=='PENDING':
            print("THIRD_INSTALLMENT_PENDING")
            pendingFeesStatusTable.append(
                {'ENROLLED_IN': data['ENROLLED_IN'],
                'STUDENT_ID': data['STUDENT_ID'],
                'NAME': data['NAME'],
                'ContractStartDate': data['CONTRACT_START_DATE'].strftime('%Y%m%d'),
                 'COMMENT': "Third Installment",
                 'MOBILE_NO':  data['MOBILE_NO'],
                 'FEES': data['FINALIZED_FEES'],
                 'PENDING_FROM': data['FEES_3_DUE_DATE']}
            )
            continue
        elif data['FEES_4_DUE_DATE']<= datetime.date.today() and data['FEES_4_STATUS']=='PENDING':
            print("FOURTH_INSTALLMENT_PENDING")
            pendingFeesStatusTable.append(
                {'ENROLLED_IN': data['ENROLLED_IN'],
                'STUDENT_ID': data['STUDENT_ID'],
                'NAME': data['NAME'],
                'ContractStartDate': data['CONTRACT_START_DATE'].strftime('%Y%m%d'),
                 'COMMENT': "Fourth Installment",
                 'MOBILE_NO':  data['MOBILE_NO'],
                 'FEES': data['FINALIZED_FEES'],
                 'PENDING_FROM': data['FEES_4_DUE_DATE']}
            )
            continue
        elif data['FEES_5_DUE_DATE']<= datetime.date.today() and data['FEES_5_STATUS']=='PENDING':
            print("FIFTH_INSTALLMENT_PENDING")
            pendingFeesStatusTable.append(
                {'ENROLLED_IN': data['ENROLLED_IN'],
                'STUDENT_ID': data['STUDENT_ID'],
                'NAME': data['NAME'],
                'ContractStartDate': data['CONTRACT_START_DATE'].strftime('%Y%m%d'),
                 'COMMENT': "Fifth Installment",
                 'MOBILE_NO':  data['MOBILE_NO'],
                 'FEES': data['FINALIZED_FEES'],
                 'PENDING_FROM': data['FEES_5_DUE_DATE']}
            )
            continue
        elif data['FEES_6_DUE_DATE']<= datetime.date.today() and data['FEES_6_STATUS']=='PENDING':
            pendingFeesStatusTable.append(
                {'ENROLLED_IN': data['ENROLLED_IN'],
                'STUDENT_ID': data['STUDENT_ID'],
                'NAME': data['NAME'],
                'ContractStartDate': data['CONTRACT_START_DATE'].strftime('%Y%m%d'),
                 'COMMENT': "Sixth Installment",
                 'MOBILE_NO':  data['MOBILE_NO'],
                 'FEES': data['FINALIZED_FEES'],
                 'PENDING_FROM': data['FEES_6_DUE_DATE']}
            )
            print("SIXTH_INSTALLMENT_PENDING")
            continue
    return pendingFeesStatusTable[0] if pendingFeesStatusTable else {}

def savePayment(studentId):
    query = """SELECT  STUDENT.ENROLLED_IN,STUDENT.NAME,STUDENT.MOBILE_NO,STUDENT.CONTRACT_START_DATE,STUDENT_FEES.*  FROM STUDENT_FEES, STUDENT  WHERE STUDENT.STUDENT_ID = STUDENT_FEES.STUDENT_ID
                AND (FEES_1_STATUS ='PENDING' OR FEES_2_STATUS ='PENDING' OR FEES_3_STATUS ='PENDING' OR FEES_4_STATUS ='PENDING' OR FEES_5_STATUS ='PENDING' OR FEES_6_STATUS ='PENDING') 
                AND STUDENT.STUDENT_ID = '{0}';""".format(studentId)
    result = selectQuery(query)
    query = 'UPDATE STUDENT_FEES SET '
    data = result[0]
    if data['FEES_1_DUE_DATE']<= datetime.date.today() and data['FEES_1_STATUS']=='PENDING':
        query += "FEES_1_STATUS ='PAID' ,FEES_2_STATUS = 'PENDING'"

    elif data['FEES_2_DUE_DATE']<= datetime.date.today() and data['FEES_2_STATUS']=='PENDING':
        query += "FEES_2_STATUS ='PAID' ,FEES_3_STATUS = 'PENDING'"

    elif data['FEES_3_DUE_DATE']<= datetime.date.today() and data['FEES_3_STATUS']=='PENDING':
        query += "FEES_3_STATUS ='PAID' ,FEES_4_STATUS = 'PENDING'"
        
    elif data['FEES_4_DUE_DATE']<= datetime.date.today() and data['FEES_4_STATUS']=='PENDING':
        query += "FEES_4_STATUS ='PAID' ,FEES_5_STATUS = 'PENDING'"
        
    elif data['FEES_5_DUE_DATE']<= datetime.date.today() and data['FEES_5_STATUS']=='PENDING':
        query += "FEES_5_STATUS ='PAID' ,FEES_6_STATUS = 'PENDING'"
        
    elif data['FEES_6_DUE_DATE']<= datetime.date.today() and data['FEES_6_STATUS']=='PENDING':
        query += "FEES_6_STATUS ='PAID'"
        
    query += " WHERE STUDENT_ID = '{0}';".format(studentId)

    print(query)
    updateQuery(query)
    return query

def getPaymentInfo(studentId):
    query = """SELECT  *  FROM STUDENT_FEES  WHERE STUDENT_ID = '{0}';""".format(studentId)
    result = (selectQuery(query))
    print("Dheerain")
    return result[0]
    


