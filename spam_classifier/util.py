import pickle

def dump_pickle_file(filename, dict):
    file = open(filename, 'wb')
    pickle.dump(dict, file, protocol=pickle.HIGHEST_PROTOCOL)
    file.close()

def load_pickle_file(filename):
    file = open(filename, 'rb')
    dict = pickle.load(file)
    file.close()
    return(dict)