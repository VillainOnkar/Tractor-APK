import requests
import json
from datetime import datetime

# Firebase URL
BASE_URL = "https://tractor-app-data-default-rtdb.asia-southeast1.firebasedatabase.app"

def get_safe_email(email):
    """Firebase keys mein '.' allowed nahi hai, isliye replace kar rahe hain"""
    return email.replace(".", "_")

def create_db():
    """Cloud mein table banane ki zarurat nahi hoti, bas import error na aaye isliye empty rakha hai"""
    pass

# ================= AUTH FUNCTIONS =================

def register_user(email, username, password, full_name, phone, address):
    s_email = get_safe_email(email)
    
    data = {
        "email": email,
        "username": username.strip().lower(),
        "password": password,
        "full_name": full_name,
        "phone": phone,
        "address": address,
        "is_verified": False 
    }
    
    try:
        # Email check pehle hi Auth handle kar lega, par DB mein bhi check karna achha hai
        url = f"{BASE_URL}/users/{s_email}.json"
        requests.put(url, json=data)
        return True, "Account Created!"
    except Exception as e:
        return False, f"Network Error: {e}"

# 3. Verify User: Isme hum check karenge ki password sahi hai ya nahi
def verify_user(email, p):
    safe_em = get_safe_email(email.strip().lower())
    try:
        # Seedha us user ka data uthayein (Faster Method)
        user_data = requests.get(f"{BASE_URL}/users/{safe_em}.json").json()
        
        if user_data:
            # Password check karein
            if str(user_data.get('password')) == str(p):
                # SUCCESS: Yahan hum is_verified ko True kar sakte hain kyunki 
                # ye function tabhi call hota hai jab Firebase Auth verify kar leta hai
                if not user_data.get('is_verified'):
                    requests.patch(f"{BASE_URL}/users/{safe_em}.json", json={"is_verified": True})
                
                return user_data
        return None
    except Exception as e:
        print(f"Verify Error: {e}")
        return None
    
def get_email_from_username(username):
    import requests
    try:
        # Saare users fetch karke username match karein
        all_users = requests.get(f"{BASE_URL}/users.json").json()
        if all_users:
            for safe_email, data in all_users.items():
                if data.get('username') == username.lower():
                    return data.get('email')
        return None
    except:
        return None
# ================= ALL APP FUNCTIONS =================

# --- Fuel ---
def add_fuel(user_email, date, station, liters, rate, total):
    safe_email = get_safe_email(user_email)
    data = {
        "date": date, "station": station, "liters": liters, 
        "rate": rate, "total": total
    }
    requests.post(f"{BASE_URL}/fuel_records/{safe_email}.json", json=data)

def get_recent_fuel(user_email):
    safe_email = get_safe_email(user_email)
    res = requests.get(f"{BASE_URL}/fuel_records/{safe_email}.json").json()
    if not res: return []
    # SQL format return: date, station, liters, total
    return [[v['date'], v['station'], v['liters'], v['total']] for v in res.values()][-10:]

# --- Maintenance ---
def add_maintenance(user_email, date, work, cost, next_date):
    try:
        safe_email = get_safe_email(user_email)
        data = {
            "date": date, "work_type": work, "cost": cost, 
            "next_service_date": next_date, "is_dismissed": 0
        }
        requests.post(f"{BASE_URL}/maintenance_records/{safe_email}.json", json=data)
        return True
    except:
        return False

def get_all_upcoming_reminders(user_email):
    safe_email = get_safe_email(user_email)
    res = requests.get(f"{BASE_URL}/maintenance_records/{safe_email}.json").json()
    if not res: return []
    # SQL format return: id, work_type, next_service_date
    return [[k, v['work_type'], v['next_service_date']] for k, v in res.items() if v.get('is_dismissed') == 0]

# --- Customers ---
def add_customer_work(user_email, name, village, phone, work_type, area, rate, total, paid, pending, date):
    safe_email = get_safe_email(user_email)
    data = {
        "name": name, "village": village, "phone": phone, "work_type": work_type,
        "area": area, "rate": rate, "total_amount": total, "paid_amount": paid,
        "pending_amount": pending, "date": date
    }
    requests.post(f"{BASE_URL}/customer_jobs/{safe_email}.json", json=data)

def fetch_all_customers(user_email):
    # Firebase Safe Email
    safe_email = get_safe_email(user_email)
    url = f"{BASE_URL}/customer_jobs/{safe_email}.json"
    
    try:
        res = requests.get(url).json()
        if not res:
            return []
        
        records = []
        for c_id, data in res.items():
            # Hum dictionary bhejenge taaki main.py mein galti na ho
            records.append({
                'id': c_id,
                'name': data.get('name', 'N/A'),
                'village': data.get('village', 'N/A'),
                'pending_amount': data.get('pending_amount', 0)
            })
        return records
    except Exception as e:
        print(f"Database Fetch Error: {e}")
        return []
        
def delete_customer_from_db(cust_id, user_email):
    # Firebase mein path ke liye email lagta hai
    safe_email = get_safe_email(user_email)
    requests.delete(f"{BASE_URL}/customer_jobs/{safe_email}/{cust_id}.json")
    return True

# --- Drivers ---
def save_driver_to_db(data):
    try:
        user_email = data.get('email')
        safe_email = get_safe_email(user_email)
        total = float(data.get('total', 0))
        paid = float(data.get('paid', 0))
        
        payload = {
            "name": data['name'], "phone": data['phone'], "address": data['addr'],
            "work_done": data['work'], "work_location": data['loc'],
            "total_amount": total, "paid_amount": paid, "pending_balance": total - paid
        }
        requests.post(f"{BASE_URL}/drivers/{safe_email}.json", json=payload)
        return True, "Driver Saved!"
    except Exception as e:
        return False, str(e)

# --- Reports ---
# --- Naya Function: Har payment ki alag entry ke liye ---
# 1. Income Transaction function ko check karein
def add_income_transaction(user_email, cust_name, amount, manual_date):
    safe_email = get_safe_email(user_email)
    payload = {
        "customer_name": cust_name,
        "amount_received": float(amount), # Is naam ka dhayan rakhein
        "date": manual_date,
        "timestamp": datetime.now().timestamp()
    }
    url = f"{BASE_URL}/daily_income/{safe_email}.json"
    requests.post(url, json=payload)

# 2. Report function ko sahi folder (daily_income) par set karein
def get_filtered_report(user_email, target_date=None):
    safe_email = get_safe_email(user_email)
    try:
        # Folder ka naam 'daily_income' hona chahiye
        inc_res = requests.get(f"{BASE_URL}/daily_income/{safe_email}.json").json() or {}
        total_income = 0.0
        
        for trans in inc_res.values():
            val = float(trans.get('amount_received', 0)) # Sahi key: 'amount_received'
            if target_date:
                if trans.get('date') == target_date:
                    total_income += val
            else:
                total_income += val

        # Expenses (Fuel + Maintenance)
        fuel_res = requests.get(f"{BASE_URL}/fuel_records/{safe_email}.json").json() or {}
        total_fuel = sum(float(v.get('total', 0)) for v in fuel_res.values())

        maint_res = requests.get(f"{BASE_URL}/maintenance_records/{safe_email}.json").json() or {}
        total_maint = sum(float(v.get('cost', 0)) for v in maint_res.values())

        return {
            "income": total_income,
            "fuel": total_fuel,
            "maintenance": total_maint,
            "profit": total_income - (total_fuel + total_maint)
        }
    except Exception as e:
        print(f"Report Error: {e}")
        return {"income": 0, "fuel": 0, "maintenance": 0, "profit": 0}