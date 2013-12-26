from google.appengine.api import users

import webapp2

import micro_webapp2
application = micro_webapp2.WSGIApplication()

@application.route('/')
def m(request, *args, **kwargs):
    return ""

@application.route('/feedback/<id>')
def mail_sender(request, *args, **kwargs):
    
    if request.method != "POST":
        return ""
    
    message = ""
    for k,v in request.POST.iteritems():
        message += "%s: %s\n" % (k,v)
    
    if kwargs["id"] == "relational":
        from google.appengine.api import mail

        mail.send_mail(sender="Feedback service <tiposchi@tiscali.it>",
            to="tiposchi@tiscali.it",
              subject="Feedback from %s" % kwargs["id"],
              body=message)

    return "Message queued"
