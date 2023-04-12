# openai-chatbot
Chatbot running on AWS Lambda that uses OpenAI GPT3.5 model and a demo chat window to query the bot

It uses GPT3.5 based Completion model to answer queries based on relevant data feed provided as context

## Front End
Built on Vanilla - `HTML`, `JS`, `CSS`

Running the server locally using python HTTP server

```bash
$ npm start

-- OR --

$ python3 -m http.server
```

## Back End
Built on `Python 3.10`

1. Build docker image
2. Push image to ECR
3. Create AWS Lambda with exposed endpoint to query and use the image pused to ECR for its codebase


Testing the backend program locally via docker :
```bash
$ docker build -t myfunction:latest .
$ docker run -p 9000:8080  myfunction:latest
$ curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'
```

---

### To change in codebase
   1. [fe] API Endpoint of newly created lambda in the front end
   2. [be] OpenAI keys
   3. [be] AWS Credentials and bucket name to use for storing the context data
   4. [be] scrapped-data.csv in the s3 bucket which will hold the scrapped data to be used as context for GPT models to analyse and answer on basis of (example csv file attached)

---

### Changes : chatgpt-query-engine

```
app.py
------
context_file_name : file name for the downloaded csv file locally (csv)
s3_bucket_name : s3 bucket holding the context data
s3_object_key_path : s3 object key path for the data file (csv)
processed_embedding_file_name : gpt processed embedding file to be stored locally
```

```
.env
-----
OPENAI_API_KEY : API key for the OpenAI platform
```

```
Dockerfile
----------
AWS_ACCESS_KEY_ID : AWS access key id for the account your s3 bucket is in 
AWS_SECRET_ACCESS_KEY : AWS secret access key for the account your s3 bucket is in 
```

### Changes : chatbot-widget-frontend

```
index.html
----------
chatGptProcessingUrl : Lambda Endpoint to hit upon for querying
```