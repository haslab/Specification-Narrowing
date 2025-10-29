import json
import os


sizes = list(range(4, 33, 4))

with open('dataset.json', 'r') as f:
    dataset = json.load(f)
    for example in dataset[:3]:
        base_model = example['model']
        for req in example['requirements']:
            all_specifications = [spec for spec in [req["oracle"]] + req["erroneous"]]
            alloy6_keywords = ["'"]
            alloy5_specifications = [spec for spec in all_specifications if not any(c in spec for c in alloy6_keywords)]
            specifications = {}
            for n in sizes:
                specifications = alloy5_specifications[:n]
                model = base_model
                for i,spec in enumerate(specifications):
                    model += f"\npred S{i} {{ {spec} }}\n"
                if not os.path.exists('problems'):
                    os.makedirs('problems')
                with open(f"problems/{example["id"]}_{req["pred"][5:]}_{n:02}.als", 'w') as out:
                    out.write(model)
