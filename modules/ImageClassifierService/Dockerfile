FROM tensorflow/tensorflow:1.5.0-py3

COPY /build/amd64-requirements.txt amd64-requirements.txt

RUN pip install -r amd64-requirements.txt
 
ADD app /app

# Expose the port
EXPOSE 80

# Set the working directory
WORKDIR /app

# Run the flask server for the endpoints
CMD python app.py
