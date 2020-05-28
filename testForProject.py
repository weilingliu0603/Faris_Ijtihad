import sqlite3
db = sqlite3.connect(r"C:\Users\Yazid\Desktop\Faris Computing\Project-JP Salon\My Project\JPSalon.db")

#services = 'Perm, Colour'
#total = 0

#service_provided = services.split(',')
#for i in service_provided:
    #i = i.strip()
    #cursor = db.execute("SELECT price FROM SERVICE WHERE service = ?", (i,))
    #results = cursor.fetchall()
    #total += results[0][0]
    #inserting cutomer's services into table

cursor = db.execute('SELECT service FROM SERVICE')
service = cursor.fetchall()
print(service, type(service))

for i in service:
    print(i[0], type(i[0]))


   
db.close()


