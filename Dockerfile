FROM python:3.14-slim AS model-builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /build

COPY requirements.txt requirements-model.txt ./

RUN python -m pip install --upgrade pip \
    && python -m pip install -r requirements-model.txt

COPY analysis ./analysis

RUN python -m analysis.synthetic_data \
    && python -m analysis.modelling_dataset \
    && python -m analysis.model_artifact


FROM python:3.14-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt requirements-model.txt ./

RUN python -m pip install --upgrade pip \
    && python -m pip install -r requirements-model.txt

RUN addgroup --system tutorpulse \
    && adduser --system --ingroup tutorpulse tutorpulse

COPY --chown=tutorpulse:tutorpulse app ./app
COPY --chown=tutorpulse:tutorpulse analysis ./analysis
COPY --from=model-builder \
    --chown=tutorpulse:tutorpulse \
    /build/artifacts \
    ./artifacts

USER tutorpulse

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]