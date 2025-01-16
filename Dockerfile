FROM python:3.10

RUN apt-get update
RUN mkdir /topsearch
COPY . /topsearch
WORKDIR /topsearch

RUN pip install -r requirements.txt
RUN pip install .
RUN export $(cat .topsearch.env)
ENV PYTHONPATH=/topsearch
EXPOSE 8000

CMD ["streamlit", "run", "app/topfind/web.py"]