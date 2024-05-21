import json


class FireBase:
    def Register_user(self, phone, username, password):
        import firebase_admin
        firebase_admin._apps.clear()
        from firebase_admin import credentials, initialize_app, db
        if not firebase_admin._apps:
            try:
                cred = credentials.Certificate("credential/farmzon-abdcb-c4c57249e43b.json")
                initialize_app(cred, {'databaseURL': 'https://farmzon-abdcb.firebaseio.com/'})
                store = db.reference("Gerente").child("Company").child(phone).child('Info_Company')
                store.set({
                    "Total_earnings": 0,
                    "Total_sms": 10,
                    "Total_buyers": 0,
                    "Today_transactions": 0,
                    "Net_earnings": 0,
                })
                store = db.reference("Gerente").child("Company").child(phone).child('User_Info')
                store.set({
                    "user_name": username,
                    "user_phone": phone,
                    "user_password": password,
                })
            except:
                return "No Internet!"

    def get_user(self, phone):
        import firebase_admin
        firebase_admin._apps.clear()
        from firebase_admin import credentials, initialize_app, db
        if not firebase_admin._apps:
            try:
                cred = credentials.Certificate("credential/farmzon-abdcb-c4c57249e43b.json")
                initialize_app(cred, {'databaseURL': 'https://farmzon-abdcb.firebaseio.com/'})
                store = db.reference("Gerente").child("Company").child(phone)
                stores = store.get()
                return stores
            except:
                return "No Internet!"

    def add_buyer(self, data, phone):
        import firebase_admin
        firebase_admin._apps.clear()
        from firebase_admin import credentials, initialize_app, db
        if not firebase_admin._apps:
            try:
                cred = credentials.Certificate("credential/farmzon-abdcb-c4c57249e43b.json")
                initialize_app(cred, {'databaseURL': 'https://farmzon-abdcb.firebaseio.com/'})
                print("again!!!!!!!!!", data)
                for x, y in data.items():
                    store = db.reference("Gerente").child("Company").child(phone).child('Buyers').child(y)
                    store.set({
                        "buyer_name": x,
                        "buyer_number": y,
                        "total_spending": "0",
                        "total_product": "0",
                        "location_region": "0"
                    })
                    print("Done!!!!")
            except:
                return "No Internet!"

    def add_attender(self, phone, name, gen_id, ceremony_name):
        import firebase_admin
        firebase_admin._apps.clear()
        from firebase_admin import credentials, initialize_app, db
        if not firebase_admin._apps:
            try:
                cred = credentials.Certificate("credential/farmzon-abdcb-c4c57249e43b.json")
                initialize_app(cred, {'databaseURL': 'https://farmzon-abdcb.firebaseio.com/'})
                store = db.reference("Ceremony").child(ceremony_name).child('Info_Ceremony')
                store.set({
                    "Attended": 0,
                })
                store = db.reference("Ceremony").child(ceremony_name).child(phone).child('User_Info')
                store.set({
                    "user_name": name,
                    "user_phone": phone,
                    "user_password": gen_id,
                    "scanned": 0
                })
            except:
                return "No Internet!"

    def search_id(self, gen_id):
        import firebase_admin
        from firebase_admin import credentials, initialize_app, db

        # Clear existing Firebase apps to avoid conflicts
        firebase_admin._apps.clear()

        try:
            # Initialize Firebase app with credentials and database URL
            cred = credentials.Certificate("credential/farmzon-abdcb-c4c57249e43b.json")
            initialize_app(cred, {'databaseURL': 'https://farmzon-abdcb.firebaseio.com/'})

            # Get a reference to the Firebase database node containing user information
            users_ref = db.reference("Ceremony")

            # Query the database to find the user with the specified gen_id
            user_info = None
            for ceremony_name in users_ref.get().keys():
                ceremony_ref = users_ref.child(ceremony_name)
                for phone_number in ceremony_ref.get().keys():
                    user_ref = ceremony_ref.child(phone_number).child('User_Info')
                    user_data = user_ref.get()
                    if user_data and user_data.get("user_password") == gen_id:
                        # Found the user with the specified gen_id
                        user_info = user_data
                        break
                if user_info:
                    break

            return user_info

        except Exception as e:
            return f"Error: {e}"

    def scan_guest(self, gen_id):
        import firebase_admin
        from firebase_admin import credentials, initialize_app, db

        # Clear existing Firebase apps to avoid conflicts
        firebase_admin._apps.clear()

        try:
            # Initialize Firebase app with credentials and database URL
            cred = credentials.Certificate("credential/farmzon-abdcb-c4c57249e43b.json")
            initialize_app(cred, {'databaseURL': 'https://farmzon-abdcb.firebaseio.com/'})

            # Get a reference to the Firebase database node containing user information
            users_ref = db.reference("Ceremony")

            # Query the database to find the user with the specified gen_id
            user_info = None
            user_ref_to_update = None
            ceremony_name_to_update = None
            for ceremony_name in users_ref.get().keys():
                ceremony_ref = users_ref.child(ceremony_name)
                for phone_number in ceremony_ref.get().keys():
                    user_ref = ceremony_ref.child(phone_number).child('User_Info')
                    user_data = user_ref.get()
                    if user_data and user_data.get("user_password") == gen_id:
                        # Found the user with the specified gen_id
                        user_info = user_data
                        user_ref_to_update = user_ref
                        ceremony_name_to_update = ceremony_name
                        break
                if user_info:
                    break

            if user_info:
                if user_info.get("scanned") == 0:
                    # Update the scanned field to 1
                    user_ref_to_update.update({"scanned": 1})

                    # Increment the Attended field
                    attended_ref = users_ref.child(ceremony_name_to_update).child('Info_Ceremony').child('Attended')
                    attended_count = attended_ref.get()
                    attended_ref.set(attended_count + 1)

                    return "User scanned status updated to 1 and Attended count incremented"
                else:
                    return "User has already been scanned"
            else:
                return "User not found"

        except Exception as e:
            return f"Error: {e}"


# x = FireBase.scan_guest(FireBase(), "20240510112246919903")
# print(x)

