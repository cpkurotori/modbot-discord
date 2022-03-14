FROM public.ecr.aws/lambda/python:3.9-arm64

RUN yum update -y expat cyrus-sasl

COPY requirements.txt .
RUN pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

COPY *.py ${LAMBDA_TASK_ROOT}

CMD ["lambda_function.lambda_handler"]