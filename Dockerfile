FROM python:3.12

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ /src/

WORKDIR /src

CMD [ "python", "split_msg.py" ]
