FROM python:3.9-slim

# Install SQLCipher
RUN apt-get update && apt-get install -y sqlcipher libsqlcipher-dev

# Install pysqlcipher3
RUN pip install pysqlcipher3

# Set the working directory
WORKDIR /app

# Copy your Python scripts or applications
COPY . /app

# Command to run your application
CMD ["python", "password_manager.py"]
