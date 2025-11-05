from flask import Flask, render_template, request
from pymysql import connections
import os, logging, boto3, botocore

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# ---------- Environment variables ----------
DBHOST = os.getenv("DBHOST", "localhost")
DBUSER = os.getenv("DBUSER", "root")
DBPWD = os.getenv("DBPWD", "password")
DATABASE = os.getenv("DATABASE", "employees")
DBPORT = int(os.getenv("DBPORT", 3306))

BG_URL = os.getenv("BG_URL", "")          # s3://bucket/path/image.jpg
HEADER_NAME = os.getenv("HEADER_NAME", "CLO835 Student")

# ---------- MySQL Connection ----------
try:
    db_conn = connections.Connection(
        host=DBHOST, port=DBPORT, user=DBUSER, password=DBPWD, db=DATABASE
    )
except Exception as e:
    logging.warning(f"MySQL not reachable yet: {e}")
    db_conn = None

# ---------- Download background image ----------
def fetch_bg():
    """Download the image from S3 to local static folder"""
    if not BG_URL.startswith("s3://"):
        logging.warning("BG_URL not set or invalid.")
        return
    logging.info(f"[CLO835] Background image URL: {BG_URL}")
    _, rest = BG_URL.split("s3://", 1)
    bucket, key = rest.split("/", 1)
    s3 = boto3.client("s3")
    os.makedirs("static", exist_ok=True)
    local_path = os.path.join("static", "bg.jpg")
    try:
        s3.download_file(bucket, key, local_path)
    except botocore.exceptions.ClientError as e:
        logging.error(f"Failed to fetch bg: {e}")
fetch_bg()

# ---------- Routes ----------
@app.route("/")
def home():
    return render_template("about.html", header_name=HEADER_NAME)

@app.route("/about")
def about():
    return render_template("about.html", header_name=HEADER_NAME)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=81)
