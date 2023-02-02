## UPDATE CERTAIN OUTCOMES - TO UPDATE FRIENDLY NAME AND TITLE ##

######################## ASK WALID BEFORE RUNNING #######################################################

#To Run on Terminal:
#rmv use 2.6.6
#ruby 'file path'

require 'typhoeus'
require 'csv'
require 'json'


@access_token = 'TOKEN'       
@domain = 'domain'         
@env = nil          
@csv_file = 'PATH'        


@env ? @env << "." : @env
@base_url = "https://#{@domain}.#{@env}instructure.com/"

CSV.foreach(@csv_file, {headers: true}) do |row|
  if row['id'].nil?
    puts 'No data in id field'
    raise 'Valid CSV headers not found (Expecting id)'
  else
    outcome_id = row['id']
    outcome_id["*"] = ""

    response = Typhoeus.get(
            @base_url + "api/v1/outcomes/#{outcome_id}",
            headers: {:authorization => 'Bearer ' + @access_token},
            params: {
                
            }
        )

    #parse JSON data to save in readable array
    data = JSON.parse(response.body)
    title = data['title']
    puts title
    if title.nil?
      puts "Blank title for #{slo['id']}"
    else
      if title.include? "SLO DBRA"          
        title["SLO DBRA"] = "SLO DBR"
      end
      if title.include? "SLO DBRG"
        title["SLO DBRG"] = "SLO DBR"
      end
      if title.include? "SLO DJCA"
        title["SLO DJCA"] = "SLO DJC"
      end
      if title.include? "SLO DJCG"
        title["SLO DJCG"] = "SLO DJC"
      end
      if title.include? "SLO TL 300.3"
        title["SLO TL 300.3"] = "SLO TL 300.2"
      end
      if title.include? "\n"
        title["\n"] = ""
      end
      if title.include? "\n"
        title["\n"] = ""
      end
      if title.include? ".SLO"
        title[".SLO"] = ". SLO"
      end

      puts title   

      response = Typhoeus.put(
            @base_url + "api/v1/outcomes/#{outcome_id}",
            headers: {:authorization => 'Bearer ' + @access_token},
            params: {
                'title' => title
            }
        )
    end
  end
end