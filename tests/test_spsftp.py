import unittest
from spsftp.spsftp import SpSftp
import io
import collections

xmlfile="""
<ns2:Trigger xmlns:ns2="http://serviceplatformen.dk/xml/wsdl/soap11/SFTP/1/types">
<FileTransferUUID>42</FileTransferUUID>
<FileDescriptor>
<FileName>hellofile</FileName>
<SizeInBytes>11</SizeInBytes>
<Sender>kong-christian</Sender>
<Recipients>x</Recipients>
</FileDescriptor>
</ns2:Trigger>
"""
hellofile = "hello there"

class SftpMock:

    st_size = 42

    def getfo(self, remotepath, fl):
        if remotepath == "IN/hellofile.metadata":
            fl.write(xmlfile.encode("utf-8"))
        else:
            fl.write(hellofile.encode("utf-8"))
        return self

    def putfo(self, fl, remotepath):
        if remotepath == "OUT/hellofile.trigger":
            self.triggerfile = fl
        return self

class SpSftpMock(SpSftp):

    get_key = lambda self, filename, password: "Key"
    get_transport = lambda self: "Transport"
    sftp_client=SftpMock()
    def connect(self):pass
    def disconnect(self): pass

class Tests(unittest.TestCase):

    def setUp(self):
        self.spsftp = SpSftpMock({
            "user": "x",
            "host": "y",
            "ssh_key_path": "",
            "ssh_key_passphrase": "",
        })

    def test_creates_key_and_transport(self):
        self.assertEqual(self.spsftp.key, "Key")
        self.assertEqual(self.spsftp.transport, "Transport")

    def test_recv_wrong_recipient(self):
        fl = io.BytesIO()
        self.spsftp.username="A"
        self.spsftp.recv("hellofile", fl,  "kong-christian")
        self.assertEqual("", fl.getvalue().decode("utf-8"))

    def test_recv_unknown_sender(self):
        fl = io.BytesIO()
        self.spsftp.recv("hellofile", fl,  "kong-kristian")
        self.assertEqual("", fl.getvalue().decode("utf-8"))

    def test_recv_good(self):
        fl = io.BytesIO()
        self.spsftp.recv("hellofile", fl,  "kong-christian")
        self.assertEqual(hellofile, fl.getvalue().decode("utf-8"))

    def test_send(self):
        fl = io.BytesIO("hello-there".encode("utf-8"))
        self.spsftp.send(fl, "hellofile", "kong-christian")
