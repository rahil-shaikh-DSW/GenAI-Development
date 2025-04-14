FROM python:3.10.16-slim
RUN apt-get update
RUN apt-get install -y build-essential
RUN apt-get install -y cmake
RUN apt-get install -y libopenblas-dev
RUN apt-get install -y liblapack-dev
RUN apt-get install -y libx11-dev
RUN apt-get install -y libgtk-3-dev
RUN apt-get install -y libboost-python-dev
RUN apt-get clean
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD python app.py