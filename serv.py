import sys
from socket import*
import time

def addFile(fileName):
    isInFile = False
    try:
        fileObject = open('allFiles.txt', 'r')
        fileData = fileObject.read()
        if fileName in fileData:
            isInFile = True
        fileObject.close()
    except IOError:
        print('> Creating allFiles.txt')
    if not isInFile:
        fileObject2 = open('allFiles.txt', 'a+')
        newName = fileName.replace('.txt', '')
        fileObject2.write(newName)
        fileObject2.write('\n')
        fileObject2.close()
    else:
        print('> Duplicate file name: ' + fileName)


def recvAll(sock, numBytes):
    recvBuff = ''
    tmpBuff = ''
    while len(recvBuff) < numBytes:
        tmpBuff = sock.recv(numBytes).decode()
        if not tmpBuff:
            break
        recvBuff += tmpBuff
    return recvBuff

def getRequest(serverSock, fileName):
    print('> Starting connection...')
    dataSocket, addr = serverSock.accept()
    print('> Data Connection accepted...')
    # check to see if the file exists first
    if '.txt' not in fileName:
        fileName += '.txt'
    try:
        fileObject = open(fileName, 'r')
        fileData = fileObject.read()
        dataSizeStr = str(len(fileData))
        if fileObject:
            while len(dataSizeStr) < 10:
                dataSizeStr = "0" + dataSizeStr
            fileData = dataSizeStr + fileData
            numByteSent = 0
            while len(fileData) > numByteSent:
                numByteSent += dataSocket.send(fileData[numByteSent:].encode())
            print('> Data sent')
            fileObject.close()
    except IOError:
        print('> No File')
        dataSocket.send('0000000000'.encode())

    dataSocket.close()
    print('> Data connection closed')
    pass

def putRequest(serverSock, fileName):
    dataSocket, addr = serverSock.accept()
    print('> Data Connection accepted')
    # receive data from the client
    fileData = ''
    recvBuff = ''
    fileSize = 0
    fileSizeBuff = ''
    fileSizeBuff = recvAll(dataSocket, 10)
    fileSize = int(fileSizeBuff)
    while len(fileData) != fileSize:
        recvBuff = recvAll(dataSocket, fileSize)
        if not recvBuff:
            break

        fileData += recvBuff
    # now write the contents to a fileData
    addFile(fileName)
    if '.txt' not in fileName:
        fileName += '.txt'

    fileObject = open(fileName, 'w+')
    fileObject.write(fileData)
    fileObject.close()
    dataSocket.close()
    print('> Data connection closed')
    pass

def lsFiles(serverSock):
    dataSocket, addr = serverSock.accept()
    print('> Data connection accepted')
    try:
        fileObject = open('allFiles.txt', 'r')
        fileData = fileObject.read()
        dataSizeStr = str(len(fileData))
        while len(dataSizeStr) < 10:
            dataSizeStr = '0' + dataSizeStr
        fileData = dataSizeStr + fileData
        numByteSent = 0
        while len(fileData) > numByteSent:
            numByteSent += dataSocket.send(fileData[numByteSent:].encode())
        fileObject.close()
    except IOError:
        # no file, send back size 0
        print('> No file')
        dataSocket.send('0000000000'.encode())

    dataSocket.close()
    print('> Data connection closed')
    pass


# FTP Server code
if len(sys.argv) > 1:
    portNumber = int(sys.argv[1])
else:
    portNumber = 1234 # default port number is 1234

# Create the TCP socket
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', portNumber))

# Start listening for incoming connections
serverSocket.listen(5)

print('> Server ready to receive')

# run forever
while 1:
    # control connection that runs for the duration of the FTP session
    print('> Waiting for connections')
    controlSocket, addr = serverSocket.accept()
    print('> Control Connection accepted')

    response = ''
    while 1:
        response = 'FAILURE'
        request = controlSocket.recv(40).decode().split(" ")
        if request[0] == 'get':
            try:
                response = 'SUCCESS'
                print('> ' + response)
                controlSocket.send(response.encode())
                getRequest(serverSocket, request[1])
            except IOError:
                print('> error')
                break
        elif request[0] == 'put':
            try:
                response = 'SUCCESS'
                print('> ' + response)
                controlSocket.send(response.encode())
                putRequest(serverSocket, request[1])
            except IOError:
                print('> error')
                break
            pass
        elif request[0] == 'ls':
            try:
                response = 'SUCCESS'
                print('> ' + response)
                controlSocket.send(response.encode())
                lsFiles(serverSocket)
            except IOError:
                print('> error')
                break
            pass
        elif request[0] == 'quit' or request[0] == 'q':
            response = 'SUCCESS'
            print('> ' + response)
            controlSocket.send(response.encode())
            break
        else:
            # send failure back to the client
            print('> Invalid syntax')
            print('> ' + response)
            controlSocket.send(response.encode())
    controlSocket.send('GOODBYE'.encode())
    controlSocket.close()
    print('> Ftp session closed...')

serverSocket.close()
print('> Server stopped')
