s=int(input("enter the size of an array"))
l1=[]
for i in range(s):
    ele=int(input("enter the element"))
    l1.append(ele)
print(l1)
item=int(input("enter the element to search"))
for i in range(s):
    if item==l1[i]:
        print(item,"present at the position",i)
else:
    print(item,"is not present")
