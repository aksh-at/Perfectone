def sort(array):
    for j in range(1,len(array)):
        cur=array[j]
        i=j
        while i>0:
            if array[i-1]<cur:
                array[i]=cur
                break
            else:
                array[i]=array[i-1]
                i-=1
        if i==0:
            array[0]=cur
    return array

print sort([2,3,8,5,4,1,45,23.5])
