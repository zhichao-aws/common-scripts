register client
```
hosts = ["https://localhost:9200"]
client=OpenSearch(
    hosts = hosts,
    http_auth = ("admin","admin"),
    verify_certs=False,
    ssl_show_warn=False
)
```

run predict api
```
# neural sparse model
client.transport.perform_request("POST",f"/_plugins/_ml/models/{model_id}/_predict",body={
  "text_docs": ["hello world", "second doc"]
})

# t2x remote connector model
client.transport.perform_request("POST",f"/_plugins/_ml/models/{model_id}/_predict",body={
    "parameters":{
        "prompt":'Below is an instruction that describes a task ... \n\n### Response:\n'
    }
})
```

read load yaml
```
import yaml

with open('configs.yaml', 'r') as file:
    configs = yaml.safe_load(file)

with open('test.yaml', 'w') as file:
    yaml.dump(data, file)

```