import time

region = "ap-northeast-1"


def get_endpoint(s):
    return "https://runtime.sagemaker.%s.amazonaws.com/endpoints/%s/invocations"%(region,s)

class Action:
    def __init__(self,method,path):
        self.method=method
        self.path=path
        
    def __call__(self,client,body=None):
        if body==None:
            return client.transport.perform_request(self.method,self.path)
        else:
            return client.transport.perform_request(self.method,self.path,body=body)


class ModelRegisterHelper:
    def __init__(self,client):
        self.client = client
        self.create_connector = Action("POST","/_plugins/_ml/connectors/_create")
        self.register_model = Action("POST","/_plugins/_ml/models/_register")
        client.transport.perform_request("PUT","/_cluster/settings",body={
            "persistent" : {
                "plugins.ml_commons.only_run_on_ml_node" : False,
                "plugins.ml_commons.allow_registering_model_via_url":True,
                "plugins.ml_commons.trusted_connector_endpoints_regex":
                [ "^https://runtime\\.sagemaker\\..*[a-z0-9-]\\.amazonaws\\.com/.*$"]
            }
        })

    def ensure_task_complete(self,task_id):
        while(1):
            print(task_id)
            response=self.client.transport.perform_request("GET","/_plugins/_ml/tasks/%s"%task_id)
            print(response["state"])
            if response["state"]=="COMPLETED":
                return response
            time.sleep(3)
            
    def ensure_deploy(self,model_id):
        response = self.client.transport.perform_request("POST","/_plugins/_ml/models/%s/_deploy"%model_id)
        self.ensure_task_complete(response["task_id"])
    
    def register_remote(self,url,**kwargs):
        response=self.create_connector(self.client,{
            "name": kwargs.get("name","model"),
            "description": "Test connector for Sagemaker model",
            "version": kwargs.get("version",1),
            "protocol": "aws_sigv4",
            "credential": {
                "access_key": kwargs.get("access_key",""),
                "secret_key": kwargs.get("secret_key","")
            },
            "parameters": {
                "region": kwargs.get("region",region),
                "service_name": kwargs.get("service_name","sagemaker")
            },
            "actions": [
                {
                    "action_type": "predict",
                    "method": "POST",
                    "headers": {
                        "content-type": "application/json"
                    },
                    "url": url,
                    "request_body": kwargs.get("request_body","${parameters.input}")
            }
            ]
        })
        connector_id=response["connector_id"]
        print("connector:",connector_id)
        response = self.register_model(self.client,{
            "name": kwargs.get("name","model"),
            "function_name": "remote",
            "version": "1.0.0",
            "connector_id": connector_id,
            "description": "Test connector for Sagemaker model",
        })
        task_id = response["task_id"]
        response = self.ensure_task_complete(task_id)
        model_id = response["model_id"]
        print("model has been registered. model_id:",model_id)
        print(model_id)
#         self.ensure_deploy(model_id)
        self.client.transport.perform_request("POST","/_plugins/_ml/models/%s/_deploy"%model_id)
        return model_id
        
        
# use case
# helper=ModelRegisterHelper(client)
# helper.register_remote(
#     url=get_endpoint('torchserve-endpoint-bi-encoder-opt-2023-12-13-05-37-34'),
#     access_key="xxxx",
#     secret_key="xxxx"
# )

# client.transport.perform_request("PUT","/_ingest/pipeline/sparse-pipeline",body={
#   "description": "An sparse encoding ingest pipeline",
#   "processors": [
#     {
#       "sparse_encoding": {
#         "model_id": "_td0YowBe3q822ROQZqE",
#         "field_map": {
#           "text": "text_sparse"
#         }
#       }
#     }
#   ]
# })