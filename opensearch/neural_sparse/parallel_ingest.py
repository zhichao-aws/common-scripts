from tqdm import tqdm
from opensearchpy import OpenSearch
from opensearchpy.helpers import parallel_bulk

client = OpenSearch(
    hosts=["http://localhost:9200"], verify_certs=False, ssl_show_warn=False
)


def gendata():
    with open(output_file) as f:
        for line in f:
            line = json.loads(line)
            yield {"_index": target_index, "_id": line["id"], "_source": line}


for success, info in tqdm(
    parallel_bulk(client, gendata(), thread_count=8, queue_size=8)
):
    if not success:
        print("A document failed:", info)
        break
