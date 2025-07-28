# Use uma imagem base oficial do Python
FROM python:3.12-slim

# Atualiza e instala dependências do sistema necessárias para pyaudio, opencv, mediapipe
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Define diretório de trabalho dentro do container
WORKDIR /app

# Copia o requirements.txt para dentro do container
COPY requirements.txt .

# Instala as dependências Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copia todo o código para dentro do container
COPY . .

# Comando para rodar seu script principal (ajuste o nome do arquivo)
CMD ["python", "seu_script_principal.py"]
