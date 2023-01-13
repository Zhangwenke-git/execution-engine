from datetime import datetime,date
import time

class BaicSet(object):

    def current(self,*args):
        current = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
        return current
    def today(self,*args):
        current = time.strftime("%Y/%m/%d",time.localtime())
        return current

    def instn21(self,*args):
        return args[0]+args[1]

    def combinationTest(self,*args):
        string = 'TestResult:'+args[0]+args[1]
        return string


    def interestTotal(self,*args):
        volume = int(args[0])
        rate = float(args[1])

        interest = volume*rate
        return interest

    def check(self,*args):
        return args[0]

    def login(self,*args):
        return args[0]+args[1]
