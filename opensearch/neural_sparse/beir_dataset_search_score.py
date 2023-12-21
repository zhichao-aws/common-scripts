import json

from tqdm import tqdm
from opensearchpy import OpenSearch
from beir.retrieval.evaluation import EvaluateRetrieval
from beir.datasets.data_loader import GenericDataLoader

client=OpenSearch(
    hosts = ["http://localhost:9200"], 
    verify_certs=False,
    ssl_show_warn=False
)
[body for body in client.cat.indices(format="json") if not body["index"].startswith(".") and not body["index"].startswith("security")]

client.transport.perform_request("PUT","/_cluster/settings", body={
     "persistent": {
         "plugins.ml_commons.only_run_on_ml_node": False,
         "plugins.ml_commons.native_memory_threshold": 99
     }
 })

# register tokenizer?
client.transport.perform_request("POST","/_plugins/_ml/models/_register",params={"deploy":"true"},body={
    "name":"amazon/neural-sparse/opensearch-neural-sparse-tokenizer-v1",
    "version":"1.0.1",
    "model_format": "TORCH_SCRIPT"
})

client.transport.perform_request("PUT","/_ingest/pipeline/sparse-pipeline",body={
  "description": "An sparse encoding ingest pipeline",
  "processors": [
    {
      "sparse_encoding": {
        "model_id": "_td0YowBe3q822ROQZqE",
        "field_map": {
          "text": "text_sparse"
        }
      }
    }
  ]
})

for dataset in ["nfcorpus","scifact","scidocs"]:
    print(dataset)
    with open("/home/ubuntu/beir/corpus/%s.json"%dataset) as f:
        corpus=json.load(f)
    try:
        client.indices.delete(index=dataset)
    except:
        pass
    client.indices.create(index=dataset, body={
        "settings": {
            "index.number_of_shards": 3,
            "default_pipeline": "sparse-pipeline"
        },
        "mappings": {
            "properties": {
                "text": {
                    "type": "text"
                },
                "text_sparse": {
                    "type": "rank_features"
                }
            }
        }
    })
    i=0
    bulk_body=[]
    for _id,body in tqdm(corpus.items()):
        text=body["title"]+" "+body["text"]
        bulk_body.append({ "index" : { "_index" : dataset, "_id" : _id } })
        bulk_body.append({ "text" : text })
        i+=1
        if i%200==0:
            response=client.bulk(bulk_body)
            assert response["errors"]==False
            try:
                assert response["errors"]==False
            except:
                print("there is errors")
                time.sleep(1)
                response = client.bulk(bulk_body)
                assert response["errors"]==False
            bulk_body=[]
    response=client.bulk(bulk_body)
    assert response["errors"]==False
    client.indices.refresh(index=dataset)
    
    
    with open("/home/ubuntu/beir/queries/%s.json"%dataset) as f:
        queries=json.load(f)
    with open("/home/ubuntu/beir/qrels/%s.json"%dataset) as f:
        qrels=json.load(f)

    run_res={}
    for _id,text in tqdm(queries.items()):
        query={
          'size': 20,
          'query': {
            "neural_sparse": {
                "text_sparse":{
                    "query_text":text,
                    "model_id":"6dfDYYwBe3q822RODppp"
                }
            }
          }
        }
        response=client.search(index=dataset,body=query)
        hits=response["hits"]["hits"]
        run_res[_id]={item["_id"]:item["_score"] for item in hits}
    for query_id, doc_dict in tqdm(run_res.items()):
        if query_id in doc_dict:
            doc_dict.pop(query_id)
    res=EvaluateRetrieval.evaluate(qrels, run_res, [10])
    print(res)