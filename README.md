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
  - 

  
        
    
  
