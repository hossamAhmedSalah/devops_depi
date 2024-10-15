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

        

  


  
        
    
  
