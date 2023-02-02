import pypyodbc
import glob
import requests as gradingScheme
import datetime
import smtplib
import ssl
from email.message import EmailMessage


ACCESS_TOKEN_PROD = 'ACCESS TOKEN'
BASE_URL_PROD = "https://{domain}.instructure.com/api/v1/courses/sis_course_id:"
REQUEST_HEADERS_PROD = {'Authorization': 'Bearer %s' % ACCESS_TOKEN_PROD}


ACCESS_TOKEN_TEST = 'ACCESS TOKEN'
BASE_URL_TEST = "https://{domain}.instructure.com/api/v1/courses/sis_course_id:"
REQUEST_HEADERS_TEST = {'Authorization': 'Bearer %s' % ACCESS_TOKEN_TEST}


TODAY_DATE_TIME = datetime.datetime.now().date()
LOG_FILE = "C: \PATH % TODAY_DATE_TIME


def sendEmail():

    smtp_server = "server_domain"
    port = 123  # For starttls
    sender_email = "email@email.com"
    receiver_email = "email@email.com"
    password = "PASS_CODE"
    message = EmailMessage()
    message.set_content('Error updating course scheme...')
    message['Subject'] = 'Error Updating Course Scheme'
    message['From'] = sender_email
    message['To'] = receiver_email
    context = ssl.create_default_context()

    try:
        server = smtplib.SMTP(smtp_server, port)
        server.starttls(context=context)  # Secure the connection
        server.login(sender_email, password)
        server.send_message(message)

    except Exception as e:
        pass
    finally:
        server.quit()


def get_courses():
    courses = []
    connection = pypyodbc.connect('Driver={SQL Server Native Client 11.0};'
                                  'Server=name;'
                                  'Database=DBNAME;'
                                  'uid=Reporting;pwd=pass_code')

    cursor = connection.cursor()
    SQLCommandCourses = ("""select course_id, Canvas_ID as j_grading_standard_id
                        from (
                            select distinct 
                            LTRIM(RTRIM(SECTION)) + '-' + LTRIM(RTRIM(SECTION)) + '-' + LTRIM(RTRIM(SECTION)) as course_id,
                            SECTION.CREDIT_TYPE,
                            case
                                when SECTION.CREDIT_TYPE = 'ST' and SUBSTRING(MASTER_V.CRS_CDE,11,2) = 'CB' and SUBSTRING(MASTER_V.CRS_CDE,16,1) != '' then '37018' /*Competency based courses*/
                                when SECTION.CREDIT_TYPE = 'ST' then '11' /*Standard grading courses*/
                                when SECTION.CREDIT_TYPE = 'PF' then '1453' /*Pass - Fail courses*/
                                when SECTION.CREDIT_TYPE = 'PN' and (MASTER_V.CRS_CDE like 'INTRO101' OR SECTION.CRS_CDE like 'PDUI101') then '8975' /*Pass - NoPass*/
                                when SECTION.CREDIT_TYPE = 'PN' then '37040' /*Pass - NoPass courses*/
                                else ''

                            end as Canvas_ID
                            from SECTION
                            join TERM_TABLE ON SECTION.YR_CDE = TERM_TABLE.YR_CDE AND SECTION.TRM_CDE = TERM_TABLE.TRM_CDE
                            join SECTION_SCH on SECTION.CRS_CDE = SECTION_SCH.CRS_CDE and SECTION.YR_CDE = SECTION_SCH.YR_CDE and
                            SECTION.TRM_CDE = SECTION_SCH.TRM_CDE
                            where (SECTION.CRS_CANCEL_FLG = 'N' OR SECTION.CRS_CANCEL_FLG is null)
                            and Convert(Date, TRM_END_DTE) >= Convert(Date, GETDATE()) 
                            and CRS_COMP1 not in ('ABC')
                            and SECTION.INSTITUT_DIV_CDE is not null
                            and (SECTION.TRM_CDE like '[0-5]_' OR SECTION.TRM_CDE = 'PJ')
                            and SECTION_SCH.BLDG_CDE is not null /* This condition is to not upload REGISTER FOR COURSES */
                        ) as courses

                        where courses.Canvas_ID != ''""")

    cursor.execute(SQLCommandCourses)
    results = cursor.fetchall()
    for result in results:
        courses.append(result)
    connection.close()
    return courses


def main():
    courses_sis = []
    courses_sis = get_Jenzabar_courses()
    if not courses_sis:
        return
    else:
        for course in courses_sis:
            courseSISID = course[0]
            jGradingStandardId = course[1]
            getURL = BASE_URL_PROD + courseSISID

            #logFile.write('Getting info for:%s.\n' % courseSISID)
            cCourseDetails = gradingScheme.get(
                getURL, headers=REQUEST_HEADERS_PROD)

            #logFile.write('Status Code:%s.\n' % cCourseDetails.status_code)
            if cCourseDetails.status_code == 200:
                cCourseDetailsJ = cCourseDetails.json()
                #logFile.write('JSON:%s.\n' % cCourseDetailsJ)
                if str(cCourseDetailsJ["grading_standard_id"]) != str(jGradingStandardId):
                    putURL = BASE_URL_PROD + courseSISID + \
                        "?course[grading_standard_id]=" + jGradingStandardId
                    putResponse = gradingScheme.put(
                        putURL, headers=REQUEST_HEADERS_PROD)
                    if putResponse.status_code == 200:
                        pass
                    else:
                        logFile.write(
                            'Issue updating grading scheme for:%s.\n' % courseSISID)
                else:
                    pass
            else:
                logFile.write(
                    'Issue getting information for:%s.\n' % courseSISID)
        return


logFile = open(LOG_FILE, "w+")
main()
logFile.close()
with open(LOG_FILE) as log:
    readLog = log.read()
    if 'Issue getting information for' in readLog or 'Issue updating grading scheme for' in readLog:
        sendEmail()
