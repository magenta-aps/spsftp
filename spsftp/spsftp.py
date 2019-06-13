#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import paramiko
import logging
import xmltodict
import hashlib
import os
import io

logger = logging.getLogger("spsftp")

triggerfile="""\
<ns2:Trigger xmlns:ns2="http://serviceplatformen.dk/xml/wsdl/soap11/SFTP/1/types">
<FileDescriptor>
<FileName>%(filename)s</FileName>
<SizeInBytes>%(filesize)s</SizeInBytes>
<Sender>%(sender)s</Sender>
<SendersFileId>%(fileid)s</SendersFileId>
<Recipients>%(recipient)s</Recipients>
</FileDescriptor>
<FileContentDescriptor>
</FileContentDescriptor>
</ns2:Trigger>"""

class SpSftp(object):
    """ upload and fetch from serviceplatformen
        providing trigger and using metadata-files
    """

    def __init__(self, settings={}):
        """Constructor.
        :param settings: user, host, port, ssh_key, ssh_key_passphrase
        :type settings: dict
        :return: void
        :rtype: None"""

        self.username = settings.get('user')
        self.host = settings.get('host', 'sftp.serviceplatformen.dk')
        self.port = int(settings.get('port', 22))


        self.key = self.get_key(
            filename=settings.get('ssh_key_path'),
            password=settings.get('ssh_key_passphrase')
        )

        self.transport = self.get_transport()


    def get_key(self):
        return paramiko.RSAKey.from_private_key_file(filename, password)

    def get_transport(self):
        self.transport = paramiko.Transport((self.host, self.port))

    def connect(self):
        """Opens connection to sftp server.
        :return: void
        :rtype: None"""

        self.transport.connect(username=self.username, pkey=self.key)
        self.sftp_client = paramiko.SFTPClient.from_transport(self.transport)

    def disconnect(self):
        """Closes connection to sftp server.
        :return: void
        :rtype: None"""

        self.sftp_client.close()
        self.transport.close()
        self.sftp_client = None

    def listdir(self, directory):
        """ list all the remote files in chosen directory
        """
        return self.sftp_client.listdir(directory)

    def send(self, fl, filename, recipient):
        """ upload both file and triggerfile
        to serviceplatformen OUT folder
        """
        remotepath = "OUT/" + filename
        sender = self.username
        fileid = hashlib.sha1(remotepath.encode("utf-8")).hexdigest()
        filesize = self.sftp_client.putfo(fl, remotepath).st_size
        self.sftp_client.putfo(
            io.StringIO(triggerfile % locals()),
            remotepath + ".trigger"
        )

    def recv(self, filename, fl, sender):
        """ download both file and metadatafile
        from serviceplatformen IN folder
        """
        remotepath = "IN/" + filename
        metafl = io.BytesIO()
        self.sftp_client.getfo(
            remotepath + ".metadata",
            metafl,
        )
        errors = []
        metadata = xmltodict.parse(metafl.getvalue())["ns2:Trigger"]
        xferid = metadata["FileTransferUUID"]
        filedescriptor = metadata["FileDescriptor"]
        if sender != filedescriptor["Sender"]:
            errors.append(
                "Sender %s not acknowledged as %s"
                % (filedescriptor["Sender"], sender)
            )
        if self.username not in filedescriptor["Recipients"]:
            errors.append(
                "%s not in Recipients: %s"
                % (self.username, filedescriptor["Recipients"])
            )

        if errors:
            logger.warning(
                "ignoring file %s because of errors in %s: %r "
                % (filename, filename+".metadata", errors)
            )
        else:
            self.sftp_client.getfo(remotepath, fl)
            logger.info("succesfully fetched and validated %s" % filename)

if __name__ == '__main__':
    sftp = SpSftp({
        "user": "clint",
        "host": "cprsftp-28787",
        "ssh_key_path": "/home/clint/.ssh/id_rsa",
        "ssh_key_passphrase": "",
    })

    logging.basicConfig(
        format='%(levelname)s %(asctime)s %(name)s %(message)s',
        level=logging.DEBUG
    )


    logging.root.setLevel(logging.DEBUG)
    sftp.connect()
    print(sftp.listdir("IN"))
    f1 = io.BytesIO("hello-there".encode("utf-8"))
    sftp.send(f1, "hellofile", "kong-christian")
    print(sftp.listdir("OUT"))
    f2 = io.BytesIO()
    sftp.recv("hellofile", f2,  "kong-kristian")
    sftp.disconnect()
