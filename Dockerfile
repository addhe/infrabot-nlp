# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Create a non-root user
RUN useradd --create-home app_user

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# Running as root to install packages system-wide in the image layer
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code to the working directory
COPY run_agent.py .
COPY run_adk_agent.py .
COPY run_openai_agent.py .
COPY my_cli_agent/ my_cli_agent/
COPY adk_cli_agent/ adk_cli_agent/

# Change the ownership of the /usr/src/app directory and its contents to the app_user
# This ensures the non-root user can read/execute the application files
RUN chown -R app_user:app_user /usr/src/app

# Switch to the non-root user
USER app_user

# Define the default command to run when the container starts
# This can be overridden at runtime if needed, e.g., to run run_adk_agent.py
CMD [ "python", "./run_agent.py" ]