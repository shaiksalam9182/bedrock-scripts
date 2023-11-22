import boto3
import json
import os
import sys

import boto3
import botocore
import pandas as pd

from opensearchpy import OpenSearch


##opensearch configs
host = 'search-contents-oflzhkvsjgukdwvszyd5erztza.us-east-1.es.amazonaws.com'  
port = 443 
auth = ('admin', '*****')
index_name = "contents"


##creating opensearch client
client = OpenSearch(
    hosts=[{'host': host, 'port': port}],
    http_auth=auth,
    use_ssl=True,
    verify_certs=True
)


##reading titles using pandas
df = pd.read_csv('netflix_titles.csv')

selected_columns = df[['show_id','title','description']]

refined_df = selected_columns.head(100)




##connecting to bedrock runtime
session = boto3.Session(region_name='us-east-1')
bedrock_client = session.client('bedrock-runtime')


##generate embedding using titan model
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

        return response_body
    except botocore.exceptions.ClientError as error:
        print(error)

##creating a document to insert
def create_document(show_id,title,description):
    document = {
        'show_id':show_id,
        'title':title['embedding'],
        'description':description['embedding']
    }

    insert_document(document)

##inserting document into opensearch
def insert_document(document):
    client.index(index=index_name, body=document)


##iterating thorough each row in data frame created through pandas and requesting embedding
for index, row in refined_df.iterrows():
    show_id = row['show_id']
    title = row['title']
    description = row['description']
    title_embedding = generate_embedding(title)
    description_embedding = generate_embedding(description)
    create_document(show_id,title_embedding,description_embedding)
    print(f"inserted:{index}")