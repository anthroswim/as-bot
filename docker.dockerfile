# Use an official Python runtime as the base image
FROM python:3.12.4-slim

# Install ffmpeg
RUN apt-get -y update && apt-get -y upgrade && apt-get install -y ffmpeg

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the project dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files to the working directory
COPY . .

# Set the entry point command for the container
CMD [ "python", "bot.py" ]