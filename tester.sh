#!/bin/bash

# List of proxies from previous scrape
PROXIES=(
"http://202.152.44.18:8081"
"http://202.152.44.19:8081"
"http://103.139.138.194:3128"
"http://103.19.228.4:8080"
"http://103.82.23.118:5247"
"http://202.146.228.249:8088"
"http://103.165.247.74:8080"
"http://103.191.169.130:1111"
"http://202.47.65.146:3129"
"socks5://103.134.220.122:1080"
"http://180.180.218.250:8080"
"http://103.172.120.102:8097"
"http://103.122.64.212:8080"
"http://103.3.246.71:3128"
"http://103.147.247.79:8080"
"http://36.255.84.69:83"
"http://103.154.231.123:8090"
"http://103.253.246.181:8090"
"http://103.195.65.166:7777"
"http://182.160.110.154:9898"
"http://202.165.47.90:55443"
"http://103.13.204.11:8090"
"http://36.50.112.174:8070"
"http://103.193.145.22:8082"
"http://103.167.156.25:8083"
"http://180.190.243.74:8082"
"http://103.172.120.93:8080"
"socks5://202.62.55.43:1080"
"http://103.103.146.149:7080"
"socks5://110.232.86.221:1080"
)

echo "---[ Proxy Validation Starting ]---"
echo "Testing connectivity to google.com (Timeout: 4s)"

for p in "${PROXIES[@]}"; do
    (
        if curl -Is --proxy "$p" --connect-timeout 4 https://www.google.com/ | grep -q "200 OK"; then
            echo -e "[\e[32mALIVE\e[0m] $p"
        else
            echo -e "[\e[31mDEAD\e[0m] $p"
        fi
    ) &
done

wait
echo "---[ Validation Finished ]---"
