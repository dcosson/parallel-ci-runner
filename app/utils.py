from glob import glob


def split_files_into_groups(num_groups, glob_pattern, shuffle_files=False):
    files = glob(glob_pattern, recursive=True)
    result = [[] for _ in range(num_groups)]
    for i, val in enumerate(files):
        result[i % num_groups].append(val)
    return result
