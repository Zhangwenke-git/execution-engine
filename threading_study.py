"""
多线程，多进程，携程，异步，队列Q

# Lock ：互斥锁   效率高
# RLock ：递归(recursion)锁  效率相对低  在同一个线程中可以被acquire多次，如果想要释放锁，acquire多少次就要release多少次
"""


#========================================多线程========================================
import time
import threading
from threading import Event,Lock,RLock,Condition,Thread,Semaphore

# 条件锁，递归锁，死锁，同步锁（lock）也叫互斥锁，信号量

def test1(n):
    print(f"T1 start to run...")
    time.sleep(n)
    print(f"T1 has wait for {n}s")

def test2(m):
    print(f"T2 start to run...")
    time.sleep(m)
    print(f"T2 has wait for {m}s")


g_num = 100
def work1():
    global  g_num
    for i in range(3):
        g_num+=1
    print('in work1 g_num is : %d' % g_num)

def work2():
    global g_num
    g_num+=1
    print('in work2 g_num is : %d' % g_num)









"""
-----------------1、原生------------------
start= time.time()
print("@main thread start to run...")
t1 = threading.Thread(target=test1,args=(5,))
t2 = threading.Thread(target=test2,args=(2,))
t1.start()
t2.start()
end = time.time()
print(f"@main thread has wait for {end-start}s")
===================result=======================
@main thread start to run...
T1 start to run...
T2 start to run...
@main thread has wait for 0.0011484622955322266s
T2 has wait for 2s
T1 has wait for 5s
*************************************************************************************************
"""

"""
-----------------2、主线程不等待子线程setDaemon------------------
start= time.time()
print("@main thread start to run...")
t1 = threading.Thread(target=test1,args=(5,))
t2 = threading.Thread(target=test2,args=(2,))

t1.daemon = True
# 已经弃用t.setDaemon(True)，使用t.daemon=True代替，否则提示：DeprecationWarning: setDaemon() is deprecated, set the daemon attribute instead
# 且setDaemon必须放在start之前，否则提示：RuntimeError: cannot set daemon status of active thread
# 作为守护线程后，即主线程不再等待守护线程结束，会出现主线程结束了，但守护线程没结束，但随着主线程结束，也会被强行结束,设置setDaemon的参数为True之后。主线程和子线程会同时运行，主线程结束运行后，无论子线程运行与否，都会和主线程一起结束
t1.start()
t2.start()

end = time.time()
print(f"@main thread has wait for {end-start}s")
===================result=======================
@main thread start to run...
T1 start to run...
T2 start to run...
@main thread has wait for 0.0009965896606445312s
T2 has wait for 2s
*************************************************************************************************
"""

"""
    -----------------3、主线程等待子线程join------------------
    start= time.time()
    print("@main thread start to run...")
    t1 = threading.Thread(target=test1,args=(5,))
    t2 = threading.Thread(target=test2,args=(2,))

    t1.start()
    t2.start()

    t1.join()
    # join是阻塞主线程，让主线程等待指定的子线程，setDaemon无需和join一起使用
    # join需要在所有的线程之后添加，而不是在t1.start和t2.start之间添加，而是在t2.start之后添加，这样t1和t2才能一起运行，减少时间
    end = time.time()
    print(f"@main thread has wait for {end-start}s")
    ===================result=======================
    @main thread start to run...
    T1 start to run...
    T2 start to run...
    T2 has wait for 2s
    T1 has wait for 5s
    @main thread has wait for 5.010838270187378s
    *************************************************************************************************
    """

"""
-----------------4、两个变成之间共享变量------------------
t1 = threading.Thread(target=work1)
t1.start()
time.sleep(2)
print("wait for 2s")  # t1对共享变量操作完成之后，返回的变量值，被t2再次操作
t2=threading.Thread(target=work2)
t2.start()
===================result=======================
in work1 g_num is : 103
wait for 2s
in work2 g_num is : 104
*************************************************************************************************
"""

"""
-----------------5、互斥锁Lock------------------
def work():
    global n
    #lock.acquire()
    temp = n
    time.sleep(0.001) #时间不能太长，太长看不到效果
    n = temp-1
    #lock.release()
if __name__ == '__main__':
    lock = Lock()
    n = 100
    l = []
    for i in range(100):
        p = Thread(target=work)
        l.append(p)
        p.start()
    for p in l:
        p.join()
    print(n)
===================result=======================
98或者99
因为100个线程都去拿到变量去做减法时，由于线程之间是进行随机调度的，如果有多个线程同时操作一个对象，如果没有很好地保护该对象，会造成程序结果的不可预期，
我们因此也称为“线程不安全”。导致输出的结果仅是98或者99
为了防止上面情况的发生，就出现了互斥锁（Lock）
步骤：对对象操作的函数中，先获获取锁，之后添加代码，最后失败锁，该过程就会仅有一个线程对其操作，如上述代码，将lock.acquire()和lock.release()
注释即可，实际调用该函数时，需要声明一个锁lock=Lock(),最后打印出的n则就是0
*************************************************************************************************
"""

"""
-----------------6、递归锁Rlock------------------
def func(lock):
    global gl_num
    lock.acquire()
    gl_num += 1
    time.sleep(0.01)
    print(gl_num)
    lock.release()


if __name__ == '__main__':
    gl_num = 0
    lock = threading.RLock()
    for i in range(10):
        t = threading.Thread(target=func,args=(lock,))
        t.start()
# 被多线程调用的函数，参数需要有lock对象，在此案例中，10个线程处理，之后10个线程都加了锁
===================result=======================
1
2
3
4
5
6
7
8
9
10

*************************************************************************************************
"""

"""
-----------------7、死锁------------------
# 1:死锁现象是怎么产生的?
#     多把(互斥/递归)锁 并且在多个线程中 交叉使用
#             fork_lock.acquire()
#             noodle_lock.acquire()
#
#             fork_lock.release()
#             noodle_lock.release()
# 2:如果是互斥锁,出现了死锁现象,最快速的解决方案把所有的互斥锁都改成一把递归锁,但是程序的效率会降低的
# 3:递归锁 效率低 但是解决死锁现象有奇效
# 4:互斥锁 效率高 但是多把锁容易出现死锁现象
# 5:一把互斥锁就够了
暂无案例
*************************************************************************************************
"""

"""
-----------------8、信号量（Semaphore）------------------
def run(n,semaphore):
    semaphore.acquire()   #加锁
    time.sleep(3)
    print('run the thread:%s\n' % n)
    semaphore.release()    #释放


if __name__== '__main__':
    semaphore = threading.BoundedSemaphore(2)   #最多允许2个线程同时运行
    for i in range(10):
        t = threading.Thread(target=run,args=('t-%s' % i,semaphore))
        t.start()
    while threading.active_count() !=1:
        pass
    else:
        print('----------all threads done-----------')
        
#互斥锁Lock同时只允许一个线程更改数据，而Semaphore是同时允许一定数量的线程更改数据，比如厕所有3个坑，那最多只允许3个人上厕所，后面的人只能等里面有人出来了才能再进去
在此案例中，则10个线程，每次2个一组，对对象进行操作
===================result=======================
run the thread:t-1
run the thread:t-0

run the thread:t-2
run the thread:t-3

run the thread:t-4
run the thread:t-5

run the thread:t-6
run the thread:t-7

run the thread:t-8
run the thread:t-9

----------all threads done-----------
*************************************************************************************************
"""

"""
-----------------9、事件------------------
def spider(n,event):# 定义event对象传输进去
    print("Thread-%s has ready!" % n)
    event.wait()
    print("Thread-%s start to work" % n)


if __name__ == "__main__":
    event = threading.Event()
    for i in range(1,11):
        t = threading.Thread(target=spider,args=(i,event,))
        t.start()
    n=0
    while n <= 3:
        n=n+1
    print("--------5 minutes,all will start to work--------")
    time.sleep(5)
    
    event.set()

此案例中，event.wait()将所有的线程进行堵塞，之后event.set()对所有的线程进行释放，如同放洪水，先存储之后一并释放，即event.wait()和event.set()成对出现
Event是一个能在多线程中共用的对象，一开始它包含一个为 False的信号标志，一旦在任一一个线程里面把这个标记改为 True，那么所有的线程都会看到这个标记变成了 True。
python线程的事件用于主线程控制其他线程的执行，事件是一个简单的线程同步对象，其主要提供以下的几个方法：
clear将flag设置为 False
set将flag设置为 True
is_set判断是否设置了flag
wait会一直监听flag，如果没有检测到flag就一直处于阻塞状态
事件处理的机制：全局定义了一个Flag，当Flag的值为False，那么event.wait()就会阻塞，当flag值为True，
那么event.wait()便不再阻塞

===================result=======================
Thread-1 has ready!
Thread-2 has ready!
Thread-3 has ready!
Thread-4 has ready!
Thread-5 has ready!
Thread-6 has ready!
Thread-7 has ready!
Thread-8 has ready!
Thread-9 has ready!
Thread-10 has ready!--------5 minutes,all will start to work--------

Thread-3 start to work
Thread-5 start to work
Thread-7 start to work
Thread-10 start to work
Thread-8 start to work
Thread-4 start to work
Thread-9 start to work
Thread-1 start to workThread-6 start to workThread-2 start to work
*************************************************************************************************
"""

"""
    -----------------8、信号量（Semaphore）------------------
    class Seeker(threading.Thread):
        def __init__(self, cond, name):
            super(Seeker, self).__init__()
            self.cond = cond
            self.name = name
    
        def run(self):
            self.cond.acquire()
            print(self.name + ': 我已经把眼睛蒙上了')
    
            self.cond.notify()
            print('notifyed...')
            # 释放condition条件锁，waiter线程Hider真正开始执行
            self.cond.wait()
            print('waited...')
            print(self.name + ': 我找到你了 ~_~')
    
            self.cond.notify()
            self.cond.release()
            print(self.name + ': 我赢了')
    
    
    class Hider(threading.Thread):
        def __init__(self, cond, name):
            super(Hider, self).__init__()
            self.cond = cond
            self.name = name
    
        def run(self):
            self.cond.acquire()
            # wait()释放对琐的占用，同时线程挂起在这里，直到被notify并重新占有琐。
            self.cond.wait()
            print(self.name + ': 我已经藏好了，你快来找我吧')
    
            self.cond.notify()
            self.cond.wait()
            self.cond.release()
            print(self.name + ': 被你找到了，哎~~~')
    
    if __name__ == "__main__":
        
        cond = threading.Condition()
        hider = Hider(cond, 'hider')
        seeker = Seeker(cond, 'seeker')
        hider.start()
        seeker.start()
        hider.join()
        seeker.join()
        print('end...')

    acquire(): 线程锁
    release(): 释放锁
    wait(timeout): 线程挂起，直到收到一个notify通知或者超时（可选的，浮点数，单位是秒s）才会被唤醒继续运行。wait()必须在已获得Lock前提下才能调用，否则会触发RuntimeError。
    notify(n=1): 通知其他线程，那些挂起的线程接到这个通知之后会开始运行，默认是通知一个正等待该condition的线程,最多则唤醒n个等待的线程。notify()必须在已获得Lock前提下才能调用，否则会触发RuntimeError。notify()不会主动释放Lock。
    notifyAll(): 如果wait状态线程比较多，notifyAll的作用就是通知所有线程
    
    cond = threading.Condition()定义一个全局锁，之后两个线程首先均要获取锁acquire，之后一个可以挂起wait，之后必须要通知其他线程notify，wait和notify必须是成对出现的，定义的cond从两
    个线程中，由上往下，以此读取wait,notify,wait,notify...可以交叉读取，看先后顺序，最后所有的线程需要release释放锁
    ===================result=======================
    seeker: 我已经把眼睛蒙上了
    notifyed...
    hider: 我已经藏好了，你快来找我吧
    waited...
    seeker: 我找到你了 ~_~
    seeker: 我赢了
    hider: 被你找到了，哎~~~
    end...

    *************************************************************************************************
"""

