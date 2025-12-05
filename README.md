# Billing System
# Milestone 5 reports module — confirmed working

## Project name
billing-system01

## Milestone 1: Schema and setup details
- customers(id, name, email, phone)
- products(id, name, price, stock_qty)
- invoices(id, customer_id, date, total)
- invoice_items(id, invoice_id, product_id, qty, unit_price, line_total)
- payments(id, invoice_id, amount, mode, paid_at)
