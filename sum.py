n=int(input("enter a number"))
sum=0
if n<0:
    print("enter positive number")
else:
    for i in range(1,n+1):
        sum=sum+i
print("sum of",n,"natural number is",sum)