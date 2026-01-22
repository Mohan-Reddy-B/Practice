import re
text="the quick brown fox jump over the lazy dog123"
word = re.findall(r'\b\w+',text)
print(word)
match=re.search(input("enter string:"),text)
if match:
    print("match found!")
else:
    print("match not found")
match=re.match(r'^\w+',text)
print("after match:",match.group(0))