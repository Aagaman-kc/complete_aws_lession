# Day 1 — AWS Core Concepts

## 1. Cloud Computing Basics

- Cloud = renting compute/storage over the internet instead of owning physical servers
- AWS provides on-demand, pay-as-you-go infrastructure
- Key benefits: elasticity, scalability, no upfront cost

---

## 2. EC2 — Elastic Compute Cloud

### 2.1 Dynamic Public IP
- Assigned automatically to EC2 instances
- Changes when instance is stopped and started
- Free while instance is running
- Belongs to the instance, not to your account

### 2.2 Elastic IP (EIP)
- A static public IPv4 address reserved to your AWS account
- Stays the same until you release it
- Can be moved between instances
- Charge applies if allocated but not attached to a running instance

| Dynamic IP | Elastic IP |
|-----------|------------|
| Belongs to the instance while running | Belongs to your AWS account |
| Changes after stop/start | Stays the same |
| Good for testing | Good for production |
| Can't be moved | Can be reassigned |

**Best practice**: Use a Load Balancer instead of exposing EC2 directly via EIP.

---

## 3. SSH & Public Key Cryptography

### 3.1 How Key Pairs Work

| Key | Role | Who Has It |
|-----|------|-----------|
| Private Key | Creates signatures | You (never leaves your machine) |
| Public Key | Verifies signatures | AWS (stored on server) |

### 3.2 RSA Signing Flow
1. AWS sends a challenge (random number)
2. Your laptop signs it with the private key: `signature = message^d mod n`
3. AWS verifies with the public key: `message = signature^e mod n`
4. Match = identity proven, private key never transmitted

### 3.3 Why RSA Is Secure
- Multiplying two primes is easy
- Factoring the product back into primes is extremely hard
- This asymmetry is the foundation of RSA security
