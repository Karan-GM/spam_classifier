import glob
from bs4 import BeautifulSoup
from es import Es
import settings as settings
import timeit
import re
import string
from nltk.corpus import wordnet

class Trec07p():
    directory_path = None
    spam_ham_index_filename = None

    def __init__(self, directory_path, spam_ham_index_filename):
        self.directory_path = directory_path
        self.spam_ham_index_filename = spam_ham_index_filename

    def __get_train_or_test(self, label, spam_count, ham_count):
        split = None
        if label == "spam":
            if spam_count > settings.spam_train_count:
                split = "test"
            else:
                split = "train"
        else:
            if ham_count > settings.ham_train_count:
                split = "test"
            else:
                split = "train"
        return(split)

    def parse_files_and_insert(self):
        start_calculation = timeit.default_timer()
        ## Parse spam/ham index
        spam_ham_index_file = open(self.spam_ham_index_filename, "r", encoding='iso-8859-1')
        spam_ham_index_content = spam_ham_index_file.readlines()
        spam_ham_index_dict = {}
        for line in spam_ham_index_content:
            spam_ham, filepath = line.split()
            spam_ham_index_dict[filepath[filepath.rfind('/')+1: ]] = spam_ham

        ## Parse all emails
        es = Es(settings.hosts, settings.index_name, settings.index_type)

        files = glob.glob(self.directory_path)
        doc_count = 0
        spam_count = 0
        ham_count = 0
        for i in range(len(files)):
            try:
                file = open(files[i], "r", encoding='iso-8859-1')

                doc_count = doc_count + 1
                filename = files[i][files[i].rfind('/')+1:]

                ## Read the entire file content
                # content = file.read()
                # text = ''.join(BeautifulSoup(content, "html.parser").findAll(text=True))

                final_words = list()
                words = BeautifulSoup(file, 'html.parser').text.split()
                for word in words:
                    if re.match("^[A-Za-z]*[?.!,]*$", word):
                        word = word.translate(str.maketrans(dict.fromkeys(string.punctuation)))
                        if wordnet.synsets(word):
                            final_words.append(word)
                text = ' '.join(final_words).lower()
                text = re.sub(' +', ' ', text)

                if(spam_ham_index_dict[filename] == "spam"):
                    spam_count = spam_count + 1
                else:
                    ham_count = ham_count + 1

                split = self.__get_train_or_test(spam_ham_index_dict[filename], spam_count, ham_count)

                if(doc_count % 1000 == 0):
                    print("Inserting {} document".format(doc_count))

                result = es.insert(doc_count, filename, spam_ham_index_dict[filename], text, split)

            except UnicodeDecodeError as ue:
                print("Error: {} in reading file: {}".format(ue, files[i]))
                continue
            except ValueError as ve:
                print("Error: {}, substring not found in file: {}".format(ve, files[i]))
                continue

        stop_calculation = timeit.default_timer()
        print("Time taken to parse and insert to elasticsearch: " + str(stop_calculation - start_calculation))
        return (doc_count)

directory_path = "input/trec07p/data/*"
spam_ham_index_filename = "input/trec07p/full/index"
trec07p = Trec07p(directory_path, spam_ham_index_filename)
trec07p.parse_files_and_insert()