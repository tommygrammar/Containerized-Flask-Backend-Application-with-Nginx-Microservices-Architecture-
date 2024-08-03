# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Copy the JSON file
COPY security_key.json /app/security_key.json 

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5000 for the Flask service
EXPOSE 5000

# Run auth-service.py when the container launches
CMD ["python", "auth-service.py"]

