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

        try:
            # Initialize Firebase app with credentials and database URL
            cred = credentials.Certificate("credential/farmzon-abdcb-c4c57249e43b.json")
            initialize_app(cred, {'databaseURL': 'https://farmzon-abdcb.firebaseio.com/'})

            # Reference to the ceremony's info node
            ceremony_info_ref = db.reference("Ceremony").child(ceremony_name).child('Info_Ceremony')

            # Check if the ceremony info node already exists
            if not ceremony_info_ref.get():
                # If not, initialize it with Attended and Total_Attenders counters
                ceremony_info_ref.set({
                    "Attended": 0,
                    "Total_Attenders": 0
                })

            # Reference to the user's info node
            user_info_ref = db.reference("Ceremony").child(ceremony_name).child(phone).child('User_Info')

            # Check if the user already exists
            if user_info_ref.get():
                return "User already exists!"

            # Set the user info
            user_info_ref.set({
                "user_name": name,
                "user_phone": phone,
                "user_password": gen_id,
                "scanned": 0
            })

            # Increment the Total_Attenders counter
            total_attenders_ref = ceremony_info_ref.child('Total_Attenders')
            total_attenders_count = total_attenders_ref.get()
            total_attenders_ref.set(total_attenders_count + 1)

            return "User added successfully!"

        except Exception as e:
            return f"No Internet! Error: {e}"

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
        from datetime import datetime

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
                    # Update the scanned field to 1 and add the scanned_time
                    current_time = datetime.now().isoformat()
                    user_ref_to_update.update({
                        "scanned": 1,
                        "scanned_time": current_time
                    })

                    # Increment the Attended field
                    attended_ref = users_ref.child(ceremony_name_to_update).child('Info_Ceremony').child('Attended')
                    attended_count = attended_ref.get()
                    attended_ref.set(attended_count + 1)

                    return "User scanned status updated to 1, scanned time added, and Attended count incremented"
                else:
                    return "User has already been scanned"
            else:
                return "User not found"

        except Exception as e:
            return f"Error: {e}"

    def ceremony_report(self, ceremony_name):
        import firebase_admin
        from firebase_admin import credentials, initialize_app, db

        # Initialize Firebase app
        if not firebase_admin._apps:
            cred = credentials.Certificate("credential/farmzon-abdcb-c4c57249e43b.json")
            initialize_app(cred, {'databaseURL': 'https://farmzon-abdcb.firebaseio.com/'})

        try:
            # References
            ceremony_info_ref = db.reference("Ceremony").child(ceremony_name).child('Info_Ceremony')
            guests_ref = db.reference("Ceremony").child(ceremony_name)

            # Fetch total guest count and attended count
            ceremony_info = ceremony_info_ref.get()
            total_guest = ceremony_info.get("Total_Attenders", 0)
            attended_guest = ceremony_info.get("Attended", 0)

            # Fetch details of all guests
            guests = guests_ref.get()
            not_attended = []

            # Traverse through guests to find those who haven't attended
            for phone, data in guests.items():
                if phone != 'Info_Ceremony' and 'User_Info' in data:
                    user_info = data['User_Info']
                    if user_info.get('scanned', 0) == 0:
                        not_attended.append({
                            "name": user_info.get("user_name", ""),
                            "phone": user_info.get("user_phone", "")
                        })

            # Preparing the report
            report = {
                "attended_guest": attended_guest,
                "total_guest": total_guest,
                "not_attended": not_attended
            }

            return report

        except Exception as e:
            return {"error": f"An error occurred: {e}"}

    def guest_report(self, gen_id="", phone=""):
        import firebase_admin
        from firebase_admin import credentials, initialize_app, db

        # Initialize Firebase app
        if not firebase_admin._apps:
            cred = credentials.Certificate("credential/farmzon-abdcb-c4c57249e43b.json")
            initialize_app(cred, {'databaseURL': 'https://farmzon-abdcb.firebaseio.com/'})

        try:
            # References
            ceremony_ref = db.reference("Ceremony")

            # Initialize an empty report
            report = {"attended_time": "", "guest_phone": "", "guest_name": ""}

            # Search by gen_id
            if gen_id:
                found = False
                ceremonies = ceremony_ref.get()
                for ceremony_name, data in ceremonies.items():
                    for phone, user_data in data.items():
                        if phone != 'Info_Ceremony' and 'User_Info' in user_data:
                            user_info = user_data['User_Info']
                            if user_info.get('user_password') == gen_id:
                                report['guest_phone'] = user_info.get('user_phone', '')
                                report['guest_name'] = user_info.get('user_name', '')
                                report['attended_time'] = user_info.get('time', '')
                                found = True
                                break
                    if found:
                        break

            # Search by phone
            elif phone:
                found = False
                ceremonies = ceremony_ref.get()
                for ceremony_name, data in ceremonies.items():
                    if phone in data and 'User_Info' in data[phone]:
                        user_info = data[phone]['User_Info']
                        report['guest_phone'] = user_info.get('user_phone', '')
                        report['guest_name'] = user_info.get('user_name', '')
                        report['attended_time'] = user_info.get('time', '')
                        found = True
                        break

            return report

        except Exception as e:
            return {"error": f"An error occurred: {e}"}

    def fetch_all_guest(self, ceremony_name):
        guests = [{"phaone": "", "attended": ""}]

# x = FireBase.scan_guest(FireBase(), "20240510112246919903")
# print(x)

# r = FireBase.ceremony_report(FireBase(), "Mbuyas")
# print(r)

# gr = FireBase.guest_report(FireBase(), phone="0715700411")
# print(gr)
