import json
import os
import argparse

import numpy as np
import pandas as pd


def validate_models(models_df):
    columns = models_df.columns
    for instance in models_df.index:
        models = None
        for solver in columns:
            if pd.isna(models_df[solver][instance]):
                continue
            elif models is None:
                models = models_df[solver][instance]
            elif models_df[solver][instance] != models:
                print(f"different model values found! instance: {instance}")


def validate_performance(performance_df):
    if performance_df.isnull().values.any():
        print("performance file contains NaNs!")


def get_instances(instance_folder):
    instances = []
    for file in os.listdir(instance_folder):
        filename = os.fsdecode(file)
        if filename.endswith(".cnf"):
            instances.append(filename)
    return instances


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--instance_folder", dest="instance_folder")
    parser.add_argument("--input_performance_file", dest="input_performance_file", type=str)
    parser.add_argument("--output_summary_file", dest="output_summary_file", default="performance_summary.csv", type=str)
    parser.add_argument("--output_models_file", dest="output_models_file", default="model_counts.csv", type=str)
    parser.add_argument("--crash_multiplier", dest="crash_multiplier", default=10) # PAR10
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    instance_names = get_instances(args.instance_folder)

    performance_df = pd.DataFrame(instance_names, columns=["instance"])
    performance_df = performance_df.set_index("instance")

    models_df = pd.DataFrame(instance_names, columns=["instance"])
    models_df = models_df.set_index("instance")

    with open(args.input_performance_file, "r") as performance_file:
        input_files = json.load(performance_file)

    for solver_name, filename in input_files.items():

        solver_df = pd.read_csv(filename)
        performance_df[solver_name] = np.nan
        models_df[solver_name] = np.nan

        for name in instance_names:
            if name not in set(solver_df["instance"]):
                raise ValueError(f"Instance {name} is not in the performance file {filename}")
            row = solver_df.loc[solver_df["instance"] == name]

            retcode = row.iloc[0]["retcode"]
            # cpu_user_time = row.iloc[0]["cpu_user_time"]
            # cpu_total_time = row.iloc[0]["cpu_total_time"]
            real_time = row.iloc[0]["real_time"]
            count = row.iloc[0]["models"]
            timeout = row.iloc[0]["timeout"]
            verdict = row.iloc[0]["verdict"]

            models_df.at[name, solver_name] = count

            if verdict == "OK":
                performance_df.at[name, solver_name] = real_time
            elif verdict in ["TIMEOUT", "MEMOUT", "CRASH"]:
                performance_df.at[name, solver_name] = timeout * args.crash_multiplier
            else:
                raise ValueError(f"Not supposed to happen! retcode: {retcode}, real_time: {real_time}, verdict: {verdict}")

    validate_performance(performance_df)
    validate_models(models_df)

    # instance name, solver1, solver2, ...
    # name1.cnf,    5,  1, ..
    # name2.cnf,    3,  8, ..
    performance_df.to_csv(args.output_summary_file, sep=",")

    # instance name, solver1, solver2, ...
    # name1.cnf,    5,  5, ..
    # name2.cnf,    2,  2, ..
    models_df.to_csv(args.output_models_file, sep=",")


if __name__ == "__main__":
    main()
