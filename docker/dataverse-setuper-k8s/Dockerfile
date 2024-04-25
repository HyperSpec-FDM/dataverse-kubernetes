# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.9

EXPOSE 8000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY docker/dataverse-setuper-k8s/requirements.txt requirements.txt
RUN python -m pip install -r requirements.txt

WORKDIR /dataverse-setuper
ADD docker/dataverse-setuper-k8s /dataverse-setuper

# Run the application
ENTRYPOINT ["python"]
CMD ["app.py"]