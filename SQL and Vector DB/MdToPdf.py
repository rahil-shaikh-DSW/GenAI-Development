import os
import markdown
import pdfkit

# Folder containing markdown files
folder_path = "chsbc"
output_pdf = "merged_output.pdf"

# Set the path to wkhtmltopdf manually
# Update the path below to where wkhtmltopdf is installed on your system
config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")

# Fetch all markdown files in the folder and sort them (optional)
md_files = sorted([f for f in os.listdir(folder_path) if f.endswith(".md")])

# Initialize an empty HTML string
html_content = "<html><head><meta charset='utf-8'><style>body { font-family: Arial, sans-serif; }</style></head><body>"

# Convert each markdown file to HTML and append
for md_file in md_files:
    with open(os.path.join(folder_path, md_file), "r", encoding="utf-8") as f:
        md_text = f.read()
        html_content += f"<h1>{md_file}</h1>"  # Add file name as a header
        html_content += markdown.markdown(md_text)  # Convert MD to HTML
        html_content += "<hr>"  # Add a horizontal line between files

html_content += "</body></html>"

# Convert HTML to PDF
pdfkit.from_string(html_content, output_pdf, configuration=config)

print(f"PDF generated successfully: {output_pdf}")
