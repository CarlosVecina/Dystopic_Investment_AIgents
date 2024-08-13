FROM mageai/mageai:latest

ARG USER_CODE_PATH=/home/dystopic_investment_aigents/${PROJECT_NAME}
ARG POETRY_VERSION=1.7.1
ARG PYTHON_VERSION=3.11

COPY ./requirements.txt ${USER_CODE_PATH}requirements.txt 
COPY ./.env ${USER_CODE_PATH}.env 
