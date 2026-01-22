s=int(input("enter the size of an array:"))
l1=[]
for i in range(s):
    ele=int(input("enter the element:"))
    l1.append(ele)
print("before sorting",l1)
for i in range(len(l1)-1):
    minIndex=i
    for j in range(i+1,len(l1)):
        if l1[j]<l1[minIndex]:
            minIndex=j
    l1[i],l1[minIndex]=l1[minIndex],l1[i]
print("after sorting",l1)