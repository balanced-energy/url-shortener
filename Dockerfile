# Use official Python image
FROM python:3.11

# Set the working directory inside the container
WORKDIR /url-shortener

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY . .

# Expose the port your FastAPI application will run on
EXPOSE 8000

# Define the command to run your FastAPI application
CMD ["uvicorn", "api.api_handlers:app", "--host", "0.0.0.0", "--port", "8000"]