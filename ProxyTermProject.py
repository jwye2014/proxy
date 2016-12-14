import os
import sys
import thread
import socket
import string
import ssl
from urlparse import urlparse
import hashlib

backlog=100
max_data=99999
debug=True

def main():

	if (len(sys.argv)<2):
		print "No port given"
		port=8080

	else:
		port=int(sys.argv[1])



	host='127.0.0.1'


	print "Proxy server running on", host, ":", port

		#create a socket
	s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind((host,port))
	s.listen(backlog)

        change=input("Do you want 1. only proxy 2. data change proxy?")

        while 1:
                if(change==1):
                        before=""
                        after=""
                        break
                elif(change==2):
                        before=raw_input("From : ")
                        after=raw_input("To :")
                        break
                else:
                        print "Please check your choice"

        
        while 1:
                if(change==1):
                        try:
                                conn, client_addr=s.accept()
                                thread.start_new_thread(proxy,(conn, client_addr))
                        except socket.error as e:
                                print e
                                sys.stdout.flush()
                                
                elif(change==2):
                        try:
                                conn, client_addr=s.accept()
                                thread.start_new_thread(proxy_B,(conn, client_addr,before,after))
                        except socket.error as e:
                                print e
                                sys.stdout.flush()
                       
                        
	s.close()


#proxy thread func

def proxy(conn, client_addr):

        if not os.path.isdir("cachefile"):
                os.mkdir("cachefile")
        
       
        request=conn.recv(max_data)
               
        try:
                first_line=request.split('\n')[0]

	except:
                print "request error : ",request
                conn.close()
                sys.exit(1)
        try:
                url=first_line.split(' ')[1]
        except:
                conn.close()
                sys.exit(1)
                
        h_count=url.count("http")
        
        if(h_count<=1):
                if(h_count==0):
                        temp=url
                elif(h_count==1):
                        http=url.find("://")
                        temp=url[(http+3):]

		port_pos=temp.find(":")
	
		if(port_pos==-1 ):
			port=80
			server_pos=temp.find("/")
			if(server_pos==-1):
				server=temp
			else:
				server=temp[:server_pos]
		else:
			server_pos=temp.find("/")
			if(server_pos>port_pos):
				port=int(temp[(port_pos+1):server_pos])
			else:
				port=int(temp[port_pos+1:])
				server=temp[:server_pos]
        else:
                http=url.find("://")
                temp=url[http+3:]
                end=temp.find("/")
                server=temp[:end]

                port=80
                                        
        #create  a socket to connect to the web server
        check=0
 
        request.replace("gzip,","")


        # need check
        jpg=request.find(".jpg")
        png=request.find(".png")
        swf=request.find(".swf")
        avi=request.find(".avi")
        if(jpg!=-1 or png!=-1 or swf!=-1 or avi!=-1):
                print server
                check=1
                
        try:        
                ss=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                ss.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                
                if(check==1 and change==1):
                        s=hashlib.md5()
                        s.update(url)
                        name=s.hexdigest()
                        cachename=name+".cached"
                        if(os.path.isfile("cachefile/"+cachename)):
                                print "Cache Hit"
                                ff=open("cachefile/"+cachename,'r')
                                data=ff.read()
                                header="HTTP/1.1 200 OK\r\nContent-Length: "+str(len(data))
                                header+="\r\n"
                                data=header+data
                                conn.send(data)
                                conn.close()
                                sys.exit(1)
                        else:
                                print "Cache Miss"
                                ss.connect((server,port))
                                ss.send(request)
                              
                else:
                        ss.connect((server,port))
                        ss.send(request)

                while 1:
                        data=ss.recv(max_data)
                        if(len(data)>0):
                                conn.send(data)
                                if(check>0):
                                        cll=data.find("Content-Length:")
                                        first=data[cll+16:]
                                        clll=first.find("\r\n")
                                        second=first[:clll]
                                        try:
                                                final=int(second)
                                                if (final!=0):
                                                        cachedata=data.split("\r\n\r\n")[1]
                                                        cachedata=cachedata[:final]
                                                        print final
                                                        f=open("cachefile/"+cachename,'w')
                                                        f.write(cachedata)
                                        except:
                                                pass
                        else:
                                break
                       
                                
                ss.close()
                conn.close()
        except socket.error, (value, message):
                if ss:
                        ss.close()
                if conn:
                        conn.close()
                sys.exit(1)


def proxy_B(conn, client_addr,before,after):
        
	#get the reqeust from browser
        request=conn.recv(max_data)
        diff=len(after)-len(before)
        
        print request

        #parse the first line
        try:
                first_line=request.split('\n')[0]
        except:
                conn.close()
                sys.exit(1)
        try:
                url=first_line.split(' ')[1]
        except:
                conn.close()
                sys.exit(1)
                
        h_count=url.count("http")
        
        if(h_count<=1):
                if(h_count==0):
                        temp=url
                elif(h_count==1):
                        http=url.find("://")
                        temp=url[(http+3):]

		port_pos=temp.find(":")

		if(port_pos==-1 ):
			port=80
			server_pos=temp.find("/")
			if(server_pos==-1):
				server=temp
			else:
				server=temp[:server_pos]
		else:
			server_pos=temp.find("/")
			if(server_pos>port_pos):
				port=int(temp[(port_pos+1):server_pos])
			else:
				port=int(temp[port_pos+1:])
				server=temp[:server_pos]
        else:
                http=url.find("://")
                temp=url[http+3:]
                end=temp.find("/")
                server=temp[:end]

                port=80
                                        
        #create  a socket to connect to the web server

        print server, port

        try:
                ss=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                ss.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                ss.connect((server,port))
                gzip_pos=request.find("gzip")
                if(gzip_pos>-1):
                        request=request.replace("gzip","")
                else:
                        pass
                ss.send(request)
        
                while 1:
                 # receive data from web

                        data=ss.recv(max_data)
                        if(len(data)>0):
                                length_pos=data.find("Content-Length: ")
                                chunk_pos=data.find("chunk")
                                print length_pos
                                if(length_pos>-1 and data.find(before)):
                                        print "Length pos:",length_pos
                                        first=data[:(length_pos)+16]
                                        beforechange=data[(length_pos)+16:]
                                        newline_pos=beforechange.find("\r\n")
                                        print "newline pos:",newline_pos
                                        second=beforechange[(newline_pos):]
                                        integer_pos=beforechange[:(newline_pos)]
                                        length=int(integer_pos)
                                        print "int:",length
                                        beforechange=""
                                        length=length+diff
                                        length=str(length)
                                        beforechange=length
                                        afterdata=str(first)+str(beforechange)
                                        afterdata+=str(second)
                                        data=afterdata
                                        
                                elif(chunk_pos>-1 and data.find(before)):
                                        print "Chunk:", chunk_pos
                                        chunk_data=data.split("\r\n")
                                        number=len(chunk_data)
                                        for i in range (0, number):
                                                if(chunk_data[i].find(before)>-1):
                                                        count=chunk_data[i].count(before)
                                                        chunk_data[i-1]=int("0x"+str(chunk_data[i-1]),16)
                                                        chunk_data[i-1]+=(count*diff)
                                                        chunk_data[i-1]=hex(chunk_data[i-1])
                                                        chunk_data[i-1]=str(chunk_data[i-1])
                                                        chunk_data[i-1]=(chunk_data[i-1])[2:]
                                                        chunk_data[i].replace(before,after)
                                        data=""
                                        for j in range(0,number):
                                                data+=chunk_data[j]

                                                
                                data=data.replace(before,after)
                                conn.send(data)
                        else:
                                break
                ss.close()
                conn.close()
       
        
                        
        except socket.error, (value, message):
                if ss:
                        ss.close()
                if conn:
                        conn.close()
                sys.exit(1)
        


        
if __name__ == '__main__':
	main()

