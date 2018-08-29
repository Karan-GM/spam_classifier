from spam_classifier_userwords import Spam_Classifier_Userwords
from spam_classifier_unigrams import Spam_Classifier_Unigrams

class App():

    def main(self):

        ## Spam Classifier for spamwords_1
        print("####### Running spam classifier for spamwords_1 #######")
        spamwords_filename = "input/spamwords_1.txt"
        spam_classifier_userwords = Spam_Classifier_Userwords(spamwords_filename)
        spam_classifier_userwords.run()

        ## Spam Classifier for spamwords_2
        print("####### Running spam classifier for spamwords_2 #######")
        spamwords_filename = "input/spamwords_2.txt"
        spam_classifier_userwords = Spam_Classifier_Userwords(spamwords_filename)
        spam_classifier_userwords.run()

        ## Spam Classifier for all unigrams
        print("####### Running spam classifier for all unigrams #######")
        spam_classifier_unigrams = Spam_Classifier_Unigrams()
        spam_classifier_unigrams.run(create_unigrams_dict=False)

app = App()
app.main()