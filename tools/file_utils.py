import os
from tools.logger import logger


class FileUtils:

    @classmethod
    def get_filenames_list(cls, dirpath):
        """
        :function:获取一个文件下所有的文件名称，并以一个list返回
        :param path:文件夹下的路径
        :return:list中包含文件夹和文件
        """
        logger.debug(f"Prepare to get filename under path [{dirpath}]")
        return os.listdir(dirpath)

    @classmethod
    def judge_file_download(cls, dirpath, filename):
        """
        :function:判断一个文件是否在某个文件夹下存在
        :param dirpath: 文件夹的路径
        :param filename: 文件名，不是文件的路径
        :return:
        """
        flag = False
        if cls.judge_file_exist(dirpath):
            if filename in cls.get_filenames_list(dirpath):
                flag = True
                logger.debug(f'The file: {filename} exists!')
            else:
                logger.error(f'File: {filename} does not exist!')
        return flag

    @classmethod
    def judge_file_exist(cls, path):
        """
        :function：判断文件或者文件夹是否存在
        :param path:
        :return:
        """
        flag = False
        if os.path.exists(path):
            flag = True
            logger.debug(f'File: {path} exists!')
        else:
            logger.error(f'File: {path} does not exist!')
        return flag

    @classmethod
    def get_file_size(cls, path):
        """
        :function：判断文件大小
        :param path:
        :return:
        """
        size = None
        if cls.judge_file_exist(path):
            size = os.path.getsize(path)
            if size == 0:
                logger.debug(f'The file: {path} is empty!')
            else:
                logger.debug(f'The size of file: {path} is :{size}!')
        return size

    @classmethod
    def get_file_count(cls, dirpath):
        """
        :function:获取一个文件夹下文件的个数，因为有的时候下载的文件重名，就会显示为：filename.format(1),这样的情况使用judgeFileDownload不行，只能通过下载文件前后，判断文件夹下的文件的数量是否有增长
        :param dirpath:
        :return:
        """
        count = None
        if cls.judge_file_exist(dirpath):
            count = int(len([lists for lists in os.listdir(dirpath) if os.path.isfile(os.path.join(dirpath, lists))]))
        logger.debug(f'The count of files is: {count}!')
        return count

    @classmethod
    def get_dirs_count(cls, dirpath):
        """
        :function:获取一个文件夹下文件夹的个数
        :param dirpath:
        :return:
        """
        count = None
        if cls.judge_file_exist(dirpath):
            count = int(len([lists for lists in os.listdir(dirpath) if os.path.isdir(os.path.join(dirpath, lists))]))
        logger.debug(f'The count of dirs is: {count}!')
        return count

    @staticmethod
    def create_file(filepath):
        """
        :function:文件不存在就创建一个，但其所在的文件夹必须存在，如果不存在，可以使用createFolder
        :param filepath:
        """
        with open(filepath, mode='a', encoding='utf-8') as f:
            f.write(filepath)

    @staticmethod
    def create_folder(folder):
        """
        :function:文件夹不存在就创建一个
        :param filepath:
        """
        if not os.path.exists(folder):
            os.makedirs(folder)

    @staticmethod
    def create_bat_file(bat_string, bat_path):
        """
        :function:生成一个bat文件
        :param bat_string: 文件字符串
        :param bat_path: 生成的路径
        """
        with open(bat_path, "w") as f:
            f.write(bat_string)

