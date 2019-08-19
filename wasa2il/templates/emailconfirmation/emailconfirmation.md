{% load i18n %}

# {{ action_msg }}

{% blocktrans %}In order to complete the action, please click the following link:{% endblocktrans %} [{% trans 'Confirm' %}]({{ confirmation_url}})

{% blocktrans %}If you did not request this action, you can safely ignore this email.{% endblocktrans %}

