# Master Data and Accounting Postings Reference

## 1. Master Data Sheet

### Company Structure

| Element | Value | Description |
| --- | --- | --- |
| Company Code | `BR01` | BuildRight Construction Pvt. Ltd. |
| Plant | `BR01` | Delhi Plant |
| Purchasing Organization | `BR10` | Central Purchasing |
| Purchasing Group | `BR1` | Raw Materials Team |

### Business Partner and Material

| Element | Value | Description |
| --- | --- | --- |
| Vendor Name | `SteelCo Supplies Ltd.` | Approved steel supplier |
| Material Number | `STL001` | Structural Steel Rods |
| Material Type | `ROH` or configured type | Raw material |
| Base Unit of Measure | `EA`, `KG`, or configured unit | According to system setup |
| Valuation Class | System dependent | Used for account determination |

## 2. Suggested Business Values

| Field | Sample Value |
| --- | --- |
| Quantity | `100` |
| Price | `INR 50,000` |
| Price Variance Scenario | `INR 52,000` |
| Currency | `INR` |
| Storage Location | `0001` |

## 3. Core P2P Documents

| Process | SAP Document |
| --- | --- |
| Internal requirement | Purchase Requisition |
| Vendor enquiry | RFQ |
| Vendor commercial response | Quotation |
| Procurement commitment | Purchase Order |
| Stock update | Material Document |
| Accounting update | FI Document |
| Vendor liability | Invoice Document |
| Settlement | Payment Document |

## 4. Typical Accounting Entries

### At Goods Receipt

Business event:
Material is received from vendor against PO.

Typical posting:

- Debit Inventory Account
- Credit GR/IR Clearing Account

Illustrative format:

| Debit | Credit |
| --- | --- |
| Inventory A/c | GR/IR A/c |

### At Invoice Verification

Business event:
Vendor invoice is posted against the PO and GR.

Typical posting:

- Debit GR/IR Clearing Account
- Credit Vendor Account

Illustrative format:

| Debit | Credit |
| --- | --- |
| GR/IR A/c | Vendor A/c |

### At Vendor Payment

Business event:
Vendor invoice is paid and open item is cleared.

Typical posting:

- Debit Vendor Account
- Credit Bank Account

Illustrative format:

| Debit | Credit |
| --- | --- |
| Vendor A/c | Bank A/c |

## 5. 3-Way Match Control Table

| Document | Control Question |
| --- | --- |
| Purchase Order | What was ordered? |
| Goods Receipt | What was actually received? |
| Invoice | What is the vendor billing for? |

### Why It Matters

- prevents payment without receipt of goods
- avoids excess billing
- improves auditability
- supports procurement governance

## 6. Common Interview or Viva Questions

### What is GR/IR?

GR/IR stands for Goods Receipt / Invoice Receipt clearing account. It acts as a temporary balance sheet account between goods receipt and invoice verification.

### Why is P2P important?

Because it integrates purchasing, inventory, and finance into one controlled process.

### What happens if invoice quantity is more than GR quantity?

Depending on SAP tolerance settings, the invoice may be blocked for payment or flagged for review.

### Which transaction creates a Purchase Order?

`ME21N`

### Which transaction is used for invoice verification?

`MIRO`
