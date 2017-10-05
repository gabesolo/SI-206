import re

f = open("regex_sum_36356.txt", 'r')

l = re.findall('[0-9]+', f.read())

l2 = []

for x in l:
	l2.append(int(x))


print(sum(l2))