import pypyodbc
import glob
import requests as gradingScheme
import datetime
import smtplib
import ssl
from email.message import EmailMessage

ACCESS_TOKEN_PROD = 'ACCESS TOKEN'
BASE_URL_PROD = ""
REQUEST_HEADERS_PROD = {'Authorization':'Bearer %s' % ACCESS_TOKEN_PROD}

ACCESS_TOKEN_TEST = 'ACCESS TOKEN'
BASE_URL_TEST = ""
REQUEST_HEADERS_TEST = {'Authorization':'Bearer %s' % ACCESS_TOKEN_TEST}


TODAY_DATE_TIME = datetime.datetime.now().date()
LOG_FILE = "" % TODAY_DATE_TIME

def sendEmail():
                smtp_server = ""
                port =   # For starttls
                sender_email = ""
                receiver_email = ""
                password = ""
                message = EmailMessage()
                message.set_content('Error updating course scheme...')
                message['Subject'] = 'Error Updating Course Scheme'
                message['From'] = sender_email
                message['To'] = receiver_email
                context = ssl.create_default_context()
                try:
                                server = smtplib.SMTP(smtp_server,port)
                                server.starttls(context=context) # Secure the connection
                                server.login(sender_email, password)
                                server.send_message(message)
                except Exception as e:
                                pass
                finally:
                                server.quit()


def get_database_courses():
                courses = []
                connection = pypyodbc.connect('Driver={SQL Server Native Client 11.0};'
                                'Server=;'
                                'Database=;'
                                'uid=;pwd=')
                cursor = connection.cursor()
                SQLCommandCourses = ("""select course_id, Canvas_ID as j_grading_standard_id
					from (
									select distinct
									LTRIM(RTRIM(COURSES_TABLE_V.CRS_CDE)) + '-' + LTRIM(RTRIM(COURSES_TABLE_V.YR_CDE)) + '-' + LTRIM(RTRIM(COURSES_TABLE_V.TRM_CDE)) as course_id,
									COURSES_TABLE_V.CREDIT_TYPE_CDE,
									case
													when COURSES_TABLE_V.CREDIT_TYPE_CDE = 'ST' and SUBSTRING(COURSES_TABLE_V.CRS_CDE,11,2) = 'CB' and SUBSTRING(COURSES_TABLE_V.CRS_CDE,16,1) != '' then 															'37018' /*Competency based courses*/
													when COURSES_TABLE_V.CREDIT_TYPE_CDE = 'ST' then '11' /*Standard grading courses*/
													when COURSES_TABLE_V.CREDIT_TYPE_CDE = 'PF' then '1453' /*Pass - Fail courses*/
													when COURSES_TABLE_V.CREDIT_TYPE_CDE = 'PN' and (COURSES_TABLE_V.CRS_CDE like 'LYNN%%101%%' OR COURSES_TABLE_V.CRS_CDE like 'DJCP%%100%%') then '8975' /														*Pass - NoPass Lynn101 and DJCP100*/
													when COURSES_TABLE_V.CREDIT_TYPE_CDE = 'PN' then '37040' /*Pass - NoPass courses*/
													else ''
									end as Canvas_ID
									from COURSES_TABLE_V
									join YEAR_TERM_TABLE ON COURSES_TABLE_V.YR_CDE = YEAR_TERM_TABLE.YR_CDE AND COURSES_TABLE_V.TRM_CDE = YEAR_TERM_TABLE.TRM_CDE
									join SECTION_SCHEDULES on COURSES_TABLE_V.CRS_CDE = SECTION_SCHEDULES.CRS_CDE and COURSES_TABLE_V.YR_CDE = SECTION_SCHEDULES.YR_CDE and
									COURSES_TABLE_V.TRM_CDE = SECTION_SCHEDULES.TRM_CDE
									where (COURSES_TABLE_V.CRS_CANCEL_FLG = 'N' OR COURSES_TABLE_V.CRS_CANCEL_FLG is null)
									and Convert(Date, TRM_END_DTE) >= Convert(Date, GETDATE())
									and CRS_COMP1 not in ('ABC')
									and COURSES_TABLE_V.INSTITUT_DIV_CDE is not null
									and (COURSES_TABLE_V.TRM_CDE like '[0-5]_' OR COURSES_TABLE_V.TRM_CDE = 'PJ')
									and SECTION_SCHEDULES.BLDG_CDE is not null /* This condition is to not upload REGISTER FOR COURSES */
					) as courses
					where courses.Canvas_ID != ''""")
                cursor.execute(SQLCommandCourses)
                results = cursor.fetchall()
                for result in results:
                                courses.append(result)
                connection.close()
                return courses

def main():
                courses_database = []
                courses_database = get_database_courses()
                if not courses_database:
                                return
                else:
                                for course in courses_database:
									courseSISID = course[0]
									jGradingStandardId = course[1]
									getURL = BASE_URL_PROD + courseSISID
									#logFile.write('Getting info for:%s.\n' % courseSISID)
									cCourseDetails = gradingScheme.get(getURL,headers=REQUEST_HEADERS_PROD)
									#logFile.write('Status Code:%s.\n' % cCourseDetails.status_code)
									if cCourseDetails.status_code == 200:
										cCourseDetailsJ = cCourseDetails.json()
										#logFile.write('JSON:%s.\n' % cCourseDetailsJ)
										if str(cCourseDetailsJ["grading_standard_id"]) != str(jGradingStandardId):
														putURL = BASE_URL_PROD + courseSISID + "?course[grading_standard_id]=" + jGradingStandardId
														putResponse = gradingScheme.put(putURL,headers=REQUEST_HEADERS_PROD)
														if putResponse.status_code == 200:
														pass
														else:
												logFile.write('Issue updating grading scheme for:%s.\n' % courseSISID)
										else:
										pass
								else:
												logFile.write('Issue getting information for:%s.\n' % courseSISID)
					return

logFile = open(LOG_FILE, "w+")
main()
logFile.close()
with open(LOG_FILE) as log:
                readLog = log.read()
                if 'Issue getting information for' in readLog or 'Issue updating grading scheme for' in readLog:
                                sendEmail()
