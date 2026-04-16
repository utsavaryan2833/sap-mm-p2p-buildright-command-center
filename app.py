import json
import sqlite3
from datetime import datetime
from decimal import Decimal
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "buildright_p2p.db"


ORG_DATA = [
    ("Company Code", "BR01"),
    ("Plant", "BR01 (Delhi)"),
    ("Purchasing Organization", "BR10"),
    ("Purchasing Group", "BR1"),
    ("Storage Location", "0001"),
    ("Business Area", "Construction Raw Materials"),
]

MASTER_DATA = [
    ("Vendor", "SteelCo Supplies Ltd."),
    ("Vendor Code", "V-BR-1001"),
    ("Material", "STL001"),
    ("Description", "Structural Steel Rods"),
    ("Material Type", "ROH"),
    ("Base UoM", "EA"),
    ("Valuation Class", "3000"),
    ("GR Processing Time", "1 Day"),
]

SEQUENCE_DEFAULTS = {
    "pr": 410000001,
    "rfq": 420000001,
    "quotation": 430000001,
    "po": 450000001,
    "gr": 500000001,
    "invoice": 510000001,
    "payment": 520000001,
    "fi": 900000001,
}

PREFIXES = {
    "pr": "PR",
    "rfq": "RFQ",
    "quotation": "QT",
    "po": "PO",
    "gr": "MAT",
    "invoice": "IV",
    "payment": "PY",
    "fi": "FI",
}

TIMELINE = [
    {"key": "pr", "title": "Purchase Requisition", "code": "ME51N"},
    {"key": "rfq", "title": "Request for Quotation", "code": "ME41"},
    {"key": "quotation", "title": "Vendor Quotation", "code": "ME47"},
    {"key": "po", "title": "Purchase Order", "code": "ME21N"},
    {"key": "gr", "title": "Goods Receipt", "code": "MIGO"},
    {"key": "invoice", "title": "Invoice Verification", "code": "MIRO"},
    {"key": "payment", "title": "Vendor Payment", "code": "F-53"},
]


def utc_now():
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def decimal_value(value):
    return float(Decimal(str(value)).quantize(Decimal("1.00")))


def dict_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


class P2PDatabase:
    def __init__(self, db_path):
      self.db_path = db_path
      self.initialize()

    def connect(self):
      conn = sqlite3.connect(self.db_path)
      conn.row_factory = dict_factory
      return conn

    def initialize(self):
      conn = self.connect()
      cur = conn.cursor()
      cur.executescript(
          """
          CREATE TABLE IF NOT EXISTS organization_data (
              label TEXT PRIMARY KEY,
              value TEXT NOT NULL
          );

          CREATE TABLE IF NOT EXISTS master_data (
              label TEXT PRIMARY KEY,
              value TEXT NOT NULL
          );

          CREATE TABLE IF NOT EXISTS sequences (
              key TEXT PRIMARY KEY,
              next_value INTEGER NOT NULL
          );

          CREATE TABLE IF NOT EXISTS documents (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              type TEXT NOT NULL,
              number TEXT NOT NULL UNIQUE,
              reference TEXT NOT NULL,
              status TEXT NOT NULL,
              value REAL NOT NULL DEFAULT 0,
              created_on TEXT NOT NULL,
              payload_json TEXT NOT NULL
          );

          CREATE TABLE IF NOT EXISTS postings (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              fi_number TEXT NOT NULL UNIQUE,
              doc_number TEXT NOT NULL,
              debit_account TEXT NOT NULL,
              credit_account TEXT NOT NULL,
              amount REAL NOT NULL,
              created_on TEXT NOT NULL,
              payload_json TEXT NOT NULL
          );
          """
      )

      cur.execute("SELECT COUNT(*) AS count FROM organization_data")
      if cur.fetchone()["count"] == 0:
          cur.executemany("INSERT INTO organization_data (label, value) VALUES (?, ?)", ORG_DATA)

      cur.execute("SELECT COUNT(*) AS count FROM master_data")
      if cur.fetchone()["count"] == 0:
          cur.executemany("INSERT INTO master_data (label, value) VALUES (?, ?)", MASTER_DATA)

      cur.execute("SELECT COUNT(*) AS count FROM sequences")
      if cur.fetchone()["count"] == 0:
          cur.executemany(
              "INSERT INTO sequences (key, next_value) VALUES (?, ?)",
              list(SEQUENCE_DEFAULTS.items()),
          )

      conn.commit()
      conn.close()

    def reset(self):
      conn = self.connect()
      cur = conn.cursor()
      cur.execute("DELETE FROM documents")
      cur.execute("DELETE FROM postings")
      cur.execute("DELETE FROM sequences")
      cur.executemany(
          "INSERT INTO sequences (key, next_value) VALUES (?, ?)",
          list(SEQUENCE_DEFAULTS.items()),
      )
      conn.commit()
      conn.close()

    def get_master_snapshot(self):
      conn = self.connect()
      cur = conn.cursor()
      org = cur.execute("SELECT label, value FROM organization_data").fetchall()
      master = cur.execute("SELECT label, value FROM master_data").fetchall()
      conn.close()
      return {
          "organization": [[row["label"], row["value"]] for row in org],
          "core": [[row["label"], row["value"]] for row in master],
      }

    def next_number(self, key):
      conn = self.connect()
      cur = conn.cursor()
      row = cur.execute("SELECT next_value FROM sequences WHERE key = ?", (key,)).fetchone()
      current = row["next_value"]
      cur.execute("UPDATE sequences SET next_value = ? WHERE key = ?", (current + 1, key))
      conn.commit()
      conn.close()
      return f"{PREFIXES[key]}{current}"

    def create_document(self, doc_type, reference, status, value, payload):
      number = self.next_number(doc_type)
      created_on = utc_now()
      conn = self.connect()
      conn.execute(
          """
          INSERT INTO documents (type, number, reference, status, value, created_on, payload_json)
          VALUES (?, ?, ?, ?, ?, ?, ?)
          """,
          (doc_type, number, reference, status, decimal_value(value), created_on, json.dumps(payload)),
      )
      conn.commit()
      conn.close()
      return number, created_on

    def create_posting(self, doc_number, debit_account, credit_account, amount, payload):
      fi_number = self.next_number("fi")
      created_on = utc_now()
      conn = self.connect()
      conn.execute(
          """
          INSERT INTO postings (fi_number, doc_number, debit_account, credit_account, amount, created_on, payload_json)
          VALUES (?, ?, ?, ?, ?, ?, ?)
          """,
          (
              fi_number,
              doc_number,
              debit_account,
              credit_account,
              decimal_value(amount),
              created_on,
              json.dumps(payload),
          ),
      )
      conn.commit()
      conn.close()
      return fi_number, created_on

    def latest_document(self, doc_type):
      conn = self.connect()
      row = conn.execute(
          "SELECT * FROM documents WHERE type = ? ORDER BY id DESC LIMIT 1", (doc_type,)
      ).fetchone()
      conn.close()
      if not row:
          return None
      row["payload"] = json.loads(row["payload_json"])
      return row

    def document_by_number(self, number):
      conn = self.connect()
      row = conn.execute("SELECT * FROM documents WHERE number = ?", (number,)).fetchone()
      conn.close()
      if not row:
          return None
      row["payload"] = json.loads(row["payload_json"])
      return row

    def list_documents(self):
      conn = self.connect()
      rows = conn.execute("SELECT * FROM documents ORDER BY id DESC").fetchall()
      conn.close()
      documents = []
      for row in rows:
          documents.append(
              {
                  "type": row["type"],
                  "number": row["number"],
                  "reference": row["reference"],
                  "status": row["status"],
                  "value": row["value"],
                  "createdOn": row["created_on"],
                  "payload": json.loads(row["payload_json"]),
              }
          )
      return documents

    def list_postings(self):
      conn = self.connect()
      rows = conn.execute("SELECT * FROM postings ORDER BY id DESC").fetchall()
      conn.close()
      postings = []
      for row in rows:
          postings.append(
              {
                  "fiDoc": row["fi_number"],
                  "docNumber": row["doc_number"],
                  "debit": row["debit_account"],
                  "credit": row["credit_account"],
                  "amount": row["amount"],
                  "createdOn": row["created_on"],
                  "payload": json.loads(row["payload_json"]),
              }
          )
      return postings


db = P2PDatabase(DB_PATH)


def latest_payload(doc_type):
    row = db.latest_document(doc_type)
    if not row:
        return None
    payload = row["payload"]
    payload["number"] = row["number"]
    payload["reference"] = row["reference"]
    payload["status"] = row["status"]
    payload["createdOn"] = row["created_on"]
    payload["value"] = row["value"]
    return payload


def get_process_data():
    return {step["key"]: latest_payload(step["key"]) for step in TIMELINE}


def build_comparison_rows(quotation):
    if not quotation:
        return []
    return [
        {
            "vendor": quotation["vendor"],
            "value": quotation["netValue"],
            "freight": quotation["freight"],
            "leadTime": quotation["leadTime"],
            "rank": 1,
            "decision": "Selected",
        },
        {
            "vendor": "Metro Alloys Trading",
            "value": quotation["netValue"] + 3500,
            "freight": 1200,
            "leadTime": quotation["leadTime"] + 2,
            "rank": 2,
            "decision": "Higher landed cost",
        },
        {
            "vendor": "NorthAxis Industrial Metals",
            "value": quotation["netValue"] + 1800,
            "freight": 600,
            "leadTime": quotation["leadTime"] + 4,
            "rank": 3,
            "decision": "Longer delivery cycle",
        },
    ]


def build_controls(process_data):
    po = process_data["po"]
    gr = process_data["gr"]
    invoice = process_data["invoice"]
    payment = process_data["payment"]

    control_rows = [
        {
            "title": "PO Quantity Check",
            "description": f"Purchase order quantity posted: {po['quantity']}" if po else "No purchase order available yet.",
            "status": "Available" if po else "Pending",
        },
        {
            "title": "GR Quantity Check",
            "description": f"Goods receipt quantity posted: {gr['quantity']}" if gr else "Goods receipt not posted yet.",
            "status": "Available" if gr else "Pending",
        },
        {
            "title": "Invoice Quantity Check",
            "description": f"Invoice quantity posted: {invoice['quantity']}" if invoice else "Invoice not posted yet.",
            "status": "Available" if invoice else "Pending",
        },
    ]

    alerts = []
    if po and gr and float(gr["quantity"]) != float(po["quantity"]):
        alerts.append(
            {
                "title": "Quantity mismatch between PO and GR",
                "description": f"Ordered {po['quantity']} EA but received {gr['quantity']} EA. Review stores posting or vendor short supply.",
                "level": "warning",
            }
        )
    if po and invoice and float(invoice["grossAmount"]) != float(po["netValue"]):
        alerts.append(
            {
                "title": "Invoice price variance detected",
                "description": f"PO net value is {po['netValue']} but invoice posted for {invoice['grossAmount']}.",
                "level": "danger",
            }
        )
    if invoice and not payment:
        alerts.append(
            {
                "title": "Vendor liability is open",
                "description": "Invoice has been posted but payment has not yet been completed.",
                "level": "warning",
            }
        )
    if not alerts:
        alerts.append(
            {
                "title": "No control exceptions",
                "description": "The current process is aligned with standard procurement controls.",
                "level": "success",
            }
        )

    po_qty = float(po["quantity"]) if po else 0
    gr_qty = float(gr["quantity"]) if gr else 0
    invoice_qty = float(invoice["quantity"]) if invoice else 0
    po_value = float(po["netValue"]) if po else 0
    invoice_value = float(invoice["grossAmount"]) if invoice else 0

    if not po and not gr and not invoice:
        match = {"status": "neutral", "label": "Awaiting transaction data"}
    elif po_qty == gr_qty == invoice_qty and po_value == invoice_value:
        match = {"status": "success", "label": "3-way match successful"}
    elif invoice_qty > gr_qty or invoice_value > po_value:
        match = {"status": "danger", "label": "Variance detected"}
    else:
        match = {"status": "warning", "label": "Partial match"}

    return {
        "controlRows": control_rows,
        "alerts": alerts,
        "match": match,
        "quantities": {
            "po": po_qty,
            "gr": gr_qty,
            "invoice": invoice_qty,
        },
    }


def get_metrics(process_data, documents):
    gr = process_data["gr"]
    invoice = process_data["invoice"]
    payment = process_data["payment"]
    inventory_value = float(gr["value"]) if gr else 0
    vendor_liability = 0
    if invoice:
        vendor_liability = float(invoice["amount"]) + float(invoice["tax"])
    if payment:
        vendor_liability = max(0, vendor_liability - float(payment["amount"]))

    return {
        "docCount": len(documents),
        "inventoryValue": inventory_value,
        "vendorLiability": vendor_liability,
        "paymentStatus": "Cleared" if payment else "Not posted",
        "paid": bool(payment),
    }


def snapshot():
    process_data = get_process_data()
    documents = db.list_documents()
    postings = db.list_postings()
    controls = build_controls(process_data)
    return {
        "company": "BuildRight Construction Pvt. Ltd.",
        "masterData": db.get_master_snapshot(),
        "timeline": TIMELINE,
        "processData": process_data,
        "documents": documents,
        "postings": postings,
        "controls": controls,
        "comparisonRows": build_comparison_rows(process_data["quotation"]),
        "metrics": get_metrics(process_data, documents),
    }


def require_document(doc_type, message):
    doc = latest_payload(doc_type)
    if not doc:
        raise ValueError(message)
    return doc


def create_pr(payload):
    quantity = int(payload["quantity"])
    record = {
        "material": payload["material"],
        "description": payload["description"],
        "quantity": quantity,
        "plant": payload["plant"],
        "purchaseGroup": payload["purchaseGroup"],
        "deliveryDate": payload["deliveryDate"],
    }
    number, created_on = db.create_document("pr", record["material"], "Open", 0, record)
    record["number"] = number
    record["createdOn"] = created_on
    return record


def create_rfq(payload):
    pr = require_document("pr", "Create a purchase requisition before RFQ.")
    record = {
        "vendor": payload["vendor"],
        "deadline": payload["deadline"],
        "quantity": int(payload["quantity"]),
        "plant": payload["plant"],
        "purchaseOrg": payload["purchaseOrg"],
        "purchaseGroup": payload["purchaseGroup"],
        "linkedPr": pr["number"],
    }
    number, created_on = db.create_document("rfq", record["vendor"], "Sent", 0, record)
    record["number"] = number
    record["createdOn"] = created_on
    return record


def create_quotation(payload):
    rfq = require_document("rfq", "Create an RFQ before recording quotation.")
    quantity = int(payload["quantity"])
    unit_price = decimal_value(payload["unitPrice"])
    freight = decimal_value(payload["freight"])
    record = {
        "vendor": payload["vendor"],
        "rfqNumber": rfq["number"],
        "quantity": quantity,
        "unitPrice": unit_price,
        "freight": freight,
        "leadTime": int(payload["leadTime"]),
        "terms": payload["terms"],
        "netValue": decimal_value(quantity * unit_price + freight),
    }
    number, created_on = db.create_document("quotation", record["vendor"], "Received", record["netValue"], record)
    record["number"] = number
    record["createdOn"] = created_on
    return record


def create_po(payload):
    quotation = require_document("quotation", "Record a quotation before creating the purchase order.")
    quantity = int(payload["quantity"])
    unit_price = decimal_value(payload["unitPrice"])
    record = {
        "vendor": payload["vendor"],
        "material": payload["material"],
        "quantity": quantity,
        "unitPrice": unit_price,
        "netValue": decimal_value(quantity * unit_price),
        "purchaseOrg": payload["purchaseOrg"],
        "companyCode": payload["companyCode"],
        "sourceQuotation": quotation["number"],
    }
    number, created_on = db.create_document("po", record["vendor"], "Released", record["netValue"], record)
    record["number"] = number
    record["createdOn"] = created_on
    return record


def create_gr(payload):
    po = require_document("po", "Create a purchase order before goods receipt.")
    po_number = payload.get("poNumber") or po["number"]
    if po_number != po["number"]:
        po = latest_payload("po") if po_number == latest_payload("po")["number"] else None
    target_po = db.document_by_number(po_number)
    if not target_po or target_po["type"] != "po":
        raise ValueError("Referenced purchase order was not found.")

    po_payload = target_po["payload"]
    quantity = int(payload["quantity"])
    value = decimal_value(quantity * float(po_payload["unitPrice"]))
    record = {
        "poNumber": target_po["number"],
        "quantity": quantity,
        "storageLocation": payload["storageLocation"],
        "movementType": payload["movementType"],
        "postingDate": payload["postingDate"],
        "batch": payload["batch"],
        "value": value,
    }
    number, created_on = db.create_document("gr", record["poNumber"], "Posted", value, record)
    fi_number, _ = db.create_posting(
        number,
        "Inventory Raw Materials",
        "GR/IR Clearing",
        value,
        {"transaction": "MIGO", "postingDate": payload["postingDate"]},
    )
    record["number"] = number
    record["fiNumber"] = fi_number
    record["createdOn"] = created_on
    return record


def create_invoice(payload):
    po = require_document("po", "Create a purchase order before invoice verification.")
    gr = require_document("gr", "Post a goods receipt before invoice verification.")
    po_number = payload.get("poNumber") or po["number"]
    po_doc = db.document_by_number(po_number)
    if not po_doc or po_doc["type"] != "po":
        raise ValueError("Referenced purchase order was not found.")

    quantity = int(payload["quantity"])
    amount = decimal_value(payload["amount"])
    tax = decimal_value(payload["tax"])
    po_value = float(po_doc["payload"]["netValue"])
    gr_qty = float(gr["quantity"])
    status = "Posted"
    status_note = "Matched to PO"
    if amount > po_value or quantity > gr_qty:
        status = "Blocked for payment"
        status_note = "Variance exceeds PO or GR values"

    record = {
        "poNumber": po_doc["number"],
        "reference": payload["reference"],
        "quantity": quantity,
        "amount": amount,
        "tax": tax,
        "grossAmount": amount,
        "postingDate": payload["postingDate"],
        "statusNote": status_note,
    }
    number, created_on = db.create_document("invoice", record["reference"], status, amount, record)
    fi_number, _ = db.create_posting(
        number,
        "GR/IR Clearing",
        "Vendor Reconciliation Account",
        amount,
        {"transaction": "MIRO", "postingDate": payload["postingDate"]},
    )
    record["number"] = number
    record["createdOn"] = created_on
    record["fiNumber"] = fi_number
    return record


def create_payment(payload):
    invoice = require_document("invoice", "Post an invoice before payment.")
    if invoice["status"] == "Blocked for payment":
        raise ValueError("Invoice is blocked for payment due to variance. Resolve the discrepancy before payment.")

    amount = decimal_value(payload["amount"])
    open_amount = decimal_value(float(invoice["amount"]) + float(invoice["tax"]))
    if amount > open_amount:
        raise ValueError("Payment amount exceeds current vendor liability.")

    record = {
        "method": payload["method"],
        "bankAccount": payload["bankAccount"],
        "amount": amount,
        "postingDate": payload["postingDate"],
        "invoiceNumber": invoice["number"],
    }
    number, created_on = db.create_document("payment", record["bankAccount"], "Cleared", amount, record)
    fi_number, _ = db.create_posting(
        number,
        "Vendor Reconciliation Account",
        "Bank Account",
        amount,
        {"transaction": "F-53", "postingDate": payload["postingDate"]},
    )
    record["number"] = number
    record["createdOn"] = created_on
    record["fiNumber"] = fi_number
    return record


TRANSACTION_HANDLERS = {
    "pr": create_pr,
    "rfq": create_rfq,
    "quotation": create_quotation,
    "po": create_po,
    "gr": create_gr,
    "invoice": create_invoice,
    "payment": create_payment,
}


def seed_demo():
    db.reset()
    create_pr(
        {
            "material": "STL001",
            "description": "Structural Steel Rods",
            "quantity": 100,
            "plant": "BR01",
            "purchaseGroup": "BR1",
            "deliveryDate": "2026-04-20",
        }
    )
    create_rfq(
        {
            "vendor": "SteelCo Supplies Ltd.",
            "deadline": "2026-04-21",
            "quantity": 100,
            "plant": "BR01",
            "purchaseOrg": "BR10",
            "purchaseGroup": "BR1",
        }
    )
    create_quotation(
        {
            "vendor": "SteelCo Supplies Ltd.",
            "quantity": 100,
            "unitPrice": 500,
            "freight": 0,
            "leadTime": 3,
            "terms": "30 Days Net",
        }
    )
    create_po(
        {
            "vendor": "SteelCo Supplies Ltd.",
            "material": "STL001",
            "quantity": 100,
            "unitPrice": 500,
            "purchaseOrg": "BR10",
            "companyCode": "BR01",
        }
    )
    create_gr(
        {
            "quantity": 100,
            "storageLocation": "0001",
            "movementType": "101",
            "postingDate": "2026-04-21",
            "batch": "SITE-DELHI-01",
        }
    )
    create_invoice(
        {
            "reference": "SC-INV-2045",
            "quantity": 100,
            "amount": 50000,
            "tax": 9000,
            "postingDate": "2026-04-22",
        }
    )
    create_payment(
        {
            "method": "Manual Outgoing Payment",
            "bankAccount": "HDFC-BR01-OPERATIONS",
            "amount": 59000,
            "postingDate": "2026-04-23",
        }
    )


class AppHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE_DIR), **kwargs)

    def _json_response(self, payload, status=HTTPStatus.OK):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        content_length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(content_length) if content_length else b"{}"
        return json.loads(raw.decode("utf-8"))

    def _handle_api_get(self, path):
        if path == "/api/state":
            self._json_response(snapshot())
            return True
        if path == "/api/export":
            self._json_response({"exportedAt": utc_now(), "snapshot": snapshot()})
            return True
        return False

    def _handle_api_post(self, path):
        if path == "/api/reset":
            db.reset()
            self._json_response(snapshot())
            return True
        if path == "/api/seed":
            seed_demo()
            self._json_response(snapshot())
            return True
        if path.startswith("/api/transactions/"):
            txn_type = path.rsplit("/", 1)[-1]
            handler = TRANSACTION_HANDLERS.get(txn_type)
            if not handler:
                self._json_response({"error": "Transaction type not found."}, HTTPStatus.NOT_FOUND)
                return True

            try:
                payload = self._read_json()
                handler(payload)
                self._json_response(snapshot(), HTTPStatus.CREATED)
            except KeyError as error:
                self._json_response({"error": f"Missing required field: {error.args[0]}"}, HTTPStatus.BAD_REQUEST)
            except ValueError as error:
                self._json_response({"error": str(error)}, HTTPStatus.CONFLICT)
            return True
        return False

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/"):
            if not self._handle_api_get(parsed.path):
                self._json_response({"error": "API endpoint not found."}, HTTPStatus.NOT_FOUND)
            return
        if parsed.path == "/":
            self.path = "/index.html"
        super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/"):
            if not self._handle_api_post(parsed.path):
                self._json_response({"error": "API endpoint not found."}, HTTPStatus.NOT_FOUND)
            return
        self._json_response({"error": "Unsupported route."}, HTTPStatus.NOT_FOUND)


def run(server_class=ThreadingHTTPServer, handler_class=AppHandler, port=8000):
    server = server_class(("127.0.0.1", port), handler_class)
    print(f"BuildRight P2P server running on http://127.0.0.1:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
    finally:
        server.server_close()


if __name__ == "__main__":
    run()
