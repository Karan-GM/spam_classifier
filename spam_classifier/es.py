from elasticsearch import Elasticsearch
from datetime import datetime
import timeit

class Es():
    es = None
    index_name = None
    index_type = None

    def __init__(self, hosts, index_name, index_type):
        self.es = Elasticsearch(hosts)
        self.index_name = index_name
        self.index_type = index_type

    def insert(self, id, filename, label, text, split):
        doc = {
            'filename': filename,
            'label': label,
            'body': text,
            'split': split,
            'timestamp': datetime.now(),
        }
        result = self.es.index(index=self.index_name, doc_type=self.index_type, id=id, body=doc)
        return (result)

    def get_all_documents(self):
        print("Retrieving all documents")
        start_calculation = timeit.default_timer()
        id_list = []
        filename_list = []
        label_list = []
        split_list = []

        scroll = '1m'
        result = self.es.search(index=self.index_name,
                           doc_type=self.index_type,
                           size=500,
                           _source_include=['filename', 'label', 'split'],
                           scroll=scroll,
                           )
        scroll_id = result['_scroll_id']
        documents = result['hits']['hits']
        for document in documents:
            id = document['_id']
            id_list.append(id)
            filename = document['_source']['filename']
            filename_list.append(filename)
            label = document['_source']['label']
            label_list.append(label)
            split = document['_source']['split']
            split_list.append(split)

        while (True):
            result = self.es.scroll(scroll_id=scroll_id, scroll=scroll)
            scroll_id = result['_scroll_id']
            documents = result['hits']['hits']
            if (len(documents) > 0):
                for document in documents:
                    id = document['_id']
                    id_list.append(id)
                    filename = document['_source']['filename']
                    filename_list.append(filename)
                    label = document['_source']['label']
                    label_list.append(label)
                    split = document['_source']['split']
                    split_list.append(split)
                # print("Retrieving {} documents done".format(len(filename_list)))
            else:
                break

        stop_calculation = timeit.default_timer()
        print("Time taken to get all documents: " + str(stop_calculation - start_calculation))

        return (id_list, filename_list, label_list, split_list)

    def get_documents_for_query(self, query):
        start_calculation = timeit.default_timer()
        id_list = []
        score_list = []

        scroll = '1m'
        result = self.es.search(index=self.index_name,
                           doc_type=self.index_type,
                           size=500,
                           _source = False,
                           scroll=scroll,
                           body={
                                "query": {
                                    "match": {
                                        "body": {
                                            "query": query,
                                            "operator": "or"
                                        }
                                    }
                                }
                            }
                    )
        scroll_id = result['_scroll_id']
        documents = result['hits']['hits']
        for document in documents:
            id = document['_id']
            id_list.append(id)
            score = document['_score']
            score_list.append(score)

        while (True):
            result = self.es.scroll(scroll_id=scroll_id, scroll=scroll)
            scroll_id = result['_scroll_id']
            documents = result['hits']['hits']
            if (len(documents) > 0):
                for document in documents:
                    id = document['_id']
                    id_list.append(id)
                    score = document['_score']
                    score_list.append(score)
                # print("Retrieving {} documents done".format(len(id_list)))
            else:
                break

        stop_calculation = timeit.default_timer()
        # print("Time taken to get all documents for a query: " + str(stop_calculation - start_calculation))

        return (id_list, score_list)

    def term_vectors(self, id):
        doc_term_vector = self.es.termvectors(
            index=self.index_name,
            doc_type=self.index_type,
            id=id,
            term_statistics=True
        )
        return(doc_term_vector)

    def get_all_vocabulary(self):
        print("Getting all vocabulary")
        start_calculation = timeit.default_timer()
        vocab_dict = {}
        id_list, _, _, _ = self.get_all_documents()
        for i in range(len(id_list)):
            if( i % 1000 == 0):
                print("Getting vocabulary for {} documents done".format(i))
            id = id_list[i]
            doc_term_vector = self.term_vectors(id)
            if "body" in doc_term_vector["term_vectors"] and "terms" in doc_term_vector["term_vectors"]["body"]:
                tokens = doc_term_vector["term_vectors"]["body"]["terms"].keys()
                local_vocab_dict = dict.fromkeys(tokens, None)
                vocab_dict.update(local_vocab_dict)
            else:
                print("No tokens present for document {}".format(id))

        print("Vocab Size: {}".format(len(vocab_dict)))

        vocab_count = 0
        for key in vocab_dict.keys():
            vocab_count = vocab_count + 1
            vocab_dict[key] = vocab_count

        stop_calculation = timeit.default_timer()
        print("Time taken to get all vocabulary for a index: " + str(stop_calculation - start_calculation))
        return(vocab_dict)

    def get(self, id):
        result = None
        try:
            result = self.es.get(index=self.index_name, doc_type=self.index_type, id=id)
        except:
            result = None
        return result

    def count(self):
        result = self.es.count(index=self.index_name, doc_type=self.index_type)
        count = result['count']
        return(count)
