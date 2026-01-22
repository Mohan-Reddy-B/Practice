class stack:
    def _init_(self):
        self.data=[]
    def push(self,ele):
        self.data.append(ele)
    def pop(self):
        return self.data.pop()
    def display(self):
        print(self.data)
    def peek(self):
        print(self.data[-1])
s1=stack()
while True:
    print("select operation:")
    print("1.push \n 2.pop \n 3.display \n 4.peek \n 5.exit()")
    op=int(input("enter your option:"))
    if op==1:
        val=int(input("enter element ->"))
        s1.push(val)
    elif op==2:
        print("remove element ->",s1.pop())
    elif op==3:
        s1.display()
    elif op==4:
        s1.peek()
    elif op==5:
        exit()
    else:
        print("enter correct option")
