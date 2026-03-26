import pandas as pd
import os
from datetime import datetime
from config import DATA_FILE

class StorageService:
    def __init__(self):
        self.columns = [
            "Telegram ID", "Full Name", "Delivery Address", "Phone Number", 
            "Preferred Start Date", "Dietary Preferences", "Product", "Duration", 
            "Price", "Status", "Timestamp"
        ]
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(DATA_FILE):
            df = pd.DataFrame(columns=self.columns)
            df.to_excel(DATA_FILE, index=False)

    def add_subscription(self, telegram_id, full_name, address, phone, start_date, diet, product, duration, price, status="Onboarded"):
        # We need to handle potential schema mismatches if the file already exists with old columns.
        if os.path.exists(DATA_FILE):
            try:
                df = pd.read_excel(DATA_FILE)
            except ValueError:
                df = pd.DataFrame(columns=self.columns)
            
            # Ensure new columns exist
            for col in self.columns:
                if col not in df.columns:
                    df[col] = ""
        else:
            df = pd.DataFrame(columns=self.columns)
            
        new_row = {
            "Telegram ID": telegram_id,
            "Full Name": full_name,
            "Delivery Address": address,
            "Phone Number": phone,
            "Preferred Start Date": start_date,
            "Dietary Preferences": diet,
            "Product": product,
            "Duration": duration,
            "Price": price,
            "Status": status,
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        # reorder columns
        df = df[self.columns]
        df.to_excel(DATA_FILE, index=False)

    def update_status(self, telegram_id, new_status):
        if not os.path.exists(DATA_FILE): return False
        try:
            df = pd.read_excel(DATA_FILE)
        except ValueError:
            return False
            
        user_rows = df[df["Telegram ID"] == telegram_id]
        if not user_rows.empty:
            latest_idx = user_rows.index[-1]
            df.at[latest_idx, "Status"] = new_status
            df.to_excel(DATA_FILE, index=False)
            return True
        return False
