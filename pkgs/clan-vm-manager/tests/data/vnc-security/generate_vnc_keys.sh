#!/usr/bin/env bash

# Step 0: Define CA subject details
CA_SUBJECT="/C=US/ST=YourState/L=YourCity/O=YourCAOrganization/OU=YourCADepartment/CN=127.0.0.1"

# Step 1: Generate the CA's private key
openssl genpkey -algorithm RSA -out ca.key -pkeyopt rsa_keygen_bits:2048

# Step 2: Create a self-signed CA certificate
openssl req -x509 -new -nodes -key ca.key -sha256 -days 3650 -out ca.crt -subj "$CA_SUBJECT" -addext "subjectAltName = IP:127.0.0.1"

# Step 3: Generate a private key for the TLS certificate
openssl genpkey -algorithm RSA -out tls.key -pkeyopt rsa_keygen_bits:2048

# Step 4: Create a Certificate Signing Request (CSR) for the TLS certificate
TLS_SUBJECT="/C=US/ST=YourState/L=YourCity/O=YourOrganization/OU=YourDepartment/CN=127.0.0.1"
openssl req -new -key tls.key -out tls.csr -subj "$TLS_SUBJECT" -addext "subjectAltName = IP:127.0.0.1"

# Step 5: Sign the CSR with your CA to generate the TLS certificate
openssl x509 -req -in tls.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out tls.crt -days 365 -sha256 -extfile <(printf "subjectAltName=IP:127.0.0.1")

echo "CA and TLS certificate, CSR, and key have been generated."
