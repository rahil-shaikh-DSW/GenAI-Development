

---

### Resources
- **Logs**: [man7.org/linux/man-pages/syslog](https://man7.org/linux/man-pages) (web:6).
- **Journalctl**: [freedesktop.org/systemd](https://freedesktop.org/software/systemd) (web:3).
- **Tutorials**:
  - “Logrotate Guide” [digitalocean.com](https://www.digitalocean.com) (web:12).
  - “Journalctl Tips” [linuxize.com](https://linuxize.com) (web:17).
- **Community**: Linux Sysadmin Reddit, X `#Linux` (post:1,4,6).


---

### 1. Understanding Log Management

- **Definition*p,c uu*: Log management involves **collecting**, **storing**, **analyzing**, and **rotating** log files to monitor system activity, troubleshoot issues, and ensure security (per web:0,6).
- **Why It Matters**:
  - **Troubleshooting**: Diagnose crashes or errors (e.g., Apache failing) (per web:12).
  - **Security**: Detect unauthorized access or anomalies (e.g., failed logins) (per web:17).
  - **Compliance**: Retain logs for audits (e.g., GDPR, SOC) (per web:19).
  - **Performance**: Identify resource issues (e.g., disk full from logs) (per web:20).
- **Key Concepts**:
  - **Log Files**: Text files in `/var/log` (e.g., `syslog`, `auth.log`).
  - **Systemd Journal**: Binary logs managed by `journalctl` for systemd systems.
  - **Rotation**: Archiving/compressing old logs to save space.
  - **Log Levels**: Debug, info, warning, error, critical.
- **Linux Context**:
  - Ubuntu uses `rsyslog` for traditional logs and `systemd-journald` for journal logs (per web:3).
  - Use cases: Monitor a web server, audit SSH logins, or automate log cleanup.

#### 1.1 Common Log Files
- `/var/log/syslog` or `/var/log/messages`: General system logs.
- `/var/log/auth.log`: Authentication (login, sudo).
- `/var/log/kern.log`: Kernel messages.
- `/var/log/dpkg.log`: Package installation.
- `/var/log/nginx/access.log`: Web server access (if installed).
- `/tmp/app.log`: Custom app logs.

#### 1.2 Setup
- **Environment**: Ubuntu 24.04 (VM, cloud, or local).
  ```bash
  sudo apt update
  lsb_release -a  # Verify: Ubuntu 24.04 LTS
  ```
- **Install Tools**:
  ```bash
  sudo apt install -y rsyslog logrotate
  ```
  - Verify:
    ```bash
    rsyslogd -v  # e.g., rsyslogd 8.2312.0
    logrotate --version  # e.g., logrotate 3.21.0
    ```
- **User**: `user` with sudo privileges.

---

### 2. Viewing and Analyzing Logs

#### 2.1 `journalctl` (Systemd Journal Logs)
- **Purpose**: Queries binary logs from `systemd-journald`, covering system and service events.
- **Usage**:
  ```bash
  journalctl
  ```
  - Scrolls through all logs (use `q` to quit, `Space` to page).
- **Options**:
  - Last 50 lines:
    ```bash
    journalctl -n 50
    ```
  - Follow live:
    ```bash
    journalctl -f
    ```
  - By service:
    ```bash
    journalctl -u ssh.service
    ```
  - By time:
    ```bash
    journalctl --since "2025-04-13 10:00" --until "2025-04-13 12:00"
    ```
  - By priority (0=emerg, 7=debug):
    ```bash
    journalctl -p 3  # Errors only
    ```
  - Boot logs:
    ```bash
    journalctl -b
    ```
  - Specific PID:
    ```bash
    journalctl _PID=1234
    ```
- **Example**:
  ```bash
  journalctl -u nginx.service -n 10
  # Shows last 10 nginx logs
  ```
- **Use Case**: Debug a service crash.

#### 2.2 Traditional Log Files
- **View Logs**:
  ```bash
  cat /var/log/syslog
  less /var/log/auth.log  # Paginated, q to quit
  tail -n 20 /var/log/kern.log
  ```
- **Live Monitoring**:
  ```bash
  tail -f /var/log/syslog
  ```
- **Search**:
  ```bash
  grep "error" /var/log/syslog
  grep "sshd.*Failed" /var/log/auth.log
  ```
- **Example**:
  ```bash
  tail -f /var/log/nginx/error.log
  # Monitor web server errors
  ```
- **Use Case**: Find failed login attempts.

#### 2.3 Other Tools
- **zcat/zgrep**: Read compressed logs.
  ```bash
  zcat /var/log/syslog.1.gz | grep "error"
  ```
- **awk/sed**: Parse logs.
  ```bash
  awk '/sshd/ {print $5}' /var/log/auth.log  # Extract fields
  ```
- **wc**: Count entries.
  ```bash
  grep "login" /var/log/auth.log | wc -l
  # Output: 42 (login attempts)
  ```

---

### 3. Configuring Log Collection

#### 3.1 `rsyslog`
- **Purpose**: Collects and routes logs to files (e.g., `/var/log/syslog`).
- **Config**: `/etc/rsyslog.conf`, `/etc/rsyslog.d/`.
- **Example**:
  ```bash
  sudo nano /etc/rsyslog.d/myapp.conf
  ```
  ```text
  :programname, isequal, "myapp" /var/log/myapp.log
  & stop
  ```
  ```bash
  sudo systemctl restart rsyslog
  ```
- **Test**:
  ```bash
  logger -t myapp "Test log"
  cat /var/log/myapp.log
  ```

#### 3.2 Systemd Journal
- **Config**: `/etc/systemd/journald.conf`.
- **Persistent Logs**:
  ```bash
  sudo nano /etc/systemd/journald.conf
  # Set:
  Storage=persistent
  ```
  ```bash
  sudo mkdir -p /var/log/journal
  sudo systemctl restart systemd-journald
  ```
- **Limit Size**:
  ```bash
  sudo nano /etc/systemd/journald.conf
  # Set:
  SystemMaxUse=100M
  ```
  ```bash
  sudo systemctl restart systemd-journald
  ```

#### 3.3 Custom App Logs
- **Python Example**:
  ```bash
  nano app.py
  ```
  ```python
  import logging
  logging.basicConfig(filename="/var/log/app.log", level=logging.INFO)
  logging.info("App started")
  ```
  ```bash
  python3 app.py
  cat /var/log/app.log
  ```

---

### 4. Rotating Logs with `logrotate`

- **Purpose**: Compresses, archives, and deletes old logs to prevent disk exhaustion.
- **Config**: `/etc/logrotate.conf`, `/etc/logrotate.d/`.
- **Usage**:
  ```bash
  logrotate --version
  ```

#### 4.1 Create Rotation Rule
- **Example**:
  ```bash
  sudo nano /etc/logrotate.d/myapp
  ```
  ```text
  /var/log/myapp.log {
      daily
      rotate 7
      compress
      missingok
      notifempty
      create 640 user adm
      postrotate
          /usr/bin/killall -HUP myapp
      endscript
  }
  ```
  - `daily`: Rotate daily.
  - `rotate 7`: Keep 7 archives.
  - `compress`: Gzip old logs.
  - `create`: Set new log permissions.
- **Test**:
  ```bash
  sudo logrotate -f /etc/logrotate.d/myapp
  ls /var/log/
  # Output: myapp.log myapp.log.1.gz
  ```

#### 4.2 Global Config
- **Edit**:
  ```bash
  sudo nano /etc/logrotate.conf
  ```
  ```text
  weekly
  rotate 4
  compress
  include /etc/logrotate.d
  ```
  ```bash
  sudo logrotate -f /etc/logrotate.conf
  ```

---

### 5. Practical Examples

- **Audit Logins**:
  ```bash
  grep "sshd.*Failed" /var/log/auth.log > failed_logins.txt
  wc -l failed_logins.txt
  ```
- **Service Debugging**:
  ```bash
  journalctl -u nginx.service -b | grep "error"
  ```
- **Custom Log**:
  ```bash
  logger -t myscript "Backup completed"
  tail /var/log/syslog | grep myscript
  ```
- **Clean Old Logs**:
  ```bash
  find /var/log -name "*.gz" -mtime +30 -delete
  ```
- **Scripted Analysis**:
  ```bash
  # logcheck.sh
  #!/bin/bash
  LOG=/var/log/syslog
  OUTPUT=report.txt
  echo "Log Report: $(date)" > $OUTPUT
  grep -i "error" $LOG | tail -n 10 >> $OUTPUT
  journalctl -p 3 -n 5 >> $OUTPUT
  ```
  ```bash
  chmod +x logcheck.sh
  ./logcheck.sh
  ```

---

### 6. Security Best Practices

- **Restrict Access**:
  ```bash
  sudo chmod 640 /var/log/myapp.log
  sudo chown user:adm /var/log/myapp.log
  ```
- **Rotate Sensitive Logs**:
  ```bash
  sudo nano /etc/logrotate.d/auth
  ```
  ```text
  /var/log/auth.log {
      daily
      rotate 7
      compress
      create 640 root adm
  }
  ```
- **Prevent Injection**:
  ```bash
  # logcheck.sh
  if [[ ! -f "$1" ]]; then
      echo "Invalid log file"
      exit 1
  fi
  ```
- **Backup Logs**:
  ```bash
  tar czf /backup/logs-$(date +%F).tar.gz /var/log/myapp.log
  chmod 600 /backup/logs-*.tar.gz
  ```
- **Monitor Access**:
  ```bash
  sudo auditctl -w /var/log -p wa -k log-access
  sudo ausearch -k log-access
  ```

---

### 7. Common Pitfalls and Fixes

- **Logs Missing**:
  - **Fix**: Check service:
    ```bash
    sudo systemctl status rsyslog
    journalctl -u systemd-journald
    ```
  - Enable persistent journal:
    ```bash
    sudo mkdir -p /var/log/journal
    ```
- **Disk Full**:
  - **Fix**: Rotate or clean:
    ```bash
    sudo logrotate -f /etc/logrotate.conf
    find /var/log -name "*.log" -size +100M -delete
    ```
- **Permission Denied**:
  - **Fix**: Adjust:
    ```bash
    sudo chown user:adm /var/log/myapp.log
    sudo chmod 640 /var/log/myapp.log
    ```
- **Logrotate Fails**:
  - **Fix**: Debug:
    ```bash
    sudo logrotate -d /etc/logrotate.d/myapp
    ```
- **Grep Overload**:
  - **Fix**: Use `journalctl`:
    ```bash
    journalctl -u myapp.service | grep "error"
    ```

---

### 8. Hands-On Challenge
To master log management:
1. **Setup**:
   - Create a script `ticker.sh` (logs “Tick” to `/var/log/ticker.log` every 5s).
   - Configure `rsyslog` to collect `ticker` logs.
2. **View**:
   - Use `journalctl` to show system logs from the last hour.
   - Use `tail` and `grep` to find “Tick” in `/var/log/ticker.log`.
3. **Rotate**:
   - Create a `logrotate` rule for `ticker.log` (daily, keep 3, compress).
   - Test rotation, verify `ticker.log.1.gz`.
4. **Analyze**:
   - Count “Tick” entries.
   - Log errors from `syslog` to `error.txt`.
5. **Security**:
   - Set `ticker.log` to `640`, `user:adm`.
   - Backup logs to `/backup/ticker-$(date +%F).tar.gz`.
Share commands/output, and I’ll review!

**Starter Commands**:
```bash
echo '#!/bin/bash\nwhile true; do logger -t ticker "Tick"; sleep 5; done' > ticker.sh
chmod +x ticker.sh
sudo nano /etc/rsyslog.d/ticker.conf
```

---

### 9. Advanced Tips

- **Centralized Logging**:
  ```bash
  sudo nano /etc/rsyslog.conf
  # Add:
  *.* @logserver:514
  ```
  ```bash
  sudo systemctl restart rsyslog
  ```
- **Journal Size**:
  ```bash
  journalctl --disk-usage
  sudo journalctl --vacuum-size=50M
  ```
- **Custom Format**:
  ```bash
  journalctl -o json-pretty > logs.json
  ```
- **Fail2Ban** (Security):
  ```bash
  sudo apt install -y fail2ban
  sudo nano /etc/fail2ban/jail.local
  ```
  ```ini
  [sshd]
  enabled = true
  logpath = /var/log/auth.log
  maxretry = 5
  ```
  ```bash
  sudo systemctl restart fail2ban
  ```
- **Cron for Analysis**:
  ```bash
  crontab -e
  # Add:
  0 * * * * /home/user/logcheck.sh
  ```

---

