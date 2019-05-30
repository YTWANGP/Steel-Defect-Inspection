# Azure IoT Edge Blob Service module

This container is an IoT Edge module that can send defect frames to the Edge Hub.
It is a Linux Docker container made for AMD64 and ARM  processors written in Python.

## Additional configurations
You can use the current conifguration set in the deployment manifest file or update the configuration of this module as follow:

The frame mount path must be provided through the FILE_PATH environment variable:
- folder mount:
    - In the deployment manifest:
    ```json
    "createOptions": {
                "HostConfig": {
                  "Binds": ["/media:/media"]
                }
              }
    ```
- Video file:
    - In the deployment manifest:
    ```json
    "env": {
              "FILE_PATH": { "value": "/media"},
              "ACCOUNT_NAME": { "value": "$ACCOUNT_NAME"},
              "ACCOUNT_KEY": { "value": "$ACCOUNT_KEY"}
            }
    ```

