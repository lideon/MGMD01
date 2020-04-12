import pandas as pd

file_location = ""
transition_matrix = pd.read_csv(r"C:\Users\.0\OneDrive - University of Toronto\MGMD01\LifetimeTransition.csv", index_col=0, header=0)
segment_matrix = pd.read_csv(r"C:\Users\.0\OneDrive - University of Toronto\MGMD01\LifetimeSegment.csv", index_col=0, header=0)

def next_instances_total(transition_matrix, segment_matrix, number_of_instances):
    ''''''
    data_matrix = segment_matrix[["Number of customers"]]
    for instance in range(1, number_of_instances+1):
        if (instance == 1):
            data_matrix["N + " + str(instance)] = transition(transition_matrix, data_matrix["Number of customers"])
        else:
            data_matrix["N + " + str(instance)] = transition(transition_matrix, data_matrix["N + " + str(instance-1)])
    return data_matrix

def transition(transition_matrix, segment_vector):
    indicies = transition_matrix.index
    return_vector = [0 for i in range(0, len(segment_vector))]
    for index in indicies:
        transition_vector = transition_matrix.loc[index]
        return_vector += (transition_vector*segment_vector.loc[index]).round(0)
    return return_vector



print(transition(transition_matrix, segment_matrix["Number of customers"]))
print(next_instances_total(transition_matrix, segment_matrix, 30))