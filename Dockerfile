# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Create a non-root user for security
RUN useradd --create-home app_user

# Copy just the requirements file first to leverage Docker layer caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application source code
COPY app.py .
COPY my_cli_agent/ my_cli_agent/

# Change ownership of the app directory to the non-root user
RUN chown -R app_user:app_user /usr/src/app

# Switch to the non-root user
USER app_user

# Expose the port the app runs on
EXPOSE 8080

# Define the command to run the application using a production-grade server
# The PORT environment variable will be supplied by Cloud Run.
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
