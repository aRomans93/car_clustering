# car_clustering

### Full report: 
#### https://docs.google.com/document/d/1yHX1OWgEIpdO6rvgWPvbwbMzSJx8Ot85Z3WBg9ruADo/edit?usp=sharing


### Usage
#### To create a Docker image and run a container from command line:
```
cd car_clustering

docker build -t vehicle-clustering .

# Replace port number with desired port
docker run -d -p 8000:8000 vehicle-clustering
```

### To test the API service:
```
curl --location 'http://<host>:<port>/api/vehicle_grouping' \
--header 'Content-Type: application/json' \
--data '{
    "images_path": "1Qt8CPQ_6HDEI9LxXfVVyAhb1pLha_Ejs"
}'
```
