from playwright.sync_api import sync_playwright
import pytesseract

def fetch_att(username, pwd):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720},
            ignore_https_errors=True
        )
        context.route('**/*.{png,jpg,jpeg}', lambda route: route.abort())
        context.route('**/*.css', lambda route: route.abort())

        # Open the login page and perform login
        page = context.new_page()
        login_url = 'https://erp.velsuniv.ac.in/velsonline/students/loginManager/youLogin.jsp'
        page.goto(login_url)
        page.fill('input[name="login"]', username)
        page.fill('input[name="passwd"]', pwd)

        # Handle CAPTCHA
        captcha_image = page.locator("//img[@src='/velsonline/captchas']")
        captcha_image.screenshot(path='captcha.png')
        captcha_text = pytesseract.image_to_string('captcha.png').strip()
        page.fill('input[name="ccode"]', captcha_text)

        page.click('#_save')

        
        # Navigate to profile page and fetch student name
        profile = context.new_page()
        profile.goto("https://erp.velsuniv.ac.in/velsonline/students/template/PageLeft.jsp")
        profile.wait_for_selector('td.ui-state-highlight.ui-corner-all b')
        student_name = profile.locator('td.ui-state-highlight.ui-corner-all b').inner_text()

        # Navigate to attendance page and fetch percentage and end date
        att_frame = context.new_page()
        att_frame.goto("https://erp.velsuniv.ac.in/velsonline/students/report/studentSubjectWiseAttendance.jsp")
        att_frame.wait_for_selector('#tblSubjectWiseAttendance tr.subtotal td:has-text("%")')
        percentage = att_frame.locator('#tblSubjectWiseAttendance tr.subtotal td:has-text("%")').inner_text()
        percentage = f"{float(percentage.strip('%')):.2f}%"
        end_date = att_frame.locator('#tblSubjectWiseAttendance tr.subheader1 td:nth-child(4)').inner_text()

        
        profile.close()
        att_frame.close()
        page.close()
        browser.close()
        return student_name, percentage, end_date
    
