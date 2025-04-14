
---

### Resources
- **Systemd**: [freedesktop.org/systemd](https://freedesktop.org/software/systemd) (web:6).
- **Tutorials**:
  - “Systemd Services” [digitalocean.com](https://www.digitalocean.com) (web:12).
  - “Journalctl” [linuxize.com](https://linuxize.com) (web:17).
- **Man Pages**:
  ```bash
  man systemd.service
  man systemctl
  ```
- **Community**: Linux Sysadmin Reddit, X `#Systemd` (post:1,4,6).

---

### 1. Understanding Systemd Services

- **Definition**: 
  - **Systemd**: A system and service manager for Linux, initializing and managing services, daemons, and system state (per web:0,6).
  - **Service**: A background process (e.g., web server, database) controlled by systemd via unit files (`.service`).
- **Why It Matters**:
  - **Automation**: Start services at boot or on demand (e.g., `nginx`, `mysql`) (per web:12).
  - **Control**: Start, stop, restart, or monitor services reliably (per web:17).
  - **Reliability**: Handle crashes, logging, and dependencies (e.g., network before web server) (per web:19).
- **Key Concepts**:
  - **Unit Files**: Configs in `/etc/systemd/system/` or `/lib/systemd/system/` defining service behavior.
  - **Types**: Services (`.service`), timers (`.timer`), mounts (`.mount`), etc.
  - **States**:
    - `active (running)`: Running normally.
    - `inactive`: Stopped.
    - `failed`: Crashed or errored.
    - `activating`/`deactivating`: Starting/stopping.
  - **Dependencies**: `Requires`, `Wants`, `After`, `Before` control order.
- **Linux Context**:
  - Systemd is the default init system in Ubuntu, Debian, Fedora, etc., replacing SysVinit (per web:3).
  - Use cases: Run a Python app, schedule backups, or manage `sshd`.

#### 1.1 Systemd Structure
- **Directories**:
  - `/lib/systemd/system/`: Default system units (don’t edit).
  - `/etc/systemd/system/`: Custom or overridden units (user edits).
  - `/run/systemd/system/`: Runtime units (temporary).
- **Commands**: `systemctl` for control, `journalctl` for logs.

#### 1.2 Setup
- **Environment**: Ubuntu 24.04 (VM, cloud, or local).
  ```bash
  sudo apt update
  lsb_release -a  # Verify: Ubuntu 24.04 LTS
  ```
- **Verify Systemd**:
  ```bash
  systemctl --version
  # Output: systemd 255 ...
  ```
- **User**: `user` with sudo privileges.

---

### 2. Creating Systemd Services

A systemd service is defined by a `.service` file specifying how to start, stop, and manage a process.

#### 2.1 Anatomy of a Service File
- **Sections**:
  - `[Unit]`: Metadata, dependencies.
  - `[Service]`: Execution details (command, restart policy).
  - `[Install]`: Enablement settings (e.g., boot startup).
- **Basic Template**:
  ```ini
  [Unit]
  Description=My Custom Service
  After=network.target

  [Service]
  ExecStart=/path/to/script.sh
  Restart=always
  User=user
  Group=user

  [Install]
  WantedBy=multi-user.target
  ```

#### 2.2 Step-by-Step: Create a Service
Let’s create a service for a Python script.

1. **Create Script**:
   ```bash
   mkdir -p ~/scripts
   nano ~/scripts/app.py
   ```
   ```python
   #!/usr/bin/env python3
   import time
   while True:
       with open("/tmp/app.log", "a") as f:
           f.write(f"Running at {time.ctime()}\n")
       time.sleep(5)
   ```
   ```bash
   chmod +x ~/scripts/app.py
   ```

2. **Create Service File**:
   ```bash
   sudo nano /etc/systemd/system/myapp.service
   ```
   ```ini
   [Unit]
   Description=My Python App
   After=network.target

   [Service]
   ExecStart=/home/user/scripts/app.py
   Restart=always
   User=user
   Group=user
   WorkingDirectory=/home/user/scripts
   Environment="PYTHONUNBUFFERED=1"

   [Install]
   WantedBy=multi-user.target
   ```

3. **Reload Systemd**:
   ```bash
   sudo systemctl daemon-reload
   ```

4. **Test Syntax**:
   ```bash
   sudo systemd-analyze verify myapp.service
   ```

#### 2.3 Example: Web Server Service
For a Node.js app:
```bash
mkdir -p ~/web
nano ~/web/server.js
```
```javascript
const http = require('http');
http.createServer((req, res) => {
    res.writeHead(200);
    res.end('Hello, Systemd!');
}).listen(8080);
```
```bash
sudo apt install -y nodejs
sudo nano /etc/systemd/system/web.service
```
```ini
[Unit]
Description=Node.js Web Server
After=network.target

[Service]
ExecStart=/usr/bin/node /home/user/web/server.js
Restart=on-failure
User=user
Environment=NODE_ENV=production
WorkingDirectory=/home/user/web

[Install]
WantedBy=multi-user.target
```
```bash
sudo systemctl daemon-reload
```

---

### 3. Managing Systemd Services

Use `systemctl` to control services.

#### 3.1 Basic Commands
- **Start**:
  ```bash
  sudo systemctl start myapp.service
  ```
- **Stop**:
  ```bash
  sudo systemctl stop myapp.service
  ```
- **Restart**:
  ```bash
  sudo systemctl restart myapp.service
  ```
- **Reload** (if supported):
  ```bash
  sudo systemctl reload myapp.service
  ```
- **Enable** (start at boot):
  ```bash
  sudo systemctl enable myapp.service
  # Creates symlink in /etc/systemd/system/multi-user.target.wants/
  ```
- **Disable**:
  ```bash
  sudo systemctl disable myapp.service
  ```
- **Status**:
  ```bash
  sudo systemctl status myapp.service
  ```
  - Output:
    ```
    ● myapp.service - My Python App
       Loaded: loaded (/etc/systemd/system/myapp.service; enabled; preset: enabled)
       Active: active (running) since Sun 2025-04-13 12:00:00 UTC
       Main PID: 1234 (python3)
       Tasks: 1
       Memory: 10.2M
       CPU: 0.500s
       CGroup: /system.slice/myapp.service
               └─1234 /usr/bin/python3 /home/user/scripts/app.py
    ```

#### 3.2 Check Service
- **Running Services**:
  ```bash
  systemctl list-units --type=service --state=running
  ```
- **All Services**:
  ```bash
  systemctl list-units --type=service
  ```
- **Failed Services**:
  ```bash
  systemctl --failed
  ```
- **Dependencies**:
  ```bash
  systemctl list-dependencies myapp.service
  ```

#### 3.3 Logs with `journalctl`
- **Service Logs**:
  ```bash
  journalctl -u myapp.service
  ```
- **Recent Logs**:
  ```bash
  journalctl -u myapp.service -n 50
  ```
- **Follow Live**:
  ```bash
  journalctl -u myapp.service -f
  ```
- **Since Date**:
  ```bash
  journalctl -u myapp.service --since "2025-04-13 10:00"
  ```

#### 3.4 Advanced Management
- **Mask** (prevent start):
  ```bash
  sudo systemctl mask myapp.service
  ```
  - Unmask:
    ```bash
    sudo systemctl unmask myapp.service
    ```
- **Edit Service**:
  ```bash
  sudo systemctl edit myapp.service
  # Creates override in /etc/systemd/system/myapp.service.d/
  ```
- **Reload All**:
  ```bash
  sudo systemctl daemon-reload
  ```
- **Reset Failed**:
  ```bash
  sudo systemctl reset-failed
  ```

---

### 4. Practical Examples

- **Python Service**:
  ```bash
  sudo systemctl start myapp.service
  journalctl -u myapp.service -n 10
  cat /tmp/app.log
  # Output: Running at Sun Apr 13 12:00:05 UTC 2025
  ```
- **Web Server**:
  ```bash
  sudo systemctl enable web.service
  sudo systemctl start web.service
  curl http://localhost:8080
  # Output: Hello, Systemd!
  ```
- **Restart on Crash**:
  ```bash
  sudo nano /etc/systemd/system/myapp.service
  # Add: RestartSec=5
  sudo systemctl daemon-reload
  sudo systemctl restart myapp.service
  ```
- **Scripted Control**:
  ```bash
  # manage.sh
  #!/bin/bash
  case $1 in
      start) sudo systemctl start myapp.service ;;
      stop) sudo systemctl stop myapp.service ;;
      status) systemctl status myapp.service ;;
      *) echo "Usage: $0 {start|stop|status}" ;;
  esac
  ```
  ```bash
  chmod +x manage.sh
  ./manage.sh status
  ```

---

### 5. Security Best Practices

- **Run as Non-Root**:
  ```ini
  [Service]
  User=user
  Group=user
  ```
- **Restrict Permissions**:
  ```bash
  sudo chown root:root /etc/systemd/system/myapp.service
  chmod 644 /etc/systemd/system/myapp.service
  ```
- **Limit Resources**:
  ```ini
  [Service]
  MemoryMax=100M
  CPUQuota=50%
  ```
  ```bash
  sudo systemctl daemon-reload
  ```
- **Protect Logs**:
  ```bash
  chmod 640 /tmp/app.log
  sudo chown user:adm /tmp/app.log
  ```
- **Validate Scripts**:
  ```bash
  # app.py
  if __name__ != "__main__":
      raise SystemExit("Not standalone")
  ```
- **Audit Actions**:
  ```bash
  sudo systemctl start myapp.service && echo "Started myapp at $(date)" >> service.log
  ```

---

### 6. Common Pitfalls and Fixes

- **Service Fails to Start**:
  - **Fix**: Check logs, syntax:
    ```bash
    journalctl -u myapp.service -b
    sudo systemd-analyze verify myapp.service
    ```
  - Verify path:
    ```bash
    ls -l /home/user/scripts/app.py
    chmod +x /home/user/scripts/app.py
    ```
- **Not Starting at Boot**:
  - **Fix**: Enable:
    ```bash
    sudo systemctl enable myapp.service
    ```
- **Permission Denied**:
  - **Fix**: Set user/group:
    ```ini
    [Service]
    User=user
    ```
    ```bash
    sudo systemctl daemon-reload
    ```
- **Logs Missing**:
  - **Fix**: Check journal:
    ```bash
    journalctl -u myapp.service --no-pager
    ```
- **Dependency Issues**:
  - **Fix**: Add `After`:
    ```ini
    [Unit]
    After=network-online.target
    Wants=network-online.target
    ```

---

### 7. Hands-On Challenge
To master systemd services:
1. **Setup**:
   - Create a Bash script `logger.sh` (writes “Log” to `/tmp/log.txt` every 10s).
   - Create a service `logger.service`.
2. **Service**:
   - Set `User=user`, `Restart=always`, run in `/home/user`.
   - Enable and start the service.
3. **Manage**:
   - Stop, restart, and check status.
   - Verify `/tmp/log.txt` updates.
   - Disable the service, confirm it doesn’t start on reboot (simulate: `sudo systemctl daemon-reload`).
4. **Logs**:
   - View last 20 lines of `logger.service` logs.
   - Log service actions to `manage.log`.
5. **Security**:
   - Restrict `logger.sh` and `/tmp/log.txt` to `640`, `user:adm`.
Share commands/output, and I’ll review!

**Starter Commands**:
```bash
mkdir -p ~/scripts
echo '#!/bin/bash\nwhile true; do echo "Log at $(date)" >> /tmp/log.txt; sleep 10; done' > ~/scripts/logger.sh
chmod +x ~/scripts/logger.sh
sudo nano /etc/systemd/system/logger.service
```

---

### 8. Advanced Tips

- **Timer for Scheduling**:
  ```bash
  sudo nano /etc/systemd/system/backup.timer
  ```
  ```ini
  [Unit]
  Description=Run backup daily

  [Timer]
  OnCalendar=daily
  Persistent=true

  [Install]
  WantedBy=timers.target
  ```
  ```bash
  sudo nano /etc/systemd/system/backup.service
  ```
  ```ini
  [Unit]
  Description=Backup script

  [Service]
  ExecStart=/home/user/backup.sh
  ```
  ```bash
  sudo systemctl enable backup.timer
  sudo systemctl start backup.timer
  ```
- **Drop-In Overrides**:
  ```bash
  sudo systemctl edit myapp.service
  ```
  ```ini
  [Service]
  Environment="DEBUG=1"
  ```
- **Resource Limits**:
  ```ini
  [Service]
  Nice=10
  MemoryHigh=200M
  ```
- **Multi-Instance**:
  ```ini
  # myapp@.service
  [Service]
  ExecStart=/usr/bin/python3 /home/user/app.py --port=%i
  ```
  ```bash
  sudo systemctl start myapp@8080.service
  sudo systemctl start myapp@8081.service
  ```
- **Analyze Boot**:
  ```bash
  systemd-analyze blame
  ```



---

