import mechanize
import json

br = mechanize.Browser()

print('Getting login page...')
br.open('https://wsr.theorytest.direct.gov.uk/testtaker/signin/SignInPage/DSA')

print('Logging in...')
br.select_form('SignInForm')
for name, value in json.load(open('resources/login_details.json')).items():
    br[name] = value
r = br.submit()

print('Saving response...')
with open('output/tmp.html', 'w') as f:
    f.write(r.read())
