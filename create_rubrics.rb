
require 'typhoeus'
require 'csv'
require 'json'

################################# CHANGE THESE VALUES ###########################
@access_token = 'TOKEN'        #your API token that was generated from your account user
@domain = 'admin'            #domain.instructure.com, use domain only
@env = nil             #Leave nil if pushing to Production
@csv_file = 'PATH'          #Use the full path /Users/XXXXX/Path/To/File.csv
############################## DO NOT CHANGE THESE VALUES #######################

@env ? @env << "." : @env
@base_url = "https://#{@domain}.#{@env}instructure.com"


CSV.foreach(@csv_file, {headers: true}) do |row|
  if row['course_id'].nil? || row['rubric_title'].nil? || row['outcome1'].nil? || row['outcome2'].nil? || row['outcome3'].nil? || row['outcome1_id'].nil? || row['outcome2_id'].nil? || row['outcome3_id'].nil?
    puts 'No data in course SIS id field'
    raise 'Valid CSV headers not found (Expecting rubric_fields)'
  else
    course_id = row['course_id'], rubric_title = row['rubric_title'], 
    outcome1 = row['outcome1'], outcome2 = row['outcome2'], outcome3 = row['outcome3'],  
    outcome1_id = row['outcome1_id'], outcome2_id = row['outcome2_id'], outcome3_id = row['outcome3_id']

    response = Typhoeus.post(
            @base_url + "/api/v1/courses/#{row['course_id']}/rubrics",
            headers: {
                :authorization => 'Bearer ' + @access_token,
                'Content-Type' => 'application/x-www-form-urlencoded'
                },
            body: {
                :rubric_association_id => row['course_id'],
                rubric: {
                    :title => row['rubric_title'],
                    :free_form_criterion_comments => 'false',
                    criteria: {
                        '0': {
                            :id => row['outcome1_id'],
                            :description => row['outcome1'],
                            :learning_outcome_id => row['outcome1_id'],
                            ratings: {
                                    '0': {
                                        :description => 'Excellent - Clearly, concisely, and logically presents key concepts related to experiment.',
                                        :points => '100'
                                    },
                                    '1': {
                                        :description => 'Above Average - Missing a key concept related to experiment. Lacks conciseness and organization.',
                                        :points => '75'
                                    },
                                    '2': {
                                        :description => 'Average - Meeting key concepts with acceptable level.',
                                        :points => '50'
                                    },
                                    '3': {
                                        :description => 'Below Average - Lacking two or more key concepts. No hypothesis or predictions.',
                                        :points => '25'
                                    },
                                    '4': {
                                        :description => 'Unacceptable - Lacking key concepts.',
                                        :points => '0'
                                    }
                                }
                            },
                        '1': {
                            :id => row['outcome2_id'],
                            :description => row['outcome2'],
                            :learning_outcome_id => row['outcome2_id'],
                            ratings: {
                                    '0': {
                                        :description => 'Excellent - Clearly, concisely, and logically presents key concepts related to experiment.',
                                        :points => '100'
                                    },
                                    '1': {
                                        :description => 'Above Average - Missing a key concept related to experiment. Lacks conciseness and organization.',
                                        :points => '75'
                                    },
                                    '2': {
                                        :description => 'Average - Meeting key concepts with acceptable level.',
                                        :points => '50'
                                    },
                                    '3': {
                                        :description => 'Below Average - Lacking two or more key concepts. No hypothesis or predictions.',
                                        :points => '25'
                                    },
                                    '4': {
                                        :description => 'Unacceptable - Lacking key concepts.',
                                        :points => '0'
                                    }
                                }
                            },
                        '2': {
                            :id => row['outcome3_id'],
                            :description => row['outcome3'],
                            :learning_outcome_id => row['outcome3_id'],
                            ratings: {
                                    '0': {
                                        :description => 'Excellent - Clearly, concisely, and logically presents key concepts related to experiment.',
                                        :points => '100'
                                    },
                                    '1': {
                                        :description => 'Above Average - Missing a key concept related to experiment. Lacks conciseness and organization.',
                                        :points => '75'
                                    },
                                    '2': {
                                        :description => 'Average - Meeting key concepts with acceptable level.',
                                        :points => '50'
                                    },
                                    '3': {
                                        :description => 'Below Average - Lacking two or more key concepts. No hypothesis or predictions.',
                                        :points => '25'
                                    },
                                    '4': {
                                        :description => 'Unacceptable - Lacking key concepts.',
                                        :points => '0'
                                    }
                                }
                        }
                    }
                    
                },
                rubric_association: {
                    :association_id => row['course_id'],
                    :association_type => 'Course',
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