import sys
import sqlite3

conn = sqlite3.connect("CareAllDB.db")
c = conn.cursor()


c.execute("""CREATE TABLE IF NOT EXISTS ELDER_DATA(E_ID INT PRIMARY KEY, E_NAME TEXT,
            E_AGE INT, E_FUND REAL, E_RATING INT, E_REVIEW TEXT, E_STATUS TEXT)""")

c.execute("""CREATE TABLE IF NOT EXISTS YOUNG_DATA(Y_ID INT PRIMARY KEY, Y_NAME TEXT,
            Y_AGE INT, Y_SALARY REAL, Y_RATING INT, Y_REVIEW TEXT, Y_ELDER_ASSIGNED INT)""")

c.execute("""CREATE TABLE IF NOT EXISTS REQUEST_DATA(ELDER_ID INT, YOUNG_ID INT)""")

c.execute("""CREATE TABLE IF NOT EXISTS ASSIGNED_DATA(ELDER_ID INT PRIMARY KEY, YOUNG_ID INT)""")



class Elder:
    def registration(self):
        
        eid = int(input("\nEnter interger ID: "))
        while True:
            c.execute("SELECT 1 FROM ELDER_DATA WHERE E_ID=?",(eid,))
            res = c.fetchone()
            if res:
                eid = int(input("ID already exists, choose another: "))
            else:
                break
        name = input("Enter your name: ")
        age = int(input("Enter age: "))
        fund = int(input("Enter fund to allocate: "))
        rating = 0
        review = 'None'
        status = 'Not Taken'
        record=(eid,name,age,fund,rating,review,status)
        c.execute("""INSERT INTO ELDER_DATA(E_ID,E_NAME,E_AGE,E_FUND,E_RATING,E_REVIEW,E_STATUS)
                  VALUES(?,?,?,?,?,?,?)""",record)
        conn.execute("COMMIT")

    def login(self):
        eid = int(input("Enter ID: "))
        c.execute("SELECT 1 FROM ELDER_DATA WHERE E_ID=?",(eid,))
        res = c.fetchone()
        if not res:
            print("ID does not exist")
            return
        c.execute("""SELECT * FROM ELDER_DATA WHERE E_ID = ?""",(eid,))
        print("(ID, NAME, AGE, FUND, RATING, REVIEW, STATUS)")
        print(next(c))
        while True:
            print("\n1.Display Requests")
            print("2.Rate and Review")
            print("3.Update Info")
            print("4.Exit")
            x = int(input("Enter your choice: "))
            if x==1:
                e.display_requests(eid)
            elif x==2:
                e.rate_and_review(eid)
            elif x==3:
                e.update_info(eid)
            elif x==4:
                break
            else:
                print("Invalid option")

    def display_requests(self,eid):
        c.execute("SELECT 1 FROM REQUEST_DATA WHERE ELDER_ID=?",(eid,))
        res = c.fetchone()
        if not res:
            print("No pending requests")
            return
        c.execute("""SELECT * FROM YOUNG_DATA INNER JOIN REQUEST_DATA ON REQUEST_DATA.ELDER_ID=?
                    WHERE YOUNG_DATA.Y_ID=REQUEST_DATA.YOUNG_ID""",(eid,))
        for row in c:
            print(row)
        aid = int(input("Enter ID to approve: "))
        c.execute("INSERT INTO ASSIGNED_DATA(ELDER_ID,YOUNG_ID) VALUES(?,?)",(eid,aid))
        c.execute("UPDATE ELDER_DATA SET E_STATUS = 'Taken' WHERE E_ID=?",(eid,))
        c.execute("SELECT COUNT(ELDER_ID) FROM ASSIGNED_DATA WHERE YOUNG_ID=?",(aid,))
        q = c.fetchone()
        if q == (4,):
            c.execute("DELETE FROM REQUEST_DATA WHERE YOUNG_ID=?",(aid,))
        c.execute("DELETE FROM REQUEST_DATA WHERE ELDER_ID=?",(eid,))
        conn.execute("COMMIT")
        
    def rate_and_review(self,eid):
        c.execute("SELECT 1 FROM ASSIGNED_DATA WHERE ELDER_ID=?",(eid,))
        res = c.fetchone()
        if not res:
            print("No one to rate and review.")
            return
        rate = int(input("Enter rating out of 5: "))
        review = str(input("Enter your review: "))
        c.execute("""SELECT YOUNG_ID FROM ASSIGNED_DATA WHERE ASSIGNED_DATA.ELDER_ID=?""",(eid,))
        yid = c
        c.execute("UPDATE YOUNG_DATA SET Y_RATING=?, Y_REVIEW=? WHERE Y_ID=?",(rate,review,yid,))
        conn.execute("COMMIT")
        
    def update_info(self,eid):
        age = int(input("Enter age: "))
        fund = int(input("Enter fund: "))
        c.execute("UPDATE ELDER_DATA SET E_AGE=?, E_FUND=? WHERE E_ID=?",(age,fund,eid,))
        conn.execute("COMMIT")

        


class Youngster:
    def registration(self):

        yid = int(input("\nEnter integer ID: "))
        while True:
            c.execute("SELECT 1 FROM YOUNG_DATA WHERE Y_ID=?",(yid,))
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
        record = (yid,name,age,salary,rating,review)
        c.execute("""INSERT INTO YOUNG_DATA(Y_ID,Y_NAME,Y_AGE,Y_SALARY,Y_RATING,Y_REVIEW)
                  VALUES(?,?,?,?,?,?)""",record)
        conn.execute("COMMIT")

    def login(self):
        yid = int(input("Enter ID: "))
        c.execute("SELECT 1 FROM YOUNG_DATA WHERE Y_ID=?",(yid,))
        res = c.fetchone()
        if not res:
            print("ID does not exist")
            return
        c.execute("""SELECT * FROM YOUNG_DATA WHERE Y_ID = ? """,(yid,))
        print("(ID, NAME, AGE, SALARY, RATING, REVIEW)")
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
                y.make_request(yid)
            elif x==2:
                y.rate_and_review(yid)
            elif x==3:
                y.update_info(yid)
            elif x==4:
                y.assigned_elders(yid)
            elif x==5:
                y.salary(yid)
            elif x==6:
                break
            else:
                print("Invalid option")

    def make_request(self,yid):
        c.execute("SELECT 1 FROM ELDER_DATA WHERE E_STATUS='Not Taken")
        res = c.fetchone()
        if not res:
            print("No elder to take care of.")
            return
        c.execute("SELECT COUNT(ELDER_ID) FROM ASSIGNED_DATA WHERE YOUNG_ID=?",(yid,))
        q = c.fetchone()
        if q == (4,):
            print("Maximum limit reached")
        else:
            
            c.execute("""SELECT * FROM ELDER_DATA WHERE E_STATUS = 'Not Taken' """)
            for row in c:
                print(row)
            rid = int(input("Enter Id to make request: "))
            c.execute("INSERT INTO REQUEST_DATA(ELDER_ID,YOUNG_ID) VALUES(?,?)",(rid,yid))
            conn.execute("COMMIT")
        
    def rate_and_review(self,yid):
        c.execute("SELECT 1 FROM ASSIGNED_DATA WHERE YOUNG_ID=?",(yid,))
        res = c.fetchone()
        if not res:
            print("No one to rate and review.")
            return
        c.execute("""SELECT ELDER_DATA.E_ID, ELDER_DATA.E_NAME, ELDER_DATA.E_AGE FROM ELDER_DATA
                    INNER JOIN ASSIGNED_DATA ON ASSIGNED_DATA.ELDER_ID=ELDER_DATA.E_ID
                    WHERE ASSIGNED_DATA.YOUNG_ID=?""",(yid,))
        eid = int(input("Enter Id to rate and review: "))
        rate = int(input("Enter rating out of 5: "))
        review = input("Enter review: ")
        c.execute("UPDATE ELDER_DATA SET E_RATING=?, E_REVIEW=? WHERE E_ID=?",(rate,review,eid,))
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
        user_class = int(input("\nEnter your choice: "))
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

