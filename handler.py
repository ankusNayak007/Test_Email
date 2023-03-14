import json
import boto3
import urllib
import os
import sys
from botocore.exceptions import ClientError
from datetime import datetime


class Tools:
    
    @staticmethod
    def debugging(*msg):
        try:
            if msg:
                for m in msg:
                    print(m)
            else:
                print("Empty Message")
            # input()
            
        except Exception as e:
            print("Error:: %s"%str(e))
            sys.exit()
        
    @staticmethod
    def get_datetime():
        
        # return a current datetime string 
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    

class EmailOperation:
    
    def __init__(self,template_key_name):
        self.ses_client = self.sesClientObject()
        self.template_key_name = template_key_name
        
        
    def sesClientObject(self):
        try:
            return boto3.client('ses')
            
        except ClientError as e:
            print("Error: while create boto3 sns client \n %s"%str(e))
            
        
    # def createAndUpdateTemplate(self):
        
    #     # self.ses_client.delete_template(
    #     #     TemplateName = self.template_name
    #     # )
        
    #     try:
            
    #         response=self.ses_client.get_template(TemplateName=self.template_name)
    #         if response['Template'] and response['ResponseMetadata']['HTTPStatusCode'] == 200:
    #             self.ses_client.update_template(
    #                     Template={
    #                         "TemplateName": self.template_name,
    #                         "SubjectPart": "{{status}} : 'File Name': {{file_name}} || Date: {{date}}",
    #                         # "SubjectPart": "Subject",
    #                         "HtmlPart": "Hello Ankus HTML",
    #                         "TextPart": "Hello Ankus Text"
    #                     }
    #                 )
                
    #     except ClientError as e:
            
    #         self.ses_client.create_template(
    #                 Template =  {
    #                     "TemplateName": self.template_name,
    #                     "SubjectPart": "{{status}} : 'File Name': {{file_name}} || Date: {{date}}",
    #                     # "SubjectPart": "Subject",
    #                     "HtmlPart": "Hello Ankus HTML",
    #                     "TextPart": "Hello Ankus Text"
    #                 }
    #             )
    #     else:
    #         return True
    
    def sampleTemplate(self):
        
        template_dict ={
            "success-success" : 
            {
                
                "TemplateName": self.template_key_name,
                "SubjectPart": "{{subject_line_of_the_email}}",
                "HtmlPart": """
                        <html>
                            <head></head>
                            <body>
                                <p>Email File Name: {{email_file_name}}</p>
                                <p>time_stamp_of_data_ingestion: {{time_stamp_of_data_ingestion}}</p>
                                <p>sender_email_id: {{sender_email_id}}</p>
                            </body>
                        
                        </html>
                """,
                "TextPart": "Hello Ankus Text"
            },
            
            "errors-wrong_data-invalid-data" :{
                "TemplateName": self.template_key_name,
                "SubjectPart": "{{subject_line_of_the_email}}",
                "HtmlPart": """
                    <html>
                        <head></head>
                        <body>
                            <p>Email File Name: {{email_file_name}}</p>
                            <p>time_stamp_of_data_ingestion: {{time_stamp_of_data_ingestion}}</p>
                            <p>sender_email_id: {{sender_email_id}}</p>
                            <p>data_error: {{data_error}}</p>
                            <p>wrong_data: {{wrong_data}}</p>
                        </body>
                    </html>
                """,
                "TextPart": "Hello Ankus Text"
            }
        }
        
        return template_dict
    
    def createTemplate(self,template):
        
        try:
            response=self.ses_client.get_template(TemplateName=self.template_key_name)
            if response['Template'] and response['ResponseMetadata']['HTTPStatusCode'] == 200:
                self.ses_client.update_template(
                        Template=template
                    )
                
        except ClientError as e:
            
            self.ses_client.create_template(
                    Template = template
                )
        else:
            return True
        
        
    
    def createAndUpdateTemplate(self):
        
        
        template_dict = self.sampleTemplate()
        template= {}
        
        
        if self.template_key_name in template_dict:
            template = template_dict[self.template_key_name]
            print(template)
            
            if self.createTemplate(template):
                return True
            else:
                return False
        else:
            sys.exit("Error: New unknown Template Occur . Need to add that in Template Dict")
            
            

    def mailStatus(self,mail_response):

        if mail_response:
            if mail_response['ResponseMetadata']['HTTPStatusCode'] == 200:
                print('email sent successfully..')
                # return True
            else:
                print('email sending failed..')
                # return False
        else:
            print('email response is empty...')
            # return False
        
    def sendEmail(self,source_email,dest_email,mail_data):
        
        response = None
        
        try:
            response = self.ses_client.send_templated_email(
                    Source = source_email,
                    Destination={
                        'ToAddresses': [
                            dest_email
                        ],
                        # 'CcAddresses': ['iamankus7@gmail.com']
                    },
                    Template=self.template_key_name,
                    # TemplateData = mail_data
                    TemplateData = mail_data
                )
                
            return response
        except Exception as e:
            print("Error: %s"%str(e))
        

class S3Operation:
    
    def __init__(self):
        
        self.s3_client = self.s3ClientObject()
        
        
    def s3ClientObject(self):
        
        try:
            session = boto3.Session()
            s3_client = session.client('s3')
            return s3_client
        except ClientError as e:
            print("Error: %s"%str(e))
            sys.exit()
            
                    
    def contentType(self, bucket_name:str, key:str):
        
        try:
            response = self.s3_client.get_object(Bucket=bucket_name, Key=key)
            print("Content Type: ",response['ContentType'])
            return response['ContentType']
        except Exception as e:
            print("Error: %s" %str(e))
            # raise e
            
    def contentData(self, bucket_name:str, key:str):
        
        try:
            response = self.s3_client.get_object(Bucket=bucket_name, Key=key)
            contents = response['Body'].read().decode('utf-8')
            return contents
        
        except Exception as e:
            print("Error: %s" %str(e))
        
    
    

class JsonOperation:
    
    @staticmethod
    def jsonToDict(json_data:str):
        
        try:
            data = {}
            if json_data:
                data = json.loads(json_data)
                
            return data
        except Exception as e:
            sys.exit("Error: %s" %str(e))
                
    
    

def handler(event, context):
    
    if event:
        
        file_obj = event['Records'][0]
        bucket_name = file_obj['s3']['bucket']['name']
        # key = urllib.parse.unquote_plus(file_obj['s3']['object']['key'], encoding='utf-8')
        key = file_obj['s3']['object']['key']
        key = urllib.parse.unquote_plus(key,encoding='utf-8')
        
        
        # - Need to find better approach for assign...
        file_name,file_prefix,file_type = None, None, None
        
        if os.path.dirname(key):
            file_name = key.split('/')[-1]
            file_prefix = key.split(file_name)[0]
            file_type = file_name.split('.')[-1]
        else:
            file_name = key
            file_type = key.split('.')[-1]
        
        # Tools.debugging(key,file_prefix)
        
        
        template_key_name = None
        
        try:
            if file_prefix:
                
                decider_folder = file_prefix.split('/')[0]
                # print(file_prefix.split('/')[1])
                
                if decider_folder.lower() == "success":
                    # Need to find better approach for split this path
                    # template_key_name=os.path.join(str(file_prefix.split('/')[0]),os.path.splitext(file_name)[0])
                    template_key_name = "-".join((str(file_prefix.split('/')[0]),os.path.splitext(file_name)[0]))
                
                elif decider_folder.lower() in ["error","errors"]:
                    # template_key_name=os.path.join(file_prefix.split('/')[0],file_prefix.split('/')[1],os.path.splitext(file_name)[0])
                    template_key_name = "-".join((str(file_prefix.split('/')[0]),str(file_prefix.split('/')[1]),os.path.splitext(file_name)[0]))
                    
                else:
                    print("Undetected Folder")
                    error_reason = "Undetected Folder"
                    sys.exit(error_reason)
                    
            else:
                status = "error"
                error_reason = "No File Prefix || So Unable to determine the status."
                sys.exit("No File Prefix || So Unable to determine the status.")
                
        except Exception as e:
            sys.exit("Error: %s"%str(e))
            
            
        
        
        s3Obj = S3Operation()
        # print(s3Obj.contentData(bucket_name,key))
        # print(type(s3Obj.contentData(bucket_name,key)))
        
        json_data = s3Obj.contentData(bucket_name,key)
        data = JsonOperation.jsonToDict(json_data)
        
        
        
        # test_data = {
        #         'status': status,
        #         'file_name': file_name,
        #         'date': Tools.get_datetime()
        #     }
            
        # if error_reason:
        #     test_data['error_reason'] = error_reason
        
        
        
        
        emailObj = EmailOperation(template_key_name)
                
        # Tools.debugging("This is test",status,emailObj.template_name)
        
        if emailObj.createAndUpdateTemplate():
            mailResponse = emailObj.sendEmail('ankus.nayak@imerit.net','ankus.nayak@imerit.net',json.dumps(data))
            emailObj.mailStatus(mailResponse)