# SAP Execution Guide for P2P Project

## Purpose

This guide helps you execute the entire P2P cycle in SAP step by step using the BuildRight Construction Pvt. Ltd. scenario. It is written in a practical format so you can follow it directly while working in your SAP system and capture screenshots.

## 1. Prerequisite Master Data

Before starting transactions, ensure the following master data exists in SAP:

- company code `BR01`
- plant `BR01`
- purchasing organization `BR10`
- purchasing group `BR1`
- vendor master for `SteelCo Supplies Ltd.`
- material master for `STL001 - Structural Steel Rods`
- valuation class and accounting views maintained for the material
- vendor-company code and vendor-purchasing organization views created

Useful display transactions:

- vendor display: `XK03`
- material display: `MM03`

## 2. Transaction Data To Use

Use this sample transactional data consistently across all screenshots:

| Field | Suggested Value |
| --- | --- |
| Material | `STL001` |
| Material Description | `Structural Steel Rods` |
| Quantity | `100` |
| Unit | `EA` or your configured UoM |
| Plant | `BR01` |
| Storage Location | `0001` if available |
| Purchase Org | `BR10` |
| Purchase Group | `BR1` |
| Vendor | `SteelCo Supplies Ltd.` |
| PO Price | `INR 50,000` total or equivalent unit price |
| Delivery Date | Choose a realistic working date |
| Invoice Amount | Match PO for normal scenario |
| Variance Scenario | `INR 52,000` for blocked/variance explanation |

## 3. Purchase Requisition (`ME51N`)

### Action

Create a Purchase Requisition for structural steel rods.

### Entry Steps

1. Open transaction `ME51N`.
2. Select standard Purchase Requisition document type.
3. Enter material `STL001`.
4. Enter quantity `100`.
5. Enter plant `BR01`.
6. Enter purchasing group `BR1`.
7. Enter delivery date.
8. Save the document.

### Result

- PR document number is generated.
- Internal purchase demand is created.

### Screenshot Needed

- Full PR creation screen showing material, quantity, plant, and generated PR number.

## 4. Request for Quotation (`ME41`)

### Action

Create an RFQ based on procurement need.

### Entry Steps

1. Open transaction `ME41`.
2. Choose RFQ document type.
3. Enter purchasing organization `BR10`.
4. Enter purchasing group `BR1`.
5. Maintain quotation deadline.
6. Enter item data for `STL001`, quantity `100`, plant `BR01`.
7. Save the RFQ.

### Result

- RFQ number is created.
- Vendor communication process can begin.

### Screenshot Needed

- RFQ header and item overview with deadline and material details.

## 5. Vendor Quotation (`ME47`)

### Action

Maintain vendor quotation received from SteelCo Supplies Ltd.

### Entry Steps

1. Open transaction `ME47`.
2. Enter the RFQ number and vendor.
3. Maintain quoted price and delivery terms.
4. Save the quotation.

### Result

- Vendor quotation becomes available for comparison and selection.

### Screenshot Needed

- Quotation screen showing vendor and price details.

## 6. Quotation Comparison (`ME49`)

### Action

Compare quotations and select the best vendor.

### Entry Steps

1. Open transaction `ME49`.
2. Enter RFQ number or selection criteria.
3. Execute comparison.
4. Review vendor price and ranking.

### Result

- Best vendor can be selected for PO creation.

### Screenshot Needed

- Comparison result screen showing quotation values.

## 7. Purchase Order (`ME21N`)

### Action

Create a Purchase Order for SteelCo Supplies Ltd.

### Entry Steps

1. Open transaction `ME21N`.
2. Select standard PO document type.
3. Enter vendor.
4. Enter purchase organization `BR10`.
5. Enter purchase group `BR1`.
6. Enter company code `BR01`.
7. Enter material `STL001`.
8. Enter plant `BR01`.
9. Enter quantity `100`.
10. Enter negotiated price.
11. Save the PO.

### Result

- PO number is generated.
- Purchase order history begins.

### Screenshot Needed

- PO screen showing vendor, material, quantity, plant, and price.

## 8. Goods Receipt (`MIGO`)

### Action

Post goods receipt against the purchase order when materials are delivered.

### Entry Steps

1. Open transaction `MIGO`.
2. Select `Goods Receipt`.
3. Reference the PO number.
4. Verify material, quantity, and plant.
5. Enter storage location if applicable.
6. Check item OK.
7. Post the document.

### Result

- material document is generated
- stock is updated
- accounting document is generated

### Screenshot Needed

- GR posting screen before posting
- confirmation screen with generated material document

### FI Impact

- Debit Inventory
- Credit GR/IR

## 9. Invoice Verification (`MIRO`)

### Action

Post the vendor invoice against the PO and GR.

### Entry Steps

1. Open transaction `MIRO`.
2. Enter invoice date and posting date.
3. Enter vendor invoice reference number.
4. Enter PO number.
5. Verify amount, tax, quantity, and item details.
6. Simulate if required.
7. Post the invoice.

### Result

- invoice document is created
- vendor liability is posted
- GR/IR is cleared

### Screenshot Needed

- MIRO entry screen before posting
- posted invoice confirmation

### FI Impact

- Debit GR/IR
- Credit Vendor

## 10. Vendor Payment (`F-53` or `F110`)

### Manual Payment with `F-53`

1. Open transaction `F-53`.
2. Enter bank account, company code, and payment amount.
3. Select open vendor item.
4. Post payment.

### Automatic Payment with `F110`

1. Configure payment parameters.
2. Enter run date and identification.
3. Execute proposal.
4. Review proposal.
5. Execute payment run if allowed in your system.

### Result

- vendor open item is cleared
- payment accounting entry is posted

### FI Impact

- Debit Vendor
- Credit Bank

### Screenshot Needed

- payment entry or payment proposal screen

## 11. Price Variance Scenario for Viva

Use this scenario to demonstrate advanced understanding:

- Purchase Order amount: `INR 50,000`
- Vendor invoice amount: `INR 52,000`

Explain:

- SAP compares invoice amount with PO conditions
- tolerance limits determine whether posting is blocked or allowed
- invoice can be marked for payment block
- finance or purchasing reviews the difference before payment

## 12. Important Viva Points

Memorize these short answers:

- P2P stands for Procure-to-Pay.
- It starts with requirement identification and ends with vendor payment.
- The main control is the 3-way match between PO, GR, and Invoice.
- `ME21N` creates the PO, `MIGO` posts GR, and `MIRO` posts invoice.
- GR updates stock and posts accounting entry.
- MIRO creates vendor liability.
- Payment is completed in FI using `F-53` or `F110`.

## 13. Final Output Expectation

By the end of execution, you should have:

- one PR number
- one RFQ number
- one or more quotation records
- one PO number
- one material document
- one invoice document
- one payment document or payment proposal

These document numbers should be inserted into the final PDF to make the project look authentic and complete.
