from flask.ext.mail import Message
from flask import current_app
from flask import render_template
from . import mail


def send_email(recipients, subject, template, **kwargs):
    msg = Message('[Flasky]' + '  ' + subject,
                  sender=current_app.config['MAIL_USERNAME'],
                  recipients=[recipients])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    mail.send(msg)
