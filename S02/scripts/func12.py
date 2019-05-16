def fun1(x1):
    x1 = x1+2

def fun2(x1):
    return x1+2

x1 = 3
print(x1)
fun1(x1)
print(x1)
x1 = fun2(x1)
print(x1)  
exit()
