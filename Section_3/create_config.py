import random
# complete undirected graph
for number_of_nodes in range(5, 50, 5):
    input_file = open(f'./configs/complete_{number_of_nodes}.in.conf', 'w')
    # print(f'{number_of_nodes}', file=input_file)
    for i in range(1, number_of_nodes + 1):
        ptiority = random.choice([1, 2, 3])
        print(f'{i}: {str(ptiority)}', file=input_file)
