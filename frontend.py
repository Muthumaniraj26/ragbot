import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:8000"
st.set_page_config(page_title="Local Service AI Hub", layout="wide")

# Persistent Session state tracking
if "token" not in st.session_state: st.session_state.token = None
if "username" not in st.session_state: st.session_state.username = None

# Inject Custom Layout CSS classes
st.markdown("""
    <style>
    .premium-card { background-color: #1E293B; border-radius: 12px; padding: 20px; border-left: 6px solid #F59E0B; margin-bottom: 12px; color: white;}
    .scraped-card { background-color: #0F172A; border-radius: 12px; padding: 20px; border-left: 6px solid #3B82F6; margin-bottom: 12px; color: #E2E8F0;}
    .review-bubble { background-color: #334155; padding: 10px; border-radius: 6px; margin-top: 5px; color: white;}
    </style>
""", unsafe_allow_html=True)

portal = st.sidebar.selectbox("Navigation Portals", ["Customer Marketplace", "Partner Dashboard and Login"])

# ----------------- CUSTOMER MARKETPLACE -----------------
if portal == "Customer Marketplace":
    st.title("AI Trade Matching Core")
    st.caption("Describe your issue naturally. The system parses partner registries and returns live web directory crawl mechanics.")
    
    # Registration sub-expander for customers
    with st.expander("Customer Identity Registration"):
        cust_u = st.text_input("Choose Username", key="c_reg_u")
        cust_p = st.text_input("Choose Password", type="password", key="c_reg_p")
        cust_n = st.text_input("Full Display Name", key="c_reg_n")
        cust_l = st.text_input("Location Area", key="c_reg_l")
        if st.button("Register Customer Profile"):
            if cust_u and cust_p and cust_n and cust_l:
                c_payload = {"username": cust_u, "password": cust_p, "name": cust_n, "location": cust_l}
                c_res = requests.post(f"{BASE_URL}/register/customer", json=c_payload)
                if c_res.status_code == 200:
                    st.success("Customer profile registered successfully.")
                else:
                    st.error(c_res.json().get("detail", "Registration encounter error."))
            else:
                st.warning("All entry variables required.")

    st.write("---")
    search_q = st.text_input("Enter required trade service or issue description:", placeholder="e.g., Leaking pressure line connection behind my wall setup")
    
    if st.button("Search Marketplaces", type="primary"):
        if search_q:
            with st.spinner("Analyzing marketplace index layers locally..."):
                try:
                    res = requests.post(f"{BASE_URL}/search", json={"customer_query": search_q})
                    if res.status_code == 200:
                        data = res.json()
                        
                        col_left, col_right = st.columns(2)
                        
                        with col_left:
                            st.subheader("Premium Handymen (Internal Verified)")
                            if data["premium"]:
                                for worker in data["premium"]:
                                    st.markdown(f"""
                                        <div class="premium-card">
                                            <h3>{worker['name']} — Rating: {worker['rating']} / 5.0</h3>
                                            <p><b>Specialization Sector:</b> {worker['profession'].upper()}</p>
                                            <p><b>Address:</b> {worker['address']}</p>
                                            <p><b>Expert Profile Summary:</b> {worker['bio']}</p>
                                            <p>Phone: {worker['phone']} | Email Address: {worker['email']}</p>
                                        </div>
                                    """, unsafe_allow_html=True)
                                    
                                    act_c1, act_c2 = st.columns(2)
                                    with act_c1: st.link_button("Call Partner", f"tel:{worker['phone']}")
                                    with act_c2: st.link_button("Dispatch Email", f"mailto:{worker['email']}")
                                    
                                    with st.expander(f"View Ratings and Activity Comments for {worker['name']}"):
                                        rev_res = requests.get(f"{BASE_URL}/reviews/{worker['username']}").json()
                                        if rev_res:
                                            for r in rev_res:
                                                st.markdown(f"<div class='review-bubble'><b>{r['customer_name']}</b> (Rating: {r['rating']}/5) at <i>{r['timestamp']}</i>:<br/>\"{r['comment']}\"</div>", unsafe_allow_html=True)
                                        else:
                                            st.caption("No internal performance remarks submitted yet.")
                                        
                                        st.write("---")
                                        with st.form(key=f"f_{worker['username']}"):
                                            st.markdown("##### Log Feedback Review")
                                            name = st.text_input("Customer Name Reference", key=f"n_{worker['username']}")
                                            score = st.slider("Quality Score", 1, 5, 5, key=f"s_{worker['username']}")
                                            comm = st.text_area("Review Observations", key=f"c_{worker['username']}")
                                            if st.form_submit_button("Publish Public Review"):
                                                if name and comm:
                                                    rev_payload = {"worker_username": worker['username'], "customer_name": name, "rating": score, "comment": comm}
                                                    requests.post(f"{BASE_URL}/submit-review", json=rev_payload)
                                                    st.success("Review logged. Re-run search query to refresh views.")
                                                    st.rerun()
                                                else:
                                                    st.warning("Please fill out name and comment fields.")
                                    st.write("###")
                            else:
                                st.info("No verified platform workers match this description yet.")
                                
                        with col_right:
                            st.subheader("Public Directory Listings (Web Scraped)")
                            if data["scraped"]:
                                for idx, worker in enumerate(data["scraped"]):
                                    st.markdown(f"""
                                        <div class="scraped-card">
                                            <h3>{worker['name']} — Web Rating: {worker['online_rating']} / 5.0</h3>
                                            <p><b>Extracted Address:</b> {worker['address']}</p>
                                            <p><b>Business Context Snippet:</b> {worker['bio']}</p>
                                            <p>Phone: {worker['phone']} | Email: {worker['email']}</p>
                                        </div>
                                    """, unsafe_allow_html=True)
                                    
                                    s_c1, s_c2 = st.columns(2)
                                    with s_c1: st.link_button("Call Listing", f"tel:{worker['phone']}")
                                    with s_c2: st.link_button("Open Source Search Engine", "https://duckduckgo.com")
                            else:
                                st.info("No external listings scraped.")
                    else:
                        st.error("System backend refused response execution processing.")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot interface with Backend API server. Ensure backend instance script execution remains active.")
        else:
            st.warning("Please fill in search target definitions before query execution.")

# ----------------- PARTNER DASHBOARD PORTAL -----------------
elif portal == "Partner Dashboard and Login":
    if not st.session_state.token:
        st.title("Partner Desk Portal")
        tab1, tab2 = st.tabs(["Secure Login", "Create Partner Profile"])
        
        with tab1:
            st.subheader("Account Login")
            lin_u = st.text_input("Username ID")
            lin_p = st.text_input("Password ID", type="password")
            if st.button("Authenticate into Dashboard"):
                res = requests.post(f"{BASE_URL}/login", json={"username": lin_u, "password": lin_p, "role": "worker"})
                if res.status_code == 200:
                    st.session_state.token = res.json()["token"]
                    st.session_state.username = res.json()["username"]
                    st.success("Authorized successfully.")
                    st.rerun()
                else: 
                    st.error("Access denied. Please check your credentials.")
                
        with tab2:
            st.subheader("Registration Pipeline")
            with st.form("reg_form"):
                u = st.text_input("Profile Handle Username")
                p = st.text_input("Profile Password", type="password")
                n = st.text_input("Legal Trader or Business Name")
                prof = st.selectbox("Trade Core Category", ["plumber", "electrician", "carpenter", "hvac"])
                ph = st.text_input("Phone Number")
                em = st.text_input("Business Email")
                addr = st.text_input("Workshop or Operating Physical Address")
                bio = st.text_area("AI Matcher Bio (Describe tools, equipment, and specialties)")
                
                if st.form_submit_button("Submit Registry Profile"):
                    if u and p and n and ph and em and addr and bio:
                        payload = {"username": u, "password": p, "name": n, "profession": prof, "phone": ph, "email": em, "address": addr, "bio": bio}
                        reg_res = requests.post(f"{BASE_URL}/register/worker", json=payload)
                        if reg_res.status_code == 200: 
                            st.success("Registered. Move over to the Secure Login tab to enter.")
                        else: 
                            st.error(reg_res.json().get("detail", "Registration failure."))
                    else:
                        st.error("All structural registration fields must be completed.")
    else:
        st.title(f"Active Management Desk: {st.session_state.username}")
        if st.button("Log Out and Disconnect"):
            st.session_state.token = None
            st.session_state.username = None
            st.rerun()
            
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        profile_res = requests.get(f"{BASE_URL}/worker/profile", headers=headers)
        
        # Guard checking against structural string exceptions 
        if profile_res.status_code == 200:
            profile = profile_res.json()
            st.metric("Your Dynamic User Score", f"Rating: {profile['rating']} / 5.0")
            st.write(f"**Business Address:** {profile['address']}")
            st.write(f"**Indexed Capabilities:** {profile['bio']}")
        else:
            st.error(f"Failed to load profile. Backend error status: {profile_res.status_code}")