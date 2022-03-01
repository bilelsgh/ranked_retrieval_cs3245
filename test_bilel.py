import math

tab = []
data = [1,2,3,4,5,6,7,8,9]

for idx,elt in enumerate( data ) :
    print("idx: {}, sqrt: {}".format(idx,math.sqrt(len(data))))
    print(idx % round( math.sqrt(len( data ) ) ))
    if idx % round( math.sqrt(len( data ) ) ) == 0:
        tab.append(elt)


print(tab)