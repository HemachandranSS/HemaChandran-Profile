require 'rmagick'
require 'combine_pdf'

start_page = 1
end_page = 51
month_name= "oct"
year = 2011
pdf = CombinePDF.new
#pdf_file_name = "OSFY_#{month_name}_#{year}.pdf"
#pdf_file_name = "EFY_#{month_name}_#{year}.pdf"
#pdf_file_name = "Leader_Board-eicher-motors-founder-vikram-lal-27-09-2024.pdf"
#pdf_file_name = "Top_Multi_Bagger_Stocks(20-Feb_2025)_Mar_02_2025.pdf"
#pdf_file_name = "02-Rupee_Driver_Jun_04_2025.pdf"
# pdf_file_name = "நாணயம்_விகடன்_Jun_20_2025.pdf"
#pdf_file_name = "National_Science_Day.pdf"
#pdf_file_name = "SportStar_Mar_28_2025.pdf"
#pdf_file_name = "International_Relations_Concept.pdf"
#pdf_file_name = "car_bazaar_nov_2024.pdf"

pdf_file_name = 'ChemistryTodayMay2026.pdf'

1.upto(51) do |page|
  #file_name = "#{page}.webp"
  file_name = "#{page}.png"
  #file_name = "#{page}.jpg"
  begin
    #system("wget https://eci.gov.in/ebooks/Leap-of-Faith/files/mobile/#{file_name}") 272
    #system("wget https://eci.gov.in/ebooks/eci-atlas/files/mobile/#{file_name}") #108
    #https://ezine.efyindia.com/ezine/EFYJan2009/HTML5/files/large/172.jpg
    #system("wget https://ezine.efyindia.com/ezine/EFY#{month_name}#{year}/HTML5/files/large/#{file_name}")
    #system("wget https://ezine.efyindia.com/ezine/EFY#{month_name}#{year}/HTML5/l/#{file_name}")
    #system("wget https://ezine.efyindia.com/ezine/lfy/LFY#{month_name}#{year}/HTML5/files/large/#{file_name}")
    #system("wget https://eci.gov.in/ebooks/eci-atlas/files/mobile/#{page}.jpg")
    jpg = Magick::ImageList.new("#{file_name}")
    jpg.write("#{page}.pdf")
    system("rm #{file_name}")
    pdf << CombinePDF.load("#{page}.pdf")
    system("rm #{page}.pdf")
  rescue => e
    print "#{e.message}"
    next
  end
end
pdf.save pdf_file_name