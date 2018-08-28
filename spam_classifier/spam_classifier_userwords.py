from spam_classifier.spamwords import Spamwords
import spam_classifier.settings as settings
from spam_classifier.es import Es
import timeit
import pandas as pd
import spam_classifier.ml_models as ml_models

class Spam_Classifier_Userwords():

    spamwords = None

    def __init__(self, sapmwords_filename):
        spamwords = Spamwords(sapmwords_filename)
        self.spamwords = spamwords.spamwords

    def __generate_feature_matrix(self):

        feature_matrix = pd.DataFrame()

        es = Es(settings.hosts, settings.index_name, settings.index_type)
        doc_count = es.count()

        ## Populate the matrix
        print("Total number of features: {}".format(len(self.spamwords)))
        for i in range(len(self.spamwords)):
            spamword = self.spamwords[i]
            result_id_list, result_score_list = es.get_documents_for_query(spamword)

            if(len(result_id_list) == 0):
                print("No documents are present for spamword {}".format(spamword))

            result_list = [0] * doc_count
            for i in range(len(result_id_list)):
                result_list[int(result_id_list[i]) - 1] = result_score_list[i]

            feature_matrix[spamword] = result_list

            ## Print purpose
            if (i % 10 == 0):
                print("Feature matrix for {} words done".format(i))

        print(feature_matrix.index.values)
        ## Get the train and test list
        id_list, filename_list, label_list, split_list = es.get_all_documents()
        label_list = [1 if x == "spam" else 0 for x in label_list]

        ## Divide into train-test set
        train_row_ids = []
        test_row_ids = []
        train_index_list = []
        train_labels = []
        test_index_list = []
        test_labels = []
        for i in range(len(split_list)):
            if(split_list[i] == 'train'):
                train_row_ids.append(int(id_list[i])-1)
                train_index_list.append(filename_list[i])
                train_labels.append(label_list[i])
            else:
                test_row_ids.append(int(id_list[i])-1)
                test_index_list.append(filename_list[i])
                test_labels.append(label_list[i])

        print("Number of documents in train: {}".format(len(train_row_ids)))
        print("Number of documents in test: {}".format(len(test_row_ids)))

        ## Divide the feature_matrix into train and test
        train_feature_matrix = feature_matrix.loc[train_row_ids, :]
        train_feature_matrix.index = train_index_list
        test_feature_matrix = feature_matrix.loc[test_row_ids, :]
        test_feature_matrix.index = test_index_list

        print("Shape of train feature matrix: {}".format(train_feature_matrix.shape))
        print("Shape of test feature matrix: {}".format(test_feature_matrix.shape))

        return(train_feature_matrix, train_labels, test_feature_matrix, test_labels, train_row_ids, test_row_ids)

    def __classification(self, train_df, train_labels, test_df, test_labels):
        logistic_regression_accuracy = ml_models.logistic_regression(train_df, train_labels, test_df, test_labels)
        print("Logistic Regression Accuracy {}".format(logistic_regression_accuracy))
        decision_tree_accuracy = ml_models.decision_tree(train_df, train_labels, test_df, test_labels)
        print("Decision Tree Accuracy {}".format(decision_tree_accuracy))
        accuracy = max(logistic_regression_accuracy, decision_tree_accuracy)
        return (accuracy)

    def run(self):
        start_calculation = timeit.default_timer()

        ## Generate feature matrix
        train_feature_matrix, train_labels, test_feature_matrix, test_labels, train_row_ids, test_row_ids = self.__generate_feature_matrix()

        ## Run the classification algorithm
        accuracy = self.__classification(train_feature_matrix, train_labels, test_feature_matrix, test_labels)

        print("Accuracy is {}".format(accuracy))

        stop_calculation = timeit.default_timer()
        print("Time taken to run spam classifier userwords: " + str(stop_calculation - start_calculation))