a=int(input("enter first element"))
b=int(input("enter the second element"))
while True:
    op=input("+,-,*,//,/: enter your option:")
    if op=="+":c=a+b
    elif op=="-":c=a-b
    elif op=="*":c=a*b
    elif op=="/":c=a/b
    elif op=="//":c=a//b
    else:
        print("invalid choice")
        exit()
    print(f"{a} {op} {b}={c}")