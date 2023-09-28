import os
import argparse
import datetime
import tarfile
import json
import re

import pandas as pd


def update_data(data, file_name, reg_expressions):
    with open(file_name, "r") as file:
        matches = extract_regex(file, reg_expressions)
        for key, value in matches.items():
            data[key] = value


def extract_regex(stream, reg_expressions):
    found_matches = {}
    for line in stream.readlines():
        for key, reg_expression in reg_expressions.items():
            match = reg_expression.match(line)
            if match:
                found_matches[key] = match.group(1)
    return found_matches


# TODO: still missing:  make multiple runs work, i.e. save run as column, have an average
#                       sat/unsat/unknown?
#                       log 10 estimate!! most notably nesthdb gives this
#                           -> maybe make this part of benchmark_runner.py?
#                       add path/timestamp to output files
#                       also: a bit of doc here!
def create_csv(config_folder, config_name, instances):
    algo_df = pd.DataFrame(columns=["instance",
                                    "instance_bench_number",
                                    "algo",
                                    "pfile",
                                    "subsolver",
                                    "retcode",
                                    "models",
                                    "date",
                                    "node",
                                    "cpus_allowed",
                                    "timeout",
                                    "real_time",
                                    "cpu_total_time",
                                    "cpu_user_time",
                                    "cpu_sys_time",
                                    "memory_limit",
                                    "max_virtual_memory",
                                    "max_memory",
                                    "verdict",
                                    ]
                           )

    for instance_folder, instance_name in instances.items():
        run_folder = os.path.join(config_folder, instance_folder)
        run_folder = os.path.join(run_folder, "run1")
        data = {
            "instance": instance_name,
            "instance_bench_number": instance_folder,
            "algo": config_name,
            "pfile": None,
            "subsolver": None,
            "retcode": None,
            "models": None,
            "date": None,
            "node": None,
            "cpus_allowed": None,
            "timeout": None,
            "real_time": None,
            "cpu_total_time": None,
            "cpu_user_time": None,
            "cpu_sys_time": None,
            "memory_limit": None,
            "max_virtual_memory": None,
            "max_memory": None,
            "verdict": "UNKNOWN",
        }

        # stdout.log: pfile, subsolver (if any is used), retcode (most importantly if solver crashed/timeouted)
        stdout_regs = {"pfile": re.compile(r"c\s+o\s+ENV\s+PFILE\s+=\s+(\w+)"),
                       "subsolver": re.compile(r"c\s+o\s+ENV\s+SUBSOLVER\s+=\s+(\w+)"),
                       "retcode": re.compile(
                           r"c\s+o\s+benchmark_wrapper:\s+Solver\s+finished\s+with\s+exit\s+code=(\w+)"), }
        update_data(data, os.path.join(run_folder, "stdout.log"), stdout_regs)

        # stderr.log: models and retcode (if finished)
        stderr_regs = {"models": re.compile(r".*Benchmarking\s+over\.\s+models:\s*(\w+)"),
                       "retcode": re.compile(r".*Benchmarking\s+over\.\s+models:\w+,\s+returncode:(\w+)"), }
        update_data(data, os.path.join(run_folder, "stderr.log"), stderr_regs)

        # node_info.log: node and cpu_allowed
        node_info_regs = {"date": re.compile(r"Date:\s+(.*)"),
                          "node": re.compile(r"Node:\s+(\w+)"),
                          "cpus_allowed": re.compile(r"Cpus_allowed:\s+(\w+)"), }
        update_data(data, os.path.join(run_folder, "node_info.log"), node_info_regs)

        # perf.log
        # cache stuff, seconds time elapsed by user/sys
        # -> does not seem useful

        # runsolver.log: TODO?
        # Child status: 0
        # CPU usage (%): 96.5996
        runsolver_regs = {"real_time": re.compile(r"Real time \(s\):\s+(\w+)"),
                          "cpu_total_time": re.compile(r"CPU time \(s\):\s+(\w+)"),
                          "cpu_user_time": re.compile(r"CPU user time \(s\):\s+(\w+)"),
                          "cpu_sys_time": re.compile(r"CPU system time \(s\):\s+(\w+)"),
                          "timeout": re.compile(
                              r"Enforcing wall clock limit \(soft limit, will send SIGTERM then SIGKILL\):\s+(\w+)"),
                          "memory_limit": re.compile(
                              r"Enforcing VSIZE limit \(hard limit, stack expansion will fail with SIGSEGV, brk\(\) and mmap\(\) will return ENOMEM\):\s+(\w+)"),
                          "max_virtual_memory": re.compile(
                              r"Max\. virtual memory \(cumulated for all children\) \(KiB\):\s+(\w+)"),
                          "max_memory": re.compile(r"Max\. memory \(cumulated for all children\) \(KiB\):\s+(\w+)"),
                          }
        update_data(data, os.path.join(run_folder, "runsolver.log"), runsolver_regs)

        if data["real_time"] is not None and data["timeout"] is not None \
                and int(data["real_time"]) >= int(data["timeout"]):
            data["verdict"] = "TIMEOUT"

        elif data["max_virtual_memory"] is not None \
                and data["max_memory"] is not None \
                and data["memory_limit"] is not None \
                and (int(data["max_virtual_memory"]) >= int(data["memory_limit"])) or (
                int(data["max_memory"]) >= int(data["memory_limit"])):
            data["verdict"] = "MEMOUT"

        elif data["retcode"] is None or int(data["retcode"]) != 0:
            data["verdict"] = "CRASH"
        else:
            data["verdict"] = "OK"  # probably

        print(json.dumps(data, indent=2))
        algo_df.loc[len(algo_df)] = data

    algo_df = algo_df.set_index("instance")
    # save it to a csv file
    algo_df.to_csv(f"{config_name}.csv")


def parse_metadata(base_folder):
    metadata_path = os.path.join(base_folder, "metadata.json")

    # read in json
    with open(metadata_path, "r") as metadata_file:
        metadata = json.load(metadata_file)

    instances = metadata["instances"]
    new_instances = {}
    for key, value in instances.items():
        new_instances[key] = os.path.basename(value.split(" ")[-1])

    configs = metadata["configs"]
    new_configs = {}
    for key, value in configs.items():
        config_parts = value.split()
        name_parts = []
        for part in config_parts:
            if '/' not in part:
                part = part.split(".")[0]  # get rid of file extensions
                part = part.split("-")[-1]  # get rid of -- and - prefixes
                name_parts.append(part)
        new_name = "_".join(name_parts)
        new_configs[key] = new_name

    metadata["instances"] = new_instances
    metadata["configs"] = new_configs
    return metadata


def extract(archive, output_folder):
    # check if output_folder exists
    if os.path.exists(output_folder):
        # Note: this is "technically" not robust against multiple files having the same timestamp,
        #           but this is highly unlikely.
        print("Output folder already exists, skipping extraction")
    else:
        # extract archive into output folder
        archive_file = tarfile.open(archive)
        archive_file.extractall(output_folder)
        archive_file.close()

    # search for the base_folder, e.g. cpriesne_output
    for file in os.listdir(output_folder):
        base_folder = os.path.join(output_folder, file)
        if os.path.isdir(base_folder):
            return base_folder
    raise ValueError("Could not find the base folder in extracted archive")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", dest="archive", type=str)
    args = parser.parse_args()
    return args


def main():
    args = parse_args()

    creation_time = datetime.datetime.fromtimestamp(os.path.getctime(args.archive))
    timestamp = creation_time.strftime("%Y-%m-%d-%Hh-%Mm-%Ss")
    output_folder = f"results_{timestamp}"

    base_folder = extract(args.archive, output_folder)

    metadata = parse_metadata(base_folder)
    print(json.dumps(metadata, indent=2))

    for config in metadata["configs"].keys():
        create_csv(config_folder=os.path.join(base_folder, config),
                   config_name=metadata["configs"][config],
                   instances=metadata["instances"])


if __name__ == "__main__":
    main()
