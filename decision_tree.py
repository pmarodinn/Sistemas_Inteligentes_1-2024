import pandas as pd
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split


# ============================== FUNCTIONS =========================================== #

def calculate_mae(leafs, train_x, val_x, train_y, val_y):
    model = DecisionTreeRegressor(max_leaf_nodes = leafs)
    model.fit(train_x, train_y)

    val_predict = model.predict(val_x)

    return mean_absolute_error(val_y, val_predict)

# ============================== END FUNCTIONS ======================================= #


data_path = "./datasets/data_4000v/env_vital_signals.csv"

victim_data = pd.read_csv(data_path, header=None)

columns_len = len(victim_data.columns)     

target = victim_data[columns_len - 2]

features_data = victim_data[[1,2,3,4,5]]
print(target)
print(features_data)

train_feat, val_feat, train_target, val_target = train_test_split(features_data, target, random_state = 1)

max_leafs = [5, 25, 50, 100, 250, 500]

smallest_mae = calculate_mae(max_leafs[0], train_feat, val_feat, train_target, val_target)
best_tree_size = max_leafs[0]

for i in range(1, len(max_leafs)):
    mae = calculate_mae(max_leafs[i], train_feat, val_feat, train_target, val_target)
    print(f"Max leaf nodes: {max_leafs[i]} \t\t Mean Absolute Error - MAE: {mae}")

    if mae < smallest_mae:
        smallest_mae = mae
        best_tree_size = max_leafs[i]


best_model = DecisionTreeRegressor(max_leaf_nodes= best_tree_size)

best_model.fit(features_data, target)


