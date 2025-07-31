# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first to take advantage of Docker layer caching
COPY requirements.txt ./requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port 5000 for the Flask app
EXPOSE 5000

# The DeepSeek API key can be provided at runtime via the environment
ENV DEEPSEEK_API_KEY=""

# Run the application
CMD ["python", "app.py"]
