import flask
import sqlite3

app = flask.Flask(__name__)

def get_db():  #function to connect to database
    db = sqlite3.connect("JPSalon.db")
    db.row_factory = sqlite3.Row
    return db
    
@app.route('/')
def home():
    return flask.render_template("index.html")


#-----------------------addMember--------------------------------   
@app.route('/addMember')
def addMember():
    return flask.render_template("addMember.html")

@app.route('/memberAdded', methods = ['POST'])
def memberAdded():
    name = flask.request.form['name']   #retrieving user input 
    gender = flask.request.form['gender']
    email = flask.request.form['email']
    contact_no = flask.request.form['contact_no']
    address = flask.request.form['address']

    #validation
    error1 = False
    nameError = ""
    if len(name.strip()) == 0:
        nameError = "Please input your name again"  #error message
        error1 = True
        print(error1)
    else:
        for i in name:
            if i.isalpha() or i == ' ':
                pass
            else:
                nameError = "Please input your name again"
                error1 = True
                print(i)
                print(i.isalpha())
                print(error1)
                break
    
    error2 = False
    emailError = ''
    if len(email.strip()) == 0:
        error2 = True
        emailError = 'Please input an email'

    error3 = False
    contactError = ''
    if contact_no.isdigit() == False:
        contactError = "Please input your contact number again"
        error3 = True
    
    error4 = False
    addError = ""
    if len(address.strip()) == 0:
        addError = "Please input your address"
        error4 = True
    

    
    if (error1 or error2 or error3 or error4) == True:  #checking if there is input error
        #sending error message to html
        return flask.render_template('addMember.html', nameError = nameError, emailError = emailError, contactError = contactError, addError = addError)
    else:
        db = get_db()       #connect to db to add new member into db
        cursor = db.execute("SELECT seq FROM sqlite_sequence WHERE name = 'MEMBER'")
        results = cursor.fetchall()
        mID = int(results[0][0]) + 1
        db.execute("INSERT INTO MEMBER VALUES(?, ?, ?, ?, ?, ?);", (mID, name, gender, email, contact_no, address))
        db.commit()
        db.close()

        return flask.render_template('memberAdded.html')


 #-------------------updateMember--------------------------------   
@app.route('/updateMember')
def updateMember():
    return flask.render_template('updateMember.html')

@app.route('/memberUpdated', methods = ['POST'])
def memberUpdated():
    email = flask.request.form['new_email']     #retrieving user input
    mobileNo = flask.request.form['new_mobileNo']
    mID = flask.request.form['ID']

    #validation
    error1 = False
    emailError = ''
    if len(email.strip()) == 0:
        error1 = True
        emailError = 'Please input an email'    #error message 

    error2 = False
    mobileError = ''
    if not mobileNo.isdigit():
        error2 = True
        mobileError = 'Please input your number again'

    error3 = False
    idError = ''
    if mID.isdigit() == False:
        error3  = True
        idError = 'Please input a valid ID'
    else:
        db = get_db()   #connect to db to check if id exists
        cursor = db.execute("SELECT * FROM MEMBER WHERE memberID = ?", (mID,))
        results = cursor.fetchall()
        if results == []:
            error2 = True
            idError = 'Please input a valid ID'

    

    
    if (error1 or error2 or error3) == True:    #check if user input is invalid
        #sending error message to html
        return flask.render_template('updateMember.html',emailError = emailError, mobileError = mobileError, idError = idError)
    else:   #update member's data
        db.execute("UPDATE MEMBER SET email = ?  WHERE memberID = ?", (email, mID)) 
        db.commit()
        db.execute("UPDATE MEMBER SET contactNo = ? WHERE memberID = ?", (mobileNo, mID))
        db.commit()
        db.close()

        return flask.render_template('memberUpdated.html')



#------------------------invoice-----------------------------------   
@app.route('/invoice')
def invoice():
    db = get_db()   #connect to db to get name of service for html page
    cursor = db.execute('SELECT service FROM SERVICE')
    service = cursor.fetchall()
    db.close()
    return flask.render_template('invoice.html', service = service)

@app.route('/invoiceAdded', methods = ['POST'])
def invoiceAdded():
    name = flask.request.form['name']   #retrieving user input
    mID = flask.request.form['memberID']
    date = flask.request.form['date']
    s1 = flask.request.form['service1']
    s2 = flask.request.form['service2']
    s3 = flask.request.form['service3']
    s4 = flask.request.form['service4']
    s5 = flask.request.form['service5']
    services = [s1, s2, s3, s4, s5]     #putting all services into 1 list for easy traversal
    

    #validaion
    error1 = False
    nameError = ""
    if len(name.strip()) == 0:
        nameError = "Please input your name again"  #error message
        error1 = True
    else:
        for i in name:
            if not i.isalpha() or i == ' ':
                nameError = "Please input your name again"
                error1 = True
                break
       
    error2 = False
    idError = ''
    if mID.isdigit() == False:
        error2 = True
        idError = 'Please input a valid ID'
    else:
        db = get_db()   #connect to db to check if id exists
        cursor = db.execute("SELECT * FROM MEMBER WHERE memberID = ?", (mID,))
        results = cursor.fetchall()
        if results == []:
            error2  = True
            idError = 'Please input a valid ID'

    error3 = False
    serviceError = ''
    for i in services:
        if i != 'None':
            break
        else:
            error3 = True
            serviceError = 'Please input at least 1 choice'
    


    if (error1 or error2 or error3) == True:    #checking if user input is invalid
        #sending error message to html
        return flask.render_template('invoice.html', nameError = nameError, idError = idError, serviceError = serviceError)


    #creating new invoiceNo
    cursor = db.execute("SELECT seq FROM sqlite_sequence WHERE name = 'INVOICE'")     
    results = cursor.fetchall()
    invoiceNo = int(results[0][0]) + 1   

    #finding total costs
    total = 0
    
    
    for i in services:
        if i != 'None':
            cursor = db.execute("SELECT price FROM SERVICE WHERE service = ?", (i,))
            results = cursor.fetchall()
            total += results[0][0]
            db.execute("INSERT INTO CUSTSERVICE VALUES(?, ?);", (invoiceNo, i))
    
    if mID == '0':
        discount_price = total
    else:
        discount_price = total * 0.9
    discount_price = round(discount_price, 2)

    #inserting invoice into table
    db.execute("INSERT INTO INVOICE VALUES(?, ?, ?, ?, ?)", (invoiceNo, name, int(mID), date, discount_price))
    db.commit()
    db.close()

    return flask.render_template('invoiceAdded.html', total = total, discount_price = discount_price)



#-----------------------dailyTransactions---------------------------   
@app.route('/dailyTransactions')
def dailyTransactions():
    return flask.render_template('DailyTransactions.html')

@app.route('/viewDailyTransactions', methods = ['POST'])
def viewDailyTransactions():
    date = flask.request.form['date']   #retrieving user input
   
    #validation
    error1 = False
    dateError = ''
    if date == '':
        error1 = True
        dateError = 'Please input a date'   #error message

    if error1 == True:  #check if user input is invalid 
        #sending error message to html
        return flask.render_template('dailyTransaction.html', dateError = dateError) 
    else:   #retrieving data from db to display in html
        print(date)
        db = get_db()
        cursor = db.execute('''SELECT INVOICE.invoiceNo, INVOICE.name, INVOICE.memberID, INVOICE.dateOfTr,
        CUSTSERVICE.service, INVOICE.price FROM INVOICE, CUSTSERVICE 
        WHERE INVOICE.invoiceNo = CUSTSERVICE.invoiceNo AND INVOICE.dateOfTr = ?''', (date,))
        rows = cursor.fetchall()
        print(rows)
        db.close()


    return flask.render_template('viewDailyTransactions.html', rows = rows)


#------------------------monthlySales---------------------------------   
@app.route('/monthlySales')
def monthlySales():
    return flask.render_template('monthlySales.html')

@app.route('/viewMonthlySales', methods = ['POST'])
def viewMonthlySales():
    month = flask.request.form['month'] #retrieving user input
    year = flask.request.form['year']
    
    #reformat the month so that use 'date >' and 'date <' in DB browser
    date1 = year + '-' + month + '-' + '01' 
    date2 = year + '-' + month + '-' + '31'
    print(date1, date2)

    db = get_db()   #retrieving all sales from the particular month
    cursor = db.execute("""SELECT price FROM INVOICE 
    WHERE dateOfTr >= ? AND  dateOfTr <= ?""", (date1, date2))
    results = cursor.fetchall()
    print(results)

    #adding all sales to find total revenue
    total = 0
    for i in results:
        total += i[0]

    db.close()

    return flask.render_template('viewMonthlySales.html', total = total)



#---------------------memberTransactions--------------------------------   
@app.route('/memberTransactions')
def memberTransactions():
    return flask.render_template('memberTransactions.html')

@app.route('/viewMemberTransactions', methods = ['POST'])
def viewMemberTransactions():
    mID = flask.request.form['memberID']    #retrieving user input

    #validation
    error1 = False
    idError = ''
    if mID.isdigit() == False:
        error1 = True
        idError = 'Please input a valid ID'
    else:
        db = get_db()   #id verification
        cursor = db.execute("SELECT * FROM MEMBER WHERE memberID = ?", (mID,))
        results = cursor.fetchall()
        if results == []:
            error1  = True
            idError = 'Please input a valid ID'

    if error1 == True:  
        return flask.render_template('memberTransactions.html', idError = idError)

    db = get_db()   #retrieving data from db to display in html
    cursor = db.execute("""SELECT INVOICE.invoiceNo, INVOICE.name, INVOICE.memberID, INVOICE.dateOfTr,
    CUSTSERVICE.service, INVOICE.price FROM INVOICE, CUSTSERVICE 
    WHERE INVOICE.invoiceNo = CUSTSERVICE.invoiceNo AND INVOICE.memberID = ?
    """, (int(mID),))
    rows = cursor.fetchall()

    return flask.render_template('viewMemberTransactions.html', rows = rows)
  

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
