import os
import random
import shutil
import argparse
import math
import json
def process_instances(instances, src_folder, dest_folder, move=False):
    for instance in instances:
        source = os.path.join(src_folder, instance)
        if move:
            shutil.move(source, dest_folder)
        else:
            shutil.copy(source, dest_folder)
def split(instance_folder, split1_folder, split2_folder, split1_percentage, move=False):
    # get all filenames
    base_instances = [f for f in os.listdir(instance_folder) if f.endswith(".cnf")]
    print(f"Found {str(len(base_instances))} instances to split")

    # get split1_percentage sized subset
    split1_num_instances = math.floor(len(base_instances) * split1_percentage)
    split1_instances = random.sample(base_instances, split1_num_instances)
    split2_instances = []
    for instance in base_instances:
        if instance not in split1_instances:
            split2_instances.append(instance)

    print(f"split1 len: {str(len(split1_instances))}")
    print(f"split2 len: {str(len(split2_instances))}")
    # sanity check if the length are the same of lists and the sets (no duplicates)
    print(f"split1 set len: {str(len(set(split1_instances)))}")
    print(f"split2 set len: {str(len(set(split2_instances)))}")
    assert len(split1_instances) == len(set(split1_instances))
    assert len(split2_instances) == len(set(split2_instances))
    print(
        f"desired percentage: {split1_percentage}, actual percentage:{len(split1_instances) / len(base_instances)}")
    # sanity check if they are combined, they have the original length again (no overlap)
    combined = []
    combined.extend(split1_instances)
    combined.extend(split2_instances)
    print(f"split1+2 len: {str(len(combined))}")
    print(f"split1+2 set len: {str(len(set(combined)))}")
    assert len(combined) == len(set(combined))
    assert len(combined) == len(base_instances)

    # for each instance in the splits, move/cp them
    process_instances(split1_instances, instance_folder, split1_folder, move)
    process_instances(split2_instances, instance_folder, split2_folder, move)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--instance_folder", dest="instance_folder", type=str)
    parser.add_argument("--split1_percentage", dest="split1_percentage", type=float, default=0.5)
    parser.add_argument("--random_seed", dest="random_seed", type=int, default=1)
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    random.seed(1)

    config_folder = os.path.join(os.path.dirname(args.instance_folder),
                                 "algo_config")
    config_training_folder = os.path.join(config_folder, "train")
    config_testing_folder = os.path.join(config_folder, "test")

    selection_folder = os.path.join(os.path.dirname(args.instance_folder),
                                    "algo_selection")
    selection_training_folder = os.path.join(selection_folder, "train")
    selection_testing_folder = os.path.join(selection_folder, "test")

    extract_config_folder = os.path.join(os.path.dirname(args.instance_folder),
                                         "extracted_algo_config")
    extract_config_training_folder = os.path.join(extract_config_folder, "train")
    extract_config_testing_folder = os.path.join(extract_config_folder, "test")

    extract_selection_folder = os.path.join(os.path.dirname(args.instance_folder),
                                            "extracted_algo_selection")
    extract_selection_training_folder = os.path.join(extract_selection_folder, "train")
    extract_selection_testing_folder = os.path.join(extract_selection_folder, "test")

    def create_folders(base, train, test):
        print(f"creating folders:\n"
              f"{base}\n"
              f"{train}\n"
              f"{test}")
        os.mkdir(base)
        os.mkdir(train)
        os.mkdir(test)

    # create the folder structure:
    create_folders(config_folder, config_training_folder, config_testing_folder)
    create_folders(selection_folder, selection_training_folder, selection_testing_folder)
    create_folders(extract_config_folder, extract_config_training_folder, extract_config_testing_folder)
    create_folders(extract_selection_folder, extract_selection_training_folder, extract_selection_testing_folder)

    # split into ac/as folders (copying them)
    split(args.instance_folder, config_folder, selection_folder, 0.5)
    # split ac folders into training/testing (moving them)
    split(config_folder, config_training_folder, config_testing_folder, 0.8, move=True)
    # split as folders into training/testing (moving them)
    split(selection_folder, selection_training_folder, selection_testing_folder, 0.8, move=True)

    from gen_instance_file import create_instance_file
    algo_config_train_file = "algo_config_train_instances.txt"
    algo_config_test_file = "algo_config_test_instances.txt"
    algo_selection_train_file = "algo_selection_train_instances.txt"
    algo_selection_test_file = "algo_selection_test_instances.txt"

    create_instance_file(config_training_folder, algo_config_train_file)
    create_instance_file(config_testing_folder, algo_config_test_file)
    create_instance_file(selection_training_folder, algo_selection_train_file)
    create_instance_file(selection_testing_folder, algo_selection_test_file)

    def create_setup_dict(name, instances_file):
        setup_dict = {
            "name" : f"cpriesne_extract_{name}",
            "executable" :  "/home/guests/cpriesne/copperbench/feature_wrapper.sh",
            "configs" : f"cb_extract_config_{name}.txt",
            "instances" : instances_file,
            "timeout" : 3600,
            "mem_limit" : 250000,
            "request_cpus" : 24,
            "working_dir" : ".",
            "exclusive": True
        }
        with open(f"cb_extract_setup_{name}.json", "w") as setup_file:
            setup_file.write(json.dumps(setup_dict, indent=4))

    create_setup_dict("ac_train", algo_config_train_file)
    create_setup_dict("ac_test", algo_config_train_file)
    create_setup_dict("as_train", algo_selection_train_file)
    create_setup_dict("as_test", algo_selection_train_file)

    def create_extract_config(name, extraction_folder):
        line = f"-extract -ext_folder {extraction_folder}"
        with open(f"cb_extract_config_{name}.txt", "w") as config_file:
            config_file.write(line)

    create_extract_config("ac_train", extract_config_training_folder)
    create_extract_config("ac_test", extract_config_testing_folder)
    create_extract_config("as_train", extract_selection_training_folder)
    create_extract_config("as_test", extract_selection_testing_folder)

if __name__ == "__main__":
    main()