1 Group Member:
Varun Rai
raiv95@csu.fullerton.edu
891675381

Programming Language: Python

To execute the serv.py simply type python serv.py [port number]. With the port number
being whatever non reserved port number you wish to designate. To execute cli.py, type 
python cli.py [server machine] [server port].

This FTP client/server was written and tested on Windows (cmd), not Linux.

FTP Protocol Design

What kinds of messages exchanged over control channel?

The client will send commands over the control channel, the commands consist of:

get Filename
put Filename
ls 
quit

If the client sends over anything other than the four commands listed above, an error message will be printed to the client console telling the client to try sending the command again. Once the message has been sent over the control channel, the client waits for a response from the server.

The server receives the entire response in 24 bytes. Up to four bytes for the command itself and then 20 bytes for the file name if specified. The server receives the command as a string and then checks to see which command was sent. If the server doesn’t recognize the command then it sends back FAILURE to the client. If the server recognizes the command it sends back SUCCESS to the client. Once the client receives the response this will initiate the data transfer from server to client and vice versa. If there is a FAILURE message delivered to the client, then the client is prompted to try entering the command again.

The client, which is awaiting a response from the server, is looking to receive 7 bytes from the server. 7 bytes because success and failure are both 7 bytes. 

This entire exchange takes place on the “control” connection. Once the client receives the success message from the server, it proceeds to initialize the “data” connection on the first available port. After that, the client created data channel waits to accept a connection from the server. 

How will the receiving side know when to start/stop receiving the file?

If the command was get or ls, the client waits to receive content from the server. If the command was put, the server waits to receive the data content from the client. The file size in bytes is appended as the first 10 bytes to the file data. This applies for get, put, and ls.

Note: When there is a put operation, the server will open a file called allFiles.txt   that contains a list of all files that have been placed on the server. This file is also used for the ls command to retrieve the file name of every file located on the server.

If there is a quit message sent to the server, then the server sends back a ‘GOODBYE’ message to the client and terminates the client socket connection. The client waits for the server to acknowledge the quit message before quitting the FTP session.
Note: This FTP client/server only supports one client connecting at a time. The server can’t handle two clients at the same time.

What does each command do?

If the user types in quit, then the server will send a ‘GOODBYE’ to the client. The client program terminates. The server program exits out of the nested inner while loop and then waits to accept a connection from a new client. The control connection is also closed in the inner while loop.

If the user types get, then the server will send SUCCESS to the client. The data channel is established. The server checks to make sure the file exists, if it doesn’t then it sends file size ‘0000000000’ to the client to notify that the file doesn’t exist on the server. If it does, then the server program proceeds to read the data from the file and then sends it to the client. Regardless of whether the file already exists on the client side, the client program opens up a file stream to write the data to the corresponding file requested in the get command.

If the user types ls, then the server sends the SUCCESS message to the client. The data channel is established. The server reads all files listed in the allFiles.txt and then sends the data over the channel. Once the client receives the data, the files are displayed by the client along with the number of bytes transferred. If there are no files on the server side, then the server sends the client the number of bytes as ‘0000000000’.

If the user types put, then the server sends the SUCCESS message to the client. The data channel is established. The client reads the content of the file and then sends it over the channel. Once the server receives the data, it creates the file and then writes the content to the newly created file. Client also displays the filename and number of bytes transferred.

Once the data transfer has completed for get, put, and ls, the data socket (data channel) is closed and the client and server both continue communicating on the control socket (control channel) until the client issues a quit command.
