# Use official NGINX image as base
FROM public.ecr.aws/nginx/nginx:alpine

# Copy your index.html into the NGINX default HTML directory
COPY index.html /usr/share/nginx/html/index.html

# Expose port 80 (default for NGINX)
EXPOSE 80

# Start NGINX
CMD ["nginx", "-g", "daemon off;"]


# # Use the official Python base image
# FROM python:3.11-slim

# # Set the working directory inside the container
# WORKDIR /app

# # Copy the Python script to the working directory
# COPY app.py .

# # Command to run the Python script
# CMD ["python", "app.py"]
