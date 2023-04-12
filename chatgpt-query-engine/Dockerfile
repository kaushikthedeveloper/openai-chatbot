FROM public.ecr.aws/lambda/python:3.10
ENV AWS_ACCESS_KEY_ID <access_key_to_add>
ENV AWS_SECRET_ACCESS_KEY <secret_key_to_add>
COPY requirements.txt  .
RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"
COPY app.py ${LAMBDA_TASK_ROOT}
CMD [ "app.handler" ]