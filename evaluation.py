import json
from timeit import default_timer as timer
from optimal import optimal_test_set
from nonoptimal1 import non_optimal1_test_set
from nonoptimal2 import non_optimal2_test_set
from statistics import mean,median

maximum = 16
step = 4
scope = 3

with open('dataset.json', 'r') as f:
    results = {}
    results['optimal_size'] = {n : [] for n in range(step, maximum+1, step)}
    results['optimal_time'] = {n : [] for n in range(step, maximum+1, step)}
    results['non_optimal1_size'] = {n : [] for n in range(step, maximum+1, step)}
    results['non_optimal1_time'] = {n : [] for n in range(step, maximum+1, step)}
    results['non_optimal2_size'] = {n : [] for n in range(step, maximum+1, step)}
    results['non_optimal2_time'] = {n : [] for n in range(step, maximum+1, step)}
    dataset = json.load(f)
    for example in dataset[:3]:
        print("========================================")
        print(example['example'])
        print("========================================")
        base_model = example['model']
        for req in example['requirements']:
            print('* '+req["description"] + ' *')
            sizes = list(range(step, maximum+1, step))
            print('         Size\t' + '\t'.join([str(n) for n in sizes]))
            instances = []
            time = []
            all_specifications = [spec.replace('{','(').replace('}',')') for spec in [req["oracle"]] + req["erroneous"]]
            alloy6 = ["'"]
            alloy5_specifications = [spec for spec in all_specifications if not any(c in spec for c in alloy6)]
            specifications = {}
            for n in sizes:
                specifications[n] = alloy5_specifications[:n]
            for n in sizes:
                model = base_model
                for i,spec in enumerate(specifications[n]):
                    model += f"\npred S{i} {{ {spec} }}\n"
                start = timer()
                result = optimal_test_set(model, scope)
                end = timer()
                instances.append(len(result))
                time.append(end - start)
                results['optimal_size'][n].append(len(result))
                results['optimal_time'][n].append(end - start)
            print('      Optimal\t' + '\t'.join([str(n) for n in instances]))
            print('         Time\t' + '\t'.join([f"{t:.2f}" for t in time]))
            instances = []
            time = []
            for n in sizes:
                model = base_model
                for i,spec in enumerate(specifications[n]):
                    model += f"\npred S{i} {{ {spec} }}\n"
                start = timer()
                result = non_optimal1_test_set(model, scope)
                end = timer()
                instances.append(len(result))
                time.append(end - start)
                results['non_optimal1_size'][n].append(len(result))
                results['non_optimal1_time'][n].append(end - start)
            print('Non Optimal 1\t' + '\t'.join([str(n) for n in instances]))
            print('         Time\t' + '\t'.join([f"{t:.2f}" for t in time]))
            instances = []
            time = []
            for n in sizes:
                model = base_model
                for i,spec in enumerate(specifications[n]):
                    model += f"\npred S{i} {{ {spec} }}\n"
                start = timer()
                result = non_optimal2_test_set(model, scope)
                end = timer()
                instances.append(len(result))
                time.append(end - start)
                results['non_optimal2_size'][n].append(len(result))
                results['non_optimal2_time'][n].append(end - start)
            print('Non Optimal 2\t' + '\t'.join([str(n) for n in instances]))
            print('         Time\t' + '\t'.join([f"{t:.2f}" for t in time]))
    print("========================================")
    print("Summary")
    print("========================================")
    sizes = list(range(step, maximum+1, step))
    print('         Size\t' + '\t'.join([str(n) for n in sizes]))
    print()
    print('      Optimal\t' + '\t'.join([f"{mean(results['optimal_size'][n]):.2f}" for n in sizes]))
    print('          Min\t' + '\t'.join([f"{min(results['optimal_size'][n])}" for n in sizes]))
    print('          Max\t' + '\t'.join([f"{max(results['optimal_size'][n])}" for n in sizes]))
    print('       Median\t' + '\t'.join([f"{median(results['optimal_size'][n]):.2f}" for n in sizes]))
    print()
    print('         Time\t' + '\t'.join([f"{mean(results['optimal_time'][n]):.2f}" for n in sizes]))
    print('          Min\t' + '\t'.join([f"{min(results['optimal_time'][n]):.2f}" for n in sizes]))
    print('          Max\t' + '\t'.join([f"{max(results['optimal_time'][n]):.2f}" for n in sizes]))
    print('       Median\t' + '\t'.join([f"{median(results['optimal_time'][n]):.2f}" for n in sizes]))
    print()
    print('Non Optimal 1\t' + '\t'.join([f"{mean(results['non_optimal1_size'][n]):.2f}" for n in sizes]))
    print('          Min\t' + '\t'.join([f"{min(results['non_optimal1_size'][n])}" for n in sizes]))
    print('          Max\t' + '\t'.join([f"{max(results['non_optimal1_size'][n])}" for n in sizes]))
    print('       Median\t' + '\t'.join([f"{median(results['non_optimal1_size'][n]):.2f}" for n in sizes]))
    print()
    print('         Time\t' + '\t'.join([f"{mean(results['non_optimal1_time'][n]):.2f}" for n in sizes]))
    print('          Min\t' + '\t'.join([f"{min(results['non_optimal1_time'][n]):.2f}" for n in sizes]))
    print('          Max\t' + '\t'.join([f"{max(results['non_optimal1_time'][n]):.2f}" for n in sizes]))
    print('       Median\t' + '\t'.join([f"{median(results['non_optimal1_time'][n]):.2f}" for n in sizes]))
    print()
    print('Non Optimal 2\t' + '\t'.join([f"{mean(results['non_optimal2_size'][n]):.2f}" for n in sizes]))
    print('          Min\t' + '\t'.join([f"{min(results['non_optimal2_size'][n])}" for n in sizes]))
    print('          Max\t' + '\t'.join([f"{max(results['non_optimal2_size'][n])}" for n in sizes]))
    print('       Median\t' + '\t'.join([f"{median(results['non_optimal2_size'][n]):.2f}" for n in sizes]))
    print()
    print('         Time\t' + '\t'.join([f"{mean(results['non_optimal2_time'][n]):.2f}" for n in sizes]))
    print('          Min\t' + '\t'.join([f"{min(results['non_optimal2_time'][n]):.2f}" for n in sizes]))
    print('          Max\t' + '\t'.join([f"{max(results['non_optimal2_time'][n]):.2f}" for n in sizes]))
    print('       Median\t' + '\t'.join([f"{median(results['non_optimal2_time'][n]):.2f}" for n in sizes]))

