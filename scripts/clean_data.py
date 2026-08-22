def remove_duplicates_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    unique_lines = list(dict.fromkeys(lines))
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(unique_lines)
