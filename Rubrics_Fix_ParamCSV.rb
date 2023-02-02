#To Run on Terminal:
#rmv use 2.6.6
#ruby 'file path'

require 'typhoeus'
require 'csv'
require 'json'

################################# CHANGE THESE VALUES ###########################
@access_token = 'TOKEN'     #your API token that was generated from your account user
@domain = 'domain'                                                                             #domain.instructure.com, use domain only
@env = 'prod'                                                                                #Leave nil if pushing to Production
@csv_file = 'PATH'                          #Use the full path /Users/XXXXX/Path/To/File.csv
############################## DO NOT CHANGE THESE VALUES #######################

@env ? @env << "." : @env
@base_url = "https://#{@domain}.#{@env}instructure.com/"

CSV.foreach(@csv_file, {headers: true}) do |row|
  if row['id'].nil?
    puts 'No data in id field'
    raise 'Valid CSV headers not found (Expecting id)'
  else
    outcome_id = row['id']
    outcome_id["*"] = ""

    response = Typhoeus.put(
            @base_url + "api/v1/outcomes/#{outcome_id}",
            headers: {:authorization => 'Bearer ' + @access_token},
            params: {
                row['param'] => row['value']
            }
        )
    #puts outcome_id
    #parse JSON data to save in readable array
    #data = JSON.parse(response.body)
    #puts data
  end
end
puts 'Successfully executed!'