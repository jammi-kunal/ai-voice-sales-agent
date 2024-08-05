# Extend the official Rasa SDK image
FROM rasa/rasa-sdk:3.6.2

USER root

COPY requirements.txt /app/requirements.txt

# Install extra requirements for actions code, if necessary (uncomment next line)
RUN pip install -r /app/requirements.txt

# Copy actions folder to working directory
COPY ./actions /app/actions
