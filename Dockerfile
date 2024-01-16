# Use an official Python runtime as a parent image
FROM python:3.8
# Set the working directory
WORKDIR /DDT

COPY . ../DDT

RUN pip install flask requests

CMD ["python" , "main.py"]

# Make port 80 available to the world outside this container
EXPOSE 5000

LABEL authors="peri"



