import sys
from socket import*

def recvAll(sock, numBytes):
    recvBuff = ''
    tmpBuff = ''
    while len(recvBuff) < numBytes:
        tmpBuff = sock.recv(numBytes).decode()
        if not tmpBuff:
            break
        recvBuff += tmpBuff
    return recvBuff

def addFile(data, fileName):
    if '.txt' not in fileName:
        fileName += '.txt'
    fileObject = open(fileName, 'w+')
    fileObject.write(data)
    fileObject.close()

def getFile(fileName, serverName, portName):
    print('ftp> Initiating connection to data channel...')
    dataSocket = socket(AF_INET, SOCK_STREAM)
    dataSocket.bind(('', 0))
    dataSocket.connect((serverName, portName))
    print('ftp> connected to server')
    print('ftp> Downloading file...')
    fileData = ''
    recvBuff = ''
    fileSize = 0
    fileSizeBuff = recvAll(dataSocket, 10)
    if int(fileSizeBuff) != 0:
        fileSize = int(fileSizeBuff)
        while len(fileData) != fileSize:
            recvBuff = recvAll(dataSocket, fileSize)
            if not recvBuff:
                break
            fileData += recvBuff
        addFile(fileData, fileName)
        print('ftp> Finished Downloading')
        print('ftp> ' + fileName)
        print('ftp> Number of bytes transferred: ' + str(len(fileData)))
    else:
        print('ftp> File does not exist')
    dataSocket.close()
    print('ftp> Connection closed')

    pass

def putFile(fileName, serverName, portName):
    # create data channel connection
    print('ftp> Initiating data channel...')
    dataSocket = socket(AF_INET, SOCK_STREAM)
    dataSocket.bind(('', 0))
    dataSocket.connect((serverName,portName))
    print('ftp> Connected to server')
    # read contents from file
    if '.txt' not in fileName:
        fileName += '.txt'
    fileObject = open(fileName, 'r')
    fileData = fileObject.read()
    # 10 bytes for the file size
    if fileObject:
        dataSizeStr = str(len(fileData))
        while len(dataSizeStr) < 10:
            dataSizeStr = "0" + dataSizeStr
        fileData = dataSizeStr + fileData
        numByteSent = 0
        while len(fileData) > numByteSent:
            numByteSent += dataSocket.send(fileData[numByteSent:].encode())
    print('ftp> ' + fileName)
    print('ftp> Number of bytes transferred: ' + str(numByteSent))
    fileObject.close()
    dataSocket.close()
    print('ftp> Connection closed')
    pass

def lsFiles(serverName, portName):
    print('ftp> Initiating data channel...')
    dataSocket = socket(AF_INET, SOCK_STREAM)
    dataSocket.bind(('', 0))
    dataSocket.connect((serverName, portName))
    print('ftp> Connected to server')
    fileSize = 0
    fileData = ''
    # get the first 10 bytes for the size of the file
    fileSizeBuff = recvAll(dataSocket, 10)
    if int(fileSizeBuff) != 0:
        fileSize = int(fileSizeBuff)
        while len(fileData) != fileSize:
            recvBuff = recvAll(dataSocket, fileSize)
            if not recvBuff:
                break
            fileData += recvBuff
        print('ftp> File contents: \n')
        print(fileData)
        print('ftp> Number of bytes transferred: ' + str(len(fileData)))
    else:
        print('ftp> No files on server')
        print('ftp> Number of bytes transferred: ' + '0')
    dataSocket.close()
    print('ftp> Connection closed')
    pass

if len(sys.argv) > 1:
    serverName = sys.argv[1]
    serverPort = int(sys.argv[2])
else:
    serverName = socket.gethostname()
    serverPort = 1234

controlSocket = socket(AF_INET, SOCK_STREAM)
controlSocket.bind(('', 0))
controlSocket.connect((serverName, serverPort))

while 1:
    data = input('ftp> ')
    request = data.split(' ')
    try:
        controlSocket.send(data.encode())
        print('ftp> Data sent')
    except IOError:
        print('ftp> NOT SENT')

    try:
        print('ftp> Awaiting response')
        response = controlSocket.recv(7).decode()
    except IOError:
        print('ftp> NO RESPONSE')

    if response == 'SUCCESS':
        print('ftp> ' + response)
        if request[0] == 'get':
            getFile(request[1], serverName, serverPort)
            pass
        elif request[0] == 'put':
            putFile(request[1], serverName, serverPort)
            pass
        elif request[0] == 'ls':
            lsFiles(serverName, serverPort)
            pass
        elif request[0] == 'quit' or request[0] == 'q':
            endSession = controlSocket.recv(7).decode()
            print('ftp> ' + endSession)
            print('ftp> Quitting Session')
            break


    elif response == 'FAILURE':
        print('ftp> ' + response)
        print('ftp> Try Again')

controlSocket.close()
print('ftp> Socket closed')
