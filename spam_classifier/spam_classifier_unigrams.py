import spam_classifier.settings as settings
from spam_classifier.es import Es
import timeit
import spam_classifier.util as util
from scipy.sparse import dok_matrix
import numpy as np
import spam_classifier.ml_models as ml_models

class Spam_Classifier_Unigrams():

    es = None

    unigrams_dict = {}

    def __init__(self):
        print(" In the constructor")
        self.es = Es(settings.hosts, settings.index_name, settings.index_type)

    def __load_unigram(self, create_unigrams_dict):
        ## Save the unigrams_dict
        if (create_unigrams_dict == True):
            self.unigrams_dict = self.es.get_all_vocabulary()
            util.dump_pickle_file(settings.unigram_filename, self.unigrams_dict)
        else:
            self.unigrams_dict = util.load_pickle_file(settings.unigram_filename)

    def __generate_feature_matrix(self, label_dict):
        start_calculation = timeit.default_timer()
        feature_sparse_matrix = dok_matrix((len(label_dict), len(self.unigrams_dict)), dtype=np.float32)
        count = 0
        ## Loop over all the documents
        for id in label_dict.keys():
            if (count % 1000 == 0):
                print("Generating features for {} documents done".format(count))
            doc_term_vector = self.es.term_vectors(id)
            if "body" in doc_term_vector["term_vectors"] and "terms" in doc_term_vector["term_vectors"]["body"]:
                tokens = doc_term_vector["term_vectors"]["body"]["terms"].keys()
                for token in tokens:
                    ## Get the token number
                    token_number = self.unigrams_dict[token]
                    tf = doc_term_vector["term_vectors"]["body"]["terms"][token]["term_freq"]
                    feature_sparse_matrix[count, token_number - 1] = tf
            count = count + 1
        stop_calculation = timeit.default_timer()
        print("Time taken to generate feature matrix: " + str(stop_calculation - start_calculation))
        return(feature_sparse_matrix)

    def __get_feature_matrix(self):
        start_calculation = timeit.default_timer()

        ## Label dict
        label_train_dict = {}
        label_test_dict = {}

        ## Get all documents and get the train and test list
        id_list, filename_list, label_list, split_list = self.es.get_all_documents()
        label_list = [1 if x == "spam" else 0 for x in label_list]

        for i in range(len(split_list)):
            if (split_list[i] == 'train'):
                label_train_dict[id_list[i]] = label_list[i]
            else:
                label_test_dict[id_list[i]] = label_list[i]

        print("Generating feature matrix for train documents")
        feature_sparse_train_matrix = self.__generate_feature_matrix(label_train_dict)
        print("Generating feature matrix for test documents")
        feature_sparse_test_matrix = self.__generate_feature_matrix(label_test_dict)

        train_csr = feature_sparse_train_matrix.tocsr()
        train_labels = list(label_train_dict.values())
        test_csr = feature_sparse_test_matrix.tocsr()
        test_labels = list(label_test_dict.values())

        stop_calculation = timeit.default_timer()
        print("Time taken to generate feature matrix: " + str(stop_calculation - start_calculation))

        return(train_csr, train_labels, test_csr, test_labels)

    def __classification(self, train_df, train_labels, test_df, test_labels):
        logistic_regression_accuracy = ml_models.logistic_regression(train_df, train_labels, test_df, test_labels)
        print("Logistic Regression Accuracy {}".format(logistic_regression_accuracy))
        decision_tree_accuracy = ml_models.decision_tree(train_df, train_labels, test_df, test_labels)
        print("Decision Tree Accuracy {}".format(decision_tree_accuracy))
        accuracy = max(logistic_regression_accuracy, decision_tree_accuracy)
        return (accuracy)

    def run(self, create_unigrams_dict = False):
        start_calculation = timeit.default_timer()

        ## Load unigram
        self.__load_unigram(create_unigrams_dict)

        ## Generate feature matrix
        train_csr, train_labels, test_csr, test_labels = self.__get_feature_matrix()

        ## Run the classification algorithm
        accuracy = self.__classification(train_csr, train_labels, test_csr, test_labels)

        print("Accuracy is {}".format(accuracy))

        stop_calculation = timeit.default_timer()
        print("Time taken to run spam classifier userwords: " + str(stop_calculation - start_calculation))


