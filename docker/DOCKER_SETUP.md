# ChatBrew Docker Setup Guide

This directory contains Docker configuration for running the ChatBrew chatbot application with both the Flask API and optional training capabilities.

## Files Included

- **`Dockerfile`** - Main production Dockerfile for running the Flask API
- **`Dockerfile.train`** - Separate Dockerfile for training the model
- **`docker-compose.yml`** - Docker Compose configuration for running all services
- **`.dockerignore`** - Files to exclude from Docker build context

## Quick Start

### Option 1: Using Docker Compose (Recommended)

This will run the chatbot API and optional Redis cache:

```bash
# Navigate to docker directory
cd docker

# Build and start services
docker-compose up --build

# Run in background
docker-compose up -d --build

# View logs
docker-compose logs -f chatbot-api

# Stop services
docker-compose down
```

The API will be available at: `http://localhost:5000`

### Option 2: Using Docker Directly

**Build the image:**
```bash
docker build -t chatbrew-api -f docker/Dockerfile .
```

**Run the container:**
```bash
docker run -p 5000:5000 \
  -v $(pwd)/intents.json:/app/intents.json \
  -v $(pwd)/data.pth:/app/data.pth \
  chatbrew-api
```

## API Endpoints

### Chat Endpoint
```
POST /chat
Content-Type: application/json

{
  "message": "Hello, do you have coffee?"
}

Response:
{
  "response": "Yes, we serve fresh coffee!"
}
```

### Health Check Endpoint
```
GET /health
```

## Training the Model

### Using Docker

Build training image:
```bash
docker build -f docker/Dockerfile.train -t chatbrew-train .
docker run --rm -v $(pwd):/app chatbrew-train
```

## Environment Variables

You can customize the Flask app behavior:

```bash
docker run -p 5000:5000 \
  -e FLASK_ENV=development \
  -e PYTHONUNBUFFERED=1 \
  chatbrew-api
```

Available variables:
- `FLASK_ENV` - Set to `development` or `production`
- `PYTHONUNBUFFERED` - Set to `1` for unbuffered output

## Persistent Data

The Docker setup uses volumes for:
- `intents.json` - Chatbot intent definitions
- `data.pth` - Trained model weights

These are mounted as read-only volumes by default. To train new models, use the training container.

## Scaling Considerations

The `docker-compose.yml` includes an optional Redis service for:
- Session management
- Caching responses
- Scaling multiple API instances

To add more API instances:
```bash
docker-compose up -d --scale chatbot-api=3
```

You'll need to configure a load balancer (nginx) for this.

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs chatbot-api

# Verify image build
docker build -t chatbrew-api -f docker/Dockerfile .
```

### Port already in use
```bash
# Change port mapping in docker-compose.yml
# Or kill the process on port 5000
lsof -i :5000
kill -9 <PID>
```

### NLTK data missing
The Dockerfile automatically downloads required NLTK data (`punkt`, `stopwords`). If you encounter tokenization errors, the data may not have downloaded properly. Rebuild the image:
```bash
docker build --no-cache -t chatbrew-api -f docker/Dockerfile .
```

## Production Deployment

For production, consider:

1. **Use environment-specific Compose files:**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

2. **Add reverse proxy (nginx):**
   ```yaml
   nginx:
     image: nginx:latest
     ports:
       - "80:80"
     volumes:
       - ./nginx.conf:/etc/nginx/nginx.conf
   ```

3. **Enable logging:**
   ```bash
   docker-compose logs --tail=100 -f
   ```

4. **Resource limits:**
   Add to docker-compose.yml:
   ```yaml
   services:
     chatbot-api:
       deploy:
         resources:
           limits:
             cpus: '1'
             memory: 512M
   ```

## Support

For issues or questions about the chatbot, refer to the main README.md.
