# Utilisez l'image de base jupyter/datascience-notebook
FROM jupyter/datascience-notebook

# FROM python:3.8
# WORKDIR /app

COPY requirements.txt .

# Mettez à jour pip et installez les bibliothèques nécessaires
RUN pip install --upgrade pip
RUN pip install -r requirements.txt