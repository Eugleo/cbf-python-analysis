import csv


def write_dicts_to_file(dicts, path):
    with open(path, 'w') as f:
        columns = list(dicts[0].keys())
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(dicts)
