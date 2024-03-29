import tkinter as tk
from tkinter import messagebox

from sqlalchemy import create_engine, null
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import *
from sqlalchemy.exc import *


from datetime import date, datetime, timedelta


from dbTable import *
# ------ Database Function ------ #
db_user = "root"
db_password = "YcyCl525JE#"
schema_name = "bt2102_as_1"

# Database Connection Initialization
engine = create_engine('mysql+mysqlconnector://{}:{}@localhost:3306/{}'.format(db_user, db_password, schema_name),
echo = True)
metadata = MetaData(engine)
DBSession = sessionmaker(bind = engine)
session = DBSession()
conn = engine.connect()


# ---------- UI ----------- #
win_w = 1000
win_h = 1000

# UI Initialization
root = tk.Tk()
root.title('ALS')
root.geometry("{}x{}".format(str(win_w), str(win_h)))
root.option_add("*font", "SF\ Pro 14")

# Frame Definition
Root_frame = tk.Frame(root, height = win_h, width = win_w)
Mem_frame = tk.Frame(root, height = win_h, width = win_w)
Book_frame = tk.Frame(root, height = win_h, width = win_w)
Loan_frame = tk.Frame(root, height = win_h, width = win_w)
Res_frame = tk.Frame(root, height = win_h, width = win_w)
Fine_frame = tk.Frame(root, height = win_h, width = win_w)
Rep_frame = tk.Frame(root, height = win_h, width = win_w)

# Frame Control Function
def change_frame(from_frame, to_frame):
    from_frame.pack_forget()
    to_frame.pack()

# Query Function
class QueryError(Exception):
    pass

def get_member(member_id):
    session_new = DBSession()
    member = session_new.query(LibMember).filter_by(memberid = member_id).one()
    session_new.close()
    return member

def get_book(acc_number):
    session_new = DBSession()
    book = session_new.query(LibBooks).filter_by(Accession_Number = acc_number).one()
    session_new.close()
    return book

def get_book_BR(acc_number):
    """
    get the book with the unique acc number from borrow_and_return_record.
    * Returns None if no valid LibBook is found.
    """
    session_new = DBSession()
    book = session_new.query(Borrow_And_Return_Record).filter_by(Accession_Number = acc_number).one()
    session_new.close()
    return book

def get_date_object(date_string):
    return datetime.strptime(date_string, '%d/%m/%Y')

def is_book_on_loan(acc_number):
    try:
        session_new = DBSession()
        br_record = session_new.query(Borrow_And_Return_Record).filter_by(Accession_Number = acc_number, Return_Date = None).one()
    except NoResultFound:
        session_new.close()
        return False
    else:
        session_new.close()
        return True


def get_reserve_record(member_id, acc_number):
    session_new = DBSession()
    reserve_record = session_new.query(Reserve_Record).filter_by(Accession_Number = acc_number, memberid = member_id).one()
    session_new.close()
    return reserve_record

def get_book_Reserve(acc_number):
    """
    get all the books with the unique acc number from reserve_record.
    * Returns None if no valid LibBook is found.
    """
    session_new = DBSession()
    book = session_new.query(Reserve_Record).filter_by(Accession_Number = acc_number).all()
    session_new.close()
    return book

def book_exist(acc_number):
    """
    check the book is in LibBook.
    * Returns False if no valid LibBook is found.
    """
    try:
        get_book(acc_number)
        return True
    except NoResultFound:
        return False

def member_exist(member_id):
    """
    check the member is in LibMember.
    * Returns False if no valid Member is found.
    """
    try:
        get_member(member_id)
        return True
    except NoResultFound:
        return False

def get_date_object(date_string):
    return datetime.strptime(date_string, '%d/%m/%Y')

def today_day():
    today = date.today()
    today = today.strftime('%d/%m/%Y')
    return today

def due_date():
    due_date = date.today() + timedelta(days = 14)
    due_date = due_date.strftime('%d/%m/%Y')
    return due_date

def get_due_date(acc_number, member_id):
    session_new = DBSession()
    br_record = session_new.query(Borrow_And_Return_Record).filter_by(Accession_Number = acc_number, memberid = member_id).one()
    session_new.close()
    return br_record.Due_Date.strftime('%d/%m/%Y')


def days_between(date1,date2):
    delta = date2 - date1
    return delta.days


def is_book_on_loan(acc_number):
    """
    check if a book is on loan.
    Returns True if is on loan. False if is not on loan.
    """
    session_new = DBSession()
    try:
        session_new.query(Borrow_And_Return_Record).filter_by(Accession_Number = acc_number, Return_Date = None).one()
    except NoResultFound:
        session_new.close()
        return False
    else:
        session_new.close()
        return True


def is_book_reserved(acc_number):
    """
    check if a book is reserved.
    Returns True if is reserved. False if is not reserved.
    """
    session_new = DBSession()
    try:
        session_new.query(Reserve_Record).filter_by(Accession_Number = acc_number).one()
    except NoResultFound:
        session_new.close()
        return False
    else:
        session_new.close()
        return True

def members_reserved(acc_number):
    """
    if book is reserved, find all the memberids that reserves the book
    """
    book_reserved = get_book_Reserve(acc_number)
    res = []
    for book in book_reserved:
        res += book_reserved.memberid
    return res

def is_quota_reached(id):
    """
    check if a member's quota is reached (2).
    Returns True if is reached. False if is not reached.
    """
    try:
        session_new = DBSession()
        session_new.query(LibMember).filter_by(memberid = id, current_books_borrowed = 2).one()
    except NoResultFound: #this member has 2 borrowed books, quota reached
        session_new.close()
        return False
    else:
        session_new.close()
        return True

def has_outstanding_fine(id):
    """
    check if a member has outstanding fine (!=0).
    Returns True if has outstanding fine. False if do not have outstanding fine.
    """
    try:
        session_new = DBSession()
        session_new.query(LibMember).filter_by(memberid = id, outstanding_fee = 0).one()
    except NoResultFound: #this member has outstanding fee of 0
        session_new.close()
        return True
    else:
        session_new.close()
        return False

def get_Authors(acc_number):
    """
    get all authors from Book_Author
    """
    res = ''
    books = session.query(Book_Author).filter_by(Accession_Number = acc_number).all()
    for book in books:
        res += book.Author + '\n'
    return res

def get_reserve_record(member_id, acc_number):
    session_new = DBSession()
    book = session_new.query(Reserve_Record).filter_by(Accession_Number = acc_number, memberid = member_id).one()
    session_new.close()
    return book

def insert_reserve_record(member_id, acc_number, res_date):
    res_table = Table('Reserve_Record', metadata, autoload = True)
    res_ins = res_table.insert()
    res_ins = res_ins.values(Accession_Number = acc_number, memberid = member_id, Reserve_Date = res_date)
    result = conn.execute(res_ins)
    print(result)

def update_member_reserved(member_id, reserved_number):
    session_new = DBSession()
    session_new.query(LibMember).filter_by(memberid = member_id).update({'current_books_reserved': reserved_number})
    session_new.commit()
    session_new.close()

def delete_reserve_record(member_id, acc_number):
    session_new = DBSession()
    session_new.query(Reserve_Record).filter_by(memberid = member_id, Accession_Number = acc_number).delete()
    session_new.commit()
    session_new.close()

def insert_LibBooks(acc_number, Title, ISBN, Publisher, Year):
    book_table = Table('LibBooks', metadata, autoload = True)
    book_ins = book_table.insert()
    book_ins = book_ins.values(Accession_Number = acc_number, Title = Title, ISBN = ISBN, Publisher = Publisher, Year = Year)
    conn.execute(book_ins)

def delete_LibBooks(acc_number):
    session_new = DBSession()
    session_new.query(LibBooks).filter_by(Accession_Number = acc_number).delete()
    session_new.commit()
    session_new.close()

def insert_Author(acc_number, AuthorList):
    for Author in AuthorList:
        author_table = Table('Book_Author', metadata, autoload = True)
        author_ins = author_table.insert()
        author_ins = author_ins.values(Accession_Number = acc_number, Author = Author)
        conn.execute(author_ins)

def delete_All_Authors(acc_number):
    session_new = DBSession()
    session_new.query(Book_Author).filter_by(Accession_Number = acc_number).delete()
    session_new.commit()
    session_new.close()

def insert_borrow_and_return_record(acc_number, member_id, borrow_date, due_date):
    br_table = Table('Borrow_And_Return_Record', metadata, autoload = True)
    br_ins = br_table.insert()
    br_ins = br_ins.values(Accession_Number = acc_number, memberid = member_id,
    Borrow_Date = get_date_object(borrow_date), Return_Date = None,
    Due_Date = get_date_object(due_date))
    conn.execute(br_ins)

def delete_borrow_and_return_record(acc_number, member_id):
    session_new = DBSession()
    session_new.query(Borrow_And_Return_Record).filter_by(memberid = member_id, Accession_Number = acc_number).delete()
    session_new.commit()
    session_new.close()

def get_borrowed_number(member_id):
    member = get_member(member_id)
    return member.current_books_borrowed



def update_member_borrowed(member_id, borrowed_number):
    session_new = DBSession()
    session_new.query(LibMember).filter_by(memberid = member_id).update({'current_books_borrowed': borrowed_number})
    session_new.commit()
    session_new.close()

def update_outstanding_fine(member_id, fine):
    session_new = DBSession()
    session_new.query(LibMember).filter_by(memberid = member_id).update({'outstanding_fee': fine})
    session_new.commit()
    session_new.close()

# Root frame object
top_text = tk.Label(Root_frame, text='ALS System', bg='cyan')
top_text.place(x = 250, y = 0, anchor = "nw")
Mem_button = tk.Button(Root_frame, text = "Memberships", width=20, fg = 'black', command = lambda: change_frame(Root_frame, Mem_frame))
Mem_button.place(x = 200, y = 50, anchor = "nw")
Book_button = tk.Button(Root_frame, text = "Books", width=20, fg = 'black', command = lambda: change_frame(Root_frame, Book_frame))
Book_button.place(x = 200, y = 100, anchor = "nw")
Loan_button = tk.Button(Root_frame, text = "Loans", width=20, fg = 'black', command = lambda: change_frame(Root_frame, Loan_frame))
Loan_button.place(x = 200, y = 150, anchor = "nw")
Res_button = tk.Button(Root_frame, text = "Reservations", width=20, fg = 'black', command = lambda: change_frame(Root_frame, Res_frame))
Res_button.place(x = 200, y = 200, anchor = "nw")
Fine_button = tk.Button(Root_frame, text = "Fines", width=20, fg = 'black', command = lambda: change_frame(Root_frame, Fine_frame))
Fine_button.place(x = 200, y = 250, anchor = "nw")
Rep_button = tk.Button(Root_frame, text = "Reports", width=20, fg = 'black', command = lambda: change_frame(Root_frame, Rep_frame))
Rep_button.place(x = 200, y = 300, anchor = "nw")

#Membership Frame
# Membership Frame Object
Mem_create_frame = tk.Frame(root, height = win_h, width = win_w)
Mem_delete_frame = tk.Frame(root, height = win_h, width = win_w)
Mem_update1_frame = tk.Frame(root, height = win_h, width = win_w)
Mem_update2_frame = tk.Frame(root, height = win_h, width = win_w)

# Membership menu labels and buttons
top_text = tk.Label(Mem_frame, text='Select One Of The Options Below', bg='cyan')
top_text.place(x = 150, y = 0, anchor = "nw")

Mem_create_label = tk.Label(Mem_frame, text = "Membership Creation", fg = 'black')
Mem_create_label.place(x = 50, y = 50, anchor = "nw")
Mem_create_button = tk.Button(Mem_frame, text = "Create A Member", fg = 'black', command = lambda: change_frame(Mem_frame, Mem_create_frame))
Mem_create_button.place(x = 300, y = 50, anchor = "nw")

Mem_delete_label = tk.Label(Mem_frame, text = "Membership Deletion", fg = 'black')
Mem_delete_label.place(x = 50, y = 100, anchor = "nw")
Mem_delete_button = tk.Button(Mem_frame, text = "Delete A Member", fg = 'black', command = lambda: change_frame(Mem_frame, Mem_delete_frame))
Mem_delete_button.place(x = 300, y = 100, anchor = "nw")

Mem_update_label = tk.Label(Mem_frame, text = "Membership Update", fg = 'black')
Mem_update_label.place(x = 50, y = 150, anchor = "nw")
Mem_update_button = tk.Button(Mem_frame, text = "Update A Member", fg = 'black', command = lambda: change_frame(Mem_frame, Mem_update1_frame))
Mem_update_button.place(x = 300, y = 150, anchor = "nw")

Back_button = tk.Button(Mem_frame, text = "Back To Main Menu", fg = 'black', command = lambda: change_frame(Mem_frame, Root_frame))
Back_button.place(x = 175, y = 200, anchor = "nw")


# Membership creation labels and buttons
def create_new_member():
    messagebox.showinfo(title='Success!', message='ALS Membership Created')

top_text = tk.Label(Mem_create_frame, text='To Create Member, Please Enter Requested Information Below:', bg='cyan')
top_text.place(x = 50, y = 0, anchor = "nw")

Mem_ID_label1 = tk.Label(Mem_create_frame, text='Membership ID', fg = 'black')
Mem_ID_label1.place(x = 50, y = 50, anchor = "nw")
Mem_ID_entry = tk.Entry(Mem_create_frame, fg = 'black', width = 60)
Mem_ID_entry.insert(0, "A unique alphanumeric id that distinguishes every member")
Mem_ID_entry.place(x = 300, y = 50, anchor = "nw")

Name_label = tk.Label(Mem_create_frame, text='Name', fg = 'black')
Name_label.place(x = 50, y = 100, anchor = "nw")
Name_entry = tk.Entry(Mem_create_frame, fg = 'black', width = 60)
Name_entry.insert(0, "Enter member's name")
Name_entry.place(x = 300, y = 100, anchor = "nw")

Faculty_label = tk.Label(Mem_create_frame, text='Faculty', fg = 'black')
Faculty_label.place(x = 50, y = 150, anchor = "nw")
Faculty_entry = tk.Entry(Mem_create_frame, fg = 'black', width = 60)
Faculty_entry.insert(0, "e.g., Computing, Engineering, Science, etc.")
Faculty_entry.place(x = 300, y = 150, anchor = "nw")

Phone_number_label = tk.Label(Mem_create_frame, text='Phone Number', fg = 'black')
Phone_number_label.place(x = 50, y = 200, anchor = "nw")
Phone_number_entry = tk.Entry(Mem_create_frame, fg = 'black', width = 60)
Phone_number_entry.insert(0, "e.g., 91234567, 81093487, 92054981, etc.")
Phone_number_entry.place(x = 300, y = 200, anchor = "nw")

Email_Address_label = tk.Label(Mem_create_frame, text='Email Address', fg = 'black')
Email_Address_label.place(x = 50, y = 250, anchor = "nw")
Email_Address_entry = tk.Entry(Mem_create_frame, fg = 'black', width = 60)
Email_Address_entry.insert(0, "e.g., ALSuser@als.edu")
Email_Address_entry.place(x = 300, y = 250, anchor = "nw")

Add_new_member_button = tk.Button(Mem_create_frame, text = "Create Member", fg = 'black', command = create_new_member)
Add_new_member_button.place(x = 50, y = 300, anchor = "nw")
Back_to_membership_menu_button_C = tk.Button(Mem_create_frame, text = "Back To Membership Menu", fg = 'black', command = lambda: change_frame(Mem_create_frame, Mem_frame))
Back_to_membership_menu_button_C.place(x = 700, y = 300, anchor = "nw")


# Membership deletion labels and buttons
def delete_mem():
    None

top_text = tk.Label(Mem_delete_frame, text='To Delete A Member, Please Membership ID Below', bg='cyan')
top_text.place(x = 50, y = 0, anchor = "nw")

ID_label = tk.Label(Mem_delete_frame, text='Membership ID')
ID_label.place(x = 50, y = 200, anchor = "nw")
ID_entry = tk.Entry(Mem_delete_frame, fg = 'black', width = 60)
ID_entry.insert(0, "A unique alphanumeric id that distinguishes every member")
ID_entry.place(x = 300, y = 200, anchor = "nw")


Mem_delete_button = tk.Button(Mem_delete_frame, text = "Delete Member", fg = 'black', command = delete_mem)
Mem_delete_button.place(x = 50, y = 300, anchor = "nw")
Back_to_mem_button = tk.Button(Mem_delete_frame, text = "Back To Membership Menu", fg = 'black', command = lambda: change_frame(Mem_delete_frame, Mem_frame))
Back_to_mem_button.place(x = 700, y = 300, anchor = "nw")


# Membership update menu labels and buttons
top_text = tk.Label(Mem_update1_frame, text='To Update A Member, Please Membership ID Below', bg='cyan')
top_text.place(x = 50, y = 0, anchor = "nw")

ID_label = tk.Label(Mem_update1_frame, text='Membership ID')
ID_label.place(x = 50, y = 200, anchor = "nw")
ID_entry = tk.Entry(Mem_update1_frame, fg = 'black', width = 60)
ID_entry.insert(0, "A unique alphanumeric id that distinguishes every member")
ID_entry.place(x = 300, y = 200, anchor = "nw")


Mem_update1_button = tk.Button(Mem_update1_frame, text = "Update Member", fg = 'black', command = lambda: change_frame(Mem_update1_frame, Mem_update2_frame))
Mem_update1_button.place(x = 50, y = 300, anchor = "nw")
Back_to_mem_button = tk.Button(Mem_update1_frame, text = "Back To Membership Menu", fg = 'black', command = lambda: change_frame(Mem_update1_frame, Mem_frame))
Back_to_mem_button.place(x = 700, y = 300, anchor = "nw")

# Membership update information labels and buttons
def update_mem():
    None

Mem_ID_label1 = tk.Label(Mem_update2_frame, text='Membership ID', fg = 'red')
Mem_ID_label1.place(x = 50, y = 50, anchor = "nw")
Mem_ID_entry = tk.Entry(Mem_update2_frame, fg = 'black', width = 60)
Mem_ID_entry.insert(0, "A unique alphanumeric id that distinguishes every member")
Mem_ID_entry.place(x = 300, y = 50, anchor = "nw")

Name_label = tk.Label(Mem_update2_frame, text='Name', fg = 'black')
Name_label.place(x = 50, y = 100, anchor = "nw")
Name_entry = tk.Entry(Mem_update2_frame, fg = 'black', width = 60)
Name_entry.insert(0, "Update name")
Name_entry.place(x = 300, y = 100, anchor = "nw")

Faculty_label = tk.Label(Mem_update2_frame, text='Faculty', fg = 'black')
Faculty_label.place(x = 50, y = 150, anchor = "nw")
Faculty_entry = tk.Entry(Mem_update2_frame, fg = 'black', width = 60)
Faculty_entry.insert(0, "Update faculty")
Faculty_entry.place(x = 300, y = 150, anchor = "nw")

Phone_number_label = tk.Label(Mem_update2_frame, text='Phone Number', fg = 'black')
Phone_number_label.place(x = 50, y = 200, anchor = "nw")
Phone_number_entry = tk.Entry(Mem_update2_frame, fg = 'black', width = 60)
Phone_number_entry.insert(0, "Update phone number")
Phone_number_entry.place(x = 300, y = 200, anchor = "nw")

Email_Address_label = tk.Label(Mem_update2_frame, text='Email Address', fg = 'black')
Email_Address_label.place(x = 50, y = 250, anchor = "nw")
Email_Address_entry = tk.Entry(Mem_update2_frame, fg = 'black', width = 60)
Email_Address_entry.insert(0, "Update Email")
Email_Address_entry.place(x = 300, y = 250, anchor = "nw")

Mem_update2_button = tk.Button(Mem_update2_frame, text = "Update Member", fg = 'black', command = lambda: change_frame(Mem_update2_frame, update_mem))
Mem_update2_button.place(x = 50, y = 300, anchor = "nw")
Back_to_mem_button = tk.Button(Mem_update2_frame, text = "Back To Previous Membership Menu", fg = 'black', command = lambda: change_frame(Mem_update2_frame, Mem_update1_frame))
Back_to_mem_button.place(x = 700, y = 300, anchor = "nw")


#Renzhou starts

#Book Frame
#Book frame object

Acq_frame = tk.Frame(root, height = win_h, width = win_w)
Withd_frame = tk.Frame(root, height = win_h, width = win_w)

top_text = tk.Label(Book_frame, text='Select One Of The Options Below', bg='cyan')
top_text.place(x = 150, y = 0, anchor = "nw")

Acq_label = tk.Label(Book_frame, text = "Book Acquisition", fg = 'black')
Acq_label.place(x = 50, y = 50, anchor = "nw")
Acq_button = tk.Button(Book_frame, text = "Acquire A Book", fg = 'black', command = lambda: change_frame(Book_frame, Acq_frame))
Acq_button.place(x = 300, y = 50, anchor = "nw")

Withd_label = tk.Label(Book_frame, text = "Book Withdrawal", fg = 'black')
Withd_label.place(x = 50, y = 100, anchor = "nw")
Withd_button = tk.Button(Book_frame, text = "Withdraw A Book", fg = 'black', command = lambda: change_frame(Book_frame, Withd_frame))
Withd_button.place(x = 300, y = 100, anchor = "nw")

Back_button = tk.Button(Book_frame, text = "Back To Main Menu", fg = 'black', command = lambda: change_frame(Book_frame, Root_frame))
Back_button.place(x = 175, y = 150, anchor = "nw")


#Book Acquisition object

top_text_book_acquisition  = tk.Label(Acq_frame, text='For New Book Acquisition, Please Enter Information Below', bg='cyan')
top_text_book_acquisition .place(x = 50, y = 0, anchor = "nw")

Acc_number_label_book_acquisition = tk.Label(Acq_frame, text='Accession Number', fg = 'black')
Acc_number_label_book_acquisition.place(x = 50, y = 50, anchor = "nw")
Acc_number_entry_book_acquisition = tk.Entry(Acq_frame, fg = 'black', width = 60)
# Acc_number_entry_book_acquisition.insert(0, "Used to identify an instance of book")
Acc_number_entry_book_acquisition.place(x = 300, y = 50, anchor = "nw")


Title_label_book_acquisition = tk.Label(Acq_frame, text='Title', fg = 'black')
Title_label_book_acquisition.place(x = 50, y = 100, anchor = "nw")
Title_entry_book_acquisition = tk.Entry(Acq_frame, fg = 'black', width = 60)
# Title_entry_book_acquisition.insert(0, "Title of the book")
Title_entry_book_acquisition.place(x = 300, y = 100, anchor = "nw")

Author_label_book_acquisition = tk.Label(Acq_frame, text='Author', fg = 'black')
Author_label_book_acquisition.place(x = 50, y = 150, anchor = "nw")
Author_entry_book_acquisition = tk.Entry(Acq_frame, fg = 'black', width = 60)
# Author_entry_book_acquisition.insert(0, "Author of the book")
Author_entry_book_acquisition.place(x = 300, y = 150, anchor = "nw")

ISBN_label_book_acquisition = tk.Label(Acq_frame, text='ISBN', fg = 'black')
ISBN_label_book_acquisition.place(x = 50, y = 200, anchor = "nw")
ISBN_entry_book_acquisition = tk.Entry(Acq_frame, fg = 'black', width = 60)
# ISBN_entry_book_acquisition.insert(0, "ISBN of the book")
ISBN_entry_book_acquisition.place(x = 300, y = 200, anchor = "nw")

Publisher_label_book_acquisition = tk.Label(Acq_frame, text='Publisher', fg = 'black')
Publisher_label_book_acquisition.place(x = 50, y = 250, anchor = "nw")
Publisher_entry_book_acquisition = tk.Entry(Acq_frame, fg = 'black', width = 60)
# Publisher_entry_book_acquisition.insert(0, "Publisher of the book")
Publisher_entry_book_acquisition.place(x = 300, y = 250, anchor = "nw")

Year_label_book_acquisition = tk.Label(Acq_frame, text='Year', fg = 'black')
Year_label_book_acquisition.place(x = 50, y = 300, anchor = "nw")
Year_entry_book_acquisition = tk.Entry(Acq_frame, fg = 'black', width = 60)
# Year_entry_book_acquisition.insert(0, "Year of publishing of the book")
Year_entry_book_acquisition.place(x = 300, y = 300, anchor = "nw")

def add_new_book():
    acc_number = Acc_number_entry_book_acquisition.get()
    Title = Title_entry_book_acquisition.get()
    Author = Author_entry_book_acquisition.get()
    Authorlist = Author.split(',')
    ISBN = ISBN_entry_book_acquisition.get()
    Publisher = Publisher_entry_book_acquisition.get()
    Year = Year_entry_book_acquisition.get()

    if book_exist(acc_number) or Title == "" or Author == "" or ISBN == "" or Publisher == "" or Year == "":
        messagebox.showinfo(title='Error!', message='Book Already Added; Duplicate, Missing or Incomplete fields')
    else:
        insert_LibBooks(acc_number, Title, ISBN, Publisher, Year)
        insert_Author(acc_number, Authorlist)
        messagebox.showinfo(title='Success!', message='New Book Added In Library!') # insert book inside LibBooks

Add_new_book_button_book_acquisition = tk.Button(Acq_frame, text = "Add New Book", fg = 'black', command = add_new_book)
Add_new_book_button_book_acquisition.place(x = 50, y = 350, anchor = "nw")


Back_to_book_button_book_acquisition = tk.Button(Acq_frame, text = "Back To Book", fg = 'black', command = lambda: change_frame(Acq_frame, Book_frame))
Back_to_book_button_book_acquisition.place(x = 700, y = 350, anchor = "nw")


#Book Withdrawal object
def withdraw_book():
    acc_number = Acc_number_entry_book_withdrawal.get()
    if not book_exist(acc_number):
            messagebox.showinfo(title='Error!', message='Book Does Not Exist.')
    else:
        book_LibBook = get_book(acc_number)
        res = messagebox.askyesno('prompt', 'Please Confirm The Details Are Correct' + '\n'
            + 'Assession Number:  ' + acc_number  + '\n Title:  ' + book_LibBook.Title 
            + '\n Authors:  ' + get_Authors(acc_number) 
            + '\n ISBN:  ' + book_LibBook.ISBN 
            + '\n Publisher:  ' + book_LibBook.Publisher
            + '\n Year:  ' + str(book_LibBook.Year))
        if res:
            withdraw_book_on_loan_or_reserved(acc_number)
        else:
            pass


def withdraw_book_on_loan_or_reserved(acc_number):
    if is_book_reserved(acc_number):
        messagebox.showinfo(title='Error!', message='Book Is Currently Reserved.')
    elif is_book_on_loan(acc_number):
        messagebox.showinfo(title='Error!', message='Book Is Currently On Loan.')
    else:
        delete_All_Authors(acc_number)
        delete_LibBooks(acc_number)
        messagebox.showinfo(title='Success!', message='Book Is Successfully Withdrawn.')

top_text_book_withdrawal = tk.Label(Withd_frame, text='To Remove Outdated Books From System, Please Enter Information Below', bg='cyan')
top_text_book_withdrawal.place(x = 50, y = 0, anchor = "nw")

Acc_number_label_book_withdrawal = tk.Label(Withd_frame, text='Accession Number')
Acc_number_label_book_withdrawal.place(x = 50, y = 200, anchor = "nw")
Acc_number_entry_book_withdrawal = tk.Entry(Withd_frame, fg = 'black', width = 60)
# Acc_number_entry_book_withdrawal.insert(0, "Used to identify an instance of book")
Acc_number_entry_book_withdrawal.place(x = 300, y = 200, anchor = "nw")

Withdraw_book_button_book_withdrawal = tk.Button(Withd_frame, text = "Withdraw Book", fg = 'black', command = withdraw_book)
Withdraw_book_button_book_withdrawal.place(x = 50, y = 350, anchor = "nw")
Back_to_book_button_book_withdrawal = tk.Button(Withd_frame, text = "Back To Book", fg = 'black', command = lambda: change_frame(Withd_frame, Book_frame))
Back_to_book_button_book_withdrawal.place(x = 700, y = 350, anchor = "nw")

#Loan Frame
#Loan frame object
Borrow_frame = tk.Frame(root, height = win_h, width = win_w)
Return_frame = tk.Frame(root, height = win_h, width = win_w)

top_text = tk.Label(Loan_frame, text='Select One Of The Options Below', bg='cyan')
top_text.place(x = 150, y = 0, anchor = "nw")

Borrow_label = tk.Label(Loan_frame, text = "Book Borrow", fg = 'black')
Borrow_label.place(x = 50, y = 50, anchor = "nw")
Borrow_button = tk.Button(Loan_frame, text = "Borrow A Book", fg = 'black', command = lambda: change_frame(Loan_frame, Borrow_frame))
Borrow_button.place(x = 300, y = 50, anchor = "nw")

Return_label = tk.Label(Loan_frame, text = "Book Return", fg = 'black')
Return_label.place(x = 50, y = 100, anchor = "nw")
Return_button = tk.Button(Loan_frame, text = "Return A Book", fg = 'black', command = lambda: change_frame(Loan_frame, Return_frame))
Return_button.place(x = 300, y = 100, anchor = "nw")

Back_button = tk.Button(Loan_frame, text = "Back To Main Menu", fg = 'black', command = lambda: change_frame(Loan_frame, Root_frame))
Back_button.place(x = 175, y = 150, anchor = "nw")


#Borrow object
top_text_book_borrow = tk.Label(Borrow_frame, text='To Borrow A Book , Please Enter Information Below', bg='cyan')
top_text_book_borrow.place(x = 50, y = 0, anchor = "nw")

Acc_number_label_book_borrow = tk.Label(Borrow_frame, text='Accession Number')
Acc_number_label_book_borrow.place(x = 50, y = 100, anchor = "nw")
Acc_number_entry_book_borrow = tk.Entry(Borrow_frame, fg = 'black', width = 60)
# Acc_number_entry_book_borrow.insert(0, "Used to identify an instance of book")
Acc_number_entry_book_borrow.place(x = 300, y = 100, anchor = "nw")

ID_label_book_borrow = tk.Label(Borrow_frame, text='Membership ID')
ID_label_book_borrow.place(x = 50, y = 200, anchor = "nw")
ID_entry_book_borrow= tk.Entry(Borrow_frame, fg = 'black', width = 60)
# ID_entry_book_borrow.insert(0, "A unique alphanumeric id that distinguishes every member")
ID_entry_book_borrow.place(x = 300, y = 200, anchor = "nw")

def borrow_book():
    acc_number = Acc_number_entry_book_borrow.get()
    member_id = ID_entry_book_borrow.get()
    borrow_date = today_day()
    if not book_exist(acc_number):
            messagebox.showinfo(title='Error!', message='Book Does Not Exist.')
    elif not member_exist(member_id):
            messagebox.showinfo(title='Error!', message='Member Does Not Exist.')
    else:
        book_LibBooks = get_book(acc_number)
        member_LibMember = get_member(member_id)
        res = messagebox.askyesno('prompt', 'Please Confirm The Details Are Correct' + '\n'
            + 'Assession Number:  ' + acc_number  
            + '\n Book Title:  ' + book_LibBooks.Title 
            + '\n Borrow Date:  ' + borrow_date
            + '\n Membership ID:  ' + member_id 
            + '\n Member Name:  ' + member_LibMember.name
            + '\n Due Date:  ' + due_date())

        if res:
            borrow_book_on_loan_quota_fine(acc_number, member_id)
        else:
            pass

def borrow_book_on_loan_quota_fine(acc_number, member_id):
    borrow_date = today_day()
    new_borrowed_number = get_borrowed_number(member_id) + 1
    if is_quota_reached(member_id):
        messagebox.showinfo(title='Error!', message='Member Loan Quota Exceeded.')
    elif is_book_on_loan(acc_number):
        book_due_date = get_due_date(acc_number, member_id)
        messagebox.showinfo(title='Error!', message='Book Is Currently On Loan Until ' + book_due_date)
    elif has_outstanding_fine(member_id):
        messagebox.showinfo(title='Error!', message='Member Has Outstanding Fines.')
    elif is_book_reserved(acc_number) and member_id not in members_reserved(acc_number):
        messagebox.showinfo(title='Error!', message='Book Is Already Reserved.')
    else:
        insert_borrow_and_return_record(acc_number, member_id, borrow_date, due_date())
        update_member_borrowed(member_id, new_borrowed_number)
        messagebox.showinfo(title='Success!', message='You Have Borrowed This Book.') 
        # add 1 to books_borrowed and update borrow_and_return_record

Borrow_book_button_book_borrow = tk.Button(Borrow_frame, text = "Borrow Book", fg = 'black', command = borrow_book)
Borrow_book_button_book_borrow.place(x = 50, y = 300, anchor = "nw")
Back_to_loan_button_book_borrow = tk.Button(Borrow_frame, text = "Back To Loan", fg = 'black', command = lambda: change_frame(Borrow_frame, Loan_frame))
Back_to_loan_button_book_borrow.place(x = 700, y = 300, anchor = "nw")

#Return object

top_text_book_return = tk.Label(Return_frame, text='To Return A Book , Please Enter Information Below', bg='cyan')
top_text_book_return.place(x = 50, y = 0, anchor = "nw")

Acc_number_label_book_return = tk.Label(Return_frame, text='Accession Number')
Acc_number_label_book_return.place(x = 50, y = 100, anchor = "nw")
Acc_number_entry_book_return = tk.Entry(Return_frame, fg = 'black', width = 60)
# Acc_number_entry_book_return.insert(0, "Used to identify an instance of book")
Acc_number_entry_book_return.place(x = 300, y = 100, anchor = "nw")

ID_label_book_return = tk.Label(Return_frame, text='Membership ID')
ID_label_book_return.place(x = 50, y = 200, anchor = "nw")
ID_entry_book_return = tk.Entry(Return_frame, fg = 'black', width = 60)
# ID_entry_book_return.insert(0, "A unique alphanumeric id that distinguishes every member")
ID_entry_book_return.place(x = 300, y = 200, anchor = "nw")

def return_book():
    acc_number = Acc_number_entry_book_return.get()
    member_id = ID_entry_book_return.get()
    if not book_exist(acc_number):
            messagebox.showinfo(title='Error!', message='Book Does Not Exist.')
    elif not member_exist(member_id):
            messagebox.showinfo(title='Error!', message='Member Does Not Exist.')
    elif not is_book_on_loan(acc_number):
            messagebox.showinfo(title='Error!', message='Book Is Not On Loan.')
    else:
        book_LibBooks = get_book(acc_number)
        book_BR = get_book_BR(acc_number)
        member_LibMember = get_member(member_id)
        Borrow_date = book_BR.Borrow_Date.strftime('%d/%m/%Y')
        Fine = max(days_between(book_BR.Due_Date, date.today()),0)

        res = messagebox.askyesno('prompt', 'Please Confirm The Details Are Correct' + '\n'
            + 'Assession Number:  ' + acc_number  
            + '\n Book Title:  ' + book_LibBooks.Title 
            + '\n Borrow Date:  ' + Borrow_date
            + '\n Membership ID:  ' + member_id 
            + '\n Member Name:  ' + member_LibMember.name
            + '\n Return Date:  ' + today_day()
            + '\n Fine:  ' + str(Fine))
            # 
        if res:
            return_book_fine(member_id, acc_number, Fine)
        else:
            pass

def return_book_fine(member_id, acc_number, Fine):
    new_borrowed_number = get_borrowed_number(member_id) - 1
    if Fine != 0:
        update_outstanding_fine(member_id, Fine)
        update_member_borrowed(member_id, new_borrowed_number)
        delete_borrow_and_return_record(acc_number, member_id)
        messagebox.showinfo(title='Error!', message='Book Returned Successfully But Member Has Fines.')
    else:
        update_member_borrowed(member_id, new_borrowed_number)
        delete_borrow_and_return_record(acc_number, member_id)
        messagebox.showinfo(title='Success!', message='You Have Returned This Book.') 
        # minus 1 to books_borrowed and update borrow_and_return_record


Return_book_button = tk.Button(Return_frame, text = "Return Book", fg = 'black', command = return_book)
Return_book_button.place(x = 50, y = 300, anchor = "nw")
Back_to_loan_button = tk.Button(Return_frame, text = "Back To Loan", fg = 'black', command = lambda: change_frame(Return_frame, Loan_frame))
Back_to_loan_button.place(x = 700, y = 300, anchor = "nw")

#Renzhou ends




# Reservation frame object
#Qingyang Code
Res_book_frame = tk.Frame(root, height = win_h, width = win_w)
Res_cancel_frame = tk.Frame(root, height = win_h, width = win_w)

Res_book_label = tk.Label(Res_frame, text = "Book Reservation", fg = 'black')
Res_book_label.place(x = 50, y = 50, anchor = "nw")
Res_book_button = tk.Button(Res_frame, text = "Reserve a Book", fg = 'black', command = lambda: change_frame(Res_frame, Res_book_frame))
Res_book_button.place(x = 300, y = 50, anchor = "nw")
Res_cancel_label = tk.Label(Res_frame, text = "Reservation Cancellation", fg = 'black')
Res_cancel_label.place(x = 50, y = 100, anchor = "nw")
Res_cancel_button = tk.Button(Res_frame, text = "Cancel Reservation", fg = 'black', command = lambda: change_frame(Res_frame, Res_cancel_frame))
Res_cancel_button.place(x = 300, y = 100, anchor = "nw")
Res_back_button = tk.Button(Res_frame, text = "Back to Main Menu", fg = 'black', command = lambda: change_frame(Res_frame, Root_frame))
Res_back_button.place(x = 300, y = 150, anchor = "nw")

Res_book_title_label = tk.Label(Res_book_frame, text = "To reserve a book, please enter information below:", fg = 'black')
Res_book_title_label.place(x = 50, y = 0, anchor = "nw")
Res_book_Acc_number_label = tk.Label(Res_book_frame, text = "Accession Number", fg = 'black')
Res_book_Acc_number_label.place(x = 50, y = 50, anchor = "nw")

Res_book_Acc_number_entry = tk.Entry(Res_book_frame, fg = 'black', bg = 'white', width = 60)
# Res_book_Acc_number_entry.insert(0, "Used to identify an instance of book")
Res_book_Acc_number_entry.place(x = 300, y = 50, anchor = "nw")
Res_book_Mem_ID_label = tk.Label(Res_book_frame, text = "Membership ID", fg = 'black')
Res_book_Mem_ID_label.place(x = 50, y = 100, anchor = "nw")
Res_book_Mem_ID_entry = tk.Entry(Res_book_frame, fg = 'black', bg = 'white', width = 60)
# Res_book_Mem_ID_entry.insert(0, "A unique alphanumeric id that distinguishes every member")
Res_book_Mem_ID_entry.place(x = 300, y = 100, anchor = "nw")
Res_book_Res_date_label = tk.Label(Res_book_frame, text = "Reserve date (DD/MM/YYYY)", fg = 'black')
Res_book_Res_date_label.place(x = 50, y = 150, anchor = "nw")
Res_book_Res_date_entry = tk.Entry(Res_book_frame, fg = 'black', bg = 'white', width = 60)
# Res_book_Res_date_entry.insert(0, "02/02/2022")
Res_book_Res_date_entry.place(x = 300, y = 150, anchor = "nw")

def commit_book_reservation(mem, book, date, toplevel):
    toplevel.destroy()
    mem_id = mem.memberid
    acc_number = book.Accession_Number
    # Check if the book is on loan
    if (is_book_on_loan(acc_number)):
        # Check if the member has already reserved the book
        try:
            get_reserve_record(mem_id, acc_number)
        except NoResultFound:
            pass
        else:
            messagebox.showerror(title = "Error", message = "\"{}\" has already reserved the book \"{}\".".format(mem.name, book.Title))
            return

        # Check if the member has outstanding fine
        if (mem.outstanding_fee == 0):
            # Check if no more than 2 books are reserved
            if (mem.current_books_reserved < 2):
                insert_reserve_record(mem_id, acc_number, date)
                update_member_reserved(mem_id, mem.current_books_reserved + 1)
            else:
                messagebox.showerror(title = "Error", message = "\"{}\" has already reserved 2 books. No more reservation is allowed.".format(mem.name))
                return
        else:
            messagebox.showerror(title = "Error", message = "\"{}\" has unpaid outstanding fine of {}. Please pay before any reservation.".format(mem.name, mem.outstanding_fee))
            return
    else:
        messagebox.showerror(title = "Error", message = "\"{}\" is available. You may go ahead and borrow it now.".format(book.Title))
        return  
      
    messagebox.showinfo(title = "Success", message = "\"{}\" have successfully reserved the book \"{}\".".format(mem.name, book.Title))  

def confirm_book_reservation():
    mem_id = Res_book_Mem_ID_entry.get()
    acc_number = Res_book_Acc_number_entry.get()
    date_string = Res_book_Res_date_entry.get()

    # Check if the input date format is wrong
    try:
        res_date = get_date_object(date_string)
    except ValueError:
        messagebox.showerror(title = "Error", message = "\"{}\" is not a valid date or a valid date format.".format(date_string))
        return

    # Check if member exists
    try:
        mem = get_member(mem_id)
    except NoResultFound:
        messagebox.showerror(title = "Error", message = "\"{}\" is not a valid member id.".format(mem_id))
        return 

    # Check if book exists
    try:
        book = get_book(acc_number)
    except NoResultFound:
        messagebox.showerror(title = "Error", message = "\"{}\" is not a valid accession number.".format(acc_number))
        return 

    Res_book_confirm_top = tk.Toplevel(height = 500, width = 500)
    Res_book_confirm_top.geometry("{}x{}".format(500, 500))
    Res_book_confirm_top.title("Confirm Reservation")
    Res_book_confirm_label = tk.Label(Res_book_confirm_top, text = "Confirm Reservation Details To Be Correct", fg = 'black')
    Res_book_confirm_label.place(x = 50, y = 0, anchor = "nw")
    Res_book_confirm_acc_label = tk.Label(Res_book_confirm_top, text = "Accession Number: {}".format(acc_number), fg = 'black')
    Res_book_confirm_acc_label.place(x = 50, y = 50, anchor = "nw")
    Res_book_confirm_title_label = tk.Label(Res_book_confirm_top, text = "Book Title: {}".format(book.Title), fg = 'black')
    Res_book_confirm_title_label.place(x = 50, y = 100, anchor = "nw")
    Res_book_confirm_memid_label = tk.Label(Res_book_confirm_top, text = "Membership ID: {}".format(mem_id), fg = 'black')
    Res_book_confirm_memid_label.place(x = 50, y = 150, anchor = "nw")
    Res_book_confirm_name_label = tk.Label(Res_book_confirm_top, text = "Member Name: {}".format(mem.name), fg = 'black')
    Res_book_confirm_name_label.place(x = 50, y = 200, anchor = "nw")
    Res_book_confirm_date_label = tk.Label(Res_book_confirm_top, text = "Reserve Date (DD/MM/YYYY): {}".format(date_string), fg = 'black')
    Res_book_confirm_date_label.place(x = 50, y = 250, anchor = "nw")
    Res_book_confirm_button = tk.Button(Res_book_confirm_top, text = "Confirm Reservation", fg = 'black', command = lambda: commit_book_reservation(mem, book, res_date, Res_book_confirm_top))
    Res_book_confirm_button.place(x = 50, y = 300, anchor = "nw")

    Res_book_confirm_top.loop()

Res_book_Res_button = tk.Button(Res_book_frame, text = "Reserve Book", fg = 'black', command = confirm_book_reservation)
Res_book_Res_button.place(x = 50, y = 200, anchor = "nw")
Res_book_Back_button = tk.Button(Res_book_frame, text = "Back to Reservation Menu", fg = 'black', command = lambda: change_frame(Res_book_frame, Res_frame))
Res_book_Back_button.place(x = 700, y = 200, anchor = "nw")

Res_cancel_title_label = tk.Label(Res_cancel_frame, text = "To cancel a reservation, please enter information below:", fg = 'black')
Res_cancel_title_label.place(x = 50, y = 0, anchor = "nw")
Res_cancel_Acc_number_label = tk.Label(Res_cancel_frame, text = "Accession Number", fg = 'black')
Res_cancel_Acc_number_label.place(x = 50, y = 50, anchor = "nw")
Res_cancel_Acc_number_entry = tk.Entry(Res_cancel_frame, fg = 'black', bg = 'white', width = 60)
# Res_cancel_Acc_number_entry.insert(0, "Used to identify an instance of book")
Res_cancel_Acc_number_entry.place(x = 300, y = 50, anchor = "nw")
Res_cancel_Mem_ID_label = tk.Label(Res_cancel_frame, text = "Membership ID", fg = 'black')
Res_cancel_Mem_ID_label.place(x = 50, y = 100, anchor = "nw")
Res_cancel_Mem_ID_entry = tk.Entry(Res_cancel_frame, fg = 'black', bg = 'white', width = 60)
# Res_cancel_Mem_ID_entry.insert(0, "A unique alphanumeric id that distinguishes every member")
Res_cancel_Mem_ID_entry.place(x = 300, y = 100, anchor = "nw")
# Res_cancel_Cancel_date_label = tk.Label(Res_cancel_frame, text = "Cancel date (DD/MM/YYYY)", fg = 'black')
# Res_cancel_Cancel_date_label.place(x = 50, y = 150, anchor = "nw")
# Res_cancel_Cancel_date_entry = tk.Entry(Res_cancel_frame, fg = 'black', bg = 'white', width = 60)
# Res_cancel_Cancel_date_entry.insert(0, "Date of reservation cancellation")
# Res_cancel_Cancel_date_entry.place(x = 300, y = 150, anchor = "nw")

def commit_cancel_reservation(mem, book, toplevel):
    toplevel.destroy()
    mem_id = mem.memberid
    acc_number = book.Accession_Number
    # Check if the member has already reserved the book
    try:
        get_reserve_record(mem_id, acc_number)
    except NoResultFound:
        messagebox.showerror(title = "Error", message = "\"{}\" hasn't reserved the book \"{}\" yet.".format(mem.name, book.Title))
        return
    else:
        delete_reserve_record(mem_id, acc_number)
        update_member_reserved(mem_id, mem.current_books_reserved - 1)

    messagebox.showinfo(title = "Success", message = "\"{}\" have successfully cancelled the reservation for the book \"{}\".".format(mem.name, book.Title))  

def confirm_cancel_reservation():
    mem_id = Res_cancel_Mem_ID_entry.get()
    acc_number = Res_cancel_Acc_number_entry.get()
    
    # Check if member exists
    try:
        mem = get_member(mem_id)
    except NoResultFound:
        messagebox.showerror(title = "Error", message = "\"{}\" is not a valid member id.".format(mem_id))
        return 

    # Check if book exists
    try:
        book = get_book(acc_number)
    except NoResultFound:
        messagebox.showerror(title = "Error", message = "\"{}\" is not a valid accession number.".format(acc_number))
        return 

    Res_cancel_confirm_top = tk.Toplevel(height = 500, width = 500)
    Res_cancel_confirm_top.geometry("{}x{}".format(500, 500))
    Res_cancel_confirm_top.title("Confirm Cancellation")
    Res_cancel_confirm_label = tk.Label(Res_cancel_confirm_top, text = "Confirm Cancellation Details To Be Correct", fg = 'black')
    Res_cancel_confirm_label.place(x = 50, y = 0, anchor = "nw")
    Res_cancel_confirm_acc_label = tk.Label(Res_cancel_confirm_top, text = "Accession Number: {}".format(acc_number), fg = 'black')
    Res_cancel_confirm_acc_label.place(x = 50, y = 50, anchor = "nw")
    Res_cancel_confirm_title_label = tk.Label(Res_cancel_confirm_top, text = "Book Title: {}".format(book.Title), fg = 'black')
    Res_cancel_confirm_title_label.place(x = 50, y = 100, anchor = "nw")
    Res_cancel_confirm_memid_label = tk.Label(Res_cancel_confirm_top, text = "Membership ID: {}".format(mem_id), fg = 'black')
    Res_cancel_confirm_memid_label.place(x = 50, y = 150, anchor = "nw")
    Res_cancel_confirm_name_label = tk.Label(Res_cancel_confirm_top, text = "Member Name: {}".format(mem.name), fg = 'black')
    Res_cancel_confirm_name_label.place(x = 50, y = 200, anchor = "nw")
    Res_cancel_confirm_button = tk.Button(Res_cancel_confirm_top, text = "Confirm Cancellation", fg = 'black', command = lambda: commit_cancel_reservation(mem, book, Res_cancel_confirm_top))
    Res_cancel_confirm_button.place(x = 50, y = 300, anchor = "nw")

    Res_cancel_confirm_top.loop()

Res_cancel_Res_button = tk.Button(Res_cancel_frame, text = "Cancel Reservation", fg = 'black', command = confirm_cancel_reservation)
Res_cancel_Res_button.place(x = 50, y = 200, anchor = "nw")
Res_cancel_Back_button = tk.Button(Res_cancel_frame, text = "Back to Reservation Menu", fg = 'black', command = lambda: change_frame(Res_cancel_frame, Res_frame))
Res_cancel_Back_button.place(x = 700, y = 200, anchor = "nw")
# Qingyang ends

#Fine frame
# Fine menu labels and buttons
Fine_payment_frame = tk.Frame(root, height = win_h, width = win_w)

top_text = tk.Label(Fine_frame, text='Select The Option Below', bg='cyan')
top_text.place(x = 150, y = 0, anchor = "nw")

Fine_payment_label = tk.Label(Fine_frame, text = "Payment", fg = 'black')
Fine_payment_label.place(x = 50, y = 50, anchor = "nw")
Fine_payment_button = tk.Button(Fine_frame, text = "Fine Payment", fg = 'black', command = lambda: change_frame(Fine_frame, Fine_payment_frame))
Fine_payment_button.place(x = 150, y = 47, anchor = "nw")

Back_to_mem_button = tk.Button(Fine_frame, text = "Back To Main Menu", fg = 'black', command = lambda: change_frame(Fine_frame, Root_frame))
Back_to_mem_button.place(x = 300, y = 100, anchor = "nw")


# Fine payment labels and buttons
def pay_fine():
    None
top_text = tk.Label(Fine_payment_frame, text='To Pay a Fine, Please Enter Information Below:', bg='cyan')
top_text.place(x = 50, y = 0, anchor = "nw")

ID_label = tk.Label(Fine_payment_frame, text='Membership ID')
ID_label.place(x = 50, y = 50, anchor = "nw")
ID_entry = tk.Entry(Fine_payment_frame, fg = 'black', width = 60)
ID_entry.insert(0, "A unique alphanumeric id that distinguishes every member")
ID_entry.place(x = 300, y = 50, anchor = "nw")

Payment_date_label = tk.Label(Fine_payment_frame, text='Payment Date')
Payment_date_label.place(x = 50, y = 100, anchor = "nw")
Payment_date_entry = tk.Entry(Fine_payment_frame, fg = 'black', width = 60)
Payment_date_entry.insert(0, "Date Payment Received")
Payment_date_entry.place(x = 300, y = 100, anchor = "nw")

Payment_amount_label = tk.Label(Fine_payment_frame, text='Payment Amount')
Payment_amount_label.place(x = 50, y = 150, anchor = "nw")
Payment_amount_entry = tk.Entry(Fine_payment_frame, fg = 'black', width = 60)
Payment_amount_entry.insert(0, "Total fine amount")
Payment_amount_entry.place(x = 300, y = 150, anchor = "nw")

Pay_fine_button = tk.Button(Fine_payment_frame, text = "Pay Fine", fg = 'black', command = pay_fine)
Pay_fine_button.place(x = 50, y = 200, anchor = "nw")
Back_to_fine_menu_button = tk.Button(Fine_payment_frame, text = "Back To Fines Menu", fg = 'black', command = lambda: change_frame(Fine_payment_frame, Fine_frame))
Back_to_fine_menu_button.place(x = 700, y = 200, anchor = "nw")

#Report frame
#other frames in the report frame
Book_search_frame = tk.Frame(root, height = win_h, width = win_w)
Book_search_results_frame = tk.Frame(root, height = win_h, width = win_w)
Book_on_Loan_frame = tk.Frame(root, height = win_h, width = win_w)
Book_on_reservation_frame = tk.Frame(root, height = win_h, width = win_w)
Outstanding_Fines__frame = tk.Frame(root, height = win_h, width = win_w)
Books_on_Loan_to_Member__frame = tk.Frame(root, height = win_h, width = win_w)
Books_on_Loan_to_Member__results_frame = tk.Frame(root, height = win_h, width = win_w)

# report frame Main menu
top_text = tk.Label(Rep_frame, text='Select One Of The Options Below', bg='cyan')
top_text.place(x = 50, y = 0, anchor = "nw")

Book_Search_label = tk.Label(Rep_frame, text = "A member can perform a search \n on the collection of books.", fg = 'black')
Book_Search_label.place(x = 400, y = 50, anchor = "nw")
Book_Search_button = tk.Button(Rep_frame, text = "Book Search", width=25, fg = 'black', command = lambda: change_frame(Rep_frame, Book_search_frame))
Book_Search_button.place(x = 50, y = 50, anchor = "nw")

Book_on_Loan_label = tk.Label(Rep_frame, text = "This function displays all the books \n currently on loan to members.", fg = 'black')
Book_on_Loan_label.place(x = 400, y = 120, anchor = "nw")
Book_on_Loan_button = tk.Button(Rep_frame, text = "Books on Loan", width=25, fg = 'black', command = lambda: change_frame(Rep_frame, Book_on_Loan_frame))
Book_on_Loan_button.place(x = 50, y = 120, anchor = "nw")

Book_on_reservation_label = tk.Label(Rep_frame, text = "This function displays all the books \n that members have reserved.", fg = 'black')
Book_on_reservation_label.place(x = 400, y = 190, anchor = "nw")
Book_on_reservation_button = tk.Button(Rep_frame, text = "Books on Reservation", width=25, fg = 'black', command = lambda: change_frame(Rep_frame, Book_on_reservation_frame))
Book_on_reservation_button.place(x = 50, y = 190, anchor = "nw")

Outstanding_Fines__label = tk.Label(Rep_frame, text = "This function displays the \n outstanding fines for members.", fg = 'black')
Outstanding_Fines__label.place(x = 400, y = 260, anchor = "nw")
Outstanding_Fines__button = tk.Button(Rep_frame, text = "Outstanding Fines", width=25, fg = 'black', command = lambda: change_frame(Rep_frame, Outstanding_Fines__frame))
Outstanding_Fines__button.place(x = 50, y = 260, anchor = "nw")

Books_on_Loan_to_Member__label = tk.Label(Rep_frame, text = "This function displays all the books a member \n identified by the membership ID has borrowed.", fg = 'black')
Books_on_Loan_to_Member__label.place(x = 400, y = 330, anchor = "nw")
Books_on_Loan_to_Member__button = tk.Button(Rep_frame, text = "Books on Loan to Member", width=25, fg = 'black', command = lambda: change_frame(Rep_frame, Books_on_Loan_to_Member__frame))
Books_on_Loan_to_Member__button.place(x = 50, y = 330, anchor = "nw")

Back_button = tk.Button(Rep_frame, text = "Back To Main Menu", fg = 'black', command = lambda: change_frame(Rep_frame, Root_frame))
Back_button.place(x = 300, y = 400, anchor = "nw")

# Book search frame
top_text = tk.Label(Book_search_frame, text='Select based on one of the categories below:', bg='cyan')
top_text.place(x = 50, y = 0, anchor = "nw")

Title_label = tk.Label(Book_search_frame, text='Title', fg = 'black')
Title_label.place(x = 50, y = 50, anchor = "nw")
Title_entry = tk.Entry(Book_search_frame, fg = 'black', width = 60)
Title_entry.insert(0, "Book Name")
Title_entry.place(x = 300, y = 50, anchor = "nw")

Author_label = tk.Label(Book_search_frame, text='Authors', fg = 'black')
Author_label.place(x = 50, y = 100, anchor = "nw")
Author_entry = tk.Entry(Book_search_frame, fg = 'black', width = 60)
Author_entry.insert(0, "There can be multiple authors for a book")
Author_entry.place(x = 300, y = 100, anchor = "nw")

ISBN_label = tk.Label(Book_search_frame, text='ISBN', fg = 'black')
ISBN_label.place(x = 50, y = 150, anchor = "nw")
ISBN_entry = tk.Entry(Book_search_frame, fg = 'black', width = 60)
ISBN_entry.insert(0, "ISBN Number")
ISBN_entry.place(x = 300, y = 150, anchor = "nw")

Publisher_label = tk.Label(Book_search_frame, text='Publisher', fg = 'black')
Publisher_label.place(x = 50, y = 200, anchor = "nw")
Publisher_entry = tk.Entry(Book_search_frame, fg = 'black', width = 60)
Publisher_entry.insert(0, "PRandom House, Penguin, Cengage, Springer, etc.")
Publisher_entry.place(x = 300, y = 200, anchor = "nw")

Year_label = tk.Label(Book_search_frame, text='Publication Year', fg = 'black')
Year_label.place(x = 50, y = 250, anchor = "nw")
Year_entry = tk.Entry(Book_search_frame, fg = 'black', width = 60)
Year_entry.insert(0, "Edition year")
Year_entry.place(x = 300, y = 250, anchor = "nw")

Search_book_buttom = tk.Button(Book_search_frame, text = "Search Book", width=20, height=1, command = lambda: change_frame(Book_search_frame, Book_search_results_frame))
Search_book_buttom.place(x = 50, y = 300, anchor = "nw")

Back_to_Report_Main = tk.Button(Book_search_frame, text = "Back to Reports Menu", width=20, height=1, command = lambda: change_frame(Book_search_frame, Rep_frame))
Back_to_Report_Main.place(x = 700, y = 300, anchor = "nw")

#Book Search Results frame
# top word
top_text = tk.Label(Book_search_results_frame, text='Book Search Results', bg='cyan')
top_text.place(x = 50, y = 0, anchor = "nw")

Back_to_Search_Function = tk.Button(Book_search_results_frame, text = "Back To Search Function", width=20, height=1, command = lambda: change_frame(Book_search_results_frame, Book_search_frame))
Back_to_Search_Function.place(x = 50, y = 100, anchor = "nw")

# Book on loan frame
top_text = tk.Label(Book_on_Loan_frame, text='Books on Loan Report', bg='cyan')
top_text.place(x = 50, y = 0, anchor = "nw")

Back_to_Report_Main = tk.Button(Book_on_Loan_frame, text = "Back to Reports Menu", width=20, height=1, command = lambda: change_frame(Book_on_Loan_frame, Rep_frame))
Back_to_Report_Main.place(x = 50, y = 100, anchor = "nw")

# Book on reservation frame
top_text = tk.Label(Book_on_reservation_frame, text='Books on Reservation Report', bg='cyan')
top_text.place(x = 50, y = 0, anchor = "nw")

Back_to_Report_Main = tk.Button(Book_on_reservation_frame, text = "Back to Reports Menu", width=20, height=1, command = lambda: change_frame(Book_on_reservation_frame, Rep_frame))
Back_to_Report_Main.place(x = 50, y = 100, anchor = "nw")


# Outstanding Fines frame
top_text = tk.Label(Outstanding_Fines__frame, text='Members With Outstanding Fines', bg='cyan')
top_text.place(x = 50, y = 0, anchor = "nw")

Back_to_Report_Main = tk.Button(Outstanding_Fines__frame, text = "Back to Reports Menu", width=20, height=1, command = lambda: change_frame(Outstanding_Fines__frame, Rep_frame))
Back_to_Report_Main.place(x = 50, y = 100, anchor = "nw")


# Books on Loan to Member search frame
top_text = tk.Label(Books_on_Loan_to_Member__frame, text='Books on Loan to Member', bg='cyan')
top_text.place(x = 50, y = 0, anchor = "nw")

MemID_text = tk.Label(Books_on_Loan_to_Member__frame, text='Membership ID')
MemID_text.place(x = 50, y = 200, anchor = "nw")
MemID_entry = tk.Entry(Books_on_Loan_to_Member__frame, fg = 'black', width = 60)
MemID_entry.insert(0, "A unique alphanumeric id that distinguishes every member")
MemID_entry.place(x = 300, y = 200, anchor = "nw")

Search_mem = tk.Button(Books_on_Loan_to_Member__frame, text = "Search Member", fg = 'black', command = lambda: change_frame(Books_on_Loan_to_Member__frame, Books_on_Loan_to_Member__results_frame))
Search_mem.place(x = 50, y = 350, anchor = "nw")
Back_to_Report_Main = tk.Button(Books_on_Loan_to_Member__frame, text = "Back to Reports Menu", fg = 'black', command = lambda: change_frame(Books_on_Loan_to_Member__frame, Rep_frame))
Back_to_Report_Main.place(x = 700, y = 350, anchor = "nw")

# Books on Loan to Member results frame
top_text = tk.Label(Books_on_Loan_to_Member__results_frame, text='Books on Loan to Member', bg='cyan')
top_text.place(x = 50, y = 0, anchor = "nw")

Back_to_Report_Main = tk.Button(Books_on_Loan_to_Member__results_frame, text = "Back to Reports Menu", width=20, height=1, command = lambda: change_frame(Books_on_Loan_to_Member__results_frame, Rep_frame))
Back_to_Report_Main.place(x = 50, y = 100, anchor = "nw")

# Root Frame Application
Root_frame.pack()
if __name__ == "__main__":
    root.mainloop()

session.close()
conn.close()
