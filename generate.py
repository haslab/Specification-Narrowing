import json
import os
import sys

import jpype
import jpype.imports

if len(sys.argv) < 5:
    print("Usage: python generate.py <min_size> <max_size> <step_size> <models>")
    sys.exit(1)

min_size = int(sys.argv[1])
max_size = int(sys.argv[2])
stp_size = int(sys.argv[3])
models = sys.argv[4:]

# the min number of wrong specifications per requirement is 29
sizes = list(range(min_size, max_size+1, stp_size))

if not jpype.isJVMStarted():
    jpype.startJVM(classpath=["AlloyMax-1.0.2.jar"])

def syntax_ok(base, req):
    try:
        from edu.mit.csail.sdg.parser import CompUtil
        from edu.mit.csail.sdg.alloy4 import ErrorSyntax
        model = f"{base}\nrun {{ {req} }}"
        CompUtil.parseEverything_fromString(None,model)
        return True
    except ErrorSyntax as e:  
        print("Discarded specification:", e.msg)
        return False

with open('dataset.json', 'r') as f:
    dataset = json.load(f)
    for example in (d for d in dataset if d["id"] in models):
        base_model = example['model']
        for req in example['requirements']:
            all_specifications = [r for r in [req["oracle"]] + req["erroneous"] if syntax_ok(base_model, r)]

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
                with open(f'problems/{example["id"]}_{req["pred"][5:]}_{n}.als', 'w') as out:
                    out.write(model)