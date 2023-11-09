# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.9

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /cronJob
COPY class_dataverse_curler.py .
COPY dataverse_cron_job.py .

# Run the application
ENTRYPOINT ["python"]
CMD ["dataverse_cron_job.py"]