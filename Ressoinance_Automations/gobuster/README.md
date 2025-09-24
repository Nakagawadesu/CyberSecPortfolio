# Gobuster Script Suite

## Key Features

- **Single Parameter**: Accepts IP or domain (auto-resolves via DNS/hosts file)
- **Stealth-Optimized**: Random delays, rotated User-Agents, request throttling
- **Scenario-Specific**: PHP, IIS, API, subdomain, and virtual host scans
- **Organized Output**: Results stored in `gobuster/<sanitized_ip>/` with clear naming
- **Enterprise Ready**: DNS resolver rotation, SSL bypass, and legacy system support

## Script Catalog

### 1. Stealth Directory Scanner (`01_stealth_scan.sh`)

- **Purpose**: Low-noise directory discovery
- **Key Parameters**:
  ```bash
  --delay 500ms       # Randomized delay between 300-700ms
  --random-agent      # Rotate through 100+ User-Agents
  -x html,php,txt     # Focus on common web extensions
  ```

### 2. PHP File Hunter (`02_php_scan.sh`)

- **Target**: PHP-based applications (WordPress, Laravel)
- **Wordlist**: Specialized `PHP.fuzz.txt` list
- **Extensions**: php, phtml, phar (common PHP file types)

### 3. IIS/ASPX Scanner (`03_iis_scan.sh`)

- **Focus**: Microsoft IIS servers and .NET applications
- **Parameters**:
  ```bash
  -x aspx,ashx,asmx  # ASP.NET extensions
  --user-agent "Mozilla/4.0..." # Legacy IE user-agent
  ```

### 4. API Endpoint Finder (`04_api_scan.sh`)

- **Discovery**: REST API endpoints and JSON resources
- **Wordlist**: `Common-Api-Endpoints.txt` with 1500+ paths
- **SSL Bypass**: `-k` ignores certificate errors

### 5. Subdomain Brute-Forcer (`05_subdomains.sh`)

- **DNS Resolution**: Multi-resolver support (Cloudflare, Google)
- **Output**: Includes IP addresses and canonical names
- **Threading**: High-speed 40-thread scanning

### 6. Virtual Host Detector (`06_vhosts.sh`)

- **Purpose**: Discover alternate sites on same IP
- **Key Features**:
  ```bash
  --append-domain    # Test both "sub" and "sub.domain.com"
  -w subdomains-top1million-20000.txt # Comprehensive list
  -t 20              # Balance speed and stealth
  ```

## Usage

### Basic Execution

```bash
# For domains (must resolve via DNS/hosts file)
./01_stealth_scan.sh example.com

# For raw IPs
./03_iis_scan.sh 10.129.95.234

# Virtual host discovery
./06_vhosts.sh unika.htb
```

### Advanced Options

```bash
# Custom resolvers (subdomain scan)
DNS_RESOLVERS="1.1.1.1,8.8.8.8" ./05_subdomains.sh example.com

# Output debugging
DEBUG=1 ./04_api_scan.sh 10.129.95.234
```

## Technical Details

### Output Structure

```bash
gobuster/
└─ 10_129_95_234/          # Sanitized IP/Domain
   ├─ 01_stealth_scan.txt  # Stealth scan results
   ├─ 02_php_scan.txt      # PHP file findings
   ├─ 03_iis_scan.txt      # IIS-specific results
   ├─ 04_api_scan.txt      # API endpoints
   ├─ 05_subdomains.txt    # Subdomain list
   └─ 06_vhosts.txt        # Virtual host discoveries
```

### Detection Avoidance

- **Request Randomization**: Varies delay times and User-Agents
- **Header Spoofing**: Mimics legitimate browser signatures
- **DNS Obfuscation**: Uses reputable DNS resolvers
- **SSL Passthrough**: Ignores certificate validation errors

### Performance Metrics

| Script Type       | Avg Requests/Min | Threads | Wordlist Size |
| ----------------- | ---------------- | ------- | ------------- |
| Stealth Scan      | 120              | 20      | 35,000        |
| Subdomain Scan    | 500              | 40      | 20,000        |
| Virtual Host Scan | 200              | 20      | 20,000        |

## Best Practices

1. **Order of Execution**:
   ```bash
   01_stealth → 05_subdomains → 06_vhosts → 02-04 specialized scans
   ```
2. **Wordlist Rotation**: Cycle wordlists weekly for repeat scans
3. **Output Analysis**: Use `grep -Ri "admin" gobuster/` for quick triage

## Legal & Ethics

- Use only on authorized targets
- Respect robots.txt and service terms
- Delete output after engagement completion
