import pandas as pd

transition_matrix = pd.read_csv(r"C:\Users\.0\OneDrive - University of Toronto\MGMD01\Models\Lifetime Valuation\LifetimeTransition.csv", index_col=0, header=0)
segment_matrix = pd.read_csv(r"C:\Users\.0\OneDrive - University of Toronto\MGMD01\Models\Lifetime Valuation\LifetimeSegment.csv", index_col=0, header=0)

def next_instances_total(transition_matrix, segment_matrix, number_of_instances, rate):
    '''Returns a new Dataframe that has instances N+0 ... N+number of instances'''
    margin = segment_matrix["Gross margins"]
    data_matrix = segment_matrix[["Number of customers"]].copy(deep = True)
    data_matrix.rename(columns={"Number of customers": "N + 0"}, inplace=True)
    data_matrix.append(pd.Series(name='Cumulative Margin'))
    data_matrix.at['Cumulative Margin', 'N + 0'] = 0
    for instance in range(1, number_of_instances+1):
        column = "N + " + str(instance)
        data_matrix[column] = transition(transition_matrix, data_matrix["N + " + str(instance-1)][:-1], 2)
        data_matrix.at["Cumulative Margin", column] = round(data_matrix.at["Cumulative Margin", "N + " + str(instance-1)] + present_value((data_matrix[column][:-1]*margin).sum(), rate, instance), 2)
    return data_matrix

def transition(transition_matrix, segment_vector, digits):
    '''Given a transition_matrix and segment vector, return next instances segment_vector'''
    indicies = transition_matrix.index
    return_vector = [0 for i in range(0, len(segment_vector))]
    for index in indicies:
        transition_vector = transition_matrix.loc[index]
        return_vector += (transition_vector*segment_vector.loc[index]).round(digits)
    return return_vector

def present_value(value, rate, period):
    return value/((1+rate)**period)

def lifetime_value(transition_matrix, segment, margin, rate):
    '''Returns a new Dataframe that has instances N+0 ... N+K where K
       Is the first instance of the transition vector being all 0'''
    data_matrix = pd.DataFrame(segment, columns=["N + 0"])
    data_matrix.append(pd.Series(name='Cumulative Margin'))
    data_matrix.at['Cumulative Margin', 'N + 0'] = 0
    data_matrix.rename(columns={"Number of customers": "N + 0"}, inplace=True)
    last_all_0 = False
    empty_vector = [0 for i in range(0, len(segment)-1)]
    instance = 1
    while(not last_all_0):
        column = "N + " + str(instance)
        data_matrix[column] = transition(transition_matrix, data_matrix["N + " + str(instance-1)][:-1], 4)
        data_matrix.at["Cumulative Margin", column] = round(data_matrix.at["Cumulative Margin", "N + " + str(instance-1)] + present_value((data_matrix[column][:-1]*margin).sum(), rate, instance), 2)
        instance += 1
        if (data_matrix[column].to_list()[:-2] == empty_vector or data_matrix[column].to_list()[-2] >= 1):
            last_all_0 = True
    return data_matrix

n = 20
print("Lifetime Value Next {} Instances".format(n))
print(next_instances_total(transition_matrix, segment_matrix, n, 0.15))
print("Lifetime Value by Segment")
lifetime_value_series = pd.Series()
for count, segment in enumerate(segment_matrix.index[:-1]):
    segment_vector = [0 for i in range (0, segment_matrix.shape[0])]
    segment_vector[count] = 1
    segment_vector = pd.Series(segment_vector, index = segment_matrix.index)
    lifetime_value_df = lifetime_value(transition_matrix, segment_vector, segment_matrix["Gross margins"], 0.15)
    print(lifetime_value_df)
    print("")
    lifetime_value_series[segment] = lifetime_value_df.iloc[-1,-1]

print("Lifetime Value of Each Segment:")
print(lifetime_value_series)

