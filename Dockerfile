# Use a newer or more secure base image if available
FROM python:3.12.2-alpine AS base
WORKDIR /code

# Ensure system packages are updated and install any necessary security updates
RUN apk update && apk upgrade && rm -rf /var/cache/apk/*

COPY ./requirements.txt /code/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools && \
    pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./code/main.py /code/main.py
COPY ./code/templates /code/templates

CMD ["/bin/sh"]

FROM base AS test
WORKDIR /code
COPY ./requirements-dev.txt /code/requirements-dev.txt

# Install development dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements-dev.txt

COPY ./code/test_main.py /code/test_main.py
COPY ./test.sh /code/test.sh

RUN chmod +x /code/test.sh
CMD [ "./test.sh" ]

FROM base AS artifact
WORKDIR /code
RUN python -m pip uninstall -y pip && \
    rm -f /sbin/apk && \
    rm -rf /etc/apk && \
    rm -rf /lib/apk && \
    rm -rf /usr/share/apk && \
    rm -rf /var/lib/apk && \
    rm -rf /root/.cache/pip

# TODO: look into re-enabling this, but need a high level of permission to run the docker commands
# RUN addgroup --system nonroot && \
#     adduser --system --ingroup nonroot nonroot
# # Set the home directory for the nonroot user
# ENV HOME=/home/nonroot
# # Create the home directory and set proper permissions
# RUN chown -R nonroot:nonroot $HOME && \
#     chown -R nonroot:nonroot /tmp && \
#     chown -R nonroot:nonroot /code
# # Switch to the nonroot user
# USER nonroot

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
