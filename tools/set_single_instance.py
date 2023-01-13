#仅支持没有参数的类
def singleton1(cls):
    """
    方法1：使用装饰器，装饰类，使其变成单个实例，即生成类的内存地址一致，可以print(Class)查看
    @param cls:
    @return:
    """
    instances = {}
    def getinstance(*args,**kwargs):
        if cls not in instances:
            instances[cls] = cls(*args,**kwargs)
        return instances[cls]
    return getinstance


#仅支持没有参数的类
def singleton2(cls):
    instance = cls()
    instance.__call__ = lambda: instance
    return instance


class Singleton(type):
    """
    方法2：使用元类，使用方法为集成元类: e.g. class Foo(metaclass=Singleton):pass
    """
    def __init__(self, *args, **kwargs):
        self.__instance = None
        super(Singleton,self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.__instance is None:
            self.__instance = super(Singleton,self).__call__(*args, **kwargs)
        return self.__instance


"""
方法3：在类中使用__new__,添加该函数即可
e.g. 
    def __new__(cls):
        # 关键在于这，每一次实例化的时候，我们都只会返回这同一个instance对象
        if not hasattr(cls, 'instance'):
            cls.instance = super(Singleton, cls).__new__(cls)
        return cls.instance
"""