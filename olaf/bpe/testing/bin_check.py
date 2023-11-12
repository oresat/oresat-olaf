# binary compare between in/out files

import sys


def bin_check(file1, file2):
    with open(file1,'rb') as f:
        data_in = f.read()

    with open(file2, 'rb') as f:
        data_out = f.read()

    count = 0

    if len(data_in) != len(data_out):
        print('In file and out file are not the same size!')

    else:
        for dataI, dataO in zip(data_in, data_out):
            if dataI != dataO:
                count += 1

    print("Data In Size; Data Out Size; Total of Nonidentical Data Instances:")
    print(len(data_in))
    print(len(data_out))
    print(count)

# if calling from command line: python bin_check.py <file1> <file2>
if __name__ == '__main__':
    file1 = sys.argv[1]
    file2 = sys.argv[2]
    bin_check(file1, file2)   
