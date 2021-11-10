ylist = [5,6,6,14,15,16,18,28,29,35,35,35,36,37,38,38,42,50,50,60,60,58,75,75,85,90,110,328]

target = 200

for i in range(len(ylist)):
    sno = target-ylist[i]
    for j in range(i+1,len(ylist)):
        if ylist[j] == sno:
            print(ylist[i],ylist[j])
