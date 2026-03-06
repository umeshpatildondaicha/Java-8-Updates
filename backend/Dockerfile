FROM python:3.11-slim

WORKDIR /app

# System deps for PyVista/VTK headless rendering
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data/uploads /app/data/output

# Headless VTK
ENV VTK_DEFAULT_OPENGL_WINDOW=vtkOSOpenGLRenderWindow
ENV DISPLAY=:99

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
