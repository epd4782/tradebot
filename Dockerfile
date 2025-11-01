FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

ARG USE_OFFLINE_WHEELS=false
ENV USE_OFFLINE_WHEELS=${USE_OFFLINE_WHEELS}

COPY requirements.txt ./
COPY wheelhouse ./wheelhouse

RUN if [ "${USE_OFFLINE_WHEELS}" = "true" ]; then
if [ -d wheelhouse ] && [ "$(ls -A wheelhouse)" ]; then
pip install --no-cache-dir --no-index --find-links=wheelhouse -r requirements.txt;
else
echo "Offline installation requested but wheelhouse is empty" >&2;
exit 1;
fi;
else
pip install --no-cache-dir -r requirements.txt;
fi

COPY . .

CMD ["python", "-m", "src.main", "paper"]