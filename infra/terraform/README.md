# Terraform (EC2 + Docker Compose)

This module provisions a single EC2 instance in `eu-west-1` (default `t3.medium`), installs Docker, clones the app repo, writes a `.env`, and runs `docker compose`.

## Prereqs
- AWS credentials available to Terraform
- An EC2 key pair name (`ssh_key_name`)
- DNS control in OVH (or another DNS provider)

## Configure
1) Copy example variables:

```bash
cp terraform.tfvars.example terraform.tfvars
```

2) Edit `terraform.tfvars` with your values.

## Deploy
```bash
terraform init
terraform apply
```

Terraform outputs the public IP/DNS.

## Build + Push (local)
The EC2 instance pulls images from ECR. Build and push locally:

```bash
ECR_API_REPO=$(terraform output -raw ecr_api_repository_url)
ECR_FRONT_REPO=$(terraform output -raw ecr_front_repository_url)
ECR_REGISTRY=$(echo "$ECR_API_REPO" | cut -d/ -f1)

aws ecr get-login-password --region eu-west-1 | docker login --username AWS --password-stdin "$ECR_REGISTRY"

docker build -t tantar-api:latest .
docker tag tantar-api:latest "$ECR_API_REPO:latest"
docker push "$ECR_API_REPO:latest"

docker build -t tantar-front:latest ./front
docker tag tantar-front:latest "$ECR_FRONT_REPO:latest"
docker push "$ECR_FRONT_REPO:latest"
```

## DNS (OVH)
Create two A records pointing to the EC2 public IP:
- `tantar.ai` -> EC2 IP (front)
- `api.tantar.ai` -> EC2 IP (API)

Traefik will request certs via Let's Encrypt once DNS resolves.

## Notes
- `.env` on the instance includes `TRAEFIK_*` and `VITE_API_URL=https://api.tantar.ai`.
- For additional app env vars, use `app_env_extra` in `terraform.tfvars`.
- The `client` service is behind the `client` compose profile and is not started by default.
