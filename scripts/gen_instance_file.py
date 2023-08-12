import os
import argparse

def create_instance_file(instance_folder, output_file):
    lines = []
    prefix = "-i"
    for file in os.listdir(instance_folder):
        filename = os.fsdecode(file)
        if filename.endswith(".cnf"):
            line = f"{prefix} {os.path.join(instance_folder, filename)}\n"
            lines.append(line)

    with open(output_file, "w") as out_file:
        out_file.writelines(lines)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--instance_folder", dest="instance_folder", type=str)
    parser.add_argument("--output_file", dest="output_file", type=str, default="instances.txt")
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    create_instance_file(args.instance_folder, args.output_file)

if __name__ == "__main__":
    main()