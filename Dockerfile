# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy dependency list and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY screen_control_app.py .
COPY .env .  # optional: include default env settings

# Expose port and default command
EXPOSE 5000
CMD ["python", "screen_control_app.py"]
