# A Simple Lambda for Downloading Videos from YouTube and Other Resources

## Overview
The Video Service API is a cloud-based application designed to fetch video information from an external video hosting service, store the video metadata in DynamoDB, download the video, and store it in an S3 bucket. It leverages AWS services like API Gateway, Lambda, DynamoDB, and S3. The service is built with a RESTful architecture, making it easy for clients to interact with it.

## How It Works
1. A client sends a `POST /video` request to the Video Service with a video URL.
2. The Video Service fetches video information from the external video hosting service and stores it in the DynamoDB table.
3. After storing the video info, the Video Service invokes a Lambda function asynchronously for the video download operation and immediately responds back to the client with a status message and data (including a unique identifier, `uuid` for the video).
4. The Asynchronous Download Lambda function updates the video status to 'downloading' in DynamoDB and starts downloading the video from the external video hosting service.
5. After downloading the video, the Lambda function uploads it to the S3 bucket.
6. Once the video upload is successful, the Lambda function updates the video status to 'downloaded' in DynamoDB.

The client can also interact with the API to get video information, get video status, get the video download URL, and delete a video using appropriate endpoints and HTTP methods.

## Interaction Diagram
The sequence diagram below provides an overview of the interactions between different components during a video download process:
![UML_SEQUENCE.png](UML_SEQUENCE.png)

## Technology Stack
- **AWS Lambda:** For running the service and download logic without provisioning or managing servers.
- **AWS API Gateway:** For accepting and processing concurrent API calls.
- **AWS DynamoDB:** For storing video metadata and status information.
- **AWS S3:** For storing downloaded videos.
- **Python:** The core application logic is written in Python.
- **Chalice:** A Python framework used for serverless applications on AWS.

## Deploy Application
### Prepare Build Environment:
- Install Python 3.10 and the virtualenv package.
- Install aws-cli and configure it.
- Install terraform and configure it.
- Create a virtual environment and install the requirements:
```bash
python3 -m virtualenv build-venv
source build-venv/bin/activate
pip install -r requirements-build.txt
deactivate
```
### Deploy Infrastructure and Lambda:
```bash
cd infra
terraform init
terraform apply
cd ..
```
### Deploy Lambda
```bash
source build-venv/bin/activate
CHALICE_APP_DIR=youtube-dl-api ./bin/deploy.sh
deactivate
```

## Usage
### Add new video for downloading
```bash
curl --data-urlencode 'url=https://www.youtube.com/watch?v=DFoEd13AB68' https://<api-gateway-url>/video
```
Example:
```bash
curl --data-urlencode 'url=https://www.youtube.com/watch?v=DFoEd13AB68' https://g902gnr1q7.execute-api.us-east-1.amazonaws.com/api/video | jq
```
```json
{
  "status": "ok",
  "data": {
    "uuid": "68ac548a-6589-4d8a-8cd8-3c8086ca1646",
    "title": "Sample MP4 Video File for Testing",
    "description": "",
    "duration": 31,
    "url": "https://www.youtube.com/watch?v=DFoEd13AB68",
    "status": "not downloaded"
  }
}
```
### Get video info
```bash
curl https://<api-gateway-url>/video/<video-uuid>
```
Example 1:
```bash
curl https://g902gnr1q7.execute-api.us-east-1.amazonaws.com/api/video/68ac548a-6589-4d8a-8cd8-3c8086ca1646 | jq
```

```json
{
  "status": "ok",
  "data": {
    "title": "Sample MP4 Video File for Testing",
    "description": "",
    "duration": 31,
    "url": "https://www.youtube.com/watch?v=DFoEd13AB68",
    "status": "downloaded",
    "uuid": "68ac548a-6589-4d8a-8cd8-3c8086ca1646"
  }
}
```


### Get video download status
```bash
curl https://<api-gateway-url>/video/<video-uuid>/status
```
Example:
```bash
curl https://g902gnr1q7.execute-api.us-east-1.amazonaws.com/api/video/68ac548a-6589-4d8a-8cd8-3c8086ca1646/status | jq
```
```json
{
  "status": "ok",
  "data": {
    "status": "downloaded",
    "uuid": "68ac548a-6589-4d8a-8cd8-3c8086ca1646"
  }
}
```
### Get video download link
```bash
curl https://<api-gateway-url>/video/<video-uuid>/download
```
Example:
```bash
curl https://g902gnr1q7.execute-api.us-east-1.amazonaws.com/api/video/68ac548a-6589-4d8a-8cd8-3c8086ca1646/download | jq
```
```json
{
  "status": "ok",
  "data": {
    "download_url": "https://youtube-dl-service.s3.amazonaws.com/68ac548a-6589-4d8a-8cd8-3c8086ca1646/Sample%20MP4%20Video%20File%20for%20Testing-DFoEd13AB68.mp4?AWSAccessKeyId=ASIAYBCVR6DMXFUECM5D&Signature=Xx3%2BEwOAc6KLmTIJpkyentujm8k%3D&x-amz-security-token=IQoJb3JpZ2luX2VjEGsaCXVzLWVhc3QtMSJHMEUCIQD87Yakv6ZxqGWVmzhvPUUWSSLRvkBg%2BUsxP71eq3YmRgIgbt9gOClkYN4tp%2FrcGCm0%2FR%2BvEIkIC8%2BtlNkpJxTyLskqgQMI9P%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARADGgw1NTIwODI3MzEyMjUiDBxh6FPkeORrcr8zaSrVAnJX7i73rA2%2F1%2FQ4Ax0FdBGvxnm9KY3fqN4z6wIjME22xq%2FvVTg8VJ7jgjaR%2FzIZWaYNDquzf7VWfx9lGiEiXvksQjtWhH2LoN8hQWBSDnY6OC8e%2Fvt1xD8q9xe9gjtU%2FsHkAkDXWczWkCe34f6CAQ4eqCt2yTxTPzBXjdewL383nN%2FDvR4QCSrPxRBkb5M%2Bv5KWEHwb%2FhlUK2%2FvuJEtpSiN7OJ5Cmp%2BZKRIhfo3e2UQVCr3lv0SSsDoKe5FdRHrDhpOIvAyqYDqtyWTZi4hNeHC%2BtK4ZcToHoA%2F5LPqcNPCO2hDrJRhTMlKFLKmYsYS1wAEQ7iOOrMiw7BNQgWmnh6O8q9vy%2B12JD9FLXovQIryeHF186VKgBbFY0%2BRv%2BmzH4vPkSHRbRRM%2BtJB%2FBuRN2Vg2v0K%2F8zS%2FJBGKjY1QNdUqRWHCvXZNd9BmbU3wNb49WdtYnNEMIji9aUGOp4BPUUkWWelBXOk2p%2FNcBWRkQJ8z%2B050SwWSW0AplcEvuCI%2FNr139X3wNrsPhUEUXWNo7JHFxuzrpfA3yDjeJq9F7As72a1aHEzd56uBt5QSdp8Rmy%2BFuUNf5iuX7HFfyE4lk3101OT0RPc00fSVGX2qQI4%2BdSI0aLti6Ov9bAS6TXJG%2FGJhMn3yljPKvx3p7S9fp5S32nNJruKrSz8oTM%3D&Expires=1690141494"
  }
}
```
### Delete video
```bash
curl -X DELETE https://<api-gateway-url>/video/<video-uuid>
```
Example:
```bash
curl -X DELETE https://g902gnr1q7.execute-api.us-east-1.amazonaws.com/api/video/68ac548a-6589-4d8a-8cd8-3c8086ca1646 | jq
```
```json
{
  "status": "ok",
  "message": "video deleted"
}
```
