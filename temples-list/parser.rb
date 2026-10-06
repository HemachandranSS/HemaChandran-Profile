temple_data = []
temple_data_en.each_with_index do |td, ind|
  temple_data << {"temple_id" => td['temple_id'], "temple_name" => temple_data_ta[ind]["temple_name"], "temple_name_en" => td['temple_name'],"website" => "https://hrce.tn.gov.in/hrcehome/index_temple.php?tid=#{td['temple_id'].gsub("TM","")}", "district_name"=> temple_data_ta[ind]["district_name"], "district_name_en" => td['district_name'], "officer_description"=> temple_data_ta[ind]['officer_description'], "officer_description_en" => td['officer_description']}
end