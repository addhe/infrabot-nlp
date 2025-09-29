# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements file into the container at /usr/src/app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container
COPY . .

# Set the environment variable for the gcloud MCP server
ENV GCLOUD_MCP_SERVER_URL="https://gcloud-mcp-361046956504.us-central1.run.app"

# Run app.py when the container launches
CMD ["python", "-m", "my_cli_agent.app"]