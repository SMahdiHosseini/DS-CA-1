# complete undirected graph
for number_of_nodes in range(5, 50, 5):
    input_file = open(f'./inputs/complete_{number_of_nodes}.in', 'w')
    print(f'{number_of_nodes}', file=input_file)
    for i in range(1, number_of_nodes + 1):
        for j in range(i + 1, number_of_nodes + 1):
            print(f'{i} {j} {1}', file=input_file)

# Undirected Ring
for number_of_nodes in range(5, 50, 5):
    input_file = open(f'./inputs/ring_{number_of_nodes}.in', 'w')
    print(f'{number_of_nodes}', file=input_file)
    for i in range(1, number_of_nodes + 1, 2):
        if i != number_of_nodes:
            print(f'{i} {i+1} {1}', file=input_file)
        else:
            print(f'{i} {1} {1}', file=input_file)

        if i != 1:
            print(f'{i} {i-1} {1}', file=input_file)
        else:
            print(f'{i} {number_of_nodes} {1}', file=input_file)

# Star graph
for number_of_nodes in range(5, 50, 5):
    input_file = open(f'./inputs/star_{number_of_nodes}.in', 'w')
    print(f'{number_of_nodes}', file=input_file)
    for i in range(2, number_of_nodes + 1):
        print(f'{1} {i} {1}', file=input_file)

# path graph
for number_of_nodes in range(5, 50, 5):
    input_file = open(f'./inputs/path_{number_of_nodes}.in', 'w')
    print(f'{number_of_nodes}', file=input_file)
    for i in range(1, number_of_nodes + 1):
        if i != number_of_nodes:
            print(f'{i} {i+1} {1}', file=input_file)