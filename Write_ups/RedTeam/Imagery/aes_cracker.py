import subprocess
import os
import sys

# --- Configuration ---
# IMPORTANT: Update these paths if rockyou.txt is not decompressed.
AES_FILE = os.path.expanduser("~/Downloads/web_20250806_120723.zip.aes")
WORDLIST = "/usr/share/wordlists/rockyou.txt" 
OUTPUT_FILE = os.path.expanduser("~/Downloads/web_backup.zip")
# --- End Configuration ---

def decrypt_aes_bruteforce(aes_file, wordlist_path, output_file):
    """
    Attempts to decrypt an AES file using openssl and a wordlist.
    """
    if not os.path.exists(aes_file):
        print(f"[-] Error: AES file not found at {aes_file}")
        sys.exit(1)
    if not os.path.exists(wordlist_path):
        print(f"[-] Error: Wordlist file not found at {wordlist_path}")
        print("[-] Hint: Did you remember to decompress rockyou.txt.gz?")
        sys.exit(1)

    print(f"[+] Starting brute-force attack on: {aes_file}")
    print(f"[+] Using wordlist: {wordlist_path}")
    
    with open(wordlist_path, 'r', encoding='latin-1', errors='ignore') as f:
        for i, line in enumerate(f):
            password = line.strip()
            
            # Skip empty or very short passwords for efficiency
            if not password or len(password) < 4:
                continue

            sys.stdout.write(f"\r[>] Trying password #{i+1}: {password}")
            sys.stdout.flush()

            # The 'openssl' command for decryption
            # -aes-256-cbc: The encryption cipher, common for AES encryption.
            # -pbkdf2: Uses Password-Based Key Derivation Function (PBKDF2) for security.
            # -d: Decrypt mode.
            # -pass pass:PASSWORD: Passes the password directly.
            cmd = [
                "openssl", "enc", "-d", "-aes-256-cbc", "-pbkdf2",
                "-in", aes_file, "-out", output_file,
                "-pass", f"pass:{password}"
            ]
            
            # Run the command, suppressing all output (stderr)
            result = subprocess.run(cmd, stderr=subprocess.DEVNULL)
            
            # OpenSSL returns a zero exit code (0) on SUCCESSFUL decryption
            if result.returncode == 0:
                print(f"\n\n[🎉 SUCCESS!] Password found: '{password}'")
                print(f"[+] Decrypted backup saved to: {output_file}")
                
                # Attempt to unzip the file now
                try:
                    subprocess.run(["unzip", "-o", output_file], check=True, stdout=subprocess.DEVNULL)
                    print("[+] Files extracted successfully to the current directory.")
                except subprocess.CalledProcessError:
                    print("[-] Decryption successful, but unzip failed. The password may be correct, but file is corrupted.")
                
                return password

    print("\n[-] Attack exhausted. Password not found in the wordlist.")
    return None

if __name__ == "__main__":
    decrypted_password = decrypt_aes_bruteforce(AES_FILE, WORDLIST, OUTPUT_FILE)
    
    if decrypted_password:
        print("\n[Final Step] Search the extracted files (e.g., app.py, config.py) for the Flask SECRET_KEY!")