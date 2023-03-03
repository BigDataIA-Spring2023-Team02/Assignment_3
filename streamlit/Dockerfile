FROM --platform=linux/amd64 python:3.10.6

WORKDIR /app

ADD . /app

RUN pip install -r requirements.txt

EXPOSE 8601

CMD ["streamlit", "run", "Login_Page.py", "--server.port", "8601"]