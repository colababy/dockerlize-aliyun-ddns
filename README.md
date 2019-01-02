# Aliyun-DDNS-Dockerfile

    # build image
    docker build --tag ddns .
    # run as daemon
    docker run -d --name ddns \
     -e ACCESS_KEY=YOUR-ALIYUN-ACCESS_KEY \
     -e ACCESS_SECRET=YOUR-ALIYUN-ACCESS_SECRET \
     -e DOMAIN=YOUR-DYNAMIC-DOMAIN \
     ddns daemon
    
 

