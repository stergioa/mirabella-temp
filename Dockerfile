# Use an official lightweight Python image suitable for Raspberry Pi (arm-based architecture)
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file to install dependencies
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app files to the working directory
COPY . /app/

# Expose the port Streamlit runs on
EXPOSE 8501

# Run the Streamlit app and fetch_data.py in parallel
CMD ["sh", "-c", "python fetch_data.py & streamlit run app.py --server.enableCORS=false --server.enableXsrfProtection=false"]
