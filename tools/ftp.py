import os
import socket
import traceback
from ftplib import FTP
from tools.config_loader import conf
from tools.logger import logger
from tools.set_single_instance import Singleton
from retry import retry

ip, username, password, port = conf("ftp.ip"), \
                               conf("ftp.username"), \
                               conf("ftp.password"), \
                               int(conf("ftp.port"))


class FTPHelper():

    def __init__(self, ip, username, password, port=21, buffer_size=1024, obj=None):
        self.ip = ip
        self.username = username
        self.password = password
        self.port = port
        self.buffer_size = buffer_size
        self.obj = obj

        ftp = FTP()
        ftp.set_pasv(True)
        socket.setdefaulttimeout(60)
        try:
            ftp.connect(self.ip, self.port)
            ftp.login(self.username, self.password)
        except Exception as e:
            logger.error(
                f"fail to login [{self.ip, self.port}] with user info [{self.username, self.password}],error as follows:{str(e)}")
        else:
            logger.info(f"success to connect ftp with info: {(self.ip, self.port, self.username)}")
            self.obj = ftp
            self.obj.set_debuglevel(0)

    def close(self):
        if self.obj:
            self.obj.quit()

    def create_dir(self, target_dir, remote_path="/home/volume/incoming"):
        try:
            remote_path = os.path.join(remote_path, target_dir)
            remote_path = remote_path.replace('\\', '/')
            self.obj.mkd(remote_path)
        except Exception:
            logger.warning(f'{remote_path} has already exist')
        else:
            logger.debug(f"success to create dir [{remote_path}]")
        finally:
            return remote_path

    def upload_folder(self, local_path='../', remote_path='/home/volume/incoming'):
        try:
            local_path = local_path.strip()
            local_path = local_path.rstrip('/')
            local_path = local_path.rstrip('\\')
            remote_path = remote_path.strip()
            remote_path = remote_path.rstrip('/')
            remote_path = remote_path.rstrip('\\')
            last_dir = os.path.basename(local_path)

            remote_path = os.path.join(remote_path, last_dir)
            remote_path = remote_path.replace('\\', '/')

            try:
                self.obj.mkd(remote_path)
            except Exception:
                logger.warning('dir: %s already exists' % last_dir)

            sub_items = os.listdir(local_path)
            for sub_item in sub_items:
                sub_item_path = os.path.join(local_path, sub_item)
                if os.path.isdir(sub_item_path):
                    self.upload_folder(sub_item_path, remote_path)
                else:
                    self.upload_file(sub_item_path, remote_path)
        except Exception:
            logger.error(f"fail to upload folder to FTP server,error as following:{traceback.format_exc()}")
            raise NotImplementedError("upload folder failure")

    def upload_file(self, src_file_path, remote_path):
        remote_file_name = os.path.basename(src_file_path)
        remote_path = remote_path + '/' + remote_file_name
        try:
            if self.obj.size(remote_path) != None:
                logger.warning("file [%s] has already exist!" % remote_path)
        except Exception:
            pass

        with open(src_file_path, 'rb') as file_handler:
            self.obj.storbinary('STOR %s' % remote_path, file_handler)
            logger.info('file [%s] has been upload to ftp server successfully!' % src_file_path)

    def download_dir(self, local_path, remote_path):
        local_path = local_path.strip()
        remote_path = remote_path.strip()
        remote_path = remote_path.rstrip('/')
        remote_path = remote_path.rstrip('\\')

        last_dir = os.path.basename(remote_path)
        local_path = os.path.join(local_path, last_dir)
        local_path = local_path.replace('/', '\\')
        if not os.path.isdir(local_path):
            os.makedirs(local_path)

        sub_items = self.obj.nlst(remote_path)
        for sub_item in sub_items:
            try:
                self.obj.cwd(sub_item)
                self.download_dir(local_path, sub_item)
            except Exception:
                self.download_file(local_path, sub_item)

    def download_file(self, local_path, remote_file_path):
        last_file_name = os.path.basename(remote_file_path)
        local_file_path = os.path.join(local_path, last_file_name)

        if os.path.isfile(local_file_path):
            local_file_path = local_file_path.replace('\\', '/')
            logger.debug('File [%s] has already exist!' % local_file_path)

        with open(local_file_path, 'wb') as file_handle:
            self.obj.retrbinary('RETR %s' % remote_file_path, file_handle.write)


@retry(ConnectionAbortedError, delay=5, jitter=(1, 3))
def _ftp(class_=FTPHelper):
    return class_(ip, username, password, port)
