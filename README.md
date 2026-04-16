# BuildRight P2P Command Center

This repository now includes a working full-stack SAP MM style project, designed as an industry-grade Procure-to-Pay simulator for **BuildRight Construction Pvt. Ltd.** It combines a polished frontend, a Python backend, SQLite persistence, and supporting academic documentation so you can demo the process live and still submit a strong report.

## What Is Included

- a full interactive P2P simulator in [index.html](/c:/Users/KIIT0001/Desktop/SAP%20Project%20P2P/index.html)
- a backend server in [app.py](/c:/Users/KIIT0001/Desktop/SAP%20Project%20P2P/app.py)
- persistent storage in `buildright_p2p.db` after first run
- enterprise styling in [styles/app.css](/c:/Users/KIIT0001/Desktop/SAP%20Project%20P2P/styles/app.css)
- transaction logic and document generation in [scripts/app.js](/c:/Users/KIIT0001/Desktop/SAP%20Project%20P2P/scripts/app.js)
- project report and supporting documentation in [docs](/c:/Users/KIIT0001/Desktop/SAP%20Project%20P2P/docs)

## Functional Scope

The simulator covers the full SAP MM P2P lifecycle:

1. Purchase Requisition (`ME51N`)
2. Request for Quotation (`ME41`)
3. Vendor Quotation (`ME47`)
4. Purchase Order (`ME21N`)
5. Goods Receipt (`MIGO`)
6. Invoice Verification (`MIRO`)
7. Vendor Payment (`F-53`)

It also includes:

- BuildRight master data setup
- generated procurement documents
- FI postings for GR, invoice, and payment
- 3-way match controls
- variance alerts for invoice mismatch
- a guided demo data loader
- snapshot export for project evidence
- backend-enforced transaction dependencies
- persistent transaction history in SQLite
- payment blocking when invoice variance exists

## How To Run

1. Start the backend server:

```powershell
python app.py
```

2. Open `http://127.0.0.1:8000` in your browser.

For the best demo flow:

1. Open the app.
2. Click `Load Guided Demo` to populate a complete world-class sample cycle.
3. Walk through `Overview`, `Transactions`, `Documents`, `FI Postings`, and `Controls`.
4. Use `Export Project Snapshot` to download the current transaction state as JSON.

## Project Positioning

This is a **SAP-inspired educational simulator**, not an official SAP product. It is designed to feel like an enterprise purchasing cockpit and to demonstrate real P2P concepts with a polished UI, coherent document flow, persistent storage, and backend business validation.

## Documentation

- [docs/Project-Report.md](/c:/Users/KIIT0001/Desktop/SAP%20Project%20P2P/docs/Project-Report.md)
- [docs/SAP-Execution-Guide.md](/c:/Users/KIIT0001/Desktop/SAP%20Project%20P2P/docs/SAP-Execution-Guide.md)
- [docs/Screenshot-Tracker.md](/c:/Users/KIIT0001/Desktop/SAP%20Project%20P2P/docs/Screenshot-Tracker.md)
- [docs/Master-Data-and-Postings.md](/c:/Users/KIIT0001/Desktop/SAP%20Project%20P2P/docs/Master-Data-and-Postings.md)
- [docs/Submission-Checklist.md](/c:/Users/KIIT0001/Desktop/SAP%20Project%20P2P/docs/Submission-Checklist.md)
