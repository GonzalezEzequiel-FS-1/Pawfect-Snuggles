FROM ubuntu:20.04

# Install necessary dependencies
RUN apt update && \
    apt install --no-install-recommends -y \
    python3.8 python3-pip python3.8-dev && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1

# Set the working directory inside the container
WORKDIR /app

# Copy only necessary files to the container
COPY requirements.txt .

# Install dependencies
RUN pip3 install -r requirements.txt

# Copy the rest of the application files
COPY . .

# Expose Port 8080
EXPOSE 8080

# Set the default command to run the app
CMD ["python3", "app.py"]
