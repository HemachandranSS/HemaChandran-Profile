require "hexapdf"

input  = "./Encyclopedia_Of_Herbal_Medicine_-_Andrew_Chevallier.pdf"
output = "./cleaned_Encyclopedia_Of_Herbal_Medicine_-_Andrew_Chevallier.pdf"

doc = HexaPDF::Document.open(input)

doc.pages.each_with_index do |page, index|
  annotations = page.each_annotation.to_a

  annotations.each do |annotation|
    if annotation[:Subtype] == :Link
      puts "Removing link from page #{index + 1}"
      page[:Annots].delete(annotation)
    end
  end
end

doc.write(output)

puts "Done: #{output}"
