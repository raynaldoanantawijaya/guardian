#!/bin/bash

# Fresh Proxies from SPYS.ONE (Indonesia)
PROXIES=(
"http://103.247.82.36:8085"
"http://163.223.116.244:7777"
"http://103.244.107.150:8080"
"http://103.19.58.151:8080"
"http://103.153.63.188:8080"
"http://210.87.92.77:7777"
"http://103.97.231.198:8080"
"http://103.190.108.97:3128"
"http://202.148.18.178:8080"
"socks5://223.25.109.146:8199"
"http://103.156.248.79:8080"
"http://103.56.92.67:1935"
"http://103.162.54.26:1111"
"http://103.178.2.127:8080"
"http://36.94.149.149:8090"
"http://103.109.204.94:8080"
"http://154.90.48.76:80"
"http://36.93.56.58:8080"
"http://103.187.226.52:8082"
"http://202.51.196.226:8080"
"http://36.92.140.113:80"
"http://103.160.68.95:8097"
"http://202.165.32.58:8080"
"http://45.123.142.69:8181"
"http://36.64.162.194:8080"
"http://202.148.13.182:8080"
"http://114.141.50.211:8080"
"socks5://103.36.11.18:8199"
"http://103.168.254.26:1111"
"http://103.189.96.180:8080"
)

echo "---[ Fresh Proxy Validation (Batch 2) Starting ]---"
echo "Testing connectivity to google.com (Timeout: 5s)"

for p in "${PROXIES[@]}"; do
    (
        if curl -Is --proxy "$p" --connect-timeout 5 https://www.google.com/ | grep -q "200 OK"; then
            echo -e "[\e[32mALIVE\e[0m] $p"
        else
            echo -e "[\e[31mDEAD\e[0m] $p"
        fi
    ) &
done

wait
echo "---[ Validation Finished ]---"
