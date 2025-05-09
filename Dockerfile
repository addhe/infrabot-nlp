FROM python:3.10-slim as base
RUN mkdir /usr/src/app
RUN useradd --create-home app_user \
    && chown -R app_user /usr/src/app \
    && chmod -R a+rwx /usr/src/app
WORKDIR /usr/src/app
COPY --chown=app_user:app_user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && rm -rf ~/.cache/pip

USER app_user

COPY --chown=app_user:app_user gemini-bot.py  gemini-bot.py
CMD [ "python", "./gemini-bot.py"]