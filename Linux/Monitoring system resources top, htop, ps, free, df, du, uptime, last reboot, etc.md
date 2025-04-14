
---

### Resources
- **Monitoring**: [man7.org/linux/man-pages](https://man7.org/linux/man-pages) (web:6).
- **Tools**: [htop.dev](https://htop.dev) (web:12).
- **Tutorials**:
  - “Linux Monitoring” [freecodecamp.org](https://www.freecodecamp.org) (web:0).
  - “Df and Du” [linuxize.com](https://linuxize.com) (web:17).
- **Community**: Linux Admin Reddit, X `#Linux` (post:1,4,6).
---

### 1. Overview of System Monitoring

- **Definition**: System monitoring involves tracking **CPU**, **memory**, **disk**, **network**, and **process** usage to ensure performance, diagnose issues, and maintain stability (per web:0,6).
- **Why It Matters**:
  - **Performance**: Identify resource-intensive processes (e.g., runaway Python script) (per web:12).
  - **Troubleshooting**: Detect low memory or full disks (per web:17).
  - **Administration**: Monitor uptime, user logins, or reboots for servers (per web:19).
- **Key Metrics**:
  - **CPU**: Usage percentage, load average.
  - **Memory**: Used, free, swap.
  - **Disk**: Space, inodes, I/O.
  - **Processes**: Running tasks, PIDs, resource usage.
  - **System**: Uptime, boot history, user activity.
- **Linux Context**:
  - Tools like `top` and `htop` provide real-time insights; `free` and `df` focus on resources (per web:3).
  - Use cases: Optimize a web server, debug crashes, or automate alerts.

#### 1.1 Setup
- **Environment**: Ubuntu 24.04 (VM, cloud, or local).
  ```bash
  sudo apt update
  lsb_release -a  # Verify: Ubuntu 24.04 LTS
  ```
- **Install Tools**:
  ```bash
  sudo apt install -y htop procps  # htop, ps, top, free, etc.
  ```
  - Verify:
    ```bash
    htop --version  # e.g., htop 3.3.0
    top --version   # e.g., procps-ng 4.0.4
    ```
- **User**: `user` with sudo privileges.

---

### 2. Monitoring Commands

Below are the key commands for monitoring system resources, with examples and practical tips.

#### 2.1 `top` (Real-Time System Monitor)
- **Purpose**: Displays live process info, CPU, memory, and load averages.
- **Usage**:
  ```bash
  top
  ```
  - Output:
    - **Header**:
      - Load average: `0.15, 0.10, 0.05` (1, 5, 15 mins; < CPU cores is healthy).
      - Tasks: Total, running, sleeping.
      - CPU: `%us` (user), `%sy` (system), `%id` (idle).
      - Mem: Total, free, used.
    - **Table**: PID, user, %CPU, %MEM, command.
  - Keys:
    - `q`: Quit.
    - `k`: Kill process (enter PID).
    - `f`: Manage fields (add/remove columns).
    - `1`: Toggle per-CPU stats.
    - `Shift+P`: Sort by CPU.
    - `Shift+M`: Sort by memory.
- **Example**:
  ```bash
  top
  # Press k, enter PID (e.g., 1234), signal 9 (SIGKILL)
  ```
- **Use Case**: Identify a CPU-hogging process (e.g., `python app.py`).

#### 2.2 `htop` (Enhanced Top)
- **Purpose**: Colorful, user-friendly alternative to `top` with mouse support.
- **Usage**:
  ```bash
  htop
  ```
  - Features:
    - Scrollable process list.
    - Filter: `F4`, type `python`.
    - Kill: `F9`, select signal.
    - Tree view: `F5`.
    - Sort: `F6` (e.g., %CPU, %MEM).
    - Exit: `F10` or `q`.
  - Customize:
    ```bash
    htop
    # Press F2, add meters (e.g., Disk I/O), save
    ```
- **Example**:
  ```bash
  htop --sort-key PERCENT_MEM
  # Shows memory-heavy processes first
  ```
- **Use Case**: Monitor a server, kill hung tasks visually.

#### 2.3 `ps` (Process Status)
- **Purpose**: Lists processes with customizable output (snapshot, not live).
- **Usage**:
  ```bash
  ps aux
  ```
  - Output:
    - `a`: All users.
    - `u`: User-oriented format.
    - `x`: Include non-terminal processes.
    - Columns: USER, PID, %CPU, %MEM, COMMAND.
  ```bash
  # Example output:
  # user  1234  0.1  0.5  python app.py
  ```
- **Options**:
  - Filter by user:
    ```bash
    ps -u user
    ```
  - By PID:
    ```bash
    ps -p 1234
    ```
  - Tree view:
    ```bash
    ps axf
    ```
  - Grep:
    ```bash
    ps aux | grep nginx
    ```
- **Example**:
  ```bash
  ps aux | grep python
  # Find PIDs, then:
  kill -9 1234
  ```
- **Use Case**: Script process checks.

#### 2.4 `free` (Memory Usage)
- **Purpose**: Shows total, used, free, and swap memory.
- **Usage**:
  ```bash
  free -h
  ```
  - Output:
    ```
           total  used  free  shared  buff/cache  available
    Mem:   7.8G   1.2G  5.0G   100M    1.6G       6.2G
    Swap:  2.0G     0B  2.0G
    ```
    - `-h`: Human-readable (GB, MB).
    - `buff/cache`: Used for caching, reclaimable.
    - `available`: Usable by new processes.
- **Options**:
  - Continuous:
    ```bash
    free -h -s 2  # Update every 2s
    ```
  - Wide:
    ```bash
    free -hw  # Split buffers, cache
    ```
- **Example**:
  ```bash
  free -h >> mem.log
  ```
- **Use Case**: Check if swap is overused (indicates low RAM).

#### 2.5 `df` (Disk Free)
- **Purpose**: Reports disk space usage.
- **Usage**:
  ```bash
  df -h
  ```
  - Output:
    ```
    Filesystem      Size  Used Avail Use% Mounted on
    /dev/sda1        50G   10G   38G  21% /
    ```
    - `-h`: Human-readable (GB, MB).
    - `Use%`: Percentage used.
- **Options**:
  - Specific filesystem:
    ```bash
    df -h /home
    ```
  - Inodes:
    ```bash
    df -i
    # Check for inode exhaustion
    ```
- **Example**:
  ```bash
  df -h / | grep /dev | awk '{print $5}'  # Output: 21%
  ```
- **Use Case**: Alert when disk exceeds 80% usage.

#### 2.6 `du` (Disk Usage)
- **Purpose**: Measures space used by files/directories.
- **Usage**:
  ```bash
  du -h /home/user
  ```
  - Output:
    ```
    4.0K    /home/user/docs
    1.2G    /home/user/videos
    1.2G    /home/user
    ```
- **Options**:
  - `-s`: Summarize:
    ```bash
    du -sh /home/user
    # Output: 1.2G /home/user
    ```
  - `-d`: Depth:
    ```bash
    du -h --max-depth=1
    ```
  - Exclude:
    ```bash
    du -h --exclude="*.log"
    ```
- **Example**:
  ```bash
  du -sh * | sort -hr  # Largest first
  ```
- **Use Case**: Find space hogs in `/var/log`.

#### 2.7 `uptime` (System Uptime)
- **Purpose**: Shows how long the system has been running, plus load averages.
- **Usage**:
  ```bash
  uptime
  ```
  - Output:
    ```
    12:34:56 up 1 day, 2:03, 2 users, load average: 0.10, 0.15, 0.20
    ```
    - Time, uptime, users, load (1, 5, 15 mins).
- **Example**:
  ```bash
  uptime | awk '{print $3}'  # Output: 1
  ```
- **Use Case**: Check server stability.

#### 2.8 `last` (Login History)
- **Purpose**: Lists recent user logins and reboots.
- **Usage**:
  ```bash
  last
  ```
  - Output:
    ```
    user  pts/0  192.168.1.100  Sun Apr 13 10:00   still logged in
    reboot system boot  5.15.0-73      Sun Apr 12 08:00
    ```
- **Options**:
  - Reboots only:
    ```bash
    last reboot
    ```
  - Specific user:
    ```bash
    last user
    ```
- **Example**:
  ```bash
  last -n 2  # Last 2 entries
  ```
- **Use Case**: Audit unauthorized logins.

#### 2.9 `reboot` and Last Reboot
- **Purpose**: Reboots the system; check last reboot time.
- **Usage**:
  ```bash
  sudo reboot
  ```
  - Check last reboot:
    ```bash
    who -b
    # Output: system boot 2025-04-12 08:00
    ```
    ```bash
    last reboot | head -n 1
    ```
- **Example**:
  ```bash
  echo "Rebooted at $(date)" >> reboot.log
  sudo reboot
  ```
- **Use Case**: Schedule maintenance reboots.

#### 2.10 Other Tools
- **iotop**: Disk I/O per process.
  ```bash
  sudo apt install -y iotop
  sudo iotop
  ```
- **netstat`/`ss**: Network usage.
  ```bash
  sudo apt install -y net-tools
  netstat -tulnp
  ss -tulnp
  ```
- **vmstat**: System stats.
  ```bash
  vmstat -s
  vmstat 1  # Update every 1s
  ```
- **dmesg**: Kernel messages.
  ```bash
  dmesg | grep error
  ```

---

### 3. Practical Examples

- **High CPU Alert**:
  ```bash
  top -bn1 | head -n 3 >> cpu.log
  if [[ $(top -bn1 | awk 'NR==1 {print $8}' | cut -d. -f1) -lt 10 ]]; then
      echo "CPU idle < 10% at $(date)" >> alert.log
  fi
  ```
- **Disk Cleanup**:
  ```bash
  df -h / | grep /dev | awk '$5 > 80 {print "Disk full"}'
  du -sh /var/log/* | sort -hr | head -n 5
  ```
- **Process Check**:
  ```bash
  ps aux | grep nginx | awk '{print $2}' | xargs kill -9
  ```
- **Uptime Report**:
  ```bash
  echo "Uptime: $(uptime -p), Last reboot: $(who -b)" > status.txt
  ```

---

### 4. Automation and Monitoring

- **Script**:
  ```bash
  # monitor.sh
  #!/bin/bash
  LOG=monitor.log
  echo "=== $(date) ===" >> $LOG
  echo "Uptime: $(uptime -p)" >> $LOG
  echo "Memory:" >> $LOG
  free -h >> $LOG
  echo "Disk:" >> $LOG
  df -h / >> $LOG
  echo "Top Processes:" >> $LOG
  ps aux --sort=-%mem | head -n 5 >> $LOG
  ```
  ```bash
  chmod +x monitor.sh
  ./monitor.sh
  ```
- **Cron Job**:
  ```bash
  crontab -e
  # Add:
  */5 * * * * /home/user/monitor.sh
  ```
- **Threshold Alert**:
  ```bash
  # alert.sh
  #!/bin/bash
  USED=$(df -h / | grep /dev | awk '{print $5}' | cut -d% -f1)
  if [ $USED -gt 80 ]; then
      echo "Disk usage at $USED% on $(date)" | mail -s "Disk Alert" user@example.com
  fi
  ```
  ```bash
  chmod +x alert.sh
  ```

---

### 5. Security Best Practices

- **Restrict Logs**:
  ```bash
  chmod 640 /var/log/syslog
  sudo chown root:adm /var/log/syslog
  ```
- **Monitor Root Processes**:
  ```bash
  ps -U root -u root u > root_procs.txt
  ```
- **Secure Scripts**:
  ```bash
  chmod 700 monitor.sh
  ```
- **Audit Access**:
  ```bash
  last -n 10 >> login_audit.log
  ```
- **Prevent Injection**:
  ```bash
  # monitor.sh
  if [[ "$1" =~ ^[a-zA-Z0-9./-]+$ ]]; then
      LOG="$1"
  else
      echo "Invalid log path"
      exit 1
  fi
  ```

---

### 6. Common Pitfalls and Fixes

- **Top/Htop Hangs**:
  - **Fix**: Reduce refresh:
    ```bash
    top -d 2  # 2s delay
    htop --delay=20  # 2s (20 * 100ms)
    ```
- **Free Misread**:
  - **Fix**: Check `available`:
    ```bash
    free -h | grep Mem | awk '{print $7}'  # Available memory
    ```
- **Df Full but Empty**:
  - **Fix**: Check inodes or deleted files:
    ```bash
    df -i
    lsof | grep deleted
    ```
- **Du Slow**:
  - **Fix**: Limit scope:
    ```bash
    du -sh /home/* --max-depth=1
    ```
- **Ps Overload**:
  - **Fix**: Filter:
    ```bash
    ps -C nginx
    ```

---

### 7. Hands-On Challenge
To master system monitoring:
1. **Setup**:
   - Install `htop`, create `monitor.log`.
   - Simulate load: `stress --cpu 2 &`.
2. **Real-Time**:
   - Use `top` to find `stress` PID, kill it.
   - Use `htop` to sort by CPU, save config.
3. **Resources**:
   - Check memory with `free -h`, log to `monitor.log`.
   - Find largest directory in `/home` with `du`.
4. **History**:
   - Log last reboot and uptime to `monitor.log`.
   - List last 3 logins with `last`.
5. **Automation**:
   - Script `df -h` and `ps aux` every minute for 5 mins.
   - Secure `monitor.log` (640, `user:adm`).
Share commands/output, and I’ll review!

**Starter Commands**:
```bash
sudo apt install -y htop stress
touch monitor.log
top
htop
```

---

### 8. Advanced Tips

- **Htop Customization**:
  ```bash
  htop
  # F2, add "Tasks" meter, move to top-left, F10
  ```
- **Ps Formatting**:
  ```bash
  ps -eo pid,ppid,%cpu,%mem,cmd --sort=-%cpu | head
  ```
- **Watch Command**:
  ```bash
  watch -n 1 free -h
  ```
- **Systemd Monitoring**:
  ```bash
  systemctl status nginx
  journalctl -u nginx -n 50
  ```
- **Glances** (All-in-One):
  ```bash
  sudo apt install -y glances
  glances
  ```
- **Sar** (Historical Data):
  ```bash
  sudo apt install -y sysstat
  sar -u 1 5  # CPU stats, 1s interval, 5 samples
  ```



---
