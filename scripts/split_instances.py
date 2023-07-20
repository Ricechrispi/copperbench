import os
import random
import shutil
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--instance_folder", dest="instance_folder", type=str)
    parser.add_argument("--split1_folder", dest="split1_folder", type=str, default="split1")
    parser.add_argument("--split2_folder", dest="split2_folder", type=str, default="split2")
    parser.add_argument("--split1_percentage", dest="split1_percentage", type=float, default=0.5)
    parser.add_argument("--random_seed", dest="random_seed", type=int, default=1)
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    random.seed(1)

    # get all filenames
    base_instances = os.listdir(args.instance_folder)
    print(f'Found {str(len(base_instances))} instances to split')

    split1_criterion = lambda x: random.random() < args.split1_percentage
    def random_subset(s, criterion):
        return set(filter(criterion, s))

    # get train_percentage sized subset
    split1_instances = random_subset(base_instances, split1_criterion)
    split2_instances = []
    for instance in base_instances:
        if instance not in split1_instances:
            split2_instances.append(instance)

    print(f'split1 len: {str(len(split1_instances))}')
    print(f'split2 len: {str(len(split2_instances))}')
    # sanity check if the length are the same of lists and the sets (no duplicates)
    print(f'split1 set len: {str(len(set(split1_instances)))}')
    print(f'split2 set len: {str(len(set(split2_instances)))}')
    assert len(split1_instances) == len(set(split1_instances))
    assert len(split2_instances) == len(set(split2_instances))
    print(f'desired percentage: {args.split1_percentage}, actual percentage:{len(split1_instances)/len(base_instances)}')
    # sanity check if they are combined, they have the original length again (no overlap)
    combined = []
    combined.extend(split1_instances)
    combined.extend(split2_instances)
    print(f'split1+2 len: {str(len(combined))}')
    print(f'split1+2 set len: {str(len(set(combined)))}')
    assert len(combined) == len(set(combined))
    assert len(combined) == len(base_instances)

    # for each instance in train set: cp to train folder
    for instance in split1_instances:
        shutil.copy(os.path.join(args.instance_folder, instance), os.path.join(args.split1_folder, instance))

    # for each instance in test set: cp to test folder
    for instance in split2_instances:
        shutil.copy(os.path.join(args.instance_folder, instance), os.path.join(args.split2_folder, instance))

if __name__ == "__main__":
    main()