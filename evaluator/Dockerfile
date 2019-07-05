FROM evapyenv
LABEL maintainer="changyua@ualberta.ca"
ENV GETURL3 'http://206.12.88.44:30296/get_new_task/3'
ENV POSTURL3 'http://206.12.88.44:30296/update_task/3'
ENV GETURL2 'http://206.12.88.44:30296/get_new_task/2'
ENV POSTURL2 'http://206.12.88.44:30296/update_task/2'
ENV INTERVAL 0.1
ENV TIMEOUT 10
COPY pySnippetEvaluator-docker.py /
CMD ["python3","-u","pySnippetEvaluator-docker.py"]