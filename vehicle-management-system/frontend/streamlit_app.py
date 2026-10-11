from datetime import date
import pandas as pd
import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Vehicle Management System",
    page_icon="🚗",
    layout="wide"
)

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
    sidebar.write(f"Role: **{st.session_state.user_role.upper()}**")

    if sidebar.button("Sign Out", type="secondary"):
        st.session_state.access_token = None
        st.session_state.user_email = None
        st.session_state.user_role = None
        st.rerun()

    pages = [
        "Dashboard & Profile",
        "Vehicles",
        "Insurance",
        "Service Records",
        "Vehicle Parts",
        "Service Centers",
        "Reports"
    ]
    choice = sidebar.radio("Go to", pages)

    if choice == "Dashboard & Profile":
        st.header("👤 Customer Profile & Account")
        customers = api_request("GET", "/customers/")
        if customers:
            st.success("Your Customer Profile:")
            show_table(customers)
        else:
            st.warning("No customer profile linked yet. Set up your profile to manage vehicles:")
            with st.form("create_customer_form"):
                cust_name = st.text_input("Full Name", value=st.session_state.user_email.split("@")[0])
                cust_email = st.text_input("Email", value=st.session_state.user_email)
                cust_phone = st.text_input("Phone Number")
                cust_address = st.text_area("Address")
                save_cust = st.form_submit_button("Save Profile")

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

    elif choice == "Vehicles":
        st.header("🚙 Vehicles")
        tab_list, tab_add = st.tabs(["Browse Vehicles", "Add Vehicle"])

        with tab_list:
            if st.button("Refresh Vehicles"):
                st.rerun()
            vehicles = api_request("GET", "/vehicles/")
            show_table(vehicles, "No vehicles found for your account.")

        with tab_add:
            with st.form("add_vehicle_form"):
                reg_no = st.text_input("Registration Number (e.g. KA-01-AB-1234)")
                brand = st.text_input("Brand (e.g. Toyota)")
                model = st.text_input("Model (e.g. Camry)")
                v_type = st.selectbox("Vehicle Type", ["Sedan", "SUV", "Truck", "Hatchback", "Electric", "Van"])
                year = st.number_input("Manufacturing Year", min_value=1950, max_value=2050, value=2022)
                color = st.text_input("Color")
                price = st.number_input("Purchase Price", min_value=0.0, value=25000.0, step=500.0)
                add_v_btn = st.form_submit_button("Register Vehicle")

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

    elif choice == "Insurance":
        st.header("🛡️ Insurance Policies")
        tab_list, tab_add = st.tabs(["View Policies", "Add Policy"])

        with tab_list:
            policies = api_request("GET", "/insurance/")
            show_table(policies, "No insurance policies found.")

        with tab_add:
            vehicles = api_request("GET", "/vehicles/")
            if not vehicles:
                st.warning("You must register at least one vehicle before adding insurance.")
            else:
                vehicle_options = {f"{v['brand']} {v['model']} ({v['registration_no']})": v["vehicle_id"] for v in vehicles}
                selected_v = st.selectbox("Select Vehicle", list(vehicle_options.keys()))

                with st.form("add_insurance_form"):
                    policy_num = st.text_input("Policy Number")
                    provider = st.text_input("Insurance Company")
                    s_date = st.date_input("Start Date", value=date.today())
                    e_date = st.date_input("End Date", value=date.today())
                    premium = st.number_input("Premium Amount", min_value=0.0, value=500.0)
                    pol_status = st.selectbox("Status", ["Active", "Pending", "Expired"])
                    ins_btn = st.form_submit_button("Submit Policy")

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

    elif choice == "Service Records":
        st.header("🔧 Service Records")
        tab_list, tab_add = st.tabs(["View Records", "Log Maintenance"])

        with tab_list:
            records = api_request("GET", "/service-records/")
            show_table(records, "No service records found.")

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
                    srv_date = st.date_input("Service Date", value=date.today())
                    srv_type = st.text_input("Service Type (e.g. 50k Inspection, Brake Service)")
                    srv_desc = st.text_area("Description")
                    odometer = st.number_input("Odometer Reading", min_value=0, value=25000)
                    cost = st.number_input("Service Cost", min_value=0.0, value=150.0)
                    srv_status = st.selectbox("Status", ["Completed", "In Progress", "Scheduled"])
                    srv_btn = st.form_submit_button("Log Record")

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

    elif choice == "Vehicle Parts":
        st.header("⚙️ Vehicle Parts")
        parts = api_request("GET", "/vehicle-parts/")
        show_table(parts, "No parts found for your service records.")

    elif choice == "Service Centers":
        st.header("🏬 Service Centers")
        centers = api_request("GET", "/service-centers/")
        show_table(centers, "No service centers found.")

        if st.session_state.user_role == "admin":
            st.subheader("Admin: Register New Service Center")
            with st.form("admin_center_form"):
                c_name = st.text_input("Center Name")
                c_phone = st.text_input("Phone")
                c_email = st.text_input("Email")
                c_addr = st.text_area("Address")
                c_city = st.text_input("City")
                c_rating = st.number_input("Rating (0.0 to 5.0)", min_value=0.0, max_value=5.0, value=4.5, step=0.1)
                submit_center = st.form_submit_button("Add Service Center")

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

    elif choice == "Reports":
        st.header("📊 Analytical Reports")
        rep_type = st.selectbox(
            "Select Report",
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
        show_table(data)


if st.session_state.access_token is None:
    login_page()
else:
    main_app()
