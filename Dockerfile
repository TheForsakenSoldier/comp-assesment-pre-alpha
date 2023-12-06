FROM python:3.10

LABEL maintainer="TheForsakenSoldier"
LABEL version="1"

RUN mkdir /usr/src/python_app
WORKDIR /usr/src/python_app
ADD . .
RUN pip install -r requirments.txt

CMD [ "python" ,"./python_app_side/cmd_user_interface.py"]