from tools.cache import memory_cache
from tools.dict_utils import DictUtils
from tools.file_utils import FileUtils

BASE_INFO = {}


class AllureEnvInitializer:
    def __init__(self):
        self.data = memory_cache()
        self.data = DictUtils.multi_dict_merge([self.data, BASE_INFO])

    def __dict_to_xml(self):
        parameter = []
        for k in sorted(self.data.keys()):
            xml = []
            v = self.data.get(k)
            if k == 'detail' and not v.startswith('<![CDATA['):
                v = '<![CDATA[{}]]>'.format(v)
            xml.append('<key>{value}</key>'.format(value=k))
            xml.append('<value>{value}</value>'.format(value=v))
            parameter.append('<parameter>{}</parameter>'.format(''.join(xml)))
        return '<environment>{}</environment>'.format(''.join(parameter))

    def init(self, xmlpath):
        data = self.__dict_to_xml()
        folder_path = xmlpath[:-15]
        FileUtils.create_folder(folder_path)
        FileUtils.create_file(xmlpath)

        with open(xmlpath, 'w') as f:
            f.write(data)
