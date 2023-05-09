import yaml

class YamlParser:
    '''
    用于解析 Yaml 文件的工具类
    '''
    def __init__(self, file_path):
        self.file_path = file_path

    def read_yaml(self):
        '''
        读取 Yaml 文件
        '''
        with open(self.file_path, 'r', encoding='utf-8') as f:
            yaml_data = yaml.load(f, Loader=yaml.FullLoader)
        return yaml_data
