import pathlib
import matplotlib.pyplot as plt
import numpy as np
plt.style.use('ggplot')
plt.rcParams['figure.figsize'] = (15, 10)
plt.rcParams.update({
    "lines.color": "black",
    "patch.edgecolor": "black",
    "text.color": "black",
    "axes.facecolor": "white",
    "axes.edgecolor": "black",
    "axes.labelcolor": "black",
    "xtick.color": "black",
    "ytick.color": "black",
    "grid.color": "gray",
    "figure.facecolor": "white",
    "figure.edgecolor": "white",
    "savefig.facecolor": "white",
    "savefig.edgecolor": "white",
    "font.size": 25})

complete_data_dict = dict([(i, []) for i in range(5, 50, 5)])


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


def construct_plot(data, name):
    plt.plot([i for i in range(5, 50, 5)], [np.average(data[key]) for key in data],
             label=name, linewidth=4)

    plt.xlabel("number of nodes(network size)")
    plt.ylabel("average number of messages")
    # plt.show()


def show_individual():
    construct_plot(complete_data_dict, "complete graph")
    plt.title("complete graph message analyse")
    plt.show()


def save_data_into_file():
    file = open("./results/results.txt", 'w')

    file.write("complete graph: ")
    file.write(str(complete_data_dict) + "\n")


# message calculation
output_dir = "output/inputs"
for directory in pathlib.Path(output_dir).glob('*'):
    add_new_data(str(directory) + "/logs")

# showing data
show_individual()

# save to file
save_data_into_file()
