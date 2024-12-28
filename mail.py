import smtplib
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


sender_email = ("Updatebotreport@gmail.com")
password = "pdsenbgulxyljurl"  # Sender's app password

receiver_mail = ("indstockmarketreview1@gmail.com")  ## You can change this as per your req.


## Send simple mail with sub and message
def mail_with_text(sub, message, is_html=False):
    # Create a MIME object
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_mail
    msg['Subject'] = sub
    
    # Attach the message body (HTML or plain text)
    if is_html:
        msg.attach(MIMEText(message, 'html'))
    else:
        msg.attach(MIMEText(message, 'plain'))
    
    # Send the email
    with smtplib.SMTP('smtp.gmail.com', 587) as server:  # Update with your SMTP server and port
        server.starttls()  # Enable TLS
        server.login(sender_email, password)  # Login to the server
        server.sendmail(sender_email, receiver_mail, msg.as_string())  # Send the email
    
    print("Email Sent Successfully")
    print(f"Mail triggered to {receiver_mail}")



def mail_with_attachment(subject , message, file_path ):
    
    # if bubject line and message and file path is fixed, we can remove parameter from the function and use these.
    subject = " "
    message = " "
        # Attach a file (Excel or CSV)
    file_path = "Orders.csv"  # Replace with your file path
    file_name = "Orders.csv"  # File name to appear in the email

    try:
        # Create the email
        email = MIMEMultipart()
        email['From'] = sender_email
        email['To'] = receiver_mail
        email['Subject'] = subject

        # Add the message body
        email.attach(MIMEText(message, 'plain'))

        # Attach the file
        file_name = file_path.split('/')[-1]  # Extract filename from the path
        with open(file_path, 'rb') as file:
            mime_base = MIMEBase('application', 'octet-stream')
            mime_base.set_payload(file.read())
        encoders.encode_base64(mime_base)
        mime_base.add_header(
            'Content-Disposition',
            f'attachment; filename={file_name}'
        )
        email.attach(mime_base)

        # Send the email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_mail, email.as_string())
        server.quit()

        print("Email Sent Successfully with Attachment!")
        print(f"Mail Triggered to {receiver_mail}")
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

# file_to_mail = "Tradebook.csv"
# mail_with_text("Subject to the Mail", "This is a sample test mail sent to check the function to check for friend without attachmant")
# send_email_with_attachment("Subject to the Mail", "This is a sample test mail sent to check the function to check for friend with attachmant",file_to_mail)

