from bs4 import BeautifulSoup
import requests
import os
import csv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

FROM_EMAIL = os.environ.get('FROM_EMAIL')
TO_EMAIL = os.environ.get('TO_EMAIL')
PASSWORD = os.environ.get('PASSWORD')
HEADER = ['TITLE', 'AUTHOR', 'AMAZON LINK']


response = requests.get(url="https://theplanets.org/100-best-science-fiction-books/")
webpage_data = response.text

soup = BeautifulSoup(webpage_data, "html.parser")
books = [book.text.split(' by ') for book in soup.select('.entry-content h3 a')]
amazon_links = [link.get('href') for link in soup.select('.entry-content h4 a')]

with open("scifi_books.csv", mode="w") as file:
    writer = csv.writer(file)
    writer.writerow(HEADER)

for index, link in enumerate(amazon_links):
    books[index].append(link)

# append data to csv file
with open("scifi_books.csv", mode="a") as file:
    for book in books:
        writer = csv.writer(file)
        writer.writerow(book)

# send mail
msg = MIMEMultipart()
msg['From'] = FROM_EMAIL
msg['To'] = TO_EMAIL
msg['Subject'] = "Top 100 Science Fiction Stories of all time"
body = "This file has the top 100 sci-fi stories of all time"
msg.attach(MIMEText(body, 'plain'))

filename = "scifi_books.csv"
attachment = open(filename, "rb")
payload = MIMEBase('application', 'octet-stream')
payload.set_payload(attachment.read())
encoders.encode_base64(payload)
payload.add_header('Content-Disposition', "attachment; filename= %s" % filename)
msg.attach(payload)
text = msg.as_string()

with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
    connection.starttls()
    connection.login(user=FROM_EMAIL, password=PASSWORD)
    connection.sendmail(
        from_addr=FROM_EMAIL,
        to_addrs=TO_EMAIL,
        msg=text
    )
