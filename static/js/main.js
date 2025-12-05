// const API_BASE = "http://localhost:8000/api";
const API_BASE = "/api";

function loadHTML(url, containerId, callback) {
    fetch(url)
        .then(res => res.text())
        .then(html => {
            const el = document.getElementById(containerId);
            if (el) el.innerHTML = html;
            if (callback) callback();
        });
}

// dashboard
async function loadDashboardSummary() {
    const [customers, products, invoices, payments, sales] = await Promise.all([
        fetch(`${API_BASE}/customers`).then(r => r.json()),
        fetch(`${API_BASE}/products`).then(r => r.json()),
        fetch(`${API_BASE}/invoices`).then(r => r.json()),
        fetch(`${API_BASE}/payments`).then(r => r.json()),
        fetch(`${API_BASE}/reports/sales-summary`).then(r => r.json()),
    ]);

    document.getElementById("dashCustomers").textContent = customers.length;
    document.getElementById("dashProducts").textContent = products.length;
    document.getElementById("dashInvoices").textContent = invoices.length;
    document.getElementById("dashPayments").textContent = payments.reduce((sum, p) => sum + p.amount, 0);
    document.getElementById("dashSales").textContent = `₹${sales.total_sales.toFixed(2)}`;
}

// Customers
function attachCustomerForm() {
    const form = document.getElementById("customerForm");
    if (!form) return;
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const payload = Object.fromEntries(new FormData(form).entries());

        const res = await fetch("/api/customers", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        if (!res.ok) {
            const txt = await res.text(); // ✅ shows backend error
            alert(`Error adding customer: ${txt}`);
            return;
        }

        const data = await res.json();
        form.reset();
        loadCustomers();
    });
    async function loadCustomers() {
        const res = await fetch("/api/customers");
        const list = await res.json();
        const tbody = document.querySelector("#customerTable tbody");
        tbody.innerHTML = "";
        list.forEach(c => {
            tbody.innerHTML += `<tr>
      <td>${c.id}</td><td>${c.name}</td><td>${c.email}</td><td>${c.phone}</td>
      <td><button onclick="deleteCustomer(${c.id})">Delete</button></td>
    </tr>`;
        });
    }
}

// Products
function attachProductForm() {
    const form = document.getElementById("productForm");
    if (!form) return;
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const payload = Object.fromEntries(new FormData(form).entries());
        const res = await fetch(`${API_BASE}/products`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        if (res.ok) { form.reset(); loadProducts(); }
        else {
            let msg = "Error";
            try { msg = (await res.json()).error || msg; } catch { }
            alert(msg);
        }
    });
}

async function loadProducts() {
    const res = await fetch(`${API_BASE}/products`);
    const list = await res.json();
    const tbody = document.querySelector("#productTable tbody");
    if (!tbody) return;
    tbody.innerHTML = "";
    list.forEach(p => {
        tbody.innerHTML += `<tr>
      <td>${p.id}</td><td>${p.name}</td><td>${p.sku ?? "-"}</td><td>${Number(p.price).toFixed(2)}</td><td>${p.stock ?? 0}</td>
      <td><button onclick="deleteProduct(${p.id})">Delete</button></td>
    </tr>`;
    });
}

async function deleteProduct(id) {
    const res = await fetch(`${API_BASE}/products/${id}`, { method: "DELETE" });
    if (res.ok) loadProducts();
}

// Invoices
function attachInvoiceForm() {
    const form = document.getElementById("invoiceForm");
    if (!form) return;
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const fd = new FormData(form);
        const plain = Object.fromEntries(fd.entries());

        const itemsDiv = document.getElementById("items");
        const rows = itemsDiv ? [...itemsDiv.querySelectorAll(".grid-3")] : [];
        const items = rows.map(r => {
            const inputs = r.querySelectorAll("input");
            const obj = {};
            inputs.forEach(i => {
                const base = i.name.replace("[]", "");
                obj[base] = i.value;
            });
            return {
                product_id: Number(obj["product_id"]),
                qty: Number(obj["qty"]),
                price: obj["price"] ? Number(obj["price"]) : 0
            };
        });

        const payload = {
            customer_id: Number(plain.customer_id),
            tax_rate: Number(plain.tax_rate || 0),
            discount_rate: Number(plain.discount_rate || 0),
            items
        };

        const res = await fetch(`${API_BASE}/invoices`, {
            method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload)
        });
        if (res.ok) {
            form.reset();
            if (itemsDiv) itemsDiv.innerHTML = "";
            loadInvoices();
        } else {
            let msg = "Error";
            try { msg = (await res.json()).error || msg; } catch { }
            alert(msg);
        }
    });
}

async function loadInvoices() {
    const res = await fetch(`${API_BASE}/invoices`);
    const list = await res.json();
    const tbody = document.querySelector("#invoiceTable tbody");
    if (!tbody) return;
    tbody.innerHTML = "";
    list.forEach(inv => {
        tbody.innerHTML += `<tr>
      <td>${inv.id}</td><td>${inv.customer_name}</td><td>${inv.grand_total}</td><td>${inv.status}</td>
    </tr>`;
    });
}

// Payments
function attachPaymentForm() {
    const form = document.getElementById("paymentForm");
    if (!form) return;
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const payload = Object.fromEntries(new FormData(form).entries());
        // Convert types
        if (payload.amount) payload.amount = Number(payload.amount);
        if (payload.invoice_id) payload.invoice_id = Number(payload.invoice_id);

        const res = await fetch(`${API_BASE}/payments`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        if (res.ok) {
            form.reset();
            loadPayments();
        } else {
            let msg = "Error";
            try { msg = (await res.json()).error || msg; } catch { }
            alert(msg);
        }
    });
}

async function loadPayments() {
    const res = await fetch(`${API_BASE}/payments`);
    const list = await res.json();
    const tbody = document.querySelector("#paymentTable tbody");
    if (!tbody) return;
    tbody.innerHTML = "";
    list.forEach(pm => {
        tbody.innerHTML += `<tr>
      <td>${pm.id}</td><td>${pm.invoice_id ?? "-"}</td><td>${pm.amount}</td><td>${pm.date ?? "-"}</td>
    </tr>`;
    });
}

// Reports
async function loadReportsSummary() {
    const [bal, sales, top] = await Promise.all([
        fetch(`${API_BASE}/reports/customer-balance`).then(r => r.json()),
        fetch(`${API_BASE}/reports/sales-summary`).then(r => r.json()),
        fetch(`${API_BASE}/reports/top-products`).then(r => r.json()),
    ]);
    const balEl = document.getElementById("reportBalance");
    const salesEl = document.getElementById("reportSales");
    const topEl = document.getElementById("reportTop");
    if (balEl) balEl.textContent = JSON.stringify(bal, null, 2);
    if (salesEl) salesEl.textContent = JSON.stringify(sales, null, 2);
    if (topEl) topEl.textContent = JSON.stringify(top, null, 2);
}
