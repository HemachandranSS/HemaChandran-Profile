import os

directory = "."
prefix = "_OceanofPDF.com_"

for filename in os.listdir(directory):
    if filename.startswith(prefix):
        new_filename = filename[len(prefix):]

        old_path = os.path.join(directory, filename)
        new_path = os.path.join(directory, new_filename)

        os.rename(old_path, new_path)

        print(f"Renamed: {filename} -> {new_filename}")

print("Done.")
