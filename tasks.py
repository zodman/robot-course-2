from robocorp.tasks import task
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive
from robocorp import browser
import os

browser.configure(headless=True)
table = Tables()
pdf = PDF()
archive = Archive()

output = os.path.join("files","orders.cvs") 

template_html = """
<H2>
Receipt
</H2>
<div>
{}
</div>

<div>
<center>
<img src="{}" />
</center>
</div>
"""


@task
def download_csv():
    http = HTTP()
    if not os.path.exists("files"):
        os.mkdir("files")
    http.download("https://robotsparebinindustries.com/orders.csv", output)

@task
def process_file():
    rows = table.read_table_from_csv(output)
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    page = browser.page()
    for i in rows:
        page.get_by_text("Ok").click()
        page.get_by_label("1. Head:").select_option(i["Head"]) 
        page.locator(f"#id-body-{i['Body']}").check()
        page.get_by_label("3. Legs:").fill(i["Legs"]) 
        page.locator("[name='address']").fill( i["Address"]) 
        page.get_by_text("Preview").click()
        img = f"files/{i['Order number']}.jpg"
        page.locator("#robot-preview-image").screenshot(path=img)
        page.get_by_role("button",name="Order").click()
        while page.locator("[class='alert alert-danger']").is_visible():
            page.get_by_role("button",name="Order").click()

        page.wait_for_selector("#receipt", state="visible")
        text = page.locator("#receipt").all_inner_texts()
        page.locator("#order-another").click()
        html = template_html.format(text[0], img)
        pdf.html_to_pdf(html, f"files/{i['Order number']}.pdf")

@task
def archive_files():
    if not os.path.exists("output"):
        os.mkdir("output")

    archive.archive_folder_with_zip("files/", "output/files.zip", include="*.pdf")

        

