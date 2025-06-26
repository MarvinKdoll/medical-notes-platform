import secrets


print("=" * 60)
print("GENERATING JWT SECRET KEY")
print("=" * 60)

jwt_secret = secrets.token_hex(32)

print(f" Your JWT Secret: {jwt_secret}")
print()
print("Next Steps:")
print("1. Copy this secret key")
print("2. Save it somewhere secure")
print("3. Set as enviorment variable: JWT_SECRET_KEY")
print()
print("COMMANDS TO SET ENVIROMENT VARIABLE: ")
print(f"Mac.Linux: export JWT_SECRET_KEY='{jwt_secret}'")
print()
print("FOR AWS LAMBDA:")
print("Go to LAmbda console -> Configuration -> Enviroment variables")
print(f"Key: JWT_SECRET_KEY")
print(f"Value: {jwt_secret}")
print("=" * 60)

with open ('jwt_secret.txt', 'w') as f:
    f.write(f"JWT_SECRET_KEY={jwt_secret}\n")
    f.write(f"Generated on: {secrets.token_hex(8)}\n")

print("Secret also saved to 'jwt_secret.txt'")
print("IMPORTANT: Add 'jwt_secret.txt' to your .gitignore file")