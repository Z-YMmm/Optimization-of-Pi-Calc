# https://blog.csdn.net/lnotime/article/details/82319973
import time

K = 100
def pi(n):
    p = 10 ** (n + K)  # 准备初始整数，先多乘 k 个 0，以增加精度，最后再去掉
    a = p * 16 // 5     # 第一项的前半部分
    b = p * 4 // -239   # 第一项的后半部分
    f = a + b           # 第一项的值
    p = f               # π
    j = 3              
    while abs(f):       # 当|f|=0后计算π的值就不会再改变了
        a //= -25       # 第n项的前半部分
        b //= -57121    # 第n项的后半部分
        f = (a + b) // j
        p += f
        j += 2
    return p // 10**K  # 去掉 k 位

t = time.time()     #获取当前时间
print(str(pi(int(1e5)))[-100:])     # 输出最后 100 位
print(time.time() - t)      # 花费时间
