
---

### Resources
- **Processes**: [man7.org/linux/man-pages/ps](https://man7.org/linux/man-pages) (web:6).
- **Signals**: [linuxize.com/post/kill](https://linuxize.com/post/linux-kill-command) (web:17).
- **Tutorials**:
  - “Linux Processes” [freecodecamp.org](https://www.freecodecamp.org) (web:0).
  - “Htop Guide” [digitalocean.com](https://www.digitalocean.com) (web:12).
- **Community**: Linux Sysadmin Reddit, X `#Linux` (post:1,4,6).

---

### 1. Understanding Linux Processes

- **Definition**: A process is an instance of a running program, identified by a **PID** (Process ID), consuming CPU, memory, and other resources (per web:0,6).
- **Why It Matters**:
  - **Control**: Start, stop, or prioritize tasks (e.g., web servers, scripts) (per web:12).
  - **Troubleshooting**: Identify and kill hung or resource-heavy processes (per web:17).
  - **Automation**: Manage background jobs or daemons (e.g., `nginx`) (per web:19).
- **Key Concepts**:
  - **PID**: Unique identifier (e.g., 1234).
  - **Parent/Child**: Processes spawn others (PPID = parent PID).
  - **States**: Running (`R`), sleeping (`S`), stopped (`T`), zombie (`Z`).
  - **Signals**: Messages to control processes (e.g., `SIGTERM`, `SIGKILL`).
  - **Foreground/Background**: Interactive (`fg`) vs. detached (`bg`).
- **Linux Context**:
  - Tools like `ps` list processes; `kill` sends signals to control them (per web:3).
  - Use cases: Stop a crashed app, monitor a server, or script process checks.

#### 1.1 Process Lifecycle
- **Start**: Via command (e.g., `python app.py`), service (`systemctl`), or fork.
- **Run**: Consumes resources, may spawn children.
- **End**: Exits naturally or via signal (e.g., `kill`).

#### 1.2 Setup
- **Environment**: Ubuntu 24.04 (VM, cloud, or local).
  ```bash
  sudo apt update
  lsb_release -a  # Verify: Ubuntu 24.04 LTS
  ```
- **Install Tools**:
  ```bash
  sudo apt install -y procps htop  # ps, kill, top, htop
  ```
  - Verify:
    ```bash
    ps --version  # e.g., procps-ng 4.0.4
    htop --version  # e.g., htop 3.3.0
    ```
- **User**: `user` with sudo privileges.

---

### 2. Process Management Commands

Below are the key commands for managing processes, with examples and practical tips.

#### 2.1 `ps` (Process Status)
- **Purpose**: Lists processes with details like PID, user, CPU/memory usage, and command (snapshot, not live).
- **Usage**:
  ```bash
  ps aux
  ```
  - Output:
    ```
    USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
    user      1234  0.1  0.5 123456 7890 pts/0    S    12:00   0:01 python app.py
    ```
    - `a`: All users.
    - `u`: User-oriented format.
    - `x`: Include non-terminal processes.
    - Columns: PID, %CPU, %MEM, COMMAND, etc.
- **Options**:
  - Current session:
    ```bash
    ps
    # Output: PID TTY TIME CMD
    #         1234 pts/0 00:00:00 bash
    ```
  - By user:
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
    # Shows parent-child relationships
    ```
  - Custom output:
    ```bash
    ps -eo pid,ppid,%cpu,comm
    # Output: PID PPID %CPU COMMAND
    ```
  - Filter:
    ```bash
    ps aux | grep python
    ```
- **Example**:
  ```bash
  ps aux | grep nginx | awk '{print $2}'  # Get nginx PIDs
  ```
- **Use Case**: Find a process to terminate or inspect.

#### 2.2 `kill` (Send Signal)
- **Purpose**: Sends signals to processes to terminate, pause, or control them.
- **Usage**:
  ```bash
  kill 1234  # Default: SIGTERM (graceful stop)
  ```
- **Common Signals**:
  - `1` (`SIGHUP`): Reload config (e.g., for daemons).
  - `2` (`SIGINT`): Interrupt (like Ctrl+C).
  - `9` (`SIGKILL`): Force kill (last resort).
  - `15` (`SIGTERM`): Polite stop (default).
  - List signals:
    ```bash
    kill -l
    ```
- **Examples**:
  - Graceful stop:
    ```bash
    kill -15 1234
    ```
  - Force kill:
    ```bash
    kill -9 1234
    ```
  - Reload:
    ```bash
    kill -HUP 5678  # e.g., nginx
    ```
- **Options**:
  - Multiple PIDs:
    ```bash
    kill 1234 5678
    ```
  - By name (via `killall`):
    ```bash
    sudo apt install -y psmisc
    killall python
    ```
- **Use Case**: Stop a hung process or reload a service.

#### 2.3 `pkill` (Kill by Name)
- **Purpose**: Kills processes matching a pattern or criteria.
- **Usage**:
  ```bash
  pkill python
  ```
- **Options**:
  - By user:
    ```bash
    pkill -u user
    ```
  - Signal:
    ```bash
    pkill -9 python
    ```
  - Exact match:
    ```bash
    pkill -x python3
    ```
- **Example**:
  ```bash
  pkill -u user -f "python.*app.py"
  ```
- **Use Case**: Terminate all instances of an app.

#### 2.4 `killall` (Kill by Exact Name)
- **Purpose**: Kills all processes with a specific name.
- **Usage**:
  ```bash
  killall nginx
  ```
- **Options**:
  - Signal:
    ```bash
    killall -HUP nginx
    ```
  - Interactive:
    ```bash
    killall -i python
    ```
- **Example**:
  ```bash
  killall -9 firefox
  ```
- **Use Case**: Stop all browser instances.

#### 2.5 `top` and `htop` (Interactive Process Management)
- **Purpose**: Monitor processes live, with options to kill or prioritize.
- **Usage**:
  ```bash
  top
  ```
  - Kill: `k`, enter PID, signal (e.g., 9).
  - Sort: `Shift+P` (CPU), `Shift+M` (memory).
  - Quit: `q`.
  ```bash
  htop
  ```
  - Kill: `F9`, select signal.
  - Filter: `F4`, type `python`.
  - Exit: `F10` or `q`.
- **Example**:
  ```bash
  htop --sort-key PERCENT_CPU
  # Press F9 on PID 1234, select SIGTERM
  ```
- **Use Case**: Visually manage high-CPU tasks.

#### 2.6 `nice` and `renice` (Adjust Priority)
- **Purpose**: Set or change process priority (-20 = highest, 19 = lowest).
- **Usage**:
  - Start with priority:
    ```bash
    nice -n 10 python app.py  # Low priority
    ```
  - Adjust running process:
    ```bash
    renice 15 -p 1234  # Lower priority
    renice -5 -p 5678  # Higher (sudo required)
    ```
- **Example**:
  ```bash
  ps -p 1234 -o pid,ni,comm
  renice 10 -p 1234
  ps -p 1234 -o pid,ni,comm
  # Output: PID NI  COMMAND
  #         1234 10 python
  ```
- **Use Case**: Prioritize a backup job lower than a web server.

#### 2.7 `bg` and `fg` (Background/Foreground)
- **Purpose**: Manage job control for processes.
- **Usage**:
  - Start background:
    ```bash
    python app.py &
    ```
  - Pause foreground:
    ```bash
    python app.py
    # Press Ctrl+Z
    ```
  - Resume:
    ```bash
    bg  # Run in background
    fg  # Bring to foreground
    ```
  - List jobs:
    ```bash
    jobs
    # Output: [1]+ Running python app.py &
    ```
- **Example**:
  ```bash
  sleep 100 &
  jobs
  fg %1
  # Ctrl+C to stop
  ```
- **Use Case**: Multitask in a terminal.

#### 2.8 `nohup` (Run Detached)
- **Purpose**: Runs a process immune to hangups (e.g., terminal close).
- **Usage**:
  ```bash
  nohup python app.py &
  ```
  - Output to `nohup.out`.
- **Example**:
  ```bash
  nohup python app.py > app.log 2>&1 &
  ```
- **Use Case**: Run a script after SSH disconnect.

#### 2.9 Other Tools
- **pidof**: Find PID by name.
  ```bash
  pidof python
  # Output: 1234 5678
  ```
- **pgrep**: Search PIDs.
  ```bash
  pgrep -u user python
  ```
- **systemctl**: Manage services.
  ```bash
  sudo systemctl stop nginx
  ```
- **jobs**: Shell job control.
  ```bash
  jobs -l  # Include PIDs
  ```

---

### 3. Practical Examples

- **Stop Hung Process**:
  ```bash
  ps aux | grep python
  # Find PID: 1234
  kill -15 1234
  sleep 2
  ps -p 1234 || kill -9 1234
  ```
- **Kill All User Processes**:
  ```bash
  pkill -u bob
  ```
- **Prioritize Server**:
  ```bash
  pidof nginx | xargs renice -10 -p
  ```
- **Background Script**:
  ```bash
  nohup ./backup.sh > backup.log 2>&1 &
  ps aux | grep backup.sh
  ```
- **Monitor and Act**:
  ```bash
  # kill-heavy.sh
  #!/bin/bash
  TOP_PID=$(ps aux --sort=-%mem | head -n 2 | tail -n 1 | awk '{print $2}')
  if [ $(ps -p $TOP_PID -o %mem | tail -n 1) -gt 50 ]; then
      kill -15 $TOP_PID
      echo "Killed PID $TOP_PID at $(date)" >> kill.log
  fi
  ```
  ```bash
  chmod +x kill-heavy.sh
  ./kill-heavy.sh
  ```

---

### 4. Security Best Practices

- **Avoid SIGKILL**:
  ```bash
  kill -15 1234  # Try SIGTERM first
  ```
- **Restrict Kill**:
  ```bash
  chmod 700 kill-script.sh
  sudo chown root:root /usr/bin/kill
  ```
- **Verify PIDs**:
  ```bash
  ps -p 1234
  # Only then:
  kill 1234
  ```
- **Log Actions**:
  ```bash
  kill -9 1234 && echo "Killed 1234 at $(date)" >> process.log
  ```
- **Monitor Root**:
  ```bash
  ps -U root -u root u > root_procs.txt
  ```
- **Prevent Injection**:
  ```bash
  # kill-safe.sh
  if [[ ! "$1" =~ ^[0-9]+$ ]]; then
      echo "Invalid PID"
      exit 1
  fi
  kill -15 "$1"
  ```

---

### 5. Common Pitfalls and Fixes

- **Wrong PID**:
  - **Fix**: Verify:
    ```bash
    ps -p 1234
    pgrep python
    ```
- **Process Won’t Die**:
  - **Fix**: Escalate signal:
    ```bash
    kill -15 1234
    sleep 2
    kill -9 1234
    ```
- **Zombie Processes**:
  - **Fix**: Kill parent:
    ```bash
    ps -ef | grep '[Z]'
    # Find PPID
    kill -15 <PPID>
    ```
- **Permission Denied**:
  - **Fix**: Use `sudo`:
    ```bash
    sudo kill -9 1234
    ```
- **Lost Background Job**:
  - **Fix**: Check:
    ```bash
    jobs
    ps aux | grep <command>
    ```

---

### 6. Hands-On Challenge
To master process management:
1. **Setup**:
   - Start `sleep 1000 &`, `python -m http.server 8000 &`.
   - Create `monitor.log`.
2. **List**:
   - Use `ps aux` to find PIDs of `sleep` and `python`.
   - Use `htop` to view, filter by `user`.
3. **Control**:
   - Send `SIGTERM` to `sleep` via `kill`.
   - Send `SIGINT` to `python` via `pkill`.
   - Restart `python` with `nice -n 5`.
4. **Background**:
   - Run `sleep 200` in background, bring to foreground, stop with Ctrl+C.
   - Use `nohup` for a script (`echo Hi > out.txt`), verify it runs.
5. **Security**:
   - Log all kills to `monitor.log`.
   - Restrict a kill script (700, `user:user`).
Share commands/output, and I’ll review!

**Starter Commands**:
```bash
sleep 1000 &
python3 -m http.server 8000 &
touch monitor.log
ps aux
```

---

### 7. Advanced Tips

- **Signal Handling**:
  ```bash
  # trap.sh
  trap "echo 'Caught SIGTERM'; exit" SIGTERM
  while true; do sleep 1; done
  ```
  ```bash
  chmod +x trap.sh
  ./trap.sh &
  kill %1
  ```
- **Process Groups**:
  ```bash
  kill -- -$(ps -o pgid= 1234 | grep -v PGID)
  # Kill process group
  ```
- **Cgroups**:
  ```bash
  sudo cgcreate -g cpu:/lowprio
  cgexec -g cpu:/lowprio python app.py
  ```
- **Systemd Integration**:
  ```bash
  sudo systemctl status python-app
  sudo systemctl restart python-app
  ```
- **Monitor with Watch**:
  ```bash
  watch -n 1 'ps -C python -o pid,%cpu,%mem'
  ```


---

