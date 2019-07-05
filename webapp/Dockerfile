FROM python:3.6-slim
LABEL maintainer="nima.mahmoudi@ualberta.ca"

EXPOSE 8000

WORKDIR /usr/src/app

COPY ./requirements.txt ./

# RUN apt-get update \
#     && apt-get install -y --no-install-recommends python3-dev gcc g++ \
#     && rm -rf /var/lib/apt/lists/* \
#     && pip install --no-cache-dir -r requirements.txt \
#     && apt-get purge -y --auto-remove gcc python3-dev g++
# the --no-install-recommends helps limit some of the install so that you can be more explicit about what gets installed

RUN pip install --no-cache-dir -r requirements.txt

ENV TZ=Canada/Mountain
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY ./ .

# CMD [ "python", "-u", "manage.py", "runserver", "0.0.0.0:8000" ]
CMD [ "gunicorn", "--workers=4", "--bind", "0.0.0.0:8000", "webapp.wsgi" ]

