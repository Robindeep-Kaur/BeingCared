import sys

from InitializeDB import connect_db

try:
    conn, c = connect_db()
except Exception:
    print("Error connecting to database. Exiting..")
    sys.exit(1)


class Elder:
    def registration(self):
        eid = int(input("\nCreate login (enter unique integer ID): "))
        while True:
            c.execute("SELECT * FROM ELDER_DATA WHERE E_ID=?",(eid,))
            res = c.fetchone()
            if res:
                eid = int(input("ID already exists, choose another: "))
            else:
                break
        name = input("Enter your name: ")
        age = int(input("Enter age: "))
        fund = int(input("Enter fund to allocate: "))
        status = 'Not Taken'
        record=(eid,name,age,fund,status)
        c.execute("""INSERT INTO ELDER_DATA(E_ID,E_NAME,E_AGE,E_FUND,E_STATUS)
                  VALUES(?,?,?,?,?)""",record)
        conn.execute("COMMIT")

    def login(self):
        eid = int(input("Enter ID: "))
        c.execute("SELECT * FROM ELDER_DATA WHERE E_ID=?",(eid,))
        res = c.fetchone()
        if not res:
            print("ID does not exist")
            return
        c.execute("""SELECT * FROM ELDER_DATA WHERE E_ID = ?""",(eid,))
        print("(ID, NAME, AGE, FUND, STATUS)")
        print(next(c))
        while True:
            e = Elder()
            print("\n1.Display Requests")
            print("2.Rate and Review")
            print("3.Update Info")
            print("4.Exit")
            action = int(input("Enter your choice: "))
            if action==1:
                e.display_requests(eid)
            elif action==2:
                e.rate_and_review(eid)
            elif action==3:
                e.update_info(eid)
            elif action==4:
                break
            else:
                print("Invalid option. Please provide numeric value corresponding to your choice above.")

    def display_requests(self,eid):
        c.execute("SELECT * FROM REQUEST_DATA WHERE ELDER_ID=?",(eid,))
        res = c.fetchone()
        if not res:
            print("No pending requests")
            return
        c.execute("""SELECT * FROM YOUNG_DATA INNER JOIN REQUEST_DATA ON YOUNG_DATA.Y_ID=REQUEST_DATA.YOUNG_ID
                    WHERE REQUEST_DATA.ELDER_ID=?""",(eid,))
        print("(ID, NAME, AGE)")
        for row in c:
            print(row)
        print("\n1.Approve request.")
        print("2.Decline all.")
        print("3.Exit")
        action = int(input("Enter your choice: "))
        if action == 1:
            aid = int(input("Enter ID to approve: "))
            c.execute("INSERT INTO ASSIGNED_DATA(ELDER_ID,YOUNG_ID) VALUES(?,?)",(eid,aid))
            c.execute("UPDATE ELDER_DATA SET E_STATUS = 'Taken' WHERE E_ID=?",(eid,))
            c.execute("SELECT COUNT(ELDER_ID) FROM ASSIGNED_DATA WHERE YOUNG_ID=?",(aid,))
            q = c.fetchone()
            if q[0] == 4:
                c.execute("UPDATE REQUEST_DATA SET REQUEST_STATUS='AutoDeclined' WHERE YOUNG_ID=?",(aid,))
            c.execute("UPDATE REQUEST_DATA SET REQUEST_STATUS='AutoDeclined' WHERE ELDER_ID=?",(eid,))
        elif action == 2:
            c.execute("UPDATE REQUEST_DATA SET REQUEST_STATUS='Declined' WHERE ELDER_ID=?",(eid,))
        elif action == 3:
            return
        else:
            print("Invalid choice. Please provide numeric value corresponding to your choice above.")
        conn.execute("COMMIT")
        
    def rate_and_review(self,eid):
        c.execute("SELECT * FROM ASSIGNED_DATA WHERE YOUNG_ID=?",(eid,))
        res = c.fetchone()
        if not res:
            print("No one to rate and review.")
            return
        c.execute("""SELECT YOUNG_DATA.Y_ID, YOUNG_DATA.Y-NAME, YOUNG_DATA.Y_AGE FROM YOUNG_DATA
                    INNER JOIN ASSIGNED_DATA ON ASSIGNED_DATA.YOUNG_ID = YOUNG_DATA.Y_ID WHERE ELDER_ID=?""",(eid,))
        tup = c.fetchone()
        print(tup)
        yid = tup[0]
        c.execute("SELECT * FROM REVIEW_RATING_DATA WHERE REVIEWER_ID=? AND REVIEWEE_ID=?",(eid,yid))
        res = c.fetchone()
        if res:
            rate = int(input("Enter rating out of 5: "))
            review = str(input("Enter your review: "))
            c.execute("UPDATE REVIEW_RATING_DATA SET REVIEW = ?, RATING = ? WHERE REVIEWER_ID = ?",(review,rate,eid))
        else:
            rate = int(input("Enter rating out of 5: "))
            review = str(input("Enter your review: "))
            c.execute("INSERT INTO REVIEW_RATING_DATA(REVIEWER_ID, REVIEWEE_ID, REVIEW, RATING) VALUES(?,?,?,?)",(eid,yid,review,rate))
        conn.execute("COMMIT")
        
    def update_info(self,eid):
        age = int(input("Enter age: "))
        fund = int(input("Enter fund: "))
        c.execute("UPDATE ELDER_DATA SET E_AGE=?, E_FUND=? WHERE E_ID=?",(age,fund,eid,))
        conn.execute("COMMIT")

        


class Youngster:
    def registration(self):

        yid = int(input("\nCreate login (enter unique integer ID): "))
        while True:
            c.execute("SELECT * FROM YOUNG_DATA WHERE Y_ID=?",(yid,))
            res = c.fetchone()
            if res:
                yid = int(input("ID already exists, choose another: "))
            else:
                break
        name = input("Enter your name: ")
        age = int(input("Enter your age: "))
        salary = 0
        rating = 0
        review = 'None'
        record = (yid,name,age,salary)
        c.execute("""INSERT INTO YOUNG_DATA(Y_ID,Y_NAME,Y_AGE,Y_SALARY)
                  VALUES(?,?,?,?)""",record)
        conn.execute("COMMIT")

    def login(self):
        yid = int(input("Enter ID: "))
        c.execute("SELECT * FROM YOUNG_DATA WHERE Y_ID=?",(yid,))
        res = c.fetchone()
        if not res:
            print("ID does not exist")
            return
        c.execute("""SELECT * FROM YOUNG_DATA WHERE Y_ID = ? """,(yid,))
        print("(ID, NAME, AGE, SALARY)")
        print(next(c))
        while True:
            print("1.Make Request")
            print("2.Rate and Review")
            print("3.Update info")
            print("4.Assigned Elders")
            print("5.Salary")
            print("6.Exit")
            x = int(input("Enter your choice: "))
            if x==1:
                self.make_request(yid)
            elif x==2:
                self.rate_and_review(yid)
            elif x==3:
                self.update_info(yid)
            elif x==4:
                self.assigned_elders(yid)
            elif x==5:
                self.salary(yid)
            elif x==6:
                break
            else:
                print("Invalid option. Please provide numeric value corresponding to your choice above.")

    def make_request(self,yid):
        c.execute("SELECT * FROM ELDER_DATA WHERE E_STATUS='Not Taken")
        res = c.fetchone()
        if not res:
            print("No elder to take care of.")
            return
        c.execute("SELECT COUNT(ELDER_ID) FROM ASSIGNED_DATA WHERE YOUNG_ID=?",(yid,))
        q = c.fetchone()
        if q[0] == 4:
            print("Maximum limit reached")
        else:
            
            c.execute("""SELECT * FROM ELDER_DATA WHERE E_STATUS = 'Not Taken' """)
            for row in c:
                print(row)
            print("\n1.Send request.")
            print("2.exit")
            action = int(input("Enter your choicd: "))
            if action == 1:
                rid = int(input("Enter Id to make request: "))
                r_status = 'Pending'
                c.execute("INSERT INTO REQUEST_DATA(ELDER_ID,YOUNG_ID,REQUEST_STATUS) VALUES(?,?,?)",(rid,yid,r_status))
                conn.execute("COMMIT")
            elif action==2:
                return
            else:
                print("Invalid option. Please provide numeric value corresponding to your choice above.")


    def rate_and_review(self,yid):
        c.execute("SELECT 1 FROM ASSIGNED_DATA WHERE YOUNG_ID=?",(yid,))
        res = c.fetchone()
        if not res:
            print("No one to rate and review.")
            return
        c.execute("""SELECT ELDER_DATA.E_ID, ELDER_DATA.E_NAME, ELDER_DATA.E_AGE FROM ELDER_DATA
                    INNER JOIN ASSIGNED_DATA ON ASSIGNED_DATA.ELDER_ID=ELDER_DATA.E_ID
                    WHERE ASSIGNED_DATA.YOUNG_ID=?""",(yid,))
        print("(ID, NAME, AGE)")
        for row in c:
            print(row)
        eid = int(input("Enter Id to rate and review: "))
        c.execute("SELECT * FROM REVIEW_RATING_DATA WHERE REVIEWER_ID=? AND REVIEWEE_ID=?",(eid,yid))
        res = c.fetchone()
        if res:
            # If a review exists already, update record
            rate = int(input("Enter rating out of 5: "))
            review = str(input("Enter your review: "))
            c.execute("UPDATE REVIEW_RATING_DATA SET REVIEW = ?, RATING = ? WHERE REVIEWER_ID = ?",(review,rate,yid))
        else:
            # else, create a new record
            rate = int(input("Enter rating out of 5: "))
            review = str(input("Enter your review: "))
            c.execute("INSERT INTO REVIEW_RATING_DATA(REVIEWER_ID, REVIEWEE_ID, REVIEW, RATING) VALUES(?,?,?,?)",(yid,eid,review,rate))
        conn.execute("COMMIT")
        
    def update_info(self,yid):
        age = int(input("Enter age: "))
        c.execute("UPDATE YOUNG_DATA SET Y_AGE=? WHERE Y_ID=?",(age,yid,))
        conn.execute("COMMIT")

    def assigned_elders(self,yid):
        c.execute("""SELECT * FROM ELDER_DATA INNER JOIN ASSIGNED_DATA ON
                  ASSIGNED_DATA.ELDER_ID=ELDER_DATA.E_ID WHERE YOUNG_ID=?""",(yid,))
        for row in c:
            print(row)

    def salary(self,yid):
        c.execute("""SELECT E_ID,E_NAME,E_FUND FROM ELDER_DATA INNER JOIN ASSIGNED_DATA
                    ON ASSIGNED_DATA.ELDER_ID=ELDER_DATA.E_ID WHERE ASSIGNED_DATA.YOUNG_ID=?""",(yid,))
        for row in c:
            print(row)
        c.execute("""SELECT SUM(E_FUND) FROM ELDER_DATA INNER JOIN ASSIGNED_DATA ON
                    ASSIGNED_DATA.ELDER_ID=ELDER_DATA.E_ID WHERE ASSIGNED_DATA.YOUNG_ID = ? """,(yid,))
        print("Your salary: ",next(c))


def main():
    while True:
        print("1.Elder")
        print("2.Youngster")
        print("3.Exit")
        user_class = int(input("\nSelect user type (indicate numeric choice): "))
        if user_class==1:
            e = Elder()
            print("\n1.Register")
            print("2.Login")
            print("3.Exit")
            action = int(input("\nEnter your choice: "))
            if action==1:
                e.registration()
            elif action==2:
                e.login()
            elif action==3:
                break
            else:
                print("Invalid choice. Please provide numeric value corresponding to your choice above.")
        elif user_class==2:
            y = Youngster()
            print("\n1.Register")
            print("2.Login")
            print("3.Exit")
            action = int(input("\nEnter your choice: "))
            if action==1:
                y.registration()
            elif action==2:
                y.login()
            elif action==3:
                break
            else:
                print("Invalid choice. Please provide numeric value corresponding to your choice above.")
        elif user_class==3:
            break
        else:
            print("Invalid option. Please provide numeric value corresponding to your choice above.")


if __name__ == "__main__":
    sys.exit(main())
