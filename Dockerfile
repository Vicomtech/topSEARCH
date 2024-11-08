FROM python:3.10

RUN apt-get update
RUN mkdir /topfind
COPY . /topfind
WORKDIR /topfind

RUN pip install -r requirements.txt
RUN pip install .
RUN export $(cat .topfind.env)
ENV PYTHONPATH=/topfind
EXPOSE 8000

CMD ["streamlit", "run", "app/topfind/web.py"]