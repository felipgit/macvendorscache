from flask import Flask, request
import sqlite3
import requests

app = Flask(__name__)

# Change to path where your database will be stored
DATABASE = 'mac_address.db'

def create_table():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS mac_address
                 (address TEXT PRIMARY KEY, vendor TEXT)''')
    conn.commit()
    conn.close()

def get_vendor_from_db(mac_address):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT vendor FROM mac_address WHERE address=?", (mac_address,))
    result = c.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return None

def add_vendor_to_db(mac_address, vendor):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("INSERT INTO mac_address (address, vendor) VALUES (?, ?)", (mac_address, vendor))
    conn.commit()
    conn.close()

def get_vendor_from_macvendors(mac_address):
    response = requests.get(f'https://api.macvendors.com/{mac_address}')
    if response.ok:
        vendor = response.text
        add_vendor_to_db(mac_address[:6], vendor)
        return vendor
    else:
        return None

@app.route("/")
def home():
    return "get a vendor of your mac"

@app.route('/api/v1/mac/<string:mac_address>')
def get_mac_vendor(mac_address):
    mac_address = mac_address.replace(':', '').replace('-', '').replace('.', '').upper()
    if len(mac_address) != 12:
        return "Invalid MAC address", 400
    mac_prefix = mac_address[:6]
    vendor = get_vendor_from_db(mac_prefix)
    if vendor:
        return vendor
    else:
        vendor = get_vendor_from_macvendors(mac_address)
        if vendor:
            return vendor
        else:
            return "Unable to determine vendor", 500

if __name__ == '__main__':
    create_table()
    app.run(debug=True, host='0.0.0.0')
