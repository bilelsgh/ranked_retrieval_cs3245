import math

tab = []
data = [1,2,3,4,5,6,7,8,9]
maxx = max(data)
for elt in data :
    tab.append(elt)
    if elt == maxx :
        break

print(tab)

