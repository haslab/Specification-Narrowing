from email.mime import text
from statistics import mean,median
import os
import subprocess
import sys
import re

if len(sys.argv) != 6:
    print("Usage: python evaluation.py <algorithm> <min_scope> <max_scope> <min_size> <max_size>")
    sys.exit(1)

algorithm = sys.argv[1]
min_scope = int(sys.argv[2])
max_scope = int(sys.argv[3])
min_size = int(sys.argv[4])
max_size = int(sys.argv[5])
sizes = []
scopes = list(range(min_scope, max_scope + 1))

testcases = {}
time = {}

for filename in os.listdir('problems'):
    if not filename.endswith('.als'):
        continue
    model = filename[:-4].split('_')[0]
    requirement = filename[:-4].split('_')[1]
    size = int(filename[:-4].split('_')[2])
    if size > max_size:
        continue
    if size < min_size:
        continue
    if size not in sizes:
        sizes.append(size)
    for scope in scopes:  
        if (size,scope) not in testcases:
            testcases[(size,scope)] = []
            time[(size,scope)] = []  
        print(f"Processing model {model}, requirement {requirement}, size {size}, with scope {scope}...")
        # run command line tool with timeout
        filepath = os.path.join('problems', filename)
        try:
            result = subprocess.run(
                ['python', algorithm + '.py', filepath, str(scope)],  
                capture_output=True,
                text=True,
                timeout=60
            )
            test_suite = result.stdout
            first_line = test_suite.splitlines()[0]
            numbers = re.findall(r'\d+\.?\d*', first_line)
            tests = int(numbers[0])
            seconds = float(numbers[1])
            testcases[(size,scope)].append(tests)
            time[(size,scope)].append(seconds)
            print(f"    Generated {tests} test cases in {seconds:.2f} seconds.")
        except subprocess.TimeoutExpired:
            print("    Timed out!")
sizes.sort()
for s in scopes:
    print("========================================")
    print("Summary for scope " + str(s))
    print("========================================")
    print('Specifications\t' + '\t'.join([str(n) for n in sizes]))
    print()
    print('     Completed\t' + '\t'.join([f"{len(testcases[(n,s)])}" for n in sizes]))
    print()
    print('          Size\t' + '\t'.join([f"{mean(testcases[(n,s)]):.2f}" if testcases[(n,s)] else "NA" for n in sizes]))
    print('           Min\t' + '\t'.join([f"{min(testcases[(n,s)])}" if testcases[(n,s)] else "NA" for n in sizes]))
    print('           Max\t' + '\t'.join([f"{max(testcases[(n,s)])}" if testcases[(n,s)] else "NA" for n in sizes]))
    print('        Median\t' + '\t'.join([f"{median(testcases[(n,s)]):.2f}" if testcases[(n,s)] else "NA" for n in sizes]))
    print()
    print('          Time\t' + '\t'.join([f"{mean(time[(n,s)]):.2f}" if time[(n,s)] else "NA" for n in sizes]))
    print('           Min\t' + '\t'.join([f"{min(time[(n,s)]):.2f}" if time[(n,s)] else "NA" for n in sizes]))
    print('           Max\t' + '\t'.join([f"{max(time[(n,s)]):.2f}" if time[(n,s)] else "NA" for n in sizes]))
    print('        Median\t' + '\t'.join([f"{median(time[(n,s)]):.2f}" if time[(n,s)] else "NA" for n in sizes]))

