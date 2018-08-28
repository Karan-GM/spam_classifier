from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
import numpy as np

def logistic_regression(train_df, train_labels, test_df, test_labels):
    logistic_regression = LogisticRegression()
    logistic_regression.fit(train_df, train_labels)
    logistic_regression_accuracy = logistic_regression.score(test_df, test_labels)
    predict_proba = logistic_regression.predict_proba(test_df)
    prob_scores = []
    for element in predict_proba:
        prob_scores.append(element[1])
    prob_result = np.array(prob_scores).argsort()[::-1][:50]
    spam_count = 0
    for i in range(50):
        if (test_labels[prob_result[i]] == 1):
            spam_count = spam_count + 1
    print("Top 50 percentage: {}".format(spam_count / 50))
    return(logistic_regression_accuracy)

def decision_tree(train_df, train_labels, test_df, test_labels):
    decision_tree_classifier = DecisionTreeClassifier(criterion="entropy")
    decision_tree_classifier.fit(train_df, train_labels)
    decision_tree_accuracy = decision_tree_classifier.score(test_df, test_labels)
    return (decision_tree_accuracy)
