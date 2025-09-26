# Use the official Playwright image
FROM mcr.microsoft.com/playwright:v1.40.0-jammy

WORKDIR /usr/src/app

# Copy source code and the new run script
COPY . .
COPY run_playwright.sh .

# Make the script executable
RUN chmod +x run_playwright.sh

# Install dependencies
RUN npm install
RUN npm install -g @playwright/mcp@latest
RUN npx playwright install --with-deps

EXPOSE 8931

# Run the server using the script
CMD ["./run_playwright.sh"]
