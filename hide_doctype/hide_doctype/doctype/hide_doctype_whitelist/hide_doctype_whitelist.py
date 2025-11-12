# Copyright (c) 2025, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class HideDoctypeWhitelist(Document):
	pass

def test():
	whitelisted_doctypes = [
		"Customer", "Sales Order", "Sales Invoice", "Delivery Note", "Quotation",
		"Sales Taxes and Charges Template", "Pricing Rule", "Item", "Item Group",
		"Supplier", "Purchase Order", "Purchase Invoice", "Purchase Receipt",
		"Supplier Quotation", "Material Request", "Stock Entry", "Stock Ledger Entry",
		"Warehouse", "Batch", "Serial No", "Item Price", "Stock Reconciliation",
		"Stock Reservation Entry", "Payment Entry", "Journal Entry", "Bank Account",
		"Mode of Payment", "Company", "Account", "Cost Center", "GL Entry", 
		"Employee", "Department", "Designation", "Project", "Task",
		"Timesheet", "User", "Role", "Role Permission for Page and Report",
		"Email Account", "Print Format", "Letter Head", "Currency", "Address",
		"Contact", "Lead", "Opportunity", "Customer Group", "Territory", "Campaign",
		"BOM", "Work Order", "Production Plan", "Routing"
	]

	for doctype_name in whitelisted_doctypes:
		exists = frappe.db.exists("Hide Doctype Whitelist", {"whitelist_doc": doctype_name})
		if not exists:
			doc = frappe.get_doc({
				"doctype": "Hide Doctype Whitelist",
				"whitelist_doc": doctype_name
			})
			doc.insert(ignore_permissions=True)
			print(f"Inserted: {doctype_name}")  
		else:
			print(f"Already exists: {doctype_name}")  
	frappe.db.commit()
	print("After install: all default doctypes processed.")  


def apply_user_cannot_search():
    all_doctypes = frappe.get_all(
        "DocType",
        filters={
            "issingle": 0, 
            "istable": 0,
			"custom": 0
        },
        fields=["name", "read_only"]
    )

    whitelisted = frappe.get_all("Hide Doctype Whitelist", fields=["whitelist_doc"])
    whitelisted_names = [w["whitelist_doc"] for w in whitelisted]

    updated_count = 0

    for dt in all_doctypes:
        name = dt["name"]
        try:
            doc = frappe.get_doc("DocType", name)

            if name in whitelisted_names:
                if doc.read_only != 0:
                    doc.read_only = 0
                    doc.save(ignore_permissions=True)
                    print(f"Whitelist: {name} → read_only set to 0")
                    updated_count += 1
                else:
                    print(f"Whitelist: {name} → already 0")
            else:
                if doc.read_only != 1:
                    doc.read_only = 1
                    doc.save(ignore_permissions=True)
                    print(f"Set User Cannot Search: {name} → read_only set to 1")
                    updated_count += 1
                else:
                    print(f"{name} → already 1")

        except Exception as e:
            frappe.log_error(message=str(e), title=f"Gagal update DocType: {name}")
            print(f"Gagal update {name}: {str(e)}")
            continue

    frappe.clear_cache()
    print(f"Done. Total DocTypes updated: {updated_count}")
