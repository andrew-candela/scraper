import boto3
email=boto3.client('ses')

class Email():
	def __init__(self):
		self.mailer=boto3.client('ses')

	def send_message(self,from_address,recipients,subject,message):
		dest={'ToAddresses':recipients}
		source=from_address
		mes={
			'Subject':{
				"Data":subject
			},
			'Body':{
				'Text':{
				"Data":message
				}
			}
		}
		resp=self.mailer.send_email(Source=source,Destination=dest,Message=mes)
		return resp

	def verify_address(self,address):
		resp = self.mailer.verify_email_identity(EmailAddress=address)
		return resp

	def check_verification(self,address):
		"""check one email address at a time to see if it has been verified"""
		resp = self.mailer.get_identity_verification_attributes(Identities = [address])
		return resp 

