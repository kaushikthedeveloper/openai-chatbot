# openai-chatbot
Chatbot running on AWS Lambda that uses OpenAI GPT3.5 model and a demo chat window to query the bot

It uses GPT3.5 based Completion model to answer queries based on relevant data feed provided as context

## Front End
Built on Vanilla HTML, JS, CSS

Run the server locally using python server

```bash
$ python3 -m http.server
```

## Back End
Build on Python 3.10

1. Build docker image
2. Push image to ECR
3. Create AWS Lambda with exposed endpoint to query and use the image in the ECR for the codebase


Testing backend program locally :
```bash
$ docker build -t myfunction:latest .
$ docker run -p 9000:8080  myfunction:latest
$ curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'
```


### To change in codebase
1. [fe] API Endpoint of newly created lambda in the front end
2. [be] OpenAI keys
3. [be] AWS Credentials and bucket name to use for storing the context data
4. [be] scrapped-data.csv in the s3 bucket which will hold the scrapped data to be used as context for GPT models to analyse and answer on basis of (example csv file attached)