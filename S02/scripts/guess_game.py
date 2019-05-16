def take_number():
    x = input('Gimme a  number : ')
    x = int(x)
    return x
    


#x = take_number()
#y = take_number()
# 
#def add(w,r):
#    return w+r
#    
#def show(z):
#    print(z)
#    
#show(add(x,y))
#exit()

import numpy as np

y = np.random.randint(100)

def take_number():
    x = input('guess a number : ')
    x = int(x)
    return x
    
 
print(x)

while True:
    x = take_number()  
    if x>y:
        print('Hi, your number is too large!')       
    elif y>x:
        print('Hi, your number is too small!')
    else:
        print('Dammet garm!')
        break
