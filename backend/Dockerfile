FROM public.ecr.aws/lambda/python:3.9

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

ENV PYTHONPATH=${LAMBDA_TASK_ROOT}
ENV AWS_DEFAULT_REGION=us-west-2

CMD ["handlers.lambda_function.lambda_handler"]

