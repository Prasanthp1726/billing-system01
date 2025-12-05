async function fetchJSON(url) {
    const res = await fetch(url);
    if (!res.ok) {
        const txt = await res.text();
        throw new Error(txt || `HTTP ${res.status}`);
    }
    return res.json();
}

function currency(x) {
    if (x === null || x === undefined) return "-";
    return `₹${Number(x).toLocaleString("en-IN")}`;
}

async function loadReportsSummary() {
    // Customer balance
    try {
        const balances = await fetchJSON("/api/reports/customer-balance");
        const tbody = document.getElementById("balanceTable");
        if (!balances.length) {
            tbody.innerHTML = `<tr><td colspan="4" class="muted">No data</td></tr>`;
        } else {
            tbody.innerHTML = balances.map(b => `
        <tr>
          <td>${b.customer}</td>
          <td>${currency(b.invoiced)}</td>
          <td>${currency(b.paid)}</td>
          <td>${currency(b.balance)}</td>
        </tr>
      `).join("");
        }
    } catch (e) {
        document.getElementById("balanceTable").innerHTML =
            `<tr><td colspan="4" class="muted">Error: ${e.message}</td></tr>`;
    }

    // Sales summary
    try {
        const sales = await fetchJSON("/api/reports/sales-summary");
        document.getElementById("salesSummary").innerHTML = `
      <tr><th>Total sales</th><td>${currency(sales.total_sales)}</td></tr>
      <tr><th>Total paid</th><td>${currency(sales.total_paid)}</td></tr>
      <tr><th>Invoice count</th><td>${sales.invoice_count}</td></tr>
    `;
    } catch (e) {
        document.getElementById("salesSummary").innerHTML =
            `<tr><td class="muted">Error: ${e.message}</td></tr>`;
    }

    // Top products
    try {
        const top = await fetchJSON("/api/reports/top-products");
        const tbody = document.getElementById("topProductsTable");
        if (!top.length) {
            tbody.innerHTML = `<tr><td colspan="2" class="muted">No data</td></tr>`;
        } else {
            tbody.innerHTML = top.map(p => `
        <tr><td>${p.product}</td><td>${p.qty_sold}</td></tr>
      `).join("");
        }
    } catch (e) {
        document.getElementById("topProductsTable").innerHTML =
            `<tr><td colspan="2" class="muted">Error: ${e.message}</td></tr>`;
    }
}

async function loadStatement(cid) {
    try {
        const list = await fetchJSON(`/api/reports/customer-statement?customer_id=${cid}`);
        const tbody = document.getElementById("statementTable");
        if (!list.length) {
            tbody.innerHTML = `<tr><td colspan="3" class="muted">No records</td></tr>`;
        } else {
            tbody.innerHTML = list.map(r => `
        <tr>
          <td>${r.date}</td>
          <td>${r.invoice}</td>
          <td>${currency(r.amount)}</td>
        </tr>
      `).join("");
        }
    } catch (e) {
        document.getElementById("statementTable").innerHTML =
            `<tr><td colspan="3" class="muted">Error: ${e.message}</td></tr>`;
    }
}

function attachStatementForm() {
    const form = document.getElementById("statementForm");
    if (!form) return;
    form.addEventListener("submit", (e) => {
        e.preventDefault();
        const cid = Number(new FormData(form).get("customer_id"));
        if (!cid) return alert("Enter a valid Customer ID");
        loadStatement(cid);
    });
}

// Initialize on page load
attachStatementForm();
loadReportsSummary();
