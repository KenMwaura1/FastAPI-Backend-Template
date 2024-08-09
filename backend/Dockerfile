# Pull official latest Python Docker image (Pulished with version 3.11.0)
FROM --platform=linux/amd64 python:alpine3.11

# Set the working directory
WORKDIR /usr/backend

# Set up Python behaviour
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV VIRTUAL_ENV=/opt/venv

# Switch on virtual environment
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Set the server port
EXPOSE 8000

# Copy requirements.txt
COPY ./requirements.txt ./

# Install system dependencies
RUN set -eux \
    && apk add --no-cache --virtual .build-deps build-base \
    libressl-dev libffi-dev gcc musl-dev python3-dev \
    postgresql-dev 
# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del .build-deps \
    && rm -rf /root/.cache/pip

# Copy all files
COPY . .

# Copy entrypoint.sh for auto connection with account_db service
COPY ./entrypoint.sh .
RUN chmod +x /usr/backend/entrypoint.sh

# Execute entrypoint.sh
ENTRYPOINT ["/usr/backend/entrypoint.sh" ]

# Start up the backend server
CMD uvicorn src.main:backend_app --reload --workers 4 --host 0.0.0.0 --port 8000
