from multiprocessing import Pool
from concurrent.futures import ProcessPoolExecutor
import pandas as pd
import numpy as np


def process_dataframe(seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({"value": rng.normal(loc=50, scale=10, size=1000)})
    df["normalized"] = (df["value"] - df["value"].mean()) / df["value"].std()
    df["source"] = seed
    return df


if __name__ == '__main__':
    seeds = list(range(8))

    with Pool(processes=4) as pool:
        results = pool.map(process_dataframe, seeds)

    final_df = pd.concat(results, ignore_index=True)
    print(final_df.groupby("source")["normalized"].mean())

    with ProcessPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(process_dataframe, seeds))
    final_df2 = pd.concat(results, ignore_index=True)
    print(final_df2.groupby("source")["normalized"].mean())

    final_df2 = pd.concat(results, ignore_index=True)
    print(f"\nРезультаты совпадают: {final_df.equals(final_df2)}")
