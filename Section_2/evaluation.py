import pathlib

complete_data_dict = dict([(i, []) for i in range(5, 50, 5)])
path_data_dict = dict([(i, []) for i in range(5, 50, 5)])
ring_data_dict = dict([(i, []) for i in range(5, 50, 5)])
star_data_dict = dict([(i, []) for i in range(5, 50, 5)])
others_data_dict = dict([(i, []) for i in [1, 2, 3, 4]])


def messages_of_node(file):
    f = open(file)
    return int(f.readlines()[-1].split()[-1])


def add_new_data(logs_directory):
    file_cat = str(logs_directory).split('.')[0].split('/')[-1].split('_')

    total_messsages = 0
    for file in pathlib.Path(logs_directory).glob('*'):
        if str(file).split('.')[2] == "stdout":
            total_messsages += messages_of_node(file)

    if file_cat[0] == 'complete':
        complete_data_dict[int(file_cat[1])].append(total_messsages)

    if file_cat[0] == 'path':
        path_data_dict[int(file_cat[1])].append(total_messsages)

    if file_cat[0] == 'ring':
        ring_data_dict[int(file_cat[1])].append(total_messsages)

    if file_cat[0] == 'star':
        star_data_dict[int(file_cat[1])].append(total_messsages)

    if file_cat[0] == 'input':
        others_data_dict[int(file_cat[1])].append(total_messsages)


# message calculation
output_dir = "output/inputs"
for directory in pathlib.Path(output_dir).glob('*'):
    add_new_data(str(directory) + "/logs")


print(complete_data_dict)
print(path_data_dict)
print(ring_data_dict)
print(star_data_dict)
print(others_data_dict)
