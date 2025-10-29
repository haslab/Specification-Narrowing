import json
import os

# the min number of wrong specifications per requirement is 29
sizes = list(range(4, 28, 4))

with open('dataset.json', 'r') as f:
    dataset = json.load(f)
    for example in dataset[:3]:
        base_model = example['model']
        for req in example['requirements']:
            all_specifications = [req["oracle"]] + req["erroneous"]
            for n in sizes:
                if n > len(all_specifications):
                    print(f"Skipping generation for {example['id']} {req['pred']} size {n} since only {len(all_specifications)} specifications are available.")
                    continue
                specifications = all_specifications[:n]
                model = base_model
                for i,spec in enumerate(specifications):
                    model += f"\npred S{i} {{ {spec} }}\n"
                if not os.path.exists('problems'):
                    os.makedirs('problems')
                with open(f"problems/{example["id"]}_{req["pred"][5:]}_{n:02}.als", 'w') as out:
                    out.write(model)