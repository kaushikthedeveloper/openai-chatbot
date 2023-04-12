import os
import os.path
import pandas as pd
import tiktoken
import openai
import numpy as np
from openai.embeddings_utils import distances_from_embeddings
import boto3
import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)


load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

openai_model = 'text-davinci-003'
openai_embedding = 'text-embedding-ada-002'
max_tokens = 150
s3 = boto3.client('s3')

# Load the cl100k_base tokenizer which is designed to work with the ada-002 model
tokenizer = tiktoken.get_encoding("cl100k_base")
context_file_name = '/tmp/scrapped-data.csv'
s3_bucket_name = 'kaushik-chatgpt-query-bucket'
s3_object_key_path = 'scrapped-data.csv'
processed_embedding_file_name = '/tmp/embeddings.csv'


def get_tokens():
    if not os.path.isfile(processed_embedding_file_name):
        if not os.path.isfile(context_file_name):
            logger.info('Downloading the context csv from ' + s3_bucket_name + '/' + s3_object_key_path)
            s3.download_file(s3_bucket_name, s3_object_key_path, context_file_name)
            logger.info('Context downloaded into path : ' + context_file_name)

        df = pd.read_csv(context_file_name, index_col=0)
        df.columns = ['title', 'text']

        # Tokenize the text and save the number of tokens to a new column
        df['n_tokens'] = df.text.apply(lambda x: len(tokenizer.encode(x)))

        # Visualize the distribution of the number of tokens per row using a histogram
        df.n_tokens.hist()

        shortened = []
        # Loop through the dataframe
        for row in df.iterrows():

            # If the text is None, go to the next row
            if row[1]['text'] is None:
                continue

            # If the number of tokens is greater than the max number of tokens, split the text into chunks
            if row[1]['n_tokens'] > max_tokens:
                shortened += split_into_many(row[1]['text'])

            # Otherwise, add the text to the list of shortened texts
            else:
                shortened.append(row[1]['text'])

        df = pd.DataFrame(shortened, columns=['text'])
        df['n_tokens'] = df.text.apply(lambda x: len(tokenizer.encode(x)))
        df.n_tokens.hist()

        df['embeddings'] = df.text.apply(
            lambda x: openai.Embedding.create(input=x, engine=openai_embedding)['data'][0]['embedding'])
        df.to_csv(processed_embedding_file_name)
        df.head()
        logger.info("Embeddings created")

    logger.info("Reading Embedding Data")
    df = pd.read_csv(processed_embedding_file_name, index_col=0)
    df['embeddings'] = df['embeddings'].apply(eval).apply(np.array)

    df.head()
    logger.info("Embedding Parsed")

    return df


# Function to split the text into chunks of a maximum number of tokens
def split_into_many(text, max_tokens=max_tokens):
    # Split the text into sentences
    sentences = text.split('. ')

    # Get the number of tokens for each sentence
    n_tokens = [len(tokenizer.encode(" " + sentence)) for sentence in sentences]

    chunks = []
    tokens_so_far = 0
    chunk = []

    # Loop through the sentences and tokens joined together in a tuple
    for sentence, token in zip(sentences, n_tokens):

        # If the number of tokens so far plus the number of tokens in the current sentence is greater
        # than the max number of tokens, then add the chunk to the list of chunks and reset
        # the chunk and tokens so far
        if tokens_so_far + token > max_tokens:
            chunks.append(". ".join(chunk) + ".")
            chunk = []
            tokens_so_far = 0

        # If the number of tokens in the current sentence is greater than the max number of
        # tokens, go to the next sentence
        if token > max_tokens:
            continue

        # Otherwise, add the sentence to the chunk and add the number of tokens to the total
        chunk.append(sentence)
        tokens_so_far += token + 1

    # Add the last chunk to the list of chunks
    if chunk:
        chunks.append(". ".join(chunk) + ".")

    return chunks


def answer_question(
        df,
        question,
        model=openai_model,
        max_len=1800,
        size="ada",
        stop_sequence=None
):
    """
    Answer a question based on the most similar context from the dataframe texts
    """
    context = create_context(
        question,
        df,
        max_len=max_len,
        size=size,
    )
    logger.info("Context : " + json.dumps(context))

    try:
        # Create a completions using the question and context
        response = openai.Completion.create(
            prompt=f"Answer the question based on the context below, and if the question can't be answered based on the context, say \"I don't know\"\n\nContext: {context}\n\n---\n\nQuestion: {question}\nAnswer:",
            temperature=0,
            max_tokens=max_tokens,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=stop_sequence,
            model=model,
        )
        return response["choices"][0]["text"].strip()
    except Exception as e:
        logger.error("Failed to query the completion text", exc_info=e)
        return ""


def create_context(
        question, df, max_len=1800, size="ada"
):
    """
    Create a context for a question by finding the most similar context from the dataframe
    """

    # Get the embeddings for the question
    q_embeddings = openai.Embedding.create(input=question, engine='text-embedding-ada-002')['data'][0]['embedding']

    # Get the distances from the embeddings
    df['distances'] = distances_from_embeddings(q_embeddings, df['embeddings'].values, distance_metric='cosine')

    returns = []
    cur_len = 0

    # Sort by distance and add the text to the context until the context is too long
    for i, row in df.sort_values('distances', ascending=True).iterrows():

        # Add the length of the text to the current length
        cur_len += row['n_tokens'] + 4

        # If the context is too long, break
        if cur_len > max_len:
            break

        # Else add it to the text that is being returned
        returns.append(row["text"])

    # Return the context
    return "\n\n###\n\n".join(returns)


def handler(event, context):
    logger.info("Event : " + json.dumps(event))
    question = json.loads(event["body"])['question']
    answer = answer_question(get_tokens(), question=question)
    logger.info("Answer : " + answer)
    return {
        'statusCode': 200,
        'body': json.dumps(
            {
                "answer": answer
            }
        )
    }

# uncomment below when running the python script directly (not as docker with AWS Lambda)
# user_question = input("Enter your question or press Enter to exit : ")
# print(answer_question(get_tokens(), question=user_question))