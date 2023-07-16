import os
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--instance_folder", dest="instance_folder", type=str)
    parser.add_argument("--output_file", dest="output_file", type=str, default="instances.txt")
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    lines = []
    prefix = "-i"
    for file in os.listdir(args.instance_folder):
        filename = os.fsdecode(file)
        if filename.endswith(".cnf"):
            line = f"{prefix} {os.path.join(args.instance_folder, filename)}\n"
            lines.append(line)

    with open(args.output_file, "w") as out_file:
        out_file.writelines(lines)

if __name__ == "__main__":
    main()