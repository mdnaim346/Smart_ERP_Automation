# Smart ERP Automation

Smart ERP Automation is an Odoo 17 module for running safe scheduled ERP automation rules. It currently supports automated sales invoice creation and automated RFQ creation for low-stock products.

## Features

- Configurable automation rules
- Manual `Run Now` action
- Scheduled automation through cron
- Sales invoice creation from confirmed sale orders
- Optional automatic invoice posting
- Product minimum quantity field
- RFQ creation for low-stock purchasable products
- Purchase order lines created automatically
- Duplicate draft RFQ prevention
- Vendor missing checks
- Execution logs for every rule run
- Rule statistics: execution count, success count, failure count, last run date
- Security groups for automation users and managers

## Dependencies

This module depends on:

```text
sale
stock
purchase
mail
```

## Installation

Place the module in your Odoo custom addons path:

```text
F:\odoo17\custom_addons\Smart_ERP_Automation
```

Upgrade the module:

```bash
python .\odoo-bin -c .\odoo.conf -d ERP -u Smart_ERP_Automation --stop-after-init --no-http
```

Start Odoo:

```bash
python .\odoo-bin -c .\odoo.conf -d ERP
```

Open:

```text
http://localhost:8069
```

## Security

The module creates two groups:

```text
Automation User
Automation Manager
```

Automation users can read rules and logs.

Automation managers can create, edit, delete, and manually run automation rules.

## Menus

After installation, open:

```text
Automation > Rules
Automation > Logs
```

## Creating an Invoice Automation Rule

Go to:

```text
Automation > Rules > New
```

Example:

```text
Name: Auto Create Sales Invoices
Active: True
Action Type: Create Invoice
Trigger: Scheduled
Auto Post Invoice: True
Max Records Per Run: 10
Company: Your company
Responsible: Admin
```

Save the rule and click:

```text
Run Now
```

The rule searches confirmed sale orders where the invoice status is `To Invoice`, creates invoices, and posts them if `Auto Post Invoice` is enabled.

## Creating a Purchase Automation Rule

Go to:

```text
Automation > Rules > New
```

Example:

```text
Name: Auto Reorder Low Stock Products
Active: True
Action Type: Create Purchase Order
Trigger: Scheduled
Reorder Quantity: 5
Max Records Per Run: 10
Company: Your company
Responsible: Admin
```

Save the rule and click:

```text
Run Now
```

The rule checks purchasable products where `On Hand Quantity` is lower than `Minimum Quantity`. If the product has a vendor and no existing draft RFQ for that product/vendor, it creates a new RFQ with a purchase order line.

## Scheduled Action

The active cron is:

```text
Run Automation Rules
```

It runs:

```python
model.run_automation()
```

The old direct invoice cron is kept inactive as:

```text
Auto Invoice Deprecated
```

## Test Process

### 1. Module Upgrade Test

Run:

```bash
python .\odoo-bin -c .\odoo.conf -d ERP -u Smart_ERP_Automation --stop-after-init --no-http
```

Expected result:

```text
Module loads without errors.
Security, cron, views, and models load successfully.
```

### 2. Menu Test

Open:

```text
Automation
```

Expected result:

```text
Rules and Logs menus are visible.
```

### 3. Invoice Automation Test

Create and confirm a sale order with an invoiceable product.

Expected sale order status:

```text
State: Sales Order
Invoice Status: To Invoice
```

Run the invoice automation rule.

Expected result:

```text
Invoice is created.
Invoice is posted if Auto Post Invoice is enabled.
Automation log is created.
Rule statistics are updated.
```

Run the same rule again.

Expected result:

```text
No duplicate invoice is created.
Log says no records were found or records were skipped.
```

### 4. Purchase Automation Test

Create or open a storable purchasable product.

Set:

```text
Minimum Quantity: greater than current on hand quantity
Vendor: configured
```

Run the purchase automation rule.

Expected result:

```text
Draft RFQ is created.
RFQ contains the product line.
Automation log is created.
```

Run the same rule again.

Expected result:

```text
No duplicate RFQ is created while the first RFQ is still draft or sent.
Log says draft RFQ already exists.
```

### 5. No Vendor Test

Create or open a purchasable product below minimum quantity with no vendor.

Run purchase automation.

Expected result:

```text
No crash.
No RFQ is created.
Log says no vendor is configured.
```

### 6. Max Records Test

Set:

```text
Max Records Per Run: 1
```

Run the rule.

Expected result:

```text
Only one matching record is processed in that run.
```

### 7. Cron Test

Enable developer mode and open:

```text
Settings > Technical > Automation > Scheduled Actions
```

Search:

```text
Run Automation Rules
```

Click:

```text
Run Manually
```

Expected result:

```text
All active rules run.
Logs are created.
```

Also confirm:

```text
Auto Invoice Deprecated
```

Expected result:

```text
The cron is inactive.
```

### 8. Security Test

Create a user with:

```text
Automation User
```

Expected result:

```text
The user can read rules and logs but cannot create, edit, or delete rules.
```

Give the user:

```text
Automation Manager
```

Expected result:

```text
The user can manage automation rules.
```

## Success Checklist

The module is working correctly when:

```text
Module upgrades without error.
Automation menu appears.
Rules can be created.
Invoice rule creates invoices.
Invoice rule avoids duplicates.
Purchase rule creates RFQs with product lines.
Purchase rule skips products without vendors.
Purchase rule prevents duplicate draft RFQs.
Logs are created for every run.
Cron runs active rules.
Security groups work correctly.
```

## Notes

Use a test database before running automation on real business data. Invoice posting and RFQ creation are real ERP actions.
