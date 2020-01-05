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
            print("\n1.Process Requests")
            print("2.Rate assigned youngster")
            print("3.Update profile info")
            print("4.Exit")
            action = int(input("Enter your choice: "))
            if action==1:
                self.process_requests(eid)
            elif action==2:
                self.add_review(eid)
            elif action==3:
                self.update_info(eid)
            elif action==4:
                break
            else:
                print("Invalid option. Please provide numeric value corresponding to your choice above.")

    def process_requests(self,eid):
        c.execute("SELECT * FROM REQUEST_DATA WHERE ELDER_ID=?",(eid,))
        res = c.fetchone()
        if not res:
            print("No pending requests")
            return
        c.execute("""SELECT YOUNG_DATA.Y_ID FROM YOUNG_DATA INNER JOIN REQUEST_DATA ON YOUNG_DATA.Y_ID=REQUEST_DATA.YOUNG_ID
                    WHERE REQUEST_DATA.ELDER_ID=?""",(eid,))
        reviewee = c.fetchall()
        r = Reviews()
        r.print_reviews(reviewee,'elder')

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
        
    def add_review(self,eid):
        c.execute("SELECT * FROM ASSIGNED_DATA WHERE ELDER_ID=?",(eid,))
        res = c.fetchone()
        if not res:
            print("You are not assigned any youngster to rate and review.")
            return
        # List youngster taking care of given elder
        c.execute("""SELECT YOUNG_DATA.Y_ID, YOUNG_DATA.Y-NAME, YOUNG_DATA.Y_AGE FROM YOUNG_DATA
                    INNER JOIN ASSIGNED_DATA ON ASSIGNED_DATA.YOUNG_ID = YOUNG_DATA.Y_ID WHERE ELDER_ID=?""",(eid,))
        tup = c.fetchone()
        print(tup)
        yid = tup[0]
        while True:
            rating = int(input("Enter rating out of 5: "))
            if 0<=rating<=5:
                break
        review = str(input("Enter your review: "))
        r = Reviews()
        r.create_update_review(eid,yid,rating,review)
        
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
            print("2.Rate assigned elder.")
            print("3.Update profile info.")
            print("4.Assigned elders list.")
            print("5.Salary")
            print("6.Exit")
            x = int(input("Enter your choice: "))
            if x==1:
                self.make_request(yid)
            elif x==2:
                self.add_review(yid)
            elif x==3:
                self.update_info(yid)
            elif x==4:
                self.get_assigned_elders(yid)
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
            
            c.execute("""SELECT E_ID FROM ELDER_DATA WHERE E_STATUS = 'Not Taken' """)
            reviewee = c.fetchall()
            r = Reviews()
            r.print_reviews(reviewee,'young')

            print("\n1.Send request.")
            print("2.exit")
            action = int(input("Enter your choice: "))
            if action == 1:
                rid = int(input("Enter Id to make request: "))
                r_status = 'Pending'
                c.execute("INSERT INTO REQUEST_DATA(ELDER_ID,YOUNG_ID,REQUEST_STATUS) VALUES(?,?,?)",(rid,yid,r_status))
                conn.execute("COMMIT")
            elif action==2:
                return
            else:
                print("Invalid option. Please provide numeric value corresponding to your choice above.")


    def add_review(self,yid):
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
        while True:
            rating = int(input("Enter rating out of 5: "))
            if 0<=rating<=5:
                break
        review = str(input("Enter your review: "))
        r = Reviews()
        r.create_update_review(yid,eid,rating,review)
        
    def update_info(self,yid):
        age = int(input("Enter age: "))
        c.execute("UPDATE YOUNG_DATA SET Y_AGE=? WHERE Y_ID=?",(age,yid,))
        conn.execute("COMMIT")

    def get_assigned_elders(self,yid):
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

class Reviews:
    def print_reviews(self, reviewees, reviewer_type):
        if reviewer_type == 'elder':
            for i in reviewees:
                c.execute("""SELECT R.REVIEWEE_ID, Y.Y_NAME, Y.Y_AGE, R.REVIEW, R.RATING FROM REVIEW_RATING_DATA AS R INNER JOIN YOUNG_DATA AS Y ON 
                            R.REVIEWEE_ID = Y.Y_ID WHERE R.REVIEWEE_ID = ?""",(i,))
                print("(REVIEWEE ID, NAME, AGE, COMMENT, RATING)")
                print(c.fetchall())
        else:
            for i in reviewees:
                    c.execute("""SELECT R.REVIEWEE_ID, E.E_NAME, E.E_AGE, E.E_FUND, R.REVIEW, R.RATING FROM REVIEW_RATING_DATA AS R INNER JOIN ELDER_DATA AS E ON 
                                R.REVIEWEE_ID = E.E_ID WHERE R.REVIEWEE_ID = ?""",(i,))
                    print("(REVIEWEE ID, NAME, AGE, FUND, COMMENT, RATING)")
                    print(c.fetchall())
        

    def create_update_review(self, reviewer, reviewee, rating, comment):
        c.execute("SELECT * FROM REVIEW_RATING_DATA WHERE REVIEWER_ID=? AND REVIEWEE_ID=?",(reviewer,reviewee))
        res = c.fetchone()
        if res:
             # If a review exists already, update record
            c.execute("UPDATE REVIEW_RATING_DATA SET REVIEW = ?, RATING = ? WHERE REVIEWER_ID = ? AND REVIEWEE_ID = ?",(comment,rating,reviewer,reviewee))
        else:
             # else, create a new record
            c.execute("INSERT INTO REVIEW_RATING_DATA(REVIEWER_ID, REVIEWEE_ID, REVIEW, RATING) VALUES(?,?,?,?)",(reviewer,reviewee,comment,rating))
        conn.execute("COMMIT")

    
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
