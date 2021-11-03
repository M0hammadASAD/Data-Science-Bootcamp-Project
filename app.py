import mysql.connector as mysql
import pandas as pd
import time
from datetime import datetime
from PIL import Image
import json
import base64
from streamlit.state.session_state import SessionState
import yagmail
import re
from re import search
# import smtplib
import datetime
import uuid
import streamlit as st
import streamlit.components.v1 as components
from streamlit import caching

import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
from sqlalchemy import create_engine
from mysql.connector.constants import ClientFlag

import yaml
import mysql.connector as mysql
from mysql.connector.constants import ClientFlag
from sqlalchemy import create_engine

st.set_page_config(
    page_title="Data Science Bootcamp",
    page_icon=":smiley:",
    initial_sidebar_state="expanded",
)



with open('credintials.yml', 'r') as f:
    credintials = yaml.load(f, Loader=yaml.FullLoader)
    db_credintials = credintials['db']
    system_pass = credintials['system_pass']['admin']
    # email_sender = credintials['email_sender']

def get_database_connection():
    db = mysql.connect(host = db_credintials['host'],
                      user = db_credintials['user'],
                      passwd = db_credintials['passwd'],
                      database = db_credintials['database'],
                      auth_plugin= db_credintials['auth_plugin'])
    cursor = db.cursor()

    return cursor, db


cursor, db = get_database_connection()
# to be commented

cursor.execute('''CREATE TABLE users (track_id varchar(255),
                    full_name varchar(255),
                    age int,
                    phone varchar(255),
                    email varchar(255),
                    city varchar(255),
                    address varchar(255),
                    hours_per_week int,
                    cur_status varchar(255),
                    gpa float,
                    pwd varchar(255),
                    reg_date date,
                    gender varchar(255)''')

cursor.execute('''CREATE TABLE admin (username varchar(255),
                    password varchar(255)
                    ''')
un='Admin'
pw='1234'
query = f'''INSERT INTO admin (username,password)
                            VALUES ('{un}','{pw}')'''
cursor.execute(query)
db.commit()

# to be commented end




if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'login' not in st.session_state:
    st.session_state.login = False

mp = {
    0: "Tracking ID",
    1: "Full Name",
    2: "Age",
    3: "Phone",
    4: "E-mail",
    5: "City",
    6: "Address",
    7: "Hours Per Week",
    8: "Current Status",
    9: "GPA",
    10: "Password",
    11: "Application Date",
    12: "Gender"
}
def view(var):
    cursor.execute(
            f"select * from users")
    tables = cursor.fetchall()
    for i in tables:
        if i[8]==var:
            with st.expander(i[1]):
                j = 0
                while j < 12:
                    tmp = i[j]
                    tmp = str(tmp)
                    st.metric(label=mp[j], value=tmp)
                    j += 1

def pending():
    cursor.execute(
            f"select * from users")
    tables = cursor.fetchall()
    for i in tables:
        if i[8]=='In queue':
            with st.expander(i[1]):
                j = 0
                flag = False
                while j < 12:
                    tmp = i[j]
                    tmp = str(tmp)
                    if j == 8 and tmp == 'In queue':
                        flag = True
                    st.metric(label=mp[j], value=tmp)
                    j += 1
                if flag:
                    col = st.columns(6)
                    accept = col[4].button("Accept",key=i[0])
                    reject = col[5].button("Reject",key=i[0])
                    if accept:
                        st.balloons()
                        st.success('Accepted')
                        cursor.execute(f"Update users set cur_status='Accepted' where track_id='{i[0]}'")
                        db.commit()
                    if reject:
                        st.warning('Rejected')
                        cursor.execute(f"Update users set cur_status='Rejected' where track_id='{i[0]}'")
                        db.commit()
                    
    

def disp():
    selection = st.sidebar.selectbox('Select View Option:', [
        'View in range of some Date', 'View Pendings', 'View Accepted', 'View Rejected'])
    if selection == 'View in range of some Date':
        st.session_state.login = True
        col0 = st.columns(2)
        date1 = col0[0].date_input("Start Date:")
        date2 = col0[1].date_input("End Date:")
        cursor.execute(
            f"select * from users where reg_date between '{date1}' and '{date2}'")
        tables = cursor.fetchall()
        for i in tables:
            with st.expander(i[1]):
                j = 0
                flag = False
                while j < 12:
                    tmp = i[j]
                    tmp = str(tmp)
                    if j == 8 and tmp == 'In queue':
                        flag = True
                    st.metric(label=mp[j], value=tmp)
                    j += 1
                if flag:
                    col = st.columns(6)
                    accept = col[4].button("Accept",key=i[0])
                    reject = col[5].button("Reject",key=i[0])
                    if accept:
                        st.balloons()
                        st.success('Accepted')
                        cursor.execute(f"Update users set cur_status='Accepted' where track_id='{i[0]}'")
                        db.commit()
                    if reject:
                        st.warning('Rejected')
                        cursor.execute(f"Update users set cur_status='Rejected' where track_id='{i[0]}'")
                        db.commit()
    elif selection=='View Pendings':
        pending()
    elif selection=='View Accepted':
        view('Accepted')
    elif selection=='View Rejected':
        view('Rejected')



def login():
    username = st.sidebar.text_input('Username', key='user')
    password = st.sidebar.text_input('Password', type='password', key='pass')
    st.session_state.login = st.sidebar.checkbox('Sign In')
    if st.session_state.login:
        cursor.execute(
            f"select * from admin where username='Admin'")
        tables = cursor.fetchall()
        if username == tables[0][0] and password == tables[0][1]:
            st.session_state.login = True
            disp()
        else:
            st.sidebar.warning("Wrong Credintials")


def apply():
    track_id = uuid.uuid1()
    track_id = str(track_id)[:18]
    with st.form(key="apply_form"):
        full_name = st.text_input("Enter your Full Name : ", "Sherlock Holmes")
        pwd = st.text_input(
            "Enter a Password to See Your Application Status in future :", "SHERLOCKED", type='password', key='pas')
        age = st.number_input("Enter your age : ", 18)
        gender = st.radio("Select Gender: ", ['Male', 'Female', 'Other'])
        phone = st.text_input("Enter Phone No. : ", "+0145678945")
        email = st.text_input("Enter your E-mail : ", "info@shelock.me")
        city = st.selectbox('Select the city you live in : ', ['-------',
                                                               'Dhaka', 'Chattogram', 'Khulna', 'Rajshahi', 'Barisal', 'Rangpur'])
        address = st.text_area("Enter your Address : ",
                               " 221b Baker St, London NW1 6XE, United Kingdom")
        hours_per_week = st.slider(
            "How may hours you can work in a Week?", min_value=0, max_value=100)
        cur_status = "In queue"
        gpa = st.text_input("Enter your GPA :", "4.00")
        reg_date = datetime.date.today()
        if st.form_submit_button('Submit'):
            query = f'''INSERT INTO users (track_id,full_name,age,phone,email,city,address,hours_per_week,cur_status,gpa,pwd,reg_date,gender)
                            VALUES ('{track_id}','{full_name}','{age}','{phone}','{email}','{city}','{address}','{hours_per_week}','{cur_status}','{gpa}','{pwd}','{reg_date}','{gender}')'''
            cursor.execute(query)
            db.commit()
            st.success(
                f'Congratulation *{full_name}*! Your Application has been received.')
            st.code(track_id)
            st.warning("Please Store this code!!! To Check your application status please go to Track Status tab from Side Bar and Enter the Tracking ID and password which you have provided on the form and Hit enter.")


def check_stat():
    track_id = st.text_input('Enter Your Tracking ID :')
    pwd = st.text_input('Enter Your Password :')
    Submit = st.button(label='Check Status')
    if Submit:
        cursor.execute(
            f"select * from users where track_id='{track_id}' and pwd='{pwd}'")
        tables = cursor.fetchall()
        if len(tables) == 0:
            st.warning("Wrong Credintials. Try Again")
        else:
            if tables[0][8] == 'In queue':
                st.info(
                    f'Dear *{tables[0][1]}*,\n Your application is In Queue. Please Wait. We will get back to you soon.')
            elif tables[0][8] == 'Accepted':
                st.balloons()
                st.success(
                    f'Dear *{tables[0][1]}*,\n Congratulations!!!You are selected for the Data Science bootcamp.')
            else:
                st.warning(
                    f'Dear *{tables[0][1]}*, \nWe are sorry. You have been rejected. Better Luck next time.')


def main():
    st.header("Welcome to Data Science Bootcamp!!!")
    st.sidebar.subheader("Please Select One :")
    menu_choice = st.sidebar.selectbox(
        '', ['---------', 'Apply for a Slot', 'Admin Login', 'Track Status'])
    if menu_choice == "Admin Login":
        login()
    elif menu_choice == "Apply for a Slot":
        apply()
    elif menu_choice == 'Track Status':
        check_stat()

if __name__ == '__main__':
    main()
