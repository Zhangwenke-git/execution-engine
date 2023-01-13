import uuid
import time
import math
import redis

"""
https://blog.csdn.net/weixin_30872499/article/details/102313842?spm=1001.2101.3001.6650.3&utm_medium=distribute.pc_relevant.none-task-blog-2%7Edefault%7ECTRLIST%7ERate-3-102313842-blog-106693255.pc_relevant_multi_platform_whitelistv3&depth_1-utm_source=distribute.pc_relevant.none-task-blog-2%7Edefault%7ECTRLIST%7ERate-3-102313842-blog-106693255.pc_relevant_multi_platform_whitelistv3&utm_relevant_index=4
"""

def acquire_lock(cli, lockname, acquire_timeout=3, lock_timeoout=2):
    """获取锁
    @param cli:   Redis实例
    @param lockname:   锁名称
    @param acquire_timeout: 客户端获取锁的超时时间（秒）, 默认3s
    @param lock_timeout: 锁过期时间（秒）, 超过这个时间锁会自动释放, 默认2s
    """
    lockname = f"lock:{lockname}"
    identifier = str(uuid.uuid4())
    lock_timeoout = math.ceil(lock_timeoout)

    end_time = time.time() + acquire_timeout

    while time.time() <= end_time:
        # 如果不存在当前锁, 则进行加锁并设置过期时间, 返回锁唯一标识
        if cli.set(lockname, identifier, ex=lock_timeoout, nx=True):  # 一条命令实现, 保证原子性
            return identifier
        # 如果锁存在但是没有失效时间, 则进行设置, 避免出现死锁
        elif cli.ttl(lockname) == -1:
            cli.expire(lockname, lock_timeoout)

        time.sleep(0.001)

    # 客户端在超时时间内没有获取到锁, 返回False
    return False


def release_lock(cli, lockname, identifier):
    """释放锁
    @param cli: Redis实例
    @param lock_name:   锁名称
    @param identifier:  锁标识
    """
    with cli.pipeline() as pipe:
        lockname = f"lock:{lockname}"
        while True:
            try:
                pipe.watch(lockname)
                id = pipe.get(lockname)
                if id and id == identifier:
                    pipe.multi()
                    pipe.delete(lockname)
                    pipe.execute()    # 执行EXEC命令后自动执行UNWATCH （DISCARD同理）
                    return True
                pipe.unwatch()  # 没有参数
                break
            except redis.WatchError:
                pass
        return False










if __name__ == "__main__":

    from threading import Thread
    # Redis 存字符串返回的是byte,指定decode_responses=True可以解决
    pool = redis.ConnectionPool(host="127.0.0.1", port=6379, socket_connect_timeout=3, decode_responses=True)
    redis_cli = redis.Redis(connection_pool=pool)

    count = 10


    def ticket(i):
        identifier = acquire_lock(redis_cli, 'Ticket')
        print(f"线程{i}--获得了锁")
        time.sleep(1)
        global count
        if count < 1:
            print(f"线程{i}没抢到票, 票已经抢完了")
            return
        count -= 1
        print(f"线程{i}抢到票了, 还剩{count}张票")
        release_lock(redis_cli, 'Resource', identifier)
        print(f"线程{i}--释放了锁")


    for i in range(10):
        t = Thread(target=ticket, args=(i, ))
        t.start()