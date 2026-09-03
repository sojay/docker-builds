# Use the official Node.js image as the base image for building the React app
FROM node:20 AS build

# Set the working directory
WORKDIR /app

ARG REACT_APP_SENTRY_DSN
ARG REACT_APP_SENTRY_ENVIRONMENT
ARG REACT_APP_SENTRY_RELEASE
ARG REACT_APP_SENTRY_TRACES_SAMPLE_RATE

ENV REACT_APP_SENTRY_DSN=${REACT_APP_SENTRY_DSN}
ENV REACT_APP_SENTRY_ENVIRONMENT=${REACT_APP_SENTRY_ENVIRONMENT}
ENV REACT_APP_SENTRY_RELEASE=${REACT_APP_SENTRY_RELEASE}
ENV REACT_APP_SENTRY_TRACES_SAMPLE_RATE=${REACT_APP_SENTRY_TRACES_SAMPLE_RATE}

# Copy the package.json and package-lock.json files
COPY package.json package-lock.json ./

# Install the app dependencies
RUN npm install

# Copy the rest of the application source code
COPY . .

# Build the React app
RUN npm run build

# Use the official Nginx image to serve the built files
FROM nginx:alpine

# Copy the built files from the previous stage
COPY --from=build /app/build /usr/share/nginx/html

# Proxy /api/* to the api service so the frontend stays same-origin
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Nginx serves the production bundle on port 80
EXPOSE 80

# Start Nginx server
CMD ["nginx", "-g", "daemon off;"]
