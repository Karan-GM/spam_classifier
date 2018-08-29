# Objective
Building a spam classifier using machine learning and elasticsearch

# Requirements
1. Index the documents with ElasticSearch, but use library to clean the html into plain test first. You dont have to do stemming or skipping stopwords (up to you); eliminating some punctuation might be useful. 
Cleaning Data is Required: By "unigram" we mean an English word, so as part of reading/processing data there will be a filter step to remove anything that doesnt look like an English word or small number.
2. Partition the spam data set into TRAIN 80% and TEST 20%. One easy way to do so is to add to each document in ES a field "split" with values either "train" or "test" randomly, following the 80%-20% rule. Thus there will be 2 feature matrices, one for training and one for testing (different documents, same exact columns/features). The spam/ham distribution is roughly a third ham and two thirds spam; you should have a similar distribution in both TRAIN and TEST sets.
3. Manual spam features
    - Manually create a list of ngrams (unigrams, bigrams, trigrams, etc) that you think are related to spam. For example : “free” , “win”, “porn”, “click here”, etc. These will be the features (columns) of the data matrix. Use ElasticSearch querying functionality in order to create feature values for each document, for each feature
    - Train a learning algorithm, the label, or outcome, or target are the spam annotation “yes” / “no” or you can replace that with 1/0.
    - Test the spam model
4. All unigrams as features
    - A feature matrix should contain a column/feature for every unigram extracted from training documents. Since the full matrix becomes too big, sparse representation is recommended
    - Train a learning algorithm and test the model.
    
 # Setup
1. Setup [elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html) and [kibana](https://www.elastic.co/guide/en/kibana/current/install.html) 

2. Create an index in elasticsearch with the following configuration through kibana

```
PUT /spam_dataset/
{
  "settings": {
    "index": {
      "store": {
        "type": "fs" 
      },
      "number_of_shards": 1,
      "number_of_replicas": 0
    }
  }
}
```
```
PUT spam_dataset/document/_mapping
{ 
  "document": { 
    "properties": { 
      "filename": { 
        "type": "keyword", 
        "store": true 
      },
      "body":{ 
        "type": "text", 
        "store": true,
        "term_vector": "with_positions_offsets_payloads",
        "fielddata": true
      },
      "label": { 
        "type": "keyword", 
        "store": true 
      },
      "split":{ 
        "type": "keyword", 
        "store": true 
      }
    } 
  } 
}
```
3. Clone the repository<br/>
	  * git clone https://github.com/Karan-GM/spam_classifier.git<br/>

4. cd into the directory<br/>
	  * cd spam_classifier<br/>

5. Install Virtual environment tool<br/> 
	  * pip install virtualenv<br/>

6. Create an virtual environment<br/> 
	  * virtualenv spam_classifier_env<br/>

7. Activate the virtual environment<br/>
	  * source spam_classifier_env/bin/activate<br/>

8. Install the libraries from requirements file<br/> 
	  * pip install -r requirements.txt<br/>

9. cd into source folder
	  * cd spam_classifier<br/>

9. Insert all the documents into elasticsearch<br/> 
	  * python trec07p.py<br/> 
    
10. Run the program
    * python app.py<br/> 
