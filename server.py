import mysql.connector
import socket
from multiprocessing import Process
import threading
import pickle

class data:
    def __init__(self,type = None,group=None,message = None,name = None):
        self.type = type
        self.group = group
        self.message = message
        self.name = name
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "127.0.0.3"
port = 5000
addr = (host,port)

try:
    s.bind(addr)
except socket.error as error:
    print(error)


db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="rootsql",
    database="chat"
)
client = []
cursor = db.cursor()
Generate = False

def threaded_client(conn,addr,cursor,client):
    connected = True
    while connected:
        try:
            client_data = pickle.loads(conn.recv(6000))
            data_received = True
        except EOFError:
            data_received = False
        if data_received == True:
            if client_data.type == "login":
                temp = login(client_data.group,cursor)
                if temp == True:
                    login_data = data("login",message = True,name=client_data.name,group=client_data.group)
                    conn.send(pickle.dumps(login_data))
                    print(client_data.name+" joined")
                    break
                else:
                    login_data = data("login",message = False)
                    conn.send(pickle.dumps(login_data))
            
            elif client_data.type == "generate":
                temp = generate(client_data.group,cursor)
                if temp == True:
                    generate_data = data("generate",message = True,group=client_data.group)
                    conn.send(pickle.dumps(generate_data))
                    break
                else:
                    generate_data = data("generate",message = False)
                    conn.send(pickle.dumps(generate_data))
            
    while True:
        try:
            client_received = pickle.loads(conn.recv(6000))
            if client_received and client_received.type == "chat":
                print(client_received.name+": "+client_received.message)
                client_send = data(type="chat",group=client_received.group,message=client_received.message,name=client_received.name)
                add_process = Process(target=add,args=(client_received.group,client_received.name,client_received.message,cursor))
                add_process.start()
                broadcast(client_send,conn)
            else:
                remove(conn)
        except:
            continue

def login(group,cursor):
    cursor.execute("SHOW TABLES LIKE '%"+group+"%'")
    temp = cursor.fetchall()
    tables=[]
    for i in range(0,len(temp)):
        tables.append(temp[i][0])
    if group in tables:
        return True
    else:
        return False

def generate(group,cursor):
    temp = login(group,cursor)
    global Generate
    if temp == False:
        cursor.execute("CREATE TABLE "+group+" (NAME VARCHAR(50),MESSAGE VARCHAR(200))")
        db.commit()
        return True
    else:
        return False

def add(group,name,message,cursor):
    name = '"'+name+'"'
    message = '"'+message+'"'
    cursor.execute("INSERT INTO "+group+" (NAME,MESSAGE) VALUES ("+name+","+message+")")
    db.commit()
    return 0 

def broadcast(message,connection):
    for c in client:
        if c != connection:
            try:
                c.send(pickle.dumps(message))
            except:
                c.close()
                remove(c)

def remove(c):
    if c in client:
        client.remove(c)

def start():
    s.listen()
    print("Server listning",host)
    while True:
        conn,addr = s.accept()
        client.append(conn)
        thread = threading.Thread(target=threaded_client,args=(conn,addr,cursor,client))
        thread.start()

start()