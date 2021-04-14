import email, smtplib, ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime


now = datetime.now()

current_time = now.strftime("%B %d, %H:%M")



def sendEmail(filenames, scrappedID,newAds,compared_count,ScrappedURl ):

	subject = now.strftime("%B %d Kijiji Scrap")
	body = ("Hi NAME, \n\nScrapped completed :"+
		" {}\n\nTotal Scrapped: {}\nTotal Compared : {}\nTotal NewAds: {} \n\n Main Page URL :{} \n\n Sincerely Solomon".format(current_time, scrappedID,newAds,compared_count,ScrappedURl))
	sender_email = "my@gmail.com"
	receiver_email = "sender@gmail.com"
	password = "*******"
	BBC = "secondemail@gmail.com"


	message = MIMEMultipart()
	message["From"] = sender_email
	message["To"] = receiver_email
	message["Subject"] = subject
	message["Bcc"] = BBC  # Recommended for mass emails

	# Add body to email
	message.attach(MIMEText(body, "plain"))


	for filename in filenames:
		with open(filename, "rb") as attachment:
		    # Add file as application/octet-stream
		    # Email client can usually download this automatically as attachment
		    part = MIMEBase("application", "octet-stream")
		    part.set_payload(attachment.read())

		# Encode file in ASCII characters to send by email    
		encoders.encode_base64(part)

		# Add header as key/value pair to attachment part
		part.add_header(
		    "Content-Disposition",
		    f"attachment; filename= {filename}",
		)

		# Add attachment to message and convert message to string
		message.attach(part)
		text = message.as_string()


		# Log in to server using secure context and send email
		context = ssl.create_default_context()
		print ("THIS PART IS DONE")
	with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
	    server.login(sender_email, password)
	    server.sendmail(sender_email, receiver_email, text)
