import paramiko
import sys

#connects to pi
#sends command, returns prints data
#returns
#status = able to connect or not (not implemented exactly yet
#out = stdout
#error = stderror
def sendsshcommand(command):
        connected = False; #allow multiple attempts to login

        while(not connected):
                nbytes = 4096
                hostname = input('Enter hostname or IP: ') #hostname will be set
                port = 22
                username = input('Enter username: ') #this should default to pi/no login
                password = input('Enter password: ')

                try:
                        #connect to client
                        client = paramiko.Transport((hostname, port))
                        client.connect(username=username, password=password)
                except paramiko.ssh_exception.AuthenticationException:
                        print("Unable to connect, wrong username or password")
                        #return -1
                except paramiko.ssh_exception.SSHException:
                        print("Invalid address")
                        #return -2


        #set client session up
        stdout_data = []
        stderr_data = []
        session = client.open_channel(kind='session')
        session.exec_command(command)

        while True:
                if session.recv_ready():
                    stdout_data.append(session.recv(nbytes))
                if session.recv_stderr_ready():
                    stderr_data.append(session.recv_stderr(nbytes))
                if session.exit_status_ready():
                    break

        print ('exit status: ', session.recv_exit_status())

        dataout = ''.join(stdout_data)
        dataerr = ''.join(stderr_data)
        print (''.join(stdout_data))
        print (''.join(stderr_data))

        session.close()
        client.close()
        return (1, dataout, dataerr)

