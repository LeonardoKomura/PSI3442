import random
i = 0
for i in range(10):
    number = random.randint(0,100)
    number -= 50
    number = number/1000
    print(number)