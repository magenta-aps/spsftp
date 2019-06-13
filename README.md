# spsftp

An sftp-client for danish sftp.serviceplatformen.dk, using trigger- and metadata files as a means of routing things around to other users

This library has only taken the term called 'simple transfer' into account.

This is paragraph 3.1 in this document [Vejledning til Serviceplatformens SFTP Service.pdf](https://share-komm.kombit.dk/P133/Ibrugtagning%20og%20test/Delte%20dokumenter/Vejledning%20til%20Serviceplatformens%20SFTP%20Service.pdf)

Create an instance of SpSftp and connect to the service

    spsftp = SpSftp({
        "user": "int",
        "host": "sftp-287",
        "ssh_key_path": "/home/int/.ssh/id_rsa",
        "ssh_key_passphrase": "",
    })
    sftp.connect()

See what is currently in the outgoing folder on the server

    print(sftp.listdir("OUT"))

Write a string 'hello-there' to a file named 'hellofile' in the OUT-folder on the server and ask for it to be transferred to the user 'kong-christian's IN-folder

    f1 = io.BytesIO("hello-there".encode("utf-8"))
    sftp.send(f1, "hellofile", "kong-christian")

See what is currently in the incoming folder on the server

    print(sftp.listdir("IN"))

Receive a file called 'hellofile' from user 'kong-kristian' and verify that it was actually sent from 'kong-kristian' and that I was indeed among the designated recipients

    f2 = io.BytesIO()
    sftp.recv("hellofile", f2,  "kong-kristian")


Getting receipts for the sent files is a manual procedure, just use the internal sftp\_client object.

    f3 = io.BytesIO()
    spsftp.sftp_client.getfo('hellofile.sftpreceipt', f3)


Disconnect from the service

    sftp.disconnect()
