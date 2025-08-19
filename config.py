import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://bgrerr:6o6zDFVNFe9RpcKS@cluster0.3ymv6iq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
JWT_SECRET = os.getenv("JWT_SECRET", "secret-key")
JWT_ALGORITHM = "HS256"