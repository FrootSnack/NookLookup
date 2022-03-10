def main():
    subj_file = 'subjects.txt'
    with open(subj_file, 'r') as f:
        subj_list = f.read().split('\n')

    print(subj_list)


if __name__ == '__main__':
    main()
