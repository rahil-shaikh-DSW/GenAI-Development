
---

### Resources
- **Permissions**: [man7.org/linux/man-pages/chmod](https://man7.org/linux/man-pages) (web:6).
- **Ownership**: [linuxize.com/post/chown](https://linuxize.com/post/linux-chown-command) (web:17).
- **Tutorials**:
  - “Linux Permissions” [freecodecamp.org](https://www.freecodecamp.org) (web:0).
  - “Chmod Guide” [digitalocean.com](https://www.digitalocean.com) (web:12).
- **Community**: Linux Stack Exchange, X `#Linux` (post:1,4,6).

---

### 1. Understanding File Permissions and Ownership

- **Definition**: 
  - **Permissions**: Rules defining who can **read**, **write**, or **execute** a file or directory, assigned to **owner**, **group**, and **others** (per web:0,6).
  - **Ownership**: Specifies the **user** (owner) and **group** associated with a file or directory, controlling access rights (per web:3).
- **Why It Matters**:
  - **Security**: Restrict access to sensitive data (e.g., `/etc/passwd`) (per web:12).
  - **Collaboration**: Share files safely within teams via group permissions (per web:17).
  - **Functionality**: Ensure scripts or binaries run correctly (e.g., `+x` for executables) (per web:19).
- **Key Concepts**:
  - **Users**: Individual accounts (e.g., `user`, `root`).
  - **Groups**: Collections of users (e.g., `devs`, `sudo`).
  - **Permission Types**:
    - `r` (read): View file contents or list directory.
    - `w` (write): Modify file or create/delete in directory.
    - `x` (execute): Run file (script/binary) or enter directory.
  - **Permission Display**:
    ```bash
    ls -l
    # Output: -rwxr-xr-- 1 user devs 123 Apr 13 12:00 script.sh
    ```
    - `-`: Regular file (`d` for directory, `l` for link).
    - `rwx`: Owner (read, write, execute).
    - `r-x`: Group (read, execute).
    - `r--`: Others (read only).
    - `user`: Owner.
    - `devs`: Group.

#### 1.1 File System Context
- **Locations**:
  - `/home/user`: User-owned files, typically `rwxr-xr-x` (755) for dirs, `rw-r--r--` (644) for files.
  - `/etc`: System configs, often `root:root`, `rw-r--r--` (644).
  - `/tmp`: World-writable, `rwxrwxrwt` (1777, sticky bit).
- **Special Bits**:
  - **Setuid**: Run as owner (e.g., `passwd`, `rwsr-xr-x`).
  - **Setgid**: Run/inherit group (e.g., `rwxr-sr-x`).
  - **Sticky Bit**: Restrict deletion in shared dirs (e.g., `/tmp`, `rwxrwxrwt`).

#### 1.2 Setup
- **Environment**: Ubuntu 24.04.
  ```bash
  sudo apt update
  lsb_release -a  # Verify: Ubuntu 24.04 LTS
  ```
- **Users/Groups**:
  ```bash
  sudo useradd -m alice
  sudo useradd -m bob
  sudo groupadd devs
  sudo usermod -aG devs alice
  sudo usermod -aG devs bob
  ```
  - Verify:
    ```bash
    id alice
    # Output: uid=1001(alice) ... groups=...1001(devs)
    ```

---

### 2. Managing Permissions with `chmod`

- **Purpose**: `chmod` (change mode) modifies file/directory permissions for owner (`u`), group (`g`), others (`o`), or all (`a`).
- **Modes**:
  - **Symbolic**: `u+rwx`, `g-w`, etc.
  - **Numeric**: Octal (e.g., `755` = `rwxr-xr-x`).
    - `4` = read, `2` = write, `1` = execute.
    - Sum per category (e.g., `7` = `rwx`, `5` = `r-x`).

#### 2.1 Usage
- **Create Test File**:
  ```bash
  touch file.txt
  ls -l
  # Output: -rw-r--r-- 1 user user 0 Apr 13 12:00 file.txt
  ```
- **Symbolic Mode**:
  ```bash
  chmod u+x file.txt  # Add execute for owner
  ls -l
  # Output: -rwxr--r-- 1 user user 0 ...
  ```
  ```bash
  chmod g+w,o-r file.txt  # Group write, others no read
  ls -l
  # Output: -rwxrw---- 1 user user 0 ...
  ```
  ```bash
  chmod a=r file.txt  # All read-only
  ls -l
  # Output: -r--r--r-- 1 user user 0 ...
  ```
- **Numeric Mode**:
  ```bash
  chmod 755 script.sh  # Owner: rwx, group/others: r-x
  ls -l
  # Output: -rwxr-xr-x 1 user user 0 ...
  ```
  ```bash
  chmod 600 secret.txt  # Owner: rw, others: none
  ls -l
  # Output: -rw------- 1 user user 0 ...
  ```
- **Recursive**:
  ```bash
  mkdir -p project/docs
  chmod -R 750 project/  # Owner: rwx, group: r-x, others: none
  ls -ld project/
  # Output: drwxr-x--- 2 user user ...
  ```

#### 2.2 Special Bits
- **Setuid** (`4000`):
  ```bash
  chmod u+s binary
  ls -l
  # Output: -rwsr-xr-x
  ```
- **Setgid** (`2000`):
  ```bash
  chmod g+s shared_dir
  ls -ld
  # Output: drwxr-sr-x
  ```
- **Sticky Bit** (`1000`):
  ```bash
  chmod +t shared/
  ls -ld
  # Output: drwxrwxrwt
  ```
- **Example**:
  ```bash
  mkdir shared
  chmod 1777 shared  # Sticky bit + world-writable
  ls -ld shared
  # Output: drwxrwxrwt
  ```

#### 2.3 Options
- `-v`: Verbose.
  ```bash
  chmod -v 644 file.txt
  # Output: mode of 'file.txt' changed to 0644 (rw-r--r--)
  ```
- `-R`: Recursive.
  ```bash
  chmod -R u+w project/
  ```

---

### 3. Managing Ownership with `chown`

- **Purpose**: `chown` (change owner) assigns a user and/or group to a file or directory.

#### 3.1 Usage
- **Change Owner**:
  ```bash
  sudo chown alice file.txt
  ls -l
  # Output: -rw-r--r-- 1 alice user 0 ...
  ```
- **Change Group**:
  ```bash
  sudo chown :devs file.txt
  ls -l
  # Output: -rw-r--r-- 1 alice devs 0 ...
  ```
- **Both**:
  ```bash
  sudo chown alice:devs file.txt
  ls -l
  # Output: -rw-r--r-- 1 alice devs 0 ...
  ```
- **Recursive**:
  ```bash
  sudo chown -R alice:devs project/
  ls -ld project/
  # Output: drwxr-xr-x 2 alice devs ...
  ```

#### 3.2 Options
- `-v`: Verbose.
  ```bash
  sudo chown -v alice file.txt
  # Output: changed ownership of 'file.txt' from user to alice
  ```
- `-R`: Recursive.
- `--reference`: Copy from another file.
  ```bash
  sudo chown --reference=file.txt file2.txt
  ```

---

### 4. Related Commands

- **chgrp** (Change Group):
  ```bash
  chgrp devs file.txt
  ls -l
  # Output: -rw-r--r-- 1 user devs 0 ...
  ```
  - Recursive:
    ```bash
    chgrp -R devs project/
    ```
- **ls -l**: View permissions/ownership.
  ```bash
  ls -l file.txt
  # Output: -rw-r--r-- 1 alice devs 0 ...
  ```
- **id**: Check user/groups.
  ```bash
  id alice
  # Output: uid=1001(alice) ... groups=1001(devs)
  ```
- **stat**: Detailed file info.
  ```bash
  stat file.txt
  # Output: Access: (0644/-rw-r--r--) Uid: (1001/alice) Gid: (1001/devs)
  ```
- **umask**: Set default permissions for new files.
  ```bash
  umask 022  # New files: 644, dirs: 755
  touch new.txt
  ls -l
  # Output: -rw-r--r-- 1 user user 0 ...
  ```
  - Persist:
    ```bash
    echo "umask 022" >> ~/.bashrc
    ```

---

### 5. Practical Examples

- **Secure Config**:
  ```bash
  touch config.txt
  sudo chown root:root config.txt
  chmod 600 config.txt
  ls -l
  # Output: -rw------- 1 root root 0 ...
  ```
- **Team Project**:
  ```bash
  mkdir -p team/code
  sudo chown -R :devs team/
  chmod -R 770 team/  # Owner/group: rwx, others: none
  ls -ld team/
  # Output: drwxrwx--- 2 user devs ...
  ```
- **Executable Script**:
  ```bash
  echo 'echo "Run me!"' > script.sh
  chmod +x script.sh
  sudo chown alice:devs script.sh
  ls -l
  # Output: -rwxr-xr-x 1 alice devs ...
  ./script.sh  # Output: Run me!
  ```
- **Shared Directory**:
  ```bash
  mkdir shared
  sudo chown :devs shared
  chmod 2775 shared  # Setgid + group rwx
  ls -ld
  # Output: drwxrwsr-x 2 user devs ...
  ```

---

### 6. Security Best Practices

- **Least Privilege**:
  ```bash
  chmod 600 private.txt
  sudo chown user:user private.txt
  ```
- **Restrict Root**:
  ```bash
  sudo chown root:root /etc/secret.conf
  chmod 400 /etc/secret.conf  # Read-only for root
  ```
- **Group Collaboration**:
  ```bash
  sudo chown -R :devs /project
  chmod -R g+w /project
  chmod g+s /project  # Inherit group
  ```
- **Sticky Bit for Shared Dirs**:
  ```bash
  chmod 1777 /tmp/shared
  ```
- **Audit Changes**:
  ```bash
  chmod 644 file.txt && echo "Set 644 on file.txt at $(date)" >> perm.log
  ```
- **Backup**:
  ```bash
  cp -r sensitive/ sensitive.bak
  chmod -R 700 sensitive.bak
  ```

---

### 7. Common Pitfalls and Fixes

- **Permission Denied**:
  - **Fix**: Check permissions/ownership:
    ```bash
    ls -l file.txt
    sudo chmod u+w file.txt
    sudo chown user file.txt
    ```
- **Wrong Permissions**:
  - **Fix**: Reset:
    ```bash
    chmod 644 file.txt  # Files
    chmod 755 dir/     # Dirs
    ```
- **Recursive Overreach**:
  - **Fix**: Be specific:
    ```bash
    chmod -R u+w project/code/  # Not project/
    ```
- **Group Access Fails**:
  - **Fix**: Verify membership:
    ```bash
    id bob
    sudo usermod -aG devs bob
    ```
- **Executable Won’t Run**:
  - **Fix**: Add `x`:
    ```bash
    chmod +x script.sh
    ./script.sh
    ```

---

### 8. Hands-On Challenge
To master permissions and ownership:
1. **Setup**:
   - Create `secure.txt`, `script.sh` (“echo Hi”), `shared/docs/`.
   - Create users `alice`, `bob`; group `team`.
2. **Ownership**:
   - Set `secure.txt` to `alice:alice`.
   - Set `shared/` to `user:team`.
3. **Permissions**:
   - `secure.txt`: Owner-only (600).
   - `script.sh`: Executable, `alice:team`, 750.
   - `shared/`: Group rwx, setgid, others none (2770).
4. **Test**:
   - As `bob`, try reading `secure.txt` (should fail).
   - As `bob`, run `script.sh` (should succeed).
   - Create file in `shared/`; verify group `team`.
5. **Security**:
   - Log changes to `access.log`.
   - Backup `secure.txt`.
Share commands/output, and I’ll review!

**Starter Commands**:
```bash
touch secure.txt
echo "echo Hi" > script.sh
mkdir -p shared/docs
sudo useradd -m alice
sudo useradd -m bob
sudo groupadd team
```

---

### 9. Advanced Tips

- **Default Permissions**:
  ```bash
  umask 027  # Files: 640, dirs: 750
  echo "umask 027" >> ~/.bashrc
  ```
- **ACLs** (Access Control Lists):
  ```bash
  sudo apt install -y acl
  setfacl -m u:bob:rw file.txt
  getfacl file.txt
  # Output: user:bob:rw-
  ```
- **Monitor Changes**:
  ```bash
  sudo apt install -y auditd
  sudo auditctl -w /home/user -p wa -k file-changes
  sudo ausearch -k file-changes
  ```
- **Scripted Management**:
  ```bash
  # secure.sh
  #!/bin/bash
  [ -z "$1" ] && { echo "Usage: $0 file"; exit 1; }
  sudo chown alice:team "$1"
  chmod 640 "$1"
  echo "Secured $1 at $(date)" >> access.log
  ```
  ```bash
  chmod +x secure.sh
  ./secure.sh file.txt
  ```
- **Find by Permissions**:
  ```bash
  find /home -perm -4000  # Setuid files
  find . -perm 777  # World-writable
  ```



---
