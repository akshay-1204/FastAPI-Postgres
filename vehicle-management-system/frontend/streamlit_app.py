from datetime import date
import pandas as pd
import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Vehicle Management System",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling and comfortable UI
st.markdown("""
<style>
    /* Metric Card Styling */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.02));
        border: 1px solid rgba(128, 128, 128, 0.2);
        padding: 16px 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
    }
    
    /* Custom Badge Styles */
    .vms-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .badge-active, .badge-completed {
        background-color: #d1fae5;
        color: #065f46;
        border: 1px solid #a7f3d0;
    }
    .badge-pending, .badge-in-progress, .badge-scheduled {
        background-color: #fef3c7;
        color: #92400e;
        border: 1px solid #fde68a;
    }
    .badge-expired {
        background-color: #fee2e2;
        color: #991b1b;
        border: 1px solid #fecaca;
    }
    .badge-plate {
        background-color: #e0f2fe;
        color: #0369a1;
        font-family: monospace;
        font-weight: 700;
        border: 1px solid #bae6fd;
    }
    
    /* Card Container */
    .vms-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 16px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
    }
    
    /* Profile Hero */
    .profile-hero {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        padding: 24px;
        border-radius: 16px;
        margin-bottom: 20px;
        box-shadow: 0 8px 24px rgba(30, 58, 138, 0.25);
    }
</style>
""", unsafe_allow_html=True)

if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "user_role" not in st.session_state:
    st.session_state.user_role = None


def api_request(method, path, *, params=None, data=None):
    headers = {}
    if st.session_state.access_token:
        headers["Authorization"] = f"Bearer {st.session_state.access_token}"
    try:
        response = requests.request(
            method,
            f"{API_URL}{path}",
            headers=headers,
            params=params,
            json=data,
            timeout=15,
        )
    except requests.RequestException as exc:
        st.error(f"Could not connect to FastAPI at {API_URL}. Is the server running? Error: {exc}")
        return None

    if not response.ok:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text
        st.error(f"API Error ({response.status_code}): {detail}")
        return None

    if response.status_code == 204 or not response.content:
        return {}
    try:
        return response.json()
    except ValueError:
        return {"message": response.text}


def show_table(data, empty_message="No records found."):
    if data is None:
        return
    if isinstance(data, dict):
        data = [data]
    if not data:
        st.info(empty_message)
        return
    st.dataframe(pd.json_normalize(data), use_container_width=True, hide_index=True)


def get_vehicle_icon(v_type):
    icons = {
        "sedan": "🚗",
        "suv": "🚙",
        "truck": "🛻",
        "electric": "⚡",
        "hatchback": "🚘",
        "van": "🚐"
    }
    return icons.get(str(v_type).lower(), "🚗")


def login_page():
    st.title("🚗 Secure Vehicle Management System")
    st.write("Sign in or create an account to manage your fleet, vehicles, services, and reports.")

    login_tab, register_tab = st.tabs(["Login", "Register"])

    with login_tab:
        st.subheader("Sign In")
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            submitted = st.form_submit_button("Sign In", type="primary", use_container_width=True)

        if submitted:
            if not email.strip() or not password:
                st.warning("Please enter your email and password.")
            else:
                try:
                    response = requests.post(
                        f"{API_URL}/auth/login",
                        data={"username": email.strip(), "password": password},
                        timeout=15,
                    )
                    if response.ok:
                        token_data = response.json()
                        st.session_state.access_token = token_data["access_token"]
                        st.session_state.user_email = email.strip()
                        st.session_state.user_role = token_data.get("role", "customer")
                        st.success(f"Logged in as {email.strip()} ({st.session_state.user_role})")
                        st.rerun()
                    else:
                        st.error("Invalid email or password.")
                except requests.RequestException as exc:
                    st.error(f"Connection failure: {exc}")

    with register_tab:
        st.subheader("Create an Account")
        with st.form("register_form"):
            full_name = st.text_input("Full Name")
            reg_email = st.text_input("Email", key="reg_email")
            reg_password = st.text_input("Password (min 8 characters)", type="password")
            role = st.selectbox("Role", ["customer", "admin"])
            reg_submitted = st.form_submit_button("Register", type="primary", use_container_width=True)

        if reg_submitted:
            if not full_name.strip() or not reg_email.strip() or len(reg_password) < 8:
                st.warning("Please provide all fields with a valid password of at least 8 characters.")
            else:
                payload = {
                    "full_name": full_name.strip(),
                    "email": reg_email.strip(),
                    "password": reg_password,
                    "role": role
                }
                res = api_request("POST", "/auth/register", data=payload)
                if res:
                    st.success("Account created successfully. You may now switch to the Login tab.")


def main_app():
    sidebar = st.sidebar
    sidebar.title("🚗 Navigation")
    sidebar.write(f"Signed in as: **{st.session_state.user_email}**")
    role_badge = "👑 Admin" if st.session_state.user_role == "admin" else "👤 Customer"
    sidebar.write(f"Account: **{role_badge}**")

    if sidebar.button("Sign Out", type="secondary", use_container_width=True):
        st.session_state.access_token = None
        st.session_state.user_email = None
        st.session_state.user_role = None
        st.rerun()

    sidebar.markdown("---")
    pages = [
        "Executive Dashboard",
        "Vehicles",
        "Insurance",
        "Service Records",
        "Vehicle Parts",
        "Service Centers",
        "Analytical Reports"
    ]
    choice = sidebar.radio("Go to", pages)

    # -------------------------------------------------------------
    # 1. EXECUTIVE DASHBOARD & PROFILE
    # -------------------------------------------------------------
    if choice == "Executive Dashboard":
        customers = api_request("GET", "/customers/") or []
        vehicles = api_request("GET", "/vehicles/") or []
        policies = api_request("GET", "/insurance/") or []
        services = api_request("GET", "/service-records/") or []

        # Find linked profile for current user
        my_profile = customers[0] if customers else None

        st.title("📊 Executive Fleet Dashboard")
        st.caption(f"Welcome back, **{my_profile['full_name'] if my_profile else st.session_state.user_email}**! Here is your live fleet overview.")

        # Top KPI Metrics Row
        total_vehicles = len(vehicles)
        active_policies = sum(1 for p in policies if str(p.get("status", "")).lower() == "active")
        total_services = len(services)
        total_maintenance_cost = sum(float(s.get("service_cost", 0.0)) for s in services)

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("🚗 Total Vehicles", total_vehicles, help="Number of registered vehicles")
        kpi2.metric("🛡️ Active Insurance", active_policies, f"{len(policies) - active_policies} Inactive", delta_color="inverse")
        kpi3.metric("🔧 Service Visits", total_services, help="Total logged maintenance visits")
        kpi4.metric("💰 Maintenance Spend", f"${total_maintenance_cost:,.2f}", help="Cumulative service expenditure")

        st.markdown("<br>", unsafe_allow_html=True)

        col_left, col_right = st.columns([1.7, 1.3])

        with col_left:
            st.subheader("🚙 Fleet Highlights")
            if not vehicles:
                st.info("No vehicles registered yet. Go to **Vehicles** to add your first car.")
            else:
                # Show top vehicles as cards
                for v in vehicles[:4]:
                    icon = get_vehicle_icon(v.get("vehicle_type", "Sedan"))
                    with st.container(border=True):
                        v_col1, v_col2 = st.columns([2, 1])
                        with v_col1:
                            st.markdown(f"#### {icon} {v.get('brand')} {v.get('model')}")
                            st.markdown(
                                f"<span class='vms-badge badge-plate'>{v.get('registration_no')}</span> "
                                f"<span class='vms-badge' style='background-color:#f1f5f9; color:#475569;'>{v.get('vehicle_type')}</span>",
                                unsafe_allow_html=True
                            )
                        with v_col2:
                            st.write(f"**Year:** {v.get('manufacturing_year')}")
                            st.write(f"**Price:** ${float(v.get('purchase_price', 0)):,.2f}")

                if len(vehicles) > 4:
                    st.caption(f"*Showing 4 of {len(vehicles)} vehicles. Visit the Vehicles tab to see all.*")

            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("🛠️ Recent Service Activity")
            if not services:
                st.info("No service maintenance logged yet.")
            else:
                for s in services[:3]:
                    status = str(s.get("status", "Completed"))
                    badge_cls = "badge-completed" if status.lower() == "completed" else "badge-pending"
                    with st.container(border=True):
                        sc1, sc2 = st.columns([2, 1])
                        with sc1:
                            st.markdown(f"**{s.get('service_type')}** • {s.get('service_date')}")
                            st.caption(s.get("description") or "Routine maintenance inspection")
                        with sc2:
                            st.markdown(f"<span class='vms-badge {badge_cls}'>{status}</span>", unsafe_allow_html=True)
                            st.markdown(f"**${float(s.get('service_cost', 0)):,.2f}**")

        with col_right:
            st.subheader("👤 Profile & Account")
            if my_profile:
                with st.container(border=True):
                    st.markdown(f"### 🪪 {my_profile.get('full_name')}")
                    st.write(f"📧 **Email:** {my_profile.get('email')}")
                    st.write(f"📱 **Phone:** {my_profile.get('phone')}")
                    st.write(f"📍 **Address:** {my_profile.get('address') or 'Not provided'}")
                    st.write(f"🆔 **Customer ID:** #{my_profile.get('customer_id')}")

                    with st.expander("✏️ Update Profile Details"):
                        with st.form("update_profile_form"):
                            edit_name = st.text_input("Full Name", value=my_profile.get("full_name", ""))
                            edit_phone = st.text_input("Phone", value=my_profile.get("phone", ""))
                            edit_address = st.text_area("Address", value=my_profile.get("address", "") or "")
                            upd_btn = st.form_submit_button("Save Changes")

                        if upd_btn:
                            res = api_request("PUT", f"/customers/{my_profile['customer_id']}", data={
                                "full_name": edit_name.strip(),
                                "phone": edit_phone.strip(),
                                "address": edit_address.strip()
                            })
                            if res:
                                st.success("Profile updated successfully!")
                                st.rerun()
            else:
                with st.container(border=True):
                    st.warning("⚠️ No customer profile linked yet.")
                    st.write("Complete your customer profile to start registering vehicles and tracking service logs.")
                    with st.form("create_customer_form"):
                        cust_name = st.text_input("Full Name", value=st.session_state.user_email.split("@")[0])
                        cust_email = st.text_input("Email", value=st.session_state.user_email)
                        cust_phone = st.text_input("Phone Number")
                        cust_address = st.text_area("Address")
                        save_cust = st.form_submit_button("Create Profile", type="primary")

                    if save_cust:
                        if not cust_name.strip() or not cust_phone.strip():
                            st.warning("Please provide your name and phone number.")
                        else:
                            payload = {
                                "full_name": cust_name.strip(),
                                "email": cust_email.strip(),
                                "phone": cust_phone.strip(),
                                "address": cust_address.strip()
                            }
                            res = api_request("POST", "/customers/", data=payload)
                            if res:
                                st.success("Profile created successfully.")
                                st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)
            with st.container(border=True):
                st.subheader("⚡ Quick Shortcuts")
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    st.info(f"**Role:** {st.session_state.user_role.upper()}")
                with col_btn2:
                    st.success("API: Connected 🟢")

    # -------------------------------------------------------------
    # 2. VEHICLES
    # -------------------------------------------------------------
    elif choice == "Vehicles":
        st.title("🚙 Vehicle Management")
        tab_list, tab_add = st.tabs(["Browse Fleet", "➕ Register Vehicle"])

        with tab_list:
            vehicles = api_request("GET", "/vehicles/") or []

            if not vehicles:
                st.info("No vehicles found for your account. Register one in the tab above!")
            else:
                filter_c1, filter_c2, filter_c3 = st.columns([2, 1, 1])
                with filter_c1:
                    search_term = st.text_input("🔍 Search by Brand, Model, or Plate", "").strip().lower()
                with filter_c2:
                    type_filter = st.selectbox("Filter Type", ["All Types"] + sorted(list({v.get("vehicle_type", "Other") for v in vehicles})))
                with filter_c3:
                    view_mode = st.radio("View As", ["Cards View", "Table View"], horizontal=True)

                filtered_vehicles = [
                    v for v in vehicles
                    if (search_term in v.get("brand", "").lower()
                        or search_term in v.get("model", "").lower()
                        or search_term in v.get("registration_no", "").lower())
                    and (type_filter == "All Types" or v.get("vehicle_type") == type_filter)
                ]

                st.caption(f"Showing **{len(filtered_vehicles)}** of **{len(vehicles)}** vehicles")

                if view_mode == "Table View":
                    show_table(filtered_vehicles)
                else:
                    grid_cols = st.columns(3)
                    for i, v in enumerate(filtered_vehicles):
                        col = grid_cols[i % 3]
                        icon = get_vehicle_icon(v.get("vehicle_type", "Sedan"))
                        with col:
                            with st.container(border=True):
                                st.markdown(f"### {icon} {v.get('brand')} {v.get('model')}")
                                st.markdown(f"<span class='vms-badge badge-plate'>{v.get('registration_no')}</span>", unsafe_allow_html=True)
                                st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
                                st.write(f"**Type:** {v.get('vehicle_type')} | **Year:** {v.get('manufacturing_year')}")
                                st.write(f"**Color:** {v.get('color') or 'N/A'}")
                                st.write(f"**Price:** 💲{float(v.get('purchase_price', 0)):,.2f}")

        with tab_add:
            st.subheader("Add a New Vehicle")
            with st.form("add_vehicle_form"):
                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    reg_no = st.text_input("Registration Plate Number (e.g. KA-01-AB-1234)")
                    brand = st.text_input("Brand / Make (e.g. Toyota, Tesla)")
                    model = st.text_input("Model (e.g. Camry, Model 3)")
                    v_type = st.selectbox("Vehicle Type", ["Sedan", "SUV", "Truck", "Hatchback", "Electric", "Van"])
                with col_f2:
                    year = st.number_input("Manufacturing Year", min_value=1950, max_value=2050, value=2022)
                    color = st.text_input("Vehicle Color (e.g. Midnight Blue)")
                    price = st.number_input("Purchase Price ($)", min_value=0.0, value=25000.0, step=500.0)

                add_v_btn = st.form_submit_button("Register Vehicle", type="primary", use_container_width=True)

            if add_v_btn:
                if not reg_no.strip() or not brand.strip() or not model.strip():
                    st.warning("Registration number, brand, and model are required.")
                else:
                    payload = {
                        "registration_no": reg_no.strip(),
                        "brand": brand.strip(),
                        "model": model.strip(),
                        "vehicle_type": v_type,
                        "manufacturing_year": int(year),
                        "color": color.strip() if color.strip() else None,
                        "purchase_price": float(price)
                    }
                    res = api_request("POST", "/vehicles/", data=payload)
                    if res:
                        st.success("Vehicle registered successfully!")
                        st.rerun()

    # -------------------------------------------------------------
    # 3. INSURANCE
    # -------------------------------------------------------------
    elif choice == "Insurance":
        st.title("🛡️ Insurance Policies")
        tab_list, tab_add = st.tabs(["Active & Expired Policies", "➕ Register Policy"])

        with tab_list:
            policies = api_request("GET", "/insurance/") or []
            if not policies:
                st.info("No insurance policies found.")
            else:
                active_count = sum(1 for p in policies if str(p.get("status", "")).lower() == "active")
                exp_count = len(policies) - active_count
                total_premium = sum(float(p.get("premium_amount", 0)) for p in policies)

                ic1, ic2, ic3 = st.columns(3)
                ic1.metric("Total Policies", len(policies))
                ic2.metric("Active Policies", active_count, f"{exp_count} Expired/Pending")
                ic3.metric("Total Premiums", f"${total_premium:,.2f}")

                st.markdown("<br>", unsafe_allow_html=True)
                view_mode = st.radio("Display Mode", ["Cards View", "Table View"], horizontal=True, key="ins_mode")

                if view_mode == "Table View":
                    show_table(policies)
                else:
                    grid_cols = st.columns(3)
                    for i, p in enumerate(policies):
                        status = str(p.get("status", "Active"))
                        badge_cls = "badge-active" if status.lower() == "active" else "badge-expired"
                        with grid_cols[i % 3]:
                            with st.container(border=True):
                                st.markdown(f"#### 🛡️ {p.get('insurance_company')}")
                                st.markdown(
                                    f"<span class='vms-badge {badge_cls}'>{status}</span> "
                                    f"<span class='vms-badge badge-plate'>{p.get('policy_number')}</span>",
                                    unsafe_allow_html=True
                                )
                                st.markdown("<hr style='margin: 8px 0;'>", unsafe_allow_html=True)
                                st.write(f"**Vehicle ID:** #{p.get('vehicle_id')}")
                                st.write(f"📅 **Duration:** {p.get('start_date')} ➔ {p.get('end_date')}")
                                st.write(f"💵 **Premium:** **${float(p.get('premium_amount', 0)):,.2f}**")

        with tab_add:
            vehicles = api_request("GET", "/vehicles/")
            if not vehicles:
                st.warning("You must register at least one vehicle before adding an insurance policy.")
            else:
                vehicle_options = {f"{v['brand']} {v['model']} ({v['registration_no']})": v["vehicle_id"] for v in vehicles}
                selected_v = st.selectbox("Select Vehicle", list(vehicle_options.keys()))

                with st.form("add_insurance_form"):
                    col_i1, col_i2 = st.columns(2)
                    with col_i1:
                        policy_num = st.text_input("Policy Number")
                        provider = st.text_input("Insurance Company")
                        premium = st.number_input("Premium Amount ($)", min_value=0.0, value=500.0)
                    with col_i2:
                        s_date = st.date_input("Start Date", value=date.today())
                        e_date = st.date_input("End Date", value=date.today())
                        pol_status = st.selectbox("Status", ["Active", "Pending", "Expired"])

                    ins_btn = st.form_submit_button("Submit Policy", type="primary", use_container_width=True)

                if ins_btn:
                    if not policy_num.strip() or not provider.strip():
                        st.warning("Policy number and company name are required.")
                    else:
                        payload = {
                            "vehicle_id": vehicle_options[selected_v],
                            "policy_number": policy_num.strip(),
                            "insurance_company": provider.strip(),
                            "start_date": str(s_date),
                            "end_date": str(e_date),
                            "premium_amount": float(premium),
                            "status": pol_status
                        }
                        res = api_request("POST", "/insurance/", data=payload)
                        if res:
                            st.success("Insurance registered successfully!")
                            st.rerun()

    # -------------------------------------------------------------
    # 4. SERVICE RECORDS
    # -------------------------------------------------------------
    elif choice == "Service Records":
        st.title("🔧 Maintenance & Service Records")
        tab_list, tab_add = st.tabs(["Service History", "➕ Log Maintenance"])

        with tab_list:
            records = api_request("GET", "/service-records/") or []
            if not records:
                st.info("No service records found.")
            else:
                total_cost = sum(float(r.get("service_cost", 0)) for r in records)
                sc1, sc2 = st.columns(2)
                sc1.metric("Total Maintenance Visits", len(records))
                sc2.metric("Cumulative Cost", f"${total_cost:,.2f}")

                st.markdown("<br>", unsafe_allow_html=True)
                view_mode = st.radio("View Style", ["Cards Feed", "Data Table"], horizontal=True, key="srv_mode")

                if view_mode == "Data Table":
                    show_table(records)
                else:
                    for r in records:
                        status = str(r.get("status", "Completed"))
                        badge_cls = "badge-completed" if status.lower() == "completed" else "badge-in-progress"
                        with st.container(border=True):
                            r_c1, r_c2, r_c3 = st.columns([2, 1, 1])
                            with r_c1:
                                st.markdown(f"#### 🛠️ {r.get('service_type')}")
                                st.caption(f"Vehicle #{r.get('vehicle_id')} • Center #{r.get('service_center_id')}")
                                st.write(r.get("description") or "Routine maintenance inspection")
                            with r_c2:
                                st.write(f"📅 **Date:** {r.get('service_date')}")
                                st.write(f"⏱️ **Odometer:** {r.get('odometer_reading'):,} km/mi")
                            with r_c3:
                                st.markdown(f"<span class='vms-badge {badge_cls}'>{status}</span>", unsafe_allow_html=True)
                                st.markdown(f"### 💲{float(r.get('service_cost', 0)):,.2f}")

        with tab_add:
            vehicles = api_request("GET", "/vehicles/")
            centers = api_request("GET", "/service-centers/")
            if not vehicles:
                st.warning("Please add a vehicle first.")
            elif not centers:
                st.warning("No service centers available yet.")
            else:
                vehicle_opts = {f"{v['brand']} {v['model']} ({v['registration_no']})": v["vehicle_id"] for v in vehicles}
                center_opts = {f"{c['center_name']} - {c.get('city', '')}": c["service_center_id"] for c in centers}

                selected_v = st.selectbox("Vehicle", list(vehicle_opts.keys()))
                selected_c = st.selectbox("Service Center", list(center_opts.keys()))

                with st.form("add_service_form"):
                    col_s1, col_s2 = st.columns(2)
                    with col_s1:
                        srv_date = st.date_input("Service Date", value=date.today())
                        srv_type = st.text_input("Service Type (e.g. 50k Inspection, Brake Replacement)")
                        srv_desc = st.text_area("Work Description")
                    with col_s2:
                        odometer = st.number_input("Odometer Reading", min_value=0, value=25000)
                        cost = st.number_input("Service Cost ($)", min_value=0.0, value=150.0)
                        srv_status = st.selectbox("Status", ["Completed", "In Progress", "Scheduled"])

                    srv_btn = st.form_submit_button("Log Maintenance Record", type="primary", use_container_width=True)

                if srv_btn:
                    if not srv_type.strip():
                        st.warning("Service type is required.")
                    else:
                        payload = {
                            "vehicle_id": vehicle_opts[selected_v],
                            "service_center_id": center_opts[selected_c],
                            "service_date": str(srv_date),
                            "service_type": srv_type.strip(),
                            "description": srv_desc.strip(),
                            "odometer_reading": int(odometer),
                            "service_cost": float(cost),
                            "status": srv_status
                        }
                        res = api_request("POST", "/service-records/", data=payload)
                        if res:
                            st.success("Service record added successfully.")
                            st.rerun()

    # -------------------------------------------------------------
    # 5. VEHICLE PARTS
    # -------------------------------------------------------------
    elif choice == "Vehicle Parts":
        st.title("⚙️ Vehicle Parts Tracker")
        parts = api_request("GET", "/vehicle-parts/") or []
        if not parts:
            st.info("No parts found for your service records.")
        else:
            total_parts_cost = sum(float(p.get("total_price", 0)) for p in parts)
            pc1, pc2 = st.columns(2)
            pc1.metric("Cataloged Replacement Parts", len(parts))
            pc2.metric("Total Parts Investment", f"${total_parts_cost:,.2f}")
            st.markdown("<br>", unsafe_allow_html=True)
            show_table(parts)

    # -------------------------------------------------------------
    # 6. SERVICE CENTERS
    # -------------------------------------------------------------
    elif choice == "Service Centers":
        st.title("🏬 Service Centers Network")
        centers = api_request("GET", "/service-centers/") or []
        if not centers:
            st.info("No service centers found.")
        else:
            st.metric("Authorized Centers", len(centers))
            st.markdown("<br>", unsafe_allow_html=True)

            sc_cols = st.columns(3)
            for i, c in enumerate(centers):
                with sc_cols[i % 3]:
                    with st.container(border=True):
                        st.markdown(f"### 🏢 {c.get('center_name')}")
                        rating = float(c.get("rating", 5.0))
                        st.markdown(f"⭐ **{rating:.1f} / 5.0** • *{c.get('city') or 'Local'}*")
                        st.write(f"📍 {c.get('address') or 'Address on file'}")
                        st.write(f"📞 {c.get('phone') or 'N/A'}")
                        st.write(f"✉️ {c.get('email') or 'N/A'}")

        if st.session_state.user_role == "admin":
            st.markdown("<hr>", unsafe_allow_html=True)
            st.subheader("👑 Admin: Register New Service Center")
            with st.form("admin_center_form"):
                c_name = st.text_input("Center Name")
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    c_phone = st.text_input("Phone")
                    c_email = st.text_input("Email")
                with col_c2:
                    c_city = st.text_input("City")
                    c_rating = st.number_input("Rating (0.0 to 5.0)", min_value=0.0, max_value=5.0, value=4.5, step=0.1)
                c_addr = st.text_area("Address")
                submit_center = st.form_submit_button("Add Service Center", type="primary")

            if submit_center:
                if not c_name.strip():
                    st.warning("Center name is required.")
                else:
                    payload = {
                        "center_name": c_name.strip(),
                        "phone": c_phone.strip() if c_phone.strip() else None,
                        "email": c_email.strip() if c_email.strip() else None,
                        "address": c_addr.strip() if c_addr.strip() else None,
                        "city": c_city.strip() if c_city.strip() else None,
                        "rating": float(c_rating)
                    }
                    res = api_request("POST", "/service-centers/", data=payload)
                    if res:
                        st.success("Service center created successfully.")
                        st.rerun()

    # -------------------------------------------------------------
    # 7. ANALYTICAL REPORTS
    # -------------------------------------------------------------
    elif choice == "Analytical Reports":
        st.title("📊 Analytical Reports & Insights")

        rep_type = st.selectbox(
            "Select Analytical Report",
            [
                "Vehicles by Type",
                "Service Cost Summary",
                "Customer Vehicle Summary",
                "Top Service Centers",
                "Parts Cost Summary",
                "Insurance Status"
            ]
        )

        path_map = {
            "Vehicles by Type": "/reports/vehicles-by-type",
            "Service Cost Summary": "/reports/service-cost-summary",
            "Customer Vehicle Summary": "/reports/customer-vehicles",
            "Top Service Centers": "/reports/top-service-centers",
            "Parts Cost Summary": "/reports/parts-cost-summary",
            "Insurance Status": "/reports/insurance-status"
        }

        data = api_request("GET", path_map[rep_type])

        if data:
            if rep_type == "Vehicles by Type":
                df = pd.DataFrame(data)
                if not df.empty and "vehicle_type" in df.columns:
                    st.subheader("Fleet Composition by Vehicle Type")
                    val_col = "total_vehicles" if "total_vehicles" in df.columns else [c for c in df.columns if c != "vehicle_type"][0]
                    st.bar_chart(df.set_index("vehicle_type")[val_col])
                with st.expander("Show Data Table", expanded=df.empty):
                    show_table(data)

            elif rep_type == "Service Cost Summary":
                st.subheader("Maintenance Financial Metrics")
                tot = data.get("total_service_cost", 0.0)
                avg = data.get("average_service_cost", 0.0)
                cnt = data.get("total_services", 0)

                m1, m2, m3 = st.columns(3)
                m1.metric("Total Service Cost", f"${tot:,.2f}")
                m2.metric("Average Cost Per Visit", f"${avg:,.2f}")
                m3.metric("Total Completed Services", cnt)

                with st.expander("Show Raw Summary"):
                    show_table(data)

            elif rep_type == "Insurance Status":
                df = pd.DataFrame(data)
                if not df.empty and "status" in df.columns:
                    st.subheader("Insurance Policies Distribution")
                    val_col = "total_policies" if "total_policies" in df.columns else [c for c in df.columns if c != "status"][0]
                    st.bar_chart(df.set_index("status")[val_col])
                with st.expander("Show Data Table", expanded=df.empty):
                    show_table(data)

            elif rep_type == "Parts Cost Summary":
                st.subheader("Parts Investment Summary")
                m1, m2, m3 = st.columns(3)
                m1.metric("Total Parts Cost", f"${data.get('total_parts_cost', 0):,.2f}")
                m2.metric("Cataloged Parts", data.get("total_parts", 0))
                m3.metric("Total Quantity Used", data.get("total_quantity", 0))

                with st.expander("Show Raw Summary"):
                    show_table(data)

            elif rep_type == "Top Service Centers":
                df = pd.DataFrame(data)
                if not df.empty and "center_name" in df.columns:
                    st.subheader("Top Service Centers by Activity")
                    val_col = "total_services" if "total_services" in df.columns else [c for c in df.columns if c != "center_name"][0]
                    st.bar_chart(df.set_index("center_name")[val_col])
                with st.expander("Show Data Table", expanded=df.empty):
                    show_table(data)

            else:
                df = pd.DataFrame(data)
                if not df.empty and "customer_name" in df.columns:
                    st.subheader("Customer Fleet Breakdown")
                    val_col = "total_vehicles" if "total_vehicles" in df.columns else [c for c in df.columns if c != "customer_name"][0]
                    st.bar_chart(df.set_index("customer_name")[val_col])
                with st.expander("Show Data Table", expanded=df.empty):
                    show_table(data)
        else:
            st.info("No report data available.")


if st.session_state.access_token is None:
    login_page()
else:
    main_app()
