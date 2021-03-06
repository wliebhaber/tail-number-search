from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import bs4, requests
import wikipedia

app = Flask(__name__)

@app.route('/', methods=['POST'])
def sms():
  # Get the text in the message sent
  message_body = request.form['Body']

  upperbody = message_body.upper()  
    #parse message body

  if upperbody[0] == 'N':
    replyText = get_tail_number(message_body)

  elif upperbody[:4] == 'WIKI':
    replyText = get_wiki(message_body[5:])

  else:
    replyText = 'Error: Command not Recognized.  Please start with \'Wiki\' or \'N\''

    # Send the message body to the getReply message, where 
    # # we will query the String and formulate a response

  # Create a Twilio response object to be able to send a reply back (as per         # Twilio docs)
  resp = MessagingResponse()
	# Text back our response!
  resp.message(replyText)
  return str(resp)

def get_tail_number(nnumber):

  url = 'http://registry.faa.gov/aircraftinquiry/NNum_Results.aspx?nNumberTxt='  #FAA registry website
  #nnumber = ''  #variable to hold n-number

  #nnumber = input('Please enter tail number: ') #get input

  res = requests.get(url+nnumber)

  try:
    res.raise_for_status()
  except Exception as exc:
    message = 'There was a problem.'
    return message
    
  data = bs4.BeautifulSoup(res.text, "html.parser")

  mfr = data.select('#content_lbMfrName')
  model = data.select('#content_Label7')
  owner = data.select('#content_lbOwnerName')

  message = '\rOwner: ' + owner[0].getText() + '\rManufacturer: ' + mfr[0].getText() + '\rModel: ' + model[0].getText()

  return message

def get_wiki(query):

  try:
    search_result = wikipedia.summary(query)
  except wikipedia.exceptions.DisambiguationError as e:
    message = ''
    for option in e.options:
      message = '\r' + message + option
    return message
  except wikipedia.exceptions.PageError as e:
    return e
    
  message = wikipedia.summary(query)
  
  if len(message) > 1600:
    message = '\r' & message[:1500] + '...'
    return message
  else:
    return message

if __name__ == '__main__':
  app.run()