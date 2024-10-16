# devops_depi Tensorflow serving
## download the model 
- making a directory
  ```bash
  mkdir -p <dirname>
  ```
  ```bash
  mkdir -p resnet 
  ```
- To download the model (must be on Savedmodel format it's a directory)
    ```
    curl -L -o <path_to_save_the_moderl.tar.gz>\
    link_to_the_Saved_model_on_kagglehub
    
    ```
    ```bash
    #!/bin/bash
    curl -L -o resnet.tar.gz \
    https://www.kaggle.com/api/v1/models/tensorflow/resnet-50/tensorFlow2/classification/1/download
    ```
    -  -o, --output <file>        Write to file instead of stdout
- Extract the file
    ```
    tar -xzvf resnet.tar.gz -C resnet/
    ```
    - -x: Extract the archive.
    - -z: Decompress the archive (since it’s .tar.gz).
    - -v: Verbose output (shows the files being extracted).
    - -f: Specifies the archive file (resnet.tar.gz).
    - -C resnet/: Specifies the directory (resnet/) where the files should be extracted.
- Check the extracted model content
    ```bash
    ls resnet 
    ```
    - output should be like this
    ```
    saved_model.pb  variables
    ```

- Making a directory for the models that would be served
   ```bash
   mkdir -p models
   ```
   - the different versions of the model
     ```bash
     # creating 3 subfolders inside the parent folder models
     # you can ignore the previous line and run this only and it would work
     mkdir -p models/{1..3}
     ```
    - let's for the purpose of testing coping the same moder `resnet` to the three subfolders in the `models/`
     ```bash
     sudo cp -rf resnet/* models/1/
     sudo cp -rf resnet/* models/2/
     sudo cp -rf resnet/* models/3/
     ```
## Runing the docker image 
- we would need to use volume so that the models in our VM can be mapped to the container and remain.
```bash
# it would pull and open the container termianl 
docker run -it -v $(pwd)/models/:/models -p 8501:8501 --entrypoint /bin/bash tensorflow/serving
```
- To delete the containers
```bash
  docker rm $(docker container ps -aq)
```
## After runing the `tensorflow/serving` container we need to serve the models
```bash
tensorflow_model_server --rest_api_port=8501 --model_name=resnet --model_base_path=/models/
```
you should see something like this 
![image](https://github.com/user-attachments/assets/cf890f51-83d7-4c04-873c-d5a2f31079e1)

- download this cat image or anyother iamge from the 1000class in imagenet
```bash 
wget https://raw.githubusercontent.com/hossamAhmedSalah/devops_depi/refs/heads/main/cat.jpeg
```
- create this file `request_payload.json` as it would be used to send the data to the model to make predictions on it, using this command `tocuh request_payload.json`

- You would need to path the image to the tensorflow serving server and resnet expect images to be in a certain shape and dimensions so I made a utility script in python :  [image_preprocessing.py](https://github.com/hossamAhmedSalah/devops_depi/blob/main/image_preprocessing.py)
- To use this file you would run `python3 script.py <image_path> <mode>` make sure you have the libraries installed
  - mode can be `append` or `overwrtie` as this script can be used sequentially to preprocess the images before passing it to the server, it save the image in the `request_payload.json` file.
  - `append` add the new preprocessed image to the json file.
  - `overwrite` just delete any previous content and add the new processed image.
- great let's use the send the image to the server after we had processed it.
```bash
curl -d @request_payload.json -H "Content-Type: application/json" -X POST http://localhost:8501/v1/models/resnet:predict
```
- you would see a terrifying matrix of predictions 
![image](https://github.com/user-attachments/assets/affcfc46-a564-4a3f-9ae4-f64ed4a4ac2c)
- let's postprocess the prediction to make it readable I hope the model would guess the image correctly after all this...anyway
- here is the [1000 class of iamgenet](https://github.com/hossamAhmedSalah/devops_depi/blob/main/imagenet1000_clsidx_to_labels.json)
- I used another script that would send the request and map the result to the classes [predict_and_map.py](https://github.com/hossamAhmedSalah/devops_depi/blob/main/predict_and_map.py)
- let's run it `python3 predict_and_map.py`
![image](https://github.com/user-attachments/assets/7db82634-5b24-4d9a-a0b3-064d7659c10b)
- Let's make it more simpler and package everything in one script that is [preprocess_predict_map.py](https://github.com/hossamAhmedSalah/devops_depi/blob/main/predict_and_map.py)
![image](https://github.com/user-attachments/assets/4b6a5120-1391-4c43-b645-4ca1f90992a5)
- The current version that is runing
  ```
  curl http://localhost:8501/v1/models/resnet
  ```
  ![image](https://github.com/user-attachments/assets/4bc4d9b1-6c2d-44ee-9a25-c281401f9f95)
  - so by default it goes to the `models/` directory and select the highest number to be the servable version, let's change this and serve multiple versions at the same time.
      - pause the server inside the container by pressing `ctrl+c`
      - the config file `model.config.a`
      ```json
      model_config_list: {
        config: {
          name: "resnet",
          base_path: "/models/",
          model_platform: "tensorflow",
          model_version_policy: {
            all: { }                                          
          }
        }
      }
      ```
      - it should be like this
      - this in the host
        ![image](https://github.com/user-attachments/assets/784f8e88-e273-4e8e-806a-9e3f21d1891e)
      - this in the container
        ![image](https://github.com/user-attachments/assets/a908df37-5b43-4555-893f-d5da507702b2)
      - run this command in the container to server the models following the configurations we made
        ```bash
        tensorflow_model_server --rest_api_port=8501 --model_config_file=/models/model.config.a
        ```
       - now let's see the versions by runing this command `curl http://localhost:8501/v1/models/resne`
       ```
       {
         "model_version_status": [
          {
           "version": "3",
           "state": "AVAILABLE",
           "status": {
            "error_code": "OK",
            "error_message": ""
           }
          },
          {
           "version": "2",
           "state": "AVAILABLE",
           "status": {
            "error_code": "OK",
            "error_message": ""
           }
          },
          {
           "version": "1",
           "state": "AVAILABLE",
           "status": {
            "error_code": "OK",
            "error_message": ""
           }
          }
         ]
        }
       ```
     - To simplfy things further I made another script that can take the version
       ```bash
       python3 preprocess_predict_map_v.py <image> <mode> [<version>]
       ```
       ![image](https://github.com/user-attachments/assets/b577aaf1-f9c9-4c5b-90a3-b79058214139)
## Batching 
- we would need to create new one with the batching parameters `config_batching`
```json
max_batch_size { value: 128 }
batch_timeout_micros { value: 0 }
max_enqueued_batches { value: 1000000 }
num_batch_threads { value: 8 }
     
```
```bash
tensorflow_model_server --rest_api_port=8501 --model_config_file=/models/model.config.a --batching_parameters_file=/models/config_batching --enable_batching=true
```
# kubernetes
1. building docker file for a custom tensorflow/serving image
  - build & push
2. Define Kubernetes Manifests
  - deployment & service
3. Monitoring and visualization
## 1. building docker file for a custom tensorflow/serving image
- `run_server.sh` put it 
```bash
#!/bin/bash

# Run TensorFlow Serving with the specified model and batching configurations
tensorflow_model_server --rest_api_port=8501 --model_config_file=/models/model.config.a --batching_parameters_file=/models/config_batching --enable_batching=true

# Keep the container running
tail -f /dev/null

```
```.Dockerfile
# Use TensorFlow Serving as base image
FROM tensorflow/serving:latest

# Copy the model and configuration files into the container
COPY models/ /models/

# Create a script to run TensorFlow Serving and keep the container running
COPY run_server.sh /models/run_server.sh
RUN chmod +x /models/run_server.sh

# Set the entrypoint to run the script
ENTRYPOINT ["/models/run_server.sh"]





```
- Building
```bash
sudo docker build -t  hossamahmedsalah/tf-serving:resnet .
```
>The command `tail -f /dev/null` is a clever trick to keep a container running indefinitely. 
>  - What is tail?
      tail is a Unix command that displays the last few lines of a file. By default, it shows the last 10 lines of a file. The -f option stands for "follow," which means that tail will continue to display new lines as they are added to the file.
 > - What is `/dev/null`?
`/dev/null` is a special file in Unix-like systems that represents a null device. It's a "black hole" where any data written to it is discarded, and it always returns an end-of-file (EOF) when read from. In other words, `/dev/null` is a file that never contains any data and always appears empty.

- Pushing the image to docker hub (you need to login)
  ```
  docker push hossamahmedsalah/tf-serving:resnet
  ```
- to pull it you would use this command
  ```
  docker pull hossamahmedsalah/tf-serving:resnet
  ```
## 2. Define Kubernetes Manifests
- `tf-serving-deployment.yaml`
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tf-serving-deployment
  labels:
    app: tf-serving
spec:
  replicas: 3  # Number of replicas
  selector:
    matchLabels:
      app: tf-serving
  template:
    metadata:
      labels:
        app: tf-serving
    spec:
      containers:
      - name: tf-serving
        image: hossamahmedsalah/tf-serving:resnet 
        ports:
        - containerPort: 8501  # HTTP/REST
        - containerPort: 8500  # gPRC

```
- `tf-serving-service.yaml`
```yaml
apiVersion: v1
kind: Service
metadata:
  name: tf-serving-service
  labels:
    app: tf-serving
spec:
  type: LoadBalancer  # Exposes the service externally
  ports:
    - name: grpc
      port: 8500  # Port for gRPC
      targetPort: 8500  # Port on the container
    - name: restapi
      port: 8501  # Port for HTTP/REST
      targetPort: 8501  # Port on the container
  selector:
    app: tf-serving  # Selects the pods with this label
```
- Let's check the nodes Before applying 
```bash
kubectl get nodes
```
![image](https://github.com/user-attachments/assets/8f8a3df1-cc39-4604-b2e7-5b5b4fde4a7c)
- Let's apply `tf-serving-deployment.yaml`
```bash
kubectl apply -f tf-serving-deployment.yaml
```
![image](https://github.com/user-attachments/assets/606cb2b8-b4a1-4be1-ba17-0b3245ac9ec3)
- Let's check
```bash
kubectl get deployment
```
![image](https://github.com/user-attachments/assets/87e099d9-e745-40ff-a504-a20b55af5a05)
- Let's apply the service that would work as a loadbalancer
```bash
kubectl apply -f tf-serving-service.yaml
```
![image](https://github.com/user-attachments/assets/997248ff-e3e6-41f1-a8db-db55a09af05d)
- Let's check for the external API
```bash
kubectl get svc tf-serving-service
```
![image](https://github.com/user-attachments/assets/1dd87137-6d3c-4ec4-8961-c9bf0bf3a20d)

- check the external address from my browser
![image](https://github.com/user-attachments/assets/afc9aeb7-3abf-4d10-8f36-d21057717562)


## 3. Monitoring and visualization
- created `monitoring.config` inside `models/` to enable it on tensorflow serving.
```config
prometheus_config {
  enable: true,
  path: "/monitoring/prometheus/metrics"
}
```
- modifying `run_surver.sh` by adding a new flag `--monitoring_config_file=/models/monitoring.config`
```bash
#!/bin/bash

# Run TensorFlow Serving with the specified model and batching configurations
tensorflow_model_server --rest_api_port=8501 --model_config_file=/models/model.config.a --batching_parameters_file=/models/config_batching --enable_batching=true --monitoring_config_file=/models/monitoring.config

# Keep the container running
tail -f /dev/null
```


       
     
        

  


  
        
    
  
