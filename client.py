import socket
import pickle
import select
import sys

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
    s.connect(addr)
except socket.error as error:
    print(error)
login = False
while True:
    print("What do you want to do - \n1. Login\n2. Generate\n3. Chat\n")
    n = int(input("Enter Your Choice : "))
    if n == 1:
            Name = input("Enter Your Name : ")
            Group = input("Enter Group Id : ")
            login_data = data(type="login",group=Group,name=Name)
            s.send(pickle.dumps(login_data))
            temp = pickle.loads(s.recv(6000))
            if temp.type == "login" and temp.message==True:
                print("Login successful Connected to "+Group+"\n")
                login = True
            else:
                print("Group Not Present\n")
    if n ==2:
            Group = input("Enter Group Id : ")
            generate_data=data(type="generate",group=Group)
            s.send(pickle.dumps(generate_data))
            temp = pickle.loads(s.recv(6000))
            if temp.type == "generate" and temp.message==True:
                print("Group Generated (Launch app to Login)\n")
                sys.exit()
            else:
                print("Failed to generate group ( Group already Exist )\n")
    
    if n == 3:
        if login == True:
            print("Welcome to Chat Room (Don't use Symbols)")
            break
        else:
            print("You must be logged in to start chat")
while True: 

    sockets_list = [sys.stdin, s] 
    read_sockets,write_socket, error_socket = select.select(sockets_list,[],[]) 
  
    for socks in read_sockets: 
        if socks == s: 
            server_message = pickle.loads(socks.recv(6000)) 
            print(server_message.name+": "+server_message.message)
        else: 
            message = input() 
            s.send(pickle.dumps(data(type="chat",group=Group,message=message,name=Name))) 
            sys.stdout.flush() 
s.close()