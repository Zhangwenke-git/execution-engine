import os
import json
from config.settings import Settings
from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateNotFound


path = os.path.join(Settings.base_dir, "templates")


class JsonTemplateReader():
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader(path))

    def get_data(self, test_name, **kwargs):
        try:
            template = self.env.get_template("{}.json".format(test_name))
            return json.loads(template.render(**kwargs))
        except TemplateNotFound:
            raise NameError(f"入参模板的json文件名称和map映射文件中的函数名称[{test_name}]不一致")
