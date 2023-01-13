__description__ = """
    给输入的日志添加颜色
"""

class Color:
    @classmethod
    def _wrap_colour(cls, colour, *args):
        for a in args:
            print(colour + '{}'.format(a) + '\033[0m')

    @classmethod
    def blue(cls, *args):
        return cls._wrap_colour('\033[94m', *args)

    @classmethod
    def bold(cls, *args):
        return cls._wrap_colour('\033[1m', *args)

    @classmethod
    def cyan(cls, *args):
        return cls._wrap_colour('\033[96m', *args)

    @classmethod
    def darkcyan(cls, *args):
        return cls._wrap_colour('\033[36m', *args)

    @classmethod
    def green(cls, *args):
        return cls._wrap_colour('\033[92m', *args)

    @classmethod
    def purple(cls, *args):
        return cls._wrap_colour('\033[95m', *args)

    @classmethod
    def red(cls, *args):
        return cls._wrap_colour('\033[91m', *args)

    @classmethod
    def underline(cls, *args):
        return cls._wrap_colour('\033[4m', *args)

    @classmethod
    def yellow(cls, *args):
        return cls._wrap_colour('\033[93m', *args)