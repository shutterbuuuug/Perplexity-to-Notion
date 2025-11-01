#!/usr/bin/env python3
"""
HTTPS Certificate Generator
===========================

Generates self-signed SSL certificates for development and testing.

For production use, obtain certificates from Let's Encrypt:
    certbot certonly --standalone -d your-domain.com

Usage:
    python generate_https_cert.py --domain localhost --output-dir ../certs
    python generate_https_cert.py --domain api.example.com --days 365

Author: Claude Code - Security Enhancement
License: MIT
"""

import argparse
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timedelta


def generate_certificate(
    domain: str,
    output_dir: Path,
    days: int = 365,
    key_size: int = 4096
) -> bool:
    """
    Generate self-signed SSL certificate.

    Args:
        domain: Domain name for certificate
        output_dir: Directory to store certificate files
        days: Certificate validity period in days
        key_size: RSA key size in bits

    Returns:
        True if successful
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    cert_file = output_dir / 'cert.pem'
    key_file = output_dir / 'key.pem'

    print(f"🔐 Generating SSL certificate for {domain}...")
    print(f"   Key size: {key_size} bits")
    print(f"   Valid for: {days} days")
    print(f"   Output: {output_dir}")

    # Generate certificate using OpenSSL
    cmd = [
        'openssl', 'req',
        '-x509',
        '-newkey', f'rsa:{key_size}',
        '-keyout', str(key_file),
        '-out', str(cert_file),
        '-days', str(days),
        '-nodes',
        '-subj', f'/CN={domain}/O=Perplexity-to-Notion/C=US'
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        print(f"✓ Certificate generated: {cert_file}")
        print(f"✓ Private key generated: {key_file}")

        # Set proper permissions
        key_file.chmod(0o600)
        cert_file.chmod(0o644)

        print(f"\n⚠️  WARNING: This is a self-signed certificate!")
        print("   Browsers will show security warnings.")
        print("   For production, use Let's Encrypt:")
        print(f"     certbot certonly --standalone -d {domain}")

        # Display certificate info
        print(f"\n📋 Certificate Information:")
        display_cert_info(cert_file)

        # Usage instructions
        print(f"\n📝 Usage in webhook server:")
        print(f"   python perplexity_to_notion.py --webhook \\")
        print(f"     --cert {cert_file} \\")
        print(f"     --key {key_file}")

        return True

    except FileNotFoundError:
        print("❌ Error: OpenSSL not found")
        print("   Install OpenSSL:")
        print("     Ubuntu/Debian: sudo apt install openssl")
        print("     macOS: brew install openssl")
        print("     Termux: pkg install openssl")
        return False

    except subprocess.CalledProcessError as e:
        print(f"❌ Error generating certificate: {e}")
        print(e.stderr)
        return False


def display_cert_info(cert_file: Path):
    """Display certificate information."""
    cmd = ['openssl', 'x509', '-in', str(cert_file), '-text', '-noout']

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # Extract key information
        lines = result.stdout.split('\n')
        for line in lines:
            if 'Subject:' in line or 'Not Before' in line or 'Not After' in line:
                print(f"   {line.strip()}")

    except subprocess.CalledProcessError:
        pass


def check_certificate(cert_file: Path, key_file: Path) -> bool:
    """
    Verify certificate and key match.

    Args:
        cert_file: Path to certificate file
        key_file: Path to private key file

    Returns:
        True if valid and matching
    """
    print(f"\n🔍 Verifying certificate and key...")

    # Check certificate
    cmd_cert = ['openssl', 'x509', '-in', str(cert_file), '-noout', '-modulus']
    # Check key
    cmd_key = ['openssl', 'rsa', '-in', str(key_file), '-noout', '-modulus']

    try:
        result_cert = subprocess.run(cmd_cert, capture_output=True, text=True, check=True)
        result_key = subprocess.run(cmd_key, capture_output=True, text=True, check=True)

        if result_cert.stdout == result_key.stdout:
            print("✓ Certificate and key match")
            return True
        else:
            print("❌ Certificate and key do NOT match")
            return False

    except subprocess.CalledProcessError as e:
        print(f"❌ Verification failed: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate self-signed SSL certificate for HTTPS webhook server',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate certificate for localhost
  python generate_https_cert.py --domain localhost --output-dir ../certs

  # Generate certificate for specific domain with custom validity
  python generate_https_cert.py --domain api.example.com --days 365

  # Check existing certificate
  python generate_https_cert.py --check ../certs/cert.pem ../certs/key.pem

Production Note:
  For production deployments, use Let's Encrypt for trusted certificates:
    sudo certbot certonly --standalone -d your-domain.com
        """
    )

    parser.add_argument(
        '--domain', '-d',
        default='localhost',
        help='Domain name for certificate (default: localhost)'
    )
    parser.add_argument(
        '--output-dir', '-o',
        type=Path,
        default=Path('certs'),
        help='Output directory for certificate files (default: certs/)'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=365,
        help='Certificate validity in days (default: 365)'
    )
    parser.add_argument(
        '--key-size',
        type=int,
        default=4096,
        choices=[2048, 4096, 8192],
        help='RSA key size in bits (default: 4096)'
    )
    parser.add_argument(
        '--check',
        nargs=2,
        metavar=('CERT', 'KEY'),
        help='Verify existing certificate and key match'
    )

    args = parser.parse_args()

    print("=" * 70)
    print("HTTPS Certificate Generator")
    print("Perplexity to Notion - Security Enhancement")
    print("=" * 70)

    if args.check:
        # Verification mode
        cert_path = Path(args.check[0])
        key_path = Path(args.check[1])

        if not cert_path.exists():
            print(f"❌ Certificate not found: {cert_path}")
            return 1

        if not key_path.exists():
            print(f"❌ Key not found: {key_path}")
            return 1

        success = check_certificate(cert_path, key_path)
        return 0 if success else 1

    else:
        # Generation mode
        success = generate_certificate(
            domain=args.domain,
            output_dir=args.output_dir,
            days=args.days,
            key_size=args.key_size
        )

        if success:
            print(f"\n✅ Certificate generation complete!")
            return 0
        else:
            print(f"\n❌ Certificate generation failed")
            return 1


if __name__ == '__main__':
    sys.exit(main())
