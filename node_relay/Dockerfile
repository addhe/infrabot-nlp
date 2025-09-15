# Use Playwright base image with browsers and system deps preinstalled
FROM mcr.microsoft.com/playwright:v1.40.0-jammy

WORKDIR /usr/src/app

# Install deps
COPY package.json .
RUN npm install --only=production && npx playwright install --with-deps

# Copy server
COPY server.js .
COPY mcp_host.js .

# Expose port
EXPOSE 8080

# Start server
CMD ["npm", "start"]
