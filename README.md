# DevOps Project Bookstore

This repository provides instructions for setting up and running both the API and UI components of the DevOps Project Bookstore. It also includes the setup of a Docker simulator for building and storing Docker images.

## Table of Contents
1. [API Setup](#api-setup)
2. [UI Setup](#ui-setup)
3. [Browser Access](#browser-access)
4. [Docker Simulator Setup](#docker-simulator-setup)
5. [Building Docker Images](#building-docker-images)

---

## API Setup

1. Open a terminal (Terminal 1) and run the following commands to set up the API:

    ```bash
    sudo apt-get update
    sudo apt-get install libpq-dev
    git clone https://github.com/prepare-sh/devops-project-bookstore.git
    cd devops-project-bookstore
    cd api
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use .\venv\Scripts\activate
    pip install -r requirements.txt
    python main.py  # Or your specific Python entry file
    ```

## UI Setup

2. In a separate terminal (Terminal 2), run the following commands to set up the UI:

    ```bash
    cd devops-project-bookstore
    cd ui
    npm install
    npm start
    ```

## Browser Access

3. Once both the API and UI are running, open your browser and access the application using the following URL:

    ```
    https://localhost:3000
    ```

## Docker Simulator Setup

4. To set up the Docker simulator, follow these steps:

    ```bash
    git clone https://github.com/prepare-sh/docker-simulator-cli
    cd docker-simulator-cli
    go build .
    mv dockermock /usr/local/bin/docker
    ```

5. Log in to Docker's GitHub container registry:

    ```bash
    docker login ghcr.io
    ```

    Choose **HTTP Authorization** when prompted.

## Building Docker Images

6. To build Docker images for the API and UI components, do the following:

   - **For the API:**
   
     Navigate to the `api` directory and run the following command to build the Docker image:
     
     ```bash
     cd devops-project-bookstore/api
     docker build .
     ```

   - **For the UI:**

     Navigate to the `ui` directory and run the following command to build the Docker image:
     
     ```bash
     cd devops-project-bookstore/ui
     docker build .
     ```

7. This will create a repository called `docker-builds` in your GitHub account. For each build, a temporary branch will be created, and the image will be built and stored in your GitHub Packages.

---

## Additional Notes

- Ensure you have Docker, and Go installed on your machine to follow the instructions above.
- This setup assumes you're working with a Linux or macOS environment. If you're on Windows, make sure you're using a compatible shell like Git Bash or WSL.
