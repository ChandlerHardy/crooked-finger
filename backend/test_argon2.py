#!/usr/bin/env python3
"""
Test script to verify Argon2 password hashing works correctly
Run: python test_argon2.py
"""

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

def test_argon2():
    print("🔐 Testing Argon2 Password Hashing\n")

    pwd_hasher = PasswordHasher()

    # Test 1: Simple password
    print("Test 1: Simple password")
    password1 = "debug"
    hash1 = pwd_hasher.hash(password1)
    print(f"  Password: {password1}")
    print(f"  Hash: {hash1[:50]}...")

    try:
        pwd_hasher.verify(hash1, password1)
        print("  ✅ Verification: PASSED\n")
    except VerifyMismatchError:
        print("  ❌ Verification: FAILED\n")
        return False

    # Test 2: Long password (would break bcrypt)
    print("Test 2: Long password (>72 bytes)")
    password2 = "a" * 100  # 100 characters
    hash2 = pwd_hasher.hash(password2)
    print(f"  Password length: {len(password2)} characters")
    print(f"  Hash: {hash2[:50]}...")

    try:
        pwd_hasher.verify(hash2, password2)
        print("  ✅ Verification: PASSED\n")
    except VerifyMismatchError:
        print("  ❌ Verification: FAILED\n")
        return False

    # Test 3: Wrong password should fail
    print("Test 3: Wrong password should fail")
    try:
        pwd_hasher.verify(hash1, "wrong_password")
        print("  ❌ Security issue: Wrong password accepted!\n")
        return False
    except VerifyMismatchError:
        print("  ✅ Security check: Wrong password correctly rejected\n")

    # Test 4: Special characters
    print("Test 4: Special characters")
    password4 = "p@ssw0rd!#$%^&*()_+-=[]{}|;:,.<>?"
    hash4 = pwd_hasher.hash(password4)
    print(f"  Password: {password4}")
    print(f"  Hash: {hash4[:50]}...")

    try:
        pwd_hasher.verify(hash4, password4)
        print("  ✅ Verification: PASSED\n")
    except VerifyMismatchError:
        print("  ❌ Verification: FAILED\n")
        return False

    print("=" * 50)
    print("🎉 All tests passed! Argon2 is working correctly.")
    print("=" * 50)
    return True

if __name__ == "__main__":
    success = test_argon2()
    exit(0 if success else 1)
