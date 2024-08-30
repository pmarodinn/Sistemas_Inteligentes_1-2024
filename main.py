import sys
import os

from manager import Manager
from vs.environment import Env
from vs.constants import DATA
from explorer import Explorer
from rescuer import Rescuer


def main(data_folder_name):

    # Set the path to config files and data files for the environment
    current_folder = os.path.abspath(os.getcwd())
    data_folder = os.path.abspath(os.path.join(current_folder, data_folder_name))

    # Instantiate the environment
    env = Env(data_folder)

    # config files for the agents
    rescuer_file = os.path.join(data_folder, "rescuer_config.txt")
    explorer_file0 = os.path.join(data_folder, "explorer_config0.txt")
    explorer_file1 = os.path.join(data_folder, "explorer_config1.txt")
    explorer_file2 = os.path.join(data_folder, "explorer_config2.txt")
    explorer_file3 = os.path.join(data_folder, "explorer_config3.txt")

    # Instantiate agents rescuer and explorer
    resc0 = Rescuer(env, rescuer_file)
    resc1 = Rescuer(env, rescuer_file)
    resc2 = Rescuer(env, rescuer_file)
    resc3 = Rescuer(env, rescuer_file)

    manager = Manager([resc0, resc1, resc2, resc3])

    # Explorer needs to know rescuer to send the map
    # that's why rescuer is instatiated before
    exp0 = Explorer(env, explorer_file0, manager)
    exp1 = Explorer(env, explorer_file1, manager)
    exp2 = Explorer(env, explorer_file2, manager)
    exp3 = Explorer(env, explorer_file3, manager)

    # creates a new map by uniting all the agents maps
    # victims = union_victims([exp0.victims, exp1.victims, exp2.victims, exp3.victims])

    # Run the environment simulator
    env.run()


if __name__ == "__main__":
    """To get data from a different folder than the default called data
    pass it by the argument line"""

    if len(sys.argv) > 1:
        data_folder_name = sys.argv[1]
    else:
        data_folder_name = os.path.join("datasets", f"data_{DATA.SCENARIO}")

    main(data_folder_name)
