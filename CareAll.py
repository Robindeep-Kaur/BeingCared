import sys

from InitializeDB import connect_db

try:
    conn, c = connect_db()
except Exception:
    print("Error connecting to database. Exiting..")
    sys.exit(1)


class Elder:
    def registration(self):
        """ Class method used to register elder couples. """
        eid = int(input("\nCreate login (enter unique integer ID): "))
        # Check whether the ID is already present.
        while True:
            c.execute("SELECT * FROM ELDER_DATA WHERE E_ID=?",(eid,))
            res = c.fetchone()
            if res:
                eid = int(input("ID already exists, choose another: "))
            else:
                break
        # Input other elder details.
        name = input("Enter your name: ")
        age = int(input("Enter age: "))
        fund = int(input("Enter fund to allocate: "))
        status = 'Not Taken'
        record=(eid,name,age,fund,status)
        c.execute("""INSERT INTO ELDER_DATA(E_ID,E_NAME,E_AGE,E_FUND,E_STATUS)
                  VALUES(?,?,?,?,?)""",record)
        conn.execute("COMMIT")

    def login(self):
        """ Class method used to log in the elder couple and manage the 
        account using different set of options provided in the menu """
        eid = int(input("Enter ID: "))
        # Check whether the ID exists.
        c.execute("SELECT 1 FROM ELDER_DATA WHERE E_ID=?",(eid,))
        res = c.fetchone()
        if not res:
            print("ID does not exist")
            return
        # Display information of the user itself.
        c.execute("""SELECT * FROM ELDER_DATA WHERE E_ID = ?""",(eid,))
        print("(ID, NAME, AGE, FUND, STATUS)")
        print(next(c))
        # Menu to manage the account by calling other class methods.
        while True:
            print("\n1.Process Requests")
            print("2.Rate assigned youngster")
            print("3.Update profile info")
            print("4.Assigned youngster's info. ")
            print("5.Exit\n")
            action = int(input("Enter your choice: "))
            if action==1:
                self.process_requests(eid)
            elif action==2:
                self.add_review(eid)
            elif action==3:
                self.update_info(eid)
            elif action==4:
                self.get_assigned_youngster(eid)
            elif action==5:
                break
            else:
                print("Invalid option. Please provide numeric value corresponding to your choice above.")

    def process_requests(self,eid):
        """ Class method used to process and display the requests received from youngsters.
        The user can approve a single request or can decline all the requests."""
        # Check whether there is any request.
        c.execute("SELECT * FROM REQUEST_DATA WHERE ELDER_ID=?",(eid,))
        res = c.fetchone()
        if not res:
            print("No pending requests")
            return
        # Display data of youngster who sent the request.
        c.execute("""SELECT YOUNG_DATA.Y_ID FROM YOUNG_DATA INNER JOIN REQUEST_DATA ON YOUNG_DATA.Y_ID=REQUEST_DATA.YOUNG_ID
                    WHERE REQUEST_DATA.REQUEST_STATUS = 'Pending' AND REQUEST_DATA.ELDER_ID=?""",(eid,))
        reviewee = c.fetchall()
        if not reviewee:
            print("No requests to display.")
            return
        # Called a function of Reviews class to print reviews of young chaps if any.
        r = Reviews()
        r.print_reviews(reviewee,'elder')

        print("\n1.Approve request.")
        print("2.Decline all.")
        print("3.Exit")
        action = int(input("Enter your choice: "))
        # Approve request and include the info in database.
        if action == 1:
            aid = int(input("Enter ID to approve: "))
            c.execute("INSERT INTO ASSIGNED_DATA(ELDER_ID,YOUNG_ID) VALUES(?,?)",(eid,aid))
            c.execute("UPDATE ELDER_DATA SET E_STATUS = 'Taken' WHERE E_ID=?",(eid,))
            c.execute("SELECT COUNT(ELDER_ID) FROM ASSIGNED_DATA WHERE YOUNG_ID=?",(aid,))
            q = c.fetchone()
            if q[0] == 4:
                c.execute("UPDATE REQUEST_DATA SET REQUEST_STATUS='AutoDeclined' WHERE YOUNG_ID=?",(aid,))
            c.execute("UPDATE REQUEST_DATA SET REQUEST_STATUS='AutoDeclined' WHERE ELDER_ID=?",(eid,))
        # Decline all the request and update the database.
        elif action == 2:
            c.execute("UPDATE REQUEST_DATA SET REQUEST_STATUS='Declined' WHERE ELDER_ID=?",(eid,))
        elif action == 3:
            return
        else:
            print("Invalid choice. Please provide numeric value corresponding to your choice above.")
        conn.execute("COMMIT")
        
    def add_review(self,eid):
        """ Class method used to add review and rating about the young chap taking care of the given elder."""
        # Check whether the elder is assigned any youngster.
        c.execute("SELECT 1 FROM ASSIGNED_DATA WHERE ELDER_ID=?",(eid,))
        res = c.fetchone()
        if not res:
            print("You are not assigned any youngster to rate and review.")
            return
        # List youngster taking care of given elder.
        c.execute("""SELECT YOUNG_DATA.Y_ID, YOUNG_DATA.Y_NAME, YOUNG_DATA.Y_AGE FROM YOUNG_DATA
                    INNER JOIN ASSIGNED_DATA ON ASSIGNED_DATA.YOUNG_ID = YOUNG_DATA.Y_ID WHERE ASSIGNED_DATA.ELDER_ID=?""",(eid,))
        tup = c.fetchone()
        print(tup)
        yid = tup[0]
        while True:
            rating = int(input("Enter rating out of 5: "))
            if 0<=rating<=5:
                break
        review = str(input("Enter your review: "))
        r = Reviews()
        # Function of class Reviews called to create or update the review of the youngster.
        r.create_update_review(eid,yid,rating,review)
        
    def update_info(self,eid):
        """ Class method used to update age and fund of the elder couple."""
        age = int(input("Enter age: "))
        fund = int(input("Enter fund: "))
        c.execute("UPDATE ELDER_DATA SET E_AGE=?, E_FUND=? WHERE E_ID=?",(age,fund,eid,))
        conn.execute("COMMIT")
    
    def get_assigned_youngster(self,eid):
        """ Class method used to display the information of the young chap 
        currently taking care of the older couple."""
        # Check whether the elder is assigned any youngster.
        c.execute("SELECT 1 FROM ASSIGNED_DATA WHERE ELDER_ID=?",(eid,))
        res = c.fetchone()
        if not res:
            print("You are not assigned any youngster.")
            return
        # Display details of youngster.
        c.execute("""SELECT Y_ID,Y_NAME,Y_AGE FROM YOUNG_DATA INNER JOIN ASSIGNED_DATA ON
                  ASSIGNED_DATA.YOUNG_ID=YOUNG_DATA.Y_ID WHERE ELDER_ID=?""",(eid,))
        print("(ID, NAME, AGE)")
        tup = c.fetchone()
        print(tup)
        # Display review of youngster if any. 
        c.execute("SELECT REVIEW, RATING FROM REVIEW_RATING_DATA WHERE REVIEWEE_ID = ?",(tup[0],))
        res1 = c.fetchall()
        if res1:
            print("(REVIEW, RATING)")
            for row in res1:
                print(row)


class Youngster:
    def registration(self):
        """ Class method used to register younger ones ready to take care of elder couple. """
        yid = int(input("\nCreate login (enter unique integer ID): "))
        # Check whether the given ID is already present.
        while True:
            c.execute("SELECT * FROM YOUNG_DATA WHERE Y_ID=?",(yid,))
            res = c.fetchone()
            if res:
                yid = int(input("ID already exists, choose another: "))
            else:
                break
        # Input other youngster details.
        name = input("Enter your name: ")
        age = int(input("Enter your age: "))
        salary = 0
        record = (yid,name,age,salary)
        c.execute("""INSERT INTO YOUNG_DATA(Y_ID,Y_NAME,Y_AGE,Y_SALARY)
                  VALUES(?,?,?,?)""",record)
        conn.execute("COMMIT")

    def login(self):
        """ Class method used to login the youngster and 
        manage the account using given set of options"""
        yid = int(input("Enter ID: "))
        # Check whether the ID exists.
        c.execute("SELECT * FROM YOUNG_DATA WHERE Y_ID=?",(yid,))
        res = c.fetchone()
        if not res:
            print("ID does not exist")
            return
        # Display information of user itself.
        c.execute("""SELECT * FROM YOUNG_DATA WHERE Y_ID = ? """,(yid,))
        print("(ID, NAME, AGE, SALARY)")
        print(next(c))
        # Calls class methods in accordance to the choosen option.
        while True:
            print("\n1.Make Request")
            print("2.Rate assigned elder.")
            print("3.Update profile info.")
            print("4.Assigned elders list.")
            print("5.Salary")
            print("6.Exit\n")
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
        """ Class method to send requests to the elder couple whom the user wishes to take care of"""
        # Check whether there is any elder that is not assigned to any youngster.
        c.execute("SELECT * FROM ELDER_DATA WHERE E_STATUS='Not Taken'")
        res = c.fetchone()
        if not res:
            print("No elder to take care of.")
            return
        # Check if the youngster has been already assigned 4 elders.
        c.execute("SELECT COUNT(ELDER_ID) FROM ASSIGNED_DATA WHERE YOUNG_ID=?",(yid,))
        q = c.fetchone()
        if q[0] == 4:
            print("Maximum limit reached")
        else:
            # If less than 4 elders are assigned.
            # Display info of elders which are not yet assigned to any youngster.
            c.execute("""SELECT E_ID FROM ELDER_DATA WHERE E_STATUS = 'Not Taken' """)
            reviewee = c.fetchall()
            r = Reviews()
            r.print_reviews(reviewee,'young')

            print("\n1.Send request.")
            print("2.exit")
            action = int(input("Enter your choice: "))
            if action == 1:
                # Request will be sent and data will be updated in database.
                rid = int(input("Enter Id to make request: "))
                r_status = 'Pending'
                c.execute("INSERT INTO REQUEST_DATA(ELDER_ID,YOUNG_ID,REQUEST_STATUS) VALUES(?,?,?)",(rid,yid,r_status))
                conn.execute("COMMIT")
            elif action==2:
                return
            else:
                print("Invalid option. Please provide numeric value corresponding to your choice above.")


    def add_review(self,yid):
        """ Class method to review and rate the elder or elders that are
         currently being taken care by the user itself."""
        # Check whether the youngster is assigned to any elder.
        c.execute("SELECT 1 FROM ASSIGNED_DATA WHERE YOUNG_ID=?",(yid,))
        res = c.fetchone()
        if not res:
            print("No one to rate and review.")
            return
        # Display info about the elder or elders that are assigned to user.
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
        # Function of class Reviews is called to create or update the review of the provided elder by the user itself.
        r.create_update_review(yid,eid,rating,review)
        
    def update_info(self,yid):
        """ Class method to update the age of the young user."""
        age = int(input("Enter age: "))
        c.execute("UPDATE YOUNG_DATA SET Y_AGE=? WHERE Y_ID=?",(age,yid,))
        conn.execute("COMMIT")

    def get_assigned_elders(self,yid):
        """ Class method to display all the information of the elders assigned currently to the young chap."""
        # Check if the youngster has been assigned to ay elder.
        c.execute("SELECT 1 FROM ASSIGNED_DATA WHERE YOUNG_ID=?",(yid,))
        res = c.fetchone()
        if not res:
            print("No elder has been assigned to you.")
            return
        # Display info about the elders currently assigned to the user.
        c.execute("""SELECT E_ID,E_NAME,E_AGE,E_FUND FROM ELDER_DATA INNER JOIN ASSIGNED_DATA ON
                  ASSIGNED_DATA.ELDER_ID=ELDER_DATA.E_ID WHERE YOUNG_ID=?""",(yid,))
        print("(ID, NAME, AGE, FUND)")
        tup = c.fetchall()
        for row in tup:
            print(row)
            # Display review if exist for the elder displayed.
            c.execute("SELECT REVIEW, RATING FROM REVIEW_RATING_DATA WHERE REVIEWEE_ID = ?",(row[0],))
            res1 = c.fetchall()
            if res1:
                print("(REVIEW, RATING)")
                for row1 in res1:
                    print(row1)

    def salary(self,yid):
        """ Class method to calculate and display salary along with the info of assigned elders."""
        # Calculate the sum of the total salary of the user.
        c.execute("""SELECT SUM(E_FUND) FROM ELDER_DATA INNER JOIN ASSIGNED_DATA ON
                    ASSIGNED_DATA.ELDER_ID=ELDER_DATA.E_ID WHERE ASSIGNED_DATA.YOUNG_ID = ? """,(yid,))
        sal = c.fetchone()
        print("Your salary: ",sal[0])
        # Check if any elder is assigned to the user.
        c.execute("SELECT 1 FROM ASSIGNED_DATA WHERE YOUNG_ID=?",(yid,))
        res = c.fetchone()
        if not res:
            return
        # If assigned elder exists then display their info.
        c.execute("""SELECT E_ID,E_NAME,E_FUND FROM ELDER_DATA INNER JOIN ASSIGNED_DATA
                    ON ASSIGNED_DATA.ELDER_ID=ELDER_DATA.E_ID WHERE ASSIGNED_DATA.YOUNG_ID=?""",(yid,))
        print("(ID, NAME, FUND)")
        for row in c:
            print(row)
        


class Reviews:
    def print_reviews(self, reviewees, reviewer_type):
        """ Class method to print the reviews of the any user if exist."""
        if reviewer_type == 'elder':
            # If the function is called from Elder class.
            print("(YOUNGER ID, NAME, AGE, COMMENT, RATING)")
            for i in reviewees:
                c.execute("SELECT Y_ID, Y_NAME, Y_AGE FROM YOUNG_DATA WHERE Y_ID = ?",(i[0],))
                res1 = c.fetchall()
                c.execute("SELECT REVIEW, RATING FROM REVIEW_RATING_DATA WHERE REVIEWEE_ID = ?",(i[0],))
                res2 = c.fetchall()
                if not res2:
                    for i in res1:
                        print(res1)
                else:
                    for i,j in zip(res1,res2):
                        print(res1,res2)
        else:
            # else, the function is called from the Youngster class.
            print("(ELDER ID, NAME, AGE, FUND, COMMENT, RATING)")
            for i in reviewees:
                c.execute("SELECT E_ID, E_NAME, E_AGE, E_FUND FROM ELDER_DATA WHERE E_ID = ?",(i[0],))
                res1 = c.fetchall()
                c.execute("SELECT REVIEW, RATING FROM REVIEW_RATING_DATA WHERE REVIEWEE_ID = ?",(i[0],))
                res2 = c.fetchall()
                if not res2:
                    for i in res1:
                        print(res1)
                else:
                    for i,j in zip(res1,res2):
                        print(res1,res2)
        

    def create_update_review(self, reviewer, reviewee, rating, comment):
        c.execute("SELECT * FROM REVIEW_RATING_DATA WHERE REVIEWER_ID=? AND REVIEWEE_ID=?",(reviewer,reviewee))
        res = c.fetchone()
        if res:
             # If a review exists already, update record.
            c.execute("UPDATE REVIEW_RATING_DATA SET REVIEW = ?, RATING = ? WHERE REVIEWER_ID = ? AND REVIEWEE_ID = ?",(comment,rating,reviewer,reviewee))
        else:
             # else, create a new record.
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
