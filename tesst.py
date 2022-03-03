with open("postings.txt","r") as f:
    f.seek(2240454)
    print(f.readline())

 #            offset = offset+1 if offset != 0 else offset
