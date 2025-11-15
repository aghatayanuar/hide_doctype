import frappe

default_whitelist = [
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

role_name = "Whitelisted Doc"
allowed_roles_keep = ("Administrator", role_name)  

def after_install():

    try:
        _populate_whitelist(default_whitelist)
        frappe.db.commit()
        frappe.msgprint("Whitelist items inserted/verified")

        add_role_whitelisted_doc()
        frappe.db.commit()

        # enforce_strict_whitelist_globally()
        # frappe.db.commit()

        frappe.msgprint("After install: whitelist applied and strict mode enforced.")

    except Exception:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "utils.after_install")
        raise

def _populate_whitelist(whitelist_list):
    
    for doctype_name in whitelist_list:
        if not frappe.db.exists("Hide Doctype Whitelist", {"whitelist_doc": doctype_name}):
            doc = frappe.get_doc({
                "doctype": "Hide Doctype Whitelist",
                "whitelist_doc": doctype_name
            })
            doc.insert(ignore_permissions=True)
            frappe.logger().info(f"Inserted whitelist doc: {doctype_name}")
        else:
            frappe.logger().info(f"Whitelist already exists: {doctype_name}")

def add_role_whitelisted_doc():
    
    if not frappe.db.exists("Role", role_name):
        role_doc = frappe.get_doc({
            "doctype": "Role",
            "role_name": role_name
        })
        role_doc.insert(ignore_permissions=True)
        frappe.db.commit()
        frappe.logger().info(f"Role '{role_name}' created")

    whitelisted = frappe.get_all("Hide Doctype Whitelist", fields=["whitelist_doc"])
    whitelisted_names = [w["whitelist_doc"] for w in whitelisted]

    for dt_name in whitelisted_names:
        
        frappe.db.sql("""
            DELETE FROM `tabCustom DocPerm` WHERE parent=%s AND role=%s
        """, (dt_name, role_name))

        frappe.get_doc({
            "doctype": "Custom DocPerm",
            "parent": dt_name,
            "parenttype": "DocType",
            "parentfield": "permissions",
            "role": role_name,
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1
        }).insert(ignore_permissions=True)

    frappe.db.commit()
    frappe.logger().info(f"Custom DocPerm set for role '{role_name}' on whitelisted doctypes.")

# def enforce_strict_whitelist_globally():

#     whitelisted = frappe.get_all("Hide Doctype Whitelist", fields=["whitelist_doc"])
#     whitelisted_names = [w["whitelist_doc"] for w in whitelisted]

#     all_doctypes = frappe.get_all("DocType", filters={"issingle": 0, "istable": 0}, fields=["name"])
#     all_dt_names = [d["name"] for d in all_doctypes]

#     non_whitelisted = [n for n in all_dt_names if n not in whitelisted_names]

#     all_roles = [r["name"] for r in frappe.get_all("Role", fields=["name"])]
#     frappe.logger().info(f"Roles detected: {all_roles}")

#     for dt_name in non_whitelisted:
#         for role in all_roles:
#             if role not in allowed_roles_keep:

#                 frappe.db.sql("""
#                     DELETE FROM `tabCustom DocPerm` WHERE parent=%s AND role=%s
#                 """, (dt_name, role))

#     frappe.db.commit()
#     frappe.logger().info("Removed Custom DocPerm for non-whitelisted doctypes for non-allowed roles.")

#     users = frappe.get_all("User", filters={"enabled": 1, "name": ("!=", "Guest")}, fields=["name"])
#     for u in users:
#         try:
#             user_doc = frappe.get_doc("User", u.name)
#             current_roles = frappe.get_roles(u.name)

#             roles_to_keep = [r for r in current_roles if r in allowed_roles_keep]

#             roles_to_remove = [r for r in current_roles if r not in roles_to_keep]

#             if roles_to_remove:
#                 user_doc.remove_roles(*roles_to_remove)

#             if role_name not in frappe.get_roles(u.name):
#                 user_doc.add_roles(role_name)

#             frappe.db.commit()
#             frappe.logger().info(f"User roles enforced for: {u.name}")
#         except Exception as e:
#             frappe.log_error(f"Error enforcing roles for {u.name}: {str(e)}")

#     frappe.logger().info("Role enforcement completed for all users.")

def update_whitelist_permissions(doc, method):
    dt_name = doc.whitelist_doc
    try:
        if method == "on_trash":
            
            frappe.db.sql("""
                DELETE FROM `tabCustom DocPerm` WHERE parent=%s AND role=%s
            """, (dt_name, role_name))

            other_roles = [r["name"] for r in frappe.get_all("Role", fields=["name"]) if r["name"] not in allowed_roles_keep]
            for role in other_roles:
                frappe.db.sql("""
                    DELETE FROM `tabCustom DocPerm` WHERE parent=%s AND role=%s
                """, (dt_name, role))

            frappe.db.commit()
            frappe.logger().info(f"Whitelist removed for {dt_name} and permissions cleaned up (on_trash).")

        else:
            
            frappe.db.sql("""
                DELETE FROM `tabCustom DocPerm` WHERE parent=%s AND role=%s
            """, (dt_name, role_name))

            frappe.get_doc({
                "doctype": "Custom DocPerm",
                "parent": dt_name,
                "parenttype": "DocType",
                "parentfield": "permissions",
                "role": role_name,
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 1
            }).insert(ignore_permissions=True)

            other_roles = [r["name"] for r in frappe.get_all("Role", fields=["name"]) if r["name"] not in allowed_roles_keep]
            for role in other_roles:
                frappe.db.sql("""
                    DELETE FROM `tabCustom DocPerm` WHERE parent=%s AND role=%s
                """, (dt_name, role))

            frappe.db.commit()
            frappe.logger().info(f"Whitelist added/updated for {dt_name} and permissions set (on_update).")

    except Exception:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "utils.update_whitelist_permissions")
        raise

def assign_whitelisted_role(doc, method):
    
    try:
        user_doc = frappe.get_doc("User", doc.name)
        current_roles = frappe.get_roles(doc.name)

        # roles_to_keep = [r for r in current_roles if r in allowed_roles_keep]
        # roles_to_remove = [r for r in current_roles if r not in roles_to_keep]

        # if roles_to_remove:
        #     user_doc.remove_roles(*roles_to_remove)

        if role_name not in frappe.get_roles(doc.name):
            user_doc.add_roles(role_name)

        frappe.db.commit()
        frappe.logger().info(f"assign_whitelisted_role executed for {doc.name}")
    except Exception:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "utils.assign_whitelisted_role")
        raise

