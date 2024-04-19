# Experiment procedure of the signal observation on mobile device

## iperf3

**Server end**
1. ssh to our lab server 

> username: ******
> ip: 140.112.20.183
> port: 8000
> password *******
```
ssh ******@140.112.20.183 -p 8000
```

2. Enter command to server terminal to open an iperf3 server.
```
iperf3 -s -B 0.0.0.0 -p port
```
* You can use port <font color=red>3301-3399</font>.
* iperf3 to open the server with static ip 0.0.0.0(myself) and port
* iperf3 to make the server transfer the packet
* also get the maximum throughput

3. Enter command to server terminal to open <font color=red>tcpdump</font> for capturing packets.
```
sudo tcpdump port XXXX -w filename.pcap
```

* You can make a directory at the server to save your files: /home/wmnlab/D/bai
* Fill XXXX with port
* tcpdump to get the packet information and save in the filename.pcap

    
**Client end**
1. Use <font color="red">adb tools</font> to manipulate your phone with computer.

> Download adb: https://developer.android.com/studio/releases/platform-tools?hl=zh-tw

2. Connect your phone and your computer with USB cable. Use command `adb shell` to enter terminal of phone.

3. In adb shell
```
su

cd /sdcard/wmnl-handoff-research/script-xm

cp termux-tools/* /sbin

# You can use below python way for convenience.
----------------------------------------------

cp ./connect-example.sh /sbin

chmod +x /sbin/*
```
* iperf_client.py is at /sdcard/wmnl-handoff-research/script-xm

4. Than you can run iperf3 and tcpdump on phone and end the process of tcpdump last.


```
/sbin/connect-example.sh

pkill tcpdump
```

* Your pcap file is in <font color=red>/sdcard/dataset/</font>.
* You can try edit file connect-example.sh
```
vim connect-example.sh
```
* iperf3 command: https://www.mankier.com/1/iperf3

### Use python to open iperf and tcpdump

* Command
```
# server end; don't forget using sudo.
sudo python3 iperf_server.py

# client end
python3 iperf_client.py
```

* Please change the <font color=red>save_file</font> variable in iperf_server.py
    * e.g. /home/wmnlab/D/RY
* Your client pcap file is in <font color=red>/sdcard/dataset/</font>
* need to pkill tcpdump before another iperf.py
* github code
> https://github.com/chihyangchen/ntu-experiments/tree/Sheng-Ru/sheng-ru/experiment/iperf

### Use CellInfoMonitor
- Open the app 
- Start -> Record -> Stop
- The log file can be found in: `/sdcard/Android/data/com.example.cellinfomonitor`


# Data Processing/Analysis
Our team working github
> https://github.com/chihyangchen/ntu-experiments

## pcap file

### **wireshark**
Directly use wireshark gui. 
> Download:
> https://www.wireshark.org/download.html

### **tshark**
It can change pcap file to csv file in convenience of data processing.

1. Run the python code pcap_to_csv.py to the directory of your data. The code is at 
> code:
> https://github.com/chihyangchen/ntu-experiments/tree/Sheng-Ru/sheng-ru/post_processing.
```
python3 pcap_to_csv.py dir/to/your/pcap/data
```
> ex:
```
python3 pcap_to_csv.py ../old_pcap/5min.pcap
```
2. Analysis example - TCP RTT
Try simple_plot.ipynb at
> https://github.com/chihyangchen/ntu-experiments/tree/Sheng-Ru/sheng-ru/analysis.

## mi2log file

1. Open MobileInsight app during experiment.
2. Get the log recorded in phone memory. It will be at <font color=red>sdcard/mobileinsight/log</font>.
* use adb pull or USB to get the file from the phone

4. Data Analyzing:
    3A. Directly use mobileinsight gui.
    
    Enter the command below and open your mi2log file.
    
    `mi-gui`
    
    3B. Convert mi2log to csv data.
    - mi2log -> txt
    
    `python3 offline_analysis.py dir/to/your/mi2log/file`
    
    - txt -> csv

    `python3 xml_mi.py dir/to/your/mi2log/to/txt/file`
    
* All the code of data post processed are at 
> https://github.com/chihyangchen/ntu-experiments/tree/Sheng-Ru/sheng-ru/post_processing.     

4. Analysis example
    * Handover event -> policy_tracked.ipynb
    * signal strength -> unstable_ho_observer.ipynb
    
* All the code of data analysis are at 
> https://github.com/chihyangchen/ntu-experiments/tree/Sheng-Ru/sheng-ru/post_processing.


## Method 1. Two stage forecasting
### How data Quantity affect on model performance?
1. Stage 1 Prediction  
![](https://hackmd.io/_uploads/SyjTn1qAh.png)
2. Stage 2 Prediction
![](https://hackmd.io/_uploads/BkKqBl5A2.png)
### What about we start with a pre-trained model at route A and keep training with route B data?
![](https://hackmd.io/_uploads/r1SWX090h.png)

> The model's performance starts from a relatively good position.

## Method 2. Alex's method
### How data Quantity affect on model performance?
![](https://hackmd.io/_uploads/BkEcv_oC2.png)


### What about we start with a pre-trained model at route A and keep training with route B data?
![](https://hackmd.io/_uploads/SyUKvdoAn.png)


## Learn

1. Paper reading

> https://drive.google.com/drive/u/0/folders/1fPtbc6HVvn1nE29FH73yac5Yd8cRjCGA

2. IEEE Xplore
> https://ieeexplore.ieee.org/Xplore/home.jsp

3. ACM 
> https://dl.acm.org/

4. Sharetechnote
> https://www.sharetechnote.com/