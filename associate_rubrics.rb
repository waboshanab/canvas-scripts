
require 'typhoeus'
require 'csv'
require 'json'

################################# CHANGE THESE VALUES ###########################
@access_token = 'TOKEN'        #your API token that was generated from your account user
@domain = 'domain'            #domain.instructure.com, use domain only
@env = nil             #Leave nil if pushing to Production
@csv_file = 'PATH'          #Use the full path /Users/XXXXX/Path/To/File.csv
############################## DO NOT CHANGE THESE VALUES #######################

@env ? @env << "." : @env
@base_url = "https://#{@domain}.#{@env}instructure.com"


CSV.foreach(@csv_file, {headers: true}) do |row|
  if row['canvas_course_id'].nil? || row['rubric_id'].nil? || row['assignment_canvas_id'].nil? || row['assignment_name'].nil?
    puts 'No data in course SIS id field'
    raise 'Valid CSV headers not found (Expecting rubric_fields)'
  else
    canvas_course_id = row['canvas_course_id'], rubric_id = row['rubric_id'], 
    assignment_canvas_id = row['assignment_canvas_id'], assignment_name = row['assignment_name']

    response = Typhoeus.post(
            @base_url + "/api/v1/courses/#{row['canvas_course_id']}/rubric_associations",
            headers: {
                :authorization => 'Bearer ' + @access_token,
                'Content-Type' => 'application/x-www-form-urlencoded'
                },
            body: {
                rubric_association: {
                    :rubric_id => row['rubric_id'],
                    :association_id => row['assignment_canvas_id'],
                    :association_type => 'Assignment',
                    :title => row['assignment_name'],
                    :use_for_grading => 'true',
                    :purpose => 'grading'
                }
            }

        )

    #parse JSON data to save in readable array
    data = JSON.parse(response.body)
    puts data
  end
end