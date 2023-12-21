```
PUT /_ingest/pipeline/pipeline-sparse
{
  "description": "An sparse encoding ingest pipeline",
  "processors": [
    {
      "sparse_encoding": {
        "model_id": "65fy8IsBzZuijRBEwRBX",
        "field_map": {
          "passage_text": "passage_embedding"
        }
      }
    }
  ]
}
PUT sparse-index
{
  "settings": {
    "default_pipeline": "pipeline-sparse"
  },
  "mappings": {
    "properties": {
      "passage_embedding": {
        "type": "rank_features"
      },
      "passage_text": {
        "type": "text"
      }
    }
  }
}
POST _bulk
{ "index" : { "_index" : "sparse-index", "_id" : "1" } }
{ "passage_text" : "the price of the api is 2$ per invokation" }
{ "index" : { "_index" : "sparse-index", "_id" : "2" } }
{ "passage_text" : "There are 6 students in class A." }
{ "index" : { "_index" : "sparse-index", "_id" : "3" } }
{ "passage_text" : "Company xyz have a history of 100 years." }

PUT /_ingest/pipeline/pipeline-dense
{
  "description": "An dense encoding ingest pipeline",
  "processors": [
    {
      "text_embedding": {
        "model_id": "uVrH8IsBDHJz1QW0-Zam",
        "field_map": {
          "passage_text": "passage_embedding"
        }
      }
    }
  ]
}
DELETE dense-index
PUT dense-index
{
  "settings": {
    "index.knn": true,
    "default_pipeline": "pipeline-dense"
  },
  "mappings": {
    "properties": {
      "passage_embedding": {
        "type": "knn_vector",
        "dimension": 384,
        "method": {
          "engine": "lucene",
          "space_type": "l2",
          "name": "hnsw",
          "parameters": {}
        }
      },
      "passage_text": {
        "type": "text"
      }
    }
  }
}
POST _bulk
{ "index" : { "_index" : "dense-index", "_id" : "1" } }
{ "passage_text" : "the price of the api is 2$ per invokation" }
{ "index" : { "_index" : "dense-index", "_id" : "2" } }
{ "passage_text" : "There are 6 students in class A." }
{ "index" : { "_index" : "dense-index", "_id" : "3" } }
{ "passage_text" : "Company xyz have a history of 100 years." }

PUT _ingest/pipeline/hybrid_pipeline
{
  "description": "A pipeline with two processors",
  "processors": [
    {
      "sparse_encoding": {
        "model_id": "65fy8IsBzZuijRBEwRBX",
        "field_map": {
          "passage_text": "sparse_embedding"
        }
      }
    },
    {
      "text_embedding": {
        "model_id": "uVrH8IsBDHJz1QW0-Zam",
        "field_map": {
          "passage_text": "dense_embedding"
        }
      }
    }
  ]
}
DELETE hybrid-index
PUT hybrid-index
{
  "settings": {
    "index.knn": true,
    "default_pipeline": "hybrid_pipeline"
  },
  "mappings": {
    "properties": {
      "dense_embedding": {
        "type": "knn_vector",
        "dimension": 384,
        "method": {
          "engine": "lucene",
          "space_type": "l2",
          "name": "hnsw",
          "parameters": {}
        }
      },
      "sparse_embedding": {
        "type": "rank_features"
      },
      "passage_text": {
        "type": "text"
      }
    }
  }
}
POST _bulk
{ "index" : { "_index" : "hybrid-index", "_id" : "1" } }
{ "passage_text" : "the price of the api is 2$ per invokation" }
{ "index" : { "_index" : "hybrid-index", "_id" : "2" } }
{ "passage_text" : "There are 6 students in class A." }
{ "index" : { "_index" : "hybrid-index", "_id" : "3" } }
{ "passage_text" : "Company xyz have a history of 100 years." }
PUT /_search/pipeline/nlp-search-pipeline
{
  "description": "Post processor for hybrid search",
  "phase_results_processors": [
    {
      "normalization-processor": {
        "normalization": {
          "technique": "min_max"
        },
        "combination": {
          "technique": "arithmetic_mean",
          "parameters": {
            "weights": [
              0.5,
              0.5
            ]
          }
        }
      }
    }
  ]
}
GET /hybrid-index/_search?search_pipeline=nlp-search-pipeline
{
  "_source": {
    "exclude": [
      "sparse_embedding",
      "dense_embedding"
    ]
  },
  "query": {
    "hybrid": {
      "queries": [
        {
          "neural_sparse":{
            "sparse_embedding":{
              "query_text":"history of xyz",
              "model_id":"65fy8IsBzZuijRBEwRBX"
            }
          }
        },
        {
          "neural":{
            "dense_embedding":{
              "query_text":"history of xyz",
              "model_id":"uVrH8IsBDHJz1QW0-Zam"
            }
          }
        }
      ]
    }
  }
}

GET hybrid-index/_search
{
  "query":{
    "neural_sparse":{
      "sparse_embedding":{
        "query_text":"history of xyz",
        "model_id":"65fy8IsBzZuijRBEwRBX"
      }
    }
  }
}
```