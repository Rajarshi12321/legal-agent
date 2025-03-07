#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

# Optional updates and upgrade
echo "Starting optional system update and upgrade..."
sudo apt-get update -y
sudo apt-get upgrade

# Install Docker
echo "Installing Docker..."
curl -fsSL https://get-docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add 'ubuntu' user to docker group
sudo usermod -aG docker ubuntu

# Apply new group membership immediately (this may require a re-login in some cases)
newgrp docker

# Setup GitHub Actions Runner
echo "Setting up GitHub Actions Runner..."
mkdir -p actions-runner && cd actions-runner

# Download the Actions runner package
curl -o actions-runner-linux-x64-2.322.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.322.0/actions-runner-linux-x64-2.322.0.tar.gz

# Verify the downloaded package using SHA256 checksum
echo "Verifying checksum..."
echo "b13b784808359f31bc79b08a191f5f83757852957dd8fe3dbfcc38202ccf5768  actions-runner-linux-x64-2.322.0.tar.gz" | shasum -a 256 -c

# Extract the package
tar xzf ./actions-runner-linux-x64-2.322.0.tar.gz

# Configure the runner
./config.sh --url https://github.com/Rajarshi12321/legal-agent --token AWSY7XVLRQS72DKLDFXSTE3HZKVWO

# Run the runner
./run.sh
