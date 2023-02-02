#Working as of October 18, 2019
require 'typhoeus'
require 'csv'
require 'json'


################################################################################
## AREA TO DEFINE THE TOKEN, DOMAIN, CANVAS ENVIRONMENT AND CSV FILE LOCATION ##

@access_token = 'TOKEN'
  #API token generated from account user in Canvas.
  #Token is generated and linked to users so it will not work with API calls for accounts 
  #unless the as_user API call is used to make the call on behalf another user

@domain = 'domain'
  #Just domain

@env = nil
  #Change nil to test or bets to switch between environments

@csv_file = 'PATH'
  #File path for the csv file used

############################ MAIN SCRIPT ####################################

#Assign the env variable
@env ? @env << "." : @env

#Assign the base url for Lynn's Canvas instance variable
@base_url = "https://#{@domain}.#{@env}instructure.com/"

@late_policy_status = true

@late_policy_points = 100.0


#################Method to enforce late policy##################

CSV.foreach(@csv_file, {headers: true}) do |row|
  if row['canvas_course_id'].nil?
    puts 'No data found in necessary canvas_course_id column'
    raise 'Valid CSV headers not found (Expecting canvas_course_id)'
  else canvas_course_id = row['canvas_course_id']
    response = Typhoeus.post(
                                @base_url + "/api/v1/courses/#{row['canvas_course_id']}/late_policy",  
                                headers:  {
                                          :authorization => 'Bearer ' + @access_token,
                                          'Content-Type' => 'application/x-www-form-urlencoded'},

                                body:     {
                                          late_policy: {
                                            :missing_submission_deduction_enabled => @late_policy_status,
                                            :missing_submission_deduction => @late_policy_points }
                                          }          
                                # params:   {
                                #           'late_policy':[missing_submission_deduction_enabled] = "true",
                                #           'late_policy':[missing_submission_deduction] = "0"
                                #           }
                              )
    #parse JSON data to save in readable array
    data = JSON.parse(response.body)
    puts data
  end
 end

#######################################################################

