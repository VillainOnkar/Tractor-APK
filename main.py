from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.animation import Animation
from kivymd.uix.screen import MDScreen,Screen
from kivy.core.window import Window
from kivymd.toast import toast
from kivymd.uix.list import TwoLineListItem
from kivymd.uix.list import OneLineListItem, TwoLineListItem
from kivymd.uix.pickers import MDDatePicker
from datetime import datetime
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import ThreeLineListItem
from kivy.factory import Factory
from kivymd.app import MDApp
from kivy.uix.widget import Widget
import re  # Email validation ke liye
from kivy.metrics import dp
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.snackbar import Snackbar # Attractive messages ke liye
from kivy.graphics import Color, RoundedRectangle
from kivymd.uix.list import ThreeLineIconListItem, IconLeftWidget
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout

from datetime import datetime, date
import calendar
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivymd.uix.label import MDLabel
from threading import Thread          # Thread define karne ke liye
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.card import MDCardSwipe
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivy.properties import NumericProperty
#from fpdf import FPDF
import os
import sqlite3
from database import register_user,verify_user,create_db, add_fuel,get_recent_fuel,add_maintenance, get_all_upcoming_reminders,get_filtered_report,add_customer_work,save_driver_to_db,delete_customer_from_db,fetch_all_customers
Window.size = (360, 780)

class FuelScreen(MDScreen):
    pass
class MaintenanceScreen(MDScreen):
    pass
class ReportScreen(MDScreen):
    pass
class CustomerScreen(MDScreen):
    pass
class DriverScreen(MDScreen):
    pass
class CustomerListScreen(Screen):
    pass
class DriverListScreen(Screen):
    pass
class MaintListScreen(Screen):
    pass
class FuelListScreen(Screen):
    pass
class FinanceScreen(MDScreen):
    pass
class SwipeListItem(MDCardSwipe):
    text = StringProperty()
    secondary_text = StringProperty()
    tertiary_text = StringProperty()
    text_color = ListProperty([0, 0, 0, 1])
    icon = StringProperty("bell")
    record_id = NumericProperty()

class SignupScreen(Screen):
    pass
class LoginScreen(Screen):
    pass
class ProfileScreen(Screen):
    pass



class TractorApp(MDApp):
    total_income = NumericProperty(0)
    fuel_expense = NumericProperty(0)
    maint_expense = NumericProperty(0)
    net_profit = NumericProperty(0)
    current_start_date = ""
    current_end_date = ""
    alert_text = StringProperty("Calculating...")
    alert_color = ListProperty([1, 1, 1, 1])
    user_email = StringProperty("") # Yeh line zaroori hai
    user_full_name = StringProperty("User")
    user_email = ""
    

    def build(self):
        create_db()
        

        self.theme_cls.primary_palette = "Green"
        Builder.load_file("fuel.kv") 
        Builder.load_file("maintenance.kv")
        Builder.load_file("reports.kv")
        Builder.load_file("customer.kv")
        Builder.load_file("driver.kv")
        Builder.load_file("customer_list.kv")
        Builder.load_file("driver_list.kv")
        Builder.load_file("maint_list.kv")
        Builder.load_file("fuel_list.kv")
        Builder.load_file("finance.kv")
        Builder.load_file("login.kv")
        Builder.load_file("profile.kv") 

        self.gui = Builder.load_file("dashboard.kv")
        
        # YAHAN BADLAV KAREIN:
        # Purana: self.gui.ids.screen_manager.current = "signup"
        self.gui.ids.screen_manager.current = "login"  # Ab pehle login dikhega
        
        return self.gui
    
    def change_screen(self, screen_name):
        # 1. Pehle menu hide karein taaki touch leak na ho
        self.hide_menu() 
        self.load_profile_data()
        self.update_dashboard_counts()
        # 2. Phir screen badlein
        if 'screen_manager' in self.root.ids:
            self.root.ids.screen_manager.current = screen_name
        else:
            for child in self.root.children:
                if hasattr(child, 'ids') and 'screen_manager' in child.ids:
                    child.ids.screen_manager.current = screen_name
                    break

    def toggle_menu(self):
        menu = self.root.ids.side_menu
        if menu.x < 0:
            Animation(x=0, duration=0.25).start(menu)
        else:
            Animation(x=-menu.width, duration=0.25).start(menu)

    def hide_menu(self):
        menu = self.root.ids.side_menu
        Animation(x=-menu.width, duration=0.25).start(menu)
    
    """def show_msg(self, text, msg_type="info"):
        from kivymd.uix.snackbar import Snackbar
        from kivy.metrics import dp

        # Colors setup (Professional Shades)
        if msg_type == "error":
            bg = (0.8, 0.1, 0.1, 1)    # Soft Red
        elif msg_type == "success":
            bg = (0.1, 0.5, 0.2, 1)    # Forest Green
        else:
            bg = (0.1, 0.4, 0.7, 1)    # Steel Blue

        full_text = f"{text}"

        # Sirf wahi properties use karenge jo aapki list mein 'Valid' hain
        snack = Snackbar(
            text=full_text,
            bg_color=bg,
            duration=3,
            radius=[dp(10), dp(10), dp(10), dp(10)], # Aapki list mein 'radius' valid hai
            elevation=4
        )
        # Font size thoda bada dikhane ke liye (agar valid ho)
        snack.font_size = "12sp" 
        
        snack.open()"""
    def show_msg(self, text, msg_type="info"):
         

        # Colors setup based on message type
        if msg_type == "error":
            bg = (0.8, 0.1, 0.1, 1)    # Red
        elif msg_type == "success":
            bg = (0.1, 0.5, 0.2, 1)    # Green
        else:
            bg = (0.1, 0.4, 0.7, 1)    # Blue

        # KivyMD 1.2.0 compatibility
        # Hum 'text' argument use nahi karenge kyunki aapki property list mein woh missing tha
        snack = Snackbar(
            bg_color=bg,
            duration=3,
            radius=[dp(10), dp(10), dp(10), dp(10)],
            elevation=4
        )
        
        # Text set karne ka manual tarika jo 1.2.0 mein crash nahi karega
        snack.text = text 
        
        snack.open()
    #=========================================Customer==========================================================
    # ================= CUSTOMER LOGIC =================

    def calculate_cust_total(self):
        screen = self.root.ids.screen_manager.get_screen('customer')
        try:
            area = float(screen.ids.work_area.text or 0)
            rate = float(screen.ids.work_rate.text or 0)
            total = area * rate
            screen.ids.total_amt.text = str(total)
        except ValueError:
            pass

    def save_customer_work(self):
        if not hasattr(self, 'user_email') or not self.user_email:
            self.show_msg("Pehle login karein!", "error")
            return

        screen = self.root.ids.screen_manager.get_screen('customer')
        import requests
        from database import BASE_URL, get_safe_email, add_income_transaction
        from datetime import datetime

        # --- DATA COLLECTION (Simple Typing) ---
        name = screen.ids.cust_name.text.strip()
        village = screen.ids.cust_village.text.strip()
        phone = screen.ids.cust_phone.text.strip()
        work = screen.ids.work_type.text.strip()
        
        # Date field se text uthana (Jaise phone number uthate hain)
        manual_date = screen.ids.manual_date_input.text.strip()
        
        # Agar khali chhoda toh aaj ki date auto aa jayegi
        if not manual_date:
            manual_date = datetime.now().strftime("%d-%m-%Y")

        try:
            area = float(screen.ids.work_area.text or 0)
            rate = float(screen.ids.work_rate.text or 0)
            total = float(screen.ids.total_amt.text or 0)
            paid = float(screen.ids.paid_amt.text or 0)
            pending = total - paid
        except ValueError:
            self.show_msg("Numbers sahi se bharein!", "error")
            return

        if not name:
            self.show_msg("Naam zaroori hai!", "error")
            return

        try:
            s_email = get_safe_email(self.user_email)
            payload = {
                "name": name, "village": village, "phone": phone,
                "work_type": work, "area": area, "rate": rate,
                "total_amount": total, "paid_amount": paid,
                "pending_amount": pending, "date": manual_date 
            }
            
            # 1. Main Job Save Karein
            requests.post(f"{BASE_URL}/customer_jobs/{s_email}.json", json=payload)
            
            # 2. Income Table mein record karein (Reports ke liye)
            if paid > 0:
                # database.py ka function call
                add_income_transaction(self.user_email, name, paid, manual_date)

            self.show_msg(f"Data Save Ho Gaya!", "success")
            
            # --- UI CLEANUP (Errors hatane ke liye) ---
            
            # Note: load_customer_list_data aur entries ko yahan se hata diya hai 
            # kyunki humne history screen se uda di hai.
            self.clear_customer_fields(screen)
            # Purane IDs jo delete ho chuke hain unhe call NA karein
            self.update_dashboard_counts()
        except Exception as e:
            print(f"Save Error: {e}")
            self.show_msg("Data save nahi hua!", "error")

    def load_customer_list_data(self):
        if not hasattr(self, 'user_email') or not self.user_email:
            return
            
        try:
            screen = self.root.ids.screen_manager.get_screen('customer_list')
            container = screen.ids.customer_list_container
            container.clear_widgets()
            
            from database import fetch_all_customers
            records = fetch_all_customers(self.user_email)
            
            if not records:
                from kivymd.uix.label import MDLabel
                container.add_widget(MDLabel(text="Koi record nahi mila", halign="center"))
                return

            for row in records:
                # Factory card banana
                item = Factory.CustomerRowCard()
                
                # Dictionary keys use karein - Yeh hai permanent solution
                item.cust_id = str(row['id'])
                item.name = str(row['name'])
                item.village = str(row['village'])
                
                try:
                    pending_val = float(row['pending_amount'])
                except:
                    pending_val = 0.0

                # AAPKA SAME LOGIC
                if pending_val <= 0:
                    item.amount = "Full Paid"
                    item.status_text = "Hisaab Clear"
                    item.amount_color = [0, 0.6, 0, 1]  # Green
                else:
                    item.amount = f"₹ {int(pending_val)}"
                    item.status_text = "Pending"
                    item.amount_color = [1, 0, 0, 1]  # Red
                
                # Click event
                item.bind(on_release=lambda x, cid=row['id']: self.show_customer_details(cid))
                
                container.add_widget(item)
                
        except Exception as e:
            print(f"Final List Error: {e}")
            self.show_msg("Data formatting error!", "error")

    def update_dashboard_counts(self):
        if not hasattr(self, 'user_email') or not self.user_email:
            return

        import requests
        from database import BASE_URL, get_safe_email
        safe_email = get_safe_email(self.user_email)
        
        try:
            # Firebase se data fetch karna
            cust_data = requests.get(f"{BASE_URL}/customer_jobs/{safe_email}.json").json() or {}
            driver_data = requests.get(f"{BASE_URL}/drivers/{safe_email}.json").json() or {}
            fuel_data = requests.get(f"{BASE_URL}/fuel_records/{safe_email}.json").json() or {}
            maint_data = requests.get(f"{BASE_URL}/maintenance_records/{safe_email}.json").json() or {}

            # 1. Customers Count
            self.root.ids.dash_cust_count.text = str(len(cust_data))
            
            # 2. Driver Count
            self.root.ids.dash_driver_count.text = str(len(driver_data))

            # 3. Fuel Total
            fuel_total = sum(float(v.get('total', 0)) for v in fuel_data.values())
            self.root.ids.dash_fuel_cost.text = f"₹ {fuel_total:,.0f}"

            # 4. Maintenance Total
            maint_total = sum(float(v.get('cost', 0)) for v in maint_data.values())
            self.root.ids.dash_maint_cost.text = f"₹ {maint_total:,.0f}"

            # 5. Due amount
            due_total = sum(float(v.get('pending_amount', 0)) for v in cust_data.values())
            self.root.ids.dash_due_payment.text = f"₹ {due_total:,.0f}"

        except Exception as e:
            print(f"Dashboard Update Error: {e}")
                
    def clear_customer_fields(self, screen):
        ids_to_clear = ['cust_name', 'cust_village', 'cust_phone', 'work_type', 
                        'work_area', 'work_rate', 'total_amt', 'paid_amt']
        for id_name in ids_to_clear:
            if id_name in screen.ids:
                screen.ids[id_name].text = ""


    # ================= SEARCH / FILTER LOGIC =================
    def filter_customers(self, query):
        if not hasattr(self, 'user_email') or not self.user_email: return
        query = query.strip().lower()
        
        screen = self.root.ids.screen_manager.get_screen('customer_list')
        container = screen.ids.customer_list_container
        container.clear_widgets()
        
        from database import BASE_URL, get_safe_email
        import requests
        s_email = get_safe_email(self.user_email)
        
        try:
            res = requests.get(f"{BASE_URL}/customer_jobs/{s_email}.json").json()
            if not res: return

            for c_id, data in res.items():
                name = str(data.get('name', '')).lower()
                village = str(data.get('village', '')).lower()
                work = str(data.get('work_type', '')).lower()
                date = str(data.get('date', '')).lower()
                
                try:
                    pending_val = float(data.get('pending_amount', 0))
                except: pending_val = 0.0
                
                status = "full paid" if pending_val <= 0 else "pending"
                
                # Search logic check
                if (query in name or query in village or query in status or 
                    query in work or query in date):
                    
                    from kivy.factory import Factory
                    item = Factory.CustomerRowCard()
                    item.cust_id = str(c_id)
                    item.name = str(data.get('name', ''))
                    item.village = str(data.get('village', ''))
                    
                    if pending_val <= 0:
                        item.amount = "Full Paid"
                        item.status_text = "Hisaab Clear"
                        item.amount_color = [0, 0.6, 0, 1]
                    else:
                        item.amount = f"₹ {int(pending_val)}"
                        item.status_text = "Pending"
                        item.amount_color = [1, 0, 0, 1]
                    
                    container.add_widget(item)
        except Exception as e:
            print(f"Filter Error: {e}")

    
    # ================= FULL RECORD VIEW =================
    def show_customer_details(self, cust_id):
        from database import BASE_URL, get_safe_email
        import requests
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDFlatButton
        
        # 1. PEHLE CHECK KAREIN: Agar pehle se koi dialog open hai, to naya mat kholo
        if hasattr(self, 'cust_detail_dialog') and self.cust_detail_dialog:
            try:
                # Agar dialog memory mein hai, to use pehle dismiss karo safety ke liye
                self.cust_detail_dialog.dismiss()
            except:
                pass

        try:
            if not self.user_email:
                self.show_msg("Session expired! Login again.", "error")
                return

            s_email = get_safe_email(self.user_email)
            url = f"{BASE_URL}/customer_jobs/{s_email}/{cust_id}.json"
            row = requests.get(url).json()

            if row:
                details = (
                    f"Name: {row.get('name', '')}\n"
                    f"Village: {row.get('village', '')}\n"
                    f"Phone: {row.get('phone', '')}\n"
                    f"Work: {row.get('work_type', '')}\n"
                    f"Area: {row.get('area', 0)} Acre\n"
                    f"Rate: ₹{row.get('rate', 0)}\n"
                    f"Total: ₹{row.get('total_amount', 0)}\n"
                    f"Paid: ₹{row.get('paid_amount', 0)}\n"
                    f"Pending: ₹{row.get('pending_amount', 0)}\n"
                    f"Date: {row.get('date', '')}"
                )
                
                # 2. DIALOG BANAYEIN
                self.cust_detail_dialog = MDDialog(
                    title="Customer Full Record",
                    text=details,
                    auto_dismiss=False, # Isko False karein taaki user sirf button se band kare
                    buttons=[
                        MDFlatButton(
                            text="CLOSE", 
                            theme_text_color="Custom",
                            on_release=self.close_cust_dialog # Alag function call karein
                        )
                    ]
                )
                self.cust_detail_dialog.open()
                
        except Exception as e:
            print(f"Details Error: {e}")
            self.show_msg("Details load nahi ho saki", "error")

    # 3. Naya Helper Function Dialog Band Karne Ke Liye
    def close_cust_dialog(self, *args):
        if self.cust_detail_dialog:
            self.cust_detail_dialog.dismiss()
            self.cust_detail_dialog = None # Memory se clear karein
    # ================= PAYMENT UPDATE DIALOG =================
    def edit_customer_dialog(self, cust_id):
        self.editing_id = cust_id 
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.textfield import MDTextField
        from kivymd.uix.button import MDRaisedButton, MDFlatButton
        from kivymd.uix.boxlayout import MDBoxLayout

        self.edit_input = MDTextField(
            hint_text="Kitna paisa jama kiya?",
            helper_text="Sirf number likhein (e.g. 500)",
            helper_text_mode="on_focus",
            input_filter="float"
        )

        self.dialog = MDDialog(
            title="Update Payment",
            type="custom",
            content_cls=MDBoxLayout(
                self.edit_input,
                orientation="vertical",
                adaptive_height=True,
                padding=[0, "10dp", 0, 0]
            ),
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="SAVE", on_release=lambda x: self.save_edit()),
            ],
        )
        self.dialog.open()

    # ================= SAVE EDIT LOGIC =================
    def save_edit(self):
        """Ye function payment update karta hai aur har entry ko alag record karta hai"""
        try:
            # 1. Input ko saaf karein (Spaces aur ₹ ka nishan hatayein)
            raw_text = self.edit_input.text.strip().replace("₹", "").replace(",", "")
            
            if not raw_text:
                self.show_msg("Paisa likhiye!", "error")
                return

            # Number mein convert karein
            added_payment = float(raw_text)
            
            from database import BASE_URL, get_safe_email, add_income_transaction
            import requests
            from datetime import datetime
            
            s_email = get_safe_email(self.user_email)
            url = f"{BASE_URL}/customer_jobs/{s_email}/{self.editing_id}.json"
            
            # Firebase se purana data fetch karein
            row = requests.get(url).json()
            
            if row:
                total_bill = float(row.get('total_amount', 0))
                old_paid = float(row.get('paid_amount', 0))
                cust_name = row.get('name', 'Unknown')
                
                # AAJ KI DATE: Manual date input field hai toh wahan se lein, 
                # nahi toh aaj ki date auto le lein
                aaj_ki_date = datetime.now().strftime("%d-%m-%Y")
                
                # Income record karein (database.py ke naya function ke hisab se)
                # Note: Check karein ki aapka function (email, name, amount, date) leta hai ya nahi
                add_income_transaction(self.user_email, cust_name, added_payment, aaj_ki_date)
                
                # Calculation
                updated_paid = old_paid + added_payment
                updated_pending = total_bill - updated_paid
                
                # Customer Job update karein
                payload = {
                    "paid_amount": updated_paid,
                    "pending_amount": updated_pending
                }
                requests.patch(url, json=payload)
                
                self.dialog.dismiss()
                
                # UI Refresh
                if hasattr(self, 'load_customer_list_data'):
                    self.load_customer_list_data()
                self.update_dashboard_counts()
                
                self.show_msg(f"₹{added_payment} Jama ho gaye!", "success")
            else:
                self.show_msg("Record nahi mila!", "error")
                
        except ValueError:
            # Yahan debug ke liye print lagayein taaki pata chale kya galat input aaya
            print(f"DEBUG: Galat input tha -> '{self.edit_input.text}'")
            self.show_msg("Sirf number likhein (e.g. 500)", "error")
        except Exception as e:
            print(f"Edit Error: {e}")
            self.show_msg("Server Error!", "error")
    
    # 1. Delete Confirm karne wala Dialog dikhana
    def confirm_delete(self, cust_id):
        self.deleting_cust_id = cust_id  # ID ko save karlein
        self.del_dialog = MDDialog(
            title="Delete Karein?",
            text="Kya aap sach mein is record ko delete karna chahte hain?",
            buttons=[
                MDFlatButton(
                    text="CANCEL", 
                    on_release=lambda x: self.del_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="DELETE", 
                    md_bg_color=(1, 0, 0, 1), # Red Color
                    on_release=lambda x: self.delete_customer_final()
                ),
            ],
        )
        self.del_dialog.open()

    # 2. Asliyat mein Firebase se delete karne wala function
    def delete_customer_final(self):
        self.del_dialog.dismiss()
        try:
            from database import delete_customer_from_db
            # Firebase se delete karein
            success = delete_customer_from_db(self.deleting_cust_id, self.user_email)
            
            if success:
                self.show_msg("Record Delete Ho Gaya!", "success")
                # List refresh karein
                self.load_customer_list_data()
                # Dashboard counts update karein
                self.update_dashboard_counts()
            else:
                self.show_msg("Delete nahi ho saka", "error")
        except Exception as e:
            print(f"Delete Error: {e}")
            self.show_msg("Database Error!", "error")
        
    #========================================= fuel =====================================================================
    # ================= FUEL LOGIC (SAME CALCULATIONS) =================
    def calculate_fuel_total(self):
        screen = self.root.ids.screen_manager.get_screen('fuel')
        try:
            # parseFloat jaisa logic taaki empty string par crash na ho
            liters = float(screen.ids.f_liters.text or 0)
            rate = float(screen.ids.f_rate.text or 0)
            total = liters * rate
            # Label update wahi formatting jo aapne di thi
            screen.ids.f_total_label.text = f"Total Amount: ₹ {total:.2f}"
        except ValueError:
            pass

    def save_fuel_entry(self):
        if not self.user_email:
            self.show_msg("Kripya pehle login karein!", "error")
            return

        screen = self.root.ids.screen_manager.get_screen('fuel')
        date = screen.ids.f_date.text
        station = screen.ids.f_station.text
        liters = screen.ids.f_liters.text
        rate = screen.ids.f_rate.text
        
        if all([date, liters, rate]):
            try:
                # Calculation Logic (Variable name 'total')
                total = float(liters) * float(rate)
                
                from database import add_fuel
                # database.py ko cloud mein save karne ke liye 6 arguments bhej rahe hain
                add_fuel(self.user_email, date, station, float(liters), float(rate), total)
                
                # Fields clear karna (Aapka logic)
                screen.ids.f_liters.text = ""
                screen.ids.f_rate.text = ""
                screen.ids.f_station.text = ""
                screen.ids.f_total_label.text = "Total Amount: ₹ 0.00"
                
                self.show_msg("Fuel record save ho gaya!", "success")
                self.update_history_list()
                self.update_dashboard_counts() 
            except ValueError:
                self.show_msg("Liters aur Rate sahi bharein!", "error")
        else:
            self.show_msg("Sabhi fields bharna zaroori hai!", "error")

    def update_history_list(self):
        """Firebase se recent fuel records lekar list mein dikhana"""
        if not self.user_email: 
            return

        try:
            screen = self.root.ids.screen_manager.get_screen('fuel')
            history_box = screen.ids.history_container
            history_box.clear_widgets() 
            
            from database import get_recent_fuel
            # Firebase se data list ke roop mein aayega
            data = get_recent_fuel(self.user_email)
            
            for row in data:
                # row structure: [Date, Station, Liters, Total]
                history_box.add_widget(
                    TwoLineListItem(
                        # Pehli line mein Date aur Station
                        text=f"Date: {row[0]} | Station: {row[1]}",
                        # Doosri line mein Diesel Quantity aur Paisa
                        secondary_text=f"Diesel: {row[2]}L | Total: ₹{row[3]}"
                    )
                )
        except Exception as e:
            print(f"Display Error: {e}")

     
    #============================================Maintance=================================================
    # ================= MAINTENANCE LOGIC =================
    def save_maintenance_entry(self):
        if not self.user_email:
            self.show_msg("Kripya pehle login karein!", "error")
            return

        try:
            # Maintenance screen se data uthana (Aapka logic)
            screen = self.root.ids.screen_manager.get_screen('maintenance')
            d = screen.ids.m_date.text.strip()
            w = screen.ids.m_type.text.strip()
            c = screen.ids.m_cost.text.strip()
            n = screen.ids.m_next_date.text.strip()

            # Validation (Same as yours)
            if not d or not w or not c:
                self.show_msg("Date, Kaam aur Kharcha bharna zaroori hai!", "error")
                return

            from database import add_maintenance
            # Firebase database mein 5 parameters bhej rahe hain
            success = add_maintenance(self.user_email, d, w, c, n)
            
            if success:
                self.show_msg("Maintenance Record Save Ho Gaya!", "success")
                # Fields ko khali karna
                screen.ids.m_date.text = ""
                screen.ids.m_type.text = ""
                screen.ids.m_cost.text = ""
                screen.ids.m_next_date.text = ""
                
                # UI aur Reminders update karna
                self.update_dashboard_counts()
                # self.start_reminder_thread() # Agar aapne thread define kiya hai
                self.update_maintenance_reminder()
                self.start_reminder_thread()
            else:
                self.show_msg("Database Error: Save nahi ho paya!", "error")

        except Exception as e:
            print(f"Save Error Details: {e}")
            self.show_msg("Technical Error! Kripya check karein.", "error")

    # ================= REMINDER LOGIC =================
    def update_maintenance_reminder(self):
        # 1. Security check
        if not self.user_email:
            return

        try:
            screen = self.root.ids.screen_manager.get_screen('maintenance')
            reminder_box = screen.ids.reminder_list
            reminder_box.clear_widgets()

            from database import get_all_upcoming_reminders
            # Firebase se login user ke specific reminders lana
            reminders = get_all_upcoming_reminders(self.user_email)
            
            if not reminders:
                reminder_box.add_widget(
                    OneLineListItem(text="Abhi koi naya reminder nahi hai")
                )
                return
            
            # 2. Loop logic (Same sequence: id, work_type, date)
            for r in reminders:
                m_id = r[0]        # Unique Firebase Key
                m_type = r[1]      # work_type
                m_date = r[2]      # next_service_date
                
                reminder_box.add_widget(
                    TwoLineListItem(
                        text=f"Service: {m_type}",
                        secondary_text=f"Due Date: {m_date}",
                        # Click logic same rakha hai
                        on_release=lambda x, mid=m_id: self.show_maintenance_details(mid)
                    )
                )
        except Exception as e:
            print(f"Reminder Update Error: {e}")

    def show_maintenance_details(self, mid):
        """Details dikhane ke liye helper function"""
        from database import BASE_URL, get_safe_email
        import requests
        try:
            s_email = get_safe_email(self.user_email)
            res = requests.get(f"{BASE_URL}/maintenance_records/{s_email}/{mid}.json").json()
            if res:
                details = (
                    f"Work: {res.get('work_type', '')}\n"
                    f"Date: {res.get('date', '')}\n"
                    f"Cost: ₹{res.get('cost', '')}\n"
                    f"Next Service: {res.get('next_service_date', 'N/A')}"
                )
                self.dialog = MDDialog(
                    title="Maintenance Detail",
                    text=details,
                    buttons=[MDFlatButton(text="CLOSE", on_release=lambda x: self.dialog.dismiss())]
                )
                self.dialog.open()
        except:
            self.show_msg("Detail nahi dikha sake", "error")     

    #=============================Report=================================================
    # ================= REPORTS LOGIC (FIREBASE INTEGRATED) =================
    def update_reports(self, start_date=None, end_date=None):
        if not self.user_email:
            self.show_msg("Pehle login karein!", "error")
            return

        from datetime import datetime
        import requests
        from database import BASE_URL, get_safe_email
        from kivymd.uix.list import ThreeLineIconListItem, IconLeftWidget

        # Default Date: Aaj ki
        if not start_date:
            start_date = datetime.now().strftime('%d-%m-%Y')
            end_date = start_date

        self.current_start_date = start_date
        self.current_end_date = end_date

        def to_iso(d_str):
            try:
                p = d_str.split('-')
                return f"{p[2]}-{p[1]}-{p[0]}"
            except: return "0000-00-00"

        s_iso, e_iso = to_iso(start_date), to_iso(end_date)
        s_email = get_safe_email(self.user_email)

        try:
            # 1. Fetch Data
            income_data = requests.get(f"{BASE_URL}/daily_income/{s_email}.json").json() or {}
            fuel_data = requests.get(f"{BASE_URL}/fuel_records/{s_email}.json").json() or {}
            maint_data = requests.get(f"{BASE_URL}/maintenance_records/{s_email}.json").json() or {}

            self.total_income = 0
            self.fuel_expense = 0
            self.maint_expense = 0
            combined_rows = []

            # Process Income
            for v in income_data.values():
                if 'date' in v:
                    row_iso = to_iso(v['date'])
                    if s_iso <= row_iso <= e_iso:
                        amt = float(v.get('amount_received', 0))
                        self.total_income += amt
                        combined_rows.append([v['date'], 'Income', amt, v.get('customer_name',''), row_iso])

            # Process Fuel
            for v in fuel_data.values():
                if 'date' in v:
                    row_iso = to_iso(v['date'])
                    if s_iso <= row_iso <= e_iso:
                        amt = float(v.get('total', 0))
                        self.fuel_expense += amt
                        combined_rows.append([v['date'], 'Fuel', amt, v.get('station',''), row_iso])

            # Process Maintenance
            for v in maint_data.values():
                if 'date' in v:
                    row_iso = to_iso(v['date'])
                    if s_iso <= row_iso <= e_iso:
                        amt = float(v.get('cost', 0))
                        self.maint_expense += amt
                        combined_rows.append([v['date'], 'Maint', amt, v.get('work_type',''), row_iso])

            self.net_profit = self.total_income - (self.fuel_expense + self.maint_expense)

            # 2. Update UI Labels
            screen = self.root.ids.screen_manager.get_screen('reports')
            screen.ids.total_income_label.text = f"₹ {self.total_income:,.0f}"
            screen.ids.total_expense_label.text = f"₹ {self.fuel_expense:,.0f}"
            screen.ids.maint_label.text = f"₹ {self.maint_expense:,.0f}"
            screen.ids.net_profit_label.text = f"₹ {self.net_profit:,.0f}"
            screen.ids.net_profit_label.text_color = (0, 1, 0, 1) if self.net_profit >= 0 else (1, 0, 0, 1)

            # 3. Update Activity Log
            history_list = screen.ids.report_history_list
            history_list.clear_widgets()
            combined_rows.sort(key=lambda x: x[4], reverse=True)

            for row in combined_rows:
                is_income = row[1] == 'Income'
                item = ThreeLineIconListItem(
                    text=f"{'Received' if is_income else 'Paid'}: ₹{row[2]}",
                    secondary_text=f"Date: {row[0]} | Type: {row[1]}",
                    tertiary_text=f"Details: {row[3]}"
                )
                icon_name = "arrow-up-bold" if is_income else "arrow-down-bold"
                icon_color = [0, 0.6, 0.2, 1] if is_income else [0.8, 0, 0, 1]
                item.add_widget(IconLeftWidget(icon=icon_name, theme_text_color="Custom", text_color=icon_color))
                history_list.add_widget(item)

        except Exception as e:
            print(f"Report Error: {e}")
            
    # ================= DATE FILTERING (DAY, MONTH, YEAR) =================
    def show_date_input(self):
        self.date_type_field = MDTextField(hint_text="DD-MM-YYYY (e.g. 12-01-2026)")
        self.date_input_dialog = MDDialog(
            title="Enter Date", type="custom", content_cls=self.date_type_field,
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda x: self.date_input_dialog.dismiss()),
                MDFlatButton(text="SHOW REPORT", on_release=lambda x: self.filter_by_day())
            ],
        )
        self.date_input_dialog.open()

    def filter_by_day(self):
        val = self.date_type_field.text.strip()
        self.date_input_dialog.dismiss()
        
        # Validation: Check karein ki DD-MM-YYYY format sahi hai
        if len(val) == 10 and val.count('-') == 2:
            try:
                # Sirf check karne ke liye ki date valid hai (e.g. 31-02-2024 na ho)
                from datetime import datetime
                datetime.strptime(val, '%d-%m-%Y')
                
                # Naya logic: update_reports ko wahi date start aur end mein bhejenge
                self.update_reports(val, val)
            except ValueError:
                self.show_msg("Galat Date hai! Sahi date bhariye.", "error")
        else:
            self.show_msg("Sahi format: DD-MM-YYYY (e.g. 14-01-2026)", "error")

    def show_month_input(self):
        self.month_field = MDTextField(hint_text="MM-YYYY (e.g. 01-2024)")
        self.dialog = MDDialog(
            title="Select Month", type="custom", content_cls=self.month_field,
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda x: self.dialog.dismiss()),
                MDFlatButton(text="SHOW REPORT", on_release=lambda x: self.filter_by_month())
            ],
        )
        self.dialog.open()

    def filter_by_month(self):
        val = self.month_field.text.strip()
        self.dialog.dismiss()
        if len(val) == 7:
            import calendar
            try:
                mm, yyyy = map(int, val.split('-'))
                last_day = calendar.monthrange(yyyy, mm)[1] # Mahine ka aakhri din nikalna
                self.update_reports(f"01-{val}", f"{last_day}-{val}")
            except:
                self.show_msg("Format: MM-YYYY", "error")
        else:
            self.show_msg("Sahi format: MM-YYYY","error")

    def show_year_input(self):
        self.year_field = MDTextField(hint_text="YYYY (e.g. 2024)")
        self.dialog = MDDialog(
            title="Select Year", type="custom", content_cls=self.year_field,
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda x: self.dialog.dismiss()),
                MDFlatButton(text="SHOW REPORT", on_release=lambda x: self.filter_by_year())
            ],
        )
        self.dialog.open()

    def filter_by_year(self):
        val = self.year_field.text.strip()
        self.dialog.dismiss()
        
        if len(val) == 4 and val.isdigit():
            # Poore saal ki range: 01-01 se 31-12 tak
            start_of_year = f"01-01-{val}"
            end_of_year = f"31-12-{val}"
            
            self.update_reports(start_of_year, end_of_year)
            self.show_msg(f"Saal {val} ki report taiyar hai", "success")
        else:
            self.show_msg("Sahi format: YYYY (e.g. 2026)", "error")
    # ================= PDF EXPORT LOGIC =================
    def export_to_pdf(self):
        if not self.user_email:
            self.show_msg("Reports dekhne ke liye Login karein!", "error")
            return
            
        try:
            from fpdf import FPDF
            import os
            from tkinter import filedialog, Tk
            from datetime import datetime
            import requests
            from database import BASE_URL, get_safe_email

            s_date = getattr(self, 'current_start_date', None) or datetime.now().strftime('%d-%m-%Y')
            e_date = getattr(self, 'current_end_date', None) or s_date

            # Folder Selection
            root = Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            selected_path = filedialog.askdirectory(title="Select Folder to Save Report")
            root.destroy()
            if not selected_path: return 

            # --- Naya Data Fetching (Screen wale logic ke jaisa) ---
            s_email = get_safe_email(self.user_email)
            def to_iso(d_str):
                p = d_str.split('-')
                return f"{p[2]}-{p[1]}-{p[0]}"
            
            s_iso, e_iso = to_iso(s_date), to_iso(e_date)
            
            # Data uthayenge (daily_income se)
            income_data = requests.get(f"{BASE_URL}/daily_income/{s_email}.json").json() or {}
            fuel_data = requests.get(f"{BASE_URL}/fuel_records/{s_email}.json").json() or {}
            maint_data = requests.get(f"{BASE_URL}/maintenance_records/{s_email}.json").json() or {}

            pdf_rows = []
            # Income rows
            for v in income_data.values():
                if 'date' in v and s_iso <= to_iso(v['date']) <= e_iso:
                    pdf_rows.append([v['date'], 'Income', v.get('customer_name','N/A'), float(v.get('amount_received',0)), to_iso(v['date'])])
            
            # Fuel & Maint rows... (wahi purana logic)
            for v in fuel_data.values():
                if 'date' in v and s_iso <= to_iso(v['date']) <= e_iso:
                    pdf_rows.append([v['date'], 'Fuel', v.get('station',''), float(v.get('total',0)), to_iso(v['date'])])
            
            for v in maint_data.values():
                if 'date' in v and s_iso <= to_iso(v['date']) <= e_iso:
                    pdf_rows.append([v['date'], 'Maint', v.get('work_type',''), float(v.get('cost',0)), to_iso(v['date'])])

            pdf_rows.sort(key=lambda x: x[4], reverse=True)

            # --- PDF Designing ---
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 20)
            pdf.cell(190, 15, "TRACTOR BUSINESS REPORT", ln=True, align='C')
            
            # Summary Section
            # --- SUMMARY SECTION (Ek ke niche ek) ---
            pdf.set_font("Arial", 'B', 12)
            pdf.set_fill_color(240, 240, 240)
            pdf.cell(190, 10, f" SUMMARY ({s_date} to {e_date})", 0, 1, 'L', True)
            
            pdf.set_font("Arial", '', 11)
            # Width 190 aur ln=1 karne se agli line niche se shuru hogi
            pdf.cell(190, 8, f"Total Income: Rs. {self.total_income}", ln=1)
            pdf.cell(190, 8, f"Total Fuel: Rs. {self.fuel_expense}", ln=1)
            pdf.cell(190, 8, f"Maintenance: Rs. {self.maint_expense}", ln=1)
            
            # Profit line thodi bold aur alag dikhegi
            pdf.ln(2) # Thoda extra space
            pdf.set_font("Arial", 'B', 11)
            pdf.cell(190, 8, f"NET PROFIT: Rs. {self.net_profit}", ln=1)
            pdf.ln(5)

            # Table Header
            pdf.set_fill_color(60, 60, 60); pdf.set_text_color(255, 255, 255)
            pdf.cell(30, 10, "Date", 1, 0, 'C', True)
            pdf.cell(30, 10, "Category", 1, 0, 'C', True)
            pdf.cell(90, 10, "Details", 1, 0, 'C', True)
            pdf.cell(40, 10, "Amount", 1, 1, 'C', True)

            # Table Data
            pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", '', 10)
            for row in pdf_rows:
                pdf.cell(30, 10, row[0], 1)
                pdf.cell(30, 10, row[1], 1)
                pdf.cell(90, 10, str(row[2])[:45], 1) # Detail agar lambi ho toh cut jaye
                pdf.cell(40, 10, f"Rs. {row[3]}", 1, 1, 'R')

            file_name = f"Report_{s_date.replace('-','_')}.pdf"
            full_path = os.path.join(selected_path, file_name)
            pdf.output(full_path)
            
            self.show_msg(f"✅ Report Save: {file_name}", "success")
            if os.name == 'nt': os.startfile(full_path)

        except Exception as e:
            print(f"PDF Error: {e}")
            self.show_msg("PDF generate nahi ho saka!", "error")








            
#==================================================driver===========================================================
    # ================= DRIVER SAVE LOGIC =================
    def process_new_driver(self):
        if not self.user_email:
            self.show_msg("Login zaroori hai!", "error")
            return

        try:
            sm = self.root.ids.screen_manager
            screen = sm.get_screen("driver")
            
            driver_data = {
                'email': self.user_email,
                'name': screen.ids.name_input.text.strip(),
                'phone': screen.ids.phone_input.text.strip(),
                'addr': screen.ids.address_input.text.strip(),
                'work': screen.ids.work_done.text.strip(),
                'loc': screen.ids.work_location.text.strip(),
                'total': screen.ids.total_to_pay.text or 0,
                'paid': screen.ids.amount_paid.text or 0
            }

            if not driver_data['name'] or not driver_data['phone']:
                self.show_msg("Driver ka naam aur phone bharein!", "error")
                return

            from database import save_driver_to_db
            success, message = save_driver_to_db(driver_data)
            
            if success:
                self.show_msg(message, "success")
                # Clear Fields
                for field in ['name_input', 'phone_input', 'address_input', 'work_done', 'work_location', 'total_to_pay', 'amount_paid']:
                    screen.ids[field].text = ""
                
                self.update_dashboard_counts()
                self.load_driver_list() # List refresh karein
            else:
                self.show_msg(message, "error")
        except Exception as e:
            print(f"Driver Save Error: {e}")

    # ================= DRIVER LIST & SEARCH =================
    def open_driver_section(self):
        self.change_screen("driver_list")
        self.load_driver_list()

    def load_driver_list(self):
        if not self.user_email: return
        self.filter_drivers("") # Khali query matlab saare drivers

    def filter_drivers(self, query):
        if not self.user_email: return
        query = query.strip().lower()
        
        screen = self.root.ids.screen_manager.get_screen('driver_list')
        container = screen.ids.driver_list_container
        container.clear_widgets()
        
        from database import BASE_URL, get_safe_email
        import requests
        s_email = get_safe_email(self.user_email)
        
        try:
            res = requests.get(f"{BASE_URL}/drivers/{s_email}.json").json()
            if not res: return

            for d_id, data in res.items():
                name = str(data.get('name', '')).lower()
                phone = str(data.get('phone', ''))
                
                try:
                    pending_val = float(data.get('pending_balance', 0))
                except: pending_val = 0.0
                
                status = "full paid" if pending_val <= 0 else "pending"
                
                # Search Logic
                if query in name or query in phone or query in status:
                    item = Factory.DriverRowCard()
                    item.driver_id = str(d_id)
                    item.name = data.get('name', '')
                    item.phone = data.get('phone', '')
                    
                    if pending_val <= 0:
                        item.salary = "Full Paid"
                        item.status_text = "Hisaab Clear"
                        item.amount_color = [0, 0.6, 0, 1]
                    else:
                        item.salary = f"₹ {int(pending_val)}"
                        item.status_text = "Pending"
                        item.amount_color = [1, 0, 0, 1]
                        
                    container.add_widget(item)
        except Exception as e:
            print(f"Driver Filter Error: {e}")

    # ================= UPDATE PAYMENT & WORK =================
    def edit_driver_payment_dialog(self, driver_id):
        self.editing_id = driver_id
        
        from kivymd.uix.boxlayout import MDBoxLayout
        layout = MDBoxLayout(orientation="vertical", spacing="12dp", size_hint_y=None, height="280dp")

        self.driver_pay_input = MDTextField(hint_text="Kitne paise diye?", mode="rectangle", input_filter="float")
        self.edit_work = MDTextField(hint_text="Kitna kaam kiya?", mode="rectangle")
        self.edit_loc = MDTextField(hint_text="Kahan kaam kiya?", mode="rectangle")

        layout.add_widget(self.driver_pay_input)
        layout.add_widget(self.edit_work)
        layout.add_widget(self.edit_loc)

        self.dialog = MDDialog(
            title="Update Driver Payment & Work",
            type="custom",
            content_cls=layout,
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="SAVE", on_release=lambda x: self.save_driver_payment())
            ]
        )
        self.dialog.open()

    def save_driver_payment(self):
        try:
            paid_now = float(self.driver_pay_input.text or 0)
            new_work = self.edit_work.text.strip()
            new_loc = self.edit_loc.text.strip()

            from database import BASE_URL, get_safe_email
            import requests
            s_email = get_safe_email(self.user_email)
            url = f"{BASE_URL}/drivers/{s_email}/{self.editing_id}.json"
            
            # 1. Purana data fetch karein
            curr = requests.get(url).json()
            if not curr: return

            old_paid = float(curr.get('paid_amount', 0))
            total = float(curr.get('total_amount', 0))
            
            updated_paid = old_paid + paid_now
            updated_pending = total - updated_paid

            # 2. Update Payload
            payload = {
                "paid_amount": updated_paid,
                "pending_balance": updated_pending,
                "work_done": new_work if new_work else curr.get('work_done', ''),
                "work_location": new_loc if new_loc else curr.get('work_location', '')
            }
            
            requests.patch(url, json=payload)
            self.dialog.dismiss()
            self.load_driver_list()
            self.show_msg("Driver ka record update ho gaya!", "success")
            
        except Exception as e:
            print(f"Driver Update Error: {e}")
            self.show_msg("Update fail ho gaya!", "error")

    # ================= DRIVER PAYMENT & HISTORY LOGIC =================
    def save_driver_payment(self):
        if not self.user_email: return
        try:
            raw_amt = self.driver_pay_input.text.strip()
            added_amt = float(raw_amt) if raw_amt else 0.0
            new_work_input = self.edit_work.text.strip()
            new_loc_input = self.edit_loc.text.strip()
            
            from database import BASE_URL, get_safe_email
            import requests
            s_email = get_safe_email(self.user_email)
            url = f"{BASE_URL}/drivers/{s_email}/{self.editing_id}.json"
            
            # 1. Fetch current data (Security & Logic Check)
            curr = requests.get(url).json()
            
            if curr:
                total_sal = float(curr.get('total_amount', 0))
                old_paid = float(curr.get('paid_amount', 0))
                old_work = str(curr.get('work_done') or "")
                old_loc = str(curr.get('work_location') or "")

                updated_paid = old_paid + added_amt
                updated_pending = total_sal - updated_paid

                # History Logic (Aapka logic: comma separated list)
                updated_work = f"{old_work}, {new_work_input}" if (old_work and new_work_input) else (new_work_input or old_work)
                updated_loc = f"{old_loc}, {new_loc_input}" if (old_loc and new_loc_input) else (new_loc_input or old_loc)
                
                # 2. Update Firebase using PATCH
                payload = {
                    "paid_amount": updated_paid,
                    "pending_balance": updated_pending,
                    "work_done": updated_work,
                    "work_location": updated_loc
                }
                
                requests.patch(url, json=payload)
                self.show_msg("Hisaab update ho gaya!", "success")
            
            self.dialog.dismiss()
            self.load_driver_list()
            
        except ValueError:
            self.show_msg("Sahi number (amount) bhariye!", "error")
        except Exception as e:
            print(f"Error: {e}")

    # ================= DRIVER DETAILS DIALOG =================
    def show_driver_details(self, driver_id):
        if not self.user_email: return
        
        from database import BASE_URL, get_safe_email
        import requests
        s_email = get_safe_email(self.user_email)
        
        try:
            # Firebase se specific driver ka data lana
            row = requests.get(f"{BASE_URL}/drivers/{s_email}/{driver_id}.json").json()

            if row:
                # Mapping Firebase keys (No more index confusion)
                name = row.get('name', 'N/A')
                phone = row.get('phone', 'N/A')
                address = row.get('address', 'N/A')
                work_done = row.get('work_done', 'N/A')
                location = row.get('work_location', 'N/A')
                total = row.get('total_amount', 0)
                paid = row.get('paid_amount', 0)
                pending = row.get('pending_balance', 0)

                details = (
                    f"[b]Phone:[/b] {phone}\n"
                    f"[b]Address:[/b] {address}\n"
                    f"[b]Work:[/b] {work_done}\n"
                    f"[b]Location:[/b] {location}\n\n"
                    f"[color=3388ff][b]Financial Summary:[/b][/color]\n"
                    f"Total Amount: ₹{total}\n"
                    f"Paid Amount: ₹{paid}\n"
                    f"[color=ff0000]Pending Balance: ₹{pending}[/color]"
                )

                self.detail_dialog = MDDialog(
                    title=f"Driver: {name}",
                    text=details,
                    buttons=[MDFlatButton(text="CLOSE", on_release=lambda x: self.detail_dialog.dismiss())],
                )
                self.detail_dialog.open()
        except Exception as e:
            print(f"Detail Fetch Error: {e}")

    # ================= DELETE DRIVER LOGIC =================
    def confirm_driver_delete(self, driver_id):
        self.editing_id = driver_id  
        
        self.delete_dialog = MDDialog(
            title="Delete Driver?",
            text="Kya aap is driver ka pura record delete karna chahte hain? Ye wapas nahi aayega.",
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda x: self.delete_dialog.dismiss()),
                MDFlatButton(
                    text="DELETE", 
                    theme_text_color="Custom",
                    text_color=[1, 0, 0, 1], # Red Color
                    on_release=lambda x: self.execute_driver_delete()
                ),
            ],
        )
        self.delete_dialog.open()

    def execute_driver_delete(self):
        if not self.user_email: return
        try:
            from database import BASE_URL, get_safe_email
            import requests
            s_email = get_safe_email(self.user_email)
            
            # Firebase DELETE request
            url = f"{BASE_URL}/drivers/{s_email}/{self.editing_id}.json"
            requests.delete(url)
            
            self.delete_dialog.dismiss()
            self.load_driver_list()
            self.update_dashboard_counts()
            self.show_msg("Driver ka record hata diya gaya!", "success")
            
        except Exception as e:
            print(f"Delete Error: {e}")
            self.show_msg("Record delete nahi ho paya!", "error")
#========================================maiantancelist=============================================
    # ---------------------------------------------------------
    # MAINTENANCE LIST LOGIC (DRIVER LIST STYLE)
    # ---------------------------------------------------------

    # ================= MAINTENANCE LIST & SEARCH (FIREBASE) =================
    def load_maintenance_list(self):
        if not self.user_email: return
        try:
            self.root.ids.screen_manager.current = "maint_list"
            self.filter_maintenance("") # Khali search matlab saare records dikhao
        except Exception as e:
            self.show_msg("Data load fail ho gaya!", "error")

    def filter_maintenance(self, query):
        if not self.user_email: return
        query = query.strip().lower()
        
        screen = self.root.ids.screen_manager.get_screen('maint_list')
        container = screen.ids.maintenance_container
        container.clear_widgets()
        
        from database import BASE_URL, get_safe_email
        import requests
        s_email = get_safe_email(self.user_email)
        
        try:
            # Firebase se pura maintenance data lana
            res = requests.get(f"{BASE_URL}/maintenance_records/{s_email}.json").json()
            if not res:
                self.show_msg("Koi record nahi mila", "info")
                return

            # Firebase data ko list mein convert karke sort karna (Newest First)
            sorted_items = sorted(res.items(), key=lambda x: x[0], reverse=True)

            for m_id, data in sorted_items:
                m_type = str(data.get('work_type', '')).lower()
                m_date = str(data.get('date', ''))
                m_cost = str(data.get('cost', ''))
                
                # Search Logic (Work type, Date ya Cost match kare)
                if query in m_type or query in m_date or query in m_cost:
                    item = Factory.MaintenanceRowCard()
                    item.m_id = str(m_id)
                    item.m_type = data.get('work_type', '')
                    item.m_date = m_date
                    item.m_cost = m_cost
                    
                    # Status logic (Agar complete ho gaya toh green color)
                    is_done = data.get('is_dismissed', 0)
                    item.m_status = "Service Done" if is_done else "Pending"
                    item.status_color = [0, 0.6, 0.2, 1] if is_done else [1, 0.5, 0, 1]
                    
                    container.add_widget(item)
        except Exception as e:
            print(f"Maint Filter Error: {e}")

    # ================= MAINTENANCE DETAILS & TASK COMPLETE =================
    def show_maintenance_details(self, m_id):
        if not self.user_email: return
        try:
            from database import BASE_URL, get_safe_email
            import requests
            s_email = get_safe_email(self.user_email)
            
            # Specific ID ka data fetch karna
            row = requests.get(f"{BASE_URL}/maintenance_records/{s_email}/{m_id}.json").json()

            if row:
                details = (
                    f"Service Type: {row.get('work_type', 'N/A')}\n"
                    f"Date: {row.get('date', 'N/A')}\n"
                    f"Cost: ₹{row.get('cost', 0)}\n"
                    f"Next Service: {row.get('next_service_date') or 'Not Set'}\n"
                )
                
                self.dialog = MDDialog(
                    title="Maintenance Detail",
                    text=details,
                    buttons=[
                        MDFlatButton(text="CLOSE", on_release=lambda x: self.dialog.dismiss()),
                        MDRaisedButton(
                            text="WORK AS DONE",
                            md_bg_color=(0, 0.5, 0, 1),
                            on_release=lambda x: self.complete_maintenance_task(m_id)
                        ),
                    ],
                )
                self.dialog.open()
        except Exception as e:
            self.show_msg("Details nahi dikha sakte", "error")
    
    def complete_maintenance_task(self, m_id):
        if not self.user_email: return
        try:
            from database import BASE_URL, get_safe_email
            import requests
            s_email = get_safe_email(self.user_email)
            
            # Firebase Update (is_dismissed ko 1 karna)
            url = f"{BASE_URL}/maintenance_records/{s_email}/{m_id}.json"
            requests.patch(url, json={"is_dismissed": 1})
            
            if self.dialog: self.dialog.dismiss()
            self.show_msg("Service complete mark ho gayi!", "success")
            self.load_maintenance_list() # List refresh
            self.start_reminder_thread() # Reminders update karein
        except Exception as e:
            self.show_msg("Status update fail hua!", "error")

    # ================= DELETE MAINTENANCE RECORD =================
    def confirm_maintenance_delete(self, m_id):
        self.delete_dialog = MDDialog(
            title="Delete Record?",
            text="Kya aap is record ko hamesha ke liye delete karna chahte hain?",
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda x: self.delete_dialog.dismiss()),
                MDRaisedButton(
                    text="DELETE",
                    md_bg_color=(1, 0, 0, 1),
                    on_release=lambda x: self.delete_maintenance_from_db(m_id)
                ),
            ],
        )
        self.delete_dialog.open()

    def delete_maintenance_from_db(self, m_id):
        try:
            from database import BASE_URL, get_safe_email
            import requests
            s_email = get_safe_email(self.user_email)
            
            # Firebase DELETE request
            url = f"{BASE_URL}/maintenance_records/{s_email}/{m_id}.json"
            requests.delete(url)
            
            self.delete_dialog.dismiss()
            self.show_msg("Record successfully deleted", "success")
            self.load_maintenance_list()
            self.start_reminder_thread()
        except Exception as e:
            print(f"Error deleting record: {e}")
            self.show_msg("Delete fail ho gaya", "error")

#=============================================fuel_list============================================
    # --- FUEL LIST FUNCTIONS ---

    # ================= FUEL LIST & SEARCH (FIREBASE) =================
    def load_fuel_list(self):
        if not self.user_email: return  # Check if user is logged in
        try:
            self.root.ids.screen_manager.current = "fuel_list"
            # Hum seedha filter_fuel ko khali query ke saath call karenge 
            # taaki saara data load ho jaye
            self.filter_fuel("") 
        except Exception as e:
            print(f"Fuel Load Error: {e}")
            self.show_msg("Fuel records load nahi huye", "error")

    def filter_fuel(self, query):
        if not self.user_email: return
        query = query.strip().lower()
        
        screen = self.root.ids.screen_manager.get_screen('fuel_list')
        container = screen.ids.fuel_container
        container.clear_widgets()
        
        from database import BASE_URL, get_safe_email
        import requests
        s_email = get_safe_email(self.user_email)
        
        try:
            # Firebase se user ka fuel data fetch karna
            res = requests.get(f"{BASE_URL}/fuel_records/{s_email}.json").json()
            if not res: return

            # Records ko reverse order mein dikhane ke liye (Newest First)
            sorted_keys = sorted(res.keys(), reverse=True)

            for f_id in sorted_keys:
                data = res[f_id]
                station = str(data.get('station', '')).lower()
                date = str(data.get('date', ''))
                total = str(data.get('total', ''))
                
                # Search Logic: Station, Date ya Total match kare
                if query in station or query in date or query in total:
                    item = Factory.FuelRowCard()
                    item.f_id = str(f_id)
                    item.f_date = data.get('date', '')
                    item.f_station = data.get('station', '')
                    item.f_liters = str(data.get('liters', ''))
                    item.f_total = str(data.get('total', ''))
                    container.add_widget(item)
        except Exception as e:
            print(f"Filter Error: {e}")

    # ================= FUEL DETAILS DIALOG =================
    def show_fuel_details(self, f_id):
        if not self.user_email: return
        try:
            from database import BASE_URL, get_safe_email
            import requests
            s_email = get_safe_email(self.user_email)
            
            # Firebase se specific record fetch karna
            row = requests.get(f"{BASE_URL}/fuel_records/{s_email}/{f_id}.json").json()

            if row:
                msg = (f"Station: {row.get('station', 'N/A')}\n"
                       f"Date: {row.get('date', 'N/A')}\n"
                       f"Liters: {row.get('liters', 0)} L\n"
                       f"Rate: ₹{row.get('rate', 0)}\n"
                       f"Total: ₹{row.get('total', 0)}")
                
                self.dialog = MDDialog(
                    title="Fuel Receipt Detail",
                    text=msg,
                    buttons=[MDFlatButton(text="CLOSE", on_release=lambda x: self.dialog.dismiss())]
                )
                self.dialog.open()
        except Exception as e:
            self.show_msg("Details load fail!", "error")

    # ================= DELETE FUEL RECORD =================
    def confirm_fuel_delete(self, f_id):
        self.dialog = MDDialog(
            title="Delete Fuel Record?",
            text="Kya aap is entry ko delete karna chahte hain?",
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda x: self.dialog.dismiss()),
                MDFlatButton(text="DELETE", theme_text_color="Error", 
                             on_release=lambda x: self.delete_fuel_record(f_id))
            ]
        )
        self.dialog.open()

    def delete_fuel_record(self, f_id):
        if not self.user_email: return
        self.dialog.dismiss()
        try:
            from database import BASE_URL, get_safe_email
            import requests
            s_email = get_safe_email(self.user_email)
            
            # Firebase DELETE request
            requests.delete(f"{BASE_URL}/fuel_records/{s_email}/{f_id}.json")
            
            self.show_msg("Fuel entry delete ho gayi!", "success")
            self.load_fuel_list() # List refresh karein
            self.update_dashboard_counts() # Dashboard stats update karein
        except Exception as e:
            self.show_msg("Entry delete nahi ho payi!", "error")

#=================================================Loan EMI=====================================================
    # ======================= Loan EMI Section =======================
    # ================= LOAN SETUP & SAVE (FIREBASE) =================
    def setup_loan_details(self):
        if not self.user_email:
            self.show_msg("Login zaroori hai!", "error")
            return

        layout = MDBoxLayout(orientation="vertical", spacing="10dp", size_hint_y=None, height="420dp")
        
        self.l_item = MDTextField(hint_text="Loan kiska hai? (e.g. Tractor)", mode="rectangle")
        self.l_bank = MDTextField(hint_text="Bank ka Naam", mode="rectangle")
        self.l_total = MDTextField(hint_text="Total Loan Amount (₹)", mode="rectangle", input_filter="float")
        self.l_emi = MDTextField(hint_text="EMI Amount (₹)", mode="rectangle", input_filter="float")
        self.l_date = MDTextField(hint_text="Hafta Tarikh (e.g. 10)", mode="rectangle")
        
        layout.add_widget(self.l_item)
        layout.add_widget(self.l_bank)
        layout.add_widget(self.l_total)
        layout.add_widget(self.l_emi)
        layout.add_widget(self.l_date)

        self.setup_dialog = MDDialog(
            title="Setup New Loan",
            type="custom",
            content_cls=layout,
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda x: self.setup_dialog.dismiss()),
                MDRaisedButton(text="SAVE", on_release=lambda x: self.save_loan_config())
            ]
        )
        self.setup_dialog.open()

    def save_loan_config(self):
        if not self.user_email: return
        try:
            from database import BASE_URL, get_safe_email
            import requests
            s_email = get_safe_email(self.user_email)

            payload = {
                "item_name": self.l_item.text.strip(),
                "bank_name": self.l_bank.text.strip(),
                "total_amount": float(self.l_total.text or 0),
                "emi_amount": float(self.l_emi.text or 0),
                "due_date": self.l_date.text.strip(),
                "created_at": str(datetime.now())
            }

            if not payload['item_name'] or not payload['total_amount']:
                self.show_msg("Naam aur Amount bhariye!", "error")
                return

            # Firebase POST (Naya loan create karein)
            requests.post(f"{BASE_URL}/loan_config/{s_email}.json", json=payload)
            
            self.setup_dialog.dismiss()
            self.start_finance_background_load()
            self.start_reminder_thread()
            self.show_msg("Naya loan setup ho gaya!", "success")
        except Exception as e:
            self.show_msg("Data save nahi ho paya!", "error")

    # ================= BACKGROUND LOADING (FIREBASE) =================
    def start_finance_background_load(self):
        Thread(target=self.load_finance_data_thread).start()

    def load_finance_data_thread(self):
        if not self.user_email: return
        try:
            from database import BASE_URL, get_safe_email
            import requests
            s_email = get_safe_email(self.user_email)
            
            # 1. Loan Configuration fetch karein
            loans = requests.get(f"{BASE_URL}/loan_config/{s_email}.json").json()
            # 2. Finance History (Payments) fetch karein
            payments = requests.get(f"{BASE_URL}/finance_hafta/{s_email}.json").json()
            
            loan_data_list = []
            if loans:
                for l_id, info in loans.items():
                    # Is specific loan ke saare payments calculate karein
                    paid_val = 0.0
                    if payments:
                        for p_id, p_info in payments.items():
                            if str(p_info.get('loan_id')) == str(l_id):
                                paid_val += float(p_info.get('amount', 0))
                    
                    loan_data_list.append({
                        'id': str(l_id),
                        'name': info.get('item_name', 'N/A'),
                        'bank': info.get('bank_name', 'N/A'),
                        'total': float(info.get('total_amount', 0)),
                        'paid': paid_val,
                        'date': info.get('due_date', '')
                    })
            
            Clock.schedule_once(lambda dt: self.update_finance_ui(loan_data_list), 0)
        except Exception as e:
            print(f"Finance Load Error: {e}")

    # ================= UI UPDATE & REMINDER LOGIC =================
    def update_finance_ui(self, loan_data_list):
        try:
            from datetime import datetime, date
            import calendar

            finance_screen = self.root.ids.screen_manager.get_screen('finance')
            container = finance_screen.ids.loan_list_container
            container.clear_widgets()

            today_date = datetime.now().date()

            for data in loan_data_list:
                card = Factory.LoanCard()
                card.loan_id = data['id']
                card.item_name = str(data['name']).upper()
                card.bank = f"Bank: {data['bank']}"
                
                total_val = data['total']
                paid_val = data['paid']
                remaining = total_val - paid_val
                
                card.total_loan = f"Total Loan: ₹{total_val:,.0f}"
                card.total_paid = f"{paid_val:,.0f}"
                card.balance = f"{remaining:,.0f}"
                card.progress = (paid_val / total_val * 100) if total_val > 0 else 0
                
                # --- DATE ALERT LOGIC ---
                try:
                    raw_date = str(data.get('date', '')).strip()
                    if not raw_date:
                        card.alert_text = "Date Set Karein"
                        card.alert_color = [0.5, 0.5, 0.5, 1]
                    else:
                        if "-" in raw_date:
                            try:
                                target_date_obj = datetime.strptime(raw_date, '%Y-%m-%d').date()
                            except:
                                target_date_obj = datetime.strptime(raw_date, '%d-%m-%Y').date()
                        else:
                            digits = ''.join(filter(str.isdigit, raw_date))
                            if digits:
                                due_day = int(digits)
                                t_year, t_month = today_date.year, today_date.month
                                if today_date.day > due_day:
                                    t_month += 1
                                    if t_month > 12: t_month = 1; t_year += 1
                                last_day = calendar.monthrange(t_year, t_month)[1]
                                target_date_obj = date(t_year, t_month, min(due_day, last_day))
                            else: raise ValueError

                        days_diff = (target_date_obj - today_date).days
                        if remaining <= 0:
                            card.alert_text = "LOAN COMPLETE! ✅"
                            card.alert_color = [0, 1, 0, 1]
                        elif days_diff < 0:
                            card.alert_text = f"⚠ Delay: {abs(days_diff)} Din"
                            card.alert_color = [1, 0, 0, 1]
                        elif days_diff == 0:
                            card.alert_text = "⚠ AAJ KIST BHARNI HAI!"
                            card.alert_color = [1, 0, 0, 1]
                        else:
                            card.alert_text = f"{days_diff} Din Baki ({target_date_obj.strftime('%d %b')})"
                            card.alert_color = [0, 0.7, 0.4, 1]
                except:
                    card.alert_text = f"Due: {raw_date}"
                    card.alert_color = [0.5, 0.5, 0.5, 1]


                container.add_widget(card)
        except Exception as e:
            print(f"UI Update Error: {e}")
            
    # --- 4. PAYMENT POPUP (MANUAL DATE & NO ZERO) ---
    def show_pay_popup(self, loan_id, loan_name):
        """EMI pay karne ka popup, ab Cloud Security ke saath."""
        if not self.user_email:
            self.show_msg("Pehle login karein!", "error")
            return

        try:
            from database import BASE_URL, get_safe_email
            import requests
            s_email = get_safe_email(self.user_email)

            # 1. Cloud se EMI amount nikalna hint ke liye
            res = requests.get(f"{BASE_URL}/loan_config/{s_email}/{loan_id}.json").json()
            hint_amt = str(res.get('emi_amount', 0)) if res else "0"

            # 2. Input fields setup
            self.pay_input = MDTextField(
                hint_text=f"Kitna Paisa Diya? (Sujhav: ₹{hint_amt})",
                input_filter="float", mode="rectangle"
            )
            
            self.pay_date_input = MDTextField(
                hint_text="Agli Kist ki Date (DD-MM-YYYY)",
                text=datetime.now().strftime("%d-%m-%Y"), 
                mode="rectangle"
            )

            layout = MDBoxLayout(orientation="vertical", adaptive_height=True, spacing="15dp", padding="10dp")
            layout.add_widget(self.pay_input)
            layout.add_widget(self.pay_date_input)

            # 3. Dialog Box Display
            self.pay_dialog = MDDialog(
                title=f"PAY EMI: {loan_name}",
                type="custom",
                content_cls=layout,
                buttons=[
                    MDFlatButton(text="CANCEL", on_release=lambda x: self.pay_dialog.dismiss()),
                    MDRaisedButton(
                        text="PAID & UPDATE",
                        md_bg_color=[0, 0.6, 0.2, 1],
                        on_release=lambda x: self.process_payment_full(
                            loan_id, self.pay_input.text, self.pay_date_input.text
                        )
                    ),
                ],
            )
            self.pay_dialog.open()
            
        except Exception as e:
            print(f"Popup Error: {e}")
            self.show_msg("Payment window nahi khul saki", "error")

    def process_payment_full(self, loan_id, amount, next_date):
        if not self.user_email: return
        try:
            from database import BASE_URL, get_safe_email
            import requests
            s_email = get_safe_email(self.user_email)

            if not amount or not next_date:
                self.show_msg("Paisa aur agli date bharna zaroori hai!", "error")
                return

            aaj = datetime.now().strftime("%d-%m-%Y")
            
            # 1. Cloud History mein entry (POST)
            payment_entry = {
                "loan_id": str(loan_id),
                "date": aaj,
                "amount": float(amount),
                "note": "EMI Paid"
            }
            requests.post(f"{BASE_URL}/finance_hafta/{s_email}.json", json=payment_entry)
            
            # 2. Main Loan table mein agli date update karna (PATCH)
            requests.patch(f"{BASE_URL}/loan_config/{s_email}/{loan_id}.json", 
                          json={"due_date": next_date})
            
            self.show_msg("Kist jama ho gayi!", "success")
            self.pay_dialog.dismiss()
            self.start_finance_background_load()
            self.start_reminder_thread()
        except Exception as e:
            self.show_msg("Error updating payment!", "error")

    # ================= LOAN DETAILS (FIREBASE) =================
    def show_emi_details(self, loan_id, loan_name, alert_msg):
        """Jab user card par click karega, Cloud se details dikhayi dengi."""
        if not self.user_email:
            self.show_msg("Login zaroori hai!", "error")
            return

        try:
            from database import BASE_URL, get_safe_email
            import requests
            s_email = get_safe_email(self.user_email)
            
            # Cloud se fetching
            res = requests.get(f"{BASE_URL}/loan_config/{s_email}/{loan_id}.json").json()

            if res:
                emi_amt = float(res.get('emi_amount', 0))
                d_date = res.get('due_date', 'N/A')
                
                self.emi_info_dialog = MDDialog(
                    title=f"{loan_name} Details",
                    type="custom",
                    text=(
                        f"💰 [b]Kist ki Rakam:[/b] ₹{emi_amt:,.0f}\n"
                        f"📅 [b]Kist ki Tarikh:[/b] {d_date}\n\n"
                        f"[b]Status:[/b]\n{alert_msg}" 
                    ),
                    buttons=[
                        MDFlatButton(text="CLOSE", on_release=lambda x: self.emi_info_dialog.dismiss()),
                        MDRaisedButton(
                            text="PAY NOW",
                            md_bg_color=[0, 0.6, 0.2, 1],
                            on_release=lambda x: self.open_pay_from_detail(loan_id, loan_name)
                        )
                    ]
                )
                self.emi_info_dialog.open()
            else:
                self.show_msg("Data access denied!", "error")

        except Exception as e:
            self.show_msg("Details load nahi ho saki!", "error")

    def open_pay_from_detail(self, loan_id, loan_name):
        self.emi_info_dialog.dismiss()
        self.show_pay_popup(loan_id, loan_name)

    # ================= DELETE LOAN (FIREBASE) =================
    def confirm_delete_loan(self, loan_id, loan_name):
        self.confirm_dialog = MDDialog(
            title="Delete Loan?",
            text=f"Kya aap '{loan_name}' ko delete karna chahte hain?",
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda x: self.confirm_dialog.dismiss()),
                MDRaisedButton(
                    text="DELETE", md_bg_color=(1, 0, 0, 1),
                    on_release=lambda x: self.delete_loan_from_db(loan_id)
                )
            ]
        )
        self.confirm_dialog.open()

    # ================= DELETE LOAN (FIREBASE) =================
    def delete_loan_from_db(self, loan_id):
        """Cloud se loan aur uski saari kist history hatane ke liye"""
        if not self.user_email: return
        
        try:
            from database import BASE_URL, get_safe_email
            import requests
            s_email = get_safe_email(self.user_email)

            # 1. Main loan configuration delete karein
            requests.delete(f"{BASE_URL}/loan_config/{s_email}/{loan_id}.json")
            
            # 2. History (Hafta table) saaf karna
            # NoSQL mein humein history fetch karke wahi records delete karne honge jo is loan_id ke hain
            hist_res = requests.get(f"{BASE_URL}/finance_hafta/{s_email}.json").json()
            if hist_res:
                for h_id, h_info in hist_res.items():
                    if str(h_info.get('loan_id')) == str(loan_id):
                        requests.delete(f"{BASE_URL}/finance_hafta/{s_email}/{h_id}.json")

            self.show_msg("Loan aur saari history delete ho gayi!", "success")
            if hasattr(self, 'confirm_dialog'):
                self.confirm_dialog.dismiss()
            
            # UI Refresh
            self.start_finance_background_load()
            self.start_reminder_thread()
            
        except Exception as e:
            print(f"Delete Error: {e}")
            self.show_msg("Cloud data delete nahi ho paya!", "error")

    # ================= HISTORY VIEW (DOUBLE CLICK) =================
    def on_card_double_click(self, loan_id, loan_name):
        """
        Jab user loan card par double tap karega, 
        toh Firebase se us specific loan ka poora hisab-kitab aayega.
        """
        if not self.user_email:
            self.show_msg("Login karke history dekhein!", "info")
            return

        try:
            from database import BASE_URL, get_safe_email
            import requests
            from kivymd.uix.list import TwoLineListItem, MDList
            from kivy.uix.scrollview import ScrollView
            
            s_email = get_safe_email(self.user_email)

            # 1. Cloud se payment history fetch karein
            all_payments = requests.get(f"{BASE_URL}/finance_hafta/{s_email}.json").json()
            
            history_list = MDList()
            found_records = False
            
            if all_payments:
                # Latest payment upar dikhane ke liye reverse sort
                for p_id in sorted(all_payments.keys(), reverse=True):
                    p_info = all_payments[p_id]
                    
                    # Sirf is loan_id ki payments filter karein
                    if str(p_info.get('loan_id')) == str(loan_id):
                        found_records = True
                        amt = float(p_info.get('amount', 0))
                        item = TwoLineListItem(
                            text=f"Paid On: {p_info.get('date')}",
                            secondary_text=f"Amount: ₹{amt:,.0f} | {p_info.get('note')}",
                            divider="Full"
                        )
                        history_list.add_widget(item)

            if not found_records:
                history_list.add_widget(
                    TwoLineListItem(text="Abhi tak koi kist jama nahi hui", 
                                    secondary_text="Pehli kist bharni baki hai")
                )

            # 2. Popup UI banana
            scroll = ScrollView(size_hint_y=None, height="400dp")
            scroll.add_widget(history_list)

            self.history_dialog = MDDialog(
                title=f"Payment History: {loan_name}",
                type="custom",
                content_cls=scroll,
                buttons=[
                    MDRaisedButton(
                        text="CLOSE", 
                        on_release=lambda x: self.history_dialog.dismiss()
                    )
                ]
            )
            self.history_dialog.open()

        except Exception as e:
            print(f"History Popup Error: {e}")
            self.show_msg("History load nahi ho saki!", "error")
#=====================================================Reminder =========================================================

    def start_reminder_thread(self):
        """Thread start karna taaki app hang na ho"""
        from threading import Thread
        Thread(target=self.run_reminder_logic, daemon=True).start()

    def run_reminder_logic(self):
        """Cloud se data fetch karke reminders aur alerts taiyar karna"""
        from datetime import datetime
        
        # 1. Security Check
        if not hasattr(self, 'user_email') or not self.user_email:
            return

        try:
            from database import BASE_URL, get_safe_email
            import requests
            s_email = get_safe_email(self.user_email)
            today = datetime.now().date()
            processed_alerts = []
            urgent_msg = ""

            # ================== 1. FINANCE CHECK (Firebase) ==================
            # Loan records fetch karna
            loans = requests.get(f"{BASE_URL}/loan_config/{s_email}.json").json()
            
            if loans:
                for l_id, l_data in loans.items():
                    d_date = l_data.get("due_date")
                    if not d_date or "---" in str(d_date): continue
                    
                    try:
                        due_dt = datetime.strptime(d_date, "%d-%m-%Y").date()
                        diff = (due_dt - today).days
                        
                        # 3 din pehle ya delay hone par
                        if diff <= 3:
                            status = "AAJ DUE" if diff == 0 else (f"{abs(diff)} DIN LATE" if diff < 0 else f"{diff} DIN BAKI")
                            processed_alerts.append({
                                "id": l_id,
                                "type": "LOAN",
                                "title": str(l_data.get("item_name", "Unknown Loan")),
                                "desc": f"EMI: ₹{l_data.get('emi_amount')} | {status}",
                                "color": [1, 0, 0, 1] if diff <= 1 else [1, 0.5, 0, 1],
                                "icon": "bank"
                            })
                            if diff <= 1: 
                                urgent_msg += f"• FINANCE: {l_data.get('item_name')} ({status})\n"
                    except: continue

            # ================== 2. MAINTENANCE CHECK (Firebase) ==================
            # Maintenance records fetch karna
            maint = requests.get(f"{BASE_URL}/maintenance_records/{s_email}.json").json()
            
            if maint:
                for m_id, m_data in maint.items():
                    # Sirf wahi dikhao jo abhi tak dismiss nahi huye
                    if m_data.get("is_dismissed") == 1: continue
                    
                    s_date = m_data.get("next_service_date")
                    if not s_date or "---" in str(s_date): continue
                    
                    try:
                        srv_dt = datetime.strptime(s_date, "%d-%m-%Y").date()
                        diff = (srv_dt - today).days
                        
                        # 7 din baki hone par alert
                        if diff <= 7:
                            status = "AAJ DUE" if diff == 0 else (f"{abs(diff)}DIN LATE" if diff < 0 else f"{diff} DIN BAKI")
                            processed_alerts.append({
                                "id": m_id,
                                "type": "SERVICE",
                                "title": str(m_data.get("work_type", "Maintenance")),
                                "desc": f"Due:{s_date}|{status}",
                                "color": [0, 0.5, 0.8, 1],
                                "icon": "wrench-cog"
                            })
                            if diff <= 1: 
                                urgent_msg += f"• SERVICE: {m_data.get('work_type')} ({status})\n"
                    except: continue

            # 3. UI Update (Main Thread par)
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self.final_ui_sync(processed_alerts, urgent_msg), 0)

        except Exception as e:
            print(f"Reminder Logic Cloud Error: {e}")

    def final_ui_sync(self, alerts, urgent_msg):
        """Dashboard ki reminder list ko refresh karta hai"""
        try:
            if not self.root or 'reminder_list' not in self.root.ids:
                return
                
            container = self.root.ids.reminder_list
            container.clear_widgets()
            
            from kivymd.uix.list import TwoLineIconListItem, IconLeftWidget, OneLineListItem
            
            if not alerts:
                container.add_widget(OneLineListItem(text="✅ Sab kaam time par hai!"))
            else:
                for a in alerts:
                    item = TwoLineIconListItem(
                        text=a["title"],
                        secondary_text=a["desc"],
                        theme_text_color="Custom",
                        text_color=a["color"]
                    )
                    item.add_widget(IconLeftWidget(icon=a["icon"]))
                    container.add_widget(item)

            # Urgent popup
            if urgent_msg:
                self.show_startup_popup(urgent_msg)
                
        except Exception as e:
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self.final_ui_sync(alerts, urgent_msg), 0.5)

    def show_startup_popup(self, msg):
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDRaisedButton
        self.rem_dialog = MDDialog(
            title="‼️ URGENT ATTENTION",
            text=msg,
            buttons=[MDRaisedButton(text="OK", on_release=lambda x: self.rem_dialog.dismiss())]
        )
        self.rem_dialog.open()
    
    def dismiss_maintenance(self, record_id):
        """Cloud par Maintenance reminder ko band (Dismiss) karna"""
        if not self.user_email: return
        
        try:
            from database import BASE_URL, get_safe_email
            import requests
            s_email = get_safe_email(self.user_email)
            
            # Cloud par is_dismissed ko 1 set karein (PATCH)
            requests.patch(f"{BASE_URL}/maintenance_records/{s_email}/{record_id}.json", 
                          json={"is_dismissed": 1})
            
            # Dashboard refresh karein
            self.run_reminder_logic()
        except Exception as e:
            print(f"Dismiss Error: {e}")
#=====================================================login signup===========================================
    # --- PROFESSIONAL SIGNUP LOGIC ---
    # ================= SIGNUP LOGIC (FIREBASE) =================
    # ================= SIGNUP LOGIC =================
    def process_signup(self):
        signup = self.root.ids.screen_manager.get_screen('signup')
        import re # Regular expression for professional email check

        # Inputs lena
        fn = signup.ids.full_name.text.strip()
        em = signup.ids.email.text.strip().lower()
        un = signup.ids.username.text.strip()
        ph = signup.ids.phone.text.strip()
        ad = signup.ids.address.text.strip()
        p1 = signup.ids.password.text.strip()
        p2 = signup.ids.confirm_password.text.strip()

        # --- Sakht Validation ---
        if not all([fn, em, un, ph, ad, p1, p2]):
            self.show_msg("Sabhi fields bharna zaroori hai!", "warning")
            return

        # Professional Email Validation
        email_pattern = r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'
        if not re.match(email_pattern, em):
            signup.ids.email.error = True
            self.show_msg("Kripya ek asli aur valid Email ID likhein!", "error")
            return

        # Phone Number Validation (Exactly 10 digits)
        if not ph.isdigit() or len(ph) != 10:
            signup.ids.phone.error = True
            self.show_msg("Mobile number barabar 10 ank ka hona chahiye!", "error")
            return

        if len(p1) < 6:
            signup.ids.password.error = True
            self.show_msg("Password kam se kam 6 aksharo ka rakhein!", "error")
            return

        if p1 != p2:
            signup.ids.confirm_password.error = True
            self.show_msg("Dono Password ek jaise hone chahiye!", "error")
            return
        
        # --- Firebase Auth & Database ---
        import requests
        from database import register_user, BASE_URL
        API_KEY = "AIzaSyAc2VmcRaEiT6ni0EKOoVP7xa3xl6GOMkE"

        try:
            signup_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"
            res = requests.post(signup_url, json={"email": em, "password": p1, "returnSecureToken": True})
            res_data = res.json()

            if res.status_code == 200:
                id_token = res_data['idToken']
                
                # Verification Link Bhejna
                verify_url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={API_KEY}"
                requests.post(verify_url, json={"requestType": "VERIFY_EMAIL", "idToken": id_token})

                # Database mein save
                success, msg = register_user(em, un, p1, fn, ph, ad)
                
                if success:
                    self.show_msg("Account ban gaya! Email link par click karke verify karein.", "success")
                    self.root.ids.screen_manager.current = "login"
                else:
                    self.show_msg(msg, "info")
            else:
                err = res_data.get('error', {}).get('message', '')
                if "EMAIL_EXISTS" in err:
                    self.show_msg("Ye Email pehle se register hai, Login karein!", "warning")
                else:
                    self.show_msg(f"Galti: {err}", "error")

        except Exception as e:
            self.show_msg("Network Error! Internet check karein.", "warning")
    
    def process_login(self):
        login = self.root.ids.screen_manager.get_screen('login')
        u_input = login.ids.user.text.strip().lower() # Username input
        p = login.ids.pwd.text.strip() # Password input

        # 1. Basic Validation
        if not u_input or not p:
            self.show_msg("Username aur Password dono bhariye", "error")
            return

        from database import verify_user, BASE_URL, get_email_from_username, get_safe_email
        import requests
        API_KEY = "AIzaSyAc2VmcRaEiT6ni0EKOoVP7xa3xl6GOMkE"

        try:
            # 2. Username se Email pata karein
            user_email = get_email_from_username(u_input)
            
            if not user_email:
                self.show_msg("Aap naye user lag rahe ho, kripya account banayein!", "info")
                return

            # 3. Firebase Auth se Login check
            login_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
            res = requests.post(login_url, json={"email": user_email, "password": p, "returnSecureToken": True})
            res_data = res.json()

            if res.status_code == 200:
                id_token = res_data['idToken']
                
                # 4. Email Verification Check
                info_url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={API_KEY}"
                info_res = requests.post(info_url, json={"idToken": id_token}).json()
                is_verified = info_res['users'][0].get('emailVerified', False)

                if not is_verified:
                    self.show_msg("Account verify nahi hai! Email link click karein.", "warning")
                    return

                # --- 5. PASSWORD SYNC LOGIC (Sabse Zaroori) ---
                # Agar user ne 'Forgot Password' se password badla hai, 
                # toh use yahan DB mein update kar dete hain.
                s_email = get_safe_email(user_email)
                requests.patch(f"{BASE_URL}/users/{s_email}.json", json={"password": p})

                # 6. Database se User ka baaki data uthayein
                user_data = verify_user(user_email, p)

                if user_data:
                    self.user_email = user_data.get('email')
                    self.user_full_name = user_data.get('full_name')

                    # UI cleanup aur transition
                    login.ids.user.text = ""
                    login.ids.pwd.text = ""
                    self.root.ids.screen_manager.current = "dashboard"
                    self.root.ids.top_bar.height = "56dp"
                    self.root.ids.top_bar.opacity = 1
                    
                    # Sabhi data refresh/load functions
                    self.update_dashboard_counts()
                    self.start_finance_background_load() 
                    self.start_reminder_thread()
                    self.update_reports()
                    self.fetch_and_set_user_name()
                    self.load_customer_list_data()
                    
                    self.show_msg(f"Swagat hai, {self.user_full_name}!", "success")
                else:
                    self.show_msg("Database Sync Error!", "error")
            else:
                # Firebase Errors handling
                err = res_data.get('error', {}).get('message', '')
                if "INVALID_PASSWORD" in err:
                    self.show_msg("Ghalat Password! Fir se koshish karein.", "error")
                elif "USER_DISABLED" in err:
                    self.show_msg("Aapka account band kar diya gaya hai.", "error")
                else:
                    self.show_msg("Login Fail: " + err, "error")

        except Exception as e:
            self.show_msg("Network Error! Internet check karein.", "warning")
            
    # ================= LOGOUT LOGIC =================
    def logout(self):
        # 1. Session Identity Clear
        self.user_email = "" 
        self.user_full_name = ""
        
        # 2. UI Reset
        if 'user_name_label' in self.root.ids:
            self.root.ids.user_name_label.text = "Tractor Manager"

        self.root.ids.top_bar.height = "0dp"
        self.root.ids.top_bar.opacity = 0

        # 3. Transition
        self.root.ids.screen_manager.transition.direction = "right"
        self.root.ids.screen_manager.current = "login"

        # 4. Side Menu Close
        from kivy.animation import Animation
        menu = self.root.ids.side_menu
        Animation(pos=(-menu.width, 0), d=0.2, t='out_quad').start(menu)

        print("Cloud Security: Session destroyed successfully.")
        self.show_msg("Logout ho gaya!", "info")
    #==================================profile=======================================================
    # ================= LOAD PROFILE DATA (FIREBASE) =================
    # ================= USER PROFILE SYNC (EMAIL BASED) =================
    def fetch_and_set_user_name(self):
        """User identity (Email) ke aadhar par naam set karna"""
        # Agar login ke waqt full_name mil gaya hai toh seedha use karein
        if hasattr(self, 'user_full_name') and self.user_full_name:
            self.root.ids.user_name_label.text = self.user_full_name
        else:
            self.root.ids.user_name_label.text = "Tractor Owner"

    def load_profile_data(self):
        """Cloud se user ki details profile screen par load karna"""
        if not self.user_email:
            return

        try:
            from database import BASE_URL, get_safe_email
            import requests
            s_email = get_safe_email(self.user_email)
            
            # Cloud fetch request
            res = requests.get(f"{BASE_URL}/users/{s_email}.json").json()
            
            if res:
                # Naam ko variable mein save karein taaki har jagah use ho sake
                self.user_full_name = res.get('full_name', 'Tractor Owner')
                
                screen = self.root.ids.screen_manager.get_screen('profile')
                
                # Profile Screen ki header wali ID update karein
                screen.ids.profile_full_name.text = str(self.user_full_name)
                
                # Baki details update karein
                screen.ids.email_info.value = str(res.get('email', self.user_email))
                screen.ids.phone_info.value = str(res.get('phone', 'N/A'))
                screen.ids.address_info.value = str(res.get('address', 'N/A'))
                
                # Agar Dashboard par bhi naam hai, toh use bhi update kar dein
                if hasattr(self.root.ids, 'user_name_label'):
                    self.root.ids.user_name_label.text = self.user_full_name
                        
        except Exception as e:
            print(f"Cloud Profile Load Error: {e}")
    # ================= DELETE ACCOUNT STEPS =================
    
    # STEP 1: Confirmation Dialog
    def show_delete_account_dialog(self):
        self.delete_dialog = MDDialog(
            title="Account Delete Karein?",
            text="Kya aap pakka apna account band karna chahte hain? Aapka saara data cloud se delete ho jayega.",
            buttons=[
                MDFlatButton(text="NAHI", on_release=lambda x: self.delete_dialog.dismiss()),
                MDRaisedButton(
                    text="HAAN, AGE BADHEIN",
                    md_bg_color=(1, 0, 0, 1),
                    on_release=lambda x: self.ask_password_for_delete() 
                ),
            ],
        )
        self.delete_dialog.open()

    # STEP 2: Password Identity Verify
    def ask_password_for_delete(self):
        self.delete_dialog.dismiss() 

        self.confirm_pwd_field = MDTextField(
            hint_text="Confirm Password",
            password=True,
            mode="rectangle",
            helper_text="Identity verify karna zaroori hai",
            helper_text_mode="on_error"
        )

        self.password_dialog = MDDialog(
            title="Password Bhariye",
            type="custom",
            content_cls=MDBoxLayout(
                self.confirm_pwd_field,
                orientation="vertical",
                adaptive_height=True,
                padding=("10dp", "20dp", "10dp", "10dp"),
                spacing="10dp"
            ),
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda x: self.password_dialog.dismiss()),
                MDRaisedButton(
                    text="DELETE PERMANENTLY",
                    md_bg_color=(1, 0, 0, 1),
                    on_release=lambda x: self.verify_and_confirm_delete()
                ),
            ],
        )
        self.password_dialog.open()

    # STEP 3: Final Delete Action (Firebase)
    # STEP 3: Final Delete Action (Firebase Database + Auth)
    def verify_and_confirm_delete(self):
        entered_password = self.confirm_pwd_field.text.strip()
        email = self.user_email
        # Aapki API Key (Firebase Project Settings se milti hai)
        API_KEY = "AIzaSyAc2VmcRaEiT6ni0EKOoVP7xa3xl6GOMkE" 

        if not entered_password:
            self.confirm_pwd_field.error = True
            return

        try:
            from database import BASE_URL, get_safe_email
            import requests
            s_email = get_safe_email(email)
            
            # --- 1. Identity Verify (Firebase Auth Login) ---
            login_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
            login_res = requests.post(login_url, json={
                "email": email, 
                "password": entered_password, 
                "returnSecureToken": True
            })
            
            if login_res.status_code == 200:
                id_token = login_res.json()['idToken']

                # --- 2. Firebase Authentication se User Record Delete ---
                auth_delete_url = f"https://identitytoolkit.googleapis.com/v1/accounts:delete?key={API_KEY}"
                auth_res = requests.post(auth_delete_url, json={"idToken": id_token})

                if auth_res.status_code == 200:
                    # --- 3. REALTIME DATABASE se saara data delete karein ---
                    # Ye list aapke database.py ke folders ke hisaab se hai
                    paths_to_delete = [
                        f"users/{s_email}",                # Profile Data
                        f"customer_jobs/{s_email}",        # Customer Entries
                        f"daily_income/{s_email}",         # Income Transactions
                        f"income_details/{s_email}",       # Reports Data
                        f"fuel_records/{s_email}",         # Fuel Data
                        f"maintenance_records/{s_email}",  # Maintenance Data
                        f"drivers/{s_email}",              # Driver Records
                        f"loan_config/{s_email}",          # Finance Settings
                        f"finance_hafta/{s_email}"         # Installments
                    ]

                    for path in paths_to_delete:
                        # Har folder se is user ka data permanently remove ho jayega
                        requests.delete(f"{BASE_URL}/{path}.json")

                    self.password_dialog.dismiss()
                    self.show_msg("Account aur saara data permanently delete ho gaya!", "success")
                    self.logout() # User ko login screen par bhej dega
                else:
                    self.show_msg("Authentication error! Kripya dobara koshish karein.", "error")
            else:
                self.confirm_pwd_field.error = True
                self.show_msg("Galat password! Suraksha ke liye account delete nahi kiya gaya.", "error")

        except Exception as e:
            print(f"Full Delete Error: {e}")
            self.show_msg("Network error! Server se sampark nahi ho saka.", "error")
#=====================================================forgotton password=================================
    # --- FORGOT PASSWORD FLOW ---
    # ================= FORGOT PASSWORD (FIREBASE) =================

    def show_forgot_password_dialog(self):
        """1. Email mangne wala dialog (Professional Way)"""
        self.forgot_email_field = MDTextField(
            hint_text="Apni registered Email ID bhariye",
            mode="rectangle",
            helper_text="Hum aapko password reset link bhejenge",
            helper_text_mode="on_focus"
        )
        
        self.forgot_dialog = MDDialog(
            title="Password Reset Karein",
            type="custom",
            content_cls=MDBoxLayout(
                self.forgot_email_field, 
                orientation="vertical", 
                adaptive_height=True,
                padding=(0, "10dp", 0, 0)
            ),
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda x: self.forgot_dialog.dismiss()),
                MDRaisedButton(
                    text="SEND RESET LINK", 
                    on_release=lambda x: self.send_firebase_reset_link()
                )
            ],
        )
        self.forgot_dialog.open()

    def send_firebase_reset_link(self):
        """2. Firebase Auth ke zariye reset email bhejna"""
        email = self.forgot_email_field.text.strip()
        
        if not email or "@" not in email:
            self.forgot_email_field.error = True
            self.show_msg("Kripya sahi Email ID bhariye", "error")
            return

        import requests
        # Aapki API Key
        API_KEY = "AIzaSyAc2VmcRaEiT6ni0EKOoVP7xa3xl6GOMkE"
        reset_url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={API_KEY}"

        try:
            # Firebase ko request bhejna
            response = requests.post(reset_url, json={
                "requestType": "PASSWORD_RESET",
                "email": email
            })
            res_data = response.json()

            if response.status_code == 200:
                self.forgot_dialog.dismiss()
                self.show_msg(f"Success! Reset link aapke email {email} par bhej diya gaya hai.", "success")
                
                # Note: Jab user link se password badal lega, toh humein 
                # Realtime Database mein bhi update karna hoga (Optional but good)
                # Hum naya password login ke time sync kar sakte hain.
                
            else:
                err = res_data.get('error', {}).get('message', '')
                if "EMAIL_NOT_FOUND" in err:
                    self.show_msg("Ye Email hamare record mein nahi hai!", "error")
                else:
                    self.show_msg(f"Error: {err}", "error")

        except Exception as e:
            self.show_msg("Internet Error! Check karein.", "error")
    

if __name__ == "__main__":
    TractorApp().run()