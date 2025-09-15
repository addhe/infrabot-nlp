# Use an official Python runtime as a parent image
FROM python:3.10-slim

WORKDIR /usr/src/app

# Install dependencies, including gunicorn
RUN pip install --no-cache-dir Flask requests gunicorn

# Copy the proxy application code
COPY playwright_proxy.py .

# Expose the port the app runs on
EXPOSE 8080

# Define the command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "playwright_proxy:app"]
