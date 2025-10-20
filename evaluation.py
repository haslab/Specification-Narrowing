import json
from timeit import default_timer as timer
from optimal import optimal_test_set
from nonoptimal import non_optimal_test_set
from statistics import mean,median

maximum = 16
step = 4
scope = 3

with open('dataset.json', 'r') as f:
    results = {}
    dataset = json.load(f)
    for example in dataset[:3]:
        example_results = results.setdefault(example['example'],{})
        example_results['optimal_size'] = {n : [] for n in range(step, maximum+1, step)}
        example_results['optimal_time'] = {n : [] for n in range(step, maximum+1, step)}
        example_results['non_optimal_size'] = {n : [] for n in range(step, maximum+1, step)}
        example_results['non_optimal_time'] = {n : [] for n in range(step, maximum+1, step)}
        print("========================================")
        print(example['example'])
        print("========================================")
        base_model = example['model']
        for req in example['requirements']:
            print('* '+req["description"] + ' *')
            sizes = list(range(step, maximum+1, step))
            print('       Size\t' + '\t'.join([str(n) for n in sizes]))
            instances = []
            time = []
            for n in sizes:
                model = base_model
                specifications = [req["oracle"]] + req["erroneous"][:n-1]
                for i,spec in enumerate(specifications):
                    model += f"\npred S{i} {spec}\n"
                start = timer()
                result = optimal_test_set(model, scope)
                end = timer()
                instances.append(len(result))
                time.append(end - start)
                example_results['optimal_size'][n].append(len(result))
                example_results['optimal_time'][n].append(end - start)
            print('    Optimal\t' + '\t'.join([str(n) for n in instances]))
            print('       Time\t' + '\t'.join([f"{t:.2f}" for t in time]))
            instances = []
            time = []
            for n in sizes:
                model = base_model
                specifications = [req["oracle"]] + req["erroneous"][:n-1]
                for i,spec in enumerate(specifications):
                    model += f"\npred S{i} {spec}\n"
                start = timer()
                result = non_optimal_test_set(model, scope)
                end = timer()
                instances.append(len(result))
                time.append(end - start)
                example_results['non_optimal_size'][n].append(len(result))
                example_results['non_optimal_time'][n].append(end - start)
            print('Non Optimal\t' + '\t'.join([str(n) for n in instances]))
            print('       Time\t' + '\t'.join([f"{t:.2f}" for t in time]))
        print("----------------------------------------")
        sizes = list(range(step, maximum+1, step))
        print('       Size\t' + '\t'.join([str(n) for n in sizes]))
        print()
        print('    Optimal\t' + '\t'.join([f"{mean(example_results['optimal_size'][n]):.2f}" for n in sizes]))
        print('        Min\t' + '\t'.join([f"{min(example_results['optimal_size'][n])}" for n in sizes]))
        print('        Max\t' + '\t'.join([f"{max(example_results['optimal_size'][n])}" for n in sizes]))
        print('     Median\t' + '\t'.join([f"{median(example_results['optimal_size'][n]):.2f}" for n in sizes]))
        print()
        print('       Time\t' + '\t'.join([f"{mean(example_results['optimal_time'][n]):.2f}" for n in sizes]))
        print('        Min\t' + '\t'.join([f"{min(example_results['optimal_time'][n]):.2f}" for n in sizes]))
        print('        Max\t' + '\t'.join([f"{max(example_results['optimal_time'][n]):.2f}" for n in sizes]))
        print('     Median\t' + '\t'.join([f"{median(example_results['optimal_time'][n]):.2f}" for n in sizes]))
        print()
        print('Non Optimal\t' + '\t'.join([f"{mean(example_results['non_optimal_size'][n]):.2f}" for n in sizes]))
        print('        Min\t' + '\t'.join([f"{min(example_results['non_optimal_size'][n])}" for n in sizes]))
        print('        Max\t' + '\t'.join([f"{max(example_results['non_optimal_size'][n])}" for n in sizes]))
        print('     Median\t' + '\t'.join([f"{median(example_results['non_optimal_size'][n]):.2f}" for n in sizes]))
        print()
        print('       Time\t' + '\t'.join([f"{mean(example_results['non_optimal_time'][n]):.2f}" for n in sizes]))
        print('        Min\t' + '\t'.join([f"{min(example_results['non_optimal_time'][n]):.2f}" for n in sizes]))
        print('        Max\t' + '\t'.join([f"{max(example_results['non_optimal_time'][n]):.2f}" for n in sizes]))
        print('     Median\t' + '\t'.join([f"{median(example_results['non_optimal_time'][n]):.2f}" for n in sizes]))

