from Crypto.PublicKey import RSA
import os

def generate_rsa_keys():
    # Check if keys already exist
    if not os.path.exists('private_key.pem') or not os.path.exists('public_key.pem'):
        # Generate a new RSA key pair
        key = RSA.generate(2048)
        private_key = key.export_key('PEM')
        public_key = key.publickey().export_key('PEM')

        # Save the private key
        with open('private_key.pem', 'wb') as f:
            f.write(private_key)

        # Save the public key
        with open('public_key.pem', 'wb') as f:
            f.write(public_key)

        print("RSA key pair generated and saved as 'private_key.pem' and 'public_key.pem'.")
    else:
        print("RSA key pair already exists.")

if __name__ == "__main__":
    generate_rsa_keys()
