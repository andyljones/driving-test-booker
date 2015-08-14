import json
import time
import datetime

import mechanize
import dateutil.parser
from bs4 import BeautifulSoup

from gmail import send_email

def load_options():
    return json.load(open('resources/login_details.json'))

def fetch_dates_page():
    options = load_options()

    br = mechanize.Browser()
    br.set_handle_robots(False)

    print('1. Selecting test type')
    br.open('https://driverpracticaltest.direct.gov.uk')
    br.form = next(br.forms())
    br.submit(id='test-type-car')

    print('2. Setting driving license number and special requirements')
    br.form = next(br.forms())
    br.form.set_value(options['license_number'], id='driving-licence')
    br.form.set_value(['false'], id='special-needs-none')
    br.submit()

    print('3. Setting postcode')
    br.form = next(br.forms())
    br.form.set_value(options['postcode'], id='test-centres-input')
    br.submit()

    print('4. Setting test centre')
    br.follow_link(text_regex=options['town'])

    print('5. Setting date')
    br.form = next(br.forms())
    br.form.set_value(options['date'], id='test-choice-calendar')
    return br.submit().read()

def parse_date(s):
    return dateutil.parser.parse(s, dayfirst=True)

def extract_dates(page):
    soup = BeautifulSoup(page)
    return [parse_date(d.string) for d in soup.find_all(class_='slotDateTime')]

def filter_acceptable_dates(dates):
    options = load_options()
    date_range = [parse_date(s).date() for s in options['date_range']]
    time_range = [parse_date(s).time() for s in options['time_range']]

    acceptable_dates = [d for d in dates if date_range[0] <= d.date() <= date_range[1]]
    acceptable_times = [d for d in acceptable_dates if time_range[0] <= d.time() <= time_range[1]]

    return acceptable_times

def email_dates(dates):
    dates_text = '\n'.join(d.strftime('%H:%M, %d %B %Y') for d in dates)
    url = 'https://driverpracticaltest.direct.gov.uk'
    text = str.format('The following dates have been found:\n\n{}\n\nTest site URL: {}', dates_text, url)

    address = load_options()['email']

    send_email(address, address, 'Practical test dates', text)

def scrape_and_send():
    print(str.format('Scraping dates at {}', str(datetime.datetime.now())))
    page = fetch_dates_page()
    dates = filter_acceptable_dates(extract_dates(page))
    if dates:
        print(str.format('Sending email with dates {}', dates))
        email_dates(dates)
    else:
        print('Did not find any acceptable dates')

if __name__ == '__main__':
    time.sleep(10) # Since the job is being run from launchd, need to wait for an internet connection
    scrape_and_send()
