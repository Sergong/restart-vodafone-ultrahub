# restart-vodafone-ultrahub
Repo with python script to automate the restart a Vodafone Ultrahub 7 router

## Setup instructions

1. Install dependencies:
```
pip3 install -r requirements.txt
```

2. Install Chrome and ChromeDriver:
```
# On Ubuntu/Debian
sudo apt update
sudo apt install chromium-browser chromium-chromedriver

# On macOS with Homebrew
brew install chromedriver

# On RHEL/CentOS/Fedora
sudo dnf install chromium chromium-chromedriver
```

3. Configure the script:
- Edit the script and replace `YOUR_ROUTER_PASSWORD_HERE` with your actual router password
- Edit the script and replace `192.168.1.1` with your actual router IP address
- Adjust `LOG_FILE` path as needed
- Make the script executable: `chmod +x vodafone_restart.py`

4. Test the script:
```
python3 vodafone_restart.py
```

## CRON setup for automated restarts

1. Add to your crontab (crontab -e):
```
# Restart router daily at 3:00 AM
0 3 * * * /usr/bin/python3 /path/to/vodafone_restart.py

# Restart router weekly on Sunday at 2:00 AM
0 2 * * 0 /usr/bin/python3 /path/to/vodafone_restart.py

# Restart router on the first Sunday of the month at 1AM
0 1 1-7 * 0 /usr/bin/python3 /path/to/vodafone_restart.py

# Restart every 6 hours
0 */6 * * * /usr/bin/python3 /path/to/vodafone_restart.py
```
