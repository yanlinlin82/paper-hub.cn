FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY frontend/package.json frontend/package-lock.json* ./

# Install dependencies
RUN npm install --registry=https://registry.npmmirror.com/ && \
    chmod -R a+w node_modules

# Copy source files
COPY frontend/ .

# Ensure /app is writable by the runtime user
RUN chmod 755 /app

# Expose Vite dev server port
EXPOSE 5173

# Default: run dev server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
