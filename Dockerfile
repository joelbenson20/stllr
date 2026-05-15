# Pull official base Python Docker image
FROM python:3.14.4

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /code

# Install dependencies
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m nltk.downloader -d /usr/local/share/nltk_data stopwords wordnet punkt_tab averaged_perceptron_tagger_eng

# Copy the Django project
COPY . .