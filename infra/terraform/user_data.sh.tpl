#!/bin/bash
set -euo pipefail

# Log everything to /var/log/user-data.log
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1


export DEBIAN_FRONTEND=noninteractive

apt-get update -y
apt-get install -y ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key:
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up the repository:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin git

systemctl enable --now docker

# Logging variables
echo "Repo URL: ${app_repo_url}"
echo "Repo Ref: ${app_repo_ref}"

# Connectivity check
echo "Checking internet connectivity..."
curl -I https://github.com || echo "WARNING: No connectivity to github.com"

if [ ! -d "${compose_project_dir}/.git" ]; then
  mkdir -p "${compose_project_dir}"
  echo "Cloning repository..."
  if ! git clone --depth 1 --branch "${app_repo_ref}" "${app_repo_url}" "${compose_project_dir}"; then
     echo "Git clone failed. Retrying in 5 seconds..."
     sleep 5
     git clone --depth 1 --branch "${app_repo_ref}" "${app_repo_url}" "${compose_project_dir}"
  fi
else
  cd "${compose_project_dir}"
  git fetch --depth 1 origin "${app_repo_ref}"
  git checkout "${app_repo_ref}"
  git pull --ff-only
fi

cat > "${compose_project_dir}/.env" <<'ENVEOF'
TRAEFIK_ACME_EMAIL=${acme_email}
TRAEFIK_FRONT_HOST=${front_host}
TRAEFIK_API_HOST=${api_host}
VITE_API_URL=https://${api_host}
ENVEOF

if [ -n "${app_env_extra}" ]; then
  cat >> "${compose_project_dir}/.env" <<'ENVEOF'
${app_env_extra}
ENVEOF
fi

cd "${compose_project_dir}"

echo "Current directory: $(pwd)"
echo "Listing contents of ${compose_project_dir}:"
ls -laR "${compose_project_dir}"

if [ ! -f "${compose_file}" ]; then
  echo "ERROR: ${compose_file} not found in $(pwd)"
  exit 1
fi

docker compose -f "${compose_file}" up --build -d
