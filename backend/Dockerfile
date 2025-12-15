# Use a newer, specific Alpine version for Python 3.11
FROM python:3.14-alpine

# Set the working directory
WORKDIR /usr/backend

# Set up Python behaviour
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/opt/venv

# Create a non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Install system dependencies needed for building Python packages
# postgresql-client is needed for runtime, build-base etc for building
RUN apk add --no-cache \
    postgresql-client \
    && apk add --no-cache --virtual .build-deps \
    build-base \
    libffi-dev \
    openssl-dev \
    postgresql-dev

# Switch on virtual environment
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy requirements.txt and install dependencies
COPY ./requirements.txt ./
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del .build-deps

# Copy all files
COPY . .

# Copy entrypoint.sh and set permissions
COPY ./entrypoint.sh .
RUN chmod +x /usr/backend/entrypoint.sh && chown appuser:appgroup /usr/backend/entrypoint.sh

# Switch to non-root user
USER appuser

# Set the server port
EXPOSE 8000

# Execute entrypoint.sh
ENTRYPOINT ["/usr/backend/entrypoint.sh"]

# Start up the backend server
CMD ["uvicorn", "src.main:backend_app", "--reload", "--workers", "4", "--host", "0.0.0.0", "--port", "8000"]