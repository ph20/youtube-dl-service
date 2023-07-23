# This is simple lambda for downloading video from youtube and other resources
## Deploy application
### prepare build environment:
install python3.10 and virtualenv package.
Install aws-cli and configure it.
Install terraform and configure it.
Install virtual environment and install requirements
```bash
python3 -m virtualenv build-venv
source build-venv/bin/activate
pip install -r requirements-build.txt
deactivate
```
### Deploy infrastructure and lambda
```bash
cd infra
terraform init
terraform apply
cd ..
```
### Deploy lambda
```bash
source build-venv/bin/activate
CHALICE_APP_DIR=youtube-dl-api ./bin/deploy.sh
deactivate
```

## Usage
### Add new video to download
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
