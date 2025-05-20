# Gobuster Script Collection

## Script Catalog

### 1. Stealth Directory Scanner (`01_dir_stealth.sh`)

- **Purpose**: Low-profile directory discovery
- **Key Parameters**:
  ```bash
  --delay 300-700ms  # Random delays between requests
  --random-agent     # Rotate User-Agent headers
  -t 20              # Conservative thread count
  ```

### 2. PHP File Hunter (`02_files_php.sh`)

- **Purpose**: Find PHP files/configs
- **Wordlist**: `PHP.fuzz.txt` (PHP-specific paths)
- **Extensions**: php,phtml,phar

### 3. IIS/ASPX Scanner (`03_files_iis.sh`)

- **Target**: Microsoft IIS servers
- **Extensions**: aspx,ashx,asmx,config
- **User-Agent**: Mimics Chrome on Windows

### 4. API Endpoint Finder (`04_api_endpoints.sh`)

- **Focus**: Discover JSON API endpoints
- **Wordlist**: `Common-Api-Endpoints.txt`
- **SSL**: Bypass checks with `-k`

### 5. Subdomain Brute-Forcer (`05_subdomains.sh`)

- **DNS Resolvers**: Rotate between Cloudflare/Google/Quad9
- **Output**: Includes resolved IP addresses

### 6. Virtual Host Detector (`06_vhosts.sh`)

- **Tactic**: Find alternate sites on same IP
- **Append Domain**: Test `sub.domain.com` and `sub`

## Usage

```bash
# 1. Add domain to hosts
echo "10.129.95.234 unika.htb" | sudo tee -a /etc/hosts

# 2. Run scripts (example)
chmod +x *.sh
./01_dir_stealth.sh 10.129.95.234 unika.htb

# 3. Review results
tree gobuster/10.129.95.234
```

## Stealth Techniques

- **Random Delays**: Avoid fixed timing patterns
- **User-Agent Rotation**: Prevent UA-based detection
- **Thread Control**: Balance speed vs. detectability
- **Resolver Rotation**: Bypass DNS rate-limiting
