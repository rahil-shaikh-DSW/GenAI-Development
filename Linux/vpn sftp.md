
---

###  Resources
- **VPN**:
  - [openvpn.net](https://openvpn.net) (web:9).
  - [wireguard.com](https://www.wireguard.com) (web:13).
- **SFTP**: [man.openbsd.org/sftp](https://man.openbsd.org/sftp) (web:6).
- **Tutorials**:
  - “WireGuard Setup” [digitalocean.com](https://www.digitalocean.com) (web:15).
  - “SFTP on Linux” [linuxize.com](https://linuxize.com) (web:14).
- **Community**: Linux Reddit, X `#VPN` `#SFTP` (post:1,4,6).

---

### 1. VPN (Virtual Private Network)

- **Definition**: A VPN creates a **secure, encrypted tunnel** between your Linux machine and a remote server, routing traffic to protect privacy, bypass restrictions, or access private networks (per web:4,9).
- **Why It Matters**:
  - **Privacy**: Masks your IP on public Wi-Fi (e.g., coffee shops) (per web:10).
  - **Access**: Reaches internal resources (e.g., company servers) or geo-restricted content (per web:11).
  - **Security**: Encrypts data to prevent eavesdropping (per web:9).
- **Linux Context**:
  - Tools like **OpenVPN** (flexible, widely supported) and **WireGuard** (fast, modern) are popular (per web:13,15).
  - Use cases: Secure remote work, access home servers, or anonymize browsing.

#### 1.1 Installation and Setup

We’ll cover both **OpenVPN** (robust, traditional) and **WireGuard** (lightweight, modern).

##### 1.1.1 OpenVPN
- **Server Setup** (Ubuntu 24.04):
  ```bash
  sudo apt update
  sudo apt install -y openvpn easy-rsa
  ```
  - **Configure Certificates** (Easy-RSA):
    ```bash
    make-cadir ~/easy-rsa
    cd ~/easy-rsa
    ./easyrsa init-pki
    ./easyrsa build-ca nopass  # Enter: ca
    ./easyrsa gen-req server nopass
    ./easyrsa sign-req server server
    ./easyrsa gen-dh
    openvpn --genkey --secret pki/ta.key
    ```
  - **Copy Files**:
    ```bash
    sudo cp pki/ca.crt pki/issued/server.crt pki/private/server.key pki/dh.pem pki/ta.key /etc/openvpn/
    ```
  - **Server Config**:
    ```bash
    sudo nano /etc/openvpn/server.conf
    ```
    ```text
    port 1194
    proto udp
    dev tun
    ca ca.crt
    cert server.crt
    key server.key
    dh dh.pem
    tls-auth ta.key 0
    server 10.8.0.0 255.255.255.0
    push "redirect-gateway def1 bypass-dhcp"
    push "dhcp-option DNS 8.8.8.8"
    keepalive 10 120
    cipher AES-256-CBC
    persist-key
    persist-tun
    ```
  - **Enable IP Forwarding**:
    ```bash
    sudo nano /etc/sysctl.conf
    # Uncomment: net.ipv4.ip_forward=1
    sudo sysctl -p
    ```
  - **Start Server**:
    ```bash
    sudo systemctl enable openvpn@server
    sudo systemctl start openvpn@server
    ```
  - **Firewall**:
    ```bash
    sudo apt install -y ufw
    sudo ufw allow 1194/udp
    sudo ufw allow OpenSSH
    sudo ufw enable
    ```
- **Client Setup** (Ubuntu):
  ```bash
  sudo apt install -y openvpn
  ```
  - **Generate Client Cert** (on server):
    ```bash
    cd ~/easy-rsa
    ./easyrsa gen-req client nopass
    ./easyrsa sign-req client client
    ```
  - **Client Config** (`client.ovpn`):
    ```text
    client
    dev tun
    proto udp
    remote server-ip 1194
    resolv-retry infinite
    nobind
    persist-key
    persist-tun
    ca ca.crt
    cert client.crt
    key client.key
    tls-auth ta.key 1
    cipher AES-256-CBC
    remote-cert-tls server
    ```
  - **Copy Files to Client**:
    ```bash
    # On client
    mkdir ~/vpn
    scp user@server-ip:~/easy-rsa/pki/{ca.crt,issued/client.crt,private/client.key,ta.key} ~/vpn/
    mv ~/vpn/client.ovpn ~/vpn/client.conf
    ```
  - **Connect**:
    ```bash
    sudo openvpn --config ~/vpn/client.conf
    ```
    - Verify:
      ```bash
      curl https://api.ipify.org
      # Output: server-ip
      ```

##### 1.1.2 WireGuard
- **Why**: Simpler, faster than OpenVPN (per web:13,15).
- **Server Setup**:
  ```bash
  sudo apt install -y wireguard
  wg genkey | tee /etc/wireguard/privatekey | wg pubkey > /etc/wireguard/publickey
  ```
  ```text
  # /etc/wireguard/wg0.conf
  [Interface]
  PrivateKey = <server-private-key>
  Address = 10.0.0.1/24
  ListenPort = 51820
  PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
  PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

  [Peer]
  PublicKey = <client-public-key>
  AllowedIPs = 10.0.0.2/32
  ```
  - Enable forwarding:
    ```bash
    sudo nano /etc/sysctl.conf
    # Add: net.ipv4.ip_forward=1
    sudo sysctl -p
    ```
  - Start:
    ```bash
    sudo wg-quick up wg0
    sudo systemctl enable wg-quick@wg0
    ```
  - Firewall:
    ```bash
    sudo ufw allow 51820/udp
    ```
- **Client Setup**:
  ```bash
  sudo apt install -y wireguard
  wg genkey | tee /etc/wireguard/client_privatekey | wg pubkey > /etc/wireguard/client_publickey
  ```
  ```text
  # /etc/wireguard/wg0.conf
  [Interface]
  PrivateKey = <client-private-key>
  Address = 10.0.0.2/24
  DNS = 8.8.8.8

  [Peer]
  PublicKey = <server-public-key>
  Endpoint = server-ip:51820
  AllowedIPs = 0.0.0.0/0, ::/0
  PersistentKeepalive = 25
  ```
  - Connect:
    ```bash
    sudo wg-quick up wg0
    ```
    - Verify:
      ```bash
      ping 10.0.0.1
      curl https://api.ipify.org
      ```

#### 1.2 Usage
- **Access Private Network**:
  ```bash
  ssh user@10.8.0.2  # OpenVPN
  ssh user@10.0.0.2  # WireGuard
  ```
- **Secure Browsing**:
  - Connect VPN, visit `whatismyipaddress.com` (shows server IP).
- **Scripted Connection**:
  ```bash
  # vpn.sh
  #!/bin/bash
  sudo openvpn --config ~/vpn/client.conf --daemon
  echo "VPN started" >> vpn.log
  ```
  ```bash
  chmod +x vpn.sh
  ./vpn.sh
  ```
- **Commercial VPN** (e.g., NordVPN):
  ```bash
  sudo apt install -y nordvpn
  nordvpn login --username user@example.com
  nordvpn connect us
  ```

#### 1.3 Security
- **Restrict Keys**:
  ```bash
  chmod 600 /etc/wireguard/* /etc/openvpn/*
  ```
- **Firewall**:
  ```bash
  sudo ufw deny out to any
  sudo ufw allow out to server-ip port 1194 proto udp
  sudo ufw reload
  ```
- **Rotate Certs** (OpenVPN):
  ```bash
  cd ~/easy-rsa
  ./easyrsa revoke client
  ./easyrsa gen-req client nopass
  ./easyrsa sign-req client client
  ```
- **Audit Logs**:
  ```bash
  sudo journalctl -u openvpn@server > vpn.log
  ```

---

### 2. SFTP (Secure File Transfer Protocol)

- **Definition**: SFTP is a secure protocol running over SSH for **transferring files** between systems, offering encryption and authentication (per web:6,14).
- **Why It Matters**:
  - Safely share files (e.g., backups, configs) without FTP’s vulnerabilities (per web:14).
  - Leverages existing SSH setup, no extra server needed (per web:6).
- **Linux Context**:
  - Built into OpenSSH, available on all Linux distros.
  - Use cases: Upload code to servers, sync data securely.

#### 2.1 Installation and Setup
- **Server** (included with OpenSSH):
  ```bash
  sudo apt update
  sudo apt install -y openssh-server
  ```
  - Verify:
    ```bash
    sudo systemctl status ssh
    # Output: active (running)
    ```
  - Configure:
    ```bash
    sudo nano /etc/ssh/sshd_config
    # Ensure:
    Subsystem sftp /usr/lib/openssh/sftp-server
    ```
    ```bash
    sudo systemctl restart ssh
    ```
- **Client**:
  ```bash
  sudo apt install -y openssh-client
  ```

#### 2.2 Usage
- **Connect**:
  ```bash
  sftp user@server-ip
  ```
  - With key:
    ```bash
    ssh-keygen -t ed25519 -C "sftp-user@example.com"
    ssh-copy-id user@server-ip
    sftp -i ~/.ssh/id_ed25519 user@server-ip
    ```
- **Commands**:
  ```bash
  # Inside sftp
  pwd          # Remote dir
  lpwd         # Local dir
  ls           # List remote
  put file.txt # Upload
  get file.txt # Download
  exit
  ```
- **Batch Transfer**:
  ```bash
  echo "put file.txt /home/user/remote.txt" > sftp.batch
  sftp -b sftp.batch user@server-ip
  ```
- **Python with Paramiko**:
  ```bash
  pip install paramiko
  ```
  ```python
  import paramiko

  def sftp_upload(local_path, remote_path, host, username, key_path="~/.ssh/id_ed25519"):
      if "rm -rf" in local_path:  # Basic guardrail
          raise ValueError("Unsafe path")
      transport = paramiko.Transport((host, 22))
      transport.connect(username=username, pkey=paramiko.Ed25519Key.from_private_key_file(key_path))
      sftp = paramiko.SFTPClient.from_transport(transport)
      sftp.put(local_path, remote_path)
      sftp.close()
      transport.close()
      with open("sftp.log", "a") as f:
          f.write(f"Uploaded {local_path} to {remote_path}\n")

  sftp_upload("test.txt", "/home/user/test.txt", "server-ip", "user")
  ```
- **Combine with VPN**:
  - Connect VPN:
    ```bash
    sudo wg-quick up wg0
    ```
  - Transfer over VPN:
    ```bash
    sftp user@10.0.0.2
    put secret.txt
    ```

#### 2.3 Security
- **Chroot Jail** (restrict SFTP users):
  ```bash
  sudo useradd -m -s /bin/false sftpuser
  sudo mkdir /home/sftpuser/upload
  sudo chown root:root /home/sftpuser
  sudo chown sftpuser:sftpuser /home/sftpuser/upload
  sudo nano /etc/ssh/sshd_config
  # Add:
  Match User sftpuser
      ChrootDirectory /home/sftpuser
      ForceCommand internal-sftp
      AllowTcpForwarding no
  sudo systemctl restart ssh
  ```
- **Disable Passwords**:
  ```bash
  sudo nano /etc/ssh/sshd_config
  # Set:
  PasswordAuthentication no
  sudo systemctl restart ssh
  ```
- **Secure Keys**:
  ```bash
  chmod 600 ~/.ssh/id_ed25519 ~/.ssh/authorized_keys
  ```
- **Audit Logs**:
  ```bash
  sudo cat /var/log/auth.log | grep sftp >> sftp.log
  ```

---

### 3. Key Concepts

- **VPN**:
  - **Tunneling**: Encrypts traffic via `tun` (OpenVPN) or `wg` (WireGuard) interfaces.
  - **Authentication**: Certificates (OpenVPN) or key pairs (WireGuard).
  - **Routing**: `AllowedIPs` (WireGuard) or `push` directives (OpenVPN) control traffic.
- **SFTP**:
  - **SSH-Based**: Uses SSH keys or passwords for auth.
  - **Commands**: Similar to FTP (`put`, `get`) but encrypted.
  - **Chroot**: Isolates users to specific directories.
- **Linux**:
  - **Firewall**: `ufw` simplifies rules (e.g., `allow 1194/udp`).
  - **Services**: Managed via `systemctl` (e.g., `openvpn@server`).
  - **Logs**: `/var/log` for debugging (e.g., `auth.log` for SFTP).

---

### 4. Common Pitfalls and Fixes

- **VPN**:
  - **No Internet**:
    - Fix: Check routing:
      ```bash
      ip route
      sudo nano /etc/openvpn/server.conf
      # Add: push "redirect-gateway def1"
      sudo systemctl restart openvpn@server
      ```
  - **WireGuard Fails**:
    - Fix: Verify keys:
      ```bash
      cat /etc/wireguard/publickey
      wg show
      ```
  - **Client Disconnects**:
    - Fix: Add keepalive:
      ```text
      # client.ovpn
      keepalive 10 120
      ```
- **SFTP**:
  - **Connection Refused**:
    - Fix: Start SSH:
      ```bash
      sudo systemctl start ssh
      sudo ufw allow 22
      ```
  - **Permission Denied**:
    - Fix: Check authorized keys:
      ```bash
      ls -l ~/.ssh/authorized_keys
      chmod 600 ~/.ssh/authorized_keys
      ```
  - **Chroot Errors**:
    - Fix: Verify ownership:
      ```bash
      sudo chown root:root /home/sftpuser
      sudo chmod 755 /home/sftpuser
      ```

#### Security Fixes
- **VPN**:
  ```bash
  sudo nano /etc/wireguard/wg0.conf
  # Restrict: AllowedIPs = 10.0.0.2/32
  sudo wg-quick down wg0 && sudo wg-quick up wg0
  ```
- **SFTP**:
  ```bash
  sudo nano /etc/ssh/sshd_config
  # Add:
  AllowUsers sftpuser
  sudo systemctl restart ssh
  ```
- **General**:
  ```bash
  sudo apt upgrade -y
  sudo find /var/log -name "*.log" -exec truncate -s 0 {} \;  # Rotate logs
  ```

---

### 5. Hands-On Challenge
To master VPN and SFTP on Linux:
1. **VPN**:
   - Set up WireGuard server on Ubuntu 24.04.
   - Connect a client, verify IP (`curl ifconfig.me`).
2. **SFTP**:
   - Create user `sftpuser` with chroot jail.
   - Upload `test.txt` (“Hello, SFTP!”) via SFTP.
   - Download as `test2.txt`, verify content.
3. **Integration**:
   - Connect VPN, SFTP over VPN (`sftp user@10.0.0.2`).
   - Upload `vpn-test.txt`.
4. **Security**:
   - Disable SSH passwords.
   - Log VPN/SFTP activity to `network.log`.
Share commands/output, and I’ll review!

**Starter Commands**:
```bash
# VPN
sudo apt install -y wireguard
wg genkey | tee /etc/wireguard/privatekey | wg pubkey > /etc/wireguard/publickey
sudo nano /etc/wireguard/wg0.conf

# SFTP
sudo apt install -y openssh-server
ssh-keygen -t ed25519
echo "Hello, SFTP!" > test.txt
```

---

### 6. Advanced Tips

- **VPN**:
  - **Split Tunneling** (WireGuard):
    ```text
    # wg0.conf (client)
    AllowedIPs = 10.0.0.0/24  # Only VPN network
    ```
    ```bash
    sudo wg-quick down wg0 && sudo wg-quick up wg0
    ```
  - **Multiple Peers**:
    ```text
    # wg0.conf (server)
    [Peer]
    PublicKey = <client2-public-key>
    AllowedIPs = 10.0.0.3/32
    ```
    ```bash
    sudo wg set wg0 peer <client2-public-key> allowed-ips 10.0.0.3/32
    ```
  - **Monitoring**:
    ```bash
    sudo watch wg show
    ```
- **SFTP**:
  - **Group Jail**:
    ```bash
    sudo groupadd sftpusers
    sudo usermod -aG sftpusers sftpuser
    sudo nano /etc/ssh/sshd_config
    # Add:
    Match Group sftpusers
        ChrootDirectory /sftp
        ForceCommand internal-sftp
    sudo mkdir /sftp
    sudo chown root:root /sftp
    sudo systemctl restart ssh
    ```
  - **Compression**:
    ```bash
    sftp -C user@server-ip
    put largefile.zip
    ```
  - **Automation**:
    ```bash
    # sftp-auto.sh
    #!/bin/bash
    echo "put /data/*.txt /home/sftpuser/upload/" | sftp user@server-ip
    ```
    ```bash
    chmod +x sftp-auto.sh
    ./sftp-auto.sh
    ```



---

