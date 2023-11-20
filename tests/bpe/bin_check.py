"""simple file check by binary comparison"""

import argparse


def bin_check(file1: str, file2: str):
    """binary compare between in/out files"""
    with open(file1, "rb") as f:
        data_in = f.read()

    with open(file2, "rb") as f:
        data_out = f.read()

    count = 0

    if len(data_in) != len(data_out):
        print("In file and out file are not the same size!")

    else:
        for dataI, dataO in zip(data_in, data_out):
            if dataI != dataO:
                count += 1

    print("\nData In Size; Data Out Size; Total of Nonidentical Data Instances:")
    print(len(data_in))
    print(len(data_out))
    print(count)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("file1")
    parser.add_argument("file2")
    args = parser.parse_args()
    bin_check(args.file1, args.file2)
