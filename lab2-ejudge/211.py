arr = list(map(int, input().split()))
arr1 = list(map(int, input().split()))
arr2 = reversed(arr1[arr[1]-1:arr[2]])
arr1[arr[1]-1:arr[2]] = arr2
for i in arr1:
    print(i, end=" ")