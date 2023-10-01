import argparse
import pandas as pd

def create_combined_file(feature_file, performance_file, combined_file):
    features_df = pd.read_csv(feature_file)
    features_df = features_df.set_index("instance_name")
    performance_df = pd.read_csv(performance_file)
    performance_df = performance_df.set_index("instance")
    assert features_df.index.equals(performance_df.index)

    train_y = performance_df.idxmin(axis=1)
    features_df["label"] = train_y
    features_df.to_csv(combined_file)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--feature_file", dest="feature_file", type=str, default="features.csv")
    parser.add_argument("--performance_file", dest="performance_file", type=str, default="performance_summary.csv")
    parser.add_argument("--combined_file", dest="combined_file", type=str, default="data.csv")
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    create_combined_file(args.feature_file, args.performance_file, args.combined_file)

if __name__ == "__main__":
    main()