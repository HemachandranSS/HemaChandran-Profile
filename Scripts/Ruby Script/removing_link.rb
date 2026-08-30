require "hexapdf"

input  = "./1dorling_kindersley_earth.pdf"
output = "./removed_1dorling_kindersley_earth.pdf"

doc = HexaPDF::Document.open(input)

doc.pages.each_with_index do |page, index|
  page.each_annotation.to_a.each do |annotation|
    next unless annotation[:Subtype] == :Link

    action = annotation[:A]

    if action && action[:URI].to_s.include?("http://www.ebook3000.org")
      puts "Removing ebook3000 link from page #{index + 1}"
      page[:Annots].delete(annotation)
    end
  end
end

doc.write(output)

puts "Done: #{output}"