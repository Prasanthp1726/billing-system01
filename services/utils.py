def calculate_totals(items, tax_rate=0.0, discount_rate=0.0):
    subtotal = sum(i["qty"] * i["unit_price"] for i in items)
    tax_total = round(subtotal * (tax_rate / 100.0), 2)
    discount_total = round(subtotal * (discount_rate / 100.0), 2)
    grand_total = round(subtotal + tax_total - discount_total, 2)
    return {
        "subtotal": round(subtotal, 2),
        "tax_total": tax_total,
        "discount_total": discount_total,
        "grand_total": grand_total
    }
