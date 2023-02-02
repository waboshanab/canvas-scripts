--Code to extract learning outcome results data from the Canvas Data Store on AWS Athena
--We are using the following tables from the CanvasDataStore database:
--account_dim
--course_dim
--learning_outcome_dim
--enrollment_term_dim
--learning_outcome_result_fact


SELECT  
 course_dim.name as [course name] --This represents the course section number and title
,course_dim.code --The Canvas SIS ID
,account_dim.subaccount1 as [college] --Which College this course belongs to
,account_dim.name as [course group] --Course Sub-account
,enrollment_term_dim.name as [enrollment term] --Course Term, when course was offered
,learning_outcome_dim.short_description as [outcome description] --Outcome description
,learning_outcome_dim.[display_name] as [slos] --Friendly name where SLOs could be split
,attempts --How many times student was evaluated on this outcome
,possible --Total possible points on this outcome
,original_score --What student scored on the first attempt
,[percent] --Percentage of socre to possible points

from learning_outcome_result_fact

--This section is where we link the 4 different tables to the learning_outcome_result_fact table

--To join course_dim
inner JOIN course_dim on learning_outcome_result_fact.course_id = course_dim.id

--To join enrollment_term_dim
inner JOIN enrollment_term_dim on learning_outcome_result_fact.enrollment_term_id = enrollment_term_dim.id

--To join learning_outcome_dim
inner JOIN learning_outcome_dim on learning_outcome_result_fact.learning_outcome_id = learning_outcome_dim.id

--To join account_dim
inner join account_dim on course_dim.account_id = account_dim.id

;
