import os
import random
import shutil
import argparse
import math
import json
from gen_instance_file import create_instance_file

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

    return split1_instances, split2_instances

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

    config_to_selection_percentage = 0.5
    train_test_percentage = 0.8
    extraction_folder = "home/guests/cpriesne/instances/extracted"
    # extraction_folder = "/home/ricechrispi/PycharmProjects/copperbench/extracted"

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
    split(args.instance_folder, config_folder, selection_folder, config_to_selection_percentage)
    # split ac folders into training/testing (moving them)
    config_split1, config_split2 = split(config_folder, config_training_folder, config_testing_folder,
                                         train_test_percentage, move=True)
    # split as folders into training/testing (moving them)
    selection_split1, selection_split2 = split(selection_folder, selection_training_folder, selection_testing_folder,
                                               train_test_percentage, move=True)


    extracted_instances = set([f for f in os.listdir(extraction_folder) if f.endswith(".cnf")])
    print(f"Found {str(len(extracted_instances))} extracted instances")

    # runs in O^2, but this should be good enough
    def matching_instances(target_instances, corresponding_split):
        split_starts = [s.split(".cnf")[0] for s in corresponding_split]
        matches = []
        for instance in target_instances:
            for split_start in split_starts:
                if instance.startswith(split_start):
                    matches.append(instance)
        return matches

    extracted_config_train = matching_instances(extracted_instances, config_split1)
    extracted_instances = extracted_instances - set(extracted_config_train)
    print(f"extracted_config_train: {extracted_config_train}")

    extracted_config_test = matching_instances(extracted_instances, config_split2)
    extracted_instances = extracted_instances - set(extracted_config_test)
    print(f"extracted_config_test: {extracted_config_test}")

    extracted_selection_train = matching_instances(extracted_instances, selection_split1)
    extracted_instances = extracted_instances - set(extracted_selection_train)
    print(f"extracted_selection_train: {extracted_selection_train}")

    extracted_selection_test = matching_instances(extracted_instances, selection_split2)
    extracted_instances = extracted_instances - set(extracted_selection_test)
    print(f"extracted_selection_test: {extracted_selection_test}")

    print(f"len of extracted_instances should be 0. it is: {len(extracted_instances)}")
    print(f"extracted instances: {str(extracted_instances)}")

    # now copy them into respective folders:
    process_instances(extracted_config_train, extraction_folder, extract_config_training_folder)
    process_instances(extracted_config_test, extraction_folder, extract_config_testing_folder)
    process_instances(extracted_selection_train, extraction_folder, extract_selection_training_folder)
    process_instances(extracted_selection_test, extraction_folder, extract_selection_testing_folder)


    # create instance files for all created folder
    all_extracted_instances_file = "all_extracted_instances.txt"
    create_instance_file(extraction_folder, all_extracted_instances_file)

    extracted_algo_config_train_file = "extracted_algo_config_train_instances.txt"
    extracted_algo_config_test_file = "extracted_algo_config_test_instances.txt"
    extracted_algo_selection_train_file = "extracted_algo_selection_train_instances.txt"
    extracted_algo_selection_test_file = "extracted_algo_selection_test_instances.txt"

    create_instance_file(extract_config_training_folder, extracted_algo_config_train_file)
    create_instance_file(extract_config_testing_folder, extracted_algo_config_test_file)
    create_instance_file(extract_selection_training_folder, extracted_algo_selection_train_file)
    create_instance_file(extract_selection_testing_folder, extracted_algo_selection_test_file)

    raw_algo_config_train_file = "raw_algo_config_train_instances.txt"
    raw_algo_config_test_file = "raw_algo_config_test_instances.txt"
    raw_algo_selection_train_file = "raw_algo_selection_train_instances.txt"
    raw_algo_selection_test_file = "raw_algo_selection_test_instances.txt"

    create_instance_file(config_training_folder, raw_algo_config_train_file)
    create_instance_file(config_testing_folder, raw_algo_config_test_file)
    create_instance_file(selection_training_folder, raw_algo_selection_train_file)
    create_instance_file(selection_testing_folder, raw_algo_selection_test_file)

    print("config stats:")
    print_statistics(train_test_percentage,
                     config_training_folder, config_testing_folder,
                     extract_config_training_folder, extract_config_testing_folder)

    print("selection stats:")
    print_statistics(train_test_percentage,
                     selection_training_folder, selection_testing_folder,
                     extract_selection_training_folder, extract_selection_testing_folder)

def print_statistics(train_test_percentage, raw_train, raw_test, extracted_train, extracted_test):

    def num_of_files(folder):
        return len([f for f in os.listdir(folder) if f.endswith(".cnf")])

    num_raw_train = num_of_files(raw_train)
    num_raw_test = num_of_files(raw_test)
    print(f"raw train: {num_raw_train}, raw test: {num_raw_test}")
    actual_percentage = num_raw_train / (num_raw_train + num_raw_test)
    print(f"train percentage: {actual_percentage}, wanted percentage: {train_test_percentage}")

    num_extracted_train = num_of_files(extracted_train)
    num_extracted_test = num_of_files(extracted_test)
    print(f"ex train: {num_extracted_train}, ex test: {num_extracted_test}")
    actual_percentage = num_extracted_train / (num_extracted_train + num_extracted_test)
    print(f"train percentage: {actual_percentage}, wanted percentage: {train_test_percentage}")


if __name__ == "__main__":
    main()