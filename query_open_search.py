from opensearchpy import OpenSearch
import boto3
import json
import os
import sys

import boto3
import botocore


##open search configs
host = 'search-contents-oflzhkvsjgukdwvszyd5erztza.us-east-1.es.amazonaws.com'  
port = 443 
auth = ('admin', '*******')
index_name = "contents"

##bedrock connection
session = boto3.Session(region_name='us-east-1')
bedrock_client = session.client('bedrock-runtime')



##creating opensearch client
client = OpenSearch(
    hosts=[{'host': host, 'port': port}],
    http_auth=auth,
    use_ssl=True,
    verify_certs=True
)

#requesting user for input query
input_query = input("Enter search string:")

#generating embedding for user input 
def generate_embedding(value):
    try:
        body = json.dumps({"inputText": value})
        modelId = "amazon.titan-embed-text-v1"
        accept = "application/json"
        contentType = "application/json"

        response = bedrock_client.invoke_model(
            body=body, modelId=modelId, accept=accept, contentType=contentType
        )
        response_body = json.loads(response.get("body").read())

        run_query(response_body['embedding'])
    except botocore.exceptions.ClientError as error:
        print(error)




#running a query with user input query embedding with description column in the contents index
def run_query(query_embedding):
    query = {
        "size": 5,
         "_source": "show_id", 
        "query": {
            "knn": {
                "description": {
                    "vector": query_embedding,
                    "k": 5
            }
        }
    }   }
    response = client.search(index=index_name, body=query)


    print(response)


    
generate_embedding(input_query)