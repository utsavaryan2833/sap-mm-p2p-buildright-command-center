# P2P Process Implementation in SAP MM for BuildRight Construction Pvt. Ltd.

## 1. Introduction

Procure-to-Pay (P2P) is one of the most important business cycles in SAP Materials Management (MM). It covers the complete purchasing process from identifying a requirement for material to making payment to the vendor. In real organizations, this process helps control procurement cost, reduce manual errors, maintain audit trails, and ensure that only valid and received goods are paid for.

This project demonstrates the end-to-end P2P cycle in SAP MM for **BuildRight Construction Pvt. Ltd.**, a fictitious construction materials company. The business procures structural steel rods from approved suppliers for project execution. The implementation includes Purchase Requisition, Request for Quotation, quotation maintenance, Purchase Order creation, Goods Receipt, Invoice Verification, and Vendor Payment.

## 2. Company Background

BuildRight Construction Pvt. Ltd. is a construction materials company with centralized purchasing operations. The company procures raw materials in bulk for ongoing projects and requires a controlled system to manage purchase demand, vendor communication, stock receipt, invoice validation, and payment settlement.

### Organizational Data

- Company Code: `BR01`
- Plant: `BR01` (Delhi)
- Purchase Organization: `BR10`
- Purchase Group: `BR1`
- Vendor: `SteelCo Supplies Ltd.`
- Material: `Structural Steel Rods`
- Material Number: `STL001`

## 3. Problem Statement

Before SAP implementation, procurement activities were handled manually or through disconnected records. This created several business problems:

- duplicate material requests from different teams
- lack of price comparison between vendors
- risk of over-ordering materials
- delayed goods tracking at plant level
- mismatch between received goods and vendor invoices
- duplicate or incorrect payments
- no proper audit trail for approvals and postings

These issues impacted cost control, inventory reliability, and financial transparency. A structured P2P cycle in SAP MM resolves these issues by integrating purchasing, inventory management, and financial accounting.

## 4. Project Objective

The objective of this project is to implement the complete procurement cycle in SAP MM and demonstrate how SAP controls each stage of purchasing through transaction-based processing and accounting integration.

The project also aims to showcase:

- automation of the purchasing lifecycle
- standardization of procurement documents
- traceability from requisition to payment
- 3-way matching for invoice control
- integration between MM and FI modules

## 5. Scope of Implementation

The project covers the following SAP transactions:

| Step | Process | Transaction Code |
| --- | --- | --- |
| 1 | Purchase Requisition | `ME51N` |
| 2 | Request for Quotation | `ME41` |
| 3 | Vendor Quotation | `ME47` |
| 4 | Quotation Comparison | `ME49` |
| 5 | Purchase Order | `ME21N` |
| 6 | Goods Receipt | `MIGO` |
| 7 | Invoice Verification | `MIRO` |
| 8 | Vendor Payment | `F-53` / `F110` |

## 6. End-to-End P2P Process

### 6.1 Purchase Requisition (`ME51N`)

The procurement cycle starts when the purchasing team or requesting department identifies the need for structural steel rods. A Purchase Requisition is created in SAP to formally record the internal requirement.

Key data maintained:

- material number: `STL001`
- material description: `Structural Steel Rods`
- quantity required
- delivery date
- plant: `BR01`
- purchasing group: `BR1`

Business purpose:

- records demand in a controlled way
- creates a reference for downstream procurement
- enables approval and audit visibility

### 6.2 Request for Quotation (`ME41`)

After the requisition is created, the buyer issues a Request for Quotation to eligible vendors. This step helps the company obtain competitive pricing and purchasing terms.

Key data maintained:

- RFQ document number
- vendor details
- material and quantity
- quotation deadline
- delivery conditions

Business purpose:

- invites suppliers to submit commercial offers
- supports vendor selection based on price and terms
- improves procurement transparency

### 6.3 Vendor Quotation and Comparison (`ME47` and `ME49`)

After receiving quotations from vendors, the buyer enters quotation details into SAP using `ME47`. If multiple quotations are collected, SAP can compare them using `ME49`.

Key comparison points:

- unit price
- delivery date
- payment terms
- freight or additional conditions

Business purpose:

- helps select the most suitable supplier
- supports cost-effective purchasing
- provides documented justification for vendor selection

### 6.4 Purchase Order Creation (`ME21N`)

Once the best quotation is identified, a Purchase Order is created for the selected vendor, SteelCo Supplies Ltd. The PO is the official external purchasing document sent to the vendor.

Key data maintained:

- vendor code and name
- purchasing organization: `BR10`
- purchasing group: `BR1`
- company code: `BR01`
- plant: `BR01`
- material: `STL001`
- order quantity
- order price
- delivery date

Business purpose:

- legally and operationally confirms the procurement
- serves as the base document for GR and invoice verification
- controls procurement terms, quantity, and pricing

### 6.5 Goods Receipt (`MIGO`)

When the vendor delivers structural steel rods to the plant, the stores or warehouse team records the Goods Receipt in SAP using `MIGO`. This step updates inventory and generates accounting entries.

Effects of GR:

- stock quantity increases in inventory
- material document is generated
- accounting document is generated
- purchase order history is updated

Business purpose:

- confirms that goods were physically received
- updates stock records in real time
- provides the second control point in the P2P cycle

### 6.6 Invoice Verification (`MIRO`)

After goods are received, the vendor invoice is posted in SAP using `MIRO`. The system verifies the invoice against the PO and GR details.

Key verification checks:

- invoice quantity versus PO quantity
- invoice quantity versus GR quantity
- invoice amount versus PO price
- tax and posting details

Business purpose:

- prevents payment of unverified invoices
- ensures financial accuracy
- creates liability to the vendor in FI

### 6.7 Payment to Vendor (`F-53` / `F110`)

Once the invoice is posted and approved, payment is made to the vendor through finance using either manual outgoing payment (`F-53`) or automatic payment program (`F110`).

Business purpose:

- clears vendor open items
- records payment in finance
- completes the procure-to-pay cycle

## 7. 3-Way Match Concept

The 3-way match is the most important control in the P2P process. SAP compares three critical business documents before releasing payment:

1. Purchase Order
2. Goods Receipt
3. Invoice

For successful payment processing, the following should align:

- PO quantity = ordered quantity
- GR quantity = physically received quantity
- Invoice quantity = billed quantity

If the invoice exceeds the ordered or received quantity, SAP can block the invoice for payment depending on tolerance settings. This control helps eliminate overbilling, duplicate invoicing, and payment errors.

## 8. MM-FI Integration

One of the strongest features of SAP is the integration between Materials Management and Financial Accounting.

### Accounting Impact at Goods Receipt

At the time of goods receipt, inventory is recognized and a GR/IR clearing entry is posted.

Typical accounting entry:

- Debit: Inventory Account
- Credit: GR/IR Clearing Account

### Accounting Impact at Invoice Verification

At the time of invoice posting, the vendor liability is recognized and GR/IR is cleared.

Typical accounting entry:

- Debit: GR/IR Clearing Account
- Credit: Vendor Account

### Accounting Impact at Payment

When payment is made to the vendor:

- Debit: Vendor Account
- Credit: Bank Account

This proves seamless integration between MM transactions and FI postings.

## 9. Price Variance Scenario

An advanced scenario in P2P occurs when the vendor invoice price differs from the price in the purchase order.

Example:

- PO price: `INR 50,000` for a lot of steel rods
- Invoice price: `INR 52,000`

Possible SAP outcome:

- SAP detects the variance during `MIRO`
- based on tolerance configuration, the invoice may be blocked for payment
- buyer or finance team reviews the discrepancy
- corrected invoice or approval is processed before payment

This scenario shows that SAP is not only a transaction system but also a control system.

## 10. Benefits Achieved

After implementing the P2P cycle in SAP MM, BuildRight Construction Pvt. Ltd. achieves the following benefits:

- controlled and trackable procurement process
- reduced duplication of orders and payments
- improved vendor selection through quotation comparison
- accurate inventory updates at the time of receipt
- stronger invoice validation through 3-way match
- better coordination between procurement and finance
- complete audit trail for every purchasing document

## 11. Future Improvements

The current project can be extended further through additional SAP MM features:

- Vendor Evaluation using `ME61`
- Source List maintenance
- Quota arrangement for multi-vendor sourcing
- Automatic payment run using `F110`
- Release strategy for requisitions and purchase orders
- integration with SAP SD or Project Systems for project-driven procurement

## 12. Conclusion

The P2P process is a core business function in SAP MM and one of the most practical implementations for demonstrating real-world procurement control. Through this project, the complete lifecycle from internal requirement to vendor payment was executed in a structured and auditable manner. The process not only improved procurement efficiency but also ensured strong financial control through MM-FI integration and 3-way matching.

This implementation clearly demonstrates how SAP MM supports modern enterprise purchasing operations and why the P2P cycle remains one of the most valuable and evaluator-friendly topics in SAP projects.

## 13. Screenshots To Insert In Final PDF

Add one screenshot each for the following:

1. Purchase Requisition creation screen in `ME51N`
2. RFQ creation screen in `ME41`
3. Vendor quotation entry in `ME47`
4. Quotation comparison in `ME49`
5. Purchase Order creation in `ME21N`
6. Goods Receipt posting in `MIGO`
7. Material document and accounting document after GR
8. Invoice verification in `MIRO`
9. Accounting document after invoice posting
10. Vendor payment screen in `F-53` or payment proposal in `F110`
