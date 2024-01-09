run predict api
```
client.transport.perform_request("POST",f"/_plugins/_ml/models/{model_id}/_predict",body={
  "text_docs": ["hello world", "second doc"]
})
```