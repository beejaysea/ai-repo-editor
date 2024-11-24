# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements and install dependencies first
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the tools directory
COPY tools /app/tools/

# Create work_dir
RUN mkdir -p /app/work_dir

# Make port 9191 available
EXPOSE 9191

# Set Python to run in verbose mode and unbuffered
ENV PYTHONUNBUFFERED=1
ENV PYTHONVERBOSE=1
ENV PYTHONPATH=/app

# Set the command to run the server
CMD ["python", "-m", "uvicorn", "tools.tools_service:app", "--host", "0.0.0.0", "--port", "9191", "--log-level", "debug"]
