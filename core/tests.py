from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

pdf_path = ("2Pages.pdf")
packet = io.BytesIO()
can = canvas.Canvas(packet, pagesize=letter)
can.setFont("Helvetica", 7)

can.drawString(50, 143, "{}: {}{} {}".format("Mariusz Sałata ", "80", "km", "Tostedt - Harburg - Tostedt 1"))
can.drawString(50, 126, "{}: {}{} {}".format("Mariusz Sałata ", "80", "km", "Tostedt - Harburg - Tostedt 2"))
can.drawString(50, 109, "{}: {}{} {}".format("Mariusz Sałata ", "80", "km", "Tostedt - Harburg - Tostedt 3"))


can.drawString(318, 143, "{}: {}{} {}".format("Mariusz Sałata ", "80", "km", "Tostedt - Harburg - Tostedt 1"))
can.drawString(318, 126, "{}: {}{} {}".format("Mariusz Sałata ", "80", "km", "Tostedt - Harburg - Tostedt 2"))
can.drawString(318, 109, "{}: {}{} {}".format("Mariusz Sałata ", "80", "km", "Tostedt - Harburg - Tostedt 3"))

can.save()


# move to the beginning of the StringIO buffer
packet.seek(0)

# create a new PDF with Reportlab
new_pdf = PdfFileReader(packet)
# read your existing PDF
existing_pdf = PdfFileReader(str(pdf_path))
output = PdfFileWriter()

# add the "watermark" (which is the new pdf) on the existing page

for page in range(existing_pdf.getNumPages()):
    page = existing_pdf.getPage(page)
    page.mergePage(new_pdf.getPage(0))
    output.addPage(page)


# finally, write "output" to a real file

outputStream = open("TestOut.pdf", "wb")
output.write(outputStream)
outputStream.close()


