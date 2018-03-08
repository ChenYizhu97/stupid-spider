import re
def regular(infilename,outfilenam,pattern='w'):
    with open(infilename, 'r') as f:
        lines = f.readlines()
        results = [line.split(',') for line in lines]
        teacher = []
        teacherlist = []
        for result in results:
            if not re.match(r'\d', result[0]):
                teacherlist.append(teacher)
                teacher = []
            teacher.append(result)
        teacherlist.remove(teacherlist[0])
        teacherlist = list(filter(lambda x: x != [['\n']] and len(x) != 1, teacherlist))

        for teacher in teacherlist:
            teacher[0][0] = teacher[0][0].strip('\n')
            for i in range(1, len(teacher)):
                teacher[i][2] = teacher[i][2].replace(r'/kns/', '/kcms/')
                teacher[i].remove(teacher[i][-1])
                if teacher[i][-1] == '':
                    teacher[i][-1] = '0'
    with open(outfilenam, pattern) as r:
        for teacher in teacherlist:
            for item in teacher:
                for col in item:
                    r.write(col + '#slash#')
                r.write(',')
            r.write('\n')
def getRegularData(filename):
    with open(filename,'r') as r:
        teacherlist = [teacher.strip('\n').split(',') for teacher in r.readlines()]

        for teacher in teacherlist:
            teacher = [item.split('#slash#') for item in teacher]
            for item in teacher:
                item.remove(item[-1])
            print(teacher)
if __name__ == '__main__':
    regular('results.txt','allresults.txt')
    regular('results-fromend.txt','allresults.txt','a')