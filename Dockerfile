# Use the official Python image
FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy only the requirements file to leverage Docker caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the FastAPI default port
EXPOSE 8000

# Set environment variable to prevent Python output buffering
ENV PYTHONUNBUFFERED=1

# Start the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
