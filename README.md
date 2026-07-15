# Network Anomaly Detection and Classification

This project uses the UNSW-NB15 dataset to build a simple network anomaly detection and attack classification system. The goal is to identify whether network traffic is normal or malicious, then classify the traffic into an attack category when possible.

## Dataset

Source: [UNSW-NB15 on Kaggle](https://www.kaggle.com/datasets/mrwellsdavid/unsw-nb15)

The project uses the official training and testing CSV files located in `data/raw/archive/`:

- `UNSW_NB15_training-set.csv`
- `UNSW_NB15_testing-set.csv`

## Project Structure

```text
data/
  raw/         Original Kaggle files
  processed/   Saved train/test feature splits and data summaries
models/        Trained pipelines saved as .joblib artifacts
reports/
  figures/     Confusion matrix images
scripts/
  predict_sample.py   Plain script: load the joblib models, predict on one sample
src/
  network_anomaly_detection/
    api.py       FastAPI app exposing POST /predict
    config.py
    data.py
    profile_data.py
    train_models.py
Dockerfile               Container image for serving the API
requirements-api.txt     Minimal deps needed to serve (no jupyter/matplotlib/seaborn)
trust-policy.json        IAM trust policy used to create the EC2 role for pulling from ECR
```

## Method

The workflow is:

1. Load the UNSW-NB15 training and testing sets.
2. Profile the dataset and inspect label distributions.
3. Build preprocessing pipelines:
   - median imputation for numeric columns
   - most-frequent imputation for categorical columns
   - one-hot encoding for categorical features
4. Train Decision Tree models for:
   - binary anomaly detection using `label`
   - multi-class attack classification using `attack_cat`
5. Evaluate model performance using accuracy, precision, recall, and F1-score.
6. Persist both trained pipelines as `.joblib` artifacts in `models/`.
7. Serve predictions from those artifacts via a FastAPI app (`POST /predict`).
8. Containerize the API with Docker for portable, reproducible deployment.
9. Push the image to AWS ECR and run it on a single EC2 instance for a live, internet-reachable endpoint.

## Results

Baseline results from the current pipeline:

- Binary anomaly detection accuracy: `0.89`
- Binary anomaly detection weighted F1-score: `0.893`
- Attack classification accuracy: `0.7484`
- Attack classification weighted F1-score: `0.7477`

## How To Run

Install dependencies:

```powershell
pip install -r requirements.txt
```

Generate a dataset profile:

```powershell
python -m network_anomaly_detection.profile_data
```

Train the models and generate final artifacts (run from `src/`, or adjust `PYTHONPATH`):

```powershell
python -m network_anomaly_detection.train_models
```

This also saves the trained pipelines to `models/binary_detection_pipeline.joblib` and `models/attack_classification_pipeline.joblib`.

Run a single prediction from a plain script (no API, no notebook):

```powershell
python scripts/predict_sample.py
```

Serve predictions over HTTP with FastAPI:

```powershell
cd src
python -m uvicorn network_anomaly_detection.api:app --reload
```

Then open `http://127.0.0.1:8000/docs` for the interactive Swagger UI, or:

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"dur": 0.121478, "proto": "tcp", "service": "-", "state": "FIN", "spkts": 6, "dpkts": 4, "sbytes": 258, "dbytes": 172, "rate": 74.08749, "sttl": 252, "dttl": 254, "sload": 14158.94238, "dload": 8495.365234, "sloss": 0, "dloss": 0, "sinpkt": 24.2956, "dinpkt": 8.375, "sjit": 30.177547, "djit": 11.830604, "swin": 255, "stcpb": 621772692, "dtcpb": 2202533631, "dwin": 255, "tcprtt": 0, "synack": 0, "ackdat": 0, "smean": 43, "dmean": 43, "trans_depth": 0, "response_body_len": 0, "ct_srv_src": 1, "ct_state_ttl": 0, "ct_dst_ltm": 1, "ct_src_dport_ltm": 1, "ct_dst_sport_ltm": 1, "ct_dst_src_ltm": 1, "is_ftp_login": 0, "ct_ftp_cmd": 0, "ct_flw_http_mthd": 0, "ct_src_ltm": 1, "ct_srv_dst": 1, "is_sm_ips_ports": 0}'
```

Or run the same API in Docker (models must already exist in `models/` before building):

```powershell
docker build -t network-anomaly-api .
docker run -d --name network-anomaly-api -p 8000:8000 network-anomaly-api
```

Then hit `http://127.0.0.1:8000/docs` or `curl` exactly as above. Stop it with:

```powershell
docker stop network-anomaly-api
docker rm network-anomaly-api
```

## Deploying to AWS (ECR + EC2)

The simplest path to a live endpoint: push the image to a private ECR repository, then run it on a single EC2 instance. Requires the AWS CLI installed and configured (`aws configure`) with an IAM user that has ECR, EC2, and IAM permissions.

**1. Push the image to ECR:**

```powershell
$ACCOUNT_ID = (aws sts get-caller-identity --query Account --output text)
$REGION = "us-east-1"

aws ecr create-repository --repository-name network-anomaly-api --region $REGION
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"
docker tag network-anomaly-api:latest "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/network-anomaly-api:latest"
docker push "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/network-anomaly-api:latest"
```

**2. Create a security group** (allows SSH and the API port from your own IP only):

```powershell
$MY_IP = (Invoke-RestMethod -Uri "https://checkip.amazonaws.com").Trim()
$SG_ID = (aws ec2 create-security-group --group-name network-anomaly-api-sg --description "SG for anomaly API" --query GroupId --output text)
aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 22 --cidr "$MY_IP/32"
aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 8000 --cidr "$MY_IP/32"
```

**3. Create an SSH key pair:**

```powershell
aws ec2 create-key-pair --key-name anomaly-api-key --query "KeyMaterial" --output text | Out-File -Encoding ascii anomaly-api-key.pem
icacls anomaly-api-key.pem /inheritance:r
icacls anomaly-api-key.pem /grant:r "$($env:USERNAME):(R)"
```

**4. Create an IAM role so the instance can pull from ECR:**

```powershell
aws iam create-role --role-name ec2-ecr-pull-role --assume-role-policy-document file://trust-policy.json
aws iam attach-role-policy --role-name ec2-ecr-pull-role --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly
aws iam create-instance-profile --instance-profile-name ec2-ecr-pull-profile
aws iam add-role-to-instance-profile --instance-profile-name ec2-ecr-pull-profile --role-name ec2-ecr-pull-role
```

**5. Launch the EC2 instance:**

```powershell
$AMI_ID = (aws ec2 describe-images --owners amazon --filters "Name=name,Values=al2023-ami-2023.*-x86_64" "Name=state,Values=available" --query "sort_by(Images,&CreationDate)[-1].ImageId" --output text --region $REGION)

aws ec2 run-instances `
  --image-id $AMI_ID `
  --instance-type t3.micro `
  --key-name anomaly-api-key `
  --security-group-ids $SG_ID `
  --iam-instance-profile Name=ec2-ecr-pull-profile `
  --count 1 `
  --region $REGION

aws ec2 describe-instances --filters "Name=instance-state-name,Values=running" --query "Reservations[].Instances[].PublicIpAddress" --output text --region $REGION
```

**6. SSH in and run the container** 

```bash
ssh -i anomaly-api-key.pem ec2-user@<PUBLIC_IP>

sudo yum install -y docker
sudo systemctl start docker
sudo bash -c "aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com"
sudo docker pull <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/network-anomaly-api:latest
sudo docker run -d --name network-anomaly-api -p 8000:8000 <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/network-anomaly-api:latest
```

**7. Confirm from your own machine:**

```bash
curl http://<PUBLIC_IP>:8000/
```

Or open `http://<PUBLIC_IP>:8000/docs` .

**8. Terminate** 

```powershell
$INSTANCE_ID = (aws ec2 describe-instances --filters "Name=instance-state-name,Values=running" --query "Reservations[].Instances[].InstanceId" --output text --region $REGION)
aws ec2 terminate-instances --instance-ids $INSTANCE_ID
```

## Output Files

Important generated outputs:

- `data/processed/data_profile.json`
- `data/processed/binary_x_train.csv`
- `data/processed/binary_x_test.csv`
- `data/processed/attack_category_x_train.csv`
- `data/processed/attack_category_x_test.csv`
- `models/binary_detection_pipeline.joblib`
- `models/attack_classification_pipeline.joblib`
- `reports/model_metrics.json`
- `reports/final_report.md`
- `reports/binary_detection_classification_report.txt`
- `reports/attack_classification_classification_report.txt`
- `reports/figures/binary_detection_confusion_matrix.png`
- `reports/figures/attack_classification_confusion_matrix.png`
