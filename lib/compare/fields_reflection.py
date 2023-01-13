from functools import reduce


class FieldReflect:

    def __init__(self,reflection_dict=None):
        self.reflection_dict = reflection_dict

    def __reflection(self,field_list):
        """
        :function: 将[string1,string2,string3...]中的字段按照mapping_dict中的关系进行转换，如果没有mapping_dict则返回原有的list
        :param fied_list:[string1,string2,string3...]
        :return:转换后的fieldList
        """
        self.reflection_dict = {} if not self.reflection_dict or len(self.reflection_dict) == 0 else self.reflection_dict

        if not isinstance(field_list,list):
            try:
                field_list = list(field_list)
            except Exception as e:
                raise AttributeError(f"Fail to convert data to list type,error as follow: {e}")
        for index,field in enumerate(field_list):
            for key,value in self.reflection_dict.items():
                if field in value:
                    field_list[index] = key
                    break
        return field_list


    def __convert(self,dict):
        """
        :function: 将dict中的key全部取出，并通过函数__reflection映射，得到映射后的field集合，因为集合类型才有&方法，求交集
        :param param_dict: dict类型
        :return: 集合类型{field1,field2,field3....}
        """
        keys_list = list(dict.keys())
        return set(self.__reflection(keys_list))


    def get_reflect(self,dict_list):
        """
        :function: 返回多个字典[dict1,dict2,dict3...] 经过映射得到的共有key
        :param data_list:
        :return:
        """
        public_key_list = list(reduce(lambda a, b: a & b, map(self.__convert, dict_list)))
        return public_key_list
